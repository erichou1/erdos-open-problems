# FABLE Code Inventory and Reachability Analysis

## Scope, snapshots, and classification

This inventory covers the claimed EGMRA implementation, its repository entry
points, configuration, persistence, external adapters, and tests.

- **Audit-start snapshot:** commit
  `4b4ec96f1c81492af02f814c65825a5106e0af60`, copied to
  `/tmp/erdos-baseline.t2afE1/src` before tests or remediation.
- **Audit-start size:** 92 non-test, non-`__init__.py` source modules; 21
  production package initializers; 10,839 non-test Python lines; 21 EGMRA test
  files; 3,117 test lines; 241 test functions.
- **Final remediation snapshot:** 95 leaf source modules (the added modules are
  `intake/review.py`, `lean/correspondence.py`, and `truth/snapshots.py`), 21
  production initializers, and 41 EGMRA test files.
  Final runtime case counts and verdicts are in
  `FABLE_FINAL_VERIFICATION.md`.

Classifications:

- **legacy-production** — called by an existing repository operational entry
  point such as `promote_verified_run.py`;
- **CLI-slice** — called through `python -m egmra.cli run`, which remains a
  bundled-fixture entry point rather than the existing Erdős scheduler;
- **library-only** — substantive local implementation without a normal caller;
- **test/export-only** — used by tests or `__init__` re-exports, not operational
  control flow;
- **mock/facade** — deterministic or injected substitute for a required service;
- **blocked-external** — repository-local boundary exists, but the actual service
  was unavailable or not exercised;
- **incomplete/status-only** — protocol, registry, descriptive topology, or
  missing required semantics;
- **duplicate/disconnected** — overlapping decision authorities with no shared
  production decision.

Import reachability is necessary but insufficient. A package imported through
an `__init__.py`, an optional object constructed but never consumed, or a class
whose result is synthesized by its caller is not counted as behaviorally
reachable.

## Entry points and real call paths

| Root | Audit-start call path and effects | Post-remediation state | Classification / limitation |
|---|---|---|---|
| Legacy promotion | `promote_verified_run.py` -> `egmra.m0.PromotionGuard` -> `egmra.policy.PolicyEnforcer`; could rewrite a legacy manifest and call a separate publisher | Policy/evidence authentication was hardened and no public fallback is accepted. The unsafe legacy publisher is now retired unconditionally; it cannot publish, and no EGMRA certificate migration bridge exists. | Narrow **legacy-production** guard with publication **unreachable/fail-closed**; broader architecture disconnected. |
| `python -m egmra.cli run --fixture …` | Fixture -> `orchestrator.research` -> deterministic intake/local corpus/subprocess compute/in-memory graph/synthetic referee/gates; writes JSONL | The loop now consumes a real budget, selection, programs, blueprint/controller, leases/fencing, scoped blackboard, authenticated compute path, optional OEIS/Lean calls, current truth snapshot, gates, and memory admission. | Strengthened **CLI-slice**, still fixture-only and not the existing repository scheduler. External Lean/provider/literature/container behavior remains unavailable or local. |
| `python -m egmra.cli verify-events` | Read and verify one JSONL hash/HMAC chain | Event log now also has an authenticated head/Merkle commitment and complete graph replay. | Operational local verifier; rollback of both log and head still needs an external monotonic anchor. |
| `policy-show`, `policy-sign`, `fixtures` | Display/sign policy or list fixtures | Signing now requires an explicit strong key and protects output replacement/symlinks. | Operational administration/status commands. |
| Existing queue/search/continuous programs | No EGMRA orchestrator imports at audit start | No evidence in this inventory that `run_continuous.py`, `problem_queue.py`, `erdos_searcher.py`, `run_verified_range.py`, or `proof_pipeline.py` now launches EGMRA research. | Broad EGMRA remains **unreachable from legacy production**. |
| API/server/worker/migration/package entry point | None | None identified. | **Omitted/incomplete**: no API app, migration command, service daemon, console script metadata, or installable project metadata. |

