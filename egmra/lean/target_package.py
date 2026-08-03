"""L0 — semantic target package (spec §9.2 L0).

Creates 2-3 Lean statement candidates for an approved interpretation, backtranslates
them, runs example / anti-example / paraphrase / mutation tests, and freezes the
approved declaration hash. Proving the wrong Lean theorem is failure, so the
package is the gate between an interpretation and any proof search.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from egmra.provenance.hashing import content_id, sha256_hex


@dataclass(frozen=True)
class LeanCandidate:
    declaration_name: str
    statement: str
    backtranslation: str
    definitions_reused: tuple[str, ...] = ()

    def type_hash(self) -> str:
        return sha256_hex(self.statement)


@dataclass
class TargetPackage:
    interpretation_id: str
    informal_claim: str
    interpretation_approved: bool = False
    candidates: list[LeanCandidate] = field(default_factory=list)
    example_lemmas: list[str] = field(default_factory=list)
    anti_example_lemmas: list[str] = field(default_factory=list)
    paraphrase_invariant: bool = False
    mutation_covariant: bool = False
    approved_declaration_hash: str = ""

    @property
    def frozen(self) -> bool:
        return bool(self.approved_declaration_hash)

    def approve(self, declaration_name: str) -> str:
        if not self.interpretation_approved:
            raise ValueError("L0 target cannot freeze before interpretation approval")
        if not self.example_lemmas or not self.anti_example_lemmas:
            raise ValueError("L0 target requires recorded example and anti-example tests")
        if not self.paraphrase_invariant or not self.mutation_covariant:
            raise ValueError("L0 target failed paraphrase/mutation semantic probes")
        if any(not candidate.backtranslation.strip() for candidate in self.candidates):
            raise ValueError("every L0 candidate requires a backtranslation")
        cand = next((c for c in self.candidates if c.declaration_name == declaration_name), None)
        if cand is None:
            raise KeyError(f"no candidate named {declaration_name!r}")
        self.approved_declaration_hash = cand.type_hash()
        return self.approved_declaration_hash

    def to_dict(self) -> dict:
        return {
            "interpretation_id": self.interpretation_id,
            "informal_claim": self.informal_claim,
            "interpretation_approved": self.interpretation_approved,
            "candidates": [c.__dict__ | {"type_hash": c.type_hash()} for c in self.candidates],
            "example_lemmas": list(self.example_lemmas),
            "anti_example_lemmas": list(self.anti_example_lemmas),
            "paraphrase_invariant": self.paraphrase_invariant,
            "mutation_covariant": self.mutation_covariant,
            "approved_declaration_hash": self.approved_declaration_hash,
            "frozen": self.frozen,
            "package_hash": content_id({
                "interp": self.interpretation_id,
                "candidates": sorted(c.type_hash() for c in self.candidates),
            }),
        }


def build_target_package(
    *, interpretation_id: str, informal_claim: str, candidates: list[LeanCandidate],
    example_lemmas: list[str] | None = None, anti_example_lemmas: list[str] | None = None,
    paraphrase_invariant: bool = True, mutation_covariant: bool = True,
    interpretation_approved: bool = False,
) -> TargetPackage:
    if not 2 <= len(candidates) <= 3:
        raise ValueError("L0 requires 2-3 Lean statement candidates")
    if len({candidate.declaration_name for candidate in candidates}) != len(candidates):
        raise ValueError("L0 candidate declaration names must be unique")
    if len({candidate.type_hash() for candidate in candidates}) != len(candidates):
        raise ValueError("L0 candidates must not duplicate the same formal statement")
    return TargetPackage(
        interpretation_id=interpretation_id,
        informal_claim=informal_claim,
        interpretation_approved=interpretation_approved,
        candidates=list(candidates),
        example_lemmas=list(example_lemmas or []),
        anti_example_lemmas=list(anti_example_lemmas or []),
        paraphrase_invariant=paraphrase_invariant,
        mutation_covariant=mutation_covariant,
    )
