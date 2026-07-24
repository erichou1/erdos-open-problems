# Phase 3 static inventory and reachability audit

Date: 2026-07-13  
Scope: the claimed EGMRA implementation under `egmra/`, `config/egmra_policy.json`, package metadata, repository entry points, and tests.  
Method: read-only source/import inspection. No test or production file was changed and no test suite was executed for this phase.

## Executive result

The tree is a large, internally consistent prototype library, not a normally reachable implementation of the claimed autonomous research system.

* There are **92 non-`__init__` source modules**, **21 production `__init__.py` files**, and **10,839 non-test Python LOC**. The test package has **21 `test_*.py` files**, **3,117 LOC**, and **241 statically counted `test_` functions**.
* The repository has **no `pyproject.toml`, `setup.py`, `setup.cfg`, console-script declaration, web/API server, worker service, or plugin entry point** for EGMRA. `requirements.txt:1-4` lists dependencies for the pre-existing repository and no EGMRA packaging/test metadata.
* Outside `egmra/`, the only non-test imports of the new package are `promote_verified_run.py:16-17`, which reach `egmra.m0`, `egmra.policy`, and their hashing dependency. No existing scheduler, searcher, verified pipeline, browser runner, or continuous worker imports the EGMRA orchestrator.
* Explicitly running `python -m egmra.cli` makes only **33/92 leaf modules import-reachable**. The CLI is a bundled-fixture demonstration (`egmra/cli.py:28-55`), not an entry point for repository Erdős problems or the existing verified pipeline. **58/92 leaf modules are in neither the legacy-production nor CLI transitive import closure.**
* The CLI loop does not execute most of the architecture it names. It ignores its `budget` and effective `runner`, discards cold-pass output, hardcodes acquisition, uses a deterministic worker, and manufactures a complete referee attack report from one Boolean probe result (`egmra/orchestrator/loop.py:148-168,189-205,258-269`). Search, selection, control, Lean, OEIS, learning, blackboard, revocation, and evaluation engines are not called by that loop.
* Several claimed production integrations are protocols, injected callables, constant registries, or fail-fast placeholders: `PostgresEventStore.connect()` only raises (`egmra/m2.py:31-54`), `ContainerSandbox.run()` only raises (`egmra/compute/sandbox.py:112-133`), solver backends are protocols (`egmra/compute/backends.py:33-48`), and real provider execution is only a caller-supplied callable (`egmra/agents/runner.py:60-91`).
* The event log is durable only for event envelopes, not the mathematical state. Graph events persist IDs/status metadata but omit claim formulae, evidence bodies, certificates, and object snapshots (`egmra/truth/graph.py:59-179`); `EpistemicGraph.__init__` always creates empty dictionaries and never replays the loaded log (`egmra/truth/graph.py:45-55`). The documented “authoritative event log” therefore cannot reconstruct its claimed disposable views.
* The tests are extensive unit/contract tests, but their integration slice is deterministic and injected. In particular, Lean “kernel” success is a lambda returning a success string (`egmra/tests/test_acceptance.py:172-180`; `egmra/tests/test_lean.py:39-48`), OEIS HTTP uses a fake fetcher (`egmra/tests/test_oeis.py:97-110`), Postgres is tested by expecting `RuntimeError` (`egmra/tests/test_m2_scale.py:28-32`), and the acceptance test claiming entry-point reachability merely calls `PolicyEnforcer.require()` with three string labels (`egmra/tests/test_acceptance.py:54-59`).

Classification used below:

* **production-integrated** — reached by an existing repository production entry point.
* **CLI-fixture** — reached only through the standalone deterministic fixture CLI.
* **library-only** — implemented local library, but not normally called by production or the CLI.
* **test-only/export-only** — imported or instantiated by tests or re-exporting `__init__.py` files, with no operational caller.
* **mock/fake** — deterministic/injected substitute presented as an integration surface.
* **incomplete/disabled** — protocol, constant/status registry, fail-fast placeholder, or feature disabled in the checked-in policy.
* **duplicate** — overlapping authority or implementation with another path, without a single shared operational decision.

## Reproducible inventory

Run from `/Users/eric/workspace/erdos/erdos_problems`:

