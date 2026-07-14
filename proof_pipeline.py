"""Provider-agnostic, persisted multi-context proof pipeline."""

import json
import hashlib
import re
import stat
from datetime import datetime, timezone
import uuid
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable, Protocol

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
    VerificationBinding,
    verify_review_attestation,
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


@dataclass(frozen=True)
class PipelineResult:
    problem_number: int
    candidate_outcome: str
    gate: GateDecision
    artifact_dir: Path


@dataclass(frozen=True)
class _RunContractContext:
    source_snapshot_id: str
    source_snapshot_sha256: str
    toolset: dict[str, Any]
    dependencies: dict[str, Any]
    runtime: dict[str, Any]


def _require_real_directory(path: Path, *, label: str) -> None:
    """Reject symlinks and non-directories at a filesystem trust boundary.

    ``Path.is_dir()`` follows symlinks, which is specifically unsafe for the
    caller-selected artifact root and its problem directory.  Callers create a
    directory first (where appropriate), then use this lstat-based check before
    any provider call or artifact write.
    """
    try:
        mode = path.lstat().st_mode
    except FileNotFoundError as error:
        raise ValueError(f"{label} does not exist: {path}") from error
    if stat.S_ISLNK(mode) or not stat.S_ISDIR(mode):
        raise ValueError(f"{label} must be a real directory, not a symlink: {path}")


