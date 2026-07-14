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
A FORMALLY_VERIFIED_CANDIDATE additionally requires an independently signed
formal-correspondence review (``--formal-correspondence-review``) binding the
kernel-checked Lean declaration to the informal claim; both review artifacts are
signed out-of-band in the independent review domain and only consumed here.
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
from egmra.compute.service import ComputeService
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
from egmra.agents.async_browser import build_browser_runner_pool
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
from egmra.m2 import ContentAddressedObjectStore, PostgresEventStore
from egmra.oeis import OEISClient
from egmra.lean.kernel_checker import (
    build_lean_replay_target,
    make_attested_kernel_runner,
    write_pinned_checker,
)
from egmra.lean.aristotle_sdk import AristotleSdkClient
from egmra.lean.formalizer import AristotleFormalizer
from egmra.lean.replay import LeanReplayVerifier
from egmra.lean.service import CheckerConfigurationError, LeanEnvironment, LeanService
from egmra.provenance.hashing import sha256_hex
from egmra.retrieval.erdos_corpus import build_erdos_corpus
from egmra.retrieval.records import TheoremRecord
from egmra.truth.events import EventLog, EventLogError
from egmra.truth.entities import (
    FormalCorrespondenceCertificate,
    IntentCertificate,
    Verdict,
)
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


def _build_browser_engine(workers: int):
    """Start an async multi-tab browser engine with ``workers`` tabs.

    Playwright's sync API is single-threaded, so genuine multi-worker overlap on
    one authenticated account uses the async API: ONE Chromium, N pages, driven on
    a dedicated event loop, one tab per campaign worker. Reachable only with an
    authenticated profile; failures surface as a clean CLI error (never a silent
    single-worker degrade).
    """
    from egmra.agents.async_browser import AsyncBrowserEngine, PlaywrightAsyncPageDriver
    try:
        import playwright  # noqa: F401
    except ImportError as exc:  # pragma: no cover - needs the browser extra
        raise ValueError(
            "browser provider requires the 'browser' extra (pip install -e .[browser] "
            "&& playwright install chromium); or use --provider deterministic"
        ) from exc
    try:  # pragma: no cover - needs an authenticated profile + display
        return AsyncBrowserEngine(PlaywrightAsyncPageDriver(), tab_count=int(workers)).start()
    except (Exception, SystemExit) as exc:  # noqa: BLE001 - surface as a clean CLI error
        raise ValueError(
            f"browser provider is not operational ({type(exc).__name__}: {exc}); "
            "authenticate a profile (python3 solve_submit.py --login) or use "
            "--provider deterministic"
        ) from exc


def _resolve_postgres_dsn(args: argparse.Namespace) -> str:
    """Resolve the Postgres DSN from --dsn or the environment (never logged)."""
    dsn = getattr(args, "dsn", None) or os.environ.get("EGMRA_POSTGRES_DSN", "")
    if not dsn:
        raise ValueError(
            "postgres event store requires a DSN: pass --dsn or set EGMRA_POSTGRES_DSN "
            "(credentials are read from the environment and never written to logs)"
        )
    return dsn


def _make_event_log(args: argparse.Namespace, run_id: str):
    """Build the event-log backend for a run (task 4.9).

    Returns ``None`` for the JSONL default (research builds its own file-backed
    append-only log at ``events_path``), or a connected
    :class:`PostgresEventStore` when ``--event-store postgres`` is selected. The
    DSN is read from the environment/CLI and never written to logs.
    """
    if getattr(args, "event_store", "jsonl") == "postgres":
        return PostgresEventStore(_resolve_postgres_dsn(args), run_id=run_id)
    return None


def _close_event_log(log) -> None:
    close = getattr(log, "close", None)
    if callable(close):  # pragma: no cover - only PostgresEventStore holds a connection
        try:
            close()
        except Exception:  # noqa: BLE001 - best-effort teardown
            pass


