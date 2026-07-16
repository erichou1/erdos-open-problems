"""Anti-false-rejection mitigations at the formal verification boundary.

A fail-closed pipeline must never let INFRASTRUCTURE noise or MISSING HUMAN
PAPERWORK look like mathematical rejection. Three channels are pinned here:

* A checker EXCEPTION (lake crash/OOM/timeout) is retried once and recorded
  as ``formal_verification_infra_retry`` — only a repeated failure surfaces
  as ``formal_verification_error``. A genuine kernel REJECTION
  (``passed=False``) is never retried and never masked.
* When the warm development REPL accepts an obligation the sealed checker
  rejects, a ``checker_discrepancy`` sentinel is recorded for operator
  review — the sealed verdict stands, but the false-rejection signature is
  no longer silent.
* ``egmra pending-correspondence`` lists kernel-PASSED proofs that cannot
  promote only because the human formal-correspondence review has not been
  signed, with a fill-in signing command. Discovery becomes cheap; the
  human decision stays human.
"""

from __future__ import annotations

import json

from egmra.lean.verdict_cache import SealedLeanService
from egmra.orchestrator.loop import research
from egmra.tests.test_gap_closures import (
    TRUE_STATEMENT,
    _corpus,
    _enforcer,
    _FakeCert,
    _FakeLeanService,
    _FormalCandidateWorker,
    _FakeFormalizer,
    _status,
)
from egmra.tests.test_wave3 import _ScriptedDevService


class _FlakyLeanService(_FakeLeanService):
    """Raises transiently N times before behaving like the fake service."""

    def __init__(self, crash_first: int, fail_first: int = 0):
        super().__init__(fail_first=fail_first)
        self.crash_first = crash_first
        self.crashes = 0

    def verify_declaration(self, *, source, **kwargs):
        if self.crashes < self.crash_first:
            self.crashes += 1
            raise TimeoutError("lake env lean timed out (transient)")
        return super().verify_declaration(source=source, **kwargs)


def _research(tmp_path, *, service, problem_id, formalizer=None, dev=None,
              repair_rounds=0):
    return research(
        problem_id=problem_id, source_bytes=TRUE_STATEMENT,
        source_id=problem_id, budget=100.0, enforcer=_enforcer(),
        worker=_FormalCandidateWorker(formalizer), goal_claim_id="goal",
        events_path=tmp_path / f"{problem_id}.jsonl",
        retrieval_corpus=_corpus(), status_claims=_status(problem_id),
        lean_service=service, informal_only=False,
        lean_repair_rounds=repair_rounds, dev_lean_service=dev,
        max_iterations=1,
    )


def test_transient_checker_crash_is_retried_not_a_rejection(tmp_path):
    service = _FlakyLeanService(crash_first=1, fail_first=0)
    result = _research(tmp_path, service=service, problem_id="infra-retry")
    # The retry succeeded: a certificate was produced and recorded.
    assert len(service.verify_calls) == 1
    assert any(r.get("passed") for r in result.formal_reports)
    assert any(f.startswith("formal_verification_infra_retry:")
               for f in result.failures)
    assert not any(f.startswith("formal_verification_error:")
                   for f in result.failures)


def test_repeated_checker_crash_still_fails_closed(tmp_path):
    service = _FlakyLeanService(crash_first=99)
    result = _research(tmp_path, service=service, problem_id="infra-dead")
    assert not result.formal_reports
    assert any(f.startswith("formal_verification_error:") for f in result.failures)


def test_kernel_rejection_is_never_retried_as_infra(tmp_path):
    service = _FakeLeanService(fail_first=99)      # rejects, never raises
    result = _research(tmp_path, service=service, problem_id="honest-reject")
    assert len(service.verify_calls) == 1          # exactly one sealed check
    assert not any("infra_retry" in f for f in result.failures)
    assert all(not r.get("passed") for r in result.formal_reports)


def test_dev_accepts_sealed_rejects_raises_discrepancy_sentinel(tmp_path):
    service = _FakeLeanService(fail_first=99)      # sealed checker rejects all
    dev = _ScriptedDevService(fail_first=0)        # dev REPL accepts all
    formalizer = _FakeFormalizer(sources=("theorem a1 : True := t1",))
    result = _research(tmp_path, service=service, problem_id="discrepancy",
                       formalizer=formalizer, dev=dev, repair_rounds=1)
    assert any(f.startswith("checker_discrepancy:")
               and "dev_accepted_sealed_rejected" in f
               for f in result.failures)


def test_pending_correspondence_lists_kernel_passed_unsigned_proofs(tmp_path, capsys):
    from egmra.cli import main

    # A PASSING certificate lands in the verdict cache with context...
    class _PassingService:
        def create_environment(self, **kwargs):
            from types import SimpleNamespace
            return SimpleNamespace(environment_id="e" * 64)

        def verify_declaration(self, **kwargs):
            cert = _FakeCert(True)
            cert.verify = lambda: True
            cert.to_dict = lambda: {
                "kernel_verified": True, "target_type_matches": True,
                "axiom_whitelist_ok": True, "expected_type_hash": "h" * 64,
            }
            return cert

    ckpts = tmp_path / "ckpts"
    sealed = SealedLeanService(
        _PassingService(), cache_dir=ckpts / "erdos-999" / "kernel_verdicts",
        problem_id="erdos-999")
    sealed.verify_declaration(
        environment=sealed.create_environment(), source="theorem d : True := trivial",
        declaration_name="erdos_999_main", expected_type_hash="h" * 64,
        immutable_target_module_hash="m" * 64, expected_type_source="True")
    reviews = tmp_path / "reviews"
    reviews.mkdir()
    (reviews / "intent-erdos-999.json").write_text("{}")

    rc = main(["pending-correspondence", "--checkpoint-dir", str(ckpts),
               "--reviews-dir", str(reviews)])
    assert rc == 0
    report = json.loads(capsys.readouterr().out)
    assert report["count"] == 1
    row = report["pending"][0]
    assert row["problem_id"] == "erdos-999"
    assert row["declaration_name"] == "erdos_999_main"
    assert row["intent_review_present"] is True
    assert "sign-review correspondence" in row["ready_to_sign"]
    # ...and disappears once the human signs the correspondence review.
    (reviews / "correspondence-erdos-999.json").write_text("{}")
    main(["pending-correspondence", "--checkpoint-dir", str(ckpts),
          "--reviews-dir", str(reviews)])
    assert json.loads(capsys.readouterr().out)["count"] == 0
