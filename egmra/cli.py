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
import secrets
import shutil
import sys
import time
from datetime import datetime, timezone
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
from egmra.intake import build_problem_contract
from egmra.intake.predicate import compile_bounded_predicate
from egmra.intake.review import interpretation_review_hash, sign_intent_certificate
from egmra.lean.correspondence import sign_formal_correspondence_certificate
from egmra.orchestrator import (
    Campaign,
    DeterministicWorker,
    PostgresCampaignStore,
    RunnerWorker,
    StructuredDemoRunner,
    classify_result,
    research,
)
from egmra.orchestrator.campaign import CampaignError
from egmra.orchestrator.outcome_ledger import (
    EgmraOutcomeLedger,
    build_outcome_record,
)
from egmra.orchestrator.triage_source import triage_ranked_problem_ids
from egmra.policy import PolicyEnforcer, PolicyError, default_policy_path, load_policy, sign_policy
from egmra.m2 import ContentAddressedObjectStore, PostgresEventStore
from egmra.oeis import OEISClient
from egmra.lean.kernel_checker import (
    build_lean_replay_target,
    expected_type_hash,
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
from egmra.retrieval.scholarly import (
    SCHOLARLY_SOURCES,
    UrllibFetcher,
    build_scholarly_corpus,
)
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
    fixture_id = getattr(args, "fixture", None)
    if fixture_id is not None:
        fx = fixture(fixture_id)
        return ProblemInput(
            problem_id=fx.problem_id,
            source_bytes=fx.statement,
            source_id=fx.problem_id,
            display_statement=fx.statement.decode("utf-8"),
            metadata={"input_kind": "fixture"},
        )
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
    if provider in ("openai-api", "deepseek-api", "anthropic-api"):
        from egmra.agents.api_runner import ApiProviderError, build_api_runner

        try:
            return build_api_runner(provider)
        except ApiProviderError as exc:
            raise ValueError(str(exc)) from exc
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
        return BrowserChatGPTRunner(
            backend=backend, throttle=throttle,
            response_timeout_s=_browser_response_timeout(),
        )  # pragma: no cover
    raise ValueError(f"unknown provider: {provider!r}")


def _browser_response_timeout() -> float:
    """Per-exchange browser response timeout (deep reasoning can exceed 5 min).

    Override with ``EGMRA_BROWSER_RESPONSE_TIMEOUT_S``; the default matches the
    proven legacy think-timeout of 600s. Bounded to a sane operator range.
    """
    raw = os.environ.get("EGMRA_BROWSER_RESPONSE_TIMEOUT_S", "").strip()
    try:
        value = float(raw) if raw else 600.0
    except ValueError:
        return 600.0
    return min(3600.0, max(60.0, value))


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


def _make_event_log(
    args: argparse.Namespace, run_id: str, *, events_path: Path | None = None
):
    """Build the event-log backend for a run (task 4.9).

    Returns a file-backed :class:`EventLog` for the JSONL default, or a connected
    :class:`PostgresEventStore` when ``--event-store postgres`` is selected. The
    DSN is read from the environment/CLI and never written to logs.
    """
    if getattr(args, "event_store", "jsonl") == "postgres":
        return PostgresEventStore(_resolve_postgres_dsn(args), run_id=run_id)
    if events_path is not None:
        return EventLog(events_path, run_id=run_id)
    return None


def _new_attempt_id(problem_id: str) -> str:
    """Return a collision-resistant run id without conflating it with the problem.

    A problem may be researched repeatedly.  The frozen problem identity remains
    content-bound and stable, while each attempt gets its own append-only chain.
    """
    return f"{problem_id}.{time.time_ns()}-{os.getpid()}-{secrets.token_hex(4)}"


def _campaign_attempt_id(campaign_id: str, problem_id: str, fencing_token: int) -> str:
    """Namespace an attempt across campaigns without trusting an ID as a path.

    PostgreSQL event run IDs are global, and JSONL paths share one directory.
    Fencing tokens are only monotonic *within* a campaign, so
    ``problem_id.token`` collides when two campaigns cover the same problem.
    """
    campaign_namespace = sha256_hex(campaign_id)[:16]
    return f"camp-{campaign_namespace}.{problem_id}.{int(fencing_token)}"


def _close_event_log(log) -> None:
    close = getattr(log, "close", None)
    if callable(close):  # pragma: no cover - only PostgresEventStore holds a connection
        try:
            close()
        except Exception:  # noqa: BLE001 - best-effort teardown
            pass


def _build_retrieval_corpus(args: argparse.Namespace, config: EgmraConfig, *, query: str = ""):
    """Construct the literature retrieval corpus (tasks 4.4 + #7).

    ``--retrieval corpus`` (default) builds auditable TheoremRecords from the
    packaged Erdős snapshot so the frozen solver packet handed to the worker after
    the blind cold pass carries real source URIs, versions, content hashes, and
    verbatim statements. ``--retrieval arxiv|crossref|scholarly`` instead performs
    LIVE, query-specific scholarly retrieval (the problem statement is the query),
    yielding the same auditable, provenance-bearing records from real sources.
    ``--retrieval none`` disables it. A retrieved record seeds hypotheses/queries
    only — it never establishes proof status.
    """
    mode = getattr(args, "retrieval", "corpus")
    if mode == "none":
        return None
    if mode == "corpus":
        corpus_tex = getattr(args, "corpus_tex", None) or default_corpus_tex_path()
        catalog = getattr(args, "catalog", None) or default_catalog_path()
        return build_erdos_corpus(corpus_tex, catalog)
    # Live scholarly retrieval — query-specific, confined to an allowlisted host set.
    sources = SCHOLARLY_SOURCES if mode == "scholarly" else (mode,)
    return build_scholarly_corpus(
        query, fetcher=UrllibFetcher(), sources=sources,
        limit=int(getattr(args, "retrieval_limit", 5)))


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
    """Build an autonomous formalization worker for `egmra run` (task #5 + R6).

    ``aristotle`` dispatches pinned obligations to the live Aristotle service;
    ``api`` uses an attested API provider (``--formalizer-provider``) as the
    formal engine; ``portfolio`` tries Aristotle first then the API engine —
    a real prover portfolio with no single point of failure. Every produced
    candidate is re-checked by the pinned kernel; a vendor status never
    promotes on its own. Returns ``None`` for the default ``none``.
    """
    kind = getattr(args, "formalizer", "none")
    if kind == "none":
        return None
    lean_project = getattr(args, "lean_project", None)
    if not lean_project:
        raise ValueError(
            f"--formalizer {kind} requires --lean-project (the built pinned Lean "
            "project used to formalize and to re-check with the kernel)")
    members: list = []
    if kind in ("aristotle", "portfolio"):
        quarantine_root = Path("egmra_quarantine") / "formalize_run"
        try:
            client = AristotleSdkClient(
                quarantine_root=quarantine_root, project_dir=Path(lean_project), env=os.environ)
        except (Exception, SystemExit) as exc:  # noqa: BLE001 - surface as a clean CLI error
            if kind == "aristotle":
                raise ValueError(
                    f"aristotle formalizer is not operational ({type(exc).__name__}: {exc}); "
                    "set ARISTOTLE_API_KEY and pass a built --lean-project, or use "
                    "--formalizer none"
                ) from exc
        else:
            members.append(AristotleFormalizer(client=client))
    if kind in ("api", "portfolio"):
        from egmra.agents.api_runner import ApiProviderError, build_api_runner
        from egmra.lean.formalizer import ApiFormalizer

        provider = getattr(args, "formalizer_provider", None) or "deepseek-api"
        try:
            members.append(ApiFormalizer(
                runner=build_api_runner(provider),
                formalizer_id=f"api:{provider}"))
        except ApiProviderError as exc:
            if kind == "api" or not members:
                raise ValueError(str(exc)) from exc
    if not members:
        raise ValueError(f"--formalizer {kind}: no formal engine is operational")
    if len(members) == 1:
        return members[0]
    from egmra.lean.formalizer import PortfolioFormalizer

    return PortfolioFormalizer(members=members)


def _build_worker_formalizers(args: argparse.Namespace, worker_ids: tuple[str, ...]) -> dict:
    """Build one autonomous formalizer per campaign worker (task #5 + R6).

    Each worker gets its OWN engine instances: the Aristotle SDK client is
    driven synchronously on a single loop and is not shared across the
    concurrent worker threads; API formalizers are stateless per call. Returns
    ``{}`` for the default ``none``. Any partially built clients are closed if
    construction later fails.
    """
    kind = getattr(args, "formalizer", "none")
    if kind == "none":
        return {}
    lean_project = getattr(args, "lean_project", None)
    if not lean_project:
        raise ValueError(
            f"--formalizer {kind} requires --lean-project (the built pinned Lean "
            "project used to formalize and to re-check with the kernel)")
    formalizers: dict = {}
    for worker_id in worker_ids:
        members: list = []
        if kind in ("aristotle", "portfolio"):
            quarantine_root = Path("egmra_quarantine") / "formalize_campaign" / worker_id
            try:
                client = AristotleSdkClient(
                    quarantine_root=quarantine_root, project_dir=Path(lean_project),
                    env=os.environ)
            except (Exception, SystemExit) as exc:  # noqa: BLE001 - clean CLI error
                if kind == "aristotle":
                    for built in formalizers.values():
                        built.close()
                    raise ValueError(
                        f"aristotle formalizer is not operational ({type(exc).__name__}: {exc}); "
                        "set ARISTOTLE_API_KEY and pass a built --lean-project, or use "
                        "--formalizer none"
                    ) from exc
            else:
                members.append(AristotleFormalizer(client=client))
        if kind in ("api", "portfolio"):
            from egmra.agents.api_runner import ApiProviderError, build_api_runner
            from egmra.lean.formalizer import ApiFormalizer

            provider = getattr(args, "formalizer_provider", None) or "deepseek-api"
            try:
                members.append(ApiFormalizer(
                    runner=build_api_runner(provider),
                    formalizer_id=f"api:{provider}"))
            except ApiProviderError as exc:
                if kind == "api" or not members:
                    for built in formalizers.values():
                        built.close()
                    raise ValueError(str(exc)) from exc
        if not members:
            for built in formalizers.values():
                built.close()
            raise ValueError(f"--formalizer {kind}: no formal engine is operational")
        if len(members) == 1:
            formalizers[worker_id] = members[0]
        else:
            from egmra.lean.formalizer import PortfolioFormalizer

            formalizers[worker_id] = PortfolioFormalizer(members=members)
    return formalizers


def _build_hostile_reviewers(count: int, providers: list[str] | None,
                             fallback_runner) -> list[tuple[str, object]]:
    """Build the hostile-review panel.

    With ``--hostile-review-provider`` each reviewer is an ATTESTED API runner
    (cycling through the given providers; two distinct providers = two genuine
    lineages, the T3 requirement).  Without it, reviewers reuse the main
    provider runner — honest but lineage-collapsed for unattested providers.
    """
    if count <= 0:
        return []
    if not providers:
        return [(f"hostile-{i + 1}", fallback_runner) for i in range(count)]
    from egmra.agents.api_runner import ApiProviderError, build_api_runner

    reviewers: list[tuple[str, object]] = []
    for i in range(count):
        provider = providers[i % len(providers)]
        try:
            reviewers.append((f"hostile-{i + 1}", build_api_runner(provider)))
        except ApiProviderError as exc:
            raise ValueError(str(exc)) from exc
    return reviewers


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
    worker_rounds = int(getattr(args, "worker_rounds", 1) or 1)
    if not 1 <= worker_rounds <= 8:
        raise ValueError("--worker-rounds must be between 1 and 8")
    hostile_review = int(getattr(args, "hostile_review", 0) or 0)
    if not 0 <= hostile_review <= 4:
        raise ValueError("--hostile-review must be between 0 and 4")
    lean_repair_rounds = int(getattr(args, "lean_repair_rounds", 0) or 0)
    if not 0 <= lean_repair_rounds <= 3:
        raise ValueError("--lean-repair-rounds must be between 0 and 3")
    formal_target = _load_formal_target(getattr(args, "formal_target_file", None))
    problem = _resolve_problem_input(args)
    # Optional operator-supplied bounded predicate (a safe expression over ``n``)
    # so the counterexample/boundary probes genuinely enumerate small cases on the
    # arbitrary/browser path — the fixture path already carries its own predicate.
    probe_predicate = (
        compile_bounded_predicate(args.predicate)
        if getattr(args, "predicate", None) else None
    )
    runner = _build_runner(args.provider, throttle=_browser_throttle(config, args.provider))
    # Exchange-level durability (finer than branch checkpoints): with a
    # checkpoint dir configured, every model exchange is cached keyed by its
    # exact prompt hash, so a retried attempt replays identical exchanges
    # instantly and goes live at the first divergence. Fail-open to live.
    checkpoint_dir = getattr(args, "checkpoint_dir", None)
    if checkpoint_dir is not None:
        from egmra.agents.exchange_cache import CachedRunner

        runner = CachedRunner(
            runner, Path(checkpoint_dir) / problem.problem_id / "exchanges")
    policy = load_policy(Path(args.policy) if args.policy else default_policy_path())
    enforcer = PolicyEnforcer(policy)
    run_id = _new_attempt_id(problem.problem_id)
    events_path = Path(config.events_dir) / f"{run_id}.jsonl"
    event_log = _make_event_log(args, run_id, events_path=events_path)
    retrieval_corpus = _build_retrieval_corpus(args, config, query=problem.display_statement)
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
        max_rounds=worker_rounds,
        formal_target=formal_target,
    )
    informal_reviewers = _build_hostile_reviewers(
        hostile_review, getattr(args, "hostile_review_provider", None), runner)
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
            probe_predicate=probe_predicate,
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
            informal_reviewers=informal_reviewers or None,
            lean_repair_rounds=lean_repair_rounds,
            checkpoint_dir=getattr(args, "checkpoint_dir", None),
            resume_from=getattr(args, "resume_from", None),
            expert_review=_load_expert_review(getattr(args, "expert_review", None)),
            explore_blocked=bool(getattr(args, "explore_blocked", False)),
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
        "run_id": run_id,
        "events_path": str(events_path),
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
    run_id = _new_attempt_id(fx.problem_id)
    events_path = Path(config.events_dir) / f"{run_id}.jsonl"
    event_log = _make_event_log(args, run_id, events_path=events_path)
    intent_review = _load_intent_review(args.intent_review)
    try:
        result = research(
            problem_id=fx.problem_id, source_bytes=fx.statement, source_id=fx.problem_id,
            budget=100.0, enforcer=enforcer, worker=_fixture_worker(fx), goal_claim_id="goal",
            events_path=events_path, event_log=event_log,
            retrieval_corpus=corpus, probe_predicate=fx.predicate(),
            status_claims=[StatusClaim(
                problem_id=fx.problem_id, status="known", source="local://bundled-fixture-manifest",
                review_date=time.strftime("%Y-%m-%d", time.gmtime()),
                source_independence="bundled-regression-fixture",
            )],
            novelty_verdict="known",
            intent_review=intent_review,
        )
    finally:
        _close_event_log(event_log)
    expectation_met = _fixture_expectation_met(fx.expected_outcome, result)
    rendered = result.render() | {
        "run_id": run_id,
        "events_path": str(events_path),
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


def _load_expert_review(path: Path | None):
    """Load a signed expert significance review (verified by the orchestrator)."""
    if path is None:
        return None
    from egmra.release.expert_review import ExpertReviewCertificate

    if path.is_symlink() or not path.is_file():
        raise ValueError("expert review path must be a regular non-symlink file")
    if path.stat().st_size > 1_000_000:
        raise ValueError("expert review artifact is too large")
    document = json.loads(
        path.read_text(encoding="utf-8"),
        object_pairs_hook=_reject_duplicate_json_keys,
    )
    return ExpertReviewCertificate.from_dict(document)


def _load_formal_target(path: Path | None) -> str:
    """Read a community-reviewed Lean statement for the worker prompt (R5).

    Read-only prompt context pinning the intended obligation — never truth
    authority, never a proof, and never a substitute for the independently
    signed formal-correspondence review.
    """
    if path is None:
        return ""
    if path.is_symlink() or not path.is_file():
        raise ValueError("formal target path must be a regular non-symlink file")
    if path.stat().st_size > 1_000_000:
        raise ValueError("formal target file is too large")
    source = path.read_text(encoding="utf-8").strip()
    if not source:
        raise ValueError("formal target file is empty")
    return source


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


_INTENT_REVIEW_METHODS = (
    "independent_parse", "examples", "anti_examples", "paraphrase", "local_mutation",
)
_CORRESPONDENCE_REVIEW_METHODS = (
    "backtranslation", "examples", "anti_examples", "paraphrase", "local_mutation",
)


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _write_signed_review(output: Path, document: dict) -> None:
    """Write a signed review artifact to a new mode-0600 file, never overwriting."""
    if os.path.lexists(output):
        raise FileExistsError(f"refusing to overwrite existing path: {output}")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(output, flags, 0o600)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(document, handle, sort_keys=True, separators=(",", ":"))
            handle.write("\n")
    except Exception:
        try:
            output.unlink(missing_ok=True)
        finally:
            raise


def cmd_sign_review_intent(args: argparse.Namespace) -> int:
    """Sign an intent-review certificate for a problem with the review key.

    The reviewer's own key (``EGMRA_INTENT_REVIEW_KEY``) authenticates the verdict,
    and the certificate binds the exact source bytes, locked interpretation, and
    informal claim of the resolved problem — recomputed here the same way the
    orchestrator does, so the artifact binds a matching run. This is a facility for
    a genuine independent reviewer to record and sign their own judgement; it does
    not perform the review, and the binding is only trustworthy if the key is held
    by a party independent of generation and intake.
    """
    problem = _resolve_problem_input(args)
    contract = build_problem_contract(
        problem_id=problem.problem_id, source_bytes=problem.source_bytes,
        source_id=problem.source_id,
    )
    interp = contract.lattice.nodes[0]
    verdict = Verdict.APPROVED if args.verdict == "approved" else Verdict.REJECTED
    certificate = sign_intent_certificate(IntentCertificate(
        certificate_id=args.certificate_id or f"intent-{problem.problem_id}",
        source_bytes_hash=contract.source_bytes_hash,
        interpretation_hash=interpretation_review_hash(interp),
        informal_claim_hash=sha256_hex(interp.conclusion),
        methods=list(_INTENT_REVIEW_METHODS),
        reviewer_ids=[args.reviewer_id],
        reviewer_independence_and_conflicts=[{
            "reviewer_id": args.reviewer_id,
            "independent_from": ["governor", "intake_retrieval"],
            "conflicts": [],
        }],
        verdict=verdict,
        created_at=_utc_now(),
    ))
    _write_signed_review(Path(args.output), certificate.to_dict())
    print(json.dumps({
        "certificate_id": certificate.certificate_id,
        "problem_id": problem.problem_id,
        "verdict": str(certificate.verdict),
        "reviewer_key_id": certificate.reviewer_key_id,
        "output": str(args.output),
        "note": (
            "signed with EGMRA_INTENT_REVIEW_KEY; asserts the named reviewer performed "
            f"the review methods {list(_INTENT_REVIEW_METHODS)} and is independent of "
            "generation/intake. The binding is only trustworthy if that key is held by "
            "such a reviewer — an operator self-signing all keys is a self-review."
        ),
    }, indent=2))
    return 0


def _build_searcher_for_refresh(searcher_root: Path, output_root: Path, *,
                                snapshot_date: str, top_k: int,
                                calibration_path: Path) -> dict:
    """Import the repo-root searcher and rebuild the corpus ranking.

    Isolated as a seam so tests can exercise the refresh plumbing without a
    full corpus snapshot rebuild.
    """
    root = Path(searcher_root).resolve()
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    import erdos_searcher

    return erdos_searcher.build_searcher(
        root, Path(output_root), snapshot_date=snapshot_date, top_k=top_k,
        egmra_calibration_path=calibration_path)


def _refresh_ranking(outcome_paths: list[Path], *, searcher_root: Path,
                     output_root: Path, snapshot_date: str, top_k: int) -> dict:
    """Corpus-wide ranking refresh from EGMRA outcomes (closes the R11 loop).

    Aggregates the outcome ledgers into an `egmra calibrate` report, writes it
    as a DERIVED artifact under the searcher's labels dir (refresh-in-place is
    deliberate — it is a projection of the append-only ledgers, carrying the
    generation timestamp), then rebuilds the ranking with the report as a
    capped weak-evidence posterior input whose provenance the searcher records.
    """
    from egmra.orchestrator.calibration import build_calibration_report

    report = build_calibration_report([Path(p) for p in outcome_paths])
    labels_dir = Path(output_root) / "labels"
    labels_dir.mkdir(parents=True, exist_ok=True)
    report_path = labels_dir / "egmra_calibration.json"
    tmp_path = report_path.with_suffix(".tmp")
    tmp_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    tmp_path.replace(report_path)
    rankings = _build_searcher_for_refresh(
        Path(searcher_root), Path(output_root), snapshot_date=snapshot_date,
        top_k=top_k, calibration_path=report_path)
    return {
        "calibration_report": str(report_path),
        "calibration_runs": report["total_runs"],
        "eligible_problems": rankings.get("eligible_problems"),
        "snapshot_id": rankings.get("snapshot_id"),
        "egmra_calibration": rankings.get("egmra_calibration"),
    }


def cmd_refresh_ranking(args: argparse.Namespace) -> int:
    """Rebuild the corpus-wide searcher ranking from EGMRA outcome ledgers."""
    summary = _refresh_ranking(
        list(args.outcomes), searcher_root=args.searcher_root,
        output_root=args.searcher_output, snapshot_date=args.snapshot_date,
        top_k=int(args.top_k))
    print(json.dumps(summary, indent=2))
    return 0


def cmd_calibrate(args: argparse.Namespace) -> int:
    """Aggregate outcome ledgers into an honest calibration report (R11)."""
    from egmra.orchestrator.calibration import build_calibration_report

    report = build_calibration_report(list(args.outcomes))
    rendered = json.dumps(report, indent=2)
    if args.output is not None:
        output = Path(args.output)
        if output.exists():
            raise ValueError(f"refusing to overwrite {output}")
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered + "\n", encoding="utf-8")
        print(json.dumps({
            "output": str(output),
            "total_runs": report["total_runs"],
            "by_state": report["by_state"],
        }, indent=2))
    else:
        print(rendered)
    return 0