```sh
# All non-test EGMRA Python files, including package initializers.
find egmra -type f -name '*.py' -not -path 'egmra/tests/*' \
  -not -path '*/__pycache__/*' | sort | wc -l
# => 113

# Non-test LOC.
find egmra -type f -name '*.py' -not -path 'egmra/tests/*' \
  -not -path '*/__pycache__/*' -print0 | sort -z | xargs -0 wc -l | tail -n 1
# => 10839 total

# Production package initializers; 113 - 21 = 92 leaf/source modules.
find egmra -type f -name '__init__.py' -not -path 'egmra/tests/*' | sort | wc -l
# => 21

# Tests and test LOC.
find egmra/tests -type f -name 'test_*.py' | wc -l
# => 21
find egmra/tests -type f -name 'test_*.py' -print0 | sort -z | xargs -0 wc -l | tail -n 1
# => 3117 total
rg -n '^def test_' egmra/tests | wc -l
# => 241

# Metadata/entry-point search.
find . -maxdepth 2 -type f \( -name pyproject.toml -o -name setup.py \
  -o -name setup.cfg -o -name tox.ini -o -name pytest.ini -o -name MANIFEST.in \) -print
# => no output
rg -n 'console_scripts|entry_points|FastAPI|Flask|APIRouter|uvicorn|grpc' egmra requirements.txt
# => no output

# All imports from outside egmra (excluding audit text).
rg -n 'from egmra|import egmra' --glob '*.py' --glob '!egmra/**' --glob '!audit/**' .
# => promote_verified_run.py:16-17 and a conditional test import in tests/test_proof_pipeline.py:16

# Checked-in status of the claimed implementation at audit time.
git status --short -- egmra config/egmra_policy.json promote_verified_run.py \
  aristotle_verifier.py tests/test_proof_pipeline.py
# => egmra/ and config/egmra_policy.json untracked; three legacy files modified

# Suspicious implementation scan.
rg -n 'except (Exception|BaseException)|except\s*:|NotImplemented|TODO|FIXME|raise RuntimeError' \
  egmra --glob '*.py' --glob '!egmra/tests/**'
rg -n 'mock|fake|deterministic|local/CI|requires Docker|requires a database|injected|Protocol' \
  egmra --glob '*.py' --glob '!egmra/tests/**'
```

The 33-module CLI and two-leaf legacy closures, plus the 58-module “neither” set, were computed by parsing `ast.Import`/`ast.ImportFrom`, resolving relative imports, and taking transitive closure from `egmra.cli` and from top-level repository Python imports. The exact 58-module set is recorded below.

## Normal reachability and side-effect map

| Root | Transitive production behavior | Persistence / external side effects | Result |
|---|---|---|---|
| Existing verified pipeline / Aristotle promotion | `promote_verified_run.py:16-17` -> `egmra.m0.PromotionGuard` -> `egmra.policy.PolicyEnforcer`; hashing loads transitively | May rewrite the pre-existing mutable `manifest.json` and publish through legacy code (`promote_verified_run.py:61-105`) | **Narrow production-integrated safety guard only.** No EGMRA truth graph, orchestrator, release certificate, retrieval, search, Lean service, or learning path is involved. |
| `python -m egmra.cli run` | `cli.cmd_run` -> fixture -> `orchestrator.research` -> intake, local retrieval, subprocess compute, in-memory graph, generated gate/certificate (`egmra/cli.py:43-57`) | Appends JSONL under `EgmraConfig.events_dir`, default `egmra_runs` (`egmra/config.py:24-32`; `egmra/cli.py:51`; `egmra/truth/events.py:173-216`). Compute artifacts remain in memory because `ComputeService.store_dir` defaults to `None` (`egmra/compute/service.py:42-47,69-70`). | **CLI-fixture demonstration.** No arbitrary problem/run input; the corpus is a one-record dummy (`egmra/cli.py:48-50`). |
| `python -m egmra.cli verify-events` | Loads JSONL and verifies hashes/HMAC (`egmra/cli.py:67-71`) | Read-only against requested event file | Operational integrity checker, but it cannot validate/reconstruct omitted graph object state. |
| `python -m egmra.cli policy-show` / `fixtures` | Prints policy fields or five constants (`egmra/cli.py:60-77`; `egmra/eval/datasets.py:42-54`) | stdout | Status/display only. |
| Importing `egmra.<package>` in tests | Package `__init__.py` re-exports many leaf symbols | Usually none until tests instantiate objects | Re-export reachability is not an operational caller. |

No code in `run_verified_pipeline.py`, `run_continuous.py`, `problem_queue.py`, `erdos_searcher.py`, `run_verified_range.py`, or `proof_pipeline.py` imports the EGMRA orchestrator. README operational instructions continue to name the legacy pipeline (`README.md:50-55,91,118-124,148-153`).

## Significant findings

### S1 — The “signed” feature policy accepts unsigned promotion-enabling documents

`config/egmra_policy.json:18-19` has an empty signature and self-declared `"unsigned-default"` trust. `load_policy()` verifies only when the signature string is nonempty; an unsigned document is returned without signature validation (`egmra/policy/__init__.py:141-164`). `PolicyEnforcer.require()` checks only Boolean flags, not signature presence or trust (`egmra/policy/__init__.py:171-212`). Thus an unsigned policy with `promotion: true` enables the supposedly non-overridable release feature.

