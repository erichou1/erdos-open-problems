"""Provider-agnostic, persisted multi-context proof pipeline."""

import json
import hashlib
from datetime import datetime, timezone
import uuid
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Protocol

from solver_prompts import (
    ADJUDICATOR_PROMPT_TEMPLATE,
    CANDIDATE_PROMPT_TEMPLATE,
    CONSTRUCTION_PROMPT_TEMPLATE,
    OFFLINE_POLICY,
    OUTPUT_CONTRACT,
    REGULATOR_PROMPT_TEMPLATE,
    REVISION_PROMPT_TEMPLATE,
    SCOUT_PROMPT_TEMPLATE,
    SEARCH_POLICY,
    SYNTHESIS_PROMPT_TEMPLATE,
    VERIFIER_PROMPT_TEMPLATE,
)
from verification import (
    GateDecision,
    Review,
    candidate_contract,
    candidate_status,
    evaluate_gate,
    VerificationEvidence,
)
from research_state import (
    ResearchState,
    graph_as_dict,
    make_statement_lock,
    parse_subgoal_graph,
    statement_lock_text,
)


class IsolatedRunner(Protocol):
    def run(self, prompt: str, *, stage: str, isolated: bool) -> str: ...
    def context_id(self, stage: str) -> str: ...


@dataclass(frozen=True)
class PipelineResult:
    problem_number: int
    candidate_outcome: str
    gate: GateDecision
    artifact_dir: Path


SCOUT_ROLES = (
    "direct, constructive, and structural",
    "contradiction, extremal, and minimal-counterexample",
    "counterexample search and finite falsification",
    "invariant invention, transforms, and cross-domain reformulation",
)
REVIEW_MANDATES = {
    "statement_integrity": "Compare the candidate to the immutable statement word by word; reject changed quantifiers, domains, assumptions, conclusions, or omitted tasks.",
    "structural_dependency": "Validate the subgoal DAG, proof coverage, claim dependencies, and that every load-bearing node is actually discharged.",
    "logic": "Check every inference locally, including reversibility, case coverage, and circularity.",
    "counterexample": "Actively falsify every major lemma and the conclusion using smallest, boundary, degenerate, and randomized examples where possible.",
    "theorem_hypotheses": "State every imported theorem exactly and verify every hypothesis; reject appeals to standard or well-known facts without enough detail.",
    "mechanical_evidence": "Identify claims suitable for exact computation, CAS, SAT/SMT, or formal checking; verify available evidence and reject unsupported computational claims.",
    "global_synthesis": "Ignore persuasive local detail and independently check that the verified pieces jointly imply the exact final theorem.",
}


def _json_object(text: str) -> dict:
    """Parse a JSON response, tolerating a surrounding markdown fence."""
    stripped = text.strip()
    if stripped.startswith("```"):
        first_newline = stripped.find("\n")
        stripped = stripped[first_newline + 1:]
        if stripped.endswith("```"):
            stripped = stripped[:-3]
    start, end = stripped.find("{"), stripped.rfind("}")
    if start < 0 or end < start:
        raise ValueError("review response did not contain a JSON object")
    # strict=False allows raw control characters (e.g. unescaped newlines) that
    # ChatGPT often emits inside JSON string values, which strict parsing rejects.
    return json.loads(stripped[start:end + 1], strict=False)


def _strings(value) -> tuple[str, ...]:
    if value in (None, "", "NONE", []):
        return ()
    if isinstance(value, str):
        return (value,)
    return tuple(str(item) for item in value)


def _review(
    data: dict, *, reviewer_id: str, expected_role: str, context_id: str
) -> Review:
    reported_role = str(data.get("reviewer_role", expected_role))
    if reported_role != expected_role:
        raise ValueError(f"reviewer role mismatch: expected {expected_role}, got {reported_role}")
    return Review(
        reviewer_id=reviewer_id,
        reviewer_role=expected_role,
        independent_context=bool(context_id),
        verdict=str(data.get("verdict", "fail")),
        claims_checked=int(data.get("claims_checked", 0)),
        claims_total=int(data.get("claims_total", 0)),
        checked_claim_ids=_strings(data.get("checked_claim_ids")),
        open_gaps=_strings(data.get("open_gaps")),
        unchecked_imports=_strings(data.get("unchecked_imports")),
        material_errors=_strings(data.get("material_errors")),
        statement_sha256=str(data.get("statement_sha256", "")),
        completeness_score=int(data.get("completeness_score", 0)),
        proof_confidence=int(data.get("proof_confidence", 0)),
        adversarial_survival_score=int(data.get("adversarial_survival_score", 0)),
        adjudicated_outcome=str(data.get("outcome", "")),
        context_id=context_id,
    )