At audit start, only 33/92 leaf modules were in the transitive import closure of
`egmra.cli`; 58/92 were in neither the CLI closure nor any top-level production
closure. Current orchestration imports substantially more modules, but import
expansion does not make the remaining status registries, external facades, or
evaluation declarations operational.

## Package and module inventory

Every audit-start leaf module is named below. The three remediation additions
`intake/review.py`, `lean/correspondence.py`, and `truth/snapshots.py` are
included as well.

| Package / modules | Purpose and public surfaces | Callers, dependencies, configuration, persistence / side effects | Tests and classification |
|---|---|---|---|
| `egmra/__init__.py` | Package description and version. | No `pyproject.toml`, setup metadata, console script, or wheel build consumes the version. | Import surface; **incomplete packaging**. |
| Root `cli.py`, `config.py` | CLI commands; layered public config and secret denylist. | CLI reads config/env, writes event files and signed policy output. No arbitrary-problem or service-mode entry point. | `test_cli.py`; **CLI-slice**. Remediation added explicit policy/config errors and fixture expectation exit codes. |
| Root `m0.py` | `PromotionGuard`, evidence precedence, quarantine records, promotion telemetry. | Guard called by legacy promoter. Quarantine/telemetry had no production loader/store at audit start. | `test_m0_safety.py`, acceptance tests; guard **legacy-production**, remainder **library/test-only**. |
| Root `m2.py` | `EventStore` protocol, PostgreSQL descriptor, content-addressed store, `M2Assembly`. | Audit-start `PostgresEventStore.connect()` always raised; assembly used local JSONL/subprocess values. No migrations or real transaction caller. | `test_m2_scale.py`; **blocked-external/incomplete**, not an operational M2 service. |
| Root `design_status.py`, `risks.py` | Machine-readable design-choice and risk registries. | No enforcement/control caller or persistence. | `test_meta.py`; **status-only**. |
| Root `services.py`, `topology.py` | Typed service descriptors/protocols and endpoint registry. | No transport, discovery, authentication, health check, startup, cancellation, or routing runtime. | `test_meta.py`; **protocol/status-only**. |
| `agents/authorities.py` | Audit start: seven `Authority` records and forbidden-action tuples. Current: HMAC capability token/issuer with permission, resource, lineage, expiry, branch and packet scope. | Current CLI loop uses issuer with blackboard. Requires `EGMRA_AUTHORITY_KEY`; token enforcement is local-process HMAC, not a distributed identity service. | `test_agents.py`, `test_adversarial_authorities.py`, orchestrator adversarial tests; current **CLI-slice security boundary**. |
| `agents/profiles.py`, `prompts.py` | Method/diversity records and role prompt text/hashes. | No model gateway enforces prompt restrictions; profile labels remain caller data unless bound by the authority/runner path. | `test_agents.py`; **library/test-only**. |
| `agents/runner.py` | `ModelRunner` protocol, deterministic runner, injected attested adapter. | CLI now consumes runner output/identity. No concrete OpenAI/Anthropic/Gemini authentication, retry, cancellation, response-schema, or production provider factory. | `test_agents.py`, orchestrator tests; deterministic path **CLI-slice mock**, live provider **blocked-external/incomplete**. |
| `comms/human.py`, `render.py` | Human intervention record and evidence-profile rendering. | Not the primary CLI release renderer; intervention log is in-memory and not graph/event integrated. | `test_meta.py`; **test-only/disconnected communication path**. |
| `compute/spec.py` | Frozen experiment purpose/input/resource/claim contract and identity. | Consumed by worker/service. Current inputs are snapshotted and validated. | Compute and security tests; **CLI-slice utility**. |
| `compute/sandbox.py` | Audit start: same-host `SubprocessSandbox` and always-raising `ContainerSandbox`. Current: restricted exact-language executor, measured replay executor, OCI boundary that fails closed when unavailable. | Runs subprocesses/temp files; bounded stdout/JSON/schema/CPU/memory/wall policy. Docker daemon was present, but no compatible Python OCI image completed a real job; no unsandboxed fallback. | 36 adversarial compute tests plus local tests; restricted path **CLI-slice**, true OCI isolation **BLOCKED-EXTERNAL**. The restricted interpreter is explicitly not labeled a complete security sandbox. |
| `compute/artifact.py`, `service.py` | Artifact classification, immutable content identity, job/persistence, replay, checker reports. | Current service persists jobs/artifacts/certificates atomically when configured, validates corruption/symlinks/environment, uses trusted checker registry; CLI may use local store depending configuration. | `test_compute.py`, `test_adversarial_compute_security.py`; strengthened local **CLI-slice**. Independent replay depends on an actually distinct measured interpreter. |
| `compute/backends.py` | Solver result types; SAT/SMT/CAS protocols; small exact/model/RUP checkers. | No concrete Z3/cvc5/Sage/PySAT production adapter or orchestrator route. | `test_compute.py`; local helpers **library-only**, external solvers **incomplete/blocked-external**. |
| `control/leases.py` | Audit start: in-memory holder record. Current: durable JSON lease state, expiry/renew/transfer, monotonic fencing tokens, file lock and atomic writes. | Current CLI loop acquires and checks fences before accepting output; local filesystem state only. | `test_control.py`, `test_adversarial_control.py`, orchestrator stale-output test; current **CLI-slice/local durable control**. Distributed database lease remains M2-unimplemented. |
| `control/throttle.py` | Exponential backoff and provider pause state. | Current validation enforces finite inputs and exact 120-second cap. No live provider adapter calls it. | Control tests; **library-only** until provider integration. |
| `control/parallel.py` | Parallel/serialization policy and verifier-reserved pool. | Current pool is bounded/thread-safe; production CLI research remains a local sequential loop. | Control tests; **library-only**, not proof of full-scale scheduling. |
| `control/recovery.py`, `congestion.py` | Recovery table and congestion-price/controller helpers. | No queue/service runtime consumes recovery actions or congestion prices. | `test_control.py`; **status/library-only**. |
| `corpus/status.py` | Dated status claims and conflict reconciliation. | CLI loop calls it; caller supplies status records. No fresh live source audit/refresh scheduler. | Retrieval/orchestrator tests; local **CLI-slice**, real status retrieval incomplete. |
| `eval/datasets.py` | Five elementary fixtures and external benchmark manifests. | CLI fixture source. External datasets are descriptions/identifiers, not bundled/executed corpora. | `test_eval.py`, CLI; fixtures **CLI-only**, benchmarks **incomplete**. |
| `eval/levels.py`, `metrics.py`, `protocol.py`, `stats.py` | Evaluation levels/tracks, metric records, freeze/comparison contracts, statistical guards. | No evaluation runner, cost ledger integration, blind graders, or result store. | `test_eval.py`; **library/status-only**. |
| `eval/ablations.py`, `progress.py` | Required ablation registry and durable-progress scoring helper. | Audit start registered names without running arms; progress signal contained no production loop. No current causal experiment evidence. | `test_eval.py`; **status-only/incomplete evaluation**. |
| `intake/statement_ir.py` | IR, binders/definitions/constraints, grammar/clause parsers, injected model parser, reconciliation/backtranslation. | CLI uses two local deterministic parsers; current semantic identity binds domains/definitions and malformed input fails. Real model-family independence is unavailable. | `test_intake.py`; local **CLI-slice**, dual-family semantic firewall **partial**. |
| `intake/interpretation.py`, `probes.py`, `contract.py`, `review.py` | Interpretation lattice, executable probes, frozen problem contract/source material, and authenticated independent intent-review envelope. | CLI calls them and current release path consumes `release_blocked` plus an exact contract/interpretation-bound review; source and structured interpretation flow downstream. Probe semantics remain bounded to supplied executable predicates/rules, and local HMAC review is not organizational independence. | Intake, intent-review, CLI, and orchestrator adversarial tests; current **CLI-slice**, sophisticated semantic equivalence/live independent review still partial. |
| `lean/service.py` | Environment/capsule/declaration/certificate APIs; static scans; checker subprocess boundary; authenticated certificate envelope. | CLI can call it for formal candidates. Real local Lean/lake was unavailable; regex parsing is now explicitly untrusted, caller booleans/lambdas cannot qualify, structured checker output is HMAC-bound to claim/type/source/environment/artifacts. | `test_lean.py`, 31+ adversarial Lean/release tests; trust-envelope local behavior **CLI-slice**, kernel operation **BLOCKED-EXTERNAL**. |
| `lean/target_package.py`, `sentinels.py` | L0 target candidates and L1 risk-ranked sentinel records. | Not a complete production L0/L1 pipeline from CLI; mostly directly invoked helpers. | `test_lean.py`; **library/test-only**, semantic/model and kernel stages external. |
| `lean/blueprint.py`, `proof_state.py` | L2 formal holes and L3 PUCT/transposition/diagnostic helpers. | No real `tryActions` loop or Lean proof-state executor in production. | `test_lean.py`; **library/test-only**, not a nested search implementation. |
| `lean/sync.py`, `coverage.py`, `correspondence.py` | Informal/formal claim linkage, risk-weighted formal coverage, and authenticated exact correspondence-review envelope. | Correspondence disclosure is consumed by the strengthened formal/release path; no live independent reviewer, full orchestration feedback loop, or durable sync store. | Lean/eval/formal-correspondence security tests; correspondence protocol **CLI-capable**, broader sync **library/test-only**. |
| `lean/hardening.py` | L5 scans/checker/archive release conditions. | Audit-start trusted booleans/dummy archive; authenticated checker envelope remediation improves local boundary. No clean pinned offline Mathlib build ran. | Lean/release adversarial tests; **partial/local**, final L5 **BLOCKED-EXTERNAL**. |
| `lean/missing_library.py`, `aristotle_routing.py` | Missing-library workflow and external prover request/quarantine/licensing records. | No real library-contribution workflow or Aristotle CLI execution; existing legacy Aristotle verifier is separate. | `test_lean.py`; **status/test-only / blocked-external**. |
| `learning/memory.py` | Typed temporary and long-term stores, current verified-fact promotion. | CLI now writes problem-local quarantined records and only promotes persistent semantic facts from a current truth snapshot plus current signed gates. Long-term store remains process memory. | `test_learning.py`, `test_adversarial_learning.py`, orchestrator tests; current **CLI-slice**, persistence/training/revocation feedback **partial**. |
| `learning/calibration.py`, `expert_iteration.py` | Calibration math/ledger and verified training-example admission. | Inputs are now validated; no training job, model update, persistent ledger, or subsequent provider behavior change. | Learning tests; **library/test-only**. |
| `models/registry.py` | In-memory bake-off records and pin-best by supplied scores. | No bake-off runner, monthly schedule, campaign persistence, or model gateway. | `test_meta.py`; **status/test-only**. |
| `oeis/transforms.py` | Typed local sequence transforms with preconditions and trace. | Current exact integer typing/immutable steps; no side effects. | OEIS adversarial/unit tests; **library utility**, called only when orchestrator receives generated sequences. |
| `oeis/client.py` | Read-only HTTP/cache/rate/query client. | Optional CLI-orchestrator call; current strict JSON/schema/query/cache hash/symlink checks, canonical-host HTTPS/default-TLS/manual redirects, 4 MiB response bound, cleanup, and fail-closed offline behavior. Live OEIS HTTP was not exercised. | OEIS tests use injected/mocked transport; local contract **CLI-capable**, live service **BLOCKED-EXTERNAL/UNVERIFIED**. |
| `oeis/matching.py` | Transform-path enumeration, scoring, held-out verification, conjecture record. | Current empty/no-match paths remain T0 and metadata is validated. Orchestrator only records heuristic query metadata; no automatic proof/novelty promotion. | OEIS tests; **library-only/heuristic**. |
| `orchestrator/loop.py` | Main `research()` result, deterministic worker, budget ledger, attack evaluator, closed-loop wiring. | Audit start was a hardcoded fixture script. Current version calls runner, selection, program archive, blueprint/controller, lease/fence, authority blackboard, compute/replay, optional OEIS/Lean, truth snapshot, referee, gates, and memory. Writes event/lease/artifact state as configured. | Orchestrator/CLI/eval plus 15 adversarial orchestrator tests; strengthened **CLI-slice**, not yet a full autonomous or legacy-integrated runtime. |
| `orchestrator/checkpoint.py`, `roles.py` | Checkpoint compatibility and role/service layout constants. | Audit start imported via package only; no complete durable controller/archive/model/provider/checkpoint restoration. Current graph/lease/compute replay is better, but this checkpoint module remains mostly direct-test code. | `test_orchestrator.py`; **test/status-only / partial resume**. |
| `policy/__init__.py` | Canonical feature schema, sign/load/verify, entry-point enforcement. | Legacy promotion and CLI use it; requires explicit `EGMRA_POLICY_KEY`, rejects duplicate JSON/unknown flags/unsigned policy. Audit entries remain local memory. | Foundation/M0/truth security/CLI tests; current **legacy-production + CLI-slice**. |
| `provenance/hashing.py` | Canonical JSON, SHA-256, content IDs, Merkle roots. | Common pure dependency. | Foundation and many adversarial tests; **production-integrated utility**. |
| `provenance/stage_identity.py`, `rules.py` | Stage/cache identity and provenance-shape rules. | Runner identity path uses part of stage identity; generic provenance rules and full cache invalidation are not integrated across all services. | Foundation/acceptance tests; **library-only/partial**. |
| `release/gates.py` | Five independent gate computation and signed gate authorization. | Current production gate requires a fresh `TruthSnapshot` and current event log; snapshot-derived profile replaces caller profile. External novelty/significance/human judgments remain caller/service inputs where applicable. | Release, snapshot, Lean/release, orchestrator tests; current **CLI-slice security boundary**. |
| `release/certificate.py` | Signed release certificate/render verification. | Current signing requires distinct strong key, exact subject/gate/promotion binding, freshness/current event head; no public fallback. Not consumed by legacy publisher. | Release/adversarial tests; **CLI-slice**, **disconnected** from legacy release. |
| `release/compiler.py`, `policy.py` | Assemble from admitted claims; promotion authorization. | CLI-slice only. Compiler assembles admitted claim text/dependency records, not a real general mathematical proof. Separate from legacy promotion guard. | Release/orchestrator tests; **CLI-slice / duplicate decision authority**. |
| `retrieval/records.py` | Theorem/premise/provenance schemas. | Current source hash and immutable mapping validation; caller/local corpus supplies data. | Retrieval tests; **CLI-slice schema**. |
| `retrieval/packet.py`, `service.py` | Frozen query/packet identity, local lexical retrieval, import auditor, novelty log. | CLI builds a local packet. Current packet commits all material fields and is deeply immutable; auditor preserves negation and requires real hashes. Still one local corpus, not four linked live indexes or formal theorem applicability. | Retrieval/adversarial/orchestrator tests; local **CLI-slice**, full retrieval **partial/blocked-external**. |
| `retrieval/premises.py`, `source_priority.py` | Token ranking/elaboration flags and claim-specific priority table. | No real Lean/theorem-index production caller or source-audit workflow. | Retrieval tests; **test/library-only**. |
| `search/controller.py` | Posterior/action utility, budget allocation, update/censoring, protected lane. | Current CLI loop calls it; finite validation and real branch/global spend added. State is process-local and not checkpointed. | Search/adversarial/orchestrator tests; current **CLI-slice local controller**. |
| `search/blueprint.py` | AND/OR nodes, dependency closure/failure cone/cycle rejection. | Current CLI creates/updates a simple direct-first blueprint. | Search/orchestrator tests; **CLI-slice local blueprint**, not full dynamic AO* executor. |
| `search/mechanism.py`, `programs.py` | Mechanism fingerprint, quality-diversity archive, research-program family instantiation. | Current CLI consumes fingerprints/archive and branch records. Archive is in-memory; program workers remain one supplied worker rather than distinct tool/model services. | Search/orchestrator tests; **CLI-slice partial program search**. |
| `search/verified_debt.py` | Frozen policy and obligation/debt calculation. | Current CLI computes debt; immutable/nonnegative/disappearing-obligation checks added. | Search/orchestrator tests; **CLI-slice utility**. |
| `search/dedup.py`, `failure.py`, `bands.py`, `algorithms.py` | Dedup cascade, failure certificate, compute bands/reserve, algorithm registry/formulas. | Not materially consumed by the current CLI loop for persistent scheduling/recovery; algorithm registry does not execute search. | `test_search.py`; **library/status-only**. |
| `selection/features.py`, `posterior.py`, `acquisition.py` | Complete local feature record, competing outcomes, acquisition/selection. | Current CLI calls selection with locally constructed features; posterior is initial/default and not learned from durable history. Numeric and hard-constraint validation added. | Selection/adversarial/orchestrator tests; **CLI-slice local selection**, closed-loop calibration partial. |
| `truth/entities.py` | Problems, interpretations, claims, branches, evidence, relations, intent/correspondence certificates and versions. | Current CLI graph uses most core types; immutable attestation/binding fields added. | Truth and cross-plane tests; **CLI-slice schema**. |
| `truth/events.py`, `graph.py` | Signed append-only log/head, graph reducer/replay, mutation/version events, snapshots/cert bindings. | Current events include complete payloads; writes lock, compare versions, fsync, and replay. Local JSONL authoritative for M1. Dual deletion/rollback of log+head requires an external monotonic anchor. | 20 truth-security plus truth/snapshot tests; current **CLI-slice durable local truth plane**. |
| `truth/validators.py`, `router.py` | Kind-specific evidence authentication/semantics and sole status transition authority. | Current evidence HMAC binds claim/artifact/provenance/replay; graph current hashes checked; direct status mutation denied. Formal validator depends on authenticated Lean envelope and exact graph bindings. | Truth/Lean/orchestrator adversarial tests; current **CLI-slice trust boundary**. |
| `truth/snapshots.py` | New signed replay-derived truth snapshot bound to claim/status/version/profile/evidence and event head/Merkle. | Used by current gates/release/learning; requires separate `EGMRA_TRUTH_SNAPSHOT_KEY`. | `test_truth_snapshots.py`, release/orchestrator tests; **CLI-slice trust handoff**. |
| `truth/blackboard.py` | Scoped immutable read slices and structured proposal admission. | Current CLI loop uses authority tokens, branch/packet hashes, proposal-kind allowlists and current fence. | Authority/orchestrator tests; current **CLI-slice least-privilege boundary**. |
| `truth/revocation.py`, `views.py` | SCC invalidation/revalidation and SQLite/manifest projections. | Revocation now events/versioning first and survives graph replay. Views remain derived and explicitly invoked; SQLite is not the authoritative concurrent store. | Truth tests; revocation **CLI-capable**, views **library-only**. |
| `verification/attacks.py`, `referee.py` | Ten attack schemas/results, independent referee accumulator and release block. | Current orchestrator uses a pessimistic mechanical evaluator or injected evaluator. It no longer synthesizes passes for unavailable attacks, but a true organizationally independent provider/human service is absent. | Verification/orchestrator adversarial tests; local **CLI-slice**, independent service **partial/blocked-external**. |
| `verification/standards.py`, `aggregation.py` | T0-T5/profile classification and pessimistic review aggregation. | Current code prevents caller hardening/T5, rejects unknown/duplicate/correlated promotion. Diversity still depends partly on attested labels rather than a multi-provider identity authority. | Verification/Lean/release tests; **CLI-capable local policy**, organizational independence partial. |

