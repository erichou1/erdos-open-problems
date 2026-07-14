"""Lean formal-verification service API (spec §9.3).

Implements ``createEnvironment / elaborate / goalState / searchPremises /
tryActions / verifyDeclaration / compareStatements`` plus the ``FormalCertificate``
and ``GoalCapsule`` value types.

The actual kernel build is delegated to an *injectable* runner (the repo's
``lean_verify.verify_project`` by default); real ``lake build`` requires a Lean
toolchain (see DECISIONS.md D-004). Everything else — placeholder/axiom/unsafe
scanning, target-type checking, axiom whitelist enforcement, and the
"``equivalent`` only with a checked proof" rule — is implemented here and tested
with fixtures and injected runners.
"""

from __future__ import annotations

import json
import hmac
import os
import re
import shutil
import subprocess
import time
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any, Callable

from egmra.provenance.hashing import canonical_json, content_id, is_sha256, sha256_bytes, sha256_hex

# A typical classical project's release axiom whitelist (spec §9.3).
DEFAULT_AXIOM_WHITELIST = frozenset({"propext", "Quot.sound", "Classical.choice"})
FORBIDDEN_AXIOMS = frozenset({"sorryAx"})
# Kernel-bypassing native mechanisms are forbidden for release (or external).
NATIVE_MECHANISMS = ("native_decide", "implemented_by", "unsafe ")
LOCAL_KERNEL_METHOD = "local_lean_kernel"
_MIN_CHECKER_KEY_BYTES = 32


class LeanServiceError(RuntimeError):
    pass


class CheckerConfigurationError(LeanServiceError):
    """A production checker is absent, weakly configured, or unpinned."""


def _utc_now(timestamp: float | None = None) -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(timestamp))


def _checker_key(env: dict[str, str] | None) -> bytes:
    values = env if env is not None else dict(os.environ)
    raw = values.get("EGMRA_LEAN_CHECKER_KEY", "").strip().encode("utf-8")
    if len(raw) < _MIN_CHECKER_KEY_BYTES:
        raise CheckerConfigurationError(
            f"EGMRA_LEAN_CHECKER_KEY must contain at least {_MIN_CHECKER_KEY_BYTES} bytes"
        )
    return raw


# ── source scanners (self-contained; no Lean required) ─────────────────────────

def strip_comments(source: str) -> str:
    source = re.sub(r"/-.*?-/", " ", source, flags=re.DOTALL)
    source = re.sub(r"--[^\n]*", " ", source)
    return source


def has_placeholder(source: str) -> bool:
    return bool(re.search(r"\b(sorry|admit)\b", strip_comments(source)))


def native_findings(source: str) -> list[str]:
    stripped = strip_comments(source)
    return [m for m in NATIVE_MECHANISMS if m.strip() in stripped]


def declared_axioms(source: str) -> list[str]:
    return re.findall(r"\baxiom\s+([A-Za-z0-9_'.]+)", strip_comments(source))


def extract_declaration_type(source: str, name: str) -> str:
    """Return the signature (type) text of ``theorem/lemma/def name``.

    The convention is: everything between the declaration name and ``:=``/``by``,
    normalized, with a single leading top-level ``:`` stripped so a binderless
    ``theorem t : P := ..`` yields exactly ``P``.
    """
    stripped = strip_comments(source)
    match = re.search(
        rf"\b(?:theorem|lemma|def)\s+{re.escape(name)}\s*([\s\S]*?)(?::=|\bby\b|$)",
        stripped,
    )
    if not match:
        raise LeanServiceError(f"declaration {name!r} not found in source")
    sig = " ".join(match.group(1).split())
    if sig.startswith(":"):
        sig = sig[1:].strip()
    return sig


# ── environment / goal capsule ──────────────────────────────────────────────────

