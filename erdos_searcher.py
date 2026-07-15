#!/usr/bin/env python3
"""Build an auditable, heuristic Erdős opportunity ranking.

This is the deliberately transparent MVP for the corpus searcher.  It does not
claim calibrated solve probabilities yet: it combines weak Bayesian priors with
explicit deterministic evidence and records the model/version on every card.
The generated attempt/outcome ledgers are the data needed for later calibration.
"""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import importlib.metadata
import json
import math
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import uuid
from collections import Counter
from collections.abc import Sequence
from contextlib import contextmanager
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import TypedDict

from erdos_ingest import (
    extract_tex_statement,
    find_latest_canonical_snapshot,
    load_canonical_corpus,
)
from feature_flags import feature_enabled
from run_contract import (
    RunContractError,
    canonical_json,
    make_run_contract,
    run_contract_id,
    run_context_id,
    validate_run_contract,
)
from run_status import classify_disposition_inputs


SCHEMA_VERSION = 2
LEDGER_SCHEMA_VERSION = 3
MODEL_VERSION = "heuristic-competing-risks-v2"
CHEAP_PROBE_VERSION = "cheap_probe_v2"
DEFAULT_MODEL_PORTFOLIO = "chatgpt-ui-unrecorded"
RESOLUTION_PRIOR = (1.0, 39.0)
PARTIAL_PRIOR = (2.0, 8.0)
LEDGER_STATUSES = {
    "verified_novel_resolution", "verified_partial_progress",
    "verified_novelty_pending", "independent_rediscovery",
    "literature_identification", "wrong_interpretation", "statement_defect",
    "formalization_mismatch", "fundamentally_flawed_candidate",
    "no_progress_within_budget", "censored_attempt", "operational_failure",
    "awaiting_external_evidence",
}
LEDGER_REQUIRED_FIELDS = {
    "problem_id", "problem_number", "execution_id", "run_contract_id",
    "run_context_id", "snapshot_id",
    "source_snapshot_sha256", "statement_sha256", "pipeline_version",
    "model_portfolio", "toolset_version", "budget", "budget_config", "status",
    "gate_status", "candidate_outcome", "learning_eligible",
}
LEDGER_OPTIONAL_FIELDS = {
    "evidence_certificate_ids", "candidate_sha256", "duration_seconds", "cost",
    "event_id", "event_sequence", "supersedes_event_id",
}
EVIDENCE_CERTIFICATE_KINDS = {
    "gate", "intent", "novelty", "partial_progress", "disposition",
}
LEDGER_GATE_STATUSES = {
    "verified_proved", "verified_disproved", "candidate_rejected",
    "awaiting_external_evidence", "unknown",
}
LEDGER_CANDIDATE_OUTCOMES = {
    "candidate_proved", "candidate_disproved", "candidate_unclassified",
    "resource_exhausted", "unknown",
}
EVIDENCE_ISSUER_POLICY = {
    "gate": {"proof_pipeline:deterministic_gate_v2"},
    "intent": {"proof_pipeline:canonical_statement_lock_v2"},
    "partial_progress": {
        "external:qualified-partial-review-v1",
        "formal:lean-clean-replay-v1",
        "computation:independent-replay-v1",
    },
    "novelty": {"external:qualified-novelty-review-v1"},
    "disposition": {"proof_pipeline:deterministic_disposition_v1"},
}
# Production has no replayable external-judgment adapter yet.  This registry is
# intentionally closed and empty; adding an adapter requires code, tests, a
# feature-flagged replay implementation, and a new ledger event.  String issuer
# labels and manual overrides can never make an event learning-eligible.
EVIDENCE_ADAPTER_REGISTRY: dict[tuple[str, str, str], object] = {}
REPLAYABLE_DISPOSITION_STATUSES = {
    "wrong_interpretation", "fundamentally_flawed_candidate",
    "no_progress_within_budget",
}
# No local disposition can train the selector until a provenance adapter or
# unforgeable production capability exists. Replayed certificates remain useful
# as audit artifacts, but caller-controlled bytes are not training authority.
AUTONOMOUS_LEARNING_STATUSES: frozenset[str] = frozenset()
EXTERNAL_JUDGMENT_STATUSES = {
    "verified_novel_resolution", "verified_partial_progress",
    "independent_rediscovery", "literature_identification",
}
SAFE_EVIDENCE_MANIFEST_FIELDS = {
    "schema_version", "projection_type", "problem_number", "execution_id",
    "run_contract", "run_contract_id", "run_context_id", "statement_sha256",
    "candidate_sha256", "gate_status", "manifest_candidate_outcome",
    "failure_plane",
}
LEDGER_TRANSITIONS = {
    "awaiting_external_evidence": {
        "verified_novelty_pending", "verified_novel_resolution",
        "independent_rediscovery", "literature_identification",
    },
    "verified_novelty_pending": {
        "verified_novel_resolution", "independent_rediscovery",
        "literature_identification",
    },
    "verified_novel_resolution": {
        "independent_rediscovery", "literature_identification",
    },
}
PIPELINE_FINGERPRINT_FILES = (
    "erdos_common.py", "proof_pipeline.py", "verification.py", "solver_prompts.py",
    "research_state.py", "run_contract.py", "run_verified_pipeline.py", "erdos_searcher.py",
    "erdos_ingest.py", "run_status.py", "problem_queue.py", "run_continuous.py",
    "run_verified_range.py", "run_sol2_batch.py", "outcome_ledger.py",
    "promote_verified_run.py", "feature_flags.py", "config/pipeline_features.json",
    "requirements.lock",
)

class BudgetConfig(TypedDict):
    max_revisions: int
    stage_timeout_s: float
    initial_backoff_s: float
    max_backoff_s: float
    request_spacing_s: float
    max_attempts: int
    rate_limit_policy: str
    browser_headless: bool
    browser_channel: str
    profile_capability: str
    scout_contexts: int
    review_roles_per_attempt: int


DEFAULT_BUDGET_CONFIG: BudgetConfig = {
    "max_revisions": 2,
    "stage_timeout_s": 1800.0,
    "initial_backoff_s": 15.0,
    "max_backoff_s": 120.0,
    "request_spacing_s": 12.0,
    "max_attempts": 8,
    "rate_limit_policy": "shared-host-tempdir-v1",
    "browser_headless": False,
    "browser_channel": "playwright-chromium",
    "profile_capability": "persistent-authenticated-user-profile-v1",
    "scout_contexts": 4,
    "review_roles_per_attempt": 8,
}


def normalized_budget_config(
    *,
    max_revisions: int,
    stage_timeout_s: float,
    initial_backoff_s: float = 15.0,
    max_backoff_s: float = 120.0,
    request_spacing_s: float = 12.0,
    max_attempts: int = 8,
    rate_limit_policy: str = "shared-host-tempdir-v1",
    browser_headless: bool = False,
    browser_channel: str = "playwright-chromium",
    profile_capability: str = "persistent-authenticated-user-profile-v1",
    scout_contexts: int = 4,
    review_roles_per_attempt: int = 8,
) -> dict:
    """Return every behavior-changing bounded-search control in canonical form."""
    normalized_max_backoff = max(0.0, min(120.0, float(max_backoff_s)))
    config: BudgetConfig = {
        "initial_backoff_s": min(max(0.0, float(initial_backoff_s)), normalized_max_backoff),
        "max_backoff_s": normalized_max_backoff,
        "max_revisions": int(max_revisions),
        "max_attempts": int(max_attempts),
        "rate_limit_policy": str(rate_limit_policy),
        "browser_headless": bool(browser_headless),
        "browser_channel": str(browser_channel),
        "profile_capability": str(profile_capability),
        "request_spacing_s": min(120.0, max(0.0, float(request_spacing_s))),
        "review_roles_per_attempt": int(review_roles_per_attempt),
        "scout_contexts": int(scout_contexts),
        "stage_timeout_s": float(stage_timeout_s),
    }
    if config["max_revisions"] < 0 or config["max_attempts"] < 1:
        raise ValueError("revision/attempt limits must be non-negative/positive")
    if config["scout_contexts"] != 4 or config["review_roles_per_attempt"] != 8:
        raise ValueError("this pipeline implementation fixes 4 scouts and 8 reviewers")
    if config["stage_timeout_s"] <= 0:
        raise ValueError("stage timeout must be positive")
    if config["initial_backoff_s"] < 0 or config["request_spacing_s"] < 0:
        raise ValueError("rate-limit delays must be non-negative")
    if config["rate_limit_policy"] != "shared-host-tempdir-v1":
        raise ValueError("unsupported rate-limit policy")
    if config["browser_channel"] != "playwright-chromium":
        raise ValueError("unsupported browser channel")
    if config["profile_capability"] != "persistent-authenticated-user-profile-v1":
        raise ValueError("unsupported browser profile capability")
    return dict(config)