## Audit-start unreachable leaf modules

The following 58/92 leaf modules were outside both the legacy-production and CLI
transitive import closures at audit start:

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

Remediation intentionally moved authorities, leases, selection, controller,
blueprint, mechanism/programs/debt, Lean/OEIS option paths, learning, blackboard,
and verification aggregation into the CLI research slice. The remaining
full-scale/evaluation/service/helper modules still require explicit production
call paths before they can be called integrated.

## Persistence, side effects, and configuration inventory

| State / side effect | Audit-start behavior | Current local behavior / limitation |
|---|---|---|
| Truth events | JSONL envelope only; public fallback HMAC; no complete replay/locking/truncation commitment | Strong env key, complete payload reducer, lock/CAS/fsync, authenticated head/Merkle, restart replay. No external anti-rollback anchor. |
| SQLite view | Rebuilt from live in-memory graph | Still a derived local view, not M2 transactional truth. |
| Leases | In-memory holder | Durable local JSON + fencing/file lock; no PostgreSQL/distributed transaction. |
| Compute jobs/artifacts | In memory by default; optional shallow file output | Immutable atomic bundles, corruption/symlink validation and restart replay when store configured. |
| Release/gates | Public fallback key; caller profile; certificate before policy | Distinct strong keys, current truth snapshot/event head and promotion binding. Unsafe legacy publication is retired; no migration bridge exists. |
| Memory/calibration/model registry | In-memory | Validated admission, but still no durable database/training feedback. |
| OEIS cache/network | Optional JSON; implicit/unbounded live Requests path | Hashed, query-bound, atomic 0600 cache plus canonical-host/default-TLS/manual-redirect/bounded transport; live HTTP unexercised. |
| Postgres/object store | Always-raising Postgres plus local object files | No verified live Postgres, migration, SCC transaction, or recovery. |
| Lean artifacts | Caller/injected values | Authenticated structured checker envelope; no installed pinned Lean/Mathlib run. |
| External model calls | Caller-supplied callable | No live provider adapter exercised. |