def cmd_sign_review_expert(args: argparse.Namespace) -> int:
    """Sign an expert significance review with the expert-review key.

    Binds the exact problem source bytes and the locked informal claim — the
    same hashes the orchestrator recomputes — so the judgement can never be
    stretched over a different statement.  Significance only: the truth plane
    alone decides correctness, and this key can never touch it.
    """
    from egmra.release.expert_review import (
        ExpertReviewCertificate,
        sign_expert_review,
    )

    problem = _resolve_problem_input(args)
    contract = build_problem_contract(
        problem_id=problem.problem_id, source_bytes=problem.source_bytes,
        source_id=problem.source_id,
    )
    interp = contract.lattice.nodes[0]
    certificate = sign_expert_review(ExpertReviewCertificate(
        certificate_id=args.certificate_id or f"expert-{problem.problem_id}",
        source_bytes_hash=contract.source_bytes_hash,
        informal_claim_hash=sha256_hex(interp.conclusion),
        reviewer_id=args.reviewer_id,
        verdict=args.verdict,
        statement_of_significance=args.significance,
        independent_from=("governor", "release"),
        created_at=_utc_now(),
    ))
    _write_signed_review(Path(args.output), certificate.to_dict())
    print(json.dumps({
        "certificate_id": certificate.certificate_id,
        "problem_id": problem.problem_id,
        "verdict": certificate.verdict,
        "reviewer_key_id": certificate.reviewer_key_id,
        "output": str(args.output),
        "note": (
            "signed with EGMRA_EXPERT_REVIEW_KEY; asserts the named HUMAN expert "
            "judged the result's significance and is independent of generation "
            "and release. It raises S1\u2192S2 only \u2014 it can never affect "
            "truth. The binding is only trustworthy if that key is held by such "
            "an expert; an operator self-signing all keys is a self-review."
        ),
    }, indent=2))
    return 0