def _build_retrieval_corpus(args: argparse.Namespace, config: EgmraConfig):
    """Construct the literature retrieval corpus (task 4.4).

    ``--retrieval corpus`` (default) builds auditable TheoremRecords from the
    packaged Erdős snapshot so the frozen solver packet handed to the worker after
    the blind cold pass carries real source URIs, versions, content hashes, and
    verbatim statements; ``--retrieval none`` disables it (empty corpus).
    """
    if getattr(args, "retrieval", "corpus") != "corpus":
        return None
    corpus_tex = getattr(args, "corpus_tex", None) or default_corpus_tex_path()
    catalog = getattr(args, "catalog", None) or default_catalog_path()
    return build_erdos_corpus(corpus_tex, catalog)


def _build_oeis_client(args: argparse.Namespace, config: EgmraConfig) -> OEISClient:
    """Construct the OEIS client (task 4.4).

    Always returns a client so the integer-sequence search stage is reachable.
    ``--oeis live`` performs real oeis.org lookups, ``offline`` uses only the
    local cache, and ``auto`` (default) follows the signed config. An OEIS match
    can seed conjectures but never establishes proof status.
    """
    mode = getattr(args, "oeis", "auto")
    offline = config.oeis_offline if mode == "auto" else (mode != "live")
    return OEISClient(cache_dir=config.oeis_cache_dir, offline=offline)


def _build_lean_service(args: argparse.Namespace):
    """Construct a real LeanService for the formal-candidate path (task 4.6).

    Returns ``(lean_service, lean_version, mathlib_commit)``. When ``--lean-project``
    is given (a built pinned project), the service's kernel runner is the pinned
    checker (egmra/lean/kernel_checker.py), so a worker-proposed Lean declaration
    candidate is re-checked by the REAL Lean kernel inside ``egmra run``. Without
    it, the formal path stays unconfigured (no formal candidates are emitted).
    """
    lean_project = getattr(args, "lean_project", None)
    if not lean_project:
        return None, "", ""
    lean_project = Path(lean_project)
    if lean_project.is_symlink() or not lean_project.is_dir() \
            or not (lean_project / ".lake").is_dir():
        raise ValueError(
            f"--lean-project must be a built Lean project (with .lake): {lean_project}")
    import egmra as _egmra_pkg

    repo_root = Path(_egmra_pkg.__file__).resolve().parent.parent
    checker_path = Path("egmra_quarantine") / "formal" / "pinned_lean_checker.py"
    checker_path.parent.mkdir(parents=True, exist_ok=True)
    write_pinned_checker(checker_path, lean_project=lean_project, repo_root=repo_root)
    runner = make_attested_kernel_runner(checker_path)
    toolchain_file = lean_project / "lean-toolchain"
    toolchain = toolchain_file.read_text(encoding="utf-8", errors="ignore").strip() \
        if toolchain_file.is_file() else ""
    lean_version = (toolchain.split(":")[-1] or "unknown") if toolchain else "unknown"
    service = LeanService(kernel_runner=runner, lean_project=lean_project)
    return service, lean_version, args.mathlib_commit


def _build_formalizer(args: argparse.Namespace):
    """Build an autonomous formalization worker for `egmra run` (task #5).

    ``--formalizer aristotle`` makes the research controller dispatch a *pinned*
    formalization obligation (declaration name + intended Lean type) to the live
    Aristotle service and re-check the produced Lean with the pinned kernel — so
    Aristotle becomes an integrated formalization worker, not a tool beside the
    pipeline. The vendor supplies only the proof term; a vendor status never
    promotes on its own. Requires a built ``--lean-project`` (to formalize against
    the pinned toolchain and to have a LeanService kernel to verify) and
    ``ARISTOTLE_API_KEY``. Returns ``None`` for the default ``none``.
    """
    if getattr(args, "formalizer", "none") != "aristotle":
        return None
    lean_project = getattr(args, "lean_project", None)
    if not lean_project:
        raise ValueError(
            "--formalizer aristotle requires --lean-project (the built pinned Lean "
            "project used to formalize and to re-check with the kernel)")
    quarantine_root = Path("egmra_quarantine") / "formalize_run"
    try:
        client = AristotleSdkClient(
            quarantine_root=quarantine_root, project_dir=Path(lean_project), env=os.environ)
    except (Exception, SystemExit) as exc:  # noqa: BLE001 - surface as a clean CLI error
        raise ValueError(
            f"aristotle formalizer is not operational ({type(exc).__name__}: {exc}); "
            "set ARISTOTLE_API_KEY and pass a built --lean-project, or use "
            "--formalizer none"
        ) from exc
    return AristotleFormalizer(client=client)


