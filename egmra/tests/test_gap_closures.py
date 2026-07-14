"""Gap closures: bounded Lean repair, audited literature imports, checkpoints.

Three previously identified pipeline gaps, each fail-closed by construction:

* **Autonomous Lean repair** — a kernel-REJECTED candidate goes back to the
  configured formalizer with the pinned checker's diagnostics for a bounded
  number of rounds; the obligation never changes and every repaired source is
  re-checked by the same pinned kernel.  Exhausted repairs leave the candidate
  rejected exactly as before.
* **Audited literature→lemma imports** — the model may only CITE records from
  the frozen retrieval packet; provenance comes from the packet, a mechanical
  overlap gate rejects non-sequiturs, one source records provenance only
  (``AUDITED_SOURCE`` never supports), and support requires two passing
  records from distinct hosts.
* **Durable within-problem checkpoints** — after each completed branch a
  signed checkpoint commits to the exact event-log prefix and graph view;
  ``resume()`` verifies it against the stored log.  A write failure is an
  operational failure string, never a mathematical verdict.
"""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from egmra.lean.formalizer import build_formalization_prompt
from egmra.orchestrator import DeterministicWorker, research, resume
from egmra.orchestrator.checkpoint import Checkpoint
from egmra.orchestrator.loop import (
    ACTOR,
    WorkerOutput,
    _admit_literature_imports,
    _import_applicable,
    _supports_repair,
)
from egmra.orchestrator.runner_worker import (
    WorkerResponseSchemaError,
    parse_worker_response,
)
from egmra.compute.spec import ExperimentSpec
from egmra.corpus.status import StatusClaim
from egmra.intake import build_problem_contract
from egmra.intake.review import interpretation_review_hash, sign_intent_certificate
from egmra.policy import PolicyEnforcer, sign_policy
from egmra.provenance.hashing import sha256_hex
from egmra.retrieval.records import TheoremRecord
from egmra.truth.entities import Interpretation, IntentCertificate, Problem, Verdict
from egmra.truth.events import EventLog
from egmra.truth.graph import EpistemicGraph
from egmra.truth.router import EvidenceRouter

TRUE_STATEMENT = b"Prove that for all natural numbers n, n squared is at least 0."
POLICY_ENV = {"EGMRA_POLICY_KEY": "gap-closure-test-policy-key-32-bytes"}
FINITE_CODE = """
def experiment(inputs):
    n = inputs["n"]
    ok = all((k * k) >= 0 for k in range(n + 1))
    return {"result": ok, "coverage": "k in 0..n exhaustive"}
"""


def _enforcer():
    policy = sign_policy({
        "claim_graph": True, "literature_retrieval": True,
        "computation_service": True, "promotion": False,
        "formal_promotion": False,
    }, env=POLICY_ENV)
    return PolicyEnforcer(policy, verification_env=POLICY_ENV)


def _corpus():
    return [TheoremRecord(
        theorem_id="thm-sq", canonical_statement="squares are nonnegative",
        conclusion="n squared is nonnegative", source_uri="https://a.example/sq",
        source_version="v1", source_content_hash="h",
        verbatim_theorem_and_hypothesis_extract="for all n, n squared >= 0")]


def _status(problem_id):
    return [StatusClaim(
        problem_id=problem_id, status="open", source="local://test-status",
        review_date="2026-07-13", source_independence="test-fixture")]


def _intent(problem_id, *, source_id):
    contract = build_problem_contract(
        problem_id=problem_id, source_bytes=TRUE_STATEMENT, source_id=source_id,
        predicate=lambda n: n * n >= 0)
    interp = contract.lattice.nodes[0]
    return sign_intent_certificate(IntentCertificate(
        certificate_id=f"intent-{problem_id}",
        source_bytes_hash=contract.source_bytes_hash,
        interpretation_hash=interpretation_review_hash(interp),
        informal_claim_hash=sha256_hex(interp.conclusion),
        methods=["independent_parse", "examples", "anti_examples",
                 "paraphrase", "local_mutation"],
        reviewer_ids=["semantic-reviewer"],
        reviewer_independence_and_conflicts=[{
            "reviewer_id": "semantic-reviewer",
            "independent_from": ["governor", "intake_retrieval"],
            "conflicts": [],
        }],
        verdict=Verdict.APPROVED,
    ))