def cmd_sign_review_correspondence(args: argparse.Namespace) -> int:
    """Sign a formal-correspondence certificate binding a Lean declaration to a claim.

    Reads the signed intent artifact (``--intent-review``) for the certificate id
    and informal-claim hash it must bind, then binds the Lean declaration name and
    its elaborated type (``--expected-type`` must match the kernel-checked
    candidate's type exactly for the orchestrator to admit the declaration as a
    formal proof of the informal claim). Signed with
    ``EGMRA_FORMAL_CORRESPONDENCE_KEY``; the binding is only trustworthy if that key
    is held by a reviewer independent of formalization and release.
    """
    intent = _load_intent_review(Path(args.intent_review))
    if intent is None:
        raise ValueError("--intent-review is required to bind the intent certificate")
    verdict = Verdict.APPROVED if args.verdict == "approved" else Verdict.REJECTED
    certificate = sign_formal_correspondence_certificate(FormalCorrespondenceCertificate(
        certificate_id=args.certificate_id or f"formal-correspondence-{args.declaration}",
        intent_certificate_id=intent.certificate_id,
        informal_claim_hash=intent.informal_claim_hash,
        lean_declaration_name=args.declaration,
        elaborated_type_hash=expected_type_hash(args.expected_type),
        notation_and_definition_map_hash=sha256_hex(args.notation_map or ""),
        methods=list(_CORRESPONDENCE_REVIEW_METHODS),
        reviewer_ids=[args.reviewer_id],
        reviewer_independence_and_conflicts=[{
            "reviewer_id": args.reviewer_id,
            "independent_from": ["formalization_authority", "governor"],
            "conflicts": [],
        }],
        verdict=verdict,
        created_at=_utc_now(),
    ))
    _write_signed_review(Path(args.output), certificate.to_dict())
    print(json.dumps({
        "certificate_id": certificate.certificate_id,
        "intent_certificate_id": certificate.intent_certificate_id,
        "lean_declaration_name": certificate.lean_declaration_name,
        "elaborated_type_hash": certificate.elaborated_type_hash,
        "verdict": str(certificate.verdict),
        "reviewer_key_id": certificate.reviewer_key_id,
        "output": str(args.output),
        "note": (
            "signed with EGMRA_FORMAL_CORRESPONDENCE_KEY; asserts the named reviewer "
            "confirmed the Lean declaration/type faithfully formalizes the informal "
            "claim and is independent of formalization/release. --expected-type must "
            "equal the kernel-checked candidate's elaborated type for the run to bind it."
        ),
    }, indent=2))
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