Required local trust secrets now include policy, event, evidence, release, gate,
promotion, Lean-checker, authority, and truth-snapshot keys. The CLI config
denylist prevents these from being persisted in public config. They remain
deployment responsibilities; no distributed secret manager is implemented.

## Incomplete authority migration

The legacy `PromotionGuard`/verification path and the EGMRA `PromotionPolicy`,
signed gates, truth snapshot, and `ReleaseCertificate` remain architecturally
separate. The legacy publisher itself is retired fail-closed, so there are not
two active publication authorities; instead, legacy publication is unavailable
and has no migration handoff into the EGMRA certificate renderer.

The remediation closes named bypasses within the EGMRA slice but does not
establish a single repository-wide release transaction or prove every future
entry point consumes it. Similarly, service protocols in
`services.py`/`m2.py`, endpoint descriptions in `topology.py`, and the external
provider/Lean/Aristotle abstractions are not service implementations merely
because their interfaces validate.

## Bottom line

At audit start, the repository contained a sizable prototype library and a
deterministic fixture demonstration; normal production reached only a narrow
promotion guard. Remediation materially strengthened and connected the local M1
CLI slice, especially truth replay, evidence authentication, control fencing,
selection/search wiring, least privilege, compute validation, release handoffs,
and fail-closed external boundaries.

It is still not accurate to call every module production-integrated. The legacy
repository scheduler remains disconnected from most EGMRA planes, while its
publisher is deliberately unavailable rather than integrated;
full evaluation, provider, Lean/Mathlib, PostgreSQL, OCI computation, Aristotle,
multi-source retrieval, service topology, and durable learning remain partial,
test-only, or externally blocked.
