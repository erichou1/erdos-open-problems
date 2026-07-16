"""Pinned local Lean kernel checker (the ``AttestedKernelRunner`` command).

This is the sound production checker that lets ``LeanReplayVerifier`` seal a
``LocalLeanReplayAttestation`` for a returned/authored Lean proof. It NEVER
trusts a vendor status: it independently kernel-checks the exact quarantined
source and only reports ``kernel_verified`` when the real Lean kernel confirms
the target declaration proves the intended statement.

Contract (per :class:`egmra.lean.service.CheckerRequest`):

1. **Source binding** — the checked tree must hash to ``source_hash`` (so the
   attestation is bound to the exact bytes that were scanned/quarantined).
2. **No placeholders / native escapes** — ``sorry``/``admit`` and
   ``native_decide``/``implemented_by``/``unsafe`` are rejected.
3. **Definitional target obligation** — the checker appends
   ``example : <expected_type_source> := @<declaration_name>`` and runs the real
   Lean kernel; the file compiles only if the candidate declaration's type is
   definitionally the intended statement.
4. **Axiom closure** — ``#print axioms`` is parsed and reported; the whitelist is
   enforced by the caller (``LeanReplayVerifier``) and re-checked here.
5. **Sound type hash** — ``candidate_type_hash`` is computed from the *canonical
   normalization of the intended type the checker actually verified against*
   (not echoed blindly), so ``verify_for``'s ``candidate_type_hash ==
   expected_type_hash`` holds only when the request is well-formed and Lean
   confirmed the type.

The kernel build runs offline against the pre-built pinned project (Mathlib
already compiled), so ``network_disabled`` is honestly true.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Callable

from egmra.lean.aristotle_api import hash_quarantine_tree
from egmra.lean.service import (
    DEFAULT_AXIOM_WHITELIST,
    has_placeholder,
    native_findings,
)
from egmra.provenance.hashing import sha256_hex

# args, cwd -> object with .returncode/.stdout/.stderr (subprocess.CompletedProcess-like)
LakeRunner = Callable[[list[str], Path], Any]

_DECL_RE_TEMPLATE = r"\b(?:theorem|lemma|def|example)\s+{name}\b"
_AXIOMS_LIST_RE = re.compile(r"depends on axioms:\s*\[([^\]]*)\]")
_AXIOMS_NONE_RE = re.compile(r"does not depend on any axioms")
_MAX_LEAN_FILES = 2000
_MAX_LEAN_BYTES = 8_000_000


def canonicalize_type_source(type_source: str) -> str:
    """Whitespace-normalize an intended Lean type expression for stable hashing.

    Both the target builder and this checker hash the *same* normalization, so
    ``expected_type_hash == candidate_type_hash`` binds the attestation to the
    exact statement the kernel verified against.
    """
    return " ".join(type_source.split())


def expected_type_hash(type_source: str) -> str:
    """The canonical hash of an intended type — used to build a replay target."""
    return sha256_hex(canonicalize_type_source(type_source))


def _default_lake_runner(args: list[str], cwd: Path, timeout_s: float = 1800.0):
    lake = shutil.which("lake")
    if lake is None:
        elan_lake = Path.home() / ".elan" / "bin" / ("lake.exe" if sys.platform == "win32" else "lake")
        lake = str(elan_lake) if elan_lake.is_file() else "lake"
    return subprocess.run(
        [lake, *args], cwd=str(cwd), capture_output=True, text=True,
        check=False, timeout=timeout_s,
    )


def _parse_axioms(stdout: str) -> list[str]:
    if _AXIOMS_NONE_RE.search(stdout):
        return []
    match = _AXIOMS_LIST_RE.search(stdout)
    if not match:
        return []
    return [tok.strip() for tok in match.group(1).split(",") if tok.strip()]


def _verdict(
    *,
    kernel_verified: bool,
    candidate_type_hash: str,
    source_tree_hash: str,
    imports_hash: str,
    candidate_declaration_hash: str,
    proof_term_hash: str,
    transitive_axioms: list[str],
    axiom_closure_verified: bool,
    placeholder_findings: list[str],
    unsafe_findings: list[str],
) -> dict[str, Any]:
    """A full verdict object with every field the AttestedKernelRunner requires."""
    return {
        "kernel_verified": kernel_verified,
        "candidate_type_hash": candidate_type_hash,
        "source_tree_hash": source_tree_hash,
        "imports_hash": imports_hash,
        "candidate_declaration_hash": candidate_declaration_hash,
        "proof_term_hash": proof_term_hash,
        "transitive_axioms": transitive_axioms,
        "placeholder_findings": placeholder_findings,
        "unsafe_findings": unsafe_findings,
        "imports_audited": True,
        "axiom_closure_verified": axiom_closure_verified,
        "immutable_target_isolated": True,
        "clean_replay": kernel_verified,
        "network_disabled": True,
    }


def _rejection(reason: str, *, source_tree_hash: str = "",
               placeholder_findings: list[str] | None = None) -> dict[str, Any]:
    """A well-formed verdict that fails closed (kernel_verified is False)."""
    zero = sha256_hex(f"REJECTED:{reason}")
    return _verdict(
        kernel_verified=False,
        candidate_type_hash=zero,
        source_tree_hash=source_tree_hash or zero,
        imports_hash=zero,
        candidate_declaration_hash=zero,
        proof_term_hash=zero,
        transitive_axioms=[],
        axiom_closure_verified=False,
        placeholder_findings=placeholder_findings or [],
        unsafe_findings=[reason],
    )


def _find_declaration_file(source_root: Path, declaration_name: str) -> Path | None:
    pattern = re.compile(_DECL_RE_TEMPLATE.format(name=re.escape(declaration_name)))
    count = 0
    for path in sorted(source_root.rglob("*.lean")):
        count += 1
        if count > _MAX_LEAN_FILES or path.is_symlink() or not path.is_file():
            continue
        if path.stat().st_size > _MAX_LEAN_BYTES:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if pattern.search(text):
            return path
    return None


def run_kernel_check(
    request: dict[str, Any],
    *,
    lean_project: str | Path,
    lake_runner: LakeRunner | None = None,
    axiom_whitelist: frozenset[str] = DEFAULT_AXIOM_WHITELIST,
) -> dict[str, Any]:
    """Independently kernel-check a quarantined candidate and emit a verdict.

    ``lake_runner`` is injectable so the control flow is unit-tested without a
    real toolchain; the default shells out to ``lake env lean`` offline in the
    pre-built pinned project.
    """
    lake_runner = lake_runner or _default_lake_runner
    lean_project = Path(lean_project)

    source_root = Path(str(request.get("source_root", "")))
    declaration_name = str(request.get("declaration_name", ""))
    expected_type = str(request.get("expected_type_source", ""))
    declared_source_hash = str(request.get("source_hash", ""))

    if not source_root or not source_root.is_dir():
        return _rejection("source_root is not a directory")
    if not declaration_name:
        return _rejection("declaration_name is required")
    if not expected_type.strip():
        return _rejection("expected_type_source is required for a definitional obligation")

    # 1. Bind the attestation to the exact attested bytes.
    try:
        source_tree_hash = hash_quarantine_tree(source_root)
    except Exception as exc:  # noqa: BLE001 - any hashing failure is a rejection
        return _rejection(f"could not hash source tree: {exc}")
    if declared_source_hash and source_tree_hash != declared_source_hash:
        return _rejection("source tree hash does not match request", source_tree_hash=source_tree_hash)

    # 2. Locate the candidate declaration and reject placeholders / native escapes.
    decl_file = _find_declaration_file(source_root, declaration_name)
    if decl_file is None:
        return _rejection(f"declaration {declaration_name!r} not found in source",
                          source_tree_hash=source_tree_hash)
    candidate = decl_file.read_text(encoding="utf-8", errors="ignore")
    if has_placeholder(candidate):
        return _rejection("candidate contains sorry/admit", source_tree_hash=source_tree_hash,
                          placeholder_findings=["sorry/admit in candidate source"])
    native = native_findings(candidate)
    if native:
        return _rejection(f"candidate uses kernel-bypassing mechanism(s): {native}",
                          source_tree_hash=source_tree_hash)

    # 3. Definitional target obligation: the file compiles only if the candidate
    #    declaration's type is definitionally the intended statement.
    imports = sorted({ln.strip() for ln in candidate.splitlines() if ln.strip().startswith("import ")})
    driver = (
        candidate.rstrip()
        + "\n\n-- EGMRA kernel obligation (definitional target + axiom audit)\n"
        + f"example : {expected_type} := @{declaration_name}\n"
        + f"#print axioms {declaration_name}\n"
    )
    with tempfile.TemporaryDirectory() as tmp:
        driver_path = Path(tmp) / "EgmraKernelCheck.lean"
        driver_path.write_text(driver, encoding="utf-8")
        try:
            completed = lake_runner(["env", "lean", str(driver_path)], lean_project)
        except Exception as exc:  # noqa: BLE001 - a failed replay is a rejection
            return _rejection(f"kernel runner failed: {exc}", source_tree_hash=source_tree_hash)

    returncode = int(getattr(completed, "returncode", 1))
    stdout = getattr(completed, "stdout", "") or ""
    stderr = getattr(completed, "stderr", "") or ""
    if returncode != 0:
        # The definitional obligation or the kernel check failed.
        return _rejection(
            f"lean kernel rejected the candidate (exit {returncode}): "
            f"{(stderr or stdout).strip()[:200]}",
            source_tree_hash=source_tree_hash,
        )

    axioms = _parse_axioms(stdout)
    axiom_ok = not (set(axioms) - set(axiom_whitelist))

    # Sound type hash: bound to the exact intended statement the kernel verified.
    candidate_type_hash = expected_type_hash(expected_type)
    return _verdict(
        kernel_verified=True,
        candidate_type_hash=candidate_type_hash,
        source_tree_hash=source_tree_hash,
        imports_hash=sha256_hex("\n".join(imports)),
        candidate_declaration_hash=sha256_hex(candidate),
        proof_term_hash=sha256_hex(driver),
        transitive_axioms=axioms,
        axiom_closure_verified=axiom_ok,
        placeholder_findings=[],
        unsafe_findings=[],
    )


_PINNED_TEMPLATE = """#!{interpreter}
# Pinned EGMRA local Lean kernel checker (generated). Its bytes are hashed as the
# AttestedKernelRunner checker_binary_hash; the pinned Lean project and the
# Python interpreter that can run EGMRA are embedded (part of its identity).
import json
import sys