def _build_worker_formalizers(args: argparse.Namespace, worker_ids: tuple[str, ...]) -> dict:
    """Build one autonomous Aristotle formalizer per campaign worker (task #5).

    Each worker gets its OWN :class:`AristotleSdkClient` (its own event loop): the
    SDK client is driven synchronously on a single loop and is not shared across
    the concurrent worker threads. Returns ``{}`` for the default ``none``. Any
    partially built clients are closed if construction later fails.
    """
    if getattr(args, "formalizer", "none") != "aristotle":
        return {}
    lean_project = getattr(args, "lean_project", None)
    if not lean_project:
        raise ValueError(
            "--formalizer aristotle requires --lean-project (the built pinned Lean "
            "project used to formalize and to re-check with the kernel)")
    formalizers: dict = {}
    for worker_id in worker_ids:
        quarantine_root = Path("egmra_quarantine") / "formalize_campaign" / worker_id
        try:
            client = AristotleSdkClient(
                quarantine_root=quarantine_root, project_dir=Path(lean_project),
                env=os.environ)
        except (Exception, SystemExit) as exc:  # noqa: BLE001 - clean CLI error
            for built in formalizers.values():
                built.close()
            raise ValueError(
                f"aristotle formalizer is not operational ({type(exc).__name__}: {exc}); "
                "set ARISTOTLE_API_KEY and pass a built --lean-project, or use "
                "--formalizer none"
            ) from exc
        formalizers[worker_id] = AristotleFormalizer(client=client)
    return formalizers


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
    event_log = _make_event_log(args, problem.problem_id)
    retrieval_corpus = _build_retrieval_corpus(args, config)
    oeis_client = _build_oeis_client(args, config)
    # Durable content-addressed store for model-exchange transcripts (task 4.10).
    artifact_store = ContentAddressedObjectStore(root=Path(config.artifact_store_dir))
    # Optional real formal-candidate path (task 4.6): a LeanService whose kernel
    # runner is the pinned checker, so worker-proposed Lean is re-checked live.
    lean_service, lean_version, mathlib_commit = _build_lean_service(args)
    # Optional autonomous formalization worker (task #5): Aristotle produces the
    # proof for a pinned obligation; the pinned kernel above re-checks it.
    formalizer = _build_formalizer(args)
    worker = RunnerWorker(
        runner=runner,
        goal_claim_id="goal",
        goal_formula=problem.display_statement,
        role=args.role,
        compute_service=ComputeService(),
        lean_version=lean_version,
        mathlib_commit=mathlib_commit,
        lean_project=args.lean_project,
        formalizer=formalizer,
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
            event_log=event_log,
            retrieval_corpus=retrieval_corpus,
            oeis_client=oeis_client,
            artifact_store=artifact_store,
            lean_service=lean_service,
            # A configured Lean project means this is a formal run: the referee's
            # formal audit expects a real kernel artifact, not an informal pass.
            informal_only=lean_service is None,
            status_claims=list(problem.status_claims),
            novelty_verdict=problem.novelty_verdict,
            intent_review=_load_intent_review(args.intent_review),
            formal_correspondence_reviews=_load_formal_correspondence_reviews(
                args.formal_correspondence_review
            ),
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
            "event_store": getattr(args, "event_store", "jsonl"),
            "events_path": str(events_path),
            "detail": str(exc),
            "note": "transient provider outage; resume later — not a mathematical result",
        }, indent=2))
        return 4
    finally:
        _close_runner(runner)
        _close_event_log(event_log)
        if formalizer is not None:
            formalizer.close()
    classification = classify_result(result, goal_claim_id="goal")
    rendered = result.render() | {
        "provider": args.provider,
        "event_store": getattr(args, "event_store", "jsonl"),
        "retrieval": {
            "mode": getattr(args, "retrieval", "corpus"),
            "corpus_records": len(retrieval_corpus) if retrieval_corpus is not None else 0,
            "oeis_mode": getattr(args, "oeis", "auto"),
        },
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


def _load_formal_correspondence_reviews(
    specs: list[str] | None,
) -> dict[str, FormalCorrespondenceCertificate] | None:
    """Load independently signed formal-correspondence review artifacts (task 4.6).

    Each ``--formal-correspondence-review`` value is ``CLAIM_ID=PATH`` (or a bare
    ``PATH`` for the default ``goal`` claim, so the common single-goal case needs
    no prefix); the file is a signed :class:`FormalCorrespondenceCertificate` JSON.
    A kernel-verified Lean declaration is admitted as a formal proof of the informal
    claim ONLY when such an independently signed review binds the intent certificate,
    the informal claim, the declaration name, and the elaborated type. Without one,
    ``research()`` records ``formal_correspondence_required`` rather than promoting —
    a kernel-checked declaration alone is never a formal proof of the informal claim.
    Signing happens out-of-band in the independent review domain; this loader only
    consumes and (via the orchestrator) re-verifies the signature.
    """
    if not specs:
        return None
    reviews: dict[str, FormalCorrespondenceCertificate] = {}
    for spec in specs:
        claim_id, separator, raw_path = spec.partition("=")
        if not separator or "/" in claim_id or "\\" in claim_id:
            claim_id, raw_path = "goal", spec  # bare path binds the default goal claim
        claim_id = claim_id.strip()
        if not claim_id:
            raise ValueError("formal-correspondence-review claim id must be non-empty")
        if claim_id in reviews:
            raise ValueError(
                f"duplicate formal-correspondence-review for claim: {claim_id}"
            )
        path = Path(raw_path)
        if path.is_symlink() or not path.is_file():
            raise ValueError(
                "formal-correspondence-review path must be a regular non-symlink file"
            )
        if path.stat().st_size > 1_000_000:
            raise ValueError("formal-correspondence-review artifact is too large")
        document = json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=_reject_duplicate_json_keys,
        )
        if not isinstance(document, dict):
            raise ValueError(
                "formal-correspondence-review artifact must be a JSON object"
            )
        document = dict(document)
        document["verdict"] = Verdict(document.get("verdict", "UNRESOLVED"))
        reviews[claim_id] = FormalCorrespondenceCertificate(**document)
    return reviews


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


