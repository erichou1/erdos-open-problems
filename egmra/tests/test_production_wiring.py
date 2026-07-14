"""Production-wiring tests: distinct branch roles (4.11), durable model-exchange
artifacts + signed events (4.10), and model-proposed finite experiments executed
in the trusted sandbox (4.5).
"""

from __future__ import annotations

import json

from egmra.compute.service import ComputeService
from egmra.intake import build_problem_contract
from egmra.intake.review import interpretation_review_hash, sign_intent_certificate
from egmra.agents.runner import DeterministicRunner, RunnerResponse
from egmra.agents.browser_runner import BrowserTranscript
from egmra.corpus.status import StatusClaim
from egmra.m2 import ContentAddressedObjectStore
from egmra.orchestrator import DeterministicWorker, RunnerWorker, research
from egmra.orchestrator.loop import (
    WORKER_ROLE_BY_FAMILY,
    _branch_role,
    _default_independent_replay_executor,
    _execute_finite_experiment,
    _record_model_exchanges,
)
from egmra.compute.spec import ExperimentSpec
from egmra.policy import PolicyEnforcer, sign_policy
from egmra.provenance.hashing import sha256_hex
from egmra.retrieval.records import TheoremRecord
from egmra.truth.events import EventLog
from egmra.truth.entities import IntentCertificate, Verdict

_POLICY_ENV = {"EGMRA_POLICY_KEY": "production-wiring-test-policy-key-32b"}
_TRUE = b"Prove that for all natural numbers n, n squared is at least 0."
_FINITE_TRUE = (
    "def experiment(inputs):\n"
    "    return {'result': all((k * k) >= 0 for k in range(inputs['n'] + 1)),"
    " 'coverage': 'k in 0..n exhaustive'}\n"
)
_FINITE_FALSE = (
    "def experiment(inputs):\n"
    "    return {'result': all(k >= 1 for k in range(inputs['n'] + 1)),"
    " 'coverage': 'k in 0..n exhaustive'}\n"
)


def _enforcer():
    policy = sign_policy({
        "claim_graph": True, "literature_retrieval": True, "computation_service": True,
        "promotion": False, "formal_promotion": False,
    }, env=_POLICY_ENV)
    return PolicyEnforcer(policy, verification_env=_POLICY_ENV)


def _corpus():
    return [TheoremRecord(theorem_id="thm-sq", canonical_statement="squares are nonnegative",
                          conclusion="n squared is nonnegative", source_uri="u", source_version="v1",
                          source_content_hash="h", verbatim_theorem_and_hypothesis_extract="x")]


def _intent_review(problem_id: str, source_id: str) -> IntentCertificate:
    contract = build_problem_contract(problem_id=problem_id, source_bytes=_TRUE,
                                      source_id=source_id, predicate=lambda n: n * n >= 0)
    interp = contract.lattice.nodes[0]
    return sign_intent_certificate(IntentCertificate(
        certificate_id=f"intent-{problem_id}",
        source_bytes_hash=contract.source_bytes_hash,
        interpretation_hash=interpretation_review_hash(interp),
        informal_claim_hash=sha256_hex(interp.conclusion),
        methods=["independent_parse", "examples", "anti_examples", "paraphrase", "local_mutation"],
        reviewer_ids=["semantic-reviewer"],
        reviewer_independence_and_conflicts=[{
            "reviewer_id": "semantic-reviewer",
            "independent_from": ["governor", "intake_retrieval"], "conflicts": [],
        }],
        verdict=Verdict.APPROVED,
    ))


def _status(problem_id: str):
    return [StatusClaim(problem_id=problem_id, status="open", source="local://test",
                        review_date="2026-07-13", source_independence="test-fixture")]


