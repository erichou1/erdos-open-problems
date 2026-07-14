"""EGMRA command-line interface.

Subcommands:
  run           research a real problem (--erdos N | --statement | --statement-file)
                or a bundled regression fixture (--fixture); prints the five-gate
                render plus the honest public result state
  doctor        report local readiness (deps, executables, keys present, policy,
                corpus) without ever printing a secret value
  status        summarize persisted research runs in the events directory
  policy-sign   sign an unsigned policy template into a new, mode-0600 file
  policy-show   print the signed feature policy (hash + flags), never secrets
  verify-events verify an append-only event-log's integrity
  fixtures      list the local evaluation fixtures

The primary ``run`` path drives the real research loop on an arbitrary problem;
it does not call the fixture loader. Real provider/Lean/OEIS integrations require
credentials/toolchains and are documented in DECISIONS.md. A *verified* release
also requires an independently signed intent-review artifact (``--intent-review``).
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import time
from pathlib import Path

from egmra import __version__
from egmra.compute.spec import ExperimentSpec
from egmra.config import SECRET_ENV_VARS, EgmraConfig
from egmra.corpus import (
    ProblemInput,
    SourceResolutionError,
    default_catalog_path,
    default_corpus_tex_path,
    from_erdos_number,
    from_statement,
    from_statement_file,
)
from egmra.agents.browser_runner import BrowserProviderUnavailable
from egmra.agents.throttle import SharedThrottle
from egmra.corpus.status import StatusClaim
from egmra.eval.datasets import FIXTURE_PROBLEMS, fixture
from egmra.intake.review import interpretation_review_hash
from egmra.orchestrator import (
    Campaign,
    DeterministicWorker,
    RunnerWorker,
    StructuredDemoRunner,
    classify_result,
    research,
)
from egmra.policy import PolicyEnforcer, PolicyError, default_policy_path, load_policy, sign_policy
from egmra.retrieval.records import TheoremRecord
from egmra.truth.events import EventLog, EventLogError
from egmra.truth.entities import IntentCertificate, Verdict
from egmra.truth.graph import EpistemicGraph
from egmra.truth.snapshots import TruthSnapshotError


def _fixture_worker(fx) -> DeterministicWorker:
    spec = None
    code = ""
    if fx.scope == "finite_domain" and fx.predicate_src:
        body = fx.predicate_src
        helper = ""
        if "_isprime" in body:
            body = body.replace("_isprime", "isprime")
            helper = (
                "def isprime(n):\n"
                "    if n < 2:\n"
                "        return False\n"
                "    i = 2\n"
                "    while i * i <= n:\n"
                "        if n % i == 0:\n"
                "            return False\n"
                "        i += 1\n"
                "    return True\n\n"
            )
        code = (helper + "def experiment(inputs):\n"
                f"    return {{'result': all((lambda n: {body})(k) for k in range(inputs['n']+1)),"
                " 'coverage': 'exhaustive 0..n'}\n")
        spec = ExperimentSpec(purpose=fx.problem_id, inputs={"n": 30},
                              arithmetic_mode="exact", coverage="0..n",
                              claim_ids=("goal",))
    return DeterministicWorker(
        goal_claim_id="goal", goal_formula=fx.statement.decode(), goal_scope=fx.scope,
        experiment_code=code, experiment_spec=spec)


def cmd_run(args: argparse.Namespace) -> int:
    """Dispatch a run to the arbitrary-problem path or a regression fixture."""
    config = EgmraConfig.load(args.config)
    selectors = [
        bool(args.erdos is not None),
        bool(args.statement is not None),
        bool(args.statement_file is not None),
        bool(args.fixture is not None),
    ]
    if sum(selectors) == 0:
        raise ValueError(
            "provide a problem to research: --erdos N, --statement TEXT, "
            "--statement-file PATH, or --fixture ID"
        )
    if sum(selectors) > 1:
        raise ValueError("choose exactly one of --erdos/--statement/--statement-file/--fixture")
    if args.fixture is not None:
        return _run_fixture(args, config)
    return _run_arbitrary(args, config)


def _resolve_problem_input(args: argparse.Namespace) -> ProblemInput:
    if args.erdos is not None:
        return from_erdos_number(
            args.erdos,
            corpus_tex_path=args.corpus_tex or default_corpus_tex_path(),
            catalog_path=args.catalog or default_catalog_path(),
        )
    if args.statement_file is not None:
        return from_statement_file(args.statement_file)
    return from_statement(args.statement)


def _build_runner(provider: str, *, throttle: "SharedThrottle | None" = None):
    """Construct the reasoning ModelRunner for the selected provider.

    ``browser`` is the primary informal provider and requires an authenticated
    Chromium profile plus the ``browser`` extra; when unavailable it raises a
    clear error rather than silently degrading to a deterministic stand-in.
    ``deterministic`` is a credential-free structured runner for tests/demos.
    The shared throttle (browser only) coordinates cooldowns across workers.
    """
    if provider == "deterministic":
        return StructuredDemoRunner()
    if provider == "browser":
        try:
            from egmra.agents.browser_runner import (
                BrowserChatGPTRunner,
                PlaywrightChatGPTBackend,
            )
        except ImportError as exc:  # pragma: no cover - needs the browser extra
            raise ValueError(
                "browser provider requires the 'browser' extra (pip install -e .[browser] "
                "&& playwright install chromium); or use --provider deterministic"
            ) from exc
        try:  # pragma: no cover - needs an authenticated profile + display
            backend = PlaywrightChatGPTBackend().start()
        except (Exception, SystemExit) as exc:  # noqa: BLE001 - surface as a clean CLI error
            raise ValueError(
                f"browser provider is not operational ({type(exc).__name__}: {exc}); "
                "authenticate a profile (python3 solve_submit.py --login) or use "
                "--provider deterministic"
            ) from exc
        return BrowserChatGPTRunner(backend=backend, throttle=throttle)  # pragma: no cover
    raise ValueError(f"unknown provider: {provider!r}")


def _browser_throttle(config: EgmraConfig, provider: str) -> "SharedThrottle | None":
    """A durable, cross-worker cooldown coordinator for the browser provider."""
    if provider != "browser":
        return None
    state = Path(config.events_dir) / "browser_throttle.json"
    return SharedThrottle(state, max_cooldown_s=config.max_backoff_seconds)


def _run_arbitrary(args: argparse.Namespace, config: EgmraConfig) -> int:
    """Run the real research loop on an arbitrary problem via a reasoning worker.

    The reasoning worker is a :class:`RunnerWorker` driven by the selected
    provider's ``ModelRunner`` (browser ChatGPT in production). It converts the
    model's structured output into claims/lemmas/falsifiers/queries — it never
    fabricates proof evidence, so a verified release stays unreachable without the
    real verification pipeline. This path never constructs the fixture worker.
    """
    if not 1 <= int(args.workers) <= 5:
        raise ValueError("--workers must be between 1 and 5")
    problem = _resolve_problem_input(args)
    runner = _build_runner(args.provider, throttle=_browser_throttle(config, args.provider))
    policy = load_policy(Path(args.policy) if args.policy else default_policy_path())
    enforcer = PolicyEnforcer(policy)
    events_path = Path(config.events_dir) / f"{problem.problem_id}.jsonl"
    worker = RunnerWorker(
        runner=runner,
        goal_claim_id="goal",
        goal_formula=problem.display_statement,
        role=args.role,
    )
    try:
        result = research(
            problem_id=problem.problem_id,
            source_bytes=problem.source_bytes,
            source_id=problem.source_id,
            budget=float(args.budget),
            enforcer=enforcer,
            worker=worker,
            goal_claim_id="goal",
            events_path=events_path,
            status_claims=list(problem.status_claims),
            novelty_verdict=problem.novelty_verdict,
            intent_review=_load_intent_review(args.intent_review),
            runner=runner,
        )
    except BrowserProviderUnavailable as exc:
        # Provider throttling/outage is transient: retain the job's durable event
        # log and report a retryable status. This is NEVER a mathematical verdict.
        print(json.dumps({
            "status": "provider_unavailable",
            "problem_id": problem.problem_id,
            "provider": args.provider,
            "retain": True,
            "events_path": str(events_path),
            "detail": str(exc),
            "note": "transient provider outage; resume later — not a mathematical result",
        }, indent=2))
        return 4
    finally:
        _close_runner(runner)
    classification = classify_result(result, goal_claim_id="goal")
    rendered = result.render() | {
        "provider": args.provider,
        "input": {
            "problem_id": problem.problem_id,
            "source_id": problem.source_id,
            "kind": problem.metadata.get("input_kind", "statement"),
            "statement_preview": problem.display_statement[:200],
            "metadata": problem.metadata,
        },
        "result_state": classification.to_dict(),
    }
    print(json.dumps(rendered, indent=2))
    return 0


def _close_runner(runner) -> None:
    close = getattr(runner, "close", None)
    if callable(close):  # pragma: no cover - only the browser runner has a tab to close
        try:
            close()
        except Exception:  # noqa: BLE001 - best-effort teardown
            pass


def _run_fixture(args: argparse.Namespace, config: EgmraConfig) -> int:
    fx = fixture(args.fixture)
    policy = load_policy(Path(args.policy) if args.policy else default_policy_path())
    enforcer = PolicyEnforcer(policy)
    corpus = [TheoremRecord(theorem_id="t", canonical_statement="x", conclusion="y",
                            source_uri="u", source_version="v", source_content_hash="h",
                            verbatim_theorem_and_hypothesis_extract="x")]
    events_path = Path(config.events_dir) / f"{fx.problem_id}.jsonl"
    intent_review = _load_intent_review(args.intent_review)
    result = research(
        problem_id=fx.problem_id, source_bytes=fx.statement, source_id=fx.problem_id,
        budget=100.0, enforcer=enforcer, worker=_fixture_worker(fx), goal_claim_id="goal",
        events_path=events_path, retrieval_corpus=corpus, probe_predicate=fx.predicate(),
        status_claims=[StatusClaim(
            problem_id=fx.problem_id, status="known", source="local://bundled-fixture-manifest",
            review_date=time.strftime("%Y-%m-%d", time.gmtime()),
            source_independence="bundled-regression-fixture",
        )],
        novelty_verdict="known",
        intent_review=intent_review,
    )
    expectation_met = _fixture_expectation_met(fx.expected_outcome, result)
    rendered = result.render() | {
        "expected_outcome": fx.expected_outcome,
        "expectation_met": expectation_met,
        "result_state": classify_result(result, goal_claim_id="goal").to_dict(),
    }
    print(json.dumps(rendered, indent=2))
    return 0 if expectation_met else 3


def _fixture_expectation_met(expected: str, result) -> bool:
    if expected == "verified":
        certificate = result.certificate
        compiled = result.compiled_proof
        gates = result.gates
        promotion = result.promotion
        if not all((certificate, compiled, gates, promotion)):
            return False
        try:
            approved = result.contract.lattice.approved_interpretation()
            replayed = EpistemicGraph(result.graph.log)
            goal = replayed.claims.get(compiled.goal_claim_id)
            replayed_interpretation = replayed.interpretations.get(
                certificate.active_interpretation_id
            )
        except (AttributeError, KeyError, TypeError, ValueError, RuntimeError):
            return False
        return bool(
            promotion.promoted
            and compiled.complete
            and result.problem_id == result.contract.problem_id
            and result.problem_id == result.graph.log.run_id
            and result.problem_id in replayed.problems
            and certificate.problem_contract_hash == result.contract.contract_hash()
            and certificate.result_claim_id == compiled.goal_claim_id
            and goal is not None
            and goal.truth_status.value == "SUPPORTED"
            and goal.canonical_hash == certificate.result_claim_hash
            and approved is not None
            and certificate.active_interpretation_id == approved.interpretation_id
            and certificate.active_interpretation_hash == interpretation_review_hash(approved)
            and replayed_interpretation is not None
            and certificate.active_interpretation_hash
            == interpretation_review_hash(replayed_interpretation)
            and certificate.gates.gate_digest == gates.gate_digest
            and certificate.promotion_authorization == promotion.to_dict()
            and gates.truth in {"T2", "T3", "T4", "T5"}
            and gates.intent == "I2"
            and gates.verify_attestation(event_log=result.graph.log)
            and certificate.verify(event_log=result.graph.log)
            and result.outcome == gates.summary_label()
            and not result.contract.release_blocked
            and result.referee_result is not None
            and not result.referee_result.blocks_release
        )
    if expected == "honest_triage":
        return result.outcome in {"honest_triage_report", "honest_no_result"} \
            and result.certificate is None
    if expected == "refuted":
        goal = result.graph.claims.get("goal")
        return bool(goal and goal.truth_status.value == "REFUTED")
    return False


def _reject_duplicate_json_keys(pairs):
    document = {}
    for key, value in pairs:
        if key in document:
            raise ValueError(f"duplicate JSON key: {key}")
        document[key] = value
    return document


def _load_intent_review(path: Path | None) -> IntentCertificate | None:
    if path is None:
        return None
    if path.is_symlink() or not path.is_file():
        raise ValueError("intent review path must be a regular non-symlink file")
    if path.stat().st_size > 1_000_000:
        raise ValueError("intent review artifact is too large")
    document = json.loads(
        path.read_text(encoding="utf-8"),
        object_pairs_hook=_reject_duplicate_json_keys,
    )
    if not isinstance(document, dict):
        raise ValueError("intent review artifact must be a JSON object")
    document = dict(document)
    document["verdict"] = Verdict(document.get("verdict", "UNRESOLVED"))
    return IntentCertificate(**document)


def cmd_policy_sign(args: argparse.Namespace) -> int:
    """Sign a policy template without a fallback key or destructive overwrite."""
    source = Path(args.input)
    output = Path(args.output)
    if os.path.lexists(output):
        raise FileExistsError(f"refusing to overwrite existing path: {output}")
    document = json.loads(
        source.read_text(encoding="utf-8"), object_pairs_hook=_reject_duplicate_json_keys,
    )
    if not isinstance(document, dict) or not isinstance(document.get("flags"), dict):
        raise ValueError("policy template must be an object containing a flags object")
    policy = sign_policy(document["flags"])
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(output, flags, 0o600)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(policy.to_document(), handle, sort_keys=True, separators=(",", ":"))
            handle.write("\n")
    except Exception:
        try:
            output.unlink(missing_ok=True)
        finally:
            raise
    print(json.dumps({"policy_hash": policy.policy_hash, "output": str(output)}))
    return 0


def cmd_policy_show(args: argparse.Namespace) -> int:
    policy = load_policy(Path(args.policy) if args.policy else default_policy_path())
    print(json.dumps({"policy_hash": policy.policy_hash, "signature_trust": policy.signature_trust,
                      "flags": dict(policy.flags)}, indent=2))
    return 0


def cmd_verify_events(args: argparse.Namespace) -> int:
    log = EventLog(Path(args.events), run_id=args.run_id)
    ok = log.verify_integrity()
    print(json.dumps({
        "run_id": args.run_id,
        "events": len(log),
        "merkle_root": log.merkle_root(),
        "integrity": ok,
    }))
    return 0 if ok else 1


def cmd_fixtures(_args: argparse.Namespace) -> int:
    for fx in FIXTURE_PROBLEMS:
        print(f"{fx.problem_id}\t[{fx.expected_outcome}]\tL{fx.level}\t{fx.statement.decode()[:60]}")
    return 0


def _parse_erdos_range(spec: str) -> list[int]:
    """Parse 'N' or 'A-B' into an ordered list of positive Erdős numbers."""
    spec = spec.strip()
    if "-" in spec:
        lo_s, hi_s = spec.split("-", 1)
        lo, hi = int(lo_s), int(hi_s)
    else:
        lo = hi = int(spec)
    if lo <= 0 or hi < lo:
        raise ValueError("--erdos-range must be 'N' or 'A-B' with 0 < A <= B")
    if hi - lo + 1 > 2000:
        raise ValueError("--erdos-range is too large (max 2000 problems)")
    return list(range(lo, hi + 1))


def cmd_campaign(args: argparse.Namespace) -> int:
    """Run (or resume) a durable, bounded-worker campaign over Erdős problems.

    State is durable and resumable: re-invoking with the same ``--state`` resumes
    without skipping or duplicating a problem. Provider throttling retains a
    problem for a later attempt; it is never recorded as a mathematical failure.
    """
    config = EgmraConfig.load(args.config)
    if not 1 <= int(args.workers) <= 5:
        raise ValueError("--workers must be between 1 and 5")
    state_path = Path(args.state)
    workers = tuple(f"w{i}" for i in range(int(args.workers)))
    campaign = Campaign(state_path, worker_ids=workers)

    if args.status:
        print(json.dumps(campaign.status(), indent=2))
        return 0

    if not args.erdos_range:
        raise ValueError("provide --erdos-range (e.g. 900-905) or --status")
    numbers = _parse_erdos_range(args.erdos_range)
    problem_ids = [f"erdos-{n}" for n in numbers]
    campaign_id = args.campaign_id or f"camp-erdos-{numbers[0]}-{numbers[-1]}"
    campaign.initialize(campaign_id, problem_ids)  # idempotent; safe to resume

    policy = load_policy(Path(args.policy) if args.policy else default_policy_path())
    enforcer = PolicyEnforcer(policy)
    corpus_tex = args.corpus_tex or default_corpus_tex_path()
    catalog = args.catalog or default_catalog_path()
    # Playwright's sync API is single-threaded, so real multi-worker overlap is
    # only safe for the credential-free provider; the browser provider drives one
    # authenticated page and runs one worker (multi-tab async is future work).
    if args.provider == "browser" and int(args.workers) > 1:
        raise ValueError(
            "browser provider supports --workers 1 (Playwright sync is single-threaded); "
            "use --provider deterministic for real multi-worker concurrency"
        )
    runner = _build_runner(args.provider, throttle=_browser_throttle(config, args.provider))

    def run_one(problem_id: str, fencing_token: int, worker_id: str) -> str:
        number = int(problem_id.split("-", 1)[1])
        problem = from_erdos_number(number, corpus_tex_path=corpus_tex, catalog_path=catalog)
        worker = RunnerWorker(runner=runner, goal_claim_id="goal",
                              goal_formula=problem.display_statement, role=args.role)
        # A distinct event log per attempt keeps each try's chain clean on resume.
        events_path = Path(config.events_dir) / f"{problem.problem_id}.{fencing_token}.jsonl"
        result = research(
            problem_id=problem.problem_id, source_bytes=problem.source_bytes,
            source_id=problem.source_id, budget=float(args.budget), enforcer=enforcer,
            worker=worker, goal_claim_id="goal", events_path=events_path,
            status_claims=list(problem.status_claims), novelty_verdict=problem.novelty_verdict,
            intent_review=None, runner=runner,
        )
        return str(classify_result(result, goal_claim_id="goal").state)

    try:
        status = campaign.run_concurrent(
            run_one, max_workers=int(args.workers), now=time.time,
            provider_unavailable=BrowserProviderUnavailable,
        )
    finally:
        _close_runner(runner)
    print(json.dumps(status, indent=2))
    return 0



# Executables that unlock live formal / vendor paths, with the probe used to
# decide whether they are genuinely operational (not merely present on PATH).
_OPTIONAL_EXECUTABLES = {
    "lake": (("--version",), "Lean/Mathlib build tool (formal verification path)"),
    "lean": (("--version",), "Lean theorem prover (formal verification path)"),
    "aristotle": (("--version",), "Aristotle CLI (vendor formal-search adapter)"),
}

_OPTIONAL_MODULES = {
    "playwright": "browser ChatGPT reasoning adapter (primary informal provider)",
    "requests": "upstream corpus fetch / status refresh",
    "yaml": "problems.yaml parsing",
}


def _module_available(name: str) -> bool:
    import importlib.util

    try:
        return importlib.util.find_spec(name) is not None
    except (ImportError, ValueError):
        return False


def _key_readiness() -> dict[str, dict[str, bool]]:
    """Report which signing keys are configured — booleans only, never values."""
    report: dict[str, dict[str, bool]] = {}
    for name in SECRET_ENV_VARS:
        raw = os.environ.get(name, "")
        report[name] = {
            "configured": bool(raw),
            "sufficient_length": len(raw.encode("utf-8")) >= 32,
        }
    return report


def _probe_executable(name: str, version_args: tuple[str, ...]) -> dict[str, object]:
    """Distinguish 'on PATH' from 'genuinely operational' via a real version probe."""
    import subprocess

    path = shutil.which(name)
    report: dict[str, object] = {"found": bool(path), "path": path or "", "operational": False}
    if not path:
        return report
    try:
        completed = subprocess.run(  # noqa: S603 - fixed argv, no shell
            [path, *version_args], capture_output=True, text=True, timeout=15, check=False,
        )
        report["operational"] = completed.returncode == 0
        report["version"] = (completed.stdout or completed.stderr or "").strip()[:120]
    except (OSError, subprocess.SubprocessError) as exc:
        report["operational"] = False
        report["probe_error"] = f"{type(exc).__name__}: {exc}"
    return report


def _lean_toolchain_report(executables: dict[str, dict[str, object]],
                           config: EgmraConfig) -> dict[str, object]:
    """Real Lean readiness: launchers must be operational AND a project configured."""
    lake = executables.get("lake", {})
    lean = executables.get("lean", {})
    project = Path(config.lean_lake_path)
    # A usable toolchain needs operational lake+lean and a lakefile/lean-toolchain
    # in the configured project directory (a launcher alone is not readiness).
    project_dir = project if project.is_dir() else project.parent
    has_project = any((project_dir / f).exists()
                      for f in ("lakefile.toml", "lakefile.lean", "lean-toolchain"))
    operational = bool(lake.get("operational") and lean.get("operational"))
    return {
        "lake_operational": bool(lake.get("operational")),
        "lean_operational": bool(lean.get("operational")),
        "project_configured": has_project,
        "project_probe_dir": str(project_dir),
        # End-to-end kernel verification also needs a pinned Mathlib build, which
        # this probe does not attempt to compile.
        "operational": operational and has_project,
    }


def cmd_doctor(args: argparse.Namespace) -> int:
    """Report local readiness without printing any secret value."""
    config = EgmraConfig.load(args.config)
    python_ok = sys.version_info >= (3, 10)
    modules = {
        name: {"available": _module_available(name), "purpose": purpose}
        for name, purpose in _OPTIONAL_MODULES.items()
    }
    executables = {
        name: {**_probe_executable(name, probe[0]), "purpose": probe[1]}
        for name, probe in _OPTIONAL_EXECUTABLES.items()
    }
    keys = _key_readiness()
    lean_toolchain = _lean_toolchain_report(executables, config)

    policy_report: dict[str, object] = {}
    policy_path = Path(args.policy) if args.policy else default_policy_path()
    try:
        policy = load_policy(policy_path)
        policy_report = {
            "path": str(policy_path), "loadable": True,
            "signature_trust": policy.signature_trust,
        }
    except (PolicyError, OSError, ValueError, json.JSONDecodeError) as exc:
        policy_report = {"path": str(policy_path), "loadable": False,
                         "error": f"{type(exc).__name__}: {exc}"}

    corpus_tex = args.corpus_tex or default_corpus_tex_path()
    catalog = args.catalog or default_catalog_path()
    corpus = {
        "corpus_tex": {"path": str(corpus_tex), "present": Path(corpus_tex).is_file()},
        "catalog": {"path": str(catalog), "present": Path(catalog).is_file()},
    }

    core_keys = ("EGMRA_EVENT_KEY", "EGMRA_EVIDENCE_KEY", "EGMRA_GATE_KEY",
                 "EGMRA_TRUTH_SNAPSHOT_KEY", "EGMRA_AUTHORITY_KEY")
    core_keys_ready = all(keys[name]["sufficient_length"] for name in core_keys)
    report = {
        "python_version": ".".join(str(v) for v in sys.version_info[:3]),
        "python_supported": python_ok,
        "egmra_version": __version__,
        "optional_dependencies": modules,
        "executables": executables,
        "lean_toolchain": lean_toolchain,
        "signing_keys": keys,
        "policy": policy_report,
        "corpus": corpus,
        "ready_for": {
            "local_research": bool(python_ok and core_keys_ready and policy_report.get("loadable")),
            "browser_reasoning": modules["playwright"]["available"],
            # Real formal verification requires an operational toolchain AND a
            # configured project — not merely a launcher on PATH.
            "formal_verification": lean_toolchain["operational"],
            "aristotle": executables["aristotle"]["operational"],
        },
    }
    print(json.dumps(report, indent=2))
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    """Summarize persisted research runs in the configured events directory."""
    config = EgmraConfig.load(args.config)
    events_dir = Path(args.events_dir) if args.events_dir else Path(config.events_dir)
    runs: list[dict[str, object]] = []
    if events_dir.is_dir():
        for path in sorted(events_dir.glob("*.jsonl")):
            if path.is_symlink() or not path.is_file():
                continue
            run_id = path.stem
            entry: dict[str, object] = {"run_id": run_id, "events_path": str(path)}
            try:
                log = EventLog(path, run_id=run_id)
                entry["events"] = len(log)
                entry["integrity"] = log.verify_integrity()
                entry["merkle_root"] = log.merkle_root()
            except (EventLogError, OSError, ValueError, json.JSONDecodeError) as exc:
                entry["error"] = f"{type(exc).__name__}: {exc}"
            runs.append(entry)
    print(json.dumps({"events_dir": str(events_dir), "run_count": len(runs), "runs": runs},
                     indent=2))
    return 0



def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="egmra", description=__doc__)
    parser.add_argument("--config", type=Path, default=None)
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="research a real problem or a regression fixture")
    run.add_argument("--erdos", type=int, default=None,
                     help="Erdős problem number to resolve from the local corpus snapshot")
    run.add_argument("--statement", default=None,
                     help="verbatim problem statement to research")
    run.add_argument("--statement-file", type=Path, default=None,
                     help="path to a file containing the problem statement")
    run.add_argument("--fixture", default=None,
                     help="bundled regression fixture id (see 'egmra fixtures')")
    run.add_argument("--provider", choices=("browser", "deterministic"), default="browser",
                     help="reasoning provider: 'browser' (primary) or 'deterministic' "
                          "(tests/demos only)")
    run.add_argument("--role", default="prover",
                     help="worker role that shapes the reasoning prompt")
    run.add_argument("--workers", type=int, default=1,
                     help="bounded worker concurrency for the run (1-5)")
    run.add_argument("--corpus-tex", type=Path, default=None,
                     help="override the corpus TeX snapshot used by --erdos")
    run.add_argument("--catalog", type=Path, default=None,
                     help="override the problem catalog used by --erdos")
    run.add_argument("--budget", type=float, default=50.0,
                     help="research budget for the run (default: 50)")
    run.add_argument("--policy", type=Path, default=None)
    run.add_argument(
        "--intent-review", type=Path, default=None,
        help="independently signed intent-review JSON bound to the problem",
    )
    run.set_defaults(func=cmd_run)

    doctor = sub.add_parser("doctor", help="report local readiness (deps, keys, policy, corpus)")
    doctor.add_argument("--policy", type=Path, default=None)
    doctor.add_argument("--corpus-tex", type=Path, default=None)
    doctor.add_argument("--catalog", type=Path, default=None)
    doctor.set_defaults(func=cmd_doctor)

    status = sub.add_parser("status", help="summarize persisted research runs")
    status.add_argument("--events-dir", type=Path, default=None,
                        help="override the events directory (default: config events_dir)")
    status.set_defaults(func=cmd_status)

    campaign = sub.add_parser("campaign", help="run/resume a durable bounded-worker campaign")
    campaign.add_argument("--erdos-range", default="",
                          help="Erdős problems as 'N' or 'A-B' (e.g. 900-905)")
    campaign.add_argument("--state", type=Path, default=Path("egmra_campaign.json"),
                          help="durable campaign state file (resume by reusing it)")
    campaign.add_argument("--campaign-id", default=None)
    campaign.add_argument("--provider", choices=("browser", "deterministic"), default="browser")
    campaign.add_argument("--role", default="prover")
    campaign.add_argument("--workers", type=int, default=1, help="bounded worker count (1-5)")
    campaign.add_argument("--budget", type=float, default=50.0)
    campaign.add_argument("--policy", type=Path, default=None)
    campaign.add_argument("--corpus-tex", type=Path, default=None)
    campaign.add_argument("--catalog", type=Path, default=None)
    campaign.add_argument("--status", action="store_true", help="print campaign status and exit")
    campaign.set_defaults(func=cmd_campaign)

    sign = sub.add_parser("policy-sign", help="sign a policy template into a new file")
    sign.add_argument("--input", type=Path, required=True)
    sign.add_argument("--output", type=Path, required=True)
    sign.set_defaults(func=cmd_policy_sign)

    show = sub.add_parser("policy-show", help="print the signed feature policy")
    show.add_argument("--policy", type=Path, default=None)
    show.set_defaults(func=cmd_policy_show)

    verify = sub.add_parser("verify-events", help="verify an event log's integrity")
    verify.add_argument("--events", type=Path, required=True)
    verify.add_argument(
        "--run-id", required=True,
        help="expected run/subject identifier authenticated by every event",
    )
    verify.set_defaults(func=cmd_verify_events)

    fixtures = sub.add_parser("fixtures", help="list local evaluation fixtures")
    fixtures.set_defaults(func=cmd_fixtures)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except (
        PolicyError, TruthSnapshotError, EventLogError, OSError, ValueError, KeyError,
        json.JSONDecodeError,
    ) as exc:
        print(json.dumps({"error": type(exc).__name__, "detail": str(exc)}), file=sys.stderr)
        return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
