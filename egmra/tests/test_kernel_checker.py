"""Hermetic tests for the pinned local Lean kernel checker (sealed-attestation core).

These exercise the full checker contract with an injected fake ``lake`` runner —
no real toolchain required — including the soundness property that
``candidate_type_hash == expected_type_hash`` holds only when the request is
well-formed and the (simulated) kernel accepted the definitional obligation.
"""

from __future__ import annotations

import json
from types import SimpleNamespace

import pytest

from egmra.lean.aristotle_api import hash_quarantine_tree
from egmra.lean.kernel_checker import (
    build_lean_replay_target,
    canonicalize_type_source,
    expected_type_hash,
    make_attested_kernel_runner,
    run_kernel_check,
)
from egmra.lean.replay import LeanReplayTarget, LeanReplayVerifier
from egmra.lean.service import CheckerRequest, LeanEnvironment
from egmra.provenance.hashing import sha256_hex

_TYPE = "2 + 2 = 4"
_DECL = "egmra_live_check"


def _lake_ok(stdout: str = "'egmra_live_check' does not depend on any axioms"):
    return lambda args, cwd: SimpleNamespace(returncode=0, stdout=stdout, stderr="")


def _lake_fail(args, cwd):
    return SimpleNamespace(returncode=1, stdout="", stderr="type mismatch: 2 + 2 = 4")


def _source_tree(tmp_path, body="theorem egmra_live_check : 2 + 2 = 4 := rfl"):
    src = tmp_path / "quarantine" / "job"
    src.mkdir(parents=True)
    (src / "AristotleProject.lean").write_text(f"import Mathlib\n{body}\n", encoding="utf-8")
    return src


def _request(src, *, source_hash=None, expected_type=_TYPE, decl=_DECL):
    env = LeanEnvironment(lean_version="4.28.0", mathlib_commit="v4.28.0",
                          project_hash=sha256_hex("proj"))
    target = build_lean_replay_target(
        claim_id="goal", declaration_name=decl, expected_type_source=expected_type,
        environment=env)
    return CheckerRequest(
        environment_id=env.environment_id,
        source_hash=source_hash if source_hash is not None else hash_quarantine_tree(src),
        declaration_name=decl, expected_type_hash=target.expected_type_hash,
        immutable_target_module_hash=target.immutable_target_module_hash,
        trust_policy_hash=target.trust_policy_hash,
        source_root=str(src), expected_type_source=expected_type,
    ), env, target


def test_accepts_valid_proof_with_bound_type_hash(tmp_path):
    src = _source_tree(tmp_path)
    request, _env, target = _request(src)
    verdict = run_kernel_check(request.to_dict(), lean_project=tmp_path / "proj",
                               lake_runner=_lake_ok())
    assert verdict["kernel_verified"] is True
    assert verdict["clean_replay"] is True and verdict["network_disabled"] is True
    assert verdict["axiom_closure_verified"] is True
    assert verdict["transitive_axioms"] == []
    assert verdict["placeholder_findings"] == [] and verdict["unsafe_findings"] == []
    # Soundness: the checker's type hash equals the target's expected hash.
    assert verdict["candidate_type_hash"] == target.expected_type_hash
    assert verdict["candidate_type_hash"] == expected_type_hash(_TYPE)


def test_parses_classical_axiom_closure_within_whitelist(tmp_path):
    src = _source_tree(tmp_path)
    request, _env, _t = _request(src)
    stdout = "'egmra_live_check' depends on axioms: [propext, Classical.choice, Quot.sound]"
    verdict = run_kernel_check(request.to_dict(), lean_project=tmp_path / "proj",
                               lake_runner=_lake_ok(stdout))
    assert verdict["kernel_verified"] is True
    assert set(verdict["transitive_axioms"]) == {"propext", "Classical.choice", "Quot.sound"}
    assert verdict["axiom_closure_verified"] is True


def test_flags_axioms_outside_whitelist(tmp_path):
    src = _source_tree(tmp_path)
    request, _env, _t = _request(src)
    stdout = "'egmra_live_check' depends on axioms: [propext, sorryAx]"
    verdict = run_kernel_check(request.to_dict(), lean_project=tmp_path / "proj",
                               lake_runner=_lake_ok(stdout))
    # kernel returned 0 but the axiom closure escapes the whitelist -> not verifiable.
    assert verdict["axiom_closure_verified"] is False