def cmd_init_db(args: argparse.Namespace) -> int:
    """Create/verify the Postgres event schema (idempotent)."""
    store = PostgresEventStore(_resolve_postgres_dsn(args), run_id="_bootstrap")
    try:
        store.migrate()
    finally:
        store.close()
    print(json.dumps({
        "status": "ok", "action": "init-db", "dsn": store.dsn,
        "schema": "events", "note": "event schema created/verified (credentials not logged)",
    }, indent=2))
    return 0


def cmd_migrate_db(args: argparse.Namespace) -> int:
    """Apply Postgres event-store migrations (idempotent)."""
    store = PostgresEventStore(_resolve_postgres_dsn(args), run_id="_bootstrap")
    try:
        store.migrate()
    finally:
        store.close()
    print(json.dumps({
        "status": "ok", "action": "migrate-db", "dsn": store.dsn,
        "note": "migrations applied (idempotent; credentials not logged)",
    }, indent=2))
    return 0


def cmd_verify_events(args: argparse.Namespace) -> int:
    if getattr(args, "event_store", "jsonl") == "postgres":
        log = PostgresEventStore(_resolve_postgres_dsn(args), run_id=args.run_id)
        try:
            ok = log.verify_integrity()
            summary = {
                "run_id": args.run_id,
                "event_store": "postgres",
                "events": len(log),
                "merkle_root": log.merkle_root(),
                "integrity": ok,
            }
        finally:
            log.close()
        print(json.dumps(summary))
        return 0 if ok else 1
    if args.events is None:
        raise ValueError("verify-events --event-store jsonl requires --events PATH")
    log = EventLog(Path(args.events), run_id=args.run_id)
    ok = log.verify_integrity()
    print(json.dumps({
        "run_id": args.run_id,
        "event_store": "jsonl",
        "events": len(log),
        "merkle_root": log.merkle_root(),
        "integrity": ok,
    }))
    return 0 if ok else 1