def _failed_review(
    *, reviewer_id: str, expected_role: str, context_id: str, error: Exception
) -> Review:
    return Review(
        reviewer_id=reviewer_id,
        reviewer_role=expected_role,
        independent_context=bool(context_id),
        verdict="fail",
        claims_checked=0,
        claims_total=0,
        material_errors=(f"malformed reviewer output: {error}",),
        context_id=context_id,
    )


class ProofPipeline:
    def __init__(
        self,
        runner: IsolatedRunner,
        artifact_root: Path,
        *,
        max_revisions: int = 2,
        verification_evidence: tuple[VerificationEvidence, ...] = (),
    ):
        self.runner = runner
        self.artifact_root = Path(artifact_root)
        self.max_revisions = max(0, max_revisions)
        self.verification_evidence = verification_evidence
        self._stage_cache = None

    def _run(self, prompt: str, stage: str) -> str:
        """Call the isolated runner, caching each stage's raw response to disk so
        an interrupted run resumes from the last finished stage instead of
        regenerating it. Isolation is preserved: a cache hit replays the exact
        response that stage already produced in its own fresh conversation."""
        cache_file = self._stage_cache / f"{stage}.txt"
        if cache_file.exists():
            cached = cache_file.read_text(encoding="utf-8", errors="ignore")
            if cached.strip():
                print(f"{stage}: reusing cached response", flush=True)
                return cached
        response = self.runner.run(prompt, stage=stage, isolated=True)
        cache_file.write_text(response, encoding="utf-8")
        return response

    def solve(self, problem_number: int, problem: str) -> PipelineResult:
        """Run all isolated stages, persist evidence, and apply the hard gate."""
        prob_dir = self.artifact_root / f"problem_{problem_number}"
        # Resume the newest incomplete run (no manifest.json) so a stop mid-problem
        # continues from the last finished stage; otherwise start a fresh run.
        incomplete = sorted(
            (d for d in prob_dir.glob("*")
             if d.is_dir() and not (d / "manifest.json").exists()),
            key=lambda d: d.name,
        ) if prob_dir.exists() else []
        if incomplete:
            out = incomplete[-1]
        else:
            run_id = (
                datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
                + "-" + uuid.uuid4().hex[:8]
            )
            out = prob_dir / run_id
        out.mkdir(parents=True, exist_ok=True)
        self._stage_cache = out / "_stage_cache"
        self._stage_cache.mkdir(exist_ok=True)
        lock = make_statement_lock(problem)
        lock_text = statement_lock_text(lock)
        (out / "problem.txt").write_text(lock.original_statement, encoding="utf-8")
        (out / "statement_lock.json").write_text(
            json.dumps(asdict(lock), indent=2) + "\n", encoding="utf-8"
        )

        scouts = []
        for index, role in enumerate(SCOUT_ROLES, 1):
            prompt = SCOUT_PROMPT_TEMPLATE.format(
                offline=OFFLINE_POLICY, role=role, search=SEARCH_POLICY, problem=lock_text
            )
            response = self._run(prompt, f"scout_{index}")
            (out / f"scout_{index}.md").write_text(response, encoding="utf-8")
            scouts.append(response)
        scout_bundle = "\n\n".join(
            f"## Scout {i}\n{response}" for i, response in enumerate(scouts, 1)
        )

        synthesis_raw = self._run(
            SYNTHESIS_PROMPT_TEMPLATE.format(
                offline=OFFLINE_POLICY,
                statement_lock=lock_text,
                scouts=scout_bundle,
                feedback="NONE",
            ),
            "synthesis",
        )
        planner_data = _json_object(synthesis_raw)
        graph = graph_as_dict(planner_data, parse_subgoal_graph(planner_data))
        graph_text = json.dumps(graph, indent=2)
        (out / "subgoal_graph.json").write_text(graph_text + "\n", encoding="utf-8")

        state = ResearchState(statement_lock=asdict(lock), subgoal_graph=graph)
        state_file = out / "research_state.json"
        state.save(state_file)

        candidate = self._run(
            CONSTRUCTION_PROMPT_TEMPLATE.format(
                candidate_prompt=CANDIDATE_PROMPT_TEMPLATE.format(problem=problem),
                synthesis=graph_text,
                scouts=scout_bundle,
            ),
            "construction",
        )
        decision = GateDecision("candidate_rejected", ("no review completed",))
        outcome = candidate_status(candidate)
        reviews = []
        for attempt in range(1, self.max_revisions + 2):
            attempt_dir = out / f"attempt_{attempt}"
            attempt_dir.mkdir(exist_ok=True)
            (attempt_dir / "candidate.md").write_text(candidate, encoding="utf-8")
            outcome = candidate_status(candidate)
            contract = candidate_contract(candidate)
            reviews, raw_reviews = self._run_reviews(
                candidate, lock_text, graph_text, attempt, attempt_dir
            )
            decision = evaluate_gate(
                outcome,
                reviews,
                expected_statement_sha256=lock.sha256,
                candidate_contract=contract,
                verification_evidence=self.verification_evidence,
                expected_candidate_sha256=hashlib.sha256(
                    candidate.encode("utf-8")
                ).hexdigest(),
            )
            rejection_evidence = sorted({
                item
                for review in reviews
                for item in (*review.open_gaps, *review.unchecked_imports, *review.material_errors)
            })
            state.attempts.append({
                "attempt": attempt,
                "candidate_outcome": outcome,
                "candidate_sha256": hashlib.sha256(candidate.encode("utf-8")).hexdigest(),
                "gate_status": decision.status,
                "gate_reasons": list(decision.reasons),
            })
            if decision.reasons == (
                "no trusted external or mechanical verification evidence",
            ):
                decision = GateDecision(
                    "awaiting_external_evidence", decision.reasons
                )
                state.attempts[-1]["gate_status"] = "awaiting_external_evidence"
                state.save(state_file)
                break
            if decision.status.startswith("verified_"):
                state.verified_lemmas.append({
                    "id": "FINAL_THEOREM",
                    "status": decision.status,
                    "candidate_sha256": state.attempts[-1]["candidate_sha256"],
                    "verified_by": [review.reviewer_role for review in reviews],
                })
                state.save(state_file)
                break

            state.failed_approaches.append({
                "attempt": attempt,
                "candidate_sha256": state.attempts[-1]["candidate_sha256"],
                "obstructions": rejection_evidence or list(decision.reasons),
                "reusable_lesson": "Do not repeat this proof path without a new ingredient that resolves every listed obstruction.",
            })
            state.save(state_file)
            if attempt > self.max_revisions:
                break
            failure_memory = json.dumps(state.failed_approaches, indent=2)
            regulator_raw = self._run(
                REGULATOR_PROMPT_TEMPLATE.format(
                    offline=OFFLINE_POLICY,
                    statement_lock=lock_text,
                    subgoal_graph=graph_text,
                    candidate=candidate,
                    reviews="\n\n".join(raw_reviews),
                    failure_memory=failure_memory,
                ),
                f"regulator_{attempt}",
            )
            try:
                regulator = _json_object(regulator_raw)
            except (ValueError, json.JSONDecodeError) as error:
                regulator = {
                    "decision": "REVISE_PROOF",
                    "rationale": f"malformed regulator output; fail-closed fallback: {error}",
                    "broken_node_ids": [],
                    "new_constraints": ["Re-evaluate every rejected claim."],
                }
            regulation = str(regulator.get("decision", "REVISE_PROOF")).upper()
            if regulation not in {"REVISE_PROOF", "REVISE_PLAN", "REWRITE"}:
                regulation = "REVISE_PROOF"
            state.attempts[-1]["regulator"] = {
                "decision": regulation,
                "rationale": str(regulator.get("rationale", "")),
                "broken_node_ids": regulator.get("broken_node_ids", []),
                "new_constraints": regulator.get("new_constraints", []),
            }
            (attempt_dir / "regulator.json").write_text(
                json.dumps(regulator, indent=2) + "\n", encoding="utf-8"
            )
            if regulation in {"REVISE_PLAN", "REWRITE"}:
                replan_raw = self._run(
                    SYNTHESIS_PROMPT_TEMPLATE.format(
                        offline=OFFLINE_POLICY,
                        statement_lock=lock_text,
                        scouts=scout_bundle,
                        feedback=json.dumps({
                            "regulator": regulator,
                            "failure_memory": state.failed_approaches,
                        }, indent=2),
                    ),
                    f"replan_{attempt}",
                )
                try:
                    replan_data = _json_object(replan_raw)
                    graph = graph_as_dict(replan_data, parse_subgoal_graph(replan_data))
                    graph_text = json.dumps(graph, indent=2)
                    state.subgoal_graph = graph
                    (out / f"subgoal_graph_revision_{attempt}.json").write_text(
                        graph_text + "\n", encoding="utf-8"
                    )
                except (ValueError, json.JSONDecodeError) as error:
                    # A malformed model response must not discard the entire
                    # problem run. Retain the last valid graph and continue the
                    # proof revision with the regulator's constraints.
                    (attempt_dir / "replan_error.txt").write_text(
                        f"Malformed replan response: {error}\n\n{replan_raw}",
                        encoding="utf-8",
                    )
                    state.attempts[-1]["replan_error"] = str(error)
            state.save(state_file)
            candidate = self._run(
                REVISION_PROMPT_TEMPLATE.format(
                    offline=OFFLINE_POLICY,
                    statement_lock=lock_text,
                    subgoal_graph=graph_text,
                    candidate=candidate,
                    reviews="\n\n".join(raw_reviews),
                    failure_memory=failure_memory,
                    search_policy=SEARCH_POLICY,
                    output_contract=OUTPUT_CONTRACT,
                ),
                f"revision_{attempt}",
            )

        (out / "candidate.md").write_text(candidate, encoding="utf-8")
        manifest = {
            "problem_number": problem_number,
            "statement_sha256": lock.sha256,
            "candidate_outcome": outcome,
            "reviews": [asdict(review) for review in reviews],
            "verification_evidence": [
                asdict(evidence) for evidence in self.verification_evidence
            ],
            "gate": asdict(decision),
        }
        (out / "manifest.json").write_text(
            json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
        )
        return PipelineResult(problem_number, outcome, decision, out)

    def _run_reviews(
        self,
        candidate: str,
        lock_text: str,
        graph_text: str,
        attempt: int,
        attempt_dir: Path,
    ) -> tuple[list[Review], list[str]]:
        reviews = []
        raw_reviews = []
        for role, mandate in REVIEW_MANDATES.items():
            stage = f"review_{role}_{attempt}"
            raw = self._run(
                VERIFIER_PROMPT_TEMPLATE.format(
                    offline=OFFLINE_POLICY,
                    role=role,
                    role_mandate=mandate,
                    statement_lock=lock_text,
                    subgoal_graph=graph_text,
                    candidate=candidate,
                ),
                stage,
            )
            (attempt_dir / f"review_{role}.json").write_text(raw, encoding="utf-8")
            raw_reviews.append(raw)
            context_id = self.runner.context_id(stage)
            try:
                reviews.append(_review(
                    _json_object(raw), reviewer_id=f"{role}-{attempt}",
                    expected_role=role, context_id=context_id,
                ))
            except (KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
                reviews.append(_failed_review(
                    reviewer_id=f"{role}-{attempt}", expected_role=role,
                    context_id=context_id, error=error,
                ))

        adjudication_stage = f"adjudication_{attempt}"
        raw_adjudication = self._run(
            ADJUDICATOR_PROMPT_TEMPLATE.format(
                offline=OFFLINE_POLICY,
                statement_lock=lock_text,
                subgoal_graph=graph_text,
                candidate=candidate,
                reviews="\n\n".join(raw_reviews),
            ),
            adjudication_stage,
        )
        (attempt_dir / "adjudication.json").write_text(
            raw_adjudication, encoding="utf-8"
        )
        raw_reviews.append(raw_adjudication)
        adjudication_context = self.runner.context_id(adjudication_stage)
        try:
            reviews.append(_review(
                _json_object(raw_adjudication),
                reviewer_id=f"adjudicator-{attempt}",
                expected_role="adjudicator",
                context_id=adjudication_context,
            ))
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
            reviews.append(_failed_review(
                reviewer_id=f"adjudicator-{attempt}",
                expected_role="adjudicator",
                context_id=adjudication_context,
                error=error,
            ))
        return reviews, raw_reviews