def test_rejects_sorry_without_invoking_kernel(tmp_path):
    src = _source_tree(tmp_path, body="theorem egmra_live_check : 2 + 2 = 4 := by sorry")
    request, _env, _t = _request(src)

    def _boom(args, cwd):
        raise AssertionError("kernel must not run on a placeholder proof")

    verdict = run_kernel_check(request.to_dict(), lean_project=tmp_path / "proj",
                               lake_runner=_boom)
    assert verdict["kernel_verified"] is False
    assert verdict["placeholder_findings"]


def test_rejects_native_decide(tmp_path):
    src = _source_tree(tmp_path, body="theorem egmra_live_check : 2 + 2 = 4 := by native_decide")
    request, _env, _t = _request(src)
    verdict = run_kernel_check(request.to_dict(), lean_project=tmp_path / "proj",
                               lake_runner=_lake_ok())
    assert verdict["kernel_verified"] is False
    assert any("native" in f for f in verdict["unsafe_findings"])


def test_rejects_source_hash_mismatch(tmp_path):
    src = _source_tree(tmp_path)
    request, _env, _t = _request(src, source_hash=sha256_hex("not-the-tree"))
    verdict = run_kernel_check(request.to_dict(), lean_project=tmp_path / "proj",
                               lake_runner=_lake_ok())
    assert verdict["kernel_verified"] is False


def test_rejects_kernel_failure(tmp_path):
    src = _source_tree(tmp_path)
    request, _env, _t = _request(src)
    verdict = run_kernel_check(request.to_dict(), lean_project=tmp_path / "proj",
                               lake_runner=_lake_fail)
    assert verdict["kernel_verified"] is False


def test_rejects_missing_declaration(tmp_path):
    src = _source_tree(tmp_path, body="theorem other_thing : True := trivial")
    request, _env, _t = _request(src)
    verdict = run_kernel_check(request.to_dict(), lean_project=tmp_path / "proj",
                               lake_runner=_lake_ok())
    assert verdict["kernel_verified"] is False


def _echo_checker_script(tmp_path, verdict):
    script = tmp_path / "pinned_checker.py"
    payload = json.dumps(verdict)
    script.write_text(
        "#!/usr/bin/env python3\n"
        "import sys\n"
        "sys.stdin.read()\n"
        f"sys.stdout.write({payload!r})\n",
        encoding="utf-8",
    )
    script.chmod(0o755)
    return script


def test_verdict_is_accepted_by_attested_runner_and_seals_replay(tmp_path):
    # A run_kernel_check verdict, run through the real AttestedKernelRunner (which
    # signs it) and verify_for, must be accepted AND seal a local replay
    # attestation via LeanReplayVerifier — the full sealed-attestation contract.
    src = _source_tree(tmp_path)
    request, env, target = _request(src)
    verdict = run_kernel_check(request.to_dict(), lean_project=tmp_path / "proj",
                               lake_runner=_lake_ok())
    assert verdict["kernel_verified"] is True

    script = _echo_checker_script(tmp_path, verdict)
    runner = make_attested_kernel_runner(script)

    attestation = runner.run(request)
    assert attestation.verify_for(request) is True

    verifier = LeanReplayVerifier(checker=runner, environment=env, target=target)
    sealed = verifier(src)
    assert sealed is not None
    assert sealed.claim_id == "goal"
    assert sealed.source_hash == hash_quarantine_tree(src)


def test_tampered_expected_type_breaks_the_hash_binding(tmp_path):
    # If a request pairs a real expected_type_hash with a DIFFERENT
    # expected_type_source, the checker's recomputed candidate_type_hash no longer
    # matches -> verify_for fails closed (no blind echo).
    src = _source_tree(tmp_path)
    request, _env, _t = _request(src)
    tampered = CheckerRequest(**(request.to_dict() | {"expected_type_source": "True"}))
    verdict = run_kernel_check(tampered.to_dict(), lean_project=tmp_path / "proj",
                               lake_runner=_lake_ok())
    # The checker binds candidate_type_hash to the source it actually verified.
    assert verdict["candidate_type_hash"] == expected_type_hash("True")
    assert verdict["candidate_type_hash"] != request.expected_type_hash


def test_target_builder_hash_matches_checker(tmp_path):
    target = build_lean_replay_target(
        claim_id="goal", declaration_name=_DECL, expected_type_source=_TYPE,
        environment=LeanEnvironment(lean_version="4.28.0", mathlib_commit="v4.28.0",
                                    project_hash=sha256_hex("p")))
    assert target.expected_type_hash == expected_type_hash(_TYPE)
    assert target.expected_type_source == _TYPE
    assert canonicalize_type_source("2 +  2\t= 4") == _TYPE