def cmd_formal_target(args: argparse.Namespace) -> int:
    """Fetch the community-reviewed Lean statement for one Erdős problem (R5).

    The fetched source is a *pinned obligation and prompt context*: pass it to
    ``egmra run --formal-target-file``.  It is never truth authority and never
    a substitute for the independently signed formal-correspondence review.  A
    mutable ref (``main``) is honestly reported as non-reproducible; pin an
    immutable ``bench-v{N}-lean4.{X}.{Y}`` tag for anything release-adjacent.
    """
    from egmra.corpus.formal_conjectures import (
        DEFAULT_REF,
        FormalConjectureUnavailable,
        fetch_formal_conjecture,
    )

    ref = args.ref or DEFAULT_REF
    try:
        target = fetch_formal_conjecture(int(args.erdos), ref=ref)
    except (FormalConjectureUnavailable, ValueError) as exc:
        print(json.dumps({"error": str(exc), "problem": args.erdos, "ref": ref}))
        return 3
    if args.output is not None:
        output = Path(args.output)
        if os.path.lexists(output):
            raise FileExistsError(f"refusing to overwrite existing path: {output}")
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW
        fd = os.open(output, flags, 0o644)
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(target.lean_source)
    print(json.dumps(target.to_dict(), indent=2))
    return 0


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


def _load_campaign_reviews(reviews_dir) -> dict:
    """Load per-problem signed review artifacts for a campaign (release parity).

    Directory convention (one file per problem, produced by ``egmra
    sign-review``):

    * ``intent-<problem_id>.json``          — signed intent review (I2)
    * ``correspondence-<problem_id>.json``  — formal correspondence for 'goal'
    * ``expert-<problem_id>.json``          — expert significance review (S2)

    Everything is loaded and validated up front so a malformed artifact fails
    the campaign LAUNCH, never a worker mid-run.  Problems without artifacts
    run exactly as before (no intent → evidence-grade only); the orchestrator
    still re-verifies every signature and hash binding per run — this loader
    grants nothing by itself.
    """
    if reviews_dir is None:
        return {}
    directory = Path(reviews_dir)
    if not directory.is_dir():
        raise ValueError(f"--reviews-dir is not a directory: {directory}")
    reviews: dict[str, dict] = {}
    for path in sorted(directory.glob("*.json")):
        name = path.name[:-len(".json")]
        for prefix, key in (("intent-", "intent"),
                            ("correspondence-", "correspondence"),
                            ("expert-", "expert")):
            if not name.startswith(prefix):
                continue
            problem_id = name[len(prefix):]
            if not problem_id:
                raise ValueError(f"review artifact has no problem id: {path.name}")
            entry = reviews.setdefault(problem_id, {})
            if key == "intent":
                entry["intent"] = _load_intent_review(path)
            elif key == "correspondence":
                entry["correspondence"] = _load_formal_correspondence_reviews(
                    [f"goal={path}"])
            else:
                entry["expert"] = _load_expert_review(path)
            break
    return reviews