# ---------------------------------------------------------------------------
# Lean repair: prompt + capability detection


def test_repair_prompt_carries_diagnostics_and_rejected_source():
    prompt = build_formalization_prompt(
        declaration_name="erdos_x", expected_type="True",
        informal_statement="s", previous_source="theorem bad : True := rfl",
        kernel_feedback="unknown identifier 'foo'")
    assert "REPAIR ROUND" in prompt
    assert "unknown identifier 'foo'" in prompt
    assert "theorem bad : True := rfl" in prompt
    # The pinned obligation is stated identically in both prompt forms.
    plain = build_formalization_prompt(
        declaration_name="erdos_x", expected_type="True", informal_statement="s")
    assert "REPAIR ROUND" not in plain
    assert plain in prompt or prompt.startswith(plain[:200])


def test_supports_repair_detection():
    class Modern:
        def formalize(self, *, declaration_name, expected_type,
                      informal_statement, previous_source="", kernel_feedback=""):
            return None

    class Legacy:
        def formalize(self, *, declaration_name, expected_type,
                      informal_statement):
            return None

    assert _supports_repair(Modern())
    assert not _supports_repair(Legacy())
    assert not _supports_repair(SimpleNamespace(formalize=None))


# ---------------------------------------------------------------------------
# Lean repair: loop integration


class _FakeCert:
    def __init__(self, passed, findings=()):
        self.passed = passed
        self.placeholder_findings = ()
        self.unsafe_findings = tuple(findings)

    def to_dict(self):
        return {"passed": self.passed,
                "unsafe_findings": list(self.unsafe_findings)}


class _FakeLeanService:
    """Rejects the first N sources, then passes."""

    def __init__(self, fail_first=1):
        self.fail_first = fail_first
        self.verify_calls: list[str] = []

    def create_environment(self, **kwargs):
        return SimpleNamespace(environment_id="env-1")

    def verify_declaration(self, *, source, **kwargs):
        self.verify_calls.append(source)
        if len(self.verify_calls) <= self.fail_first:
            return _FakeCert(False, findings=(
                "lean kernel rejected the candidate (exit 1): "
                "unknown identifier 'foo'",))
        return _FakeCert(True)


class _FakeFormalizer:
    formalizer_id = "fake-repair"

    def __init__(self, sources=("theorem repaired : True := trivial",)):
        self.sources = list(sources)
        self.calls: list[dict] = []

    def formalize(self, *, declaration_name, expected_type, informal_statement,
                  previous_source="", kernel_feedback=""):
        self.calls.append({
            "declaration_name": declaration_name,
            "previous_source": previous_source,
            "kernel_feedback": kernel_feedback,
        })
        index = min(len(self.calls) - 1, len(self.sources) - 1)
        return self.sources[index]


class _FormalCandidateWorker:
    """Stub worker: proposes the goal plus one Lean candidate, nothing else."""

    def __init__(self, formalizer):
        self.formalizer = formalizer

    def cold_pass(self, contract, *, budget):
        return WorkerOutput(falsifiers=["check small n"],
                            search_queries=["squares nonnegative"])

    def work_branch(self, contract, packet, *, branch_id, budget,
                    fencing_token, branch_slice=None):
        return WorkerOutput(
            claim_proposals=[{
                "claim_id": "goal",
                "canonical_formula": "for all n, n*n >= 0",
                "informal_text": "",
                "scope": "general",
                "dependencies": [],
            }],
            formal_candidates=[{
                "claim_id": "goal",
                "source": "theorem broken : True := foo",
                "declaration_name": "erdos_test",
                "expected_type_source": "True",
                "lean_version": "4.28.0",
                "mathlib_commit": "v4.28.0",
                "project_hash": sha256_hex("project"),
                "expected_type_hash": sha256_hex("True"),
                "immutable_target_module_hash": sha256_hex("module"),
                "trust_policy": "classical-whitelist",
            }],
        )


def _repair_research(tmp_path, *, service, formalizer, repair_rounds,
                     problem_id):
    return research(
        problem_id=problem_id, source_bytes=TRUE_STATEMENT,
        source_id=problem_id, budget=100.0, enforcer=_enforcer(),
        worker=_FormalCandidateWorker(formalizer), goal_claim_id="goal",
        events_path=tmp_path / f"{problem_id}.jsonl",
        retrieval_corpus=_corpus(), status_claims=_status(problem_id),
        lean_service=service, informal_only=False,
        lean_repair_rounds=repair_rounds, max_iterations=1,
    )