def _formalize_candidate_dir(args: argparse.Namespace, lean_project: Path) -> Path:
    """Obtain a quarantine directory holding the candidate Lean to verify."""
    quar_root = Path("egmra_quarantine") / "formalize"
    if args.formalizer == "local":
        if not args.lean_file:
            raise ValueError("--formalizer local requires --lean-file PATH")
        src = Path(args.lean_file)
        if src.is_symlink() or not src.is_file():
            raise ValueError("--lean-file must be a regular non-symlink file")
        if src.stat().st_size > 4_000_000:
            raise ValueError("--lean-file is too large")
        job = quar_root / "local"
        if job.exists():
            shutil.rmtree(job)
        job.mkdir(parents=True)
        (job / (src.name if src.suffix == ".lean" else "Candidate.lean")).write_text(
            src.read_text(encoding="utf-8", errors="ignore"), encoding="utf-8")
        return job
    if not args.prompt:
        raise ValueError("--formalizer aristotle requires --prompt TEXT")
    client = AristotleSdkClient(quarantine_root=quar_root / "aristotle",
                                project_dir=lean_project, env=os.environ)
    try:
        submission = client.submit(args.prompt)
        artifact = client.fetch(submission, wait=True)
    finally:
        client.close()
    return artifact.quarantine_dir