The tests normalize this behavior: `test_promotion_guard_allows_when_signed_enabled` constructs a `FeaturePolicy` with both promotion flags true but no signature and expects success (`egmra/tests/test_m0_safety.py:25-29`). The default-disabled file prevents promotion by default, but the claimed signed-policy invariant is absent. `PromotionGuard.check()` even returns the constant message “promotion enabled by signed policy” without testing a signature (`egmra/m0.py:41-48`).

The checked-in policy also disables the capabilities needed for the claimed live system: continuous scheduling, parallel workers, Lean execution, external prover routing, automated external evidence, promotion, and formal promotion are all false (`config/egmra_policy.json:4-8,12-13`). This is correctly fail-closed for the default run, but means those production capabilities are disabled.

### S2 — Event sourcing is not replayable or authoritative

`EventLog` loads and verifies JSONL envelopes (`egmra/truth/events.py:110-169,220-235`) and appends an event with IDs, version maps, hashes, and reasons (`egmra/truth/events.py:173-216`). Graph operations, however, persist neither the entity snapshots nor enough event payload to recreate them:

* `PROBLEM_FROZEN` stores the problem ID and optional source hash, not the `Problem` record (`egmra/truth/graph.py:59-70`).
* `INTERPRETATION_ADDED` stores only the interpretation ID/reason (`egmra/truth/graph.py:72-85`).
* `CLAIM_PROPOSED` stores only claim ID/version/reason, omitting formula, assumptions, dependencies, scope, and interpretation (`egmra/truth/graph.py:115-160`).
* `EVIDENCE_ATTACHED` stores evidence/claim IDs and artifact hashes, omitting evidence findings and validator inputs (`egmra/truth/graph.py:162-180`).
* Certificates are stored in dictionaries but their events carry only certificate IDs and reason codes (`egmra/truth/graph.py:89-111`).

`EpistemicGraph(log)` always initializes empty dictionaries and has no reducer/replay method (`egmra/truth/graph.py:45-55`). `materialize_sqlite()` and `manifest_projection()` claim disposable rebuildability but read those live in-memory dictionaries (`egmra/truth/views.py:18-22,51-77,84-104`). A process restart preserves an envelope history but loses the mathematical state, so JSONL is not a durable substitute for the claimed event database.

Additionally, the default event/release HMAC keys are public constants (`egmra/truth/events.py:22-24,104-107`; `egmra/release/certificate.py:18,69-82`), and append has no file lock, compare-and-swap, fsync, or transaction (`egmra/truth/events.py:191-216`). This is local demonstration persistence, not a concurrent authoritative store.

### S3 — The orchestrator is a fixture script with hardcoded success semantics

`research()` advertises a seventeen-step loop, but its implementation omits the search/control architecture:

* `budget` is accepted and never read. `runner` defaults to `DeterministicRunner` and is never used after assignment (`egmra/orchestrator/loop.py:148-168`).
* The return from `worker.cold_pass()` is discarded (`egmra/orchestrator/loop.py:189-191`).
* Retrieval is a fresh in-memory lexical index over the caller's list; the CLI supplies one synthetic theorem with one-letter URI/version/hash (`egmra/orchestrator/loop.py:193-202`; `egmra/cli.py:48-50`). The packet is not given to an import auditor before work.
* Acquisition is the constant `True`; no `selection`, `search.controller`, `search.programs`, compute bands, leases, throttling, or parallel worker policy is invoked (`egmra/orchestrator/loop.py:204-205`).
* The deterministic worker proposes the requested goal formula itself and optionally converts one finite subprocess result into evidence (`egmra/orchestrator/loop.py:67-119`). The CLI special-cases any `_isprime` predicate to the constant body `True` (`egmra/cli.py:31-35`).
* Every one of ten adversarial attacks is marked passed unless the single intake `probe_failed` Boolean applies to `target_diff` or `countermodel_search`; no attack implementation runs (`egmra/orchestrator/loop.py:258-269`). `dependency_trace` is declared discharged as a constant string.
* Intent is auto-approved for a single deterministic interpretation and the reviewer/method list is hardcoded (`egmra/orchestrator/loop.py:207-222`).
* Status defaults to `status_uncertain` with no sources (`egmra/corpus/status.py:82-93`) but the loop still performs deep work and can issue a release certificate; the status resolution is not persisted or returned (`egmra/orchestrator/loop.py:177-205,224-295`).
* Gate input hardcodes `correspondence_cert=None`, `non_vacuous=True`, and `replay_reports=[]`; the CLI's actual replay is not passed to the reproducibility gate (`egmra/orchestrator/loop.py:277-293`).

