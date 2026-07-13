"""Provider-agnostic, persisted multi-context proof pipeline."""

import json
import hashlib
import re
from datetime import datetime, timezone
import uuid
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Protocol

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
from run_contract import (
    STAGE_CACHE_SCHEMA_VERSION,
    RunContractError,
    canonical_json,
    make_run_contract,
    run_contract_id,
    run_context_id,
    stage_cache_context_id,
    validate_run_contract,
)


_ROUTING_MODES = {
    "statement_audit", "human_clarification", "formal_search",
    "exact_construction_search", "construction_verification",
    "shared_infrastructure_search", "subproblem_decomposition",
    "exact_computation", "counterexample_search", "literature_search",
    "natural_language_research",
}


def normalize_research_directive(
    directive: dict | None, *, parent_statement_sha256: str,
) -> tuple[dict, str]:
    """Validate a search-plane directive without changing the truth target."""
    if directive is None:
        directive = {
            "schema_version": 1,
            "parent_statement_sha256": parent_statement_sha256,
            "recommended_attack_modes": ["natural_language_research"],
            "subproblem_targets": [],
        }
    if not isinstance(directive, dict) or set(directive) != {
        "schema_version", "parent_statement_sha256",
        "recommended_attack_modes", "subproblem_targets",
    }:
        raise ValueError("research directive schema is not closed")
    if directive.get("schema_version") != 1 \
            or directive.get("parent_statement_sha256") != parent_statement_sha256:
        raise ValueError("research directive parent statement binding mismatch")
    modes = directive.get("recommended_attack_modes")
    if not isinstance(modes, list) or not modes or len(modes) != len(set(modes)) \
            or any(mode not in _ROUTING_MODES for mode in modes):
        raise ValueError("research directive contains invalid attack modes")
    raw_targets = directive.get("subproblem_targets")
    if not isinstance(raw_targets, list):
        raise ValueError("research directive subproblem targets must be a list")
    targets = []
    for target in raw_targets:
        required = {
            "subproblem_id", "part_index", "subproblem_contract_sha256",
            "parent_statement_sha256", "focus_question", "focus_question_sha256",
        }
        if not isinstance(target, dict) or set(target) != required:
            raise ValueError("research directive subproblem schema is not closed")
        if target.get("parent_statement_sha256") != parent_statement_sha256:
            raise ValueError("subproblem target parent binding mismatch")
        focus = str(target.get("focus_question", "")).strip()
        focus_sha = hashlib.sha256(focus.encode("utf-8")).hexdigest()
        if not focus or target.get("focus_question_sha256") != focus_sha:
            raise ValueError("subproblem focus-question hash mismatch")
        part_index = target.get("part_index")
        if not isinstance(part_index, int) or isinstance(part_index, bool) or part_index < 1:
            raise ValueError("subproblem part index is invalid")
        expected_contract = hashlib.sha256(canonical_json({
            "parent_statement_sha256": parent_statement_sha256,
            "focus_question_sha256": focus_sha,
            "part_index": part_index,
        }).encode("utf-8")).hexdigest()
        if target.get("subproblem_contract_sha256") != expected_contract \
                or not re.fullmatch(
                    rf"erdos-[0-9]+-part-{part_index:02d}-{expected_contract[:8]}",
                    str(target.get("subproblem_id", "")),
                ):
            raise ValueError("subproblem target contract identity mismatch")
        targets.append({**target, "focus_question": focus})
    normalized = {
        "schema_version": 1,
        "parent_statement_sha256": parent_statement_sha256,
        "recommended_attack_modes": list(modes),
        "subproblem_targets": targets,
    }
    digest = hashlib.sha256(canonical_json(normalized).encode("utf-8")).hexdigest()
    return normalized, digest


class IsolatedRunner(Protocol):
    def run(self, prompt: str, *, stage: str, isolated: bool) -> str: ...
    def context_id(self, stage: str) -> str: ...
    def restore_context(self, stage: str, context_id: str) -> None: ...


@dataclass(frozen=True)
class PipelineResult:
    problem_number: int
    candidate_outcome: str
    gate: GateDecision
    artifact_dir: Path