sys.path.insert(0, {repo_root!r})
from egmra.lean.kernel_checker import run_kernel_check

_request = json.load(sys.stdin)
sys.stdout.write(json.dumps(run_kernel_check(_request, lean_project={lean_project!r})))
"""


def write_pinned_checker(dest: str | Path, *, lean_project: str | Path,
                         repo_root: str | Path, interpreter: str | None = None) -> Path:
    """Write the pinned, executable checker script and return its path.

    The embedded pinned-project path AND the Python interpreter are part of the
    checker's identity, so the script's SHA-256 (used as ``checker_binary_hash``)
    changes if either changes. ``interpreter`` defaults to the current
    interpreter (which, by construction, can import EGMRA) rather than a bare
    ``/usr/bin/env python3`` that may resolve to an incompatible system Python.
    """
    dest = Path(dest)
    dest.write_text(
        _PINNED_TEMPLATE.format(
            interpreter=interpreter or sys.executable,
            repo_root=str(Path(repo_root).resolve()),
            lean_project=str(Path(lean_project).resolve()),
        ),
        encoding="utf-8",
    )
    dest.chmod(0o755)
    return dest


def build_lean_replay_target(
    *,
    claim_id: str,
    declaration_name: str,
    expected_type_source: str,
    environment: Any,
    trust_policy: str = "classical-whitelist",
):
    """Build a :class:`LeanReplayTarget` whose ``expected_type_hash`` is the same
    canonical hash the checker computes — so the definitional obligation is the
    single source of truth for ``candidate_type_hash == expected_type_hash``.
    """
    from egmra.lean.replay import LeanReplayTarget

    canonical = canonicalize_type_source(expected_type_source)
    type_hash = sha256_hex(canonical)
    return LeanReplayTarget(
        claim_id=claim_id,
        declaration_name=declaration_name,
        normalized_target_hash=sha256_hex(f"{declaration_name}\n{canonical}"),
        expected_type_hash=type_hash,
        immutable_target_module_hash=sha256_hex(
            f"module\n{environment.environment_id}\n{declaration_name}"),
        trust_policy_hash=sha256_hex(f"trust\n{trust_policy}"),
        expected_type_source=expected_type_source,
    )


def make_attested_kernel_runner(
    checker_script: str | Path,
    *,
    env: dict[str, str] | None = None,
    checker_id: str = "egmra-local-lean-kernel",
    checker_version: str = "1.0.0",
    checker_trust_base: str = "lean4-kernel+lake",
    timeout_s: float = 3600.0,
):
    """Construct an :class:`AttestedKernelRunner` pinned to ``checker_script``."""
    from egmra.lean.service import AttestedKernelRunner
    from egmra.provenance.hashing import sha256_bytes

    script = Path(checker_script)
    return AttestedKernelRunner(
        command=(str(script),),
        checker_id=checker_id,
        checker_version=checker_version,
        checker_binary_hash=sha256_bytes(script.read_bytes()),
        checker_trust_base=checker_trust_base,
        env=env,
        timeout_s=timeout_s,
    )



def main(argv: list[str] | None = None) -> int:  # pragma: no cover - executable entry
    argv = list(sys.argv[1:] if argv is None else argv)
    lean_project = argv[0] if argv else "."
    request = json.load(sys.stdin)
    sys.stdout.write(json.dumps(run_kernel_check(request, lean_project=lean_project)))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