def cmd_campaign(args: argparse.Namespace) -> int:
    """Run (or resume) a durable, bounded-worker campaign over Erdős problems.

    State is durable and resumable: re-invoking with the same ``--state`` resumes
    without skipping or duplicating a problem. Provider throttling retains a
    problem for a later attempt; it is never recorded as a mathematical failure.
    """
    config = EgmraConfig.load(args.config)
    if not 1 <= int(args.workers) <= 5:
        raise ValueError("--workers must be between 1 and 5")
    campaign_worker_rounds = int(getattr(args, "worker_rounds", 1) or 1)
    if not 1 <= campaign_worker_rounds <= 8:
        raise ValueError("--worker-rounds must be between 1 and 8")
    campaign_repair_rounds = int(getattr(args, "lean_repair_rounds", 0) or 0)
    if not 0 <= campaign_repair_rounds <= 3:
        raise ValueError("--lean-repair-rounds must be between 0 and 3")
    campaign_hostile_review = int(getattr(args, "hostile_review", 0) or 0)
    if not 0 <= campaign_hostile_review <= 4:
        raise ValueError("--hostile-review must be between 0 and 4")
    state_path = Path(args.state)
    workers = tuple(f"w{i}" for i in range(int(args.workers)))
    # Durable campaign state: a signed local JSON file by default, or an opt-in
    # DB-backed store (--state-store postgres) so leases/checkpoints are durable
    # and coordinated across processes/hosts sharing the database.
    campaign_store = None
    if getattr(args, "state_store", "file") == "postgres":
        campaign_store = PostgresCampaignStore(
            _resolve_postgres_dsn(args), name=(args.campaign_id or state_path.stem))
    campaign = Campaign(state_path, worker_ids=workers, store=campaign_store)
    # R12-lite: one in-process memory shared across the campaign's runs, so
    # branch families that actually produce supported claims earn cross-problem
    # posterior priors (search-order preference only, never a truth signal).
    from egmra.learning import LongTermMemory

    campaign_memory = LongTermMemory()

    if args.status:
        try:
            print(json.dumps(campaign.status(), indent=2))
        finally:
            campaign.close()
        return 0

    # Problem source: an explicit --erdos-range, or the searcher's triage
    # rankings drained in ranked order (the single-pipeline replacement for the
    # legacy run_continuous.py, which drove ProofPipeline instead of EGMRA).
    triage_dir = getattr(args, "triage", None)
    max_problems = int(getattr(args, "max_problems", 0) or 0)
    if triage_dir is not None and args.erdos_range:
        raise ValueError("provide either --erdos-range or --triage, not both")
    if triage_dir is not None:
        limit = max_problems if max_problems > 0 else None
        problem_ids = triage_ranked_problem_ids(
            Path(triage_dir), lane=args.triage_lane, limit=limit)
        numbers = [int(pid.split("-", 1)[1]) for pid in problem_ids]
        campaign_id = args.campaign_id or (
            f"camp-triage-{args.triage_lane}-{numbers[0]}")
    elif args.erdos_range:
        numbers = _parse_erdos_range(args.erdos_range)
        problem_ids = [f"erdos-{n}" for n in numbers]
        campaign_id = args.campaign_id or f"camp-erdos-{numbers[0]}-{numbers[-1]}"
    else:
        raise ValueError(
            "provide --erdos-range (e.g. 900-905), --triage DIR, or --status")
    campaign.initialize(campaign_id, problem_ids)  # idempotent; safe to resume

    outcome_ledger = (
        EgmraOutcomeLedger(Path(args.outcome_ledger))
        if getattr(args, "outcome_ledger", None) else None
    )

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
                browser_engine, throttle=_browser_throttle(config, args.provider),
                response_timeout_s=_browser_response_timeout())
            runners_by_worker = dict(zip(workers, pool))
        else:
            runner = _build_runner(
                args.provider, throttle=_browser_throttle(config, args.provider))
    except BaseException:
        for formalizer in formalizers_by_worker.values():
            formalizer.close()
        raise
    # Literature corpus: built once (shared, read-only) for the packaged snapshot,
    # or rebuilt per-problem for the query-specific LIVE scholarly modes.
    scholarly_mode = args.retrieval not in {"corpus", "none"}
    shared_corpus = None if scholarly_mode else _build_retrieval_corpus(args, config)
    # Per-problem signed review artifacts (release parity with `egmra run`):
    # a campaign problem with a valid signed intent — and, for the formal
    # route, a correspondence certificate — can reach a release exactly like
    # a single-problem run. Loaded and validated once, up front.
    campaign_reviews = _load_campaign_reviews(getattr(args, "reviews_dir", None))

    def run_one(problem_id: str, fencing_token: int, worker_id: str) -> str:
        # Each worker drives its own browser tab (or shares the deterministic runner)
        # and its own autonomous formalizer.
        worker_runner = runners_by_worker[worker_id] if browser_engine is not None else runner
        number = int(problem_id.split("-", 1)[1])
        problem = from_erdos_number(number, corpus_tex_path=corpus_tex, catalog_path=catalog)
        if getattr(args, "checkpoint_dir", None) is not None:
            from egmra.agents.exchange_cache import CachedRunner

            # pass@k retry independence: after a COMPLETED attempt recorded an
            # outcome, the next attempt salts the cache so it draws fresh,
            # independent samples instead of replaying the failed trajectory.
            # Crash retries (no recorded outcome) keep salt "" and replay free.
            prior_outcomes = 0
            if outcome_ledger is not None:
                try:
                    prior_outcomes = sum(
                        1 for row in outcome_ledger.records()
                        if row.get("problem_id") == problem.problem_id)
                except (OSError, ValueError):
                    prior_outcomes = 0
            worker_runner = CachedRunner(
                worker_runner,
                Path(args.checkpoint_dir) / problem.problem_id / "exchanges",
                salt=f"retry-sample-{prior_outcomes}" if prior_outcomes else "")
        retrieval_corpus = (
            _build_retrieval_corpus(args, config, query=problem.display_statement)
            if scholarly_mode else shared_corpus)
        worker = RunnerWorker(runner=worker_runner, goal_claim_id="goal",
                              goal_formula=problem.display_statement, role=args.role,
                              compute_service=ComputeService(),
                              lean_version=lean_version, mathlib_commit=mathlib_commit,
                              lean_project=args.lean_project,
                              formalizer=formalizers_by_worker.get(worker_id),
                              max_rounds=campaign_worker_rounds)
        # Durable per-problem dossier (search guidance only, never truth): a
        # NEW campaign process seeds this problem's approach-family outcomes
        # and failed approaches from the previous processes' learning instead
        # of re-deriving them. Fail-open end to end.
        dossier_path = None
        if getattr(args, "checkpoint_dir", None) is not None:
            from egmra.orchestrator.dossier import load_dossier, seed_from_dossier

            dossier_path = (Path(args.checkpoint_dir) / problem.problem_id
                            / "dossier.json")
            seed_from_dossier(load_dossier(dossier_path), memory=campaign_memory,
                              worker=worker, problem_id=problem.problem_id)
        # A distinct event log per attempt keeps each try's chain clean on resume.
        attempt_run_id = _campaign_attempt_id(
            campaign_id, problem.problem_id, fencing_token,
        )
        events_path = Path(config.events_dir) / f"{attempt_run_id}.jsonl"
        event_log = _make_event_log(
            args, attempt_run_id, events_path=events_path,
        )
        oeis_client = _build_oeis_client(args, config)
        problem_reviews = campaign_reviews.get(problem.problem_id, {})
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
                intent_review=problem_reviews.get("intent"),
                formal_correspondence_reviews=problem_reviews.get("correspondence"),
                expert_review=problem_reviews.get("expert"),
                runner=worker_runner,
                lean_repair_rounds=campaign_repair_rounds,
                checkpoint_dir=getattr(args, "checkpoint_dir", None),
                # A campaign retry warm-starts from its own checkpoint dir: the
                # verified snapshot skips already-attempted branches and
                # re-books the budget already spent. Fail-closed to fresh.
                resume_from=getattr(args, "checkpoint_dir", None),
                explore_blocked=bool(getattr(args, "explore_blocked", False)),
                memory=campaign_memory,
                informal_reviewers=_build_hostile_reviewers(
                    campaign_hostile_review,
                    getattr(args, "hostile_review_provider", None),
                    worker_runner) or None,
            )
        finally:
            _close_event_log(event_log)
        state = str(classify_result(result, goal_claim_id="goal").state)
        if dossier_path is not None:
            from egmra.orchestrator.dossier import harvest_for_dossier, update_dossier

            try:
                update_dossier(dossier_path, problem_id=problem.problem_id,
                               public_state=state,
                               harvest=harvest_for_dossier(
                                   campaign_memory, worker, problem.problem_id))
            except OSError:
                pass    # persistence is an ops aid, never a verdict
        # Honest EGMRA-native outcome telemetry (never the legacy contract-bound
        # searcher ledger, never a release authority).
        if outcome_ledger is not None:
            outcome_ledger.record(build_outcome_record(
                problem_id=problem.problem_id, result=result,
                run_id=attempt_run_id, state=state))
            if getattr(args, "auto_rerank", False):
                # Continuous rerank: observed outcomes mechanically adjust the
                # PENDING order (search preference only — never truth, never
                # release). The searcher prior is the tie-break; leased and
                # completed problems are untouched. Fail-open: a rerank
                # problem never affects the recorded mathematical outcome.
                try:
                    from egmra.orchestrator.rerank import rerank_pending

                    new_order, reasons = rerank_pending(
                        list(problem_ids), outcome_ledger.records())
                    if campaign.reorder_pending(new_order) and reasons:
                        print(json.dumps({
                            "auto_rerank": {"order": new_order,
                                            "reasons": reasons},
                        }), file=sys.stderr, flush=True)
                except (CampaignError, OSError, ValueError):
                    pass
        return state

    try:
        status = campaign.run_concurrent(
            run_one, max_workers=int(args.workers), now=time.time,
            provider_unavailable=BrowserProviderUnavailable,
            permanent_failure=SourceResolutionError,
        )
        # Corpus-wide refresh AFTER the campaign: outcomes feed the searcher's
        # posterior scoring as capped weak evidence and the whole ranking is
        # rebuilt. Fail-open with a recorded note — a ranking refresh problem
        # is operational, never a mathematical outcome.
        if getattr(args, "refresh_ranking_after", False) \
                and getattr(args, "outcome_ledger", None) is not None:
            try:
                status["ranking_refresh"] = _refresh_ranking(
                    [Path(args.outcome_ledger)],
                    searcher_root=Path.cwd(),
                    output_root=Path(args.triage) if args.triage else Path("triage"),
                    snapshot_date=datetime.now(timezone.utc).date().isoformat(),
                    top_k=25)
            except Exception as exc:  # noqa: BLE001 - ops aid, never a verdict
                status["ranking_refresh"] = {
                    "error": f"{type(exc).__name__}: {exc}"}
    finally:
        if browser_engine is not None:
            browser_engine.close()  # tears down the browser and every tab
        else:
            _close_runner(runner)
        for formalizer in formalizers_by_worker.values():
            formalizer.close()
        campaign.close()
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
    run.add_argument("--predicate", default=None,
                     help="safe bounded predicate expression over the integer 'n' (e.g. "
                          "'n*n >= 0' or 'all(k*k >= 0 for k in range(n+1))') that the "
                          "counterexample/boundary probes enumerate over the small domain; "
                          "AST-restricted to numeric expressions (no imports, attribute "
                          "access, or arbitrary calls). Applies to --erdos/--statement runs")
    run.add_argument("--provider",
                     choices=("browser", "deterministic", "openai-api",
                              "deepseek-api", "anthropic-api"),
                     default="browser",
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
    run.add_argument("--retrieval",
                     choices=("corpus", "arxiv", "crossref", "semanticscholar", "mathoverflow",
                              "scholarly", "none"),
                     default="corpus",
                     help="literature retrieval: 'corpus' (packaged Erdős snapshot), "
                          "'arxiv'/'crossref'/'semanticscholar'/'mathoverflow' or 'scholarly' "
                          "(LIVE query-specific scholarly retrieval on the problem statement; "
                          "'scholarly' merges all sources), or 'none' (empty)")
    run.add_argument("--oeis", choices=("auto", "offline", "live"), default="auto",
                     help="OEIS sequence lookups: 'auto' (config), 'offline' (cache only), "
                          "or 'live' (oeis.org)")
    run.add_argument("--lean-project", type=Path, default=None,
                     help="built pinned Lean project (with .lake); enables the real "
                          "formal-candidate path (worker-proposed Lean re-checked by the kernel)")
    run.add_argument("--mathlib-commit", default="v4.28.0",
                     help="Mathlib revision recorded in formal candidates")
    run.add_argument(
        "--formalizer", choices=("none", "aristotle", "api", "portfolio"),
        default="none",
        help="autonomous formalization worker: 'aristotle' dispatches pinned "
             "formalization obligations to the live Aristotle service (requires "
             "--lean-project + ARISTOTLE_API_KEY), 'api' uses an attested API "
             "provider (--formalizer-provider, e.g. deepseek-api), 'portfolio' "
             "tries aristotle then the API engine (R6: no single formal-engine "
             "point of failure). Every produced Lean is re-checked by the "
             "pinned kernel. Default 'none' (model-authored Lean only)")
    run.add_argument(
        "--formalizer-provider", choices=("openai-api", "deepseek-api", "anthropic-api"),
        default=None,
        help="attested API provider for --formalizer api|portfolio "
             "(default: deepseek-api)")
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
    run.add_argument(
        "--worker-rounds", type=int, default=1,
        help="model rounds per mechanism branch (1-8): later rounds replay the "
             "lemma ledger, open subgoals, objections, and failed-approach "
             "memory so the worker closes/repairs instead of restating "
             "(default: 1, single-shot)",
    )
    run.add_argument(
        "--hostile-review", type=int, default=0, metavar="N",
        help="run N (0-4) hostile natural-language reviews of the proposed "
             "dependency cone before assembly; passing reviews admit "
             "informal-review evidence (unattested model reviewers collapse "
             "to one lineage, capping at SINGLE review \u2014 T3 needs two "
             "attested independent lineages) (default: 0, off)",
    )
    run.add_argument(
        "--hostile-review-provider", action="append", default=None,
        choices=("openai-api", "deepseek-api", "anthropic-api"),
        help="attested API provider(s) for the hostile reviewers (repeatable); "
             "two DISTINCT providers give two attested lineages \u2014 the "
             "requirement for DOUBLE_INDEPENDENT/T3. Without this flag the "
             "reviewers reuse the main provider runner (unattested for "
             "browser, capping at SINGLE)",
    )
    run.add_argument(
        "--lean-repair-rounds", type=int, default=0, metavar="N",
        help="when a Lean candidate is REJECTED by the pinned kernel, send it "
             "back to the configured --formalizer with the kernel diagnostics "
             "for up to N (0-3) bounded repair rounds; every repaired source "
             "is re-checked by the same pinned kernel and the obligation never "
             "changes (default: 0, off)",
    )
    run.add_argument(
        "--checkpoint-dir", type=Path, default=None,
        help="write a signed within-problem checkpoint (event-log prefix + "
             "graph view hash + remaining budget) after each completed branch "
             "so long runs leave verifiable durable state (default: off)",
    )
    run.add_argument(
        "--resume-from", type=Path, default=None,
        help="consume the latest signed checkpoint for this problem from the "
             "given directory: verified snapshots skip already-attempted "
             "branches and re-book prior spend (full event-chain verification "
             "when continuing the same log; honest warm start otherwise; "
             "fail-closed to a fresh run)",
    )
    run.add_argument(
        "--expert-review", type=Path, default=None,
        help="signed expert significance review JSON (egmra sign-review "
             "expert); a verified approval bound to this problem's locked "
             "claim raises the significance gate S1\u2192S2 \u2014 it never "
             "affects truth",
    )
    run.add_argument(
        "--explore-blocked", action="store_true",
        help="explore interpretation-blocked problems anyway: branch work "
             "(lemmas, falsifiers, experiments) proceeds under the primary "
             "interpretation while release stays blocked and the override is "
             "recorded (default: the selector declines disputed readings)",
    )
    run.add_argument(
        "--formal-target-file", type=Path, default=None,
        help="local .lean file with the community-reviewed formal statement "
             "(fetch one with 'egmra formal-target'); supplied to the worker as "
             "the pinned intended obligation \u2014 read-only prompt context, never "
             "truth authority and never a substitute for the "
             "formal-correspondence review",
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
    campaign.add_argument("--triage", type=Path, default=None,
                          help="drain a triage ranking directory instead of "
                               "--erdos-range: reads triage/rankings/<lane>.json "
                               "(the searcher's own order) and researches each "
                               "problem through the EGMRA loop. This is the "
                               "single-pipeline replacement for run_continuous.py")
    campaign.add_argument("--triage-lane", default="current",
                          help="triage ranking lane to drain (default: 'current' "
                               "= the interleaved allocation queue; e.g. "
                               "'t2_closable', 'tractable_frontier', "
                               "'highest_probability_lean_verification')")
    campaign.add_argument("--max-problems", type=int, default=0,
                          help="cap the number of triage problems drained "
                               "(0 = all ranked problems)")
    campaign.add_argument("--outcome-ledger", type=Path, default=None,
                          help="append each EGMRA outcome (public state + gate "
                               "profile + run id) to this JSONL; honest "
                               "telemetry only, never a release authority")
    campaign.add_argument("--state", type=Path, default=Path("egmra_campaign.json"),
                          help="durable campaign state file (resume by reusing it)")
    campaign.add_argument("--campaign-id", default=None)
    campaign.add_argument("--provider",
                          choices=("browser", "deterministic", "openai-api",
                                   "deepseek-api", "anthropic-api"),
                          default="browser")
    campaign.add_argument("--role", default="prover")
    campaign.add_argument("--worker-rounds", type=int, default=1,
                          help="model rounds per mechanism branch (1-8); see "
                               "'egmra run --worker-rounds'")
    campaign.add_argument("--workers", type=int, default=5,
                          help="bounded worker count (1-5; default 5 — one browser "
                               "tab + one Aristotle formalizer per worker)")
    campaign.add_argument("--budget", type=float, default=50.0)
    campaign.add_argument("--policy", type=Path, default=None)
    campaign.add_argument("--corpus-tex", type=Path, default=None)
    campaign.add_argument("--catalog", type=Path, default=None)
    campaign.add_argument("--event-store", choices=("jsonl", "postgres"), default="jsonl",
                          help="event-log backend for each attempt ('jsonl' or 'postgres')")
    campaign.add_argument("--state-store", choices=("file", "postgres"), default="file",
                          help="campaign lease/checkpoint store: 'file' (signed local JSON) "
                               "or 'postgres' (DB-backed, coordinated across processes; "
                               "uses --dsn or EGMRA_POSTGRES_DSN)")
    campaign.add_argument("--dsn", default=None,
                          help="Postgres DSN for --event-store postgres (or EGMRA_POSTGRES_DSN)")
    campaign.add_argument("--retrieval",
                          choices=("corpus", "arxiv", "crossref", "semanticscholar",
                                   "mathoverflow", "scholarly", "none"),
                          default="corpus",
                          help="literature retrieval source (default: Erdős snapshot); the "
                               "scholarly modes retrieve LIVE per problem statement")
    campaign.add_argument("--oeis", choices=("auto", "offline", "live"), default="auto",
                          help="OEIS lookup mode ('auto', 'offline', or 'live')")
    campaign.add_argument("--lean-project", type=Path, default=None,
                          help="built pinned Lean project (with .lake); enables the formal "
                               "path so worker/Aristotle Lean is re-checked by the kernel")
    campaign.add_argument("--mathlib-commit", default="v4.28.0",
                          help="Mathlib revision recorded in formal candidates")
    campaign.add_argument("--formalizer", choices=("none", "aristotle", "api", "portfolio"),
                          default="none",
                          help="autonomous formalization worker per campaign worker: "
                               "'aristotle' (requires --lean-project + ARISTOTLE_API_KEY), "
                               "'api' (attested --formalizer-provider engine), 'portfolio' "
                               "(aristotle then api); produced Lean is re-checked by the "
                               "pinned kernel. Default 'none'")
    campaign.add_argument("--formalizer-provider",
                          choices=("openai-api", "deepseek-api", "anthropic-api"),
                          default=None,
                          help="attested API provider for --formalizer api|portfolio "
                               "(default: deepseek-api)")
    campaign.add_argument("--lean-repair-rounds", type=int, default=0, metavar="N",
                          help="bounded kernel-feedback repair rounds per rejected Lean "
                               "candidate (0-3); same semantics as 'egmra run "
                               "--lean-repair-rounds'")
    campaign.add_argument("--checkpoint-dir", type=Path, default=None,
                          help="write signed within-problem checkpoints after each "
                               "completed branch; same semantics as 'egmra run "
                               "--checkpoint-dir'")
    campaign.add_argument("--hostile-review", type=int, default=0, metavar="N",
                          help="hostile NL reviews per problem (0-4); same semantics as "
                               "'egmra run --hostile-review'")
    campaign.add_argument("--hostile-review-provider", action="append", default=None,
                          choices=("openai-api", "deepseek-api", "anthropic-api"),
                          help="attested API provider(s) for campaign hostile reviewers "
                               "(repeatable); same semantics as 'egmra run "
                               "--hostile-review-provider'")
    campaign.add_argument("--explore-blocked", action="store_true",
                          help="explore interpretation-blocked problems anyway (release "
                               "stays blocked); same semantics as 'egmra run "
                               "--explore-blocked'")
    campaign.add_argument("--reviews-dir", type=Path, default=None,
                          help="directory of per-problem signed review artifacts "
                               "(intent-<problem_id>.json / correspondence-<problem_id>.json "
                               "/ expert-<problem_id>.json, from 'egmra sign-review'); "
                               "a problem with a valid signed intent can RELEASE from a "
                               "campaign exactly like 'egmra run' \u2014 problems without "
                               "artifacts stay evidence-grade as before")
    campaign.add_argument("--auto-rerank", action="store_true",
                          help="continuously rerank the PENDING queue from observed "
                               "outcomes after each completed problem (progress promotes, "
                               "repeated dead-ends demote; searcher order is the "
                               "tie-break) \u2014 a search-order preference only, never a "
                               "truth or release signal")
    campaign.add_argument("--refresh-ranking-after", action="store_true",
                          help="after the campaign completes, aggregate its outcome "
                               "ledger into a calibration report and rebuild the "
                               "corpus-wide searcher ranking with it (capped "
                               "weak-evidence posterior input, provenance recorded); "
                               "fail-open \u2014 a refresh error never affects outcomes")
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

    signrev = sub.add_parser(
        "sign-review",
        help="sign an intent or formal-correspondence review certificate with the review key")
    signrev_sub = signrev.add_subparsers(dest="review_kind", required=True)

    sri = signrev_sub.add_parser(
        "intent", help="sign an intent-review certificate bound to a resolved problem")
    sri_selector = sri.add_mutually_exclusive_group(required=True)
    sri_selector.add_argument("--erdos", type=int, default=None,
                              help="Erdős problem number to resolve from the corpus snapshot")
    sri_selector.add_argument("--statement", default=None,
                              help="verbatim problem statement to review")
    sri_selector.add_argument("--statement-file", type=Path, default=None,
                              help="path to a file containing the problem statement")
    sri_selector.add_argument("--fixture", default=None,
                              help="bundled regression fixture id to review")
    sri.add_argument("--corpus-tex", type=Path, default=None,
                     help="override the corpus TeX snapshot used by --erdos")
    sri.add_argument("--catalog", type=Path, default=None,
                     help="override the problem catalog used by --erdos")
    sri.add_argument("--reviewer-id", default="independent-intent-reviewer",
                     help="identity of the independent reviewer signing the certificate")
    sri.add_argument("--verdict", choices=("approved", "rejected"), default="approved",
                     help="the reviewer's verdict (default: approved)")
    sri.add_argument("--certificate-id", default=None,
                     help="certificate id (default: intent-<problem_id>)")
    sri.add_argument("--output", "-o", type=Path, required=True,
                     help="destination for the signed certificate (created 0600; never overwritten)")
    sri.set_defaults(func=cmd_sign_review_intent)

    src = signrev_sub.add_parser(
        "correspondence",
        help="sign a formal-correspondence certificate binding a Lean declaration to a claim")
    src.add_argument("--intent-review", type=Path, required=True,
                     help="the signed intent-review JSON whose certificate id + informal-claim "
                          "hash this correspondence binds")
    src.add_argument("--declaration", required=True,
                     help="the Lean declaration name the kernel-checked candidate establishes")
    src.add_argument("--expected-type", required=True,
                     help="the exact Lean type the declaration proves (must match the "
                          "kernel-checked candidate's elaborated type)")
    src.add_argument("--notation-map", default=None,
                     help="optional notation/definition map text bound into the certificate")
    src.add_argument("--reviewer-id", default="independent-formal-reviewer",
                     help="identity of the independent reviewer signing the certificate")
    src.add_argument("--verdict", choices=("approved", "rejected"), default="approved",
                     help="the reviewer's verdict (default: approved)")
    src.add_argument("--certificate-id", default=None,
                     help="certificate id (default: formal-correspondence-<declaration>)")
    src.add_argument("--output", "-o", type=Path, required=True,
                     help="destination for the signed certificate (created 0600; never overwritten)")
    src.set_defaults(func=cmd_sign_review_correspondence)

    sre = signrev_sub.add_parser(
        "expert",
        help="sign an expert SIGNIFICANCE review (S1\u2192S2); a human judgement "
             "that a result fully resolves the stated problem \u2014 never a "
             "correctness authority")
    sre_selector = sre.add_mutually_exclusive_group(required=True)
    sre_selector.add_argument("--erdos", type=int, default=None,
                              help="Erd\u0151s problem number to resolve from the corpus snapshot")
    sre_selector.add_argument("--statement", default=None,
                              help="verbatim problem statement reviewed")
    sre_selector.add_argument("--statement-file", type=Path, default=None,
                              help="path to a file containing the problem statement")
    sre_selector.add_argument("--fixture", default=None,
                              help="bundled regression fixture id reviewed")
    sre.add_argument("--corpus-tex", type=Path, default=None,
                     help="override the corpus TeX snapshot used by --erdos")
    sre.add_argument("--catalog", type=Path, default=None,
                     help="override the problem catalog used by --erdos")
    sre.add_argument("--reviewer-id", default="independent-expert-reviewer",
                     help="identity of the human expert signing the certificate")
    sre.add_argument("--verdict", choices=("approved", "rejected"), default="approved",
                     help="the expert's verdict (default: approved)")
    sre.add_argument("--significance", required=True,
                     help="the expert's written statement of why the result fully "
                          "resolves the problem (required; empty approvals are refused)")
    sre.add_argument("--certificate-id", default=None,
                     help="certificate id (default: expert-<problem_id>)")
    sre.add_argument("--output", "-o", type=Path, required=True,
                     help="destination for the signed certificate (created 0600; never overwritten)")
    sre.set_defaults(func=cmd_sign_review_expert)

    show = sub.add_parser("policy-show", help="print the signed feature policy")
    show.add_argument("--policy", type=Path, default=None)
    show.set_defaults(func=cmd_policy_show)

    calibrate = sub.add_parser(
        "calibrate",
        help="aggregate outcome ledgers into an honest calibration report "
             "(observed frequencies; never a release authority)")
    calibrate.add_argument("--outcomes", type=Path, action="append", required=True,
                           help="outcome-ledger JSONL path (repeatable)")
    calibrate.add_argument("--output", "-o", type=Path, default=None,
                           help="write the report JSON here (refuses overwrite); "
                                "prints to stdout when omitted")
    calibrate.set_defaults(func=cmd_calibrate)

    refresh = sub.add_parser(
        "refresh-ranking",
        help="rebuild the corpus-wide searcher ranking with EGMRA outcome "
             "frequencies as a capped weak-evidence posterior input "
             "(provenance recorded in the ranking)")
    refresh.add_argument("--outcomes", type=Path, action="append", required=True,
                         help="outcome-ledger JSONL path (repeatable)")
    refresh.add_argument("--searcher-root", type=Path, default=Path.cwd(),
                         help="repo root containing erdos_searcher.py and the corpus")
    refresh.add_argument("--searcher-output", type=Path, default=Path("triage"),
                         help="searcher output root (triage/) whose rankings are rebuilt")
    refresh.add_argument("--snapshot-date",
                         default=datetime.now(timezone.utc).date().isoformat())
    refresh.add_argument("--top-k", type=int, default=25)
    refresh.set_defaults(func=cmd_refresh_ranking)

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

    formal_target = sub.add_parser(
        "formal-target",
        help="fetch the community-reviewed Lean statement for an Erdős problem "
             "(formal-conjectures repository) for use with 'run --formal-target-file'")
    formal_target.add_argument("--erdos", type=int, required=True,
                               help="Erdős problem number")
    formal_target.add_argument("--ref", default=None,
                               help="git ref to pin (immutable bench tag recommended; "
                                    "default 'main' is mutable and marked "
                                    "non-reproducible)")
    formal_target.add_argument("--output", type=Path, default=None,
                               help="write the fetched .lean statement to this path "
                                    "(refuses to overwrite)")
    formal_target.set_defaults(func=cmd_formal_target)

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
        json.JSONDecodeError, RuntimeError,
    ) as exc:
        print(json.dumps({"error": type(exc).__name__, "detail": str(exc)}), file=sys.stderr)
        return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