def test_rejected_candidate_is_repaired_and_rechecked(tmp_path):
    service = _FakeLeanService(fail_first=1)
    formalizer = _FakeFormalizer()
    result = _repair_research(tmp_path, service=service, formalizer=formalizer,
                              repair_rounds=2, problem_id="repair-ok")
    # kernel saw the broken source then the repaired one
    assert len(service.verify_calls) == 2
    assert service.verify_calls[1] == "theorem repaired : True := trivial"
    # the formalizer received the kernel diagnostics and the rejected source
    assert len(formalizer.calls) == 1
    assert "unknown identifier 'foo'" in formalizer.calls[0]["kernel_feedback"]
    assert formalizer.calls[0]["previous_source"] == "theorem broken : True := foo"
    # audit trail: the repaired attempt is a separate report marked as a repair
    repair_reports = [r for r in result.formal_reports if r.get("repair_round")]
    assert len(repair_reports) == 1 and repair_reports[0]["passed"]
    # the repaired pass still cannot promote without a correspondence review
    assert any(f.startswith("formal_correspondence_required")
               for f in result.failures)


def test_exhausted_repairs_leave_candidate_rejected(tmp_path):
    service = _FakeLeanService(fail_first=99)     # never passes
    formalizer = _FakeFormalizer(sources=(
        "theorem attempt1 : True := bar", "theorem attempt2 : True := baz"))
    result = _repair_research(tmp_path, service=service, formalizer=formalizer,
                              repair_rounds=2, problem_id="repair-exhausted")
    assert len(service.verify_calls) == 3         # original + 2 repairs
    assert len(formalizer.calls) == 2
    assert all(not r["passed"] for r in result.formal_reports)
    assert result.certificate is None


def test_zero_repair_rounds_never_invokes_the_formalizer(tmp_path):
    service = _FakeLeanService(fail_first=99)
    formalizer = _FakeFormalizer()
    _repair_research(tmp_path, service=service, formalizer=formalizer,
                     repair_rounds=0, problem_id="repair-off")
    assert len(service.verify_calls) == 1
    assert formalizer.calls == []


def test_legacy_formalizer_without_feedback_kwarg_never_repairs(tmp_path):
    class LegacyFormalizer:
        formalizer_id = "legacy"
        calls = 0

        def formalize(self, *, declaration_name, expected_type,
                      informal_statement):
            LegacyFormalizer.calls += 1
            return "theorem x : True := trivial"

    service = _FakeLeanService(fail_first=99)
    _repair_research(tmp_path, service=service, formalizer=LegacyFormalizer(),
                     repair_rounds=2, problem_id="repair-legacy")
    assert len(service.verify_calls) == 1
    assert LegacyFormalizer.calls == 0


# ---------------------------------------------------------------------------
# literature imports: worker parsing


def _worker_json(**overrides):
    document = {
        "goal_restatement": "g", "claims": [], "proof_steps": [],
        "assumptions": [], "falsifiers": [], "search_queries": [],
        "candidate_sequences": [], "experiments": [],
        "formalization_requests": [], "lean_declaration_candidates": [],
        "open_subgoals": [], "bottleneck": "", "confidence": 0.5,
    }
    document.update(overrides)
    return "```json\n" + json.dumps(document) + "\n```"


def test_parse_worker_response_accepts_literature_imports():
    parsed = parse_worker_response(_worker_json(literature_imports=[
        {"claim_id": "lem1", "theorem_id": "thm-sq"},
        {"claim_id": "", "theorem_id": "dropped"},      # skipped, not fatal
    ]))
    assert parsed["literature_imports"] == [
        {"claim_id": "lem1", "theorem_id": "thm-sq"}]


def test_parse_worker_response_rejects_non_object_import():
    with pytest.raises(WorkerResponseSchemaError):
        parse_worker_response(_worker_json(literature_imports=["thm-sq"]))


# ---------------------------------------------------------------------------
# literature imports: admission semantics