The loop is therefore a deterministic component demonstration, not orchestration of the modules catalogued in the design.

### S4 — Real adapters are absent, injected, or disconnected

* `AttestedRunner` is an adapter around an arbitrary caller-supplied `call` object; there is no OpenAI/Anthropic/Gemini implementation, authentication, retry, response validation, or production instantiation (`egmra/agents/runner.py:60-91`). The loop's runner is unused.
* `ModelParser` similarly wraps an arbitrary callable and is not configured by `EgmraConfig` or the CLI (`egmra/intake/statement_ir.py:264-294`). Default parsing is two regex/cue parsers.
* `LeanService` defaults to no kernel runner (`egmra/lean/service.py:168-179,276-285`), performs “elaboration” and type matching with regex/string hashes (`egmra/lean/service.py:55-72,187-198,234-240`), and treats any caller-supplied `kernel_result=True` or injected result string `"kernel_verified"` as a kernel pass (`egmra/lean/service.py:276-285`). Any nonempty `proof_artifact` makes `compare_statements()` return `equivalent` without checking it (`egmra/lean/service.py:287-293`). Nothing connects this class to the repository's real `lean_verify.py`.
* `AristotleRouting` returns request objects and constant policy/pipeline tuples; it executes none of the listed stages (`egmra/lean/aristotle_routing.py:48-95`). The real `aristotle_verifier.py` calls the legacy `promote_verified_run`, not this module (`aristotle_verifier.py:430-447`).
* SAT/SMT/CAS are protocols; only small exact/model/RUP helpers are implemented (`egmra/compute/backends.py:18-109`).
* `PostgresEventStore` contains DDL and a `connect()` that always raises (`egmra/m2.py:31-54`). `M2Assembly` uses the local JSONL store and subprocess sandbox (`egmra/m2.py:78-99`).
* `ContainerSandbox.run()` always raises and only prints a sample Docker command (`egmra/compute/sandbox.py:112-133`). The default subprocess sandbox monkeypatches Python `socket`; it is not an OS network namespace, and its resource setup broadly swallows errors (`egmra/compute/sandbox.py:23-47,73-109`).
* `OEISClient` contains a real `requests.get` fallback (`egmra/oeis/client.py:112-136`), but the default configuration is offline (`egmra/config.py:27-28`), the orchestrator never constructs the client, and tests use an injected fake fetcher.

### S5 — “Passed,” “independent,” “immutable,” and “durable” labels often lack their advertised semantics

Examples found by the constant/no-op scan:

* Missing executable boundary/counterexample probes return `passed=True` while explicitly saying they were not run (`egmra/intake/probes.py:111-151`). A source to which no paraphrase/mutation rule applies also passes trivially (`egmra/intake/probes.py:67-96`). These values can help auto-approve intent.
* `ComputeService.replay()` reuses the same code, host Python, and default `SubprocessSandbox`; “independent” is only a caller-supplied label included in an environment hash (`egmra/compute/service.py:27-28,111-127`). Acceptance test 11 passes `environment_label="independent"` and calls that independent replay (`egmra/tests/test_acceptance.py:161-169`).
* `SourcePacket` is a mutable dataclass containing lists/dicts despite its “immutable” description. Its hash omits packet ID, query text/results, coverage databases/gaps, unresolved conflicts, snapshot time, and reentry reason (`egmra/retrieval/packet.py:50-103`).
* `LongTermMemory` is only in-memory lists/dicts with Boolean field-presence admission (`egmra/learning/memory.py:29-100`); no persistence, graph linkage, revocation feed, or orchestrator caller exists.
* `ProgressLedger.signal_value()` returns zero in both branches for every input, so it is a no-op status function (`egmra/eval/progress.py:31-46`). The evaluation package contains schemas/guards but no experiment runner or stored results.
* `RoleLayout`, `ServiceTopology`, and `ServiceContract` describe counts/endpoints/protocols; they do not start processes, perform health checks, or route requests (`egmra/orchestrator/roles.py:13-37`; `egmra/topology.py:12-40`; `egmra/services.py:14-79`).
* `ImportAuditor` calls a desired conclusion a logical consequence when its lowercase word tokens are a subset of theorem-conclusion tokens (`egmra/retrieval/service.py:78-113`). This is lexical status, not a proof/application audit.
* `enumerate_transform_paths()` catches every exception and silently drops the path (`egmra/oeis/matching.py:104-125`). Other broad catches are mostly conservative fail-closed checks, but the sandbox resource catch can silently weaken isolation.

### S6 — Tests demonstrate local contracts, not production integration

Static test inventory is broad, but the strongest claims are not exercised through production wiring:

* The four end-to-end orchestrator tests use `DeterministicWorker`, a local one-record corpus, `tmp_path`, Python predicates, and a policy with promotion disabled (`egmra/tests/test_orchestrator.py:29-99`). They do not use a model, search controller, Lean, OEIS, scheduler, Postgres, container runtime, real literature, or existing Erdős pipeline.
* The CLI tests call `main([...])` directly and redirect events to `tmp_path`; they establish fixture behavior only (`egmra/tests/test_cli.py:38-61`).
* The “18 acceptance tests” are mostly direct unit predicates. Acceptance 1 does not inspect actual entry points (`egmra/tests/test_acceptance.py:54-59`); acceptance 5 never reloads/reconstructs the graph (`egmra/tests/test_acceptance.py:87-97`); acceptance 10 uses an in-memory fake clock (`egmra/tests/test_acceptance.py:151-158`); acceptance 12 uses a success lambda instead of Lean (`egmra/tests/test_acceptance.py:172-185`); acceptance 18 checks a two-Boolean function rather than a paired evaluation (`egmra/tests/test_acceptance.py:231-234`).
* M2 tests explicitly treat “Postgres always raises” and “container object reports policy string” as coverage (`egmra/tests/test_m2_scale.py:28-40`).
* The only test crossing into the pre-existing proof pipeline uses a canned `_Passing` runner and only verifies default policy blockage (`egmra/tests/test_m0_safety.py:84-117`). It does not run any EGMRA research subsystem.

The tests are valuable for local data-structure and fail-closed invariants, but their count must not be read as evidence that 120 architectural requirements or real integrations are operational.

### S7 — Duplicate/disconnected decision authorities

There are two promotion systems:

1. `egmra.m0.PromotionGuard`, used by the legacy `promote_verified_run.py` before the legacy `verification.evaluate_gate` (`promote_verified_run.py:25-38,67-89`); and
2. `egmra.release.PromotionPolicy`, used only by the CLI-fixture orchestrator (`egmra/release/policy.py:26-62`; `egmra/orchestrator/loop.py:293`).

The EGMRA release certificate is not consumed by the legacy publisher, and the legacy gate result is not an EGMRA truth-graph event. These are duplicate/disconnected promotion authorities rather than one integrated release path. There are also separate `ProvenanceError` classes in `egmra/provenance/hashing.py:20` and `egmra/provenance/rules.py:32`, and service protocols duplicated between `egmra/services.py`, concrete packages, and `egmra/m2.py` without a runtime service registry.

## Package/module inventory

All 92 leaf modules are named below. `__init__.py` files mostly re-export the listed symbols; such re-exports are public surfaces, not evidence of an operational caller.