@dataclass(frozen=True)
class LeanEnvironment:
    lean_version: str
    mathlib_commit: str
    project_hash: str
    trust_policy: str = "classical-whitelist"
    imports: tuple[str, ...] = ()
    options: dict = field(default_factory=dict)

    @property
    def environment_id(self) -> str:
        return content_id({
            "lean_version": self.lean_version,
            "mathlib_commit": self.mathlib_commit,
            "project_hash": self.project_hash,
            "trust_policy": self.trust_policy,
            "imports": sorted(self.imports),
            "options": self.options,
        })


@dataclass(frozen=True)
class CheckerRequest:
    """Exact values a checker must bind in its attestation."""

    environment_id: str
    source_hash: str
    declaration_name: str
    expected_type_hash: str
    immutable_target_module_hash: str
    trust_policy_hash: str

    def to_dict(self) -> dict[str, str]:
        return dict(self.__dict__)


@dataclass(frozen=True)
class CheckerAttestation:
    """Signed output of a pinned production checker.

    The public constructor is intentionally not a trust decision.  Qualification
    requires a valid HMAC under the checker-service key *and* exact request
    binding.  This keeps serialized checker output independently verifiable while
    preventing caller booleans/status strings from becoming proof evidence.
    """

    environment_id: str
    source_hash: str
    declaration_name: str
    expected_type_hash: str
    candidate_type_hash: str
    candidate_declaration_hash: str
    proof_term_hash: str
    immutable_target_module_hash: str
    trust_policy_hash: str
    source_tree_hash: str
    imports_hash: str
    checker_id: str
    checker_version: str
    checker_trust_base: str
    checker_binary_hash: str
    checker_log_hash: str
    transitive_axioms: tuple[str, ...]
    placeholder_findings: tuple[str, ...]
    unsafe_findings: tuple[str, ...]
    imports_audited: bool
    axiom_closure_verified: bool
    immutable_target_isolated: bool
    clean_replay: bool
    network_disabled: bool
    kernel_verified: bool
    production: bool
    issued_at: str
    key_fingerprint: str
    signature: str = ""

    def signed_record(self) -> dict[str, Any]:
        record = dict(self.__dict__)
        record.pop("signature", None)
        record["transitive_axioms"] = list(self.transitive_axioms)
        record["placeholder_findings"] = list(self.placeholder_findings)
        record["unsafe_findings"] = list(self.unsafe_findings)
        return record

    @property
    def attestation_hash(self) -> str:
        return content_id(self.signed_record() | {"signature": self.signature})

    def verify_for(
        self, request: CheckerRequest, *, env: dict[str, str] | None = None,
    ) -> bool:
        try:
            key = _checker_key(env)
        except CheckerConfigurationError:
            return False
        expected_signature = hmac.new(
            key, canonical_json(self.signed_record()).encode("utf-8"), "sha256"
        ).hexdigest()
        exact_bindings = (
            self.environment_id == request.environment_id
            and self.source_hash == request.source_hash
            and self.declaration_name == request.declaration_name
            and self.expected_type_hash == request.expected_type_hash
            and self.immutable_target_module_hash == request.immutable_target_module_hash
            and self.trust_policy_hash == request.trust_policy_hash
        )
        hashes_valid = all(
            is_sha256(value)
            for value in (
                self.environment_id,
                self.source_hash,
                self.expected_type_hash,
                self.candidate_type_hash,
                self.candidate_declaration_hash,
                self.proof_term_hash,
                self.immutable_target_module_hash,
                self.trust_policy_hash,
                self.source_tree_hash,
                self.imports_hash,
                self.checker_binary_hash,
                self.checker_log_hash,
                self.key_fingerprint,
            )
        )
        return bool(
            self.signature
            and self.production
            and bool(self.checker_id and self.checker_version and self.checker_trust_base)
            and self.kernel_verified
            and self.clean_replay
            and self.network_disabled
            and self.imports_audited
            and self.axiom_closure_verified
            and self.immutable_target_isolated
            and not self.placeholder_findings
            and not self.unsafe_findings
            and exact_bindings
            and hashes_valid
            and self.candidate_type_hash == request.expected_type_hash
            and self.key_fingerprint == sha256_bytes(key)
            and hmac.compare_digest(expected_signature, self.signature)
        )