class _ModelRunner:
    """A credential-free runner that emits schema-valid branch JSON and records
    a browser-style transcript per exchange (drives 4.5 + 4.10 hermetically)."""

    runner_id = "model-wiring-test"

    def __init__(self, *, experiment_code: str | None = None, claim_id: str = "goal"):
        self._delegate = DeterministicRunner()
        self._code = experiment_code
        self._claim = claim_id
        self.records: list[BrowserTranscript] = []

    def run(self, prompt: str, *, stage: str) -> RunnerResponse:
        base = self._delegate.run(prompt, stage=stage)
        if stage.startswith("branch:"):
            experiments = []
            if self._code is not None:
                experiments = [{"description": "finite exhaustive check", "kind": "finite_domain",
                                "code": self._code, "inputs": {"n": 30},
                                "claim_id": self._claim, "coverage": "0..n exhaustive"}]
            payload = {"goal_restatement": "", "claims": [], "falsifiers": ["check small cases"],
                       "search_queries": [], "candidate_sequences": [], "experiments": experiments,
                       "open_subgoals": [], "bottleneck": "finite check", "confidence": 0.3}
        elif stage == "cold_pass":
            payload = {"falsifiers": ["smallest cases"], "search_queries": ["q"],
                       "bottleneck": "blind", "confidence": 0.1}
        else:
            payload = {"falsifiers": [], "search_queries": [], "bottleneck": "", "confidence": 0.1}
        text = json.dumps(payload)
        self.records.append(BrowserTranscript(
            stage=stage, model_label="test-ui", account_class="test",
            conversation_url=f"https://example/c/{base.prompt_hash[:8]}",
            prompt_hash=base.prompt_hash, response_hash=sha256_hex(text),
            runner_version="test", attested=False, rate_limit_pauses=0,
            response_retries=0, created_at="2026-07-13T00:00:00Z"))
        return RunnerResponse(text=text, model=base.model, context_id=base.context_id,
                              prompt_hash=base.prompt_hash)


# ── 4.11: distinct worker roles per mechanism branch ────────────────────────────

def test_for_role_specializes_and_shares_runner():
    worker = RunnerWorker(runner=DeterministicRunner(), role="prover")
    skeptic = worker.for_role("skeptic")
    assert skeptic.role == "skeptic" and skeptic.runner is worker.runner
    assert worker.for_role("prover") is worker  # same role -> no copy


def test_branch_role_mapping_is_distinct():
    worker = RunnerWorker(runner=DeterministicRunner(), role="prover")
    assert _branch_role("direct_structural", worker) == "prover"
    assert _branch_role("computational_finite_reduction", worker) == "experimentalist"
    assert _branch_role("formal_library_first", worker) == "formalizer"
    assert len(set(WORKER_ROLE_BY_FAMILY.values())) == len(WORKER_ROLE_BY_FAMILY)


def test_research_records_distinct_branch_roles(tmp_path):
    runner = _ModelRunner()
    worker = RunnerWorker(runner=runner, goal_claim_id="goal",
                          goal_formula="for all n, n*n >= 0", role="prover")
    result = research(
        problem_id="erdos-roles-1", source_bytes=_TRUE, source_id="fx-roles",
        budget=100.0, enforcer=_enforcer(), worker=worker, goal_claim_id="goal",
        events_path=tmp_path / "e.jsonl", retrieval_corpus=_corpus(), runner=runner,
        probe_predicate=lambda n: n * n >= 0, status_claims=_status("erdos-roles-1"),
        intent_review=_intent_review("erdos-roles-1", "fx-roles"))
    branches = result.graph.branches
    assert branches, "expected mechanism branches"
    for branch in branches.values():
        role = branch.mechanism_fingerprint.get("worker_role")
        assert role == WORKER_ROLE_BY_FAMILY.get(branch.branch_id, "prover")


# ── 4.10: durable content-addressed transcripts + signed exchange events ────────

