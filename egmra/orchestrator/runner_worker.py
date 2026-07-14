"""Runner-backed research worker: turns model responses into WorkerOutput.

This closes the gap where a browser/model runner produced only advisory text that
the deterministic worker ignored. :class:`RunnerWorker` drives a ``ModelRunner``
(browser ChatGPT in production, a structured demo/fake in tests) through
role-specific prompts, parses the response against a strict JSON schema, and
converts it into a :class:`~egmra.orchestrator.loop.WorkerOutput` — proposing
claims, lemmas, falsifiers, retrieval queries, candidate sequences, experiments,
and subgoals.

Epistemic boundaries enforced here:

* The worker never emits proof/verification evidence. A text model's output is
  *hypotheses and structure*, never a kernel/exact-computation artifact, so the
  goal claim can only become SUPPORTED through the real verification pipeline —
  not because a model asserted it.
* Unparseable mathematical output is rejected (recorded as a failure with no
  claims), never silently treated as progress or proof.
* The canonical goal formula stays the locked target; the model may propose
  subsidiary claims but cannot substitute the research target.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any

from egmra.agents.runner import DeterministicRunner, ModelRunner, RunnerResponse
from egmra.compute.artifact import ReplayReport
from egmra.compute.service import ComputeService
from egmra.compute.spec import ExperimentSpec
from egmra.lean.kernel_checker import expected_type_hash as _canonical_type_hash
from egmra.orchestrator.loop import (
    WorkerOutput,
    _default_independent_replay_executor,
    _execute_finite_experiment,
)
from egmra.provenance.hashing import sha256_hex

_CLAIM_ID_RE = re.compile(r"[^A-Za-z0-9_.-]")
_MAX_CLAIMS = 16
_MAX_LIST = 24
_MAX_SEQ_TERMS = 64

WORKER_RESPONSE_SCHEMA = {
    "goal_restatement": "str",
    "claims": "list[{claim_id, statement, depends_on[], scope, confidence}]",
    "proof_steps": "list[str]",
    "assumptions": "list[str]",
    "falsifiers": "list[str]",
    "search_queries": "list[str]",
    "candidate_sequences": "list[list[int]]",
    "experiments": "list[{description, kind, code?, inputs?, claim_id?, coverage?}]",
    "formalization_requests": "list[str]",
    "lean_declaration_candidates": "list[{claim_id, declaration_name, source, expected_type}]",
    "open_subgoals": "list[str]",
    "bottleneck": "str",
    "confidence": "number 0..1",
}


class WorkerResponseSchemaError(ValueError):
    """Raised when a model response cannot be parsed into the worker schema."""


def _extract_json_object(text: str) -> str:
    """Return the first balanced top-level JSON object substring in ``text``."""
    start = text.find("{")
    if start < 0:
        raise WorkerResponseSchemaError("no JSON object found in model response")
    depth = 0
    in_string = False
    escape = False
    for i in range(start, len(text)):
        ch = text[i]
        if in_string:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = False
            continue
        if ch == '"':
            in_string = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start:i + 1]
    raise WorkerResponseSchemaError("unbalanced JSON object in model response")


def _as_str_list(value: Any, *, field_name: str) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise WorkerResponseSchemaError(f"{field_name} must be a list")
    out: list[str] = []
    for item in value[:_MAX_LIST]:
        if not isinstance(item, str):
            raise WorkerResponseSchemaError(f"{field_name} entries must be strings")
        cleaned = item.strip()
        if cleaned:
            out.append(cleaned)
    return out


def parse_worker_response(text: str) -> dict[str, Any]:
    """Strictly parse a model response into the normalized worker schema."""
    document = json.loads(_extract_json_object(text))
    if not isinstance(document, dict):
        raise WorkerResponseSchemaError("model response is not a JSON object")

    claims_raw = document.get("claims") or []
    if not isinstance(claims_raw, list):
        raise WorkerResponseSchemaError("claims must be a list")
    claims: list[dict[str, Any]] = []
    for entry in claims_raw[:_MAX_CLAIMS]:
        if not isinstance(entry, dict):
            raise WorkerResponseSchemaError("each claim must be an object")
        statement = entry.get("statement")
        if not isinstance(statement, str) or not statement.strip():
            raise WorkerResponseSchemaError("each claim needs a non-empty 'statement'")
        depends_on = entry.get("depends_on") or []
        if not isinstance(depends_on, list) or not all(isinstance(d, str) for d in depends_on):
            raise WorkerResponseSchemaError("claim 'depends_on' must be a list of strings")
        scope = entry.get("scope", "general")
        if scope not in {"general", "parameter_range", "finite_domain", "conditional"}:
            scope = "general"
        claims.append({
            "claim_id": str(entry.get("claim_id", "")).strip(),
            "statement": statement.strip(),
            "depends_on": [d.strip() for d in depends_on if d.strip()],
            "scope": scope,
            "confidence": _confidence(entry.get("confidence")),
        })

    sequences: list[list[int]] = []
    raw_sequences = document.get("candidate_sequences") or []
    if not isinstance(raw_sequences, list):
        raise WorkerResponseSchemaError("candidate_sequences must be a list")
    for seq in raw_sequences[:_MAX_LIST]:
        if not isinstance(seq, list):
            raise WorkerResponseSchemaError("each candidate sequence must be a list")
        terms = seq[:_MAX_SEQ_TERMS]
        if not all(isinstance(n, int) and not isinstance(n, bool) for n in terms):
            raise WorkerResponseSchemaError("candidate sequences must contain only integers")
        if terms:
            sequences.append(list(terms))

    experiments: list[dict[str, Any]] = []
    for exp in (document.get("experiments") or [])[:_MAX_LIST]:
        if not isinstance(exp, dict):
            raise WorkerResponseSchemaError("each experiment must be an object")
        description = str(exp.get("description", "")).strip()
        if not description:
            continue
        entry: dict[str, Any] = {
            "description": description,
            "kind": str(exp.get("kind", "unspecified")).strip() or "unspecified",
        }
        # Optional finite-check payload: a capability-free `experiment(inputs)`
        # the sandbox will contain (task 4.5). Executed only if a compute service
        # is configured; a match yields at most COMPUTATIONAL_EVIDENCE, never a proof.
        code = exp.get("code")
        if isinstance(code, str) and code.strip():
            inputs = exp.get("inputs")
            entry["code"] = code
            entry["inputs"] = inputs if isinstance(inputs, dict) else {}
            entry["claim_id"] = str(exp.get("claim_id", "")).strip()
            entry["coverage"] = str(exp.get("coverage", "")).strip()
        experiments.append(entry)

    lean_candidates: list[dict[str, str]] = []
    for cand in (document.get("lean_declaration_candidates") or [])[:_MAX_LIST]:
        if not isinstance(cand, dict):
            raise WorkerResponseSchemaError("each lean_declaration_candidate must be an object")
        source = str(cand.get("source", "")).strip()
        declaration_name = str(cand.get("declaration_name", "")).strip()
        expected_type = str(cand.get("expected_type", "")).strip()
        # A candidate needs a declaration name and the intended type it must prove.
        # The proof ``source`` is optional: a source-less candidate is a *pinned
        # formalization request* an autonomous formalizer (e.g. Aristotle) fills
        # in; either way the pinned kernel re-checks it (never a fabricated proof).
        if not (declaration_name and expected_type):
            continue
        lean_candidates.append({
            "claim_id": str(cand.get("claim_id", "")).strip(),
            "declaration_name": declaration_name,
            "source": source,
            "expected_type": expected_type,
        })

    return {
        "goal_restatement": str(document.get("goal_restatement", "")).strip(),
        "claims": claims,
        "proof_steps": _as_str_list(document.get("proof_steps"), field_name="proof_steps"),
        "assumptions": _as_str_list(document.get("assumptions"), field_name="assumptions"),
        "falsifiers": _as_str_list(document.get("falsifiers"), field_name="falsifiers"),
        "search_queries": _as_str_list(document.get("search_queries"), field_name="search_queries"),
        "candidate_sequences": sequences,
        "experiments": experiments,
        "formalization_requests": _as_str_list(
            document.get("formalization_requests"), field_name="formalization_requests"),
        "lean_declaration_candidates": lean_candidates,
        "open_subgoals": _as_str_list(document.get("open_subgoals"), field_name="open_subgoals"),
        "bottleneck": str(document.get("bottleneck", "")).strip(),
        "confidence": _confidence(document.get("confidence")),
    }


def _confidence(value: Any) -> float:
    try:
        conf = float(value)
    except (TypeError, ValueError):
        return 0.0
    return max(0.0, min(1.0, conf))


def _safe_claim_id(raw: str, *, fallback: str) -> str:
    cleaned = _CLAIM_ID_RE.sub("_", raw).strip("_")
    return cleaned or fallback


def cold_pass_prompt(statement: str, *, role: str) -> str:
    return (
        "You are an EGMRA mathematical research worker performing a BLIND cold "
        f"pass in the role '{role}'. Do NOT use any literature yet.\n\n"
        f"STATEMENT:\n{statement}\n\n"
        "List, as JSON only, plausible falsifiers to check first and retrieval "
        "queries to run next. Do NOT claim the statement is proved or disproved.\n"
        "Return ONLY a JSON object with keys: falsifiers (list of strings), "
        "search_queries (list of strings), bottleneck (string), "
        "confidence (number 0..1)."
    )


def branch_prompt(statement: str, *, role: str, branch_id: str, packet_summary: str) -> str:
    return (
        f"You are an EGMRA research worker in the role '{role}' working branch "
        f"'{branch_id}'. Reason rigorously about the target below.\n\n"
        f"TARGET STATEMENT:\n{statement}\n\n"
        f"FROZEN LITERATURE PACKET (read-only):\n{packet_summary or '(none available)'}\n\n"
        "Propose subsidiary claims/lemmas (NOT the target itself), falsifiers, "
        "retrieval queries, candidate integer sequences for OEIS lookup, and "
        "finite experiments. Do NOT assert the target is proved; proof requires "
        "independent verification you do not perform.\n"
        "For a finite experiment you MAY include a capability-free Python function "
        "`def experiment(inputs): ...` returning {\"result\": bool, \"coverage\": str} "
        "in an 'code' field (with 'inputs' object, a 'claim_id' it checks, and a "
        "'coverage' string). No imports, file, or network access are available; it "
        "runs in a sandbox and yields only finite computational evidence.\n"
        "You MAY also request formalization and propose Lean declaration candidates: "
        "each is {claim_id, declaration_name, source (Lean 4 + Mathlib, `import Mathlib`), "
        "expected_type (the exact intended Lean type it proves)}. These are re-checked "
        "by an independent pinned Lean kernel; a claim is never proved because you assert it.\n"
        "Return ONLY a JSON object with keys: goal_restatement (string), claims "
        "(list of {claim_id, statement, depends_on, scope, confidence}), proof_steps "
        "(list of strings), assumptions (list of strings), falsifiers (list), "
        "search_queries (list), candidate_sequences (list of integer lists), "
        "experiments (list of {description, kind, code?, inputs?, claim_id?, coverage?}), "
        "formalization_requests (list of strings), lean_declaration_candidates (list of "
        "{claim_id, declaration_name, source, expected_type}), open_subgoals (list), "
        "bottleneck (string), confidence (number 0..1)."
    )


def referee_prompt(statement: str, claims: list[dict[str, Any]]) -> str:
    rendered = "\n".join(f"- {c['claim_id'] or '?'}: {c['statement']}" for c in claims) or "(none)"
    return (
        "You are an independent skeptical referee. For the target and the "
        "proposed claims below, list concrete objections or gaps as JSON.\n\n"
        f"TARGET:\n{statement}\n\nPROPOSED CLAIMS:\n{rendered}\n\n"
        "Return ONLY a JSON object with keys: falsifiers (list of strings) and "
        "bottleneck (string). Do NOT approve or assert any proof."
    )


@dataclass
class RunnerWorker:
    """A ``Worker`` that turns a ``ModelRunner``'s structured output into research state."""

    runner: ModelRunner
    goal_claim_id: str = "goal"
    goal_formula: str = ""
    role: str = "prover"
    max_repair_attempts: int = 1
    referee: ModelRunner | None = None
    compute_service: ComputeService | None = None
    replay_sandbox: object | None = field(default_factory=_default_independent_replay_executor)
    lean_version: str = ""
    mathlib_commit: str = ""
    lean_project: Any = None
    trust_policy: str = "classical-whitelist"
    formalizer: Any = None
    parsed_responses: list[dict[str, Any]] = field(default_factory=list)

    def for_role(self, role: str) -> "RunnerWorker":
        """A role-specialized view (distinct branch role) sharing the same runner.

        The orchestrator allocates a distinct role per mechanism branch so the
        prover / experimentalist / formalizer reason from different prompts; the
        shared ``parsed_responses`` keeps one audit trail across roles.
        """
        if not role or role == self.role:
            return self
        return replace(self, role=role)

    def _statement(self, contract) -> str:
        if self.goal_formula:
            return self.goal_formula
        try:
            return contract.lattice.nodes[0].conclusion
        except (AttributeError, IndexError):
            return ""

    def _packet_summary(self, packet) -> str:
        records = getattr(packet, "theorem_records", None) or []
        lines = []
        for rec in list(records)[:5]:
            statement = getattr(rec, "canonical_statement", "") or getattr(rec, "conclusion", "")
            if statement:
                lines.append(f"- {statement[:160]}")
        return "\n".join(lines)

    def _ask_structured(self, prompt: str, *, stage: str) -> tuple[dict[str, Any] | None, list[str]]:
        failures: list[str] = []
        current = prompt
        for attempt in range(self.max_repair_attempts + 1):
            response = self.runner.run(current, stage=stage)
            try:
                parsed = parse_worker_response(response.text)
                self.parsed_responses.append({"stage": stage, "attempt": attempt,
                                              "prompt_hash": response.prompt_hash})
                return parsed, failures
            except (WorkerResponseSchemaError, json.JSONDecodeError) as exc:
                failures.append(f"malformed_model_output:{stage}:attempt{attempt}:{exc}")
                current = (
                    "Your previous reply was not valid JSON matching the required "
                    f"schema ({exc}). Re-emit ONLY the JSON object, nothing else.\n\n"
                    + prompt
                )
        # Reject: no claims/evidence are fabricated from unparseable output.
        failures.append(f"unparseable_model_output:{stage}")
        return None, failures

    def cold_pass(self, contract, *, budget: float) -> WorkerOutput:
        statement = self._statement(contract)
        parsed, failures = self._ask_structured(
            cold_pass_prompt(statement, role=self.role), stage="cold_pass"
        )
        if parsed is None:
            return WorkerOutput(bottleneck="cold pass produced no parseable output",
                                failures=failures)
        return WorkerOutput(
            falsifiers=parsed["falsifiers"],
            search_queries=parsed["search_queries"],
            bottleneck=parsed["bottleneck"] or "blind cold pass",
            failures=failures,
        )

    def work_branch(self, contract, packet, *, branch_id: str, budget: float,
                    fencing_token: int, branch_slice=None) -> WorkerOutput:
        statement = self._statement(contract)
        parsed, failures = self._ask_structured(
            branch_prompt(statement, role=self.role, branch_id=branch_id,
                          packet_summary=self._packet_summary(packet)),
            stage=f"branch:{branch_id}",
        )
        # Always track the locked target as the goal claim; never fabricate its proof.
        proposals: list[dict[str, Any]] = [{
            "claim_id": self.goal_claim_id,
            "canonical_formula": self.goal_formula or statement,
            "informal_text": self.goal_formula or statement,
            "scope": "general",
            "dependencies": [],
        }]
        if parsed is None:
            return WorkerOutput(claim_proposals=proposals, failures=failures,
                                bottleneck="branch produced no parseable output")

        seen = {self.goal_claim_id}
        for index, claim in enumerate(parsed["claims"]):
            cid = _safe_claim_id(claim["claim_id"], fallback=f"{branch_id}_lemma_{index}")
            if cid == self.goal_claim_id or cid in seen:
                cid = f"{branch_id}_lemma_{index}"
            seen.add(cid)
            deps = [d for d in claim["depends_on"] if d and d != cid]
            proposals.append({
                "claim_id": cid,
                "canonical_formula": claim["statement"],
                "informal_text": claim["statement"],
                "scope": claim["scope"],
                "dependencies": deps,
            })

        falsifiers = list(parsed["falsifiers"])
        bottleneck = parsed["bottleneck"] or "close the goal claim"
        if self.referee is not None:
            failures, falsifiers, bottleneck = self._referee_pass(
                statement, parsed["claims"], failures, falsifiers, bottleneck
            )

        evidence, experiment_replays = self._run_experiments(
            parsed["experiments"], branch_id=branch_id, seen=seen, failures=failures)
        formal_candidates = self._build_formal_candidates(
            parsed["lean_declaration_candidates"], branch_id=branch_id, seen=seen,
            failures=failures)

        return WorkerOutput(
            claim_proposals=proposals,
            evidence=evidence,
            replay_reports=experiment_replays,
            formal_candidates=formal_candidates,
            falsifiers=falsifiers,
            search_queries=parsed["search_queries"],
            generated_sequences=parsed["candidate_sequences"],
            proof_steps=parsed["proof_steps"],
            assumptions=parsed["assumptions"],
            formalization_requests=parsed["formalization_requests"],
            failures=failures,
            bottleneck=bottleneck,
        )

    def _build_formal_candidates(self, candidates, *, branch_id: str,
                                 seen: set[str], failures: list[str] | None = None) -> list[dict]:
        """Turn model Lean declaration candidates into formal_candidates (task 4.6).

        Hashes are computed deterministically here (never trusted from the model):
        ``expected_type_hash`` is the canonical hash of the intended type — the
        same one the pinned kernel checker recomputes — so the orchestrator's
        ``candidate_type_hash == expected_type_hash`` binding is sound. Emitted
        only when a pinned Lean environment is configured; a candidate is inert
        unless research() also has a LeanService to run the real kernel.

        A source-less candidate is a *pinned formalization request*: when a
        ``formalizer`` (e.g. Aristotle) is configured, the vendor produces the
        PROOF while the obligation (``declaration_name`` + ``expected_type``) stays
        pinned here; the produced Lean is untrusted and re-checked by the pinned
        kernel downstream. A vendor status never promotes on its own.
        """
        if not (self.lean_version and self.mathlib_commit):
            return []
        if self.lean_project is not None:
            project_hash = sha256_hex(str(Path(self.lean_project).resolve()))
        else:
            project_hash = sha256_hex(f"{self.lean_version}\n{self.mathlib_commit}")
        out: list[dict] = []
        for cand in candidates:
            requested = cand.get("claim_id") or ""
            target = requested if requested in seen else self.goal_claim_id
            expected_type = cand["expected_type"]
            source = (cand.get("source") or "").strip()
            if not source and self.formalizer is not None:
                try:
                    produced = self.formalizer.formalize(
                        declaration_name=cand["declaration_name"],
                        expected_type=expected_type,
                        informal_statement=self.goal_formula or expected_type,
                    )
                    source = (produced or "").strip()
                except Exception as exc:  # noqa: BLE001 - vendor outage is not a math failure
                    source = ""
                    if failures is not None:
                        failures.append(
                            f"formalizer_error:{branch_id}:{type(exc).__name__}")
                if not source and failures is not None:
                    failures.append(
                        f"formalization_unavailable:{branch_id}:{cand['declaration_name']}")
            if not source:
                # Nothing to verify (no proof source, no/failed formalizer); never
                # fabricate a formal artifact.
                continue
            out.append({
                "claim_id": target,
                "source": source,
                "declaration_name": cand["declaration_name"],
                "expected_type_source": expected_type,
                "lean_version": self.lean_version,
                "mathlib_commit": self.mathlib_commit,
                "project_hash": project_hash,
                "expected_type_hash": _canonical_type_hash(expected_type),
                "immutable_target_module_hash": sha256_hex(
                    f"module\n{self.lean_version}\n{self.mathlib_commit}\n"
                    f"{cand['declaration_name']}"),
                "trust_policy": self.trust_policy,
            })
        return out

    def _run_experiments(self, experiments, *, branch_id: str, seen: set[str],
                         failures: list[str]) -> tuple[list[dict], list[ReplayReport]]:
        """Execute model-proposed finite experiments in the trusted sandbox (task 4.5).

        Runs at most three coded experiments; each is contained by the compute
        service's capability-free sandbox and yields ``exact_computation`` evidence
        only when the predicate returns True and an independent replay matches — so
        the goal can reach at most COMPUTATIONAL_EVIDENCE, never a proof.
        """
        evidence: list[dict] = []
        replays: list[ReplayReport] = []
        if self.compute_service is None:
            return evidence, replays
        executed = 0
        for index, exp in enumerate(experiments):
            code = exp.get("code")
            if not code:
                continue
            if executed >= 3:
                break
            executed += 1
            requested = exp.get("claim_id") or ""
            target = requested if requested in seen else self.goal_claim_id
            try:
                spec = ExperimentSpec(
                    purpose=f"{branch_id}:{target}:{index}",
                    claim_ids=(target,), branch_ids=(branch_id,),
                    inputs=exp.get("inputs") or {}, coverage=exp.get("coverage") or "",
                    arithmetic_mode="exact",
                )
            except (ValueError, TypeError) as exc:
                failures.append(f"invalid_experiment_spec:{branch_id}:{exc}")
                continue
            ev, rp, fl = _execute_finite_experiment(
                self.compute_service, self.replay_sandbox, spec, code, target)
            evidence.extend(ev)
            replays.extend(rp)
            failures.extend(fl)
        return evidence, replays

    def _referee_pass(self, statement, claims, failures, falsifiers, bottleneck):
        """Independent skeptical pass; its objections augment falsifiers, never approve."""
        try:
            reply = self.referee.run(referee_prompt(statement, claims), stage="referee")
            parsed = parse_worker_response(reply.text)
        except (WorkerResponseSchemaError, json.JSONDecodeError, RuntimeError, ValueError) as exc:
            failures.append(f"referee_unavailable:{type(exc).__name__}")
            return failures, falsifiers, bottleneck
        merged = list(dict.fromkeys([*falsifiers, *parsed["falsifiers"]]))
        return failures, merged, (parsed["bottleneck"] or bottleneck)


