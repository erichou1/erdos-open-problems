"""Verified leverage: formal targets in campaigns, verdict cache, lemma library.

Three mechanisms grounded in the ATP literature (LeanDojo/ReProver: premise
selection is the bottleneck; DeepSeek-Prover-V2: solved subgoals compound):

* campaigns hand each worker the community's exact Lean statement of its
  problem (read-only prompt context — correspondence review still gates use);
* identical kernel re-checks replay the ORIGINAL signed certificate (its own
  HMAC re-verified on load; any tamper/mismatch falls open to a live check);
* every kernel-PASSED lemma is sealed into a durable library and offered back
  through retrieval with honest kernel_checked provenance.
"""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

from egmra.lean.service import FormalCertificate
from egmra.lean.verdict_cache import SealedLeanService
from egmra.retrieval.lemma_library import append_sealed_lemma, load_lemma_records


def _passing_certificate(**overrides) -> FormalCertificate:
    import hmac as _hmac

    from egmra.lean.service import _checker_key, sha256_bytes
    from egmra.provenance.hashing import canonical_json

    base = dict(
        expected_type_hash="a" * 64, candidate_declaration_hash="b" * 64,
        proof_term_hash="c" * 64, immutable_target_module_hash="d" * 64,
        source_tree_hash="e" * 64, transitive_axioms=("Classical.choice",),
        axiom_whitelist_ok=True, placeholder_findings=(), unsafe_findings=(),
        trust_policy_hash="f" * 64, checker_id="pinned-checker",
        checker_version="1", independent_checker_id="mechanical-checks-v1",
        checker_log_hash="1" * 64, kernel_verified=True,
        target_type_matches=True, verification_method="local_lean_kernel",
        candidate_type_hash="a" * 64, environment_id="4" * 64,
        checker_attestation_hash="2" * 64, production_checker=True,
        clean_replay=True, network_disabled=True, axiom_closure_verified=True,
        import_audit_verified=True, immutable_target_isolated=True,
        checker_trust_base="lean4", source_environment_bound=True,
        source_hash="3" * 64, declaration_name="erdos_lemma",
        claim_bindings=(("goal", "9" * 64),),
        artifact_hashes=("d" * 64, "e" * 64),
    )
    base.update(overrides)
    key = _checker_key(None)
    unsigned = replace(FormalCertificate(**base),
                       certificate_key_fingerprint=sha256_bytes(key),
                       certificate_signature="")
    signature = _hmac.new(
        key, canonical_json(unsigned.signed_record()).encode("utf-8"),
        "sha256").hexdigest()
    return replace(unsigned, certificate_signature=signature)


class _CountingService:
    def __init__(self, certificate):
        self.certificate = certificate
        self.calls = 0

    def create_environment(self, **kw):
        return SimpleNamespace(environment_id="env-1")

    def verify_declaration(self, **kw):
        self.calls += 1
        return self.certificate


def _verify_kwargs(source="theorem t : True := trivial"):
    return dict(
        environment=SimpleNamespace(environment_id="env-1"), source=source,
        declaration_name="erdos_lemma", expected_type_hash="a" * 64,
        immutable_target_module_hash="d" * 64,
        expected_type_source="True", claim_bindings={"goal": "9" * 64})


# ---------------------------------------------------------------------------
# verdict cache


def test_identical_recheck_replays_the_signed_certificate(tmp_path):
    cert = _passing_certificate()
    service = _CountingService(cert)
    sealed = SealedLeanService(service, cache_dir=tmp_path / "verdicts")
    first = sealed.verify_declaration(**_verify_kwargs())
    second = sealed.verify_declaration(**_verify_kwargs())
    assert service.calls == 1                       # kernel paid exactly once
    assert second.to_dict() == first.to_dict()      # identical certificate
    assert second.verify()                          # original signature intact
    assert (sealed.hits, sealed.misses) == (1, 1)