def test_record_model_exchanges_persists_and_signs(tmp_path):
    runner = _ModelRunner()
    for stage in ("cold_pass", "branch:direct_structural"):
        runner.run("prompt", stage=stage)
    store = ContentAddressedObjectStore(root=tmp_path / "artifacts")
    log = EventLog(tmp_path / "e.jsonl", run_id="prob")
    # The same runner passed twice in one call is de-duplicated (recorded once).
    count = _record_model_exchanges(log, store, "prob", runners=(runner, runner))
    assert count == 2
    exchange_events = [e for e in log.events if e.action == "MODEL_EXCHANGE_RECORDED"]
    assert len(exchange_events) == 2
    for event in exchange_events:
        assert event.output_hashes and store.get(event.output_hashes[0])  # durable artifact
        assert event.payload["prompt_hash"] and "conversation_url" in event.payload


def test_research_records_model_exchanges(tmp_path):
    runner = _ModelRunner()
    store = ContentAddressedObjectStore(root=tmp_path / "artifacts")
    result = research(
        problem_id="erdos-tx-1", source_bytes=_TRUE, source_id="fx-tx",
        budget=100.0, enforcer=_enforcer(), worker=DeterministicWorker(
            goal_claim_id="goal", goal_formula="for all n, n*n >= 0"),
        goal_claim_id="goal", events_path=tmp_path / "e.jsonl", retrieval_corpus=_corpus(),
        runner=runner, artifact_store=store, status_claims=_status("erdos-tx-1"),
        intent_review=_intent_review("erdos-tx-1", "fx-tx"))
    assert "record_exchanges" in result.phases
    exchange_events = [e for e in result.graph.log.events if e.action == "MODEL_EXCHANGE_RECORDED"]
    assert exchange_events, "expected durable signed model-exchange events"
    assert result.graph.log.verify_integrity() is True


# ── 4.5: model-proposed finite experiments executed in the trusted sandbox ──────

def test_execute_finite_experiment_true_yields_evidence():
    spec = ExperimentSpec(purpose="p", claim_ids=("goal",), inputs={"n": 20},
                          coverage="0..n", arithmetic_mode="exact")
    evidence, replays, failures = _execute_finite_experiment(
        ComputeService(), _default_independent_replay_executor(), spec, _FINITE_TRUE, "goal")
    assert evidence and evidence[0]["kind"] == "exact_computation"
    assert evidence[0]["claim_ids"] == ["goal"] and replays


def test_execute_finite_experiment_false_yields_no_evidence():
    spec = ExperimentSpec(purpose="p", claim_ids=("goal",), inputs={"n": 20},
                          coverage="0..n", arithmetic_mode="exact")
    evidence, _replays, failures = _execute_finite_experiment(
        ComputeService(), None, spec, _FINITE_FALSE, "goal")
    assert not evidence
    assert any("returned false" in f for f in failures)


def test_runner_worker_executes_model_experiment_as_computational_evidence(tmp_path):
    # A model that proposes a true finite check gets it EXECUTED in the trusted
    # sandbox and admitted as authenticated exact_computation evidence (task 4.5)
    # — but a finite check never proves a *general* claim, so the goal is not
    # over-promoted. This is the sound computational-evidence boundary.
    runner = _ModelRunner(experiment_code=_FINITE_TRUE, claim_id="goal")
    worker = RunnerWorker(runner=runner, goal_claim_id="goal",
                          goal_formula="for all n, n*n >= 0", compute_service=ComputeService())
    result = research(
        problem_id="erdos-compute-1", source_bytes=_TRUE, source_id="fx-compute",
        budget=100.0, enforcer=_enforcer(), worker=worker, goal_claim_id="goal",
        events_path=tmp_path / "e.jsonl", retrieval_corpus=_corpus(), runner=runner,
        probe_predicate=lambda n: n * n >= 0, informal_only=True,
        status_claims=_status("erdos-compute-1"),
        intent_review=_intent_review("erdos-compute-1", "fx-compute"))
    # The model's finite experiment was executed and its evidence authenticated.
    assert "ev_goal" in result.graph.evidence
    # Finite computation over a bounded range never proves a general statement.
    assert result.graph.claims["goal"].truth_status.value != "SUPPORTED"


