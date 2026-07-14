"""L5 — hardening & release (spec §9.2 L5).

Eliminate placeholders/axioms/unsafe mechanisms; compute the transitive axiom
closure and enforce the whitelist; build from a clean pinned checkout with network
disabled; require a second checker/trust path for untrusted generated Lean; and
archive the full environment. A `FormalCertificate` only becomes releasable after
hardening passes.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from egmra.lean.service import FORBIDDEN_AXIOMS, FormalCertificate
from egmra.provenance.hashing import is_sha256


@dataclass(frozen=True)
class HardeningReport:
    certificate_passed: bool
    no_placeholders: bool
    no_unsafe: bool
    axiom_whitelist_ok: bool
    clean_offline_build: bool
    independent_checker_present: bool
    imports_minimized: bool
    archived: bool
    reasons: tuple[str, ...] = ()

    @property
    def releasable(self) -> bool:
        return all([
            self.certificate_passed, self.no_placeholders, self.no_unsafe,
            self.axiom_whitelist_ok, self.clean_offline_build,
            self.independent_checker_present, self.imports_minimized, self.archived,
        ])


@dataclass
class ArchiveManifest:
    source_tree_hash: str
    lake_manifest_hash: str
    toolchain: str
    build_log_hash: str
    container_hash: str
    theorem_hashes: tuple[str, ...] = field(default_factory=tuple)

    def valid_for(self, certificate: FormalCertificate) -> bool:
        """The archive must be complete and bound to the checked source tree."""
        return bool(
            self.source_tree_hash == certificate.source_tree_hash
            and is_sha256(self.source_tree_hash)
            and is_sha256(self.lake_manifest_hash)
            and self.toolchain.strip()
            and is_sha256(self.build_log_hash)
            and is_sha256(self.container_hash)
            and self.theorem_hashes
            and all(is_sha256(item) for item in self.theorem_hashes)
            and certificate.candidate_declaration_hash in self.theorem_hashes
        )


def harden(
    certificate: FormalCertificate, *, clean_offline_build: bool, imports_minimized: bool,
    untrusted_generated: bool, archive: ArchiveManifest | None,
    checker_env: dict[str, str] | None = None,
) -> HardeningReport:
    """Decide releasability of a formal artifact after the L5 checks."""
    reasons: list[str] = []
    no_placeholders = not certificate.placeholder_findings
    no_unsafe = not certificate.unsafe_findings
    whitelist_ok = certificate.axiom_whitelist_ok and not (
        set(certificate.transitive_axioms) & FORBIDDEN_AXIOMS
    )
    # Untrusted generated Lean needs a second, independent checker/trust path.
    independent_ok = (not untrusted_generated) or bool(certificate.independent_checker_id)
    offline_ok = bool(
        clean_offline_build and certificate.clean_replay and certificate.network_disabled
    )
    archive_ok = bool(archive is not None and archive.valid_for(certificate))
    if not no_placeholders:
        reasons.append("placeholder (sorry/admit) present")
    if not no_unsafe:
        reasons.append("unsafe/native mechanism present")
    if not whitelist_ok:
        reasons.append("axiom closure not within whitelist")
    if not offline_ok:
        reasons.append("no clean pinned offline build")
    if not independent_ok:
        reasons.append("untrusted generated Lean lacks an independent checker")
    if not imports_minimized:
        reasons.append("imports were not minimized/audited")
    if not archive_ok:
        reasons.append("release archive missing, incomplete, or not bound to the checked tree")
    return HardeningReport(
        certificate_passed=certificate.verify(env=checker_env),
        no_placeholders=no_placeholders,
        no_unsafe=no_unsafe,
        axiom_whitelist_ok=whitelist_ok,
        clean_offline_build=offline_ok,
        independent_checker_present=independent_ok,
        imports_minimized=imports_minimized,
        archived=archive_ok,
        reasons=tuple(reasons),
    )