def cmd_formalize(args: argparse.Namespace) -> int:
    """Re-check a candidate Lean proof with the real local kernel and seal an attestation.

    The candidate is produced locally (``--formalizer local --lean-file``) or by
    the live Aristotle service (``--formalizer aristotle --prompt``); either way
    it is independently re-verified by the pinned Lean kernel — a definitional
    target obligation (``example : <expected-type> := @<declaration>``) plus an
    axiom-whitelist audit. A vendor ``COMPLETE`` never promotes on its own; only
    a sealed local kernel replay is promotable.
    """
    lean_project = Path(args.lean_project)
    if lean_project.is_symlink() or not lean_project.is_dir():
        raise ValueError(f"--lean-project must be a built Lean project directory: {lean_project}")
    if not (lean_project / ".lake").is_dir():
        raise ValueError(
            f"Lean project is not built (no .lake): run 'cd {lean_project} && lake exe cache get "
            "&& lake build' first")

    candidate_dir = _formalize_candidate_dir(args, lean_project)

    import egmra as _egmra_pkg

    repo_root = Path(_egmra_pkg.__file__).resolve().parent.parent
    checker_path = Path("egmra_quarantine") / "formalize" / "pinned_lean_checker.py"
    checker_path.parent.mkdir(parents=True, exist_ok=True)
    write_pinned_checker(checker_path, lean_project=lean_project, repo_root=repo_root)

    toolchain_file = lean_project / "lean-toolchain"
    toolchain = toolchain_file.read_text(encoding="utf-8", errors="ignore").strip() \
        if toolchain_file.is_file() else ""
    env = LeanEnvironment(
        lean_version=(toolchain.split(":")[-1] or "unknown") if toolchain else "unknown",
        mathlib_commit=args.mathlib_commit,
        project_hash=sha256_hex(str(lean_project.resolve())))
    target = build_lean_replay_target(
        claim_id=args.claim_id, declaration_name=args.declaration,
        expected_type_source=args.expected_type, environment=env)
    verifier = LeanReplayVerifier(
        checker=make_attested_kernel_runner(checker_path), environment=env, target=target)
    try:
        sealed = verifier(candidate_dir)
    except CheckerConfigurationError as exc:
        raise ValueError(f"formal checker is not configured: {exc}") from exc

    result = {
        "formalizer": args.formalizer,
        "declaration": args.declaration,
        "expected_type": args.expected_type,
        "lean_project": str(lean_project),
        "candidate_dir": str(candidate_dir),
        "sealed": sealed is not None,
        "promotable_local_replay": sealed is not None,
        "note": (
            "sealed a local Lean kernel replay attestation (promotable); a vendor status "
            "alone is never trusted" if sealed is not None else
            "the local kernel did NOT verify the declaration has the expected type — "
            "not promotable (never a mathematical result)"),
    }
    if sealed is not None:
        result |= {
            "claim_id": sealed.claim_id, "source_hash": sealed.source_hash,
            "lean_version": sealed.lean_version, "mathlib_commit": sealed.mathlib_commit,
            "checker_id": sealed.checker_id,
        }
    print(json.dumps(result, indent=2))
    return 0 if sealed is not None else 3


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
    # Optional formal path (task 4.6 / #5): a shared pinned-kernel LeanService plus
    # one autonomous Aristotle formalizer per worker (the SDK client owns a single
    # event loop, so it is never shared across the concurrent worker threads).
    lean_service, lean_version, mathlib_commit = _build_lean_service(args)
    formalizers_by_worker = _build_worker_formalizers(args, workers)
    # Genuine multi-worker overlap: the deterministic provider shares one runner
    # across threads, while the browser provider drives ONE authenticated Chromium
    # with N tabs on a dedicated event loop (async multi-tab), one tab per worker.
    browser_engine = None
    runners_by_worker: dict[str, Any] = {}
    runner = None
    try:
        if args.provider == "browser":
            browser_engine = _build_browser_engine(int(args.workers))
            pool = build_browser_runner_pool(
                browser_engine, throttle=_browser_throttle(config, args.provider))
            runners_by_worker = dict(zip(workers, pool))
        else:
            runner = _build_runner(
                args.provider, throttle=_browser_throttle(config, args.provider))
    except BaseException:
        for formalizer in formalizers_by_worker.values():
            formalizer.close()
        raise
    # Build the immutable literature corpus once; it is shared read-only across
    # worker threads (the retrieval service copies it per packet).
    retrieval_corpus = _build_retrieval_corpus(args, config)

    def run_one(problem_id: str, fencing_token: int, worker_id: str) -> str:
        # Each worker drives its own browser tab (or shares the deterministic runner)
        # and its own autonomous formalizer.
        worker_runner = runners_by_worker[worker_id] if browser_engine is not None else runner
        number = int(problem_id.split("-", 1)[1])
        problem = from_erdos_number(number, corpus_tex_path=corpus_tex, catalog_path=catalog)
        worker = RunnerWorker(runner=worker_runner, goal_claim_id="goal",
                              goal_formula=problem.display_statement, role=args.role,
                              compute_service=ComputeService(),
                              lean_version=lean_version, mathlib_commit=mathlib_commit,
                              lean_project=args.lean_project,
                              formalizer=formalizers_by_worker.get(worker_id))
        # A distinct event log per attempt keeps each try's chain clean on resume.
        events_path = Path(config.events_dir) / f"{problem.problem_id}.{fencing_token}.jsonl"
        event_log = _make_event_log(args, f"{problem.problem_id}.{fencing_token}")
        oeis_client = _build_oeis_client(args, config)
        try:
            result = research(
                problem_id=problem.problem_id, source_bytes=problem.source_bytes,
                source_id=problem.source_id, budget=float(args.budget), enforcer=enforcer,
                worker=worker, goal_claim_id="goal", events_path=events_path,
                event_log=event_log, retrieval_corpus=retrieval_corpus,
                oeis_client=oeis_client, lean_service=lean_service,
                informal_only=lean_service is None,
                status_claims=list(problem.status_claims),
                novelty_verdict=problem.novelty_verdict,
                intent_review=None, runner=worker_runner,
            )
        finally:
            _close_event_log(event_log)
        return str(classify_result(result, goal_claim_id="goal").state)

    try:
        status = campaign.run_concurrent(
            run_one, max_workers=int(args.workers), now=time.time,
            provider_unavailable=BrowserProviderUnavailable,
        )
    finally:
        if browser_engine is not None:
            browser_engine.close()  # tears down the browser and every tab
        else:
            _close_runner(runner)
        for formalizer in formalizers_by_worker.values():
            formalizer.close()
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
                     help="bounded worker concurrency for the run (1-5); a single problem "
                          "is researched sequentially, so genuine multi-worker/multi-tab "
                          "overlap is a campaign feature (see 'egmra campaign --workers')")
    run.add_argument("--corpus-tex", type=Path, default=None,
                     help="override the corpus TeX snapshot used by --erdos")
    run.add_argument("--catalog", type=Path, default=None,
                     help="override the problem catalog used by --erdos")
    run.add_argument("--budget", type=float, default=50.0,
                     help="research budget for the run (default: 50)")
    run.add_argument("--policy", type=Path, default=None)
    run.add_argument("--event-store", choices=("jsonl", "postgres"), default="jsonl",
                     help="event-log backend: 'jsonl' (default, file-backed) or 'postgres'")
    run.add_argument("--dsn", default=None,
                     help="Postgres DSN for --event-store postgres (or set EGMRA_POSTGRES_DSN); "
                          "credentials are read from the environment and never logged")
    run.add_argument("--retrieval", choices=("corpus", "none"), default="corpus",
                     help="literature retrieval corpus: 'corpus' (packaged Erdős snapshot) "
                          "or 'none' (empty)")
    run.add_argument("--oeis", choices=("auto", "offline", "live"), default="auto",
                     help="OEIS sequence lookups: 'auto' (config), 'offline' (cache only), "
                          "or 'live' (oeis.org)")
    run.add_argument("--lean-project", type=Path, default=None,
                     help="built pinned Lean project (with .lake); enables the real "
                          "formal-candidate path (worker-proposed Lean re-checked by the kernel)")
    run.add_argument("--mathlib-commit", default="v4.28.0",
                     help="Mathlib revision recorded in formal candidates")
    run.add_argument(
        "--formalizer", choices=("none", "aristotle"), default="none",
        help="autonomous formalization worker: 'aristotle' dispatches pinned "
             "formalization obligations to the live Aristotle service (requires "
             "--lean-project + ARISTOTLE_API_KEY; the produced Lean is re-checked by "
             "the pinned kernel), or 'none' (model-authored Lean only)")
    run.add_argument(
        "--intent-review", type=Path, default=None,
        help="independently signed intent-review JSON bound to the problem",
    )
    run.add_argument(
        "--formal-correspondence-review", action="append", default=None,
        metavar="[CLAIM_ID=]PATH",
        help="independently signed formal-correspondence review JSON binding a "
             "kernel-verified Lean declaration to the informal claim (repeatable; "
             "CLAIM_ID defaults to 'goal'); required to reach a "
             "FORMALLY_VERIFIED_CANDIDATE",
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
    campaign.add_argument("--event-store", choices=("jsonl", "postgres"), default="jsonl",
                          help="event-log backend for each attempt ('jsonl' or 'postgres')")
    campaign.add_argument("--dsn", default=None,
                          help="Postgres DSN for --event-store postgres (or EGMRA_POSTGRES_DSN)")
    campaign.add_argument("--retrieval", choices=("corpus", "none"), default="corpus",
                          help="literature retrieval corpus source (default: Erdős snapshot)")
    campaign.add_argument("--oeis", choices=("auto", "offline", "live"), default="auto",
                          help="OEIS lookup mode ('auto', 'offline', or 'live')")
    campaign.add_argument("--lean-project", type=Path, default=None,
                          help="built pinned Lean project (with .lake); enables the formal "
                               "path so worker/Aristotle Lean is re-checked by the kernel")
    campaign.add_argument("--mathlib-commit", default="v4.28.0",
                          help="Mathlib revision recorded in formal candidates")
    campaign.add_argument("--formalizer", choices=("none", "aristotle"), default="none",
                          help="autonomous formalization worker per campaign worker: "
                               "'aristotle' (requires --lean-project + ARISTOTLE_API_KEY; "
                               "produced Lean is re-checked by the pinned kernel) or 'none'")
    campaign.add_argument("--status", action="store_true", help="print campaign status and exit")
    campaign.set_defaults(func=cmd_campaign)

    initdb = sub.add_parser("init-db", help="create/verify the Postgres event schema")
    initdb.add_argument("--dsn", default=None,
                        help="Postgres DSN (or set EGMRA_POSTGRES_DSN); credentials never logged")
    initdb.set_defaults(func=cmd_init_db)

    migratedb = sub.add_parser("migrate-db",
                               help="apply Postgres event-store migrations (idempotent)")
    migratedb.add_argument("--dsn", default=None,
                           help="Postgres DSN (or set EGMRA_POSTGRES_DSN); credentials never logged")
    migratedb.set_defaults(func=cmd_migrate_db)

    sign = sub.add_parser("policy-sign", help="sign a policy template into a new file")
    sign.add_argument("--input", type=Path, required=True)
    sign.add_argument("--output", type=Path, required=True)
    sign.set_defaults(func=cmd_policy_sign)

    show = sub.add_parser("policy-show", help="print the signed feature policy")
    show.add_argument("--policy", type=Path, default=None)
    show.set_defaults(func=cmd_policy_show)

    verify = sub.add_parser("verify-events", help="verify an event log's integrity")
    verify.add_argument("--events", type=Path, default=None,
                        help="JSONL event-log path (required for --event-store jsonl)")
    verify.add_argument("--event-store", choices=("jsonl", "postgres"), default="jsonl",
                        help="event-log backend to verify ('jsonl' or 'postgres')")
    verify.add_argument("--dsn", default=None,
                        help="Postgres DSN for --event-store postgres (or EGMRA_POSTGRES_DSN)")
    verify.add_argument(
        "--run-id", required=True,
        help="expected run/subject identifier authenticated by every event",
    )
    verify.set_defaults(func=cmd_verify_events)

    formalize = sub.add_parser(
        "formalize",
        help="re-check a candidate Lean proof with the local kernel and seal an attestation")
    formalize.add_argument("--formalizer", choices=("local", "aristotle"), default="local",
                           help="candidate source: a local Lean file or the live Aristotle service")
    formalize.add_argument("--declaration", required=True,
                           help="the Lean declaration name the proof must establish")
    formalize.add_argument("--expected-type", required=True,
                           help="the intended Lean type the declaration must prove "
                                "(e.g. '2 + 2 = 4')")
    formalize.add_argument("--lean-file", type=Path, default=None,
                           help="candidate Lean file (--formalizer local)")
    formalize.add_argument("--prompt", default=None,
                           help="task prompt for the Aristotle agent (--formalizer aristotle)")
    formalize.add_argument("--lean-project", type=Path, default=Path("aristotle_lean_project"),
                           help="built pinned Lean project (must contain .lake)")
    formalize.add_argument("--mathlib-commit", default="v4.28.0",
                           help="Mathlib revision recorded in the attestation")
    formalize.add_argument("--claim-id", default="goal",
                           help="claim id bound into the sealed replay attestation")
    formalize.set_defaults(func=cmd_formalize)

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