| Package / modules | Purpose and public interface | Production callers, dependencies, config, persistence, side effects | Tests / reachability / classification |
|---|---|---|---|
| `egmra/__init__.py` | Package documentation and `__version__ = "0.1.0"` (`egmra/__init__.py:1-20`). | No packaging metadata consumes the version. | Import surface only; **incomplete packaging**. |
| Root: `cli.py`, `config.py` | `cli`: `cmd_run`, `cmd_policy_show`, `cmd_verify_events`, `cmd_fixtures`, `build_parser`, `main`. `config`: `EgmraConfig.load`, public config, env-only secret accessor. | CLI reads JSON/env and writes fixture event JSONL. No console-script entry. Config fields for artifact/OEIS/Lean are not wired into services (`egmra/config.py:24-59`). | `test_cli.py`; `cli` is **CLI-fixture**, `config` CLI-only. |
| Root: `m0.py` | `PromotionGuard`, evidence precedence, legacy quarantine records, `PromotionTelemetry`. | `PromotionGuard` is the only EGMRA class called by existing production (`promote_verified_run.py:16,36`). Quarantine and telemetry have no production caller/persistence. | `test_m0_safety.py`, `test_acceptance.py`; guard **production-integrated**, remainder **library/test-only**. |
| Root: `m2.py` | `EventStore` protocol, nonfunctional `PostgresEventStore`, local content-addressed object store, `M2Assembly`. | Writes local object files if explicitly used; no normal caller. Postgres/container paths do not execute. | `test_m2_scale.py` only; **test-only, incomplete scale adapter**. |
| Root: `design_status.py`, `risks.py` | Constant `DesignChoice` and `Risk` registries plus lookup functions. | No caller outside tests; no persistence or enforcement. | `test_meta.py`; **status-only/test-only**. |
| Root: `services.py`, `topology.py` | Service protocol/schema registry; ten topology description strings and endpoint registration. | No service construction, discovery, health, transport, or production caller. | `test_meta.py`; **status/protocol-only**. |
| `agents`: `authorities.py` | Seven `Authority` records, `authority()`, `is_forbidden()`. | Re-exported only; orchestrator does not use authority checks. | `test_agents.py`; **export/test-only**. |
| `agents`: `profiles.py` | `MethodProfile`, diversity comparisons, `DiversityAudit`. | Re-exported only; no scheduler/governor caller. | `test_agents.py`; **export/test-only**. |
| `agents`: `prompts.py` | Constant role prompts, `role_prompt`, `role_prompt_hash`. | Re-exported only; no model run consumes them. | `test_agents.py`; **export/test-only**. |
| `agents`: `runner.py` | `ModelRunner` protocol, `RunnerResponse`, `DeterministicRunner`, `AttestedRunner`. | Imported by orchestrator; deterministic runner is assigned but not called. Attested adapter requires injected callable and has no production instantiation. | `test_agents.py`, `test_acceptance.py`; **CLI-imported mock/incomplete real adapter**. |
| `comms`: `human.py`, `render.py` | In-memory `InterventionLog`; certificate/human summary rendering. | No orchestrator/release caller; no intervention event persistence. | `test_meta.py`; **test-only**. |
| `compute`: `spec.py` | Immutable-ish `ExperimentSpec` and content hashes. | Used by CLI/worker/service/sandbox. | `test_compute.py`, orchestrator/eval tests; **CLI-fixture utility**. |
| `compute`: `sandbox.py` | `SubprocessSandbox`, nonfunctional `ContainerSandbox`, `SandboxResult`. | Subprocess/temp files/process execution on CLI; optional resource limits and socket monkeypatch. Container always raises. | `test_compute.py`; local sandbox **CLI-fixture**, container **incomplete**. |
| `compute`: `artifact.py`, `service.py` | Artifact classifications, replay/certificate reports; synchronous in-memory job/artifact service. | CLI worker executes subprocess twice. Optional artifact persistence exists but CLI leaves `store_dir=None`. Checker is injected and broadly caught fail-closed. | `test_compute.py`, `test_acceptance.py`; **CLI-fixture/local library**. |
| `compute`: `backends.py` | `SolverResult`, SAT/SMT/CAS protocols, small model/RUP/exact arithmetic checkers. | No orchestrator caller or concrete solver. | `test_compute.py`; **library/test-only, incomplete adapters**. |
| `control`: `leases.py`, `throttle.py`, `parallel.py`, `recovery.py`, `congestion.py` | In-memory leases, exponential backoff state, static parallel/serialization rules, recovery table, congestion price. | No scheduler/orchestrator caller; no durable lease, provider quota, queue, worker, or event integration. | `test_control.py`, acceptance 9-10; **test-only/in-memory substitutes**. |
| `corpus`: `status.py` | Snapshot/status records and `reconcile_status`. | Called by CLI loop, but no external status source; default empty claims produce uncertainty and the result is not persisted. | `test_retrieval.py`; **CLI-fixture status logic, incomplete integration**. |
| `eval`: `datasets.py` | Five local elementary fixtures and four benchmark description records. | CLI fixture source. External datasets are strings/fetch instructions only. | `test_eval.py`, CLI tests; fixtures **CLI-only**, benchmark integration **incomplete**. |
| `eval`: `levels.py`, `metrics.py`, `progress.py`, `protocol.py`, `stats.py`, `ablations.py` | Difficulty/track constants; metric dataclasses; progress counter; frozen eval/ablation schemas; statistical guard functions; preregistration registry. | No evaluation runner, storage, paired baseline executor, grader, or production caller. | `test_eval.py`, acceptance 18; **test/status-only**. |
| `intake`: `statement_ir.py` | IR dataclasses; regex/cue `GrammarParser` and `ClauseParser`; injected `ModelParser`; reconciliation/backtranslation. | CLI uses deterministic parsers. Different `parser_id` strings are the only enforced independence condition (`egmra/intake/statement_ir.py:330-357`). | `test_intake.py`; **CLI-fixture parser**, real model parser **incomplete**. |
| `intake`: `interpretation.py`, `probes.py`, `contract.py` | Mutable interpretation lattice, regex/predicate probes, `ProblemContract` builder. | Called by CLI loop. No durable source record beyond hashes/event IDs; missing executable probes pass. | `test_intake.py`, acceptance 7; **CLI-fixture with status-without-semantics gaps**. |
| `lean`: `service.py` | Lean environment/goal/certificate values; regex scanners; injected kernel/checker API. | No orchestrator or real Lean caller; no default runner. Caller-controlled success and string hashing. | `test_lean.py`, acceptance 12-13; **test-only fake/incomplete integration**. |
| `lean`: `aristotle_routing.py` | Request/attestation records and constant sandbox/admission pipeline. | No Aristotle or legacy verifier caller. | `test_lean.py`; **status-only/test-only**. |
| `lean`: `blueprint.py`, `coverage.py`, `hardening.py`, `missing_library.py`, `proof_state.py`, `sentinels.py`, `sync.py`, `target_package.py` | Local dataclasses/algorithms for formal holes, risk-weighted coverage, certificate hardening, checklist workflow, PUCT/cache, sentinel scores, informal-formal links, target choice. | No production/CLI orchestration caller; all state in memory. `hardening.py` calls `service.py` certificate fields but not a kernel. | `test_lean.py`, `test_eval.py`; **library/test-only**. |
| `learning`: `memory.py`, `expert_iteration.py`, `calibration.py` | In-memory typed memory buckets, field-presence training-example admission, calibration math/ledger. | No persistence, training job, model update, graph revocation, or orchestrator caller. | `test_learning.py`; **test-only/in-memory substitute**. |
| `models`: `registry.py` | In-memory bake-off records and pin-best by caller-provided score. | No bake-off executor, config persistence, gateway, or production caller. | `test_meta.py`; **test/status-only**. |
| `oeis`: `client.py` | Offline cache + optional `requests` query; submissions forbidden. | Real HTTP function exists but is never reached by orchestrator/CLI; default offline. Optional JSON cache writes. | `test_oeis.py` fake fetcher; **library-only, real path untested/disconnected**. |
| `oeis`: `transforms.py`, `matching.py` | Twenty local sequence transforms, match scoring, held-out checks, conjecture descriptor. | No orchestrator caller; transform failures can be silently dropped. | `test_oeis.py`, acceptance 16; **library/test-only**. |
| `orchestrator`: `loop.py` | `Worker` protocol, deterministic worker, `ResearchResult`, `research`. | Standalone fixture CLI only; writes event JSONL and executes local subprocess compute. Does not call most architecture modules. | `test_orchestrator.py`, `test_eval.py`; **CLI-fixture/mock orchestration**. |
| `orchestrator`: `checkpoint.py`, `roles.py` | Checkpoint/resume comparison records; constant four-role/five-service layout. | Imported through package `__init__` by CLI but never called by CLI loop; checkpoint not persisted and cannot restore graph/state. | `test_orchestrator.py`, acceptance 5; **test/status-only**. |
| `policy`: `__init__.py` | Feature policy schema/sign/load/verify and `PolicyEnforcer`. | Reached by legacy promotion and CLI. Reads JSON/env; enforcement audit is in-memory list only. Unsigned policy accepted. | `test_foundations.py`, `test_m0_safety.py`; **production-integrated but signature invariant incomplete**. |
| `provenance`: `hashing.py` | Canonical JSON, SHA-256, content IDs, Merkle root. | Common dependency; reached by legacy guard and CLI. No side effects. | `test_foundations.py`; **production-integrated utility**. |
| `provenance`: `stage_identity.py`, `rules.py` | Caller-supplied model/stage identity and cache bindings; field-presence provenance checks. | Stage identity imported transitively by unused runner; rules have no normal caller. | `test_foundations.py`, acceptance 2-4; **test/library-only**. |
| `release`: `gates.py` | Six-axis `FiveGateResult` and direct classification functions. | CLI loop only; inputs are caller-supplied records/Booleans, including hardcoded loop values. | `test_release.py`; **CLI-fixture decision logic**. |
| `release`: `certificate.py` | Mutable HMAC `ReleaseCertificate` with local fallback key. | CLI creates but does not persist certificate or feed legacy publisher. | `test_release.py`, `test_meta.py`; **CLI-fixture, disconnected release record**. |
| `release`: `compiler.py`, `policy.py` | Assemble text from supported claims; second promotion decision authority. | CLI loop only. Compiler renders claim text, not a derivation/proof object; promotion remains disabled by default. | `test_release.py`; **CLI-fixture, duplicate/disconnected policy**. |
| `retrieval`: `records.py`, `packet.py`, `service.py` | Source/premise records, mutable source packet/local TF-IDF index, lexical import auditor, novelty query log. | CLI loop constructs local service over one dummy theorem; no network/corpus snapshot/import audit is called. | `test_retrieval.py`, orchestrator tests; **CLI-fixture/local mock corpus**. |
| `retrieval`: `premises.py`, `source_priority.py` | Local token-overlap premise ranking and source-priority table. | No Lean/orchestrator caller. | `test_retrieval.py`; **test-only**. |
| `search`: `algorithms.py`, `bands.py` | Algorithm-name registry plus UCB/AO*/Boolean guards; compute-band constants. | No orchestrator caller or persisted state. | `test_search.py`; **test/status-only**. |
| `search`: `blueprint.py`, `controller.py` | In-memory AND/OR graph; in-memory posterior/random branch controller. | No CLI/worker/graph integration. Budget accounting is local mutable state. | `test_search.py`; **library/test-only**. |
| `search`: `dedup.py`, `failure.py`, `mechanism.py`, `programs.py`, `verified_debt.py` | Local token/fingerprint dedup, failure records, QD archive, constant method families/program creation, weighted-debt math. | No scheduler/orchestrator/event-store caller; no durable archive. | `test_search.py`; **test-only**. |
| `selection`: `features.py`, `posterior.py`, `acquisition.py` | Feature record, in-memory Dirichlet posterior, random selector/acquisition score. | No corpus/queue/orchestrator caller and no connection to existing `problem_queue.py`. | `test_selection.py`; **test-only/duplicate selector concept**. |
| `truth`: `entities.py` | Core dataclasses/enums for problems, claims, evidence, relations, certificates. | CLI graph uses a subset. Most fields never reach events or persistence. | `test_truth_plane.py`, many package tests; **CLI-fixture schema**. |
| `truth`: `events.py`, `graph.py`, `router.py`, `validators.py` | JSONL envelope log, in-memory graph, kind router, field-based evidence validators. | CLI core; event file is the primary lasting side effect. Graph not reconstructable. | `test_truth_plane.py`, orchestrator/release tests; **CLI-fixture local truth plane, durability incomplete**. |
| `truth`: `blackboard.py`, `revocation.py`, `views.py` | In-memory proposal blackboard; SCC revocation; SQLite/manifest projections. | No CLI loop caller. SQLite writes only when explicitly invoked. | `test_truth_plane.py`, acceptance 5/8; **test-only despite core architectural claims**. |
| `verification`: `attacks.py`, `referee.py`, `standards.py` | Attack result containers, referee accumulator, evidence-tier classifier. | CLI loop constructs synthetic pass results; no attack worker/tool executes. | `test_verification.py`, orchestrator tests; **CLI-fixture status aggregation**. |
| `verification`: `aggregation.py` | Pessimistic review decision and conflict record. | No referee/orchestrator/release caller. | `test_verification.py`; **test-only**. |