def _create_or_validate_real_directory(path: Path, *, label: str) -> None:
    """Create ``path`` if absent, then enforce the no-follow directory rule."""
    try:
        path.mkdir(parents=True, exist_ok=False)
    except FileExistsError:
        pass
    _require_real_directory(path, label=label)


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
_MAX_STAGE_TEXT_BYTES = 16 * 1024 * 1024
_STAGE_NAME_RE = re.compile(r"[A-Za-z0-9_-]{1,128}")


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
    def reject_duplicate_keys(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate JSON key: {key}")
            result[key] = value
        return result

    # strict=False allows raw control characters (e.g. unescaped newlines) that
    # ChatGPT often emits inside JSON string values, which strict parsing rejects.
    value = json.loads(
        stripped[start:end + 1], strict=False,
        object_pairs_hook=reject_duplicate_keys,
    )
    if not isinstance(value, dict):
        raise ValueError("review response must contain one JSON object")
    return value


def _strings(value) -> tuple[str, ...]:
    if value in (None, "", "NONE", []):
        return ()
    if isinstance(value, str):
        return (value,)
    return tuple(str(item) for item in value)


def _review(
    data: dict, *, reviewer_id: str, expected_role: str, context_id: str,
    candidate_sha256: str,
    problem_number: int,
    run_contract_id_value: str,
    execution_id: str,
    run_context_id_value: str,
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
        candidate_sha256=candidate_sha256,
        problem_number=problem_number,
        run_contract_id=run_contract_id_value,
        execution_id=execution_id,
        run_context_id=run_context_id_value,
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
        verification_evidence_provider: (
            Callable[[VerificationBinding], tuple[VerificationEvidence, ...]] | None
        ) = None,
        pipeline_version: str = "unrecorded",
        model_portfolio: str = "unrecorded",
        execution_config: dict | None = None,
        source_snapshot_id: str | None = None,
        source_snapshot_sha256: str | None = None,
        toolset: dict[str, Any] | None = None,
        dependencies: dict[str, Any] | None = None,
        runtime: dict[str, Any] | None = None,
        adjudicator_runner: IsolatedRunner | None = None,
        review_attestor: Callable[[Review, str], Review] | None = None,
        attestation_env: dict[str, str] | None = None,
        literature_context: str = "",
        literature_grounding: dict | None = None,
    ):
        self.runner = runner
        # A distinct model for the final adjudicator breaks the correlated blind
        # spots of a model reviewing its own work. Defaults to the same runner.
        self.adjudicator_runner = adjudicator_runner or runner
        # Runner identity and separation of duties must be established by a
        # boundary outside model output. Without such a gateway reviews remain
        # useful blockers, but cannot authorize promotion.
        self.review_attestor = review_attestor
        self.attestation_env = dict(attestation_env) if attestation_env is not None else None
        # Optional offline related-work grounding, injected into the SEARCH
        # stages only (scouts + construction); reviews/adjudication stay blind
        # so the adversarial check is never softened by "known result" framing.
        self.literature_context = literature_context or ""
        self.literature_grounding = literature_grounding
        self.artifact_root = Path(artifact_root)
        self.max_revisions = max(0, max_revisions)
        self.verification_evidence = verification_evidence
        self.verification_evidence_provider = verification_evidence_provider
        self.pipeline_version = pipeline_version
        self.model_portfolio = model_portfolio
        self.execution_config = dict(execution_config or {})
        self._stage_cache: Path | None = None
        context_fields = (
            ("source_snapshot_id", source_snapshot_id),
            ("source_snapshot_sha256", source_snapshot_sha256),
            ("toolset", toolset),
            ("dependencies", dependencies),
            ("runtime", runtime),
        )
        if all(value is None for _, value in context_fields):
            self._run_contract_context: _RunContractContext | None = None
        elif (
            source_snapshot_id is None
            or source_snapshot_sha256 is None
            or toolset is None
            or dependencies is None
            or runtime is None
        ):
            missing = sorted(
                key for key, value in context_fields if value is None
            )
            raise ValueError(
                "run-contract context is incomplete; missing " + ", ".join(missing)
            )
        else:
            self._run_contract_context = _RunContractContext(
                source_snapshot_id=source_snapshot_id,
                source_snapshot_sha256=source_snapshot_sha256,
                toolset=toolset,
                dependencies=dependencies,
                runtime=runtime,
            )
        self._active_run_contract: dict[str, Any] | None = None
        self._active_problem_number = 0
        self._active_execution_id = ""

    def _budget(self) -> dict[str, Any]:
        return {
            "max_revisions": self.max_revisions,
            "scout_contexts": len(SCOUT_ROLES),
            "review_roles_per_attempt": len(REVIEW_MANDATES) + 1,
        }

    def _bind_run_contract(
        self, statement_sha256: str,
        research_directive_sha256: str | None = None,
    ) -> dict[str, Any] | None:
        """Bind the exact statement to this pipeline's reusable identity."""
        if self._run_contract_context is None:
            self._active_run_contract = None
            return None
        context = self._run_contract_context
        self._active_run_contract = make_run_contract(
            statement_sha256=statement_sha256,
            source_snapshot_id=context.source_snapshot_id,
            source_snapshot_sha256=context.source_snapshot_sha256,
            pipeline_fingerprint=self.pipeline_version,
            research_directive_sha256=(
                research_directive_sha256
                or hashlib.sha256(b"synthetic-test-research-directive").hexdigest()
            ),
            model_portfolio=self.model_portfolio,
            toolset=context.toolset,
            budget=self._budget(),
            execution_config=self.execution_config,
            dependencies=context.dependencies,
            runtime=context.runtime,
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
    def _write_text_atomic(path: Path, value: str) -> None:
        temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
        try:
            temporary.write_text(value, encoding="utf-8")
            temporary.replace(path)
        finally:
            temporary.unlink(missing_ok=True)

    def _run(
        self, prompt: str, stage: str, runner: IsolatedRunner | None = None,
    ) -> str:
        """Call the isolated runner and persist a diagnostic stage transcript.

        Stage files are deliberately *not* replayed.  They live in a
        caller-writable artifact tree, and a digest stored next to a response is
        circular authentication: an attacker can replace both.  Until a
        provider-authenticated replay receipt exists, every model stage must be
        obtained freshly from its configured runner.

        ``runner`` overrides the model for a single stage (e.g. a distinct
        adjudicator model); it defaults to this pipeline's primary runner."""
        if not isinstance(stage, str) or not _STAGE_NAME_RE.fullmatch(stage):
            raise ValueError("stage name must use the closed basename grammar")
        if not isinstance(prompt, str) \
                or len(prompt.encode("utf-8")) > _MAX_STAGE_TEXT_BYTES:
            raise ValueError("model-stage prompt exceeds the bounded byte limit")
        runner = runner or self.runner
        stage_cache = self._stage_cache
        if stage_cache is None:
            raise ValueError("stage cache is not initialized")
        _require_real_directory(stage_cache, label="stage-cache directory")
        cache_file = stage_cache / f"{stage}.txt"
        metadata_file = stage_cache / f"{stage}.meta.json"
        prompt_sha256 = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
        if self._active_run_contract is None:
            # Without an exact statement/source/model/tool/runtime contract there
            # is no defensible cache key. The solver may continue, but no stage
            # response is persisted or replayed under an ambiguous identity.
            response = runner.run(prompt, stage=stage, isolated=True)
            if not isinstance(response, str) \
                    or len(response.encode("utf-8")) > _MAX_STAGE_TEXT_BYTES:
                raise ValueError("model-stage response exceeds the bounded byte limit")
            return response

        active_contract = validate_run_contract(self._active_run_contract)
        active_contract_id = run_contract_id(active_contract)
        cache_context_id = stage_cache_context_id(
            run_contract_id_value=active_contract_id,
            stage=stage,
            prompt_sha256=prompt_sha256,
        )
        response = runner.run(prompt, stage=stage, isolated=True)
        if not isinstance(response, str) \
                or len(response.encode("utf-8")) > _MAX_STAGE_TEXT_BYTES:
            raise ValueError("model-stage response exceeds the bounded byte limit")
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
        self._write_text_atomic(cache_file, response)
        self._write_json_atomic(metadata_file, metadata)
        return response

    def solve(
        self, problem_number: int, problem: str, *,
        research_directive: dict | None = None,
    ) -> PipelineResult:
        """Run all isolated stages, persist evidence, and apply the hard gate."""
        if type(problem_number) is not int or problem_number < 1:
            raise ValueError("problem_number must be a positive integer")
        lock = make_statement_lock(problem)
        directive, directive_sha256 = normalize_research_directive(
            research_directive, parent_statement_sha256=lock.sha256,
        )
        self._bind_run_contract(lock.sha256, directive_sha256)
        _create_or_validate_real_directory(
            self.artifact_root, label="artifact root"
        )
        prob_dir = self.artifact_root / f"problem_{problem_number}"
        _create_or_validate_real_directory(prob_dir, label="problem directory")
        # Incomplete executions contain caller-writable model transcripts and
        # therefore are not safe checkpoints.  Start a fresh execution rather
        # than mixing unauthenticated cached output into a new run.
        for _ in range(32):
            run_id = (
                datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
                + "-" + uuid.uuid4().hex[:8]
            )
            out = prob_dir / run_id
            try:
                out.mkdir(mode=0o700, exist_ok=False)
            except FileExistsError:
                continue
            break
        else:  # pragma: no cover - 32 UUID collisions cannot be induced normally
            raise RuntimeError("could not allocate a unique execution directory")
        _require_real_directory(out, label="execution directory")
        self._active_problem_number = problem_number
        self._active_execution_id = out.name
        self._write_json_atomic(out / "research_directive.json", {
            **directive,
            "research_directive_sha256": directive_sha256,
        })
        contract_record = self._run_contract_record(out.name)
        if contract_record is not None:
            self._write_json_atomic(out / "run_contract.json", contract_record)
        stage_cache = out / "_stage_cache"
        stage_cache.mkdir(mode=0o700, exist_ok=False)
        _require_real_directory(stage_cache, label="stage-cache directory")
        self._stage_cache = stage_cache
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
        reviews: list[Review] = []
        active_evidence = self.verification_evidence
        for attempt in range(1, self.max_revisions + 2):
            attempt_dir = out / f"attempt_{attempt}"
            attempt_dir.mkdir(mode=0o700, exist_ok=False)
            _require_real_directory(attempt_dir, label="attempt directory")
            (attempt_dir / "candidate.md").write_text(candidate, encoding="utf-8")
            outcome = candidate_status(candidate)
            contract = candidate_contract(candidate)
            candidate_sha256 = hashlib.sha256(candidate.encode("utf-8")).hexdigest()
            active_contract_id = (
                run_contract_id(self._active_run_contract)
                if self._active_run_contract is not None else ""
            )
            active_context_id = (
                run_context_id(
                    run_contract_id_value=active_contract_id,
                    execution_id=out.name,
                ) if active_contract_id else ""
            )
            binding = VerificationBinding(
                problem_number=problem_number,
                statement_sha256=lock.sha256,
                candidate_sha256=candidate_sha256,
                run_contract_id=active_contract_id,
                execution_id=out.name,
                run_context_id=active_context_id,
            )
            if self.verification_evidence_provider is not None:
                active_evidence = tuple(self.verification_evidence_provider(binding))
            reviews, raw_reviews = self._run_reviews(
                candidate, research_context, graph_text, attempt, attempt_dir
            )
            decision = evaluate_gate(
                outcome,
                reviews,
                expected_statement_sha256=lock.sha256,
                candidate_contract=contract,
                verification_evidence=active_evidence,
                expected_candidate_sha256=candidate_sha256,
                attestation_env=self.attestation_env,
                expected_problem_number=problem_number,
                expected_run_contract_id=active_contract_id,
                expected_execution_id=out.name,
                expected_run_context_id=active_context_id,
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
        manifest_contract_id = (
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
            "run_contract_id": manifest_contract_id,
            "run_context_id": (
                run_context_id(
                    run_contract_id_value=manifest_contract_id,
                    execution_id=out.name,
                )
                if manifest_contract_id is not None else None
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
                asdict(evidence) for evidence in active_evidence
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
                active_contract_id = (
                    run_contract_id(self._active_run_contract)
                    if self._active_run_contract is not None else ""
                )
                active_context_id = (
                    run_context_id(
                        run_contract_id_value=active_contract_id,
                        execution_id=self._active_execution_id,
                    ) if active_contract_id else ""
                )
                review = _review(
                    _json_object(raw), reviewer_id=f"{role}-{attempt}",
                    expected_role=role, context_id=context_id,
                    candidate_sha256=hashlib.sha256(
                        candidate.encode("utf-8")
                    ).hexdigest(),
                    problem_number=self._active_problem_number,
                    run_contract_id_value=active_contract_id,
                    execution_id=self._active_execution_id,
                    run_context_id_value=active_context_id,
                )
                reviews.append(self._attest_review(review, stage))
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
            active_contract_id = (
                run_contract_id(self._active_run_contract)
                if self._active_run_contract is not None else ""
            )
            active_context_id = (
                run_context_id(
                    run_contract_id_value=active_contract_id,
                    execution_id=self._active_execution_id,
                ) if active_contract_id else ""
            )
            review = _review(
                _json_object(raw_adjudication),
                reviewer_id=f"adjudicator-{attempt}",
                expected_role="adjudicator",
                context_id=adjudication_context,
                candidate_sha256=hashlib.sha256(
                    candidate.encode("utf-8")
                ).hexdigest(),
                problem_number=self._active_problem_number,
                run_contract_id_value=active_contract_id,
                execution_id=self._active_execution_id,
                run_context_id_value=active_context_id,
            )
            reviews.append(self._attest_review(review, adjudication_stage))
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
            reviews.append(_failed_review(
                reviewer_id=f"adjudicator-{attempt}",
                expected_role="adjudicator",
                context_id=adjudication_context,
                error=error,
            ))
        return reviews, raw_reviews

    def _attest_review(self, review: Review, stage: str) -> Review:
        """Apply a trusted identity gateway without letting it rewrite findings."""
        if self.review_attestor is None:
            return review
        attested = self.review_attestor(review, stage)
        if not isinstance(attested, Review):
            raise ValueError("review attestor did not return a Review")
        mutable_identity_fields = {
            "authority_id", "model_provider", "model_name", "model_version",
            "model_lineage", "schema_version", "attestor_key_id", "attestation",
        }
        for field_name in review.__dataclass_fields__:
            if field_name not in mutable_identity_fields \
                    and getattr(attested, field_name) != getattr(review, field_name):
                raise ValueError(
                    f"review attestor attempted to rewrite {field_name}"
                )
        if not verify_review_attestation(attested, env=self.attestation_env):
            raise ValueError("review attestor returned an invalid attestation")
        return attested