def _failure_classification(
    outcome: str,
    decision: GateDecision,
    contract,
    reviews: list[Review],
) -> tuple[str, list[str]]:
    """Separate mathematical rejection evidence from process/schema failure."""
    if decision.status.startswith("verified_"):
        return "verified", []
    if decision.status == "awaiting_external_evidence":
        return "external_evidence", list(decision.reasons)
    if outcome == "resource_exhausted":
        return "budget", []
    statement_findings: list[str] = []
    mathematical_findings: list[str] = []
    for review in reviews:
        findings = [
            item for item in (
                *review.open_gaps,
                *review.unchecked_imports,
                *review.material_errors,
            )
            if item and not item.lower().startswith("malformed reviewer output:")
        ]
        if review.reviewer_role == "statement_integrity":
            statement_findings.extend(findings)
        else:
            mathematical_findings.extend(findings)
    mathematical_findings.extend(contract.open_gaps if contract else ())
    mathematical_findings.extend(contract.unchecked_imports if contract else ())
    if statement_findings:
        return "statement", sorted(set(statement_findings))
    if mathematical_findings:
        return "mathematical", sorted(set(mathematical_findings))
    return "operational_verification", list(decision.reasons)


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
    reported_role = str(data.get("reviewer_role", expected_role)).strip()
    accepted_roles = {
        expected_role.casefold(),
        f"independent adversarial referee ({expected_role})".casefold(),
    }
    if reported_role.casefold() not in accepted_roles:
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
        pipeline_version: str = "unrecorded",
        model_portfolio: str = "unrecorded",
        execution_config: dict | None = None,
        source_snapshot_id: str | None = None,
        source_snapshot_sha256: str | None = None,
        toolset: dict[str, Any] | None = None,
        dependencies: dict[str, Any] | None = None,
        runtime: dict[str, Any] | None = None,
        adjudicator_runner: IsolatedRunner | None = None,
        literature_context: str = "",
        literature_grounding: dict | None = None,
    ):
        self.runner = runner
        # A distinct model for the final adjudicator breaks the correlated blind
        # spots of a model reviewing its own work. Defaults to the same runner.
        self.adjudicator_runner = adjudicator_runner or runner
        # Optional offline related-work grounding, injected into the SEARCH
        # stages only (scouts + construction); reviews/adjudication stay blind
        # so the adversarial check is never softened by "known result" framing.
        self.literature_context = literature_context or ""
        self.literature_grounding = literature_grounding
        self.artifact_root = Path(artifact_root)
        self.max_revisions = max(0, max_revisions)
        self.verification_evidence = verification_evidence
        self.pipeline_version = pipeline_version
        self.model_portfolio = model_portfolio
        self.execution_config = dict(execution_config or {})
        self._stage_cache = None
        contract_context = {
            "source_snapshot_id": source_snapshot_id,
            "source_snapshot_sha256": source_snapshot_sha256,
            "toolset": toolset,
            "dependencies": dependencies,
            "runtime": runtime,
        }
        supplied = [value is not None for value in contract_context.values()]
        if any(supplied) and not all(supplied):
            missing = sorted(
                key for key, value in contract_context.items() if value is None
            )
            raise ValueError(
                "run-contract context is incomplete; missing " + ", ".join(missing)
            )
        self._run_contract_context = contract_context if all(supplied) else None
        self._active_run_contract = None

    def _budget(self) -> dict[str, Any]:
        return {
            "max_revisions": self.max_revisions,
            "scout_contexts": len(SCOUT_ROLES),
            "review_roles_per_attempt": len(REVIEW_MANDATES) + 1,
        }

    def _bind_run_contract(
        self, statement_sha256: str,
        research_directive_sha256: str | None = None,
    ) -> dict | None:
        """Bind the exact statement to this pipeline's reusable identity."""
        if self._run_contract_context is None:
            self._active_run_contract = None
            return None
        context = self._run_contract_context
        self._active_run_contract = make_run_contract(
            statement_sha256=statement_sha256,
            source_snapshot_id=context["source_snapshot_id"],
            source_snapshot_sha256=context["source_snapshot_sha256"],
            pipeline_fingerprint=self.pipeline_version,
            research_directive_sha256=(
                research_directive_sha256
                or hashlib.sha256(b"synthetic-test-research-directive").hexdigest()
            ),
            model_portfolio=self.model_portfolio,
            toolset=context["toolset"],
            budget=self._budget(),
            execution_config=self.execution_config,
            dependencies=context["dependencies"],
            runtime=context["runtime"],
        )
        return self._active_run_contract

    def _run_contract_record(self, execution_id: str) -> dict[str, Any] | None:
        if self._active_run_contract is None:
            return None
        contract = validate_run_contract(self._active_run_contract)
        contract_id = run_contract_id(contract)
        return {
            "run_contract_record_schema_version": 1,
            "execution_id": execution_id,
            "run_contract_id": contract_id,
            "run_context_id": run_context_id(
                run_contract_id_value=contract_id,
                execution_id=execution_id,
            ),
            "run_contract": contract,
        }

    def _incomplete_run_is_compatible(
        self, directory: Path, problem: str, research_directive_sha256: str,
    ) -> bool:
        expected = self._run_contract_record(directory.name)
        if expected is None:
            return False
        try:
            recorded = json.loads(
                (directory / "run_contract.json").read_text(encoding="utf-8")
            )
            if not isinstance(recorded, dict) or set(recorded) != {
                "run_contract_record_schema_version",
                "execution_id",
                "run_contract_id",
                "run_context_id",
                "run_contract",
            }:
                return False
            embedded_contract = validate_run_contract(recorded["run_contract"])
            if (
                recorded != expected
                or run_contract_id(embedded_contract) != recorded["run_contract_id"]
            ):
                return False
            problem_file = directory / "problem.txt"
            if problem_file.exists() and problem_file.read_text(
                encoding="utf-8"
            ) != problem:
                return False
            statement_lock_file = directory / "statement_lock.json"
            if statement_lock_file.exists():
                statement_lock = json.loads(
                    statement_lock_file.read_text(encoding="utf-8")
                )
                if statement_lock.get("sha256") != embedded_contract["statement_sha256"]:
                    return False
            directive_file = directory / "research_directive.json"
            if not directive_file.exists():
                return False
            directive_record = json.loads(directive_file.read_text(encoding="utf-8"))
            if directive_record.get("research_directive_sha256") \
                    != research_directive_sha256:
                return False
        except (
            KeyError,
            OSError,
            TypeError,
            ValueError,
            json.JSONDecodeError,
            RunContractError,
        ):
            return False
        return True

    @staticmethod
    def _write_json_atomic(path: Path, value: object) -> None:
        temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
        try:
            temporary.write_text(
                json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            temporary.replace(path)
        finally:
            temporary.unlink(missing_ok=True)

    @staticmethod
    def _cache_metadata_is_compatible(
        metadata: object,
        *,
        stage: str,
        prompt_sha256: str,
        response_sha256: str,
        expected_contract: dict,
        expected_contract_id: str,
        expected_cache_context_id: str,
    ) -> bool:
        required = {
            "cache_schema_version",
            "stage",
            "prompt_sha256",
            "response_sha256",
            "run_contract",
            "run_contract_id",
            "cache_context_id",
            "context_id",
            "recorded_at",
        }
        if not isinstance(metadata, dict) or set(metadata) != required:
            return False
        try:
            embedded_contract = validate_run_contract(metadata["run_contract"])
            embedded_contract_id = run_contract_id(embedded_contract)
            recorded_at = datetime.fromisoformat(metadata["recorded_at"])
        except (KeyError, TypeError, ValueError, RunContractError):
            return False
        return (
            metadata["cache_schema_version"] == STAGE_CACHE_SCHEMA_VERSION
            and metadata["stage"] == stage
            and metadata["prompt_sha256"] == prompt_sha256
            and metadata["response_sha256"] == response_sha256
            and embedded_contract == expected_contract
            and embedded_contract_id == expected_contract_id
            and metadata["run_contract_id"] == expected_contract_id
            and metadata["cache_context_id"] == expected_cache_context_id
            and isinstance(metadata["context_id"], str)
            and recorded_at.tzinfo is not None
        )

    def _run(self, prompt: str, stage: str, runner=None) -> str:
        """Call the isolated runner, caching each stage's raw response to disk so
        an interrupted run resumes from the last finished stage instead of
        regenerating it. Isolation is preserved: a cache hit replays the exact
        response that stage already produced in its own fresh conversation.

        ``runner`` overrides the model for a single stage (e.g. a distinct
        adjudicator model); it defaults to this pipeline's primary runner."""
        runner = runner or self.runner
        cache_file = self._stage_cache / f"{stage}.txt"
        metadata_file = self._stage_cache / f"{stage}.meta.json"
        prompt_sha256 = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
        if self._active_run_contract is None:
            # Without an exact statement/source/model/tool/runtime contract there
            # is no defensible cache key. The solver may continue, but no stage
            # response is persisted or replayed under an ambiguous identity.
            return runner.run(prompt, stage=stage, isolated=True)

        active_contract = validate_run_contract(self._active_run_contract)
        active_contract_id = run_contract_id(active_contract)
        cache_context_id = stage_cache_context_id(
            run_contract_id_value=active_contract_id,
            stage=stage,
            prompt_sha256=prompt_sha256,
        )
        if cache_file.exists() and metadata_file.exists():
            try:
                cached = cache_file.read_text(encoding="utf-8")
                metadata = json.loads(metadata_file.read_text(encoding="utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError, OSError, ValueError):
                cached, metadata = "", {}
            cached_response_sha256 = hashlib.sha256(
                cached.encode("utf-8")
            ).hexdigest()
            if cached.strip() and self._cache_metadata_is_compatible(
                metadata,
                stage=stage,
                prompt_sha256=prompt_sha256,
                response_sha256=cached_response_sha256,
                expected_contract=active_contract,
                expected_contract_id=active_contract_id,
                expected_cache_context_id=cache_context_id,
            ):
                context_id = str(metadata.get("context_id", ""))
                restore_context = getattr(runner, "restore_context", None)
                if context_id and callable(restore_context):
                    try:
                        restore_context(stage, context_id)
                    except Exception:
                        # A response whose isolated provenance cannot be restored
                        # is regenerated instead of being returned ambiguously.
                        pass
                    else:
                        print(f"{stage}: reusing validated cached response", flush=True)
                        return cached
                else:
                    print(f"{stage}: reusing validated cached response", flush=True)
                    return cached
        response = runner.run(prompt, stage=stage, isolated=True)
        context_id = runner.context_id(stage)
        metadata = {
            "cache_schema_version": STAGE_CACHE_SCHEMA_VERSION,
            "stage": stage,
            "prompt_sha256": prompt_sha256,
            "response_sha256": hashlib.sha256(response.encode("utf-8")).hexdigest(),
            "run_contract": active_contract,
            "run_contract_id": active_contract_id,
            "cache_context_id": cache_context_id,
            "context_id": context_id,
            "recorded_at": datetime.now(timezone.utc).isoformat(),
        }
        cache_tmp = cache_file.with_suffix(cache_file.suffix + ".tmp")
        metadata_tmp = metadata_file.with_suffix(metadata_file.suffix + ".tmp")
        cache_tmp.write_text(response, encoding="utf-8")
        cache_tmp.replace(cache_file)
        metadata_tmp.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
        metadata_tmp.replace(metadata_file)
        return response

    def solve(
        self, problem_number: int, problem: str, *,
        research_directive: dict | None = None,
    ) -> PipelineResult:
        """Run all isolated stages, persist evidence, and apply the hard gate."""
        lock = make_statement_lock(problem)
        directive, directive_sha256 = normalize_research_directive(
            research_directive, parent_statement_sha256=lock.sha256,
        )
        self._bind_run_contract(lock.sha256, directive_sha256)
        prob_dir = self.artifact_root / f"problem_{problem_number}"
        # Resume the newest incomplete run (no manifest.json) so a stop mid-problem
        # continues from the last finished stage; otherwise start a fresh run.
        incomplete = sorted(
            (d for d in prob_dir.glob("*")
             if d.is_dir()
             and not (d / "manifest.json").exists()
             and self._incomplete_run_is_compatible(
                 d, lock.original_statement, directive_sha256,
             )),
            key=lambda d: d.name,
        ) if prob_dir.exists() else []
        if incomplete:
            out = incomplete[-1]
            new_execution = False
        else:
            run_id = (
                datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
                + "-" + uuid.uuid4().hex[:8]
            )
            out = prob_dir / run_id
            new_execution = True
        out.mkdir(parents=True, exist_ok=True)
        if new_execution:
            self._write_json_atomic(out / "research_directive.json", {
                **directive,
                "research_directive_sha256": directive_sha256,
            })
            contract_record = self._run_contract_record(out.name)
            if contract_record is not None:
                self._write_json_atomic(out / "run_contract.json", contract_record)
        self._stage_cache = out / "_stage_cache"
        self._stage_cache.mkdir(exist_ok=True)
        lock_text = statement_lock_text(lock)
        research_context = (
            f"{lock_text}\n\nRESEARCH ROUTING DIRECTIVE (search guidance only; "
            "it cannot modify the exact locked target):\n"
            f"ROUTING_PACKET_SHA256: {directive_sha256}\n"
            + json.dumps(directive, indent=2, ensure_ascii=False, sort_keys=True)
        )
        search_context = research_context
        if self.literature_context:
            (out / "literature_context.md").write_text(
                self.literature_context, encoding="utf-8"
            )
            search_context = (
                research_context
                + "\n\nUNTRUSTED RELATED-WORK CONTEXT (recall aid only; NOT part "
                  "of the locked problem; never cite as authority; state and "
                  "verify the exact hypotheses of any theorem you use):\n"
                  "<untrusted_literature>\n" + self.literature_context
                + "\n</untrusted_literature>"
            )
        (out / "problem.txt").write_text(lock.original_statement, encoding="utf-8")
        (out / "statement_lock.json").write_text(
            json.dumps(asdict(lock), indent=2) + "\n", encoding="utf-8"
        )

        scouts = []
        for index, role in enumerate(SCOUT_ROLES, 1):
            prompt = SCOUT_PROMPT_TEMPLATE.format(
                offline=OFFLINE_POLICY, role=role, search=SEARCH_POLICY,
                problem=search_context,
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
                statement_lock=research_context,
                scouts=scout_bundle,
                feedback="NONE",
            ),
            "synthesis",
        )
        try:
            planner_data = _json_object(synthesis_raw)
        except (ValueError, json.JSONDecodeError) as error:
            # All scouts already succeeded; a malformed planner response (e.g. an
            # unescaped quote in a JSON string) must not discard the whole run.
            # Fall back to a minimal single-goal graph and let construction
            # proceed from the scout reports, mirroring the replan fallback.
            (out / "synthesis_error.txt").write_text(
                f"Malformed synthesis response: {error}\n\n{synthesis_raw}",
                encoding="utf-8",
            )
            planner_data = {
                "summary": "planner output was unparseable; using a minimal "
                           "single-goal graph so construction can still proceed",
                "bottleneck_ids": ["GOAL"],
                "subgoals": [{
                    "id": "GOAL", "claim": lock.original_statement,
                    "dependencies": [], "centrality": 5, "falsifiable": True,
                }],
            }
        graph = graph_as_dict(planner_data, parse_subgoal_graph(planner_data))
        graph_text = json.dumps(graph, indent=2)
        (out / "subgoal_graph.json").write_text(graph_text + "\n", encoding="utf-8")

        state = ResearchState(statement_lock=asdict(lock), subgoal_graph=graph)
        state_file = out / "research_state.json"
        state.save(state_file)

        candidate = self._run(
            CONSTRUCTION_PROMPT_TEMPLATE.format(
                candidate_prompt=CANDIDATE_PROMPT_TEMPLATE.format(
                    problem=search_context
                ),
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
                candidate, research_context, graph_text, attempt, attempt_dir
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
                    statement_lock=research_context,
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
                        statement_lock=research_context,
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
                    statement_lock=research_context,
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
        active_contract_id = (
            run_contract_id(self._active_run_contract)
            if self._active_run_contract is not None else None
        )
        failure_plane, failure_evidence = _failure_classification(
            outcome, decision, contract, reviews
        )
        manifest = {
            "problem_number": problem_number,
            "execution_id": out.name,
            "pipeline_version": self.pipeline_version,
            "model_portfolio": self.model_portfolio,
            "adjudicator_distinct_model": self.adjudicator_runner is not self.runner,
            "literature_grounding": self.literature_grounding,
            "budget": {
                **self.execution_config,
                **self._budget(),
            },
            "run_contract_id": active_contract_id,
            "run_context_id": (
                run_context_id(
                    run_contract_id_value=active_contract_id,
                    execution_id=out.name,
                )
                if active_contract_id is not None else None
            ),
            "run_contract": self._active_run_contract,
            "statement_sha256": lock.sha256,
            "research_directive": directive,
            "research_directive_sha256": directive_sha256,
            "candidate_sha256": hashlib.sha256(
                candidate.encode("utf-8")
            ).hexdigest(),
            "candidate_outcome": outcome,
            "failure_plane": failure_plane,
            "failure_evidence": failure_evidence,
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
            runner=self.adjudicator_runner,
        )
        (attempt_dir / "adjudication.json").write_text(
            raw_adjudication, encoding="utf-8"
        )
        raw_reviews.append(raw_adjudication)
        # Provenance for the adjudication must come from the runner that served
        # it — which is a distinct model when an adjudicator_runner is supplied.
        adjudication_context = self.adjudicator_runner.context_id(adjudication_stage)
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