def research_budget_id(
    *,
    max_revisions: int,
    stage_timeout_s: float,
    initial_backoff_s: float = 15.0,
    max_backoff_s: float = 120.0,
    request_spacing_s: float = 12.0,
    max_attempts: int = 8,
    rate_limit_policy: str = "shared-host-tempdir-v1",
    browser_headless: bool = False,
    browser_channel: str = "playwright-chromium",
    profile_capability: str = "persistent-authenticated-user-profile-v1",
    scout_contexts: int = 4,
    review_roles_per_attempt: int = 8,
) -> str:
    config = normalized_budget_config(
        max_revisions=max_revisions,
        stage_timeout_s=stage_timeout_s,
        initial_backoff_s=initial_backoff_s,
        max_backoff_s=max_backoff_s,
        request_spacing_s=request_spacing_s,
        max_attempts=max_attempts,
        rate_limit_policy=rate_limit_policy,
        browser_headless=browser_headless,
        browser_channel=browser_channel,
        profile_capability=profile_capability,
        scout_contexts=scout_contexts,
        review_roles_per_attempt=review_roles_per_attempt,
    )
    payload = json.dumps(config, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    return f"verified_pipeline_v2:{digest[:16]}"


DEFAULT_BUDGET = research_budget_id(**DEFAULT_BUDGET_CONFIG)


def split_run_budget(config: dict | BudgetConfig) -> tuple[dict, dict]:
    normalized = normalized_budget_config(**config)
    budget = {
        key: normalized[key]
        for key in ("max_revisions", "scout_contexts", "review_roles_per_attempt")
    }
    execution = {
        key: normalized[key]
        for key in (
            "stage_timeout_s", "initial_backoff_s", "max_backoff_s",
            "request_spacing_s", "max_attempts", "rate_limit_policy",
            "browser_headless", "browser_channel", "profile_capability",
        )
    }
    return budget, execution


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def runtime_identity() -> dict:
    return {
        "implementation": platform.python_implementation(),
        "python": platform.python_version(),
        "platform": sys.platform,
        "platform_release": platform.release(),
        "machine": platform.machine(),
    }


def dependency_identity(root: Path) -> dict:
    lock = root / "requirements.lock"
    return {
        "requirements_lock_sha256": sha256_file(lock) if lock.is_file() else "absent",
    }


@lru_cache(maxsize=1)
def browser_binary_identity() -> dict:
    """Identify the installed Playwright Chromium bytes without launching it."""
    try:
        manifest = Path(
            str(importlib.metadata.distribution("playwright").locate_file(
                "playwright/driver/package/browsers.json"
            ))
        )
        data = json.loads(manifest.read_text(encoding="utf-8"))
        chromium = next(
            item for item in data.get("browsers", [])
            if item.get("name") == "chromium"
        )
        revision = str(chromium["revision"])
        version = str(chromium["browserVersion"])
    except (ImportError, StopIteration, KeyError, OSError, ValueError):
        return {"revision": "absent", "version": "absent", "binary_sha256": "absent"}

    roots = [
        Path.home() / "Library" / "Caches" / "ms-playwright",
        Path.home() / ".cache" / "ms-playwright",
        Path.home() / "AppData" / "Local" / "ms-playwright",
    ]
    patterns = (
        f"chromium-{revision}/chrome-*/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing",
        f"chromium-{revision}/chrome-*/chrome",
        f"chromium-{revision}/chrome-*/chrome.exe",
    )
    executables = [
        path
        for cache_root in roots if cache_root.is_dir()
        for pattern in patterns
        for path in cache_root.glob(pattern)
        if path.is_file()
    ]
    executable = sorted(executables)[0] if executables else None
    return {
        "revision": revision,
        "version": version,
        "binary_sha256": sha256_file(executable) if executable else "absent",
    }


def toolset_identity(root: Path) -> dict:
    try:
        playwright_version = importlib.metadata.version("playwright")
        browser_manifest = Path(
            str(importlib.metadata.distribution("playwright").locate_file(
                "playwright/driver/package/browsers.json"
            ))
        )
    except importlib.metadata.PackageNotFoundError:
        playwright_version = "absent"
        browser_manifest = Path("/nonexistent")
    feature_flags = root / "config" / "pipeline_features.json"
    return {
        "browser_runner": "playwright",
        "playwright": playwright_version,
        "playwright_browsers_manifest_sha256": (
            sha256_file(browser_manifest) if browser_manifest.is_file() else "absent"
        ),
        "chromium_binary": browser_binary_identity(),
        "feature_flags_sha256": (
            sha256_file(feature_flags) if feature_flags.is_file() else "absent"
        ),
        "formal_verifier": "disabled",
        "rate_limit_state": "tempdir/erdos_chatgpt_rate_limit.json",
    }


def toolset_version(root: Path) -> str:
    identity = {
        "toolset": toolset_identity(root),
        "dependencies": dependency_identity(root),
        "runtime": runtime_identity(),
    }
    return sha256_bytes(canonical_json(identity).encode("utf-8"))


def make_allocation_context(
    *, root: Path, snapshot_id: str, source_snapshot_sha256: str,
    source_snapshot_id: str, canonical_open_source_records: int,
    pipeline_version: str, model_portfolio: str, budget: str,
    budget_config: dict | BudgetConfig, allocation_top_k: int,
) -> tuple[dict, str | None]:
    context = {
        "snapshot_id": snapshot_id,
        "source_snapshot_id": source_snapshot_id,
        "source_snapshot_sha256": source_snapshot_sha256,
        "canonical_open_source_records": int(canonical_open_source_records),
        "pipeline_version": pipeline_version,
        "model_portfolio": model_portfolio,
        "toolset_version": toolset_version(root),
        "budget": budget,
        "budget_config": budget_config,
        "allocation_top_k": int(allocation_top_k),
        "dependencies": dependency_identity(root),
        "runtime": runtime_identity(),
    }
    if model_portfolio == DEFAULT_MODEL_PORTFOLIO or "unrecorded" in model_portfolio.lower():
        return context, None
    return context, sha256_bytes(canonical_json(context).encode("utf-8"))


def research_directive_for_card(card: dict) -> dict:
    """Return the deterministic search-plane packet for one exact parent target."""
    return {
        "schema_version": 1,
        "parent_statement_sha256": card["statement"]["statement_sha256"],
        "recommended_attack_modes": list(card["routes"]),
        "subproblem_targets": [
            {
                "subproblem_id": item["subproblem_id"],
                "part_index": item["part_index"],
                "subproblem_contract_sha256": item["subproblem_contract_sha256"],
                "parent_statement_sha256": item["statement"]["statement_sha256"],
                "focus_question": item["statement"]["focus_question"],
                "focus_question_sha256": item["statement"]["focus_question_sha256"],
            }
            for item in card.get("subproblems", [])
        ],
    }


def research_directive_sha256(directive: dict) -> str:
    return sha256_bytes(canonical_json(directive).encode("utf-8"))


def bind_card_run_contract(root: Path, card: dict) -> None:
    """Attach an exact reusable contract, or explicitly withhold allocation."""
    card["toolset_version"] = toolset_version(root)
    source_snapshot_id = card["provenance"].get("source_snapshot_id")
    source_snapshot_sha256 = card["provenance"].get("source_snapshot_sha256")
    budget, execution = split_run_budget(card["budget_config"])
    try:
        contract = make_run_contract(
            statement_sha256=card["statement"]["statement_sha256"],
            source_snapshot_id=source_snapshot_id,
            source_snapshot_sha256=source_snapshot_sha256,
            pipeline_fingerprint=card["pipeline_version"],
            research_directive_sha256=card["research_directive_sha256"],
            model_portfolio=card["model_portfolio"],
            toolset=toolset_identity(root),
            budget=budget,
            execution_config=execution,
            dependencies=dependency_identity(root),
            runtime=runtime_identity(),
        )
    except RunContractError as error:
        card["run_contract_id"] = None
        card["run_contract"] = None
        card["allocation_status"] = f"withheld: {error}"
        return
    card["run_contract"] = contract
    card["run_contract_id"] = run_contract_id(contract)
    card["allocation_status"] = "exact_context_ready"


def bind_subproblem_run_contracts(root: Path, card: dict) -> None:
    budget, execution = split_run_budget(card["budget_config"])
    for subproblem in card.get("subproblems", []):
        try:
            contract = make_run_contract(
                statement_sha256=subproblem["subproblem_contract_sha256"],
                source_snapshot_id=card["provenance"]["source_snapshot_id"],
                source_snapshot_sha256=card["provenance"]["source_snapshot_sha256"],
                pipeline_fingerprint=card["pipeline_version"],
                research_directive_sha256=subproblem["subproblem_contract_sha256"],
                model_portfolio=card["model_portfolio"],
                toolset=toolset_identity(root),
                budget=budget,
                execution_config=execution,
                dependencies=dependency_identity(root),
                runtime=runtime_identity(),
            )
        except RunContractError:
            subproblem["run_contract_id"] = None
        else:
            subproblem["run_contract_id"] = run_contract_id(contract)


def canonical_problem_run_inputs(
    root: Path,
    output_root: Path,
    problem_number: int,
    *,
    model_portfolio: str,
    budget_config: dict,
    canonical_snapshot: Path | None = None,
    canonical_sources: dict[int, dict] | None = None,
) -> dict:
    """Return the exact statement and complete constructor context for a run."""
    snapshot = (
        Path(canonical_snapshot) if canonical_snapshot is not None
        else find_latest_canonical_snapshot(output_root)
    )
    sources = (
        canonical_sources if canonical_sources is not None
        else load_canonical_corpus(snapshot)
    )
    try:
        source = sources[problem_number]
    except KeyError as error:
        raise RuntimeError(
            f"canonical snapshot has no open problem {problem_number}"
        ) from error
    config = normalized_budget_config(**budget_config)
    budget, execution_config = split_run_budget(config)
    snapshot_sha256 = sha256_file(snapshot / "manifest.json")
    pipeline_version = pipeline_fingerprint(root)
    card_path = Path(output_root) / "normalized" / "problem_cards" / f"{problem_number}.json"
    try:
        card = json.loads(card_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise RuntimeError(
            f"problem {problem_number} has no readable searcher routing card"
        ) from error
    statement_sha256 = sha256_bytes(source["statement"].strip().encode("utf-8"))
    directive = research_directive_for_card(card)
    directive_sha256 = research_directive_sha256(directive)
    if (
        card.get("problem_number") != problem_number
        or card.get("pipeline_version") != pipeline_version
        or card.get("statement", {}).get("statement_sha256") != statement_sha256
        or card.get("provenance", {}).get("source_snapshot_sha256") != snapshot_sha256
        or card.get("research_directive") != directive
        or card.get("research_directive_sha256") != directive_sha256
    ):
        raise RuntimeError(
            f"problem {problem_number} searcher routing card is stale or inconsistent"
        )
    toolset = toolset_identity(root)
    dependencies = dependency_identity(root)
    runtime = runtime_identity()
    contract = make_run_contract(
        statement_sha256=statement_sha256,
        source_snapshot_id=source["provenance"]["snapshot_id"],
        source_snapshot_sha256=snapshot_sha256,
        pipeline_fingerprint=pipeline_version,
        research_directive_sha256=directive_sha256,
        model_portfolio=model_portfolio,
        toolset=toolset,
        budget=budget,
        execution_config=execution_config,
        dependencies=dependencies,
        runtime=runtime,
    )
    return {
        "statement": source["statement"].strip(),
        "canonical_source": source,
        "source_snapshot_id": source["provenance"]["snapshot_id"],
        "source_snapshot_sha256": snapshot_sha256,
        "pipeline_version": pipeline_version,
        "model_portfolio": model_portfolio,
        "toolset": toolset,
        "dependencies": dependencies,
        "runtime": runtime,
        "budget": research_budget_id(**config),
        "budget_config": config,
        "execution_config": execution_config,
        "research_directive": directive,
        "research_directive_sha256": directive_sha256,
        "run_contract": contract,
        "run_contract_id": run_contract_id(contract),
    }


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    temporary = path.with_name(
        f".{path.name}.{os.getpid()}.{uuid.uuid4().hex}.tmp"
    )
    try:
        with temporary.open("w", encoding="utf-8") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def extract_statement(tex: str) -> str:
    """Compatibility wrapper around the shared fail-closed section parser."""
    return extract_tex_statement(tex)


def normalize_space(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def git_commit(root: Path) -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=root, text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def pipeline_fingerprint(root: Path) -> str:
    """Identify exact behavior bytes without coupling artifacts to moving HEAD.

    A Git commit is release provenance, but it is not a safe cache identity for
    committed generated artifacts: an artifact-only commit would immediately
    invalidate itself.  This digest covers every behavior-defining file plus
    the runtime and therefore remains stable across unrelated commits.
    """
    inventory = [
        (name, sha256_file(root / name))
        for name in PIPELINE_FINGERPRINT_FILES
        if (root / name).is_file()
    ]
    inventory.append((
        "__runtime__",
        f"{platform.python_implementation()}-{platform.python_version()}-"
        f"{sys.platform}-{platform.machine()}",
    ))
    digest = sha256_bytes(
        json.dumps(inventory, separators=(",", ":")).encode("utf-8")
    )
    return f"pipeline-content-sha256:{digest}"


def classify_goal(statement: str) -> str:
    lowered = statement.lower()
    if "for which" in lowered or "classify" in lowered or "determine all" in lowered:
        return "classify"
    if "is it true" in lowered or "prove or disprove" in lowered:
        return "prove_or_disprove"
    if "construct" in lowered or "does there exist" in lowered:
        return "construct"
    if "maximum" in lowered or "minimum" in lowered or "estimate" in lowered:
        return "estimate"
    if "what is" in lowered or "compute" in lowered or "find the value" in lowered:
        return "compute"
    return "prove"


def statement_probe(statement: str) -> dict:
    lowered = statement.lower()
    ambiguity_markers = {
        "unspecified_constant": r"\b(?:some|a) constant\b",
        "sufficiently_large": r"sufficiently large",
        "which_objects": r"\bfor which\b",
        "asymptotic_notation": r"(?:\\gg|\\ll|\\sim|o\(|O\()",
        "multiple_questions": r"\?[^?]+\?",
        "implicit_convention": r"\b(?:path|graph|sequence|density|random)\b",
    }
    hits = [name for name, pattern in ambiguity_markers.items()
            if re.search(pattern, statement, re.IGNORECASE | re.DOTALL)]
    quantifiers = len(re.findall(
        r"\b(?:for all|for every|there exists|does there exist|any|some)\b|[∀∃]",
        lowered,
    ))
    question_count = statement.count("?")
    material = question_count > 1 or len(hits) >= 3
    status = "material" if material else "minor" if hits else "clear"
    return {
        "ambiguity_status": status,
        "ambiguity_markers": hits,
        "quantifier_signal_count": quantifiers,
        "question_count": question_count,
        "statement_characters": len(statement),
        "statement_tokens_approx": len(statement.split()),
        "requires_source_audit": status != "clear",
    }


def structure_probe(statement: str, tags: list[str]) -> dict:
    lowered = statement.lower()
    finite_terms = ("finite", "integer", "natural number", "coloring", "graph on", "subset of")
    asymptotic_terms = ("sufficiently large", "as n", "tends to", "density", "\\gg", "\\ll")
    exact_terms = ("maximum", "minimum", "exactly", "does there exist", "counterexample")
    finite_signal = any(term in lowered for term in finite_terms)
    asymptotic = any(term in lowered for term in asymptotic_terms)
    exact_search = any(term in lowered for term in exact_terms) and finite_signal
    return {
        "goal": classify_goal(statement),
        "finite_signal": finite_signal,
        "asymptotic": asymptotic,
        "multi_part": statement.count("?") > 1,
        "exact_search_affordance": exact_search,
        "primary_domain": tags[0] if tags else "unclassified",
    }


def extract_subproblems(problem_number: int, statement: str) -> list[dict]:
    """Lock explicit focus questions inside the complete source statement.

    This intentionally handles only explicit multi-question statements.  It
    never treats a punctuation fragment as a self-contained theorem: every
    part retains the entire parent statement, while a separately hashed focus
    question makes its allocation/cache identity distinct.
    """
    question_ends = [match.end() for match in re.finditer(r"\?", statement)]
    if len(question_ends) < 2:
        return []
    first_end = question_ends[0]
    first_start = max(
        statement.rfind(". ", 0, first_end),
        statement.rfind("! ", 0, first_end),
        statement.rfind("\n\n", 0, first_end),
    )
    if first_start < 0:
        first_start = 0
        shared_prefix = ""
    else:
        delimiter_width = 2
        shared_prefix = statement[: first_start + delimiter_width].strip()
        first_start += delimiter_width

    parent_statement = statement.strip()
    parent_normalized = normalize_space(parent_statement)
    parent_sha256 = sha256_bytes(parent_statement.encode("utf-8"))
    parts: list[dict] = []
    segment_start = first_start
    for index, end in enumerate(question_ends, 1):
        question = statement[segment_start:end].strip()
        segment_start = end
        if not question:
            continue
        focus_question = question
        if shared_prefix and index == 1:
            focus_question = f"{shared_prefix} {question}".strip()
        focus_sha256 = sha256_bytes(focus_question.encode("utf-8"))
        contract_sha256 = sha256_bytes(canonical_json({
            "parent_statement_sha256": parent_sha256,
            "focus_question_sha256": focus_sha256,
            "part_index": index,
        }).encode("utf-8"))
        parts.append({
            "schema_version": SCHEMA_VERSION,
            "subproblem_id": (
                f"erdos-{problem_number}-part-{index:02d}-{contract_sha256[:8]}"
            ),
            "parent_problem_id": f"erdos-{problem_number}",
            "part_index": index,
            "subproblem_contract_sha256": contract_sha256,
            "statement": {
                "original": parent_statement,
                "normalized": parent_normalized,
                "statement_sha256": parent_sha256,
                "focus_question": focus_question,
                "focus_question_sha256": focus_sha256,
            },
        })
    return parts if len(parts) >= 2 else []


def forum_probe(path: Path) -> dict:
    if not path.exists():
        return {"snapshot_available": False, "comment_count": 0, "recent_claim_signal": False}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"snapshot_available": True, "comment_count": 0, "parse_error": True,
                "recent_claim_signal": False}
    comments = data.get("comments") or []
    claim_signal = any(
        re.search(r"\b(?:proof|disproof|counterexample|solved|refut)\w*\b",
                  str(item.get("text", "")), re.IGNORECASE)
        for item in comments
    )
    return {
        "snapshot_available": True,
        "comment_count": int(data.get("comment_count", len(comments))),
        "recent_claim_signal": claim_signal,
        "retrieved_at": data.get("retrieved_at"),
        "source_html_sha256": data.get("source_html_sha256"),
    }


def outcome_probe(records: Sequence[dict | str]) -> dict:
    """Summarize only schema-valid, exact-context ledger aggregates.

    Private proof-run directories are deliberately outside the searcher's
    trust boundary.  Callers pass records returned by ``load_outcome_records``
    and filtered by ``matching_outcome_records``; a new card therefore starts
    with a neutral probe until that validated join has happened.
    """
    normalized = [record for record in records if isinstance(record, dict)]
    gates = [
        str(record["gate_status"])
        for record in normalized
        if record.get("gate_status") in LEDGER_GATE_STATUSES
    ]
    censored = sum(record.get("status") == "censored_attempt" for record in normalized)
    return {
        "runs": len(normalized),
        "attempts": len(normalized),
        "completed_manifests": len(normalized),
        "incomplete_runs": censored,
        "gate_statuses": gates,
        "censored": censored > 0,
        "correctness_gate_present_unbound": any(
            status in {"verified_proved", "verified_disproved"} for status in gates
        ),
        "learning_policy": "schema_valid_exact_context_ledger_only",
    }


def formal_probe(catalog_entry: dict, statement: str) -> dict:
    raw_formalized = catalog_entry.get("formalized")
    if isinstance(raw_formalized, dict):
        formalized = str(raw_formalized.get("state", "")).strip().lower() in {
            "yes", "true", "formalized", "proved", "proved (lean)",
        }
    elif isinstance(raw_formalized, str):
        formalized = raw_formalized.strip().lower() in {"yes", "true", "formalized"}
    else:
        formalized = raw_formalized is True
    return {
        "source_reports_formalized": formalized,
        "translation_risk": statement_probe(statement)["ambiguity_status"],
        "lean_route_available": formalized,
        "lean_evidence_certificate": False,
    }


def route_problem(card: dict) -> list[str]:
    queues: list[str] = []
    ambiguity = card["statement"]["ambiguity_status"]
    structure = card["probe_summary"]["structure"]
    forum = card["probe_summary"]["literature"]
    formal = card["probe_summary"]["formal"]
    if ambiguity == "material":
        queues.extend(["statement_audit", "human_clarification"])
    if formal["lean_route_available"]:
        queues.append("formal_search")
    if structure["goal"] == "construct":
        queues.extend(["exact_construction_search", "construction_verification"])
    if structure["exact_search_affordance"]:
        queues.extend(["exact_computation", "counterexample_search"])
    if structure["multi_part"]:
        queues.extend(["subproblem_decomposition", "shared_infrastructure_search"])
    elif formal["lean_route_available"]:
        queues.append("shared_infrastructure_search")
    if forum["recent_claim_signal"] or card["metadata"]["source_reports_resolved"]:
        queues.append("literature_search")
    if ambiguity != "material":
        queues.append("natural_language_research")
    return list(dict.fromkeys(queues or ["statement_audit"]))


def beta_summary(alpha: float, beta: float) -> dict:
    probability = alpha / (alpha + beta)
    effective_n = alpha + beta + 1
    radius = 1.96 * math.sqrt(max(probability * (1 - probability), 1e-9) / effective_n)
    return {
        "probability": round(probability, 6),
        "credible_interval_approx": [
            round(max(0.0, probability - radius), 6),
            round(min(1.0, probability + radius), 6),
        ],
        "alpha": round(alpha, 3),
        "beta": round(beta, 3),
    }


def estimate_posteriors(
    card: dict,
    outcome_records: Sequence[dict | str] | None = None,
    egmra_calibration: dict | None = None,
) -> dict:
    outcome_records = outcome_records or []
    statuses = [
        str(record.get("status", "")).strip().lower()
        if isinstance(record, dict) else str(record).strip().lower()
        for record in outcome_records
    ]
    statement = card["probe_summary"]["statement"]
    structure = card["probe_summary"]["structure"]
    literature = card["probe_summary"]["literature"]
    formal = card["probe_summary"]["formal"]
    resolved = card["metadata"]["source_reports_resolved"]
    reference_count = len(card["metadata"].get("references", []))

    ra, rb = RESOLUTION_PRIOR
    pa, pb = PARTIAL_PRIOR
    if formal["lean_route_available"]:
        ra += 0.8
        pa += 0.8
    if structure["exact_search_affordance"]:
        ra += 0.8
        pa += 0.6
    if structure["multi_part"]:
        rb += 2.0
    if statement["ambiguity_status"] == "material":
        rb += 4.0
        pb += 1.5
    elif statement["ambiguity_status"] == "minor":
        rb += 1.0
    if literature["comment_count"] > 20:
        rb += 0.5
        pa += 0.4
    if resolved:
        rb += 100.0

    failure_a = (
        1.0 + 4.0 * (statement["ambiguity_status"] == "material")
        + 1.0 * (statement["ambiguity_status"] == "minor")
    )
    failure_b = 9.0
    known_a = (
        (8.0 if resolved else 1.0)
        + min(2.0, literature["comment_count"] / 25)
        + 1.5 * bool(literature.get("recent_claim_signal"))
        + min(1.0, reference_count / 4)
    )
    known_b = 2.0 if resolved else 12.0
    pending_a, pending_b = 1.0, 9.0

    for status in statuses:
        if status == "verified_novel_resolution":
            ra += 3.0
            pa += 3.0
        elif status == "verified_partial_progress":
            pa += 3.0
        elif status == "verified_novelty_pending":
            pending_a += 3.0
        elif status in {"independent_rediscovery", "literature_identification"}:
            known_a += 3.0
        elif status in {"wrong_interpretation", "statement_defect", "formalization_mismatch"}:
            failure_a += 3.0
            rb += 0.5
            pb += 0.5
        elif status in {"fundamentally_flawed_candidate", "no_progress_within_budget"}:
            rb += 1.5
            pb += 1.0
        # Censoring, operational failure, and awaiting evidence carry cost and
        # uncertainty information only.  They are deliberately not successes
        # or failures for the mathematical target.

    clarity_bonus = 0.8 if statement["ambiguity_status"] == "clear" else 0.2
    quantifier_signal = min(1.0, statement.get("quantifier_signal_count", 0) / 3)
    # EGMRA outcome-frequency adjustment (observed, unattested pipeline
    # telemetry from `egmra calibrate`). Deliberately WEAK and CAPPED: these
    # are search-preference signals, never verified outcomes — a verified
    # ledger record moves a posterior by 3.0; the entire EGMRA history of a
    # problem is capped well below that. Applied adjustments are recorded.
    egmra_note: dict | None = None
    if isinstance(egmra_calibration, dict) and egmra_calibration.get("attempts"):
        states = egmra_calibration.get("states") or {}
        attempts = int(egmra_calibration.get("attempts", 0))
        blocked = int(states.get("BLOCKED_BY_INTERPRETATION", 0))
        progress_states = (
            "COMPUTATIONAL_EVIDENCE", "CANDIDATE_SOLUTION",
            "CANDIDATE_DISPROOF", "VERIFIED_CANDIDATE",
            "FORMALLY_VERIFIED_CANDIDATE",
        )
        progressed = sum(int(states.get(s, 0)) for s in progress_states)
        salvaged = int(egmra_calibration.get("salvaged_supported_claims", 0))
        stalled = max(0, attempts - progressed - blocked)
        adjustments: dict[str, float] = {}
        if blocked >= 2:
            delta = min(2.0, 0.5 * blocked)
            failure_a += delta
            rb += min(1.0, 0.25 * blocked)
            adjustments["interpretation_failure_evidence"] = round(delta, 3)
        if stalled >= 3:
            delta = min(1.5, 0.25 * stalled)
            rb += delta
            pb += min(1.0, 0.2 * stalled)
            adjustments["no_progress_evidence"] = round(delta, 3)
        if progressed:
            delta = min(2.0, 1.0 * progressed)
            pa += delta
            adjustments["observed_progress_evidence"] = round(delta, 3)
        if salvaged:
            delta = min(1.0, 0.2 * salvaged)
            pa += delta
            adjustments["salvaged_claims_evidence"] = round(delta, 3)
        egmra_note = {
            "applied": bool(adjustments),
            "attempts_observed": attempts,
            "adjustments": adjustments,
            "note": (
                "observed EGMRA outcome frequencies (unattested pipeline "
                "telemetry); capped weak-evidence adjustment — never a "
                "verified outcome, never a release signal"
            ),
        }
    lean_a = (
        0.5 + 2.5 * formal["lean_route_available"] + clarity_bonus
        + 0.5 * quantifier_signal + 0.3 * (structure["goal"] in {"prove", "classify"})
    )
    lean_b = 12.0 + 2.0 * (statement["ambiguity_status"] == "material") \
        + 1.0 * structure["multi_part"]
    compute_a = (
        0.5 + 2.0 * structure["exact_search_affordance"]
        + 0.8 * structure["finite_signal"]
        + 0.7 * (structure["goal"] in {"construct", "compute", "classify"})
        + 0.3 * (statement["ambiguity_status"] == "clear")
    )
    compute_b = 12.0 + 2.0 * structure["asymptotic"] \
        + 1.0 * (statement["ambiguity_status"] == "material")
    infrastructure_a = (
        0.5 + 1.8 * formal["lean_route_available"] + 0.7 * structure["multi_part"]
        + 0.6 * quantifier_signal + 0.4 * (structure["primary_domain"] != "unclassified")
    )
    infrastructure_b = 12.0 + 1.5 * (statement["ambiguity_status"] == "material") \
        + 0.5 * (structure["goal"] == "compute")
    mathematical_value_a = (
        1.0 + min(1.5, literature["comment_count"] / 30)
        + min(1.0, reference_count / 3) + 0.8 * structure["asymptotic"]
        + 0.5 * structure["multi_part"] + 0.5 * quantifier_signal
    )
    mathematical_value_b = 9.0 + 0.5 * (structure["primary_domain"] == "unclassified")
    return {
        "model_version": MODEL_VERSION,
        "calibration_status": (
            "egmra_outcome_adjusted" if egmra_note and egmra_note["applied"]
            else "uncalibrated_weak_prior_mvp"
        ),
        "egmra_calibration": egmra_note,
        "matching_outcome_records": len(statuses),
        "matching_verified_outcome_records": sum(
            status.startswith("verified_") for status in statuses
        ),
        "outcome_status_counts": dict(sorted(Counter(statuses).items())),
        "p_verified_novel_resolution": beta_summary(ra, rb),
        "p_verified_partial_progress": beta_summary(pa, pb),
        "p_correct_but_already_known": beta_summary(known_a, known_b),
        "p_verified_correctness_novelty_pending": beta_summary(pending_a, pending_b),
        "p_statement_or_interpretation_failure": beta_summary(failure_a, failure_b),
        "p_lean_verified_exact_target": beta_summary(lean_a, lean_b),
        "p_finite_computational_resolution": beta_summary(compute_a, compute_b),
        "p_reusable_formal_infrastructure": beta_summary(
            infrastructure_a, infrastructure_b
        ),
        "p_high_mathematical_value": beta_summary(
            mathematical_value_a, mathematical_value_b
        ),
    }


def cost_estimate(card: dict) -> dict:
    tokens = card["probe_summary"]["statement"]["statement_tokens_approx"]
    references = len(card["metadata"]["references"])
    attempts = card["probe_summary"]["early_research"]["attempts"]
    units = 1.0 + min(4.0, tokens / 250) + min(3.0, references / 8) + min(2.0, attempts / 4)
    return {
        "relative_compute_units": round(units, 3),
        "expected_compute_cost": "unknown_until_instrumented",
        "expected_verification_cost": "high" if units >= 5 else "medium" if units >= 3 else "low",
        "expected_expert_review_cost": "unknown",
    }


def build_card(root: Path, snapshot_id: str, source_commit: str,
               number: int, entry: dict, tex_path: Path,
               *, canonical_source: dict,
               verified_outcomes: list[str] | None = None,
               model_portfolio: str = DEFAULT_MODEL_PORTFOLIO,
               budget: str = DEFAULT_BUDGET,
               budget_config: dict | BudgetConfig | None = None,
               source_snapshot_id: str | None = None,
               source_snapshot_sha256: str | None = None,
               forum_path: Path | None = None) -> dict:
    normalized_budget = normalized_budget_config(**(
        budget_config or DEFAULT_BUDGET_CONFIG
    ))
    if research_budget_id(**normalized_budget) != budget:
        raise ValueError("budget identifier does not match complete budget_config")
    tex_path.read_text(encoding="utf-8")
    original = str(canonical_source["statement"]).strip()
    if not original:
        raise ValueError(f"problem {number} canonical statement is empty")
    normalized = normalize_space(original)
    statement_sha = sha256_bytes(original.strip().encode("utf-8"))
    reference_text = str(canonical_source.get("references", ""))
    refs = sorted(set(
        re.findall(r"\[([A-Za-z]+\d+[A-Za-z]?)\]", reference_text)
        or [line.strip() for line in reference_text.splitlines() if line.strip()]
    ))
    statement_info = statement_probe(original)
    structure = structure_probe(original, list(entry.get("tags") or []))
    card = {
        "schema_version": SCHEMA_VERSION,
        "problem_id": f"erdos-{number}",
        "problem_number": number,
        "snapshot_id": snapshot_id,
        "pipeline_version": source_commit,
        "model_portfolio": model_portfolio,
        "budget": budget,
        "budget_config": normalized_budget,
        "cheap_probe_version": CHEAP_PROBE_VERSION,
        "statement": {
            "original": original,
            "normalized": normalized,
            "intended": original,
            "statement_sha256": statement_sha,
            "ambiguity_status": statement_info["ambiguity_status"],
            "interpretation_branches": [],
            "intended_statement_status": "source_text_pending_theorem_level_audit",
        },
        "metadata": {
            "source_state": entry.get("source_state", "unknown"),
            "source_reports_resolved": bool(entry.get("source_reports_resolved")),
            "source_last_update": entry.get("source_last_update"),
            "source_problem_url": entry.get("source_problem_url"),
            "formalized": entry.get("formalized"),
            "tags": list(entry.get("tags") or []),
            "references": refs,
            "source_sections": {
                "remarks": str(canonical_source.get("remarks", "")),
                "references": reference_text,
            },
        },
        "problem_type": structure,
        "subproblems": extract_subproblems(number, original),
        "probe_summary": {
            "statement": statement_info,
            "structure": structure,
            "literature": forum_probe(
                forum_path or root / "forum_threads" / f"{number}.json"
            ),
            "formal": formal_probe(entry, original),
            "early_research": outcome_probe(verified_outcomes or []),
        },
        "provenance": {
            "latex_path": str(tex_path.relative_to(root)),
            "latex_sha256": sha256_file(tex_path),
            "catalog_fetched_at": None,
            "source_commit": source_commit,
            "source_snapshot_id": (
                canonical_source["provenance"]["snapshot_id"]
                if canonical_source else source_snapshot_id or snapshot_id
            ),
            "source_snapshot_sha256": source_snapshot_sha256,
            "canonical_source": canonical_source["provenance"],
        },
    }
    card["routes"] = route_problem(card)
    research_directive = research_directive_for_card(card)
    card["research_directive"] = research_directive
    card["research_directive_sha256"] = research_directive_sha256(
        research_directive
    )
    bind_card_run_contract(root, card)
    bind_subproblem_run_contracts(root, card)
    card["posterior"] = estimate_posteriors(card, verified_outcomes or [])
    card["cost"] = cost_estimate(card)
    return card


def _problem_number_from_source_path(path: Path) -> int:
    match = re.fullmatch(r"problem_(\d+)", path.stem)
    if match is None:
        raise ValueError(f"invalid problem source filename: {path.name}")
    return int(match.group(1))


def audit_corpus(
    catalog: dict,
    latex_paths: list[Path],
    canonical_numbers: set[int] | None = None,
) -> dict:
    """Compare the rankable local corpus with catalog records marked exactly open."""
    catalog_open = {
        int(number)
        for number, entry in catalog.get("problems", {}).items()
        if str(entry.get("source_state", "")).strip().lower() == "open"
    }
    local_numbers = {
        _problem_number_from_source_path(path)
        for path in latex_paths
    }
    missing = sorted(catalog_open - local_numbers)
    unexpected = sorted(local_numbers - catalog_open)
    canonical_numbers = canonical_numbers if canonical_numbers is not None else catalog_open
    catalog_missing_from_canonical = sorted(catalog_open - canonical_numbers)
    canonical_missing_from_catalog = sorted(canonical_numbers - catalog_open)
    all_equal = (
        not missing
        and not unexpected
        and not catalog_missing_from_canonical
        and not canonical_missing_from_catalog
    )
    return {
        "status": "complete" if all_equal else "degraded",
        "catalog_open_records": len(catalog_open),
        "canonical_open_source_records": len(canonical_numbers),
        "local_open_latex_files": len(local_numbers),
        "rankable_intersection": len(catalog_open & local_numbers & canonical_numbers),
        "missing_open_problem_numbers": missing,
        "unexpected_problem_numbers": unexpected,
        "catalog_records_missing_canonical_source": catalog_missing_from_canonical,
        "canonical_sources_missing_catalog_record": canonical_missing_from_catalog,
    }


def snapshot_sources(
    root: Path,
    output_root: Path,
    snapshot_date: str,
    *,
    canonical_numbers: set[int] | None = None,
) -> tuple[str, dict, dict]:
    catalog_path = root / "problem_catalog.json"
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    latex_paths = sorted((root / "open" / "individual").glob("problem_*.tex"))
    local_open_numbers = {
        _problem_number_from_source_path(path) for path in latex_paths
    }
    forum_paths = sorted(
        path for path in (root / "forum_threads").glob("*.json")
        if (match := re.search(r"\d+", path.stem))
        and int(match.group()) in local_open_numbers
    )
    integrity = audit_corpus(catalog, latex_paths, canonical_numbers)
    repository_head_at_capture = git_commit(root)
    latex_inventory = [(path.name, sha256_file(path)) for path in latex_paths]
    forum_inventory = [(path.name, sha256_file(path)) for path in forum_paths]
    inputs = {
        "catalog_sha256": sha256_file(catalog_path),
        "local_latex_inventory_sha256": sha256_bytes(
            json.dumps(latex_inventory, separators=(",", ":")).encode("utf-8")
        ),
        "local_forum_inventory_sha256": sha256_bytes(
            json.dumps(forum_inventory, separators=(",", ":")).encode("utf-8")
        ),
        "catalog_source_url": catalog.get("source_data_url"),
        "catalog_fetched_at": catalog.get("fetched_at"),
        "snapshot_date": snapshot_date,
    }
    fingerprint = sha256_bytes(json.dumps(inputs, sort_keys=True).encode("utf-8"))[:12]
    snapshot_id = f"{snapshot_date.replace('-', '')}-{fingerprint}"
    snapshot_dir = output_root / "snapshots" / snapshot_id
    raw_dir = snapshot_dir / "raw"
    if not snapshot_dir.exists():
        (raw_dir / "latex").mkdir(parents=True, exist_ok=True)
        (raw_dir / "forum").mkdir(parents=True, exist_ok=True)
        shutil.copy2(catalog_path, raw_dir / "problem_catalog.json")
        for tex_path in latex_paths:
            shutil.copy2(tex_path, raw_dir / "latex" / tex_path.name)
            number = _problem_number_from_source_path(tex_path)
            forum = root / "forum_threads" / f"{number}.json"
            if forum.exists():
                shutil.copy2(forum, raw_dir / "forum" / forum.name)
        manifest = {
            "schema_version": SCHEMA_VERSION,
            "snapshot_id": snapshot_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            **inputs,
            "raw_latex_files": len(list((raw_dir / "latex").glob("*.tex"))),
            "raw_forum_files": len(list((raw_dir / "forum").glob("*.json"))),
            "corpus_integrity": integrity,
            "repository_head_at_capture": repository_head_at_capture,
        }
        write_json(snapshot_dir / "source_manifest.json", manifest)
    else:
        manifest_path = snapshot_dir / "source_manifest.json"
        if not manifest_path.exists():
            raise RuntimeError(f"incomplete immutable source snapshot: {snapshot_dir}")
        try:
            existing_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise RuntimeError(
                f"unreadable immutable source snapshot manifest: {snapshot_dir}"
            ) from error
        if any(existing_manifest.get(key) != value for key, value in inputs.items()):
            raise RuntimeError(f"source snapshot manifest/input mismatch: {snapshot_dir}")
        raw_catalog = raw_dir / "problem_catalog.json"
        raw_latex = sorted((raw_dir / "latex").glob("problem_*.tex"))
        raw_forum = sorted((raw_dir / "forum").glob("*.json"))
        raw_latex_inventory = [(path.name, sha256_file(path)) for path in raw_latex]
        raw_forum_inventory = [(path.name, sha256_file(path)) for path in raw_forum]
        if (
            not raw_catalog.exists()
            or sha256_file(raw_catalog) != inputs["catalog_sha256"]
            or sha256_bytes(
                json.dumps(raw_latex_inventory, separators=(",", ":")).encode("utf-8")
            ) != inputs["local_latex_inventory_sha256"]
            or sha256_bytes(
                json.dumps(raw_forum_inventory, separators=(",", ":")).encode("utf-8")
            ) != inputs["local_forum_inventory_sha256"]
        ):
            raise RuntimeError(f"source snapshot raw bytes failed integrity check: {snapshot_dir}")
    return snapshot_id, catalog, integrity


def diversified_ranking(cards: list[dict], limit: int) -> list[dict]:
    remaining = list(cards)
    selected: list[dict] = []
    domains: Counter[str] = Counter()
    while remaining and len(selected) < limit:
        def acquisition(card: dict) -> float:
            p = card["posterior"]["p_verified_novel_resolution"]["probability"]
            interval = card["posterior"]["p_verified_novel_resolution"]["credible_interval_approx"]
            uncertainty = interval[1] - interval[0]
            domain = card["problem_type"]["primary_domain"]
            diversity = 0.02 / (1 + domains[domain])
            cost = card["cost"]["relative_compute_units"]
            return p / cost + 0.08 * uncertainty + diversity

        winner = max(remaining, key=lambda card: (acquisition(card), -card["problem_number"]))
        remaining.remove(winner)
        domains[winner["problem_type"]["primary_domain"]] += 1
        selected.append(winner)
    return selected


def ranking_record(card: dict, rank: int, *, reason: str,
                   posterior_key: str = "p_verified_novel_resolution") -> dict:
    directive = card.get("research_directive") or research_directive_for_card(card)
    directive_sha256 = card.get("research_directive_sha256") or research_directive_sha256(
        directive
    )
    posterior = card["posterior"][posterior_key]
    interval = posterior["credible_interval_approx"]
    compact_date = card["snapshot_id"].split("-", 1)[0]
    snapshot_date = (
        f"{compact_date[:4]}-{compact_date[4:6]}-{compact_date[6:8]}"
        if len(compact_date) == 8 else compact_date
    )
    risks = []
    if card["statement"]["ambiguity_status"] != "clear":
        risks.append(f"statement ambiguity: {card['statement']['ambiguity_status']}")
    if card["metadata"]["source_reports_resolved"]:
        risks.append("source reports the problem resolved; literature cleanup only")
    if card["probe_summary"]["early_research"]["censored"]:
        risks.append("prior run is incomplete/censored")
    positives = []
    if card["probe_summary"]["formal"]["lean_route_available"]:
        positives.append("source reports an existing formalization")
    if card["problem_type"]["exact_search_affordance"]:
        positives.append("deterministic finite/exact probe appears feasible")
    if not positives:
        positives.append("eligible for bounded natural-language research probe")
    return {
        "problem_id": card["problem_id"],
        "problem_number": card["problem_number"],
        "rank": rank,
        "snapshot_id": card["snapshot_id"],
        "snapshot_date": snapshot_date,
        "pipeline_version": card["pipeline_version"],
        "model_portfolio": card["model_portfolio"],
        "model_version": MODEL_VERSION,
        "budget": card["budget"],
        "budget_config": card["budget_config"],
        "toolset_version": card["toolset_version"],
        "run_contract_id": card["run_contract_id"],
        "allocation_context_id": card.get("allocation_context_id"),
        "source_snapshot_id": card["provenance"]["source_snapshot_id"],
        "source_snapshot_sha256": card["provenance"]["source_snapshot_sha256"],
        "statement_sha256": card["statement"]["statement_sha256"],
        "allocation_status": card["allocation_status"],
        "probability": posterior["probability"],
        "credible_interval": interval,
        "uncertainty": round(interval[1] - interval[0], 6),
        "calibration_status": card["posterior"]["calibration_status"],
        "recommended_attack_mode": card["routes"][0],
        "recommended_attack_modes": list(card["routes"]),
        "research_directive": directive,
        "research_directive_sha256": directive_sha256,
        "strongest_positive_signals": positives,
        "largest_risks": risks,
        "statement_status": card["statement"]["ambiguity_status"],
        "literature_status": "source_resolved" if card["metadata"]["source_reports_resolved"] else "not_audited",
        "lean_status": "available_unreviewed" if card["probe_summary"]["formal"]["lean_route_available"] else "not_available",
        "computational_status": "probe_recommended" if card["problem_type"]["exact_search_affordance"] else "not_identified",
        "estimated_compute": card["cost"],
        "estimated_review_cost": card["cost"]["expected_expert_review_cost"],
        "reason_selected": reason,
    }


def posterior_ranking(cards: list[dict], posterior_key: str, limit: int,
                      reason: str) -> list[dict]:
    ordered = sorted(
        cards,
        key=lambda card: (
            -card["posterior"][posterior_key]["probability"],
            card["problem_number"],
        ),
    )[:limit]
    return [
        ranking_record(card, rank, reason=reason, posterior_key=posterior_key)
        for rank, card in enumerate(ordered, 1)
    ]


def protected_exploration(
    cards: list[dict],
    limit: int,
    *,
    excluded_problem_numbers: set[int] | None = None,
) -> list[dict]:
    """Reserve a deterministic slice for cheap, under-attempted uncertain probes."""
    excluded_problem_numbers = excluded_problem_numbers or set()
    candidates = [
        card for card in cards
        if card["problem_number"] not in excluded_problem_numbers
    ]
    exploration_limit = min(len(candidates), max(1, limit // 5))
    ordered = sorted(
        candidates,
        key=lambda card: (
            card["probe_summary"]["early_research"]["attempts"],
            -(
                card["posterior"]["p_verified_novel_resolution"]
                ["credible_interval_approx"][1]
                - card["posterior"]["p_verified_novel_resolution"]
                ["credible_interval_approx"][0]
            ),
            card["problem_number"],
        ),
    )[:exploration_limit]
    return [
        ranking_record(
            card, rank,
            reason="protected exploration: low attempt count and high uncertainty",
        )
        for rank, card in enumerate(ordered, 1)
    ]


def add_corpus_unlock_posteriors(cards: list[dict]) -> None:
    """Add a corpus-dependent reuse target instead of aliasing formal value."""
    domain_counts = Counter(card["problem_type"]["primary_domain"] for card in cards)
    corpus_size = max(1, len(cards))
    for card in cards:
        infrastructure = card["posterior"]["p_reusable_formal_infrastructure"]
        domain_share = domain_counts[card["problem_type"]["primary_domain"]] / corpus_size
        route_reuse = "shared_infrastructure_search" in card["routes"]
        multi_part = card["problem_type"]["multi_part"]
        alpha = (
            0.5 + 4.0 * infrastructure["probability"] + 2.0 * domain_share
            + 0.8 * route_reuse + 0.5 * multi_part
        )
        beta = 10.0 + 1.5 * (
            card["statement"]["ambiguity_status"] == "material"
        ) + 0.5 * (card["problem_type"]["primary_domain"] == "unclassified")
        card["posterior"]["p_expected_corpus_wide_unlock"] = beta_summary(alpha, beta)


def interleave_allocation(
    exploitation: list[dict], exploration: list[dict], *, exploit_per_explore: int = 4
) -> list[dict]:
    """Create the actual deterministic queue with an explicit protected lane."""
    combined: list[dict] = []
    exploit_index = 0
    explore_index = 0
    while exploit_index < len(exploitation) or explore_index < len(exploration):
        for _ in range(exploit_per_explore):
            if exploit_index >= len(exploitation):
                break
            combined.append({**exploitation[exploit_index], "allocation_lane": "exploitation"})
            exploit_index += 1
        if explore_index < len(exploration):
            combined.append({**exploration[explore_index], "allocation_lane": "protected_exploration"})
            explore_index += 1
        if exploit_index >= len(exploitation) and explore_index < len(exploration):
            combined.extend(
                {**record, "allocation_lane": "protected_exploration"}
                for record in exploration[explore_index:]
            )
            break
    for rank, record in enumerate(combined, 1):
        record["lane_rank"] = record["rank"]
        record["rank"] = rank
        record["allocation_rank"] = rank
    return combined


def subproblem_ranking(cards: list[dict]) -> list[dict]:
    rows: list[dict] = []
    for card in cards:
        parent_probability = card["posterior"]["p_verified_partial_progress"]["probability"]
        for subproblem in card.get("subproblems", []):
            rows.append({
                **subproblem,
                "problem_number": card["problem_number"],
                "snapshot_id": card["snapshot_id"],
                "pipeline_version": card["pipeline_version"],
                "model_portfolio": card["model_portfolio"],
                "budget": card["budget"],
                "parent_run_contract_id": card.get("run_contract_id"),
                "recommended_attack_modes": card["routes"],
                "priority_score": round(
                    parent_probability / max(1, len(card["subproblems"])), 6
                ),
            })
    rows.sort(key=lambda row: (-row["priority_score"], row["subproblem_id"]))
    for rank, row in enumerate(rows, 1):
        row["rank"] = rank
    return rows


def render_ranking(records: list[dict], title: str,
                   metric_label: str = "Selected target probability") -> str:
    lines = [f"# {title}", "", f"Snapshot: `{records[0]['snapshot_id'] if records else 'none'}`", "",
             "> Probabilities are transparent weak-prior MVP estimates and are not yet calibrated.", "",
             f"| Rank | Problem | {metric_label} | Interval | Route | Main risk |",
             "| ---: | ---: | ---: | --- | --- | --- |"]
    for record in records:
        risk = "; ".join(record["largest_risks"]) or "none identified by cheap probe"
        lines.append(
            f"| {record['rank']} | {record['problem_number']} | {record['probability']:.3f} | "
            f"{record['credible_interval']} | {record['recommended_attack_mode']} | {risk} |"
        )
    return "\n".join(lines) + "\n"


_FORBIDDEN_LEDGER_CONTENT = re.compile(
    r"(?:https?://(?:chatgpt\.com|chat\.openai\.com)/(?:c|share)/|"
    r"https?://(?:chat\.deepseek\.com)/(?:a/)?chat/(?:s/)?|"
    r"\bBearer\s+[A-Za-z0-9._-]+|\bsk-[A-Za-z0-9_-]{12,}|"
    r"(?:api[_ -]?key|access[_ -]?token)\s*[:=])",
    re.IGNORECASE,
)


def _json_file_bytes(value: object) -> bytes:
    return (
        json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    ).encode("utf-8")


def _validate_evidence_support_bytes(name: str, value: bytes) -> None:
    if not isinstance(value, bytes) or not value or len(value) > 25_000_000:
        raise ValueError("evidence support must be nonempty bounded bytes")
    if _FORBIDDEN_LEDGER_CONTENT.search(value.decode("utf-8", errors="ignore")):
        raise ValueError(f"evidence support {name} contains private content")


def _store_evidence_support(evidence_root: Path, value: bytes) -> tuple[dict, Path | None]:
    digest = sha256_bytes(value)
    relative = f"support/{digest}.bin"
    path = evidence_root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.is_symlink() or path.read_bytes() != value:
            raise ValueError("content-addressed evidence support conflict")
        created = None
    else:
        temporary = path.with_name(f".{path.name}.{os.getpid()}.{uuid.uuid4().hex}.tmp")
        try:
            with temporary.open("wb") as handle:
                handle.write(value)
                handle.flush()
                os.fsync(handle.fileno())
            temporary.replace(path)
            created = path
        finally:
            temporary.unlink(missing_ok=True)
    return {"path": relative, "sha256": digest, "size_bytes": len(value)}, created


@contextmanager
def evidence_transaction(output_root: Path):
    """Serialize evidence writes and remove only files created by a failed workflow."""
    output_identity = sha256_bytes(str(Path(output_root).resolve()).encode("utf-8"))
    lock_path = Path(tempfile.gettempdir()) / f"erdos-evidence-{output_identity}.lock"
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    created_paths: list[Path] = []
    with lock_path.open("a+", encoding="utf-8") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        try:
            try:
                yield created_paths
            except Exception:
                for path in reversed(created_paths):
                    path.unlink(missing_ok=True)
                raise
        finally:
            fcntl.flock(lock, fcntl.LOCK_UN)


def _load_evidence_support(evidence_root: Path, references: dict) -> dict[str, bytes]:
    if not isinstance(references, dict):
        raise ValueError("evidence support references must be an object")
    loaded: dict[str, bytes] = {}
    reference_fields = {"path", "sha256", "size_bytes"}
    for name, reference in references.items():
        if not isinstance(name, str) or not re.fullmatch(r"[a-z_]{3,32}", name):
            raise ValueError("invalid evidence support name")
        if not isinstance(reference, dict) or set(reference) != reference_fields:
            raise ValueError("evidence support reference schema is not closed")
        digest = str(reference.get("sha256", ""))
        if not re.fullmatch(r"[0-9a-f]{64}", digest) \
                or reference.get("path") != f"support/{digest}.bin":
            raise ValueError("unsafe evidence support path")
        size = reference.get("size_bytes")
        if not isinstance(size, int) or isinstance(size, bool) or not 0 < size <= 25_000_000:
            raise ValueError("invalid evidence support size")
        path = evidence_root / f"support/{digest}.bin"
        if path.is_symlink() or not path.is_file():
            raise ValueError("evidence support is absent")
        value = path.read_bytes()
        if len(value) != size or sha256_bytes(value) != digest:
            raise ValueError("evidence support hash/size mismatch")
        _validate_evidence_support_bytes(name, value)
        loaded[name] = value
    return loaded


def _json_support(support: dict[str, bytes], name: str) -> dict:
    try:
        value = json.loads(support[name])
    except (KeyError, TypeError, json.JSONDecodeError) as error:
        raise ValueError(f"evidence support {name} is not valid JSON") from error
    if not isinstance(value, dict):
        raise ValueError(f"evidence support {name} must be a JSON object")
    return value


def _replay_deterministic_evidence(
    kind: str,
    payload: dict,
    support: dict[str, bytes],
    binding: dict,
) -> None:
    required_support = {
        "gate": {"manifest", "candidate"},
        "intent": {"manifest", "candidate", "source_manifest", "source_record"},
        "disposition": {"manifest", "candidate"},
    }
    if kind not in required_support:
        if support:
            raise ValueError("external audit evidence has no production replay adapter")
        return
    if set(support) != required_support[kind]:
        raise ValueError(f"{kind} evidence support is incomplete")
    manifest_bytes = support["manifest"]
    candidate_bytes = support["candidate"]
    manifest = _json_support(support, "manifest")
    if set(manifest) != SAFE_EVIDENCE_MANIFEST_FIELDS \
            or manifest.get("schema_version") != 1 \
            or manifest.get("projection_type") != "ledger-disposition-input-v1":
        raise ValueError("evidence manifest projection schema is not closed")
    try:
        contract = validate_run_contract(manifest["run_contract"])
        contract_id = run_contract_id(contract)
        execution_id = str(manifest["execution_id"])
        context_id = run_context_id(
            run_contract_id_value=contract_id,
            execution_id=execution_id,
        )
    except (KeyError, TypeError, ValueError, RunContractError) as error:
        raise ValueError("evidence manifest has no valid exact run contract") from error
    expected = {
        "run_contract_id": contract_id,
        "run_context_id": context_id,
        "statement_sha256": contract["statement_sha256"],
        "candidate_sha256": sha256_bytes(candidate_bytes),
    }
    for field, value in expected.items():
        if manifest.get(field) != value or binding.get(field) != value:
            raise ValueError(f"evidence manifest {field} binding mismatch")
    if binding.get("pipeline_version") not in {None, contract["pipeline_fingerprint"]} \
            or binding.get("model_portfolio") not in {None, contract["model_portfolio"]}:
        raise ValueError("evidence manifest pipeline/model binding mismatch")
    if binding.get("snapshot_id") not in {None, contract["source_snapshot"]["id"]} \
            or binding.get("source_snapshot_sha256") not in {
                None, contract["source_snapshot"]["sha256"],
            }:
        raise ValueError("evidence manifest source snapshot binding mismatch")
    if "budget_config" in binding:
        expected_budget, expected_execution = split_run_budget(binding["budget_config"])
        if contract["budget"] != expected_budget \
                or contract["execution_config"] != expected_execution \
                or binding.get("budget") != research_budget_id(**binding["budget_config"]):
            raise ValueError("evidence manifest budget binding mismatch")
    if "toolset_version" in binding:
        identity = {
            "toolset": contract["toolset"],
            "dependencies": contract["dependencies"],
            "runtime": contract["runtime"],
        }
        if binding["toolset_version"] != sha256_bytes(
            canonical_json(identity).encode("utf-8")
        ):
            raise ValueError("evidence manifest toolset binding mismatch")
    problem_number = manifest.get("problem_number")
    if not isinstance(problem_number, int) or isinstance(problem_number, bool) \
            or problem_number < 1:
        raise ValueError("evidence manifest problem number is invalid")
    if binding.get("problem_id") not in {None, f"erdos-{problem_number}"}:
        raise ValueError("evidence manifest problem binding mismatch")
    gate_status = manifest.get("gate_status")
    manifest_candidate_outcome = manifest.get("manifest_candidate_outcome")
    failure_plane = manifest.get("failure_plane")
    if gate_status not in LEDGER_GATE_STATUSES \
            or manifest_candidate_outcome not in LEDGER_CANDIDATE_OUTCOMES \
            or failure_plane not in {None, "statement", "mathematical"}:
        raise ValueError("evidence classifier inputs are not bounded")
    replayed_disposition = classify_disposition_inputs(
        problem_number=problem_number,
        gate_status=gate_status,
        manifest_candidate_outcome=manifest_candidate_outcome,
        failure_plane=failure_plane,
        candidate_text=candidate_bytes.decode("utf-8", errors="ignore"),
    )
    if kind in {"gate", "disposition"}:
        if sha256_bytes(manifest_bytes) != payload["manifest_sha256"]:
            raise ValueError(f"{kind} evidence manifest hash mismatch")
    if kind == "disposition":
        disposition = {
            "status": replayed_disposition["outcome_class"],
            "gate_status": replayed_disposition["gate_status"],
            "candidate_outcome": replayed_disposition["candidate_outcome"],
        }
        if any(disposition[field] != payload[field] for field in disposition) \
                or binding.get("status") not in {None, disposition["status"]} \
                or sha256_bytes(canonical_json(disposition).encode("utf-8")) \
                != payload["disposition_object_sha256"]:
            raise ValueError("disposition evidence replay failed")
        return
    if kind == "gate":
        gate = {"status": gate_status}
        if gate_status != payload["gate_status"] \
                or sha256_bytes(canonical_json(gate).encode("utf-8")) \
                != payload["gate_object_sha256"]:
            raise ValueError("gate evidence object replay failed")
        return
    source_manifest_bytes = support["source_manifest"]
    source_record_bytes = support["source_record"]
    source_manifest = _json_support(support, "source_manifest")
    source_record = _json_support(support, "source_record")
    source_snapshot = contract["source_snapshot"]
    if (
        sha256_bytes(source_manifest_bytes) != source_snapshot["sha256"]
        or payload["source_snapshot_sha256"] != source_snapshot["sha256"]
        or payload["source_snapshot_id"] != source_snapshot["id"]
        or source_manifest.get("snapshot_id") != source_snapshot["id"]
        or source_manifest.get("canonical") is not True
        or source_manifest.get("corpus_complete") is not True
    ):
        raise ValueError("intent evidence canonical snapshot replay failed")
    records = source_manifest.get("records")
    if not isinstance(records, list):
        raise ValueError("intent evidence source manifest has no records")
    matches = [
        item for item in records
        if isinstance(item, dict) and item.get("problem_number") == problem_number
    ]
    if len(matches) != 1:
        raise ValueError("intent evidence has no unique source record")
    source_entry = matches[0]
    if sha256_bytes(source_record_bytes) != source_entry.get("source_record_sha256") \
            or source_record.get("problem_number") != problem_number:
        raise ValueError("intent evidence source record hash/binding mismatch")
    statement_section = source_record.get("sections", {}).get("statement", {})
    statement = statement_section.get("text")
    if not isinstance(statement, str) or (
        sha256_bytes(statement.strip().encode("utf-8")) != binding["statement_sha256"]
        or statement_section.get("sha256") != binding["statement_sha256"]
        or source_entry.get("statement_sha256") != binding["statement_sha256"]
        or payload["statement_sha256"] != binding["statement_sha256"]
        or payload["run_contract_id"] != binding["run_contract_id"]
    ):
        raise ValueError("intent evidence canonical statement replay failed")


def _validate_evidence_payload(
    kind: str,
    issuer: str,
    payload: dict,
    *,
    run_contract_id_value: str,
    statement_sha256: str,
    record: dict | None = None,
) -> None:
    """Apply the closed issuer and kind-specific evidence admission policy."""
    if issuer not in EVIDENCE_ISSUER_POLICY.get(kind, set()):
        raise ValueError(f"issuer is not authorized for {kind} evidence")
    if not isinstance(payload, dict):
        raise ValueError("certificate evidence payload must be an object")

    def digest(field: str) -> None:
        if not re.fullmatch(r"[0-9a-f]{64}", str(payload.get(field, ""))):
            raise ValueError(f"evidence payload {field} must be a SHA-256 digest")

    def bounded_identity(field: str) -> None:
        value = payload.get(field)
        if not isinstance(value, str) or not re.fullmatch(
            r"[A-Za-z0-9][A-Za-z0-9._:@/+\-]{2,127}", value
        ):
            raise ValueError(f"evidence payload {field} must be a bounded identity")

    if kind == "gate":
        if set(payload) != {"manifest_sha256", "gate_status", "gate_object_sha256"}:
            raise ValueError("gate evidence payload schema is not closed")
        digest("manifest_sha256")
        digest("gate_object_sha256")
        if payload["gate_status"] not in {"verified_proved", "verified_disproved"}:
            raise ValueError("gate evidence does not record a verified decision")
    elif kind == "intent":
        required = {
            "source_snapshot_id", "source_snapshot_sha256",
            "statement_sha256", "run_contract_id",
        }
        if set(payload) != required:
            raise ValueError("intent evidence payload schema is not closed")
        digest("source_snapshot_sha256")
        if payload["statement_sha256"] != statement_sha256 \
                or payload["run_contract_id"] != run_contract_id_value:
            raise ValueError("intent evidence run/statement binding mismatch")
        bounded_identity("source_snapshot_id")
        if record is not None and (
            payload["source_snapshot_id"] != record.get("snapshot_id")
            or payload["source_snapshot_sha256"]
            != record.get("source_snapshot_sha256")
        ):
            raise ValueError("intent evidence source snapshot binding mismatch")
    elif kind == "disposition":
        required = {
            "manifest_sha256", "status", "gate_status", "candidate_outcome",
            "disposition_object_sha256",
        }
        if set(payload) != required:
            raise ValueError("disposition evidence payload schema is not closed")
        digest("manifest_sha256")
        digest("disposition_object_sha256")
        if payload["status"] not in REPLAYABLE_DISPOSITION_STATUSES \
                or payload["gate_status"] not in LEDGER_GATE_STATUSES \
                or payload["candidate_outcome"] not in LEDGER_CANDIDATE_OUTCOMES:
            raise ValueError("disposition evidence status is invalid")
        if record is not None and any(
            payload[field] != record.get(field)
            for field in ("status", "gate_status", "candidate_outcome")
        ):
            raise ValueError("disposition evidence contradicts ledger record")
    elif kind == "partial_progress":
        required = {
            "decision", "verification_method", "verifier_identity",
            "evidence_report_sha256", "verified_claim_sha256", "adapter_version",
        }
        if set(payload) != required:
            raise ValueError("partial-progress evidence payload schema is not closed")
        digest("evidence_report_sha256")
        digest("verified_claim_sha256")
        if payload["decision"] != "verified_partial_progress" \
                or payload["verification_method"] not in {
                    "qualified_human_review", "lean_clean_replay",
                    "independent_exact_computation",
                }:
            raise ValueError("partial-progress evidence decision/method is invalid")
        bounded_identity("verifier_identity")
        if not re.fullmatch(r"[a-z0-9][a-z0-9._-]{2,63}", str(payload["adapter_version"])):
            raise ValueError("partial-progress adapter version is invalid")
    elif kind == "novelty":
        required = {
            "decision", "reviewer_identity", "review_scope",
            "evidence_report_sha256", "source_inventory_sha256", "source_count",
            "adapter_version",
        }
        if set(payload) != required:
            raise ValueError("novelty evidence payload schema is not closed")
        digest("evidence_report_sha256")
        digest("source_inventory_sha256")
        if payload["decision"] not in {
            "novel", "independent_rediscovery", "literature_identification",
        } or payload["review_scope"] != "theorem-level-current-literature":
            raise ValueError("novelty evidence decision/scope is invalid")
        bounded_identity("reviewer_identity")
        if not isinstance(payload["source_count"], int) \
                or isinstance(payload["source_count"], bool) \
                or payload["source_count"] < 1:
            raise ValueError("novelty evidence reviewer/source inventory is invalid")
        if not re.fullmatch(r"[a-z0-9][a-z0-9._-]{2,63}", str(payload["adapter_version"])):
            raise ValueError("novelty adapter version is invalid")
        if record is not None:
            expected_decision = {
                "verified_novel_resolution": "novel",
                "independent_rediscovery": "independent_rediscovery",
                "literature_identification": "literature_identification",
            }.get(str(record.get("status")))
            if expected_decision is not None and payload["decision"] != expected_decision:
                raise ValueError("novelty evidence decision contradicts outcome status")


def register_evidence_certificate(
    output_root: Path,
    *,
    kind: str,
    run_contract_id_value: str,
    run_context_id_value: str,
    statement_sha256: str,
    candidate_sha256: str,
    evidence_payload: dict,
    issuer: str,
    supporting_artifacts: dict[str, bytes] | None = None,
    _transaction_created_paths: list[Path] | None = None,
) -> str:
    """Persist a deterministic evidence artifact and a bound certificate.

    The returned ID is the SHA-256 of the closed certificate body.  A ledger
    label cannot learn from it unless both the certificate and its evidence
    artifact remain present, untampered, and bound to the exact run/candidate.
    """
    if _transaction_created_paths is None:
        with evidence_transaction(output_root) as created_paths:
            return register_evidence_certificate(
                output_root,
                kind=kind,
                run_contract_id_value=run_contract_id_value,
                run_context_id_value=run_context_id_value,
                statement_sha256=statement_sha256,
                candidate_sha256=candidate_sha256,
                evidence_payload=evidence_payload,
                issuer=issuer,
                supporting_artifacts=supporting_artifacts,
                _transaction_created_paths=created_paths,
            )
    if kind not in EVIDENCE_CERTIFICATE_KINDS:
        raise ValueError(f"unsupported evidence certificate kind: {kind}")
    for label, value in (
        ("run_contract_id", run_contract_id_value),
        ("run_context_id", run_context_id_value),
        ("statement_sha256", statement_sha256),
        ("candidate_sha256", candidate_sha256),
    ):
        if not re.fullmatch(r"[0-9a-f]{64}", str(value)):
            raise ValueError(f"invalid certificate {label}")
    issuer = str(issuer).strip()
    if not issuer or issuer.lower() in {"unknown", "unrecorded", "none"}:
        raise ValueError("certificate issuer must be exact")
    if not isinstance(evidence_payload, dict):
        raise ValueError("certificate evidence payload must be an object")
    _validate_evidence_payload(
        kind,
        issuer,
        evidence_payload,
        run_contract_id_value=run_contract_id_value,
        statement_sha256=statement_sha256,
    )
    evidence_root = Path(output_root) / "labels" / "evidence"
    raw_support = supporting_artifacts or {}
    if not isinstance(raw_support, dict):
        raise ValueError("supporting_artifacts must be an object")
    for support_name, support_bytes in raw_support.items():
        if not isinstance(support_name, str) or not re.fullmatch(
            r"[a-z_]{3,32}", support_name
        ):
            raise ValueError("invalid evidence support name")
        _validate_evidence_support_bytes(support_name, support_bytes)
    _replay_deterministic_evidence(
        kind,
        evidence_payload,
        raw_support,
        {
            "run_contract_id": run_contract_id_value,
            "run_context_id": run_context_id_value,
            "statement_sha256": statement_sha256,
            "candidate_sha256": candidate_sha256,
        },
    )
    if _FORBIDDEN_LEDGER_CONTENT.search(json.dumps({
        "kind": kind, "issuer": issuer, "evidence": evidence_payload,
    }, ensure_ascii=False)):
        raise ValueError("evidence artifact contains forbidden private content")
    created_support: list[Path] = []
    created_artifact: Path | None = None
    created_certificate: Path | None = None
    try:
        support_references = {}
        for support_name, support_bytes in raw_support.items():
            reference, created = _store_evidence_support(
                evidence_root, support_bytes
            )
            support_references[support_name] = reference
            if created is not None:
                created_support.append(created)
        artifact = {
            "schema_version": 2,
            "kind": kind,
            "issuer": issuer,
            "evidence": evidence_payload,
            "supporting_artifacts": support_references,
        }
        artifact_bytes = _json_file_bytes(artifact)
        artifact_sha256 = sha256_bytes(artifact_bytes)
        artifact_path = evidence_root / "artifacts" / f"{artifact_sha256}.json"
        if artifact_path.exists():
            if artifact_path.is_symlink() or artifact_path.read_bytes() != artifact_bytes:
                raise ValueError("content-addressed evidence artifact conflict")
        else:
            write_json(artifact_path, artifact)
            created_artifact = artifact_path
        certificate = {
            "schema_version": 1,
            "kind": kind,
            "artifact_path": f"artifacts/{artifact_sha256}.json",
            "artifact_sha256": artifact_sha256,
            "run_contract_id": run_contract_id_value,
            "run_context_id": run_context_id_value,
            "statement_sha256": statement_sha256,
            "candidate_sha256": candidate_sha256,
            "issuer": issuer,
            "passed": True,
        }
        certificate_id = sha256_bytes(canonical_json(certificate).encode("utf-8"))
        certificate_path = evidence_root / "certificates" / f"{certificate_id}.json"
        if certificate_path.exists():
            if certificate_path.is_symlink() or json.loads(
                certificate_path.read_text(encoding="utf-8")
            ) != certificate:
                raise ValueError("content-addressed evidence certificate conflict")
        else:
            write_json(certificate_path, certificate)
            created_certificate = certificate_path
        _transaction_created_paths.extend([
            *created_support,
            *([created_artifact] if created_artifact is not None else []),
            *([created_certificate] if created_certificate is not None else []),
        ])
        return certificate_id
    except Exception:
        if created_certificate is not None:
            created_certificate.unlink(missing_ok=True)
        if created_artifact is not None:
            created_artifact.unlink(missing_ok=True)
        for path in created_support:
            path.unlink(missing_ok=True)
        raise


def _required_evidence_kinds(status: str, learning_eligible: bool) -> set[str]:
    if status == "verified_novel_resolution":
        return {"gate", "intent", "novelty"}
    if status == "verified_partial_progress":
        return {"gate", "intent", "partial_progress"}
    if status == "verified_novelty_pending":
        return {"gate", "intent"}
    if status in {"independent_rediscovery", "literature_identification"}:
        return {"gate", "intent", "novelty"}
    if status in AUTONOMOUS_LEARNING_STATUSES and learning_eligible:
        return {"disposition"}
    return set()


def validate_evidence_certificates(output_root: Path, record: dict) -> set[str]:
    """Resolve every ledger certificate and enforce exact cryptographic bindings."""
    certificate_ids = record.get("evidence_certificate_ids", [])
    if not isinstance(certificate_ids, list):
        raise ValueError("invalid evidence_certificate_ids")
    if len(certificate_ids) != len(set(certificate_ids)):
        raise ValueError("duplicate evidence certificate IDs")
    required = _required_evidence_kinds(
        str(record.get("status", "")), record.get("learning_eligible") is True
    )
    if (required or certificate_ids) and not re.fullmatch(
        r"[0-9a-f]{64}", str(record.get("candidate_sha256", ""))
    ):
        raise ValueError("evidenced outcomes require candidate_sha256")
    evidence_root = Path(output_root) / "labels" / "evidence"
    certificate_fields = {
        "schema_version", "kind", "artifact_path", "artifact_sha256",
        "run_contract_id", "run_context_id", "statement_sha256",
        "candidate_sha256", "issuer", "passed",
    }
    artifact_fields = {
        "schema_version", "kind", "issuer", "evidence", "supporting_artifacts",
    }
    observed: set[str] = set()
    for certificate_id in certificate_ids:
        if not isinstance(certificate_id, str) or not re.fullmatch(
            r"[0-9a-f]{64}", certificate_id
        ):
            raise ValueError("evidence certificate ID must be a SHA-256 digest")
        path = evidence_root / "certificates" / f"{certificate_id}.json"
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"evidence certificate is absent: {certificate_id}")
        try:
            certificate = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise ValueError("evidence certificate is unreadable") from error
        if not isinstance(certificate, dict) or set(certificate) != certificate_fields:
            raise ValueError("evidence certificate schema is not closed")
        if sha256_bytes(canonical_json(certificate).encode("utf-8")) != certificate_id:
            raise ValueError("evidence certificate content hash mismatch")
        kind = certificate.get("kind")
        if kind not in EVIDENCE_CERTIFICATE_KINDS or certificate.get("passed") is not True:
            raise ValueError("evidence certificate is not a passing supported check")
        for field in (
            "run_contract_id", "run_context_id", "statement_sha256",
            "candidate_sha256",
        ):
            if certificate.get(field) != record.get(field):
                raise ValueError(f"evidence certificate {field} binding mismatch")
        artifact_sha256 = str(certificate.get("artifact_sha256", ""))
        if certificate.get("artifact_path") != f"artifacts/{artifact_sha256}.json" \
                or not re.fullmatch(r"[0-9a-f]{64}", artifact_sha256):
            raise ValueError("unsafe evidence artifact path")
        artifact_path = evidence_root / "artifacts" / f"{artifact_sha256}.json"
        if artifact_path.is_symlink() or not artifact_path.is_file() \
                or sha256_file(artifact_path) != artifact_sha256:
            raise ValueError("evidence artifact is absent or its hash mismatches")
        try:
            artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise ValueError("evidence artifact is unreadable") from error
        if not isinstance(artifact, dict) or set(artifact) != artifact_fields:
            raise ValueError("evidence artifact schema is not closed")
        if artifact.get("schema_version") != 2:
            raise ValueError("evidence artifact schema is unsupported")
        if artifact.get("kind") != kind or artifact.get("issuer") != certificate.get("issuer"):
            raise ValueError("evidence artifact identity mismatch")
        if _FORBIDDEN_LEDGER_CONTENT.search(json.dumps(artifact, ensure_ascii=False)):
            raise ValueError("evidence artifact contains forbidden private content")
        _validate_evidence_payload(
            kind,
            str(certificate["issuer"]),
            artifact["evidence"],
            run_contract_id_value=str(record["run_contract_id"]),
            statement_sha256=str(record["statement_sha256"]),
            record=record,
        )
        support = _load_evidence_support(
            evidence_root, artifact["supporting_artifacts"]
        )
        _replay_deterministic_evidence(
            kind,
            artifact["evidence"],
            support,
            record,
        )
        observed.add(kind)
    if not required <= observed:
        raise ValueError(
            f"outcome evidence is incomplete; missing {sorted(required - observed)}"
        )
    return observed


def _registered_adapter_learning_eligible(output_root: Path, record: dict) -> bool:
    """Replay a production-registered external adapter, or fail closed.

    The registry is empty in this release and the feature flag defaults off.
    This path exists so a future adapter cannot be enabled by an issuer string
    or manual ledger field alone: a code-registered kind/issuer/version tuple
    and an affirmative deterministic replay are both mandatory.
    """
    if record.get("status") not in EXTERNAL_JUDGMENT_STATUSES \
            or not feature_enabled("automated_external_evidence"):
        return False
    evidence_root = Path(output_root) / "labels" / "evidence"
    expected_kind = (
        "partial_progress"
        if record.get("status") == "verified_partial_progress" else "novelty"
    )
    for certificate_id in record.get("evidence_certificate_ids", []):
        certificate_path = evidence_root / "certificates" / f"{certificate_id}.json"
        try:
            certificate = json.loads(certificate_path.read_text(encoding="utf-8"))
            artifact = json.loads(
                (evidence_root / certificate["artifact_path"]).read_text(encoding="utf-8")
            )
            payload = artifact["evidence"]
            key = (
                str(certificate["kind"]), str(certificate["issuer"]),
                str(payload["adapter_version"]),
            )
        except (OSError, KeyError, TypeError, json.JSONDecodeError):
            return False
        if key[0] != expected_kind:
            continue
        adapter = EVIDENCE_ADAPTER_REGISTRY.get(key)
        if not callable(adapter):
            return False
        try:
            replayed = adapter(Path(output_root), record, artifact)
        except Exception:
            return False
        return replayed is True
    return False


def _expected_learning_eligible(
    output_root: Path, record: dict, observed_evidence: set[str]
) -> bool:
    if record.get("status") in AUTONOMOUS_LEARNING_STATUSES:
        return "disposition" in observed_evidence
    return _registered_adapter_learning_eligible(output_root, record)


def _event_identity(record: dict) -> str:
    payload = {
        key: value for key, value in record.items()
        if key not in {"event_id", "schema_version", "recorded_at"}
    }
    return sha256_bytes(canonical_json(payload).encode("utf-8"))


def _event_business_record(record: dict) -> dict:
    return {
        key: value for key, value in record.items()
        if key not in {
            "event_id", "event_sequence", "supersedes_event_id",
            "schema_version", "recorded_at",
        }
    }


def _validate_event_identity(record: dict) -> None:
    event_id = str(record.get("event_id", ""))
    sequence = record.get("event_sequence")
    if not re.fullmatch(r"[0-9a-f]{64}", event_id):
        raise ValueError("ledger event_id must be a SHA-256 digest")
    if not isinstance(sequence, int) or isinstance(sequence, bool) or sequence < 1:
        raise ValueError("ledger event_sequence must be a positive integer")
    supersedes = record.get("supersedes_event_id")
    if sequence == 1 and supersedes is not None:
        raise ValueError("first ledger event cannot supersede another event")
    if sequence > 1 and not re.fullmatch(r"[0-9a-f]{64}", str(supersedes or "")):
        raise ValueError("ledger revision must bind the superseded event")
    if _event_identity(record) != event_id:
        raise ValueError("ledger event content hash mismatch")


def _validate_event_transition(previous: dict, current: dict) -> None:
    immutable_fields = (
        "problem_id", "execution_id", "run_contract_id", "run_context_id",
        "snapshot_id", "source_snapshot_sha256", "statement_sha256",
        "pipeline_version", "model_portfolio", "toolset_version", "budget",
        "budget_config", "candidate_sha256",
    )
    if any(current.get(field) != previous.get(field) for field in immutable_fields):
        raise ValueError("ledger revision changes immutable run or candidate identity")
    allowed = LEDGER_TRANSITIONS.get(str(previous.get("status")), set())
    if current.get("status") not in allowed:
        raise ValueError(
            f"unsupported ledger status transition: {previous.get('status')} -> "
            f"{current.get('status')}"
        )


def _stored_ledger_business_record(record: object) -> dict:
    if not isinstance(record, dict):
        raise ValueError("stored ledger event must be an object")
    if not {"schema_version", "recorded_at"} <= set(record) \
            or record.get("schema_version") != LEDGER_SCHEMA_VERSION:
        raise ValueError("stored ledger schema version is unsupported")
    recorded_at = record.get("recorded_at")
    if not isinstance(recorded_at, str) or len(recorded_at) > 64:
        raise ValueError("stored ledger timestamp is invalid")
    try:
        parsed = datetime.fromisoformat(recorded_at.replace("Z", "+00:00"))
    except ValueError as error:
        raise ValueError("stored ledger timestamp is invalid") from error
    if parsed.tzinfo is None:
        raise ValueError("stored ledger timestamp must be timezone-aware")
    business = {
        key: value for key, value in record.items()
        if key not in {"schema_version", "recorded_at"}
    }
    _validate_ledger_record(business)
    return business


def load_outcome_records(output_root: Path) -> dict[str, list[dict]]:
    """Load the latest valid event per execution, including live evidence checks."""
    outcomes: dict[str, list[dict]] = {}
    ledger = output_root / "labels" / "outcomes.jsonl"
    if not ledger.exists():
        return outcomes
    latest: dict[str, dict] = {}
    for line in ledger.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        try:
            record = json.loads(stripped)
        except json.JSONDecodeError:
            continue
        try:
            candidate = _stored_ledger_business_record(record)
            _validate_event_identity(candidate)
            observed = validate_evidence_certificates(output_root, candidate)
            if candidate["learning_eligible"] is not _expected_learning_eligible(
                output_root, candidate, observed
            ):
                raise ValueError("ledger learning eligibility failed adapter replay")
            previous = latest.get(candidate["execution_id"])
            if previous is None:
                if candidate["event_sequence"] != 1:
                    raise ValueError("ledger event chain does not begin at one")
            else:
                if candidate["event_sequence"] != previous["event_sequence"] + 1 \
                        or candidate.get("supersedes_event_id") != previous["event_id"]:
                    raise ValueError("ledger event chain is discontinuous")
                _validate_event_transition(previous, candidate)
        except ValueError:
            continue
        latest[candidate["execution_id"]] = candidate
    for candidate in latest.values():
        outcomes.setdefault(candidate["problem_id"], []).append(candidate)
    return outcomes


def matching_outcome_records(card: dict, records: list[dict]) -> list[dict]:
    """Bind learning to the exact reusable run contract and its explicit fields."""
    if card.get("model_portfolio") == DEFAULT_MODEL_PORTFOLIO:
        return []
    exact_fields = (
        "run_contract_id", "snapshot_id", "source_snapshot_sha256",
        "statement_sha256", "pipeline_version", "model_portfolio",
        "toolset_version", "budget", "budget_config",
    )
    expected = {
        "run_contract_id": card.get("run_contract_id"),
        "snapshot_id": card.get("provenance", {}).get("source_snapshot_id"),
        "source_snapshot_sha256": card.get("provenance", {}).get(
            "source_snapshot_sha256"
        ),
        "statement_sha256": card.get("statement", {}).get("statement_sha256"),
        "pipeline_version": card.get("pipeline_version"),
        "model_portfolio": card.get("model_portfolio"),
        "toolset_version": card.get("toolset_version"),
        "budget": card.get("budget"),
        "budget_config": card.get("budget_config"),
    }
    if any(expected[field] in {None, ""} for field in exact_fields if field != "budget_config"):
        return []
    if not isinstance(expected["budget_config"], dict):
        return []
    return [
        record for record in records
        if record.get("learning_eligible") is True
        and all(record.get(field) == expected[field] for field in exact_fields)
    ]


def tractable_frontier_ranking(cards: list[dict], limit: int) -> list[dict]:
    """Problems most amenable to formal verification or exact computation.

    This is the frontier where an autoformalize-and-prove system (e.g. Aristotle)
    has the best realistic odds: an existing/likely Lean route, a finite exact
    target, and a clear statement. It is not a claim of novel resolution.
    """
    def score(card: dict) -> float:
        posterior = card["posterior"]
        lean = posterior["p_lean_verified_exact_target"]["probability"]
        compute = posterior["p_finite_computational_resolution"]["probability"]
        lean_route = card["probe_summary"]["formal"]["lean_route_available"]
        clear = card["statement"]["ambiguity_status"] == "clear"
        return 0.5 * lean + 0.4 * compute + 0.15 * bool(lean_route) + 0.05 * bool(clear)

    ordered = sorted(
        cards, key=lambda card: (-score(card), card["problem_number"])
    )[:limit]
    return [
        ranking_record(
            card, rank,
            reason="formal/exact-computation tractable frontier",
            posterior_key="p_lean_verified_exact_target",
        )
        for rank, card in enumerate(ordered, 1)
    ]


ATTEMPT_EXCLUSIONS_FILENAME = "attempt_exclusions.json"


def load_attempt_exclusions(root: Path) -> set[int]:
    """Problem numbers to keep out of every attack lane.

    These are problems that carry a known solution (e.g. an erdosproblems.com
    forum thread) even though the canonical ``source_state`` is still ``open``,
    so re-ingestion keeps them in the corpus. The exclusion is applied to the
    ranking/allocation only: cards and corpus audit stay complete, but the
    solver never spends a run on them.
    """
    path = Path(root) / ATTEMPT_EXCLUSIONS_FILENAME
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return set()
    excluded: set[int] = set()
    for item in data.get("excluded", []) if isinstance(data, dict) else []:
        number = item.get("problem") if isinstance(item, dict) else item
        if isinstance(number, bool):
            continue
        if isinstance(number, int):
            excluded.add(number)
        elif isinstance(number, str) and number.strip().isdigit():
            excluded.add(int(number))
    return excluded


def load_egmra_calibration(path: Path | None) -> tuple[dict[str, dict], dict]:
    """Load an `egmra calibrate` report as per-problem observed frequencies.

    Returns ``(by_problem, provenance)``.  The report is honest COUNTS from
    the EGMRA outcome ledger — unattested pipeline telemetry, distinct from
    the contract-bound verified ledger — so consumers apply it only as capped
    weak evidence.  Fail-closed: a missing path yields empty; a malformed or
    symlinked report raises.
    """
    if path is None:
        return {}, {"enabled": False}
    report_path = Path(path)
    if report_path.is_symlink() or not report_path.is_file():
        raise RuntimeError(f"egmra calibration report is not a regular file: {report_path}")
    payload = report_path.read_text(encoding="utf-8")
    report = json.loads(payload)
    if not isinstance(report, dict) or not isinstance(report.get("by_problem"), dict):
        raise RuntimeError("egmra calibration report is malformed (no by_problem)")
    by_problem: dict[str, dict] = {}
    for problem_id, entry in report["by_problem"].items():
        if not isinstance(entry, dict):
            continue
        by_problem[str(problem_id)] = {
            "attempts": int(entry.get("attempts", 0)),
            "states": dict(entry.get("states", {})),
            "salvaged_supported_claims": int(
                entry.get("salvaged_supported_claims", 0)),
        }
    provenance = {
        "enabled": True,
        "report_sha256": hashlib.sha256(payload.encode("utf-8")).hexdigest(),
        "generated_at": report.get("generated_at"),
        "total_runs": report.get("total_runs"),
        "note": (
            "observed EGMRA outcome frequencies; capped weak-evidence "
            "posterior adjustment only"
        ),
    }
    return by_problem, provenance


def build_searcher(root: Path, output_root: Path, *, snapshot_date: str,
                   top_k: int,
                   model_portfolio: str = DEFAULT_MODEL_PORTFOLIO,
                   budget: str = DEFAULT_BUDGET,
                   budget_config: dict | BudgetConfig | None = None,
                   canonical_snapshot: Path | None = None,
                   egmra_calibration_path: Path | None = None) -> dict:
    if canonical_snapshot is None:
        source_roots = [output_root]
        default_source_root = root / "triage"
        if default_source_root.resolve() != output_root.resolve():
            source_roots.append(default_source_root)
        source_errors: list[str] = []
        for source_root in source_roots:
            try:
                canonical_snapshot = find_latest_canonical_snapshot(source_root)
                break
            except RuntimeError as error:
                source_errors.append(str(error))
        else:
            raise RuntimeError(
                "ranking withheld: no complete canonical first-party source snapshot; "
                + "; ".join(source_errors)
            )
    canonical_snapshot = Path(canonical_snapshot)
    canonical_sources = load_canonical_corpus(canonical_snapshot)
    snapshot_id, catalog, integrity = snapshot_sources(
        root,
        output_root,
        snapshot_date,
        canonical_numbers=set(canonical_sources),
    )
    normalized_budget = normalized_budget_config(**(
        budget_config or DEFAULT_BUDGET_CONFIG
    ))
    if research_budget_id(**normalized_budget) != budget:
        raise ValueError("budget identifier does not match complete budget_config")
    source_snapshot_manifest = canonical_snapshot / "manifest.json"
    source_snapshot_sha256 = sha256_file(source_snapshot_manifest)
    entries = catalog.get("problems", {})
    attempt_exclusions = load_attempt_exclusions(root)
    cards: list[dict] = []
    cards_dir = output_root / "normalized" / "problem_cards"
    cards_dir.mkdir(parents=True, exist_ok=True)
    source_commit = pipeline_fingerprint(root)
    allocation_context, allocation_context_id = make_allocation_context(
        root=root,
        snapshot_id=snapshot_id,
        source_snapshot_id=canonical_snapshot.name,
        source_snapshot_sha256=source_snapshot_sha256,
        canonical_open_source_records=len(canonical_sources),
        pipeline_version=source_commit,
        model_portfolio=model_portfolio,
        budget=budget,
        budget_config=normalized_budget,
        allocation_top_k=top_k,
    )
    outcome_records = load_outcome_records(output_root)
    egmra_by_problem, egmra_provenance = load_egmra_calibration(egmra_calibration_path)
    rankable_numbers = {
        int(number)
        for number, entry in entries.items()
        if str(entry.get("source_state", "")).strip().lower() == "open"
    }
    for tex_path in sorted(
        (
            path for path in (root / "open" / "individual").glob("problem_*.tex")
            if _problem_number_from_source_path(path) in rankable_numbers
        ),
        key=_problem_number_from_source_path,
    ):
        number = _problem_number_from_source_path(tex_path)
        entry = entries.get(str(number), {
            "problem": number,
            "source_state": "unknown",
            "source_reports_resolved": False,
            "tags": [],
        })
        try:
            canonical_source = canonical_sources[number]
        except KeyError as error:
            raise RuntimeError(
                f"canonical source snapshot is missing open problem {number}"
            ) from error
        card = build_card(
            root, snapshot_id, source_commit, number, entry, tex_path,
            canonical_source=canonical_source,
            verified_outcomes=[],
            model_portfolio=model_portfolio,
            budget=budget,
            budget_config=normalized_budget,
            source_snapshot_id=snapshot_id,
            source_snapshot_sha256=source_snapshot_sha256,
            forum_path=(
                output_root / "snapshots" / snapshot_id / "raw" / "forum"
                / f"{number}.json"
            ),
        )
        matching_records = matching_outcome_records(
            card, outcome_records.get(f"erdos-{number}", [])
        )
        card["probe_summary"]["early_research"] = outcome_probe(matching_records)
        card["posterior"] = estimate_posteriors(
            card, matching_records,
            egmra_calibration=egmra_by_problem.get(f"erdos-{number}"),
        )
        card["cost"] = cost_estimate(card)
        card["allocation_context_id"] = allocation_context_id
        card["provenance"]["catalog_fetched_at"] = catalog.get("fetched_at")
        cards.append(card)

    add_corpus_unlock_posteriors(cards)
    for card in cards:
        write_json(cards_dir / f"{card['problem_number']}.json", card)

    current_card_names = {f"{card['problem_number']}.json" for card in cards}
    for stale_card in cards_dir.glob("*.json"):
        if stale_card.name not in current_card_names:
            stale_card.unlink()

    subproblems = subproblem_ranking(cards)
    subproblem_dir = output_root / "normalized" / "subproblem_cards"
    subproblem_dir.mkdir(parents=True, exist_ok=True)
    current_subproblem_names: set[str] = set()
    for subproblem in subproblems:
        name = f"{subproblem['subproblem_id']}.json"
        current_subproblem_names.add(name)
        write_json(subproblem_dir / name, subproblem)
    for stale_subproblem in subproblem_dir.glob("*.json"):
        if stale_subproblem.name not in current_subproblem_names:
            stale_subproblem.unlink()

    eligible = [
        card for card in cards
        if not card["metadata"]["source_reports_resolved"]
        and card["problem_number"] not in attempt_exclusions
    ]
    direct = sorted(
        eligible,
        key=lambda card: (
            -card["posterior"]["p_verified_novel_resolution"]["probability"],
            card["problem_number"],
        ),
    )[:top_k]
    exploration_quota = min(len(eligible), max(1, top_k // 5))
    exploitation_limit = max(0, min(len(eligible), top_k) - exploration_quota)
    diversified = diversified_ranking(eligible, exploitation_limit)
    direct_records = [ranking_record(card, i, reason="highest transparent posterior")
                      for i, card in enumerate(direct, 1)]
    diverse_records = [ranking_record(card, i, reason="posterior plus uncertainty/domain diversity")
                       for i, card in enumerate(diversified, 1)]
    exploration_records = protected_exploration(
        eligible,
        top_k,
        excluded_problem_numbers={card["problem_number"] for card in diversified},
    )
    allocation_ready = (
        allocation_context_id is not None
        and all(card.get("run_contract_id") for card in eligible)
        and integrity["status"] == "complete"
    )
    allocation_queue = (
        interleave_allocation(diverse_records, exploration_records)
        if allocation_ready else []
    )
    rankings = {
        "schema_version": SCHEMA_VERSION,
        "snapshot_id": snapshot_id,
        "model_version": MODEL_VERSION,
        "model_portfolio": model_portfolio,
        "budget": budget,
        "budget_config": budget_config,
        "pipeline_version": source_commit,
        "toolset_version": toolset_version(root),
        "source_snapshot_id": canonical_snapshot.name,
        "source_snapshot_sha256": source_snapshot_sha256,
        "canonical_open_source_records": len(canonical_sources),
        "allocation_top_k": int(top_k),
        "allocation_context": allocation_context,
        "allocation_context_id": allocation_context_id,
        "allocation_status": (
            "ready" if allocation_ready
            else "withheld_until_complete_exact_recorded_context"
        ),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "eligible_problems": len(eligible),
        "attempt_exclusions": sorted(attempt_exclusions),
        "egmra_calibration": egmra_provenance,
        "corpus_integrity": integrity,
        "unranked_missing_source_records": integrity["missing_open_problem_numbers"],
        "direct_solve_probability": direct_records,
        "diversified_attack_queue": diverse_records,
        "allocation_queue": allocation_queue,
        "highest_probability_verified_novel_solution": posterior_ranking(
            eligible, "p_verified_novel_resolution", top_k,
            "highest transparent posterior for a verified novel resolution",
        ),
        "highest_probability_verified_partial_progress": posterior_ranking(
            eligible, "p_verified_partial_progress", top_k,
            "highest transparent posterior for verified partial progress",
        ),
        "highest_probability_lean_verification": posterior_ranking(
            eligible, "p_lean_verified_exact_target", top_k,
            "highest Lean-route posterior from the bounded probe",
        ),
        "best_finite_computation_targets": posterior_ranking(
            eligible, "p_finite_computational_resolution", top_k,
            "highest finite exact-computation posterior",
        ),
        "tractable_frontier": tractable_frontier_ranking(eligible, top_k),
        "most_likely_stale_literature_records": posterior_ranking(
            eligible, "p_correct_but_already_known", top_k,
            "highest already-known/literature-cleanup posterior",
        ),
        "highest_value_uncertain_problems": [
            ranking_record(
                card, rank,
                reason="uncertainty times mathematical-value prior per compute unit",
            )
            for rank, card in enumerate(sorted(
                eligible,
                key=lambda item: -(
                    (
                        item["posterior"]["p_verified_novel_resolution"]
                        ["credible_interval_approx"][1]
                        - item["posterior"]["p_verified_novel_resolution"]
                        ["credible_interval_approx"][0]
                    )
                    * item["posterior"]["p_high_mathematical_value"]["probability"]
                    / item["cost"]["relative_compute_units"]
                ),
            )[:top_k], 1)
        ],
        "highest_mathematical_value_targets": posterior_ranking(
            eligible, "p_high_mathematical_value", top_k,
            "multi-signal mathematical-value prior",
        ),
        "highest_reusable_formal_infrastructure_value": posterior_ranking(
            eligible, "p_reusable_formal_infrastructure", top_k,
            "highest reusable formal-infrastructure posterior",
        ),
        "highest_expected_corpus_wide_unlock": posterior_ranking(
            eligible, "p_expected_corpus_wide_unlock", top_k,
            "domain prevalence, shared routes, and formal reuse potential",
        ),
        "protected_exploration": exploration_records,
        "subproblem_attack_queue": subproblems,
    }
    (output_root / "rankings").mkdir(parents=True, exist_ok=True)
    write_json(output_root / "rankings" / "subproblem_attack_queue.json", subproblems)
    subproblem_lines = [
        "# Explicit Multi-Part Subproblem Queue", "",
        "Only source-explicit question parts are included; no mathematical decomposition is inferred.",
        "", "| Rank | Subproblem | Parent | Priority |", "| ---: | --- | ---: | ---: |",
    ]
    subproblem_lines.extend(
        f"| {row['rank']} | `{row['subproblem_id']}` | {row['problem_number']} | "
        f"{row['priority_score']:.3f} |"
        for row in subproblems
    )
    (output_root / "rankings" / "subproblem_attack_queue.md").write_text(
        "\n".join(subproblem_lines) + "\n", encoding="utf-8"
    )
    (output_root / "rankings" / "current.md").write_text(
        render_ranking(allocation_queue, "Erdős Searcher MVP — Protected Allocation Queue"),
        encoding="utf-8",
    )
    markdown_rankings = {
        "highest_probability_verified_novel_solution": (
            "Highest Probability of a Verified Novel Solution",
            "P(verified novel solution)",
        ),
        "highest_probability_verified_partial_progress": (
            "Highest Probability of Verified Partial Progress",
            "P(verified partial progress)",
        ),
        "highest_probability_lean_verification": (
            "Highest Probability of Lean Verification",
            "P(Lean-verified exact target)",
        ),
        "best_finite_computation_targets": (
            "Best Finite-Computation Targets",
            "P(finite computational resolution)",
        ),
        "tractable_frontier": (
            "Formal / Exact-Computation Tractable Frontier",
            "P(Lean-verified exact target)",
        ),
        "most_likely_stale_literature_records": (
            "Most Likely Stale Literature Records",
            "P(correct but already known)",
        ),
        "highest_value_uncertain_problems": (
            "Highest-Value Uncertain Problems",
            "P(verified novel solution)",
        ),
        "highest_mathematical_value_targets": (
            "Highest Mathematical-Value Targets (MVP Proxy)",
            "P(verified novel solution; value proxy)",
        ),
        "highest_reusable_formal_infrastructure_value": (
            "Highest Reusable Formal-Infrastructure Value",
            "P(reusable formal infrastructure)",
        ),
        "highest_expected_corpus_wide_unlock": (
            "Highest Expected Corpus-Wide Unlock (MVP Proxy)",
            "P(reusable formal infrastructure; unlock proxy)",
        ),
        "protected_exploration": (
            "Protected Exploration Queue",
            "P(verified novel solution)",
        ),
    }
    for key, (title, metric) in markdown_rankings.items():
        (output_root / "rankings" / f"{key}.md").write_text(
            render_ranking(rankings[key], title, metric), encoding="utf-8"
        )
    immutable_content = {
        key: value for key, value in rankings.items() if key != "generated_at"
    }
    ranking_content_sha256 = sha256_bytes(
        json.dumps(immutable_content, sort_keys=True, separators=(",", ":"))
        .encode("utf-8")
    )
    rankings["ranking_content_sha256"] = ranking_content_sha256
    allocation_id = None
    if allocation_context_id is not None:
        allocation_id = sha256_bytes(canonical_json({
            "allocation_context_id": allocation_context_id,
            "ranking_content_sha256": ranking_content_sha256,
        }).encode("utf-8"))
    rankings["allocation_id"] = allocation_id
    context_path = None
    if allocation_context_id is not None:
        context_path = (
            output_root / "rankings" / "contexts" / allocation_context_id
            / f"{ranking_content_sha256}.json"
        )
    history = (
        output_root / "rankings" / "history"
        / f"{snapshot_id}--{ranking_content_sha256[:12]}.json"
    )

    def validate_existing_ranking(path: Path) -> None:
        try:
            existing = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise RuntimeError(f"immutable ranking artifact is unreadable: {path}") from error
        existing_content = {
            key: value for key, value in existing.items()
            if key not in {"generated_at", "ranking_content_sha256", "allocation_id"}
        }
        existing_hash = sha256_bytes(
            json.dumps(existing_content, sort_keys=True, separators=(",", ":"))
            .encode("utf-8")
        )
        if (
            existing_content != immutable_content
            or existing_hash != ranking_content_sha256
            or existing.get("ranking_content_sha256") != ranking_content_sha256
            or existing.get("allocation_id") != allocation_id
        ):
            raise RuntimeError(f"immutable ranking artifact conflict: {path}")

    if context_path is not None and context_path.exists():
        validate_existing_ranking(context_path)
    if history.exists():
        validate_existing_ranking(history)
    write_json(output_root / "rankings" / "current.json", rankings)
    if context_path is not None and not context_path.exists():
        write_json(context_path, rankings)
    if not history.exists():
        write_json(history, rankings)
    return rankings


def _validate_ledger_record(record: dict) -> None:
    allowed = LEDGER_REQUIRED_FIELDS | LEDGER_OPTIONAL_FIELDS
    unknown = set(record) - allowed
    if unknown:
        raise ValueError(f"ledger record has unsupported fields: {sorted(unknown)}")
    missing = LEDGER_REQUIRED_FIELDS - set(record)
    if missing:
        raise ValueError(f"ledger record missing required fields: {sorted(missing)}")
    if not re.fullmatch(r"erdos-[0-9]+", str(record["problem_id"])):
        raise ValueError("invalid ledger problem_id")
    problem_number = int(str(record["problem_id"]).removeprefix("erdos-"))
    if "problem_number" in record and (
        not isinstance(record["problem_number"], int)
        or isinstance(record["problem_number"], bool)
        or record["problem_number"] != problem_number
    ):
        raise ValueError("ledger problem_number does not match problem_id")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:-]{2,127}", str(record["execution_id"])):
        raise ValueError("invalid ledger execution_id")
    for field in (
        "run_contract_id", "run_context_id", "source_snapshot_sha256",
        "statement_sha256",
    ):
        if not re.fullmatch(r"[0-9a-f]{64}", str(record[field])):
            raise ValueError(f"invalid ledger {field}")
    expected_run_context_id = run_context_id(
        run_contract_id_value=str(record["run_contract_id"]),
        execution_id=str(record["execution_id"]),
    )
    if record["run_context_id"] != expected_run_context_id:
        raise ValueError("ledger run_context_id does not bind execution_id to run_contract_id")
    status = str(record["status"])
    if status not in LEDGER_STATUSES:
        raise ValueError(f"invalid ledger status: {status}")
    learning_eligible = record["learning_eligible"]
    if not isinstance(learning_eligible, bool):
        raise ValueError("ledger learning_eligible must be boolean")
    if status not in AUTONOMOUS_LEARNING_STATUSES | EXTERNAL_JUDGMENT_STATUSES \
            and learning_eligible is not False:
        raise ValueError("non-learning disposition is incorrectly marked eligible")
    for field in (
        "snapshot_id", "pipeline_version", "model_portfolio", "toolset_version",
    ):
        raw_identity = record[field]
        identity = str(raw_identity)
        if (
            not isinstance(raw_identity, str)
            or not re.fullmatch(r"[\x21-\x7e]{3,128}", identity)
            or identity.lower() in {"unknown", "unrecorded", "none"}
            or "unrecorded" in identity.lower()
        ):
            raise ValueError(f"ledger {field} must record an exact identity")
    budget_config = record["budget_config"]
    if not isinstance(budget_config, dict):
        raise ValueError("ledger budget_config must be an object")
    expected_budget_keys = set(DEFAULT_BUDGET_CONFIG)
    if set(budget_config) != expected_budget_keys:
        raise ValueError("ledger budget_config is not the complete normalized budget")
    normalized_budget = normalized_budget_config(**budget_config)
    if budget_config != normalized_budget:
        raise ValueError("ledger budget_config is not canonical")
    if str(record["budget"]) != research_budget_id(**normalized_budget):
        raise ValueError("ledger budget does not match budget_config")
    certificates = record.get("evidence_certificate_ids", [])
    if not isinstance(certificates, list) or any(
        not isinstance(item, str)
        or not re.fullmatch(r"[0-9a-f]{64}", item)
        for item in certificates
    ):
        raise ValueError("invalid evidence_certificate_ids")
    if "candidate_sha256" in record and not re.fullmatch(
        r"[0-9a-f]{64}", str(record["candidate_sha256"])
    ):
        raise ValueError("invalid ledger candidate_sha256")
    gate_status = record.get("gate_status")
    if gate_status is not None and (
        not isinstance(gate_status, str) or gate_status not in LEDGER_GATE_STATUSES
    ):
        raise ValueError("invalid bounded ledger gate_status")
    candidate_outcome = record.get("candidate_outcome")
    if candidate_outcome is not None and (
        not isinstance(candidate_outcome, str)
        or candidate_outcome not in LEDGER_CANDIDATE_OUTCOMES
    ):
        raise ValueError("invalid bounded ledger candidate_outcome")
    positive_statuses = {
        "verified_novel_resolution", "verified_partial_progress",
        "verified_novelty_pending", "independent_rediscovery",
        "literature_identification",
    }
    if status in positive_statuses and (
        gate_status not in {"verified_proved", "verified_disproved"}
        or candidate_outcome not in {"candidate_proved", "candidate_disproved"}
    ):
        raise ValueError("positive ledger status contradicts gate/candidate outcome")
    if status == "no_progress_within_budget" and (
        gate_status != "candidate_rejected"
        or candidate_outcome != "resource_exhausted"
    ):
        raise ValueError("no-progress status contradicts candidate outcome")
    if status in {
        "wrong_interpretation", "statement_defect", "formalization_mismatch",
        "fundamentally_flawed_candidate",
    } and gate_status != "candidate_rejected":
        raise ValueError("rejected-candidate status contradicts gate outcome")
    if "event_id" in record and not re.fullmatch(
        r"[0-9a-f]{64}", str(record["event_id"])
    ):
        raise ValueError("invalid ledger event_id")
    if "event_sequence" in record and (
        not isinstance(record["event_sequence"], int)
        or isinstance(record["event_sequence"], bool)
        or record["event_sequence"] < 1
    ):
        raise ValueError("invalid ledger event_sequence")
    if "supersedes_event_id" in record and not re.fullmatch(
        r"[0-9a-f]{64}", str(record["supersedes_event_id"])
    ):
        raise ValueError("invalid ledger supersedes_event_id")
    if _FORBIDDEN_LEDGER_CONTENT.search(json.dumps(record, ensure_ascii=False)):
        raise ValueError("ledger record contains a forbidden secret or conversation URL")
    if "duration_seconds" in record and (
        not isinstance(record["duration_seconds"], (int, float))
        or isinstance(record["duration_seconds"], bool)
        or not math.isfinite(record["duration_seconds"])
        or record["duration_seconds"] < 0
    ):
        raise ValueError("invalid duration_seconds")
    if "cost" in record:
        cost = record["cost"]
        allowed_costs = {
            "input_tokens", "output_tokens", "total_tokens", "requests",
            "estimated_usd", "compute_seconds", "relative_compute_units",
        }
        if not isinstance(cost, dict) or set(cost) - allowed_costs or any(
            not isinstance(value, (int, float))
            or isinstance(value, bool)
            or not math.isfinite(value)
            or value < 0
            for value in cost.values()
        ):
            raise ValueError("invalid closed cost record")


def append_ledger(output_root: Path, kind: str, record_path: Path) -> bool:
    if kind not in {"attempts", "outcomes"}:
        raise ValueError(f"unsupported ledger kind: {kind}")
    record = json.loads(record_path.read_text(encoding="utf-8"))
    if not isinstance(record, dict):
        raise ValueError("ledger record must be an object")
    _validate_ledger_record(record)
    ledger = output_root / "labels" / f"{kind}.jsonl"
    ledger.parent.mkdir(parents=True, exist_ok=True)
    with ledger.open("a+", encoding="utf-8") as handle:
        fcntl.flock(handle, fcntl.LOCK_EX)
        try:
            handle.seek(0)
            chain: list[dict] = []
            for line in handle:
                try:
                    existing = json.loads(line)
                except json.JSONDecodeError:
                    continue
                try:
                    candidate = _stored_ledger_business_record(existing)
                except ValueError:
                    continue
                if candidate.get("execution_id") != record["execution_id"]:
                    continue
                try:
                    _validate_event_identity(candidate)
                except ValueError:
                    continue
                if _event_business_record(candidate) == _event_business_record(record):
                    observed = validate_evidence_certificates(output_root, record)
                    if record["learning_eligible"] is not _expected_learning_eligible(
                        output_root, record, observed
                    ):
                        raise ValueError("ledger learning eligibility failed adapter replay")
                    return False
                chain.append(candidate)
            chain.sort(key=lambda item: item["event_sequence"])
            for index, existing_event in enumerate(chain):
                expected_existing_sequence = index + 1
                expected_existing_parent = chain[index - 1]["event_id"] if index else None
                if existing_event["event_sequence"] != expected_existing_sequence \
                        or existing_event.get("supersedes_event_id") != expected_existing_parent:
                    raise ValueError("existing ledger event chain is discontinuous")
                observed = validate_evidence_certificates(output_root, existing_event)
                if existing_event["learning_eligible"] is not _expected_learning_eligible(
                    output_root, existing_event, observed
                ):
                    raise ValueError("existing ledger learning eligibility is invalid")
                if index:
                    _validate_event_transition(chain[index - 1], existing_event)
            previous = chain[-1] if chain else None
            expected_sequence = previous["event_sequence"] + 1 if previous else 1
            expected_supersedes = previous["event_id"] if previous else None
            if "event_sequence" in record and record["event_sequence"] != expected_sequence:
                raise ValueError("ledger event_sequence does not extend the latest event")
            if "supersedes_event_id" in record \
                    and record.get("supersedes_event_id") != expected_supersedes:
                raise ValueError("ledger supersedes_event_id does not bind latest event")
            event = {
                key: value for key, value in record.items()
                if key not in {"event_id", "event_sequence", "supersedes_event_id"}
            }
            event["event_sequence"] = expected_sequence
            if expected_supersedes is not None:
                event["supersedes_event_id"] = expected_supersedes
            calculated_event_id = _event_identity(event)
            if "event_id" in record and record["event_id"] != calculated_event_id:
                raise ValueError("provided ledger event_id does not match content")
            event["event_id"] = calculated_event_id
            _validate_ledger_record(event)
            _validate_event_identity(event)
            observed = validate_evidence_certificates(output_root, event)
            if event["learning_eligible"] is not _expected_learning_eligible(
                output_root, event, observed
            ):
                raise ValueError("ledger learning eligibility failed adapter replay")
            if previous is not None:
                _validate_event_transition(previous, event)
            stored = {
                **event,
                "schema_version": LEDGER_SCHEMA_VERSION,
                "recorded_at": datetime.now(timezone.utc).isoformat(),
            }
            handle.seek(0, os.SEEK_END)
            handle.write(json.dumps(stored, ensure_ascii=False, sort_keys=True) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        finally:
            fcntl.flock(handle, fcntl.LOCK_UN)
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("build", "record-attempt", "record-outcome"))
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--output", type=Path, default=Path("triage"))
    parser.add_argument("--snapshot-date", default=datetime.now(timezone.utc).date().isoformat())
    parser.add_argument("--top-k", type=int, default=25)
    parser.add_argument("--model-portfolio",
                        default=os.environ.get("CHATGPT_MODEL_PORTFOLIO", DEFAULT_MODEL_PORTFOLIO))
    parser.add_argument("--budget", default=DEFAULT_BUDGET)
    parser.add_argument("--egmra-calibration", type=Path, default=None,
                        help="egmra calibrate report (JSON); observed outcome "
                             "frequencies apply a capped weak-evidence posterior "
                             "adjustment with recorded provenance \u2014 never a "
                             "verified outcome")
    parser.add_argument("--record", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    output = (root / args.output).resolve() if not args.output.is_absolute() else args.output
    if args.command == "build":
        rankings = build_searcher(root, output, snapshot_date=args.snapshot_date,
                                  top_k=args.top_k,
                                  model_portfolio=args.model_portfolio,
                                  budget=args.budget,
                                  egmra_calibration_path=args.egmra_calibration)
        print(f"Built {rankings['eligible_problems']} eligible problem cards; "
              f"ranking snapshot {rankings['snapshot_id']}")
        return
    if args.record is None:
        parser.error("--record is required for ledger commands")
    append_ledger(output, "attempts" if args.command == "record-attempt" else "outcomes",
                  args.record)
    print(f"Appended {args.command} record from {args.record}")


if __name__ == "__main__":
    main()