def _import_graph(tmp_path, formula):
    graph = EpistemicGraph(EventLog(tmp_path / "events.jsonl", run_id="imports"))
    graph.add_problem(Problem(problem_id="p"), actor=ACTOR)
    graph.add_interpretation(Interpretation("int", "p", "S"), actor=ACTOR)
    graph.propose_claim(claim_id="lem", interpretation_id="int",
                        canonical_formula=formula, actor=ACTOR)
    return graph, EvidenceRouter(graph)


def _record(theorem_id, uri, text):
    return TheoremRecord(
        theorem_id=theorem_id, canonical_statement=text, conclusion=text,
        source_uri=uri, source_version="v1", source_content_hash=sha256_hex(text),
        verbatim_theorem_and_hypothesis_extract=text)


FORMULA = "every squarefree integer is a product of distinct primes"


def test_unknown_record_claim_and_non_sequitur_are_rejected(tmp_path):
    graph, router = _import_graph(tmp_path, FORMULA)
    packet = SimpleNamespace(theorem_records=[
        _record("thm-1", "https://a.example/1", "totally unrelated statement")])
    failures: list[str] = []
    admitted = _admit_literature_imports(
        [{"claim_id": "lem", "theorem_id": "ghost"},
         {"claim_id": "ghost", "theorem_id": "thm-1"},
         {"claim_id": "lem", "theorem_id": "thm-1"}],
        packet=packet, graph=graph, router=router, branch_id="b",
        failures=failures)
    assert admitted == 0
    assert any(f.startswith("literature_import_unknown_record") for f in failures)
    assert any(f.startswith("literature_import_unknown_claim") for f in failures)
    assert any(f.startswith("literature_import_inapplicable") for f in failures)
    assert graph.claims["lem"].truth_status.value == "UNKNOWN"


def test_single_audited_import_records_provenance_but_never_supports(tmp_path):
    graph, router = _import_graph(tmp_path, FORMULA)
    packet = SimpleNamespace(theorem_records=[
        _record("thm-1", "https://a.example/1",
                f"Theorem: {FORMULA}. Standard fact.")])
    failures: list[str] = []
    admitted = _admit_literature_imports(
        [{"claim_id": "lem", "theorem_id": "thm-1"}],
        packet=packet, graph=graph, router=router, branch_id="b",
        failures=failures)
    assert admitted == 1 and failures == []
    claim = graph.claims["lem"]
    assert claim.truth_status.value == "UNKNOWN"        # provenance, not support
    assert claim.evidence_profile.external_import.name == "AUDITED_SOURCE"


def test_two_distinct_hosts_corroborate_and_support(tmp_path):
    graph, router = _import_graph(tmp_path, FORMULA)
    packet = SimpleNamespace(theorem_records=[
        _record("thm-1", "https://a.example/1", f"Theorem: {FORMULA}."),
        _record("thm-2", "https://b.example/2", f"Known result: {FORMULA}."),
    ])
    failures: list[str] = []
    admitted = _admit_literature_imports(
        [{"claim_id": "lem", "theorem_id": "thm-1"},
         {"claim_id": "lem", "theorem_id": "thm-2"}],
        packet=packet, graph=graph, router=router, branch_id="b",
        failures=failures)
    assert admitted == 2
    claim = graph.claims["lem"]
    assert claim.evidence_profile.external_import.name == "INDEPENDENTLY_CORROBORATED"
    assert claim.truth_status.value == "SUPPORTED"


def test_two_records_from_the_same_host_never_corroborate(tmp_path):
    graph, router = _import_graph(tmp_path, FORMULA)
    packet = SimpleNamespace(theorem_records=[
        _record("thm-1", "https://a.example/1", f"Theorem: {FORMULA}."),
        _record("thm-2", "https://a.example/2", f"Also: {FORMULA}."),
    ])
    failures: list[str] = []
    _admit_literature_imports(
        [{"claim_id": "lem", "theorem_id": "thm-1"},
         {"claim_id": "lem", "theorem_id": "thm-2"}],
        packet=packet, graph=graph, router=router, branch_id="b",
        failures=failures)
    claim = graph.claims["lem"]
    assert claim.evidence_profile.external_import.name == "AUDITED_SOURCE"
    assert claim.truth_status.value == "UNKNOWN"