def test_runner_worker_without_compute_service_does_not_execute():
    runner = _ModelRunner(experiment_code=_FINITE_TRUE, claim_id="goal")
    worker = RunnerWorker(runner=runner, goal_claim_id="goal", goal_formula="P")
    from types import SimpleNamespace

    output = worker.work_branch(SimpleNamespace(), SimpleNamespace(),
                                branch_id="computational_finite_reduction", budget=10.0,
                                fencing_token=1)
    assert output.evidence == []  # no compute service configured -> nothing executed


# ── 4.1: full typed worker-output schema ────────────────────────────────────────

def test_parse_worker_response_captures_full_typed_schema():
    from egmra.orchestrator.runner_worker import parse_worker_response

    doc = {
        "claims": [], "proof_steps": ["reduce to finite check", "apply lemma A"],
        "assumptions": ["n is a natural number"],
        "formalization_requests": ["formalize the reduction to Lean"],
        "lean_declaration_candidates": [
            {"claim_id": "goal", "declaration_name": "egmra_demo",
             "source": "import Mathlib\ntheorem egmra_demo : 2 + 2 = 4 := rfl",
             "expected_type": "2 + 2 = 4"},
            {"declaration_name": "", "source": "x", "expected_type": "y"},  # incomplete -> dropped
        ],
        "falsifiers": [], "search_queries": [], "candidate_sequences": [], "experiments": [],
        "open_subgoals": [], "bottleneck": "", "confidence": 0.5,
    }
    parsed = parse_worker_response(json.dumps(doc))
    assert parsed["proof_steps"] == ["reduce to finite check", "apply lemma A"]
    assert parsed["assumptions"] == ["n is a natural number"]
    assert parsed["formalization_requests"] == ["formalize the reduction to Lean"]
    assert len(parsed["lean_declaration_candidates"]) == 1  # incomplete candidate dropped
    assert parsed["lean_declaration_candidates"][0]["declaration_name"] == "egmra_demo"


# ── 4.6: formal candidates emitted + verified via a real LeanService ────────────

from egmra.orchestrator.runner_worker import parse_worker_response  # noqa: E402
from egmra.lean.kernel_checker import expected_type_hash as _canon_type_hash  # noqa: E402
from egmra.lean.kernel_checker import make_attested_kernel_runner  # noqa: E402
from egmra.lean.service import LeanService  # noqa: E402
from egmra.provenance.hashing import is_sha256  # noqa: E402

_LEAN_SRC = "import Mathlib\n\ntheorem egmra_demo : 2 + 2 = 4 := rfl\n"


class _FormalRunner:
    """Emits a branch response proposing a Lean declaration candidate."""

    runner_id = "formal-wiring-test"

    def __init__(self):
        self._delegate = DeterministicRunner()

    def run(self, prompt: str, *, stage: str) -> RunnerResponse:
        base = self._delegate.run(prompt, stage=stage)
        if stage.startswith("branch:"):
            payload = {"goal_restatement": "", "claims": [], "proof_steps": ["p"],
                       "assumptions": [], "falsifiers": [], "search_queries": [],
                       "candidate_sequences": [], "experiments": [],
                       "formalization_requests": ["formalize"],
                       "lean_declaration_candidates": [{
                           "claim_id": "goal", "declaration_name": "egmra_demo",
                           "source": _LEAN_SRC, "expected_type": "2 + 2 = 4"}],
                       "open_subgoals": [], "bottleneck": "formalize", "confidence": 0.4}
        else:
            payload = {"falsifiers": [], "search_queries": [], "bottleneck": "", "confidence": 0.1}
        return RunnerResponse(text=json.dumps(payload), model=base.model,
                              context_id=base.context_id, prompt_hash=base.prompt_hash)