@dataclass
class StructuredDemoRunner:
    """A credential-free ``ModelRunner`` emitting schema-valid JSON (tests/demos only).

    It proposes structure (a subsidiary lemma, falsifiers, queries) but NEVER any
    proof/evidence, so it can never manufacture a verified result. Its identity is
    unattested, exactly like ``DeterministicRunner``.
    """

    runner_id: str = "structured-demo-local"
    _delegate: DeterministicRunner = field(default_factory=DeterministicRunner)
    calls: list[dict[str, str]] = field(default_factory=list)

    def run(self, prompt: str, *, stage: str) -> RunnerResponse:
        base = self._delegate.run(prompt, stage=stage)
        payload = self._payload(prompt, stage)
        self.calls.append({"stage": stage, "prompt_hash": base.prompt_hash})
        return RunnerResponse(text=json.dumps(payload), model=base.model,
                              context_id=base.context_id, prompt_hash=base.prompt_hash)

    def _payload(self, prompt: str, stage: str) -> dict[str, Any]:
        digest = sha256_hex(prompt)[:8]
        if stage == "cold_pass":
            return {
                "falsifiers": ["check the smallest nontrivial cases",
                               "look for a boundary counterexample"],
                "search_queries": [f"prior work related to {digest}"],
                "bottleneck": "no literature yet (blind pass)",
                "confidence": 0.1,
            }
        if stage == "referee":
            return {"falsifiers": ["verify each lemma independently"],
                    "bottleneck": "claims need independent verification"}
        return {
            "goal_restatement": "restated target",
            "claims": [{
                "claim_id": f"lemma_{digest}",
                "statement": "a subsidiary lemma proposed for the target",
                "depends_on": [], "scope": "general", "confidence": 0.3,
            }],
            "falsifiers": ["search small cases for a counterexample"],
            "search_queries": [f"techniques for target {digest}"],
            "candidate_sequences": [],
            "experiments": [{"description": "enumerate small finite cases",
                             "kind": "finite_enumeration"}],
            "open_subgoals": ["establish the subsidiary lemma"],
            "bottleneck": "close the goal claim",
            "confidence": 0.2,
        }