class AttestedKernelRunner:
    """Run a pinned external checker that emits a structured JSON verdict.

    This is the only runner type whose result the service can qualify.  Test
    callbacks and simulated runners remain useful for exercising orchestration,
    but are intentionally not instances of this class and cannot set
    ``kernel_verified`` on a production certificate.

    The command receives a canonical JSON :class:`CheckerRequest` on stdin and
    must return JSON containing ``kernel_verified``, ``candidate_type_hash``,
    ``source_tree_hash``, ``imports_hash``, ``transitive_axioms``,
    ``clean_replay``, and ``network_disabled``.  Its executable bytes are pinned
    by ``checker_binary_hash``.
    """

    def __init__(
        self, *, command: tuple[str, ...], checker_id: str, checker_version: str,
        checker_binary_hash: str, checker_trust_base: str,
        env: dict[str, str] | None = None,
        timeout_s: float = 3600.0,
    ) -> None:
        if not command or not checker_id or not checker_version or not checker_trust_base:
            raise CheckerConfigurationError(
                "checker command, id, version, and trust base are required"
            )
        if not is_sha256(checker_binary_hash):
            raise CheckerConfigurationError("checker_binary_hash must be a SHA-256 digest")
        self.command = tuple(command)
        self.checker_id = checker_id
        self.checker_version = checker_version
        self.checker_trust_base = checker_trust_base
        self.checker_binary_hash = checker_binary_hash
        self.env = dict(env) if env is not None else None
        self.timeout_s = float(timeout_s)

    def _executable(self) -> Path:
        resolved = shutil.which(self.command[0]) or self.command[0]
        path = Path(resolved)
        if not path.is_file():
            raise CheckerConfigurationError(f"checker executable is unavailable: {self.command[0]}")
        if sha256_bytes(path.read_bytes()) != self.checker_binary_hash:
            raise CheckerConfigurationError("checker executable hash does not match the pin")
        return path

    @staticmethod
    def _runtime_environment() -> dict[str, str]:
        """Minimal non-secret environment for the checker subprocess."""
        allow = ("PATH", "HOME", "TMPDIR", "LANG", "LC_ALL")
        return {name: os.environ[name] for name in allow if name in os.environ}

    def run(self, request: CheckerRequest) -> CheckerAttestation:
        executable = self._executable()
        command = (str(executable), *self.command[1:])
        try:
            completed = subprocess.run(
                command,
                input=canonical_json(request.to_dict()),
                capture_output=True,
                text=True,
                check=False,
                timeout=self.timeout_s,
                env=self._runtime_environment(),
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise LeanServiceError(f"trusted checker execution failed: {exc}") from exc
        if completed.returncode != 0:
            raise LeanServiceError(
                f"trusted checker rejected candidate (exit {completed.returncode})"
            )
        try:
            output = json.loads(completed.stdout)
        except (TypeError, json.JSONDecodeError) as exc:
            raise LeanServiceError("trusted checker returned malformed JSON") from exc
        if not isinstance(output, dict):
            raise LeanServiceError("trusted checker response must be an object")
        required = {
            "kernel_verified", "candidate_type_hash", "source_tree_hash", "imports_hash",
            "candidate_declaration_hash", "proof_term_hash", "transitive_axioms",
            "placeholder_findings", "unsafe_findings", "imports_audited",
            "axiom_closure_verified", "immutable_target_isolated",
            "clean_replay", "network_disabled",
        }
        if required - set(output):
            raise LeanServiceError(
                f"trusted checker response missing fields: {sorted(required - set(output))}"
            )
        if output["kernel_verified"] is not True:
            raise LeanServiceError("trusted checker did not report kernel verification")
        axioms = output["transitive_axioms"]
        if not isinstance(axioms, list) or any(not isinstance(item, str) for item in axioms):
            raise LeanServiceError("trusted checker transitive_axioms must be a string list")
        placeholders = output["placeholder_findings"]
        unsafe_findings = output["unsafe_findings"]
        if not isinstance(placeholders, list) or any(
            not isinstance(item, str) for item in placeholders
        ):
            raise LeanServiceError("trusted checker placeholder_findings must be a string list")
        if not isinstance(unsafe_findings, list) or any(
            not isinstance(item, str) for item in unsafe_findings
        ):
            raise LeanServiceError("trusted checker unsafe_findings must be a string list")
        key = _checker_key(self.env)
        attestation = CheckerAttestation(
            environment_id=request.environment_id,
            source_hash=request.source_hash,
            declaration_name=request.declaration_name,
            expected_type_hash=request.expected_type_hash,
            candidate_type_hash=str(output["candidate_type_hash"]),
            candidate_declaration_hash=str(output["candidate_declaration_hash"]),
            proof_term_hash=str(output["proof_term_hash"]),
            immutable_target_module_hash=request.immutable_target_module_hash,
            trust_policy_hash=request.trust_policy_hash,
            source_tree_hash=str(output["source_tree_hash"]),
            imports_hash=str(output["imports_hash"]),
            checker_id=self.checker_id,
            checker_version=self.checker_version,
            checker_trust_base=self.checker_trust_base,
            checker_binary_hash=self.checker_binary_hash,
            checker_log_hash=sha256_hex(completed.stdout + "\n" + completed.stderr),
            transitive_axioms=tuple(axioms),
            placeholder_findings=tuple(placeholders),
            unsafe_findings=tuple(unsafe_findings),
            imports_audited=output["imports_audited"] is True,
            axiom_closure_verified=output["axiom_closure_verified"] is True,
            immutable_target_isolated=output["immutable_target_isolated"] is True,
            clean_replay=output["clean_replay"] is True,
            network_disabled=output["network_disabled"] is True,
            kernel_verified=True,
            production=True,
            issued_at=_utc_now(),
            key_fingerprint=sha256_bytes(key),
        )
        signature = hmac.new(
            key, canonical_json(attestation.signed_record()).encode("utf-8"), "sha256"
        ).hexdigest()
        return CheckerAttestation(**(attestation.__dict__ | {"signature": signature}))


@dataclass(frozen=True)
class GoalCapsule:
    """Keyed by Lean+Mathlib+imports/options+local context+target+trust policy.

    Textual pretty-printed goals are insufficient cache keys (spec §9.3).
    """

    environment_id: str
    local_context: tuple[str, ...]
    target_expression: str
    trust_policy: str

    def key(self) -> str:
        return content_id({
            "environment_id": self.environment_id,
            "local_context": list(self.local_context),
            "target_expression": self.target_expression,
            "trust_policy": self.trust_policy,
        })


@dataclass(frozen=True)
class FormalCertificate:
    """Everything a released Lean theorem must carry (spec §9.3)."""

    expected_type_hash: str
    candidate_declaration_hash: str
    proof_term_hash: str
    immutable_target_module_hash: str
    source_tree_hash: str
    transitive_axioms: tuple[str, ...]
    axiom_whitelist_ok: bool
    placeholder_findings: tuple[str, ...]
    unsafe_findings: tuple[str, ...]
    trust_policy_hash: str
    checker_id: str
    checker_version: str
    independent_checker_id: str
    checker_log_hash: str
    kernel_verified: bool
    target_type_matches: bool
    verification_method: str
    candidate_type_hash: str = ""
    environment_id: str = ""
    checker_attestation_hash: str = ""
    production_checker: bool = False
    clean_replay: bool = False
    network_disabled: bool = False
    axiom_closure_verified: bool = False
    import_audit_verified: bool = False
    immutable_target_isolated: bool = False
    checker_trust_base: str = ""
    source_environment_bound: bool = False
    source_hash: str = ""
    declaration_name: str = ""
    claim_bindings: tuple[tuple[str, str], ...] = ()
    artifact_hashes: tuple[str, ...] = ()
    certificate_key_fingerprint: str = ""
    certificate_signature: str = ""

    def _qualifies(self) -> bool:
        return bool(
            self.kernel_verified
            and self.target_type_matches
            and self.axiom_whitelist_ok
            and not self.placeholder_findings
            and not self.unsafe_findings
            and self.verification_method == LOCAL_KERNEL_METHOD
            and self.production_checker
            and self.clean_replay
            and self.network_disabled
            and self.axiom_closure_verified
            and self.import_audit_verified
            and self.immutable_target_isolated
            and self.source_environment_bound
            and bool(self.checker_attestation_hash)
            and all(
                is_sha256(value)
                for value in (
                    self.expected_type_hash,
                    self.candidate_declaration_hash,
                    self.proof_term_hash,
                    self.immutable_target_module_hash,
                    self.source_tree_hash,
                    self.trust_policy_hash,
                    self.checker_log_hash,
                    self.candidate_type_hash,
                    self.environment_id,
                    self.checker_attestation_hash,
                    self.source_hash,
                    self.certificate_key_fingerprint,
                )
            )
            and bool(self.checker_id and self.checker_version and self.checker_trust_base)
            and bool(self.declaration_name)
            and all(
                claim_id and is_sha256(claim_hash)
                for claim_id, claim_hash in self.claim_bindings
            )
            and len({claim_id for claim_id, _ in self.claim_bindings})
            == len(self.claim_bindings)
            and self.artifact_hashes
            and all(is_sha256(value) for value in self.artifact_hashes)
        )

    def signed_record(self) -> dict[str, Any]:
        record = dict(self.__dict__)
        record.pop("certificate_signature", None)
        for key, value in list(record.items()):
            if isinstance(value, tuple):
                record[key] = [list(item) if isinstance(item, tuple) else item for item in value]
        return record

    @property
    def certificate_digest(self) -> str:
        return content_id(
            self.signed_record() | {"certificate_signature": self.certificate_signature}
        )

    def verify(self, *, env: dict[str, str] | None = None) -> bool:
        """Authenticate every trust-relevant certificate field."""
        try:
            key = _checker_key(env)
        except CheckerConfigurationError:
            return False
        expected = hmac.new(
            key, canonical_json(self.signed_record()).encode("utf-8"), "sha256"
        ).hexdigest()
        return bool(
            self._qualifies()
            and self.certificate_signature
            and self.certificate_key_fingerprint == sha256_bytes(key)
            and hmac.compare_digest(expected, self.certificate_signature)
        )

    @property
    def passed(self) -> bool:
        # If no checker key is available in the process environment, a
        # serialized object cannot silently become proof authority.
        return self.verify()

    def to_dict(self) -> dict[str, Any]:
        out = self.signed_record() | {
            "certificate_signature": self.certificate_signature,
            "certificate_digest": self.certificate_digest,
        }
        out["passed"] = self.passed
        return out


def verify_formal_certificate(
    envelope: FormalCertificate | dict[str, Any], *,
    env: dict[str, str] | None = None,
    expected_source_hash: str,
    expected_environment_id: str,
    expected_type_hash: str,
    expected_claim_bindings: dict[str, str],
    required_artifact_hashes: tuple[str, ...] = (),
    expected_declaration_name: str | None = None,
) -> bool:
    """Verify a serialized formal-certificate envelope and all caller bindings.

    Truth admission should call this function with values independently derived
    from the Evidence record.  Merely copying booleans from an envelope is not a
    verification operation.
    """
    if isinstance(envelope, FormalCertificate):
        certificate = envelope
    elif isinstance(envelope, dict):
        try:
            values = dict(envelope)
            values.pop("passed", None)
            supplied_digest = values.pop("certificate_digest", "")
            for field_name in (
                "transitive_axioms", "placeholder_findings", "unsafe_findings",
                "artifact_hashes",
            ):
                values[field_name] = tuple(values.get(field_name, ()))
            values["claim_bindings"] = tuple(
                (str(item[0]), str(item[1])) for item in values.get("claim_bindings", ())
            )
            certificate = FormalCertificate(**values)
            if supplied_digest and supplied_digest != certificate.certificate_digest:
                return False
        except (KeyError, TypeError, ValueError):
            return False
    else:
        return False
    expected_claims = tuple(sorted(expected_claim_bindings.items()))
    required_artifacts = set(required_artifact_hashes)
    return bool(
        certificate.verify(env=env)
        and certificate.source_hash == expected_source_hash
        and certificate.environment_id == expected_environment_id
        and certificate.expected_type_hash == expected_type_hash
        and certificate.candidate_type_hash == expected_type_hash
        and certificate.claim_bindings == expected_claims
        and required_artifacts.issubset(set(certificate.artifact_hashes))
        and (
            expected_declaration_name is None
            or certificate.declaration_name == expected_declaration_name
        )
    )


@dataclass(frozen=True)
class EquivalenceAttempt:
    relation: str
    verdict: str          # equivalent | plausibly_corresponding | not_equivalent
    proof_artifact_hash: str = ""


@dataclass(frozen=True)
class CheckedEquivalenceProof:
    """A checked biconditional (or pair of implications) bound to both inputs."""

    declaration_a_hash: str
    declaration_b_hash: str
    relation: str
    certificate: FormalCertificate
    proof_artifact_hash: str

    def valid_for(
        self, declaration_a: str, declaration_b: str, relation: str,
        *, env: dict[str, str] | None = None,
    ) -> bool:
        expected_target = _equivalence_target_hash(declaration_a, declaration_b, relation)
        return bool(
            self.certificate.verify(env=env)
            and self.relation == relation
            and relation in {"iff", "implication_pair"}
            and self.declaration_a_hash == sha256_hex(declaration_a)
            and self.declaration_b_hash == sha256_hex(declaration_b)
            and self.certificate.expected_type_hash == expected_target
            and self.certificate.candidate_type_hash == expected_target
            and self.proof_artifact_hash == self.certificate.proof_term_hash
        )


def _equivalence_target_hash(
    declaration_a: str, declaration_b: str, relation: str,
) -> str:
    if relation == "iff":
        expression = f"({declaration_a}) ↔ ({declaration_b})"
    elif relation == "implication_pair":
        expression = (
            f"(({declaration_a}) → ({declaration_b})) ∧ "
            f"(({declaration_b}) → ({declaration_a}))"
        )
    else:
        return ""
    return sha256_hex(expression)


class LeanService:
    """The Lean service API. ``kernel_runner`` performs the real build."""

    checker_id = "unavailable"
    checker_version = "unavailable"

    def __init__(self, *, kernel_runner: Any = None,
                 independent_checker: Any = None,
                 axiom_whitelist: frozenset[str] = DEFAULT_AXIOM_WHITELIST,
                 checker_env: dict[str, str] | None = None):
        self._kernel_runner = kernel_runner
        self._independent_checker = independent_checker
        self.axiom_whitelist = axiom_whitelist
        self._checker_env = dict(checker_env) if checker_env is not None else None

    def create_environment(self, *, lean_version: str, mathlib_commit: str,
                           project_hash: str, trust_policy: str = "classical-whitelist",
                           imports: tuple[str, ...] = (), options: dict | None = None) -> LeanEnvironment:
        return LeanEnvironment(lean_version, mathlib_commit, project_hash, trust_policy,
                               imports, dict(options or {}))

    def elaborate(self, *, environment: LeanEnvironment, source: str, declaration_name: str) -> dict:
        try:
            type_sig = extract_declaration_type(source, declaration_name)
        except LeanServiceError as exc:
            return {"ast_hash": "", "diagnostics": [str(exc)], "goals": [], "type": ""}
        return {
            "ast_hash": sha256_hex(strip_comments(source)),
            "diagnostics": [],
            "goals": [] if not has_placeholder(source) else ["open goal (sorry/admit present)"],
            "type": type_sig,
            "type_hash": sha256_hex(type_sig),
            # This method performs a conservative source scan only.  It must not
            # masquerade as Lean elaboration when no trusted checker is present.
            "trusted_elaboration": False,
            "backend": "static_source_scan",
        }

    def goal_state(self, *, environment: LeanEnvironment, local_context: tuple[str, ...],
                   target_expression: str) -> GoalCapsule:
        return GoalCapsule(environment.environment_id, local_context, target_expression,
                           environment.trust_policy)

    def transitive_axioms(self, *, source: str, print_axioms_runner: Callable[[], list[str]] | None = None) -> list[str]:
        """Compute the transitive axiom set.

        Real closure needs Lean's ``#print axioms`` (injected as
        ``print_axioms_runner``). The static fallback is a conservative
        approximation from the source and is marked as such by the caller.
        """
        if print_axioms_runner is not None:
            return list(print_axioms_runner())
        axioms = set(declared_axioms(source))
        if has_placeholder(source):
            axioms.add("sorryAx")
        if re.search(r"\bClassical\b|Mathlib", source):
            axioms |= set(DEFAULT_AXIOM_WHITELIST)
        return sorted(axioms)

    def verify_declaration(
        self, *, environment: LeanEnvironment, source: str, declaration_name: str,
        expected_type_hash: str, immutable_target_module_hash: str,
        verification_method: str = "local_lean_kernel",
        print_axioms_runner: Callable[[], list[str]] | None = None,
        kernel_result: Any = None,
        claim_bindings: dict[str, str] | None = None,
        artifact_hashes: tuple[str, ...] = (),
    ) -> FormalCertificate:
        """Produce a certificate; only a bound checker attestation may pass.

        ``kernel_result`` is retained solely for backwards-compatible parsing of
        old callers.  It is never trusted, regardless of whether it is ``True``,
        ``"kernel_verified"``, or an object with a similarly named status.
        """
        placeholders = tuple(["sorry/admit"] if has_placeholder(source) else [])
        unsafe = tuple(native_findings(source))
        request = CheckerRequest(
            environment_id=environment.environment_id,
            source_hash=sha256_hex(source),
            declaration_name=declaration_name,
            expected_type_hash=expected_type_hash,
            immutable_target_module_hash=immutable_target_module_hash,
            trust_policy_hash=sha256_hex(environment.trust_policy),
        )
        attestation = self._run_kernel(request, kernel_result)
        attested = bool(
            attestation is not None
            and verification_method == LOCAL_KERNEL_METHOD
            and attestation.verify_for(request, env=self._checker_env)
        )

        if attested:
            if attestation is None:
                raise LeanServiceError("attested checker result is unavailable")
            axioms = tuple(attestation.transitive_axioms)
            candidate_type_hash = attestation.candidate_type_hash
            candidate_declaration_hash = attestation.candidate_declaration_hash
            proof_term_hash = attestation.proof_term_hash
            placeholders = tuple(dict.fromkeys((*placeholders, *attestation.placeholder_findings)))
            unsafe = tuple(dict.fromkeys((*unsafe, *attestation.unsafe_findings)))
            checker_id = attestation.checker_id
            checker_version = attestation.checker_version
            checker_trust_base = attestation.checker_trust_base
            checker_log = attestation.checker_log_hash
            source_tree_hash = attestation.source_tree_hash
        else:
            # Static findings remain useful diagnostics, but are not transitive
            # kernel evidence and cannot establish an elaborated type match.
            axioms = tuple(
                self.transitive_axioms(
                    source=source, print_axioms_runner=print_axioms_runner
                )
            )
            try:
                candidate_type_hash = sha256_hex(
                    extract_declaration_type(source, declaration_name)
                )
            except LeanServiceError:
                candidate_type_hash = ""
            candidate_declaration_hash = candidate_type_hash
            proof_term_hash = sha256_hex(strip_comments(source))
            checker_id = self.checker_id
            checker_version = self.checker_version
            checker_trust_base = ""
            checker_log = ""
            source_tree_hash = sha256_hex(source)

        whitelist_ok = set(axioms).issubset(self.axiom_whitelist) and not (
            set(axioms) & FORBIDDEN_AXIOMS
        )
        target_matches = bool(attested and candidate_type_hash == expected_type_hash)
        kernel_ok = bool(attested)

        independent_id = ""
        if attested and attestation is not None \
                and isinstance(self._independent_checker, AttestedKernelRunner):
            try:
                independent = self._independent_checker.run(request)
                if independent.verify_for(request, env=self._checker_env) and (
                    independent.checker_id != attestation.checker_id
                    and independent.checker_binary_hash != attestation.checker_binary_hash
                    and independent.checker_trust_base != attestation.checker_trust_base
                ):
                    independent_id = independent.checker_id
            except LeanServiceError:
                independent_id = ""

        certificate = FormalCertificate(
            expected_type_hash=expected_type_hash,
            candidate_declaration_hash=candidate_declaration_hash,
            proof_term_hash=proof_term_hash,
            immutable_target_module_hash=immutable_target_module_hash,
            source_tree_hash=source_tree_hash,
            transitive_axioms=axioms,
            axiom_whitelist_ok=whitelist_ok,
            placeholder_findings=placeholders,
            unsafe_findings=unsafe,
            trust_policy_hash=sha256_hex(environment.trust_policy),
            checker_id=checker_id,
            checker_version=checker_version,
            independent_checker_id=independent_id,
            checker_log_hash=checker_log,
            kernel_verified=kernel_ok,
            target_type_matches=target_matches,
            verification_method=verification_method,
            candidate_type_hash=candidate_type_hash,
            environment_id=environment.environment_id,
            checker_attestation_hash=attestation.attestation_hash if attested and attestation else "",
            production_checker=bool(attested and attestation and attestation.production),
            clean_replay=bool(attested and attestation and attestation.clean_replay),
            network_disabled=bool(attested and attestation and attestation.network_disabled),
            axiom_closure_verified=bool(
                attested and attestation and attestation.axiom_closure_verified
            ),
            import_audit_verified=bool(
                attested and attestation and attestation.imports_audited
            ),
            immutable_target_isolated=bool(
                attested and attestation and attestation.immutable_target_isolated
            ),
            checker_trust_base=checker_trust_base,
            source_environment_bound=attested,
            source_hash=request.source_hash,
            declaration_name=declaration_name,
            claim_bindings=tuple(sorted((claim_bindings or {}).items())),
            artifact_hashes=tuple(sorted(set((
                *artifact_hashes,
                request.source_hash,
                candidate_declaration_hash,
                proof_term_hash,
                source_tree_hash,
                checker_log,
            )) - {""})),
        )
        if not attested:
            return certificate
        key = _checker_key(self._checker_env)
        unsigned = replace(
            certificate,
            certificate_key_fingerprint=sha256_bytes(key),
        )
        signature = hmac.new(
            key, canonical_json(unsigned.signed_record()).encode("utf-8"), "sha256"
        ).hexdigest()
        return replace(unsigned, certificate_signature=signature)

    def _run_kernel(
        self, request: CheckerRequest, kernel_result: Any,
    ) -> CheckerAttestation | None:
        if kernel_result is not None:
            return None
        if not isinstance(self._kernel_runner, AttestedKernelRunner):
            return None
        try:
            return self._kernel_runner.run(request)
        except LeanServiceError:
            return None

    def compare_statements(self, *, declaration_a: str, declaration_b: str, relation: str,
                           proof_artifact: str | CheckedEquivalenceProof | None = None) -> EquivalenceAttempt:
        """``equivalent`` only with a checked A↔B (or implication pair) artifact."""
        if isinstance(proof_artifact, CheckedEquivalenceProof) and proof_artifact.valid_for(
            declaration_a, declaration_b, relation, env=self._checker_env
        ):
            return EquivalenceAttempt(
                relation, "equivalent", proof_artifact.proof_artifact_hash
            )
        # A model judgment / backtranslation is never formal equivalence.
        return EquivalenceAttempt(relation, "plausibly_corresponding", "")