def _fake_attested_checker(tmp_path):
    """A pinned checker script that echoes a verdict verify_for accepts."""
    script = tmp_path / "fake_lean_checker.py"
    script.write_text(
        "#!/usr/bin/env python3\n"
        "import sys, json, hashlib\n"
        "req = json.load(sys.stdin)\n"
        "def h(s): return hashlib.sha256(s.encode()).hexdigest()\n"
        "sys.stdout.write(json.dumps({\n"
        "  'kernel_verified': True, 'candidate_type_hash': req['expected_type_hash'],\n"
        "  'source_tree_hash': h('st'), 'imports_hash': h('im'),\n"
        "  'candidate_declaration_hash': h('cd'), 'proof_term_hash': h('pt'),\n"
        "  'transitive_axioms': ['propext'], 'placeholder_findings': [],\n"
        "  'unsafe_findings': [], 'imports_audited': True, 'axiom_closure_verified': True,\n"
        "  'immutable_target_isolated': True, 'clean_replay': True, 'network_disabled': True}))\n",
        encoding="utf-8")
    script.chmod(0o755)
    return script


def test_runner_worker_emits_formal_candidates():
    from types import SimpleNamespace

    worker = RunnerWorker(runner=_FormalRunner(), goal_claim_id="goal",
                          goal_formula="2 + 2 = 4", lean_version="4.28.0",
                          mathlib_commit="v4.28.0")
    output = worker.work_branch(SimpleNamespace(), SimpleNamespace(),
                                branch_id="formal_library_first", budget=10.0, fencing_token=1)
    assert output.formal_candidates
    fc = output.formal_candidates[0]
    assert fc["declaration_name"] == "egmra_demo" and fc["claim_id"] == "goal"
    assert fc["expected_type_hash"] == _canon_type_hash("2 + 2 = 4")  # deterministic, not model-trusted
    assert is_sha256(fc["project_hash"]) and is_sha256(fc["immutable_target_module_hash"])
    assert fc["expected_type_source"] == "2 + 2 = 4"


def test_runner_worker_no_formal_candidates_without_lean_env():
    from types import SimpleNamespace

    worker = RunnerWorker(runner=_FormalRunner(), goal_claim_id="goal", goal_formula="P")
    output = worker.work_branch(SimpleNamespace(), SimpleNamespace(),
                                branch_id="formal_library_first", budget=10.0, fencing_token=1)
    assert output.formal_candidates == []


def test_research_formal_candidate_verified_by_lean_service(tmp_path):
    lean_service = LeanService(kernel_runner=_fake_attested_checker_runner(tmp_path))
    worker = RunnerWorker(runner=_FormalRunner(), goal_claim_id="goal",
                          goal_formula="for all n, n*n >= 0", lean_version="4.28.0",
                          mathlib_commit="v4.28.0")
    result = research(
        problem_id="erdos-formal-1", source_bytes=_TRUE, source_id="fx-formal",
        budget=100.0, enforcer=_enforcer(), worker=worker, goal_claim_id="goal",
        events_path=tmp_path / "e.jsonl", retrieval_corpus=_corpus(),
        runner=_FormalRunner(), lean_service=lean_service,
        probe_predicate=lambda n: n * n >= 0, status_claims=_status("erdos-formal-1"),
        intent_review=_intent_review("erdos-formal-1", "fx-formal"))
    # The formal-candidate path fired: the LeanService verified the declaration.
    assert result.formal_reports, "expected a formal verification report"
    report = result.formal_reports[0]
    assert report["declaration_name"] == "egmra_demo"
    assert report["kernel_verified"] is True and report["target_type_matches"] is True
    # No signed formal-correspondence review was provided, so a verified
    # declaration is NOT admitted as a formal proof of the informal claim.
    assert any("formal_correspondence_required" in f for f in result.failures)


def _fake_attested_checker_runner(tmp_path):
    return make_attested_kernel_runner(_fake_attested_checker(tmp_path))