## Leaf modules outside every normal import closure

These **58/92** leaf modules are not in the transitive import closure of either (a) any top-level repository Python production import or (b) `egmra.cli`. Many are exercised only because tests import package `__init__.py` re-exports:

```text
egmra.agents.authorities
egmra.agents.profiles
egmra.agents.prompts
egmra.comms.human
egmra.comms.render
egmra.compute.backends
egmra.control.congestion
egmra.control.leases
egmra.control.parallel
egmra.control.recovery
egmra.control.throttle
egmra.design_status
egmra.eval.ablations
egmra.eval.levels
egmra.eval.metrics
egmra.eval.progress
egmra.eval.protocol
egmra.eval.stats
egmra.lean.aristotle_routing
egmra.lean.blueprint
egmra.lean.coverage
egmra.lean.hardening
egmra.lean.missing_library
egmra.lean.proof_state
egmra.lean.sentinels
egmra.lean.service
egmra.lean.sync
egmra.lean.target_package
egmra.learning.calibration
egmra.learning.expert_iteration
egmra.learning.memory
egmra.m2
egmra.models.registry
egmra.oeis.client
egmra.oeis.matching
egmra.oeis.transforms
egmra.provenance.rules
egmra.retrieval.premises
egmra.retrieval.source_priority
egmra.risks
egmra.search.algorithms
egmra.search.bands
egmra.search.blueprint
egmra.search.controller
egmra.search.dedup
egmra.search.failure
egmra.search.mechanism
egmra.search.programs
egmra.search.verified_debt
egmra.selection.acquisition
egmra.selection.features
egmra.selection.posterior
egmra.services
egmra.topology
egmra.truth.blackboard
egmra.truth.revocation
egmra.truth.views
egmra.verification.aggregation
```

Import reachability still overstates functional reachability: among the 33 CLI-reachable leaf modules, `orchestrator.checkpoint` and `orchestrator.roles` are merely imported by `egmra/orchestrator/__init__.py`; `provenance.stage_identity` is pulled in by an unused runner; and the referee/attack modules receive synthetic results rather than executing attacks.

## Bottom line

The implementation contains useful local primitives—canonical hashing, fail-closed evidence validators, a deterministic subprocess computation path, graph mutation rules, and many explicit schemas—but the claimed system breadth is mainly an API/type/constant inventory plus tests. Normal repository production reaches only the new default-off promotion guard. The standalone CLI reaches a deterministic fixture slice that bypasses most declared subsystems and substitutes hardcoded/injected evidence. The event record cannot restore the state it claims to make authoritative, the checked-in policy is unsigned and disables the major capabilities, and the real provider/Lean/Postgres/container integrations are absent or intentionally nonfunctional.