def test_import_applicability_gate():
    good = _record("t", "https://a.example/1", f"We recall that {FORMULA} holds.")
    assert _import_applicable(FORMULA, good)
    assert not _import_applicable(FORMULA, _record(
        "t", "https://a.example/1", "the Riemann zeta function has a pole at 1"))
    assert not _import_applicable("", good)


# ---------------------------------------------------------------------------
# durable within-problem checkpoints


def _fixture_worker():
    spec = ExperimentSpec(
        purpose="finite nonneg", inputs={"n": 50}, arithmetic_mode="exact",
        coverage="k in 0..n", claim_ids=("goal",),
    )
    return DeterministicWorker(
        goal_claim_id="goal", goal_formula="for all n, n*n >= 0",
        goal_scope="finite_domain", experiment_code=FINITE_CODE,
        experiment_spec=spec)


def test_checkpoints_are_written_signed_and_resumable(tmp_path):
    ckpt_dir = tmp_path / "ckpts"
    result = research(
        problem_id="ckpt-run", source_bytes=TRUE_STATEMENT, source_id="ckpt",
        budget=100.0, enforcer=_enforcer(), worker=_fixture_worker(),
        goal_claim_id="goal", events_path=tmp_path / "events.jsonl",
        retrieval_corpus=_corpus(), probe_predicate=lambda n: n * n >= 0,
        informal_only=True, status_claims=_status("ckpt-run"),
        checkpoint_dir=ckpt_dir,
    )
    assert "checkpoint" in result.phases
    files = sorted((ckpt_dir / "ckpt-run").glob("checkpoint_*.json"))
    assert files
    record = json.loads(files[-1].read_text())
    # Reconstitute and verify: the signed checkpoint must authenticate AND
    # commit to an exact prefix of the run's real event log.
    checkpoint = Checkpoint(
        run_id=record["run_id"], last_sequence=record["last_sequence"],
        last_event_id=record["last_event_id"], merkle_root=record["merkle_root"],
        problem_contract_hash=record["problem_contract_hash"],
        interpretation_hashes=tuple(record["interpretation_hashes"]),
        graph_view_hash=record["graph_view_hash"],
        controller_posteriors=record["controller_posteriors"],
        budgets=record["budgets"], seeds=record["seeds"],
        active_leases=tuple(record["active_leases"]),
        behavior_closure_fingerprint=record["behavior_closure_fingerprint"],
        stage_caches=record["stage_caches"],
        rate_limit_state=record["rate_limit_state"],
        in_flight_calls=tuple(record["in_flight_calls"]),
        _sealed_hash=record["sealed_hash"], _signature=record["signature"],
    )
    assert checkpoint.verify_checkpoint_hash()
    report = resume(
        checkpoint, log=result.graph.log,
        current_closure_fingerprint=record["behavior_closure_fingerprint"],
    )
    assert report.ok and report.chain_verified
    assert record["budgets"]["remaining"] <= record["budgets"]["total"]


def test_checkpoint_write_failure_is_operational_not_mathematical(tmp_path):
    blocker = tmp_path / "not-a-dir"
    blocker.write_text("occupied")
    result = research(
        problem_id="ckpt-fail", source_bytes=TRUE_STATEMENT, source_id="ckptf",
        budget=100.0, enforcer=_enforcer(), worker=_fixture_worker(),
        goal_claim_id="goal", events_path=tmp_path / "events2.jsonl",
        retrieval_corpus=_corpus(), probe_predicate=lambda n: n * n >= 0,
        informal_only=True, status_claims=_status("ckpt-fail"),
        intent_review=_intent("ckpt-fail", source_id="ckptf"),
        checkpoint_dir=blocker,
    )
    assert any(f.startswith("checkpoint_write_failed") for f in result.failures)
    # the mathematical outcome is untouched by the ops failure
    assert result.graph.claims["goal"].truth_status.value == "SUPPORTED"


def test_no_checkpoint_dir_means_no_checkpoint_phase(tmp_path):
    result = research(
        problem_id="ckpt-off", source_bytes=TRUE_STATEMENT, source_id="ckpto",
        budget=100.0, enforcer=_enforcer(), worker=_fixture_worker(),
        goal_claim_id="goal", events_path=tmp_path / "events3.jsonl",
        retrieval_corpus=_corpus(), probe_predicate=lambda n: n * n >= 0,
        informal_only=True, status_claims=_status("ckpt-off"),
    )
    assert "checkpoint" not in result.phases