def test_different_obligation_or_source_never_hits(tmp_path):
    service = _CountingService(_passing_certificate())
    sealed = SealedLeanService(service, cache_dir=tmp_path / "verdicts")
    sealed.verify_declaration(**_verify_kwargs())
    sealed.verify_declaration(**_verify_kwargs(source="theorem t : True := by trivial"))
    other = _verify_kwargs()
    other["claim_bindings"] = {"goal": "8" * 64}    # different binding context
    sealed.verify_declaration(**other)
    assert service.calls == 3


def test_tampered_cache_entry_falls_open_to_live_kernel(tmp_path):
    service = _CountingService(_passing_certificate())
    sealed = SealedLeanService(service, cache_dir=tmp_path / "verdicts")
    sealed.verify_declaration(**_verify_kwargs())
    entry = next((tmp_path / "verdicts").glob("verdict.*.json"))
    record = json.loads(entry.read_text())
    record["certificate"]["kernel_verified"] = True
    record["certificate"]["declaration_name"] = "forged_lemma"   # break signature
    entry.write_text(json.dumps(record))
    sealed.verify_declaration(**_verify_kwargs())
    assert service.calls == 2                       # live re-check, not the forgery


def test_failed_verdicts_recheck_live_and_never_seal(tmp_path):
    rejected = _passing_certificate(kernel_verified=False,
                                    unsafe_findings=("kernel rejected",))
    assert rejected.passed is False        # qualification fails despite signing
    library = tmp_path / "library.jsonl"
    service = _CountingService(rejected)
    sealed = SealedLeanService(service, cache_dir=tmp_path / "verdicts",
                               lemma_library=library)
    assert sealed.verify_declaration(**_verify_kwargs()).passed is False
    assert sealed.verify_declaration(**_verify_kwargs()).passed is False
    assert service.calls == 2              # rejections re-check live (not cached)
    assert load_lemma_records(library) == []


# ---------------------------------------------------------------------------
# lemma library


def test_passing_lemma_is_sealed_and_retrievable(tmp_path):
    library = tmp_path / "library.jsonl"
    service = _CountingService(_passing_certificate())
    sealed = SealedLeanService(service, cache_dir=None, lemma_library=library,
                               problem_id="erdos-312")
    sealed.verify_declaration(**_verify_kwargs())
    records = load_lemma_records(library)
    assert len(records) == 1
    record = records[0]
    assert record.proof_status == "kernel_checked"
    assert record.independent_verification_status == "kernel_checked"
    assert "erdos_lemma" in record.canonical_statement
    assert record.source_uri.startswith("egmra://lemma-library/")
    # Idempotent: the same sealed lemma is stored once.
    sealed2 = SealedLeanService(_CountingService(_passing_certificate()),
                                lemma_library=library, problem_id="erdos-312")
    sealed2.verify_declaration(**_verify_kwargs())
    assert len(load_lemma_records(library)) == 1


def test_failed_lemma_is_never_sealed(tmp_path):
    library = tmp_path / "library.jsonl"
    rejected = _passing_certificate(kernel_verified=False)
    sealed = SealedLeanService(_CountingService(rejected), lemma_library=library)
    sealed.verify_declaration(**_verify_kwargs())
    assert load_lemma_records(library) == []
    assert load_lemma_records(None) == []


def test_library_degenerate_states_fail_open(tmp_path):
    bad = tmp_path / "bad.jsonl"
    bad.write_text("not json\n{\"schema_version\": 99}\n")
    assert load_lemma_records(bad) == []
    assert append_sealed_lemma(tmp_path / "lib.jsonl", problem_id="p",
                               declaration_name="", expected_type_source="T",
                               source="", certificate={}) is False


# ---------------------------------------------------------------------------
# campaign formal-target loading convention


def test_campaign_target_naming_convention(tmp_path):
    """Both <problem_id>.lean and erdos_<N>.lean resolve (the fetch/manual styles)."""
    import egmra.cli as cli_module

    targets = tmp_path / "targets"
    targets.mkdir()
    (targets / "erdos-312.lean").write_text("theorem erdos_312 : True := trivial")
    (targets / "erdos_495.lean").write_text("theorem erdos_495 : True := trivial")
    for name in ("erdos-312.lean", "erdos_495.lean"):
        loaded = cli_module._load_formal_target(targets / name)
        assert loaded.startswith("theorem")
