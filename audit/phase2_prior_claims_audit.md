# Phase 2 prior-claims audit

## Audit conclusion

The prior completion conclusion is **rejected**. The repository has a substantial, testable collection of schemas, deterministic helpers, local adapters, and unit tests, but the evidence does not support the claims that all requirements are verified, that M0 or M1 is complete, that the three searches run as an integrated system, or that the Section 13.6 acceptance criteria are met.

The strongest distinction is between **surface presence** and **faithful, reachable behavior**:

- The raw repository-size and test-collection figures reproduce.
- The independent inventory contains **216** requirements, whereas the prior ledger contains **120** rows, all marked `VERIFIED`. The difference of 96 records is not automatically 96 omissions because the prior ledger merges clauses, but those merges conceal independently testable failure behavior, integration, and milestone obligations.
- Many named components exist only as dataclasses, constants, protocols, injected test doubles, or local facades. The production `research()` path does not reach most of them.
- The tests establish many local helper properties, but frequently construct the trusted fact being asserted, replace a required independent system with a label or lambda, or call a helper directly instead of exercising a production entry point.

No production or test file was changed for this audit.

## Reproduced quantitative claims at the audited snapshot

The following counts were independently reproduced at the Phase 1/audit-start snapshot against which the prior report was written:

| Measurement | Current result | Assessment |
|---|---:|---|
| Python files under `egmra/` | 135 | Supported at the audited snapshot |
| Source modules excluding tests and `__init__.py` | 92 | Supported |
| `__init__.py` files | 22 | Supported as a package-directory count; this includes the root package and `egmra/tests`, so it does not establish 22 operational subsystems |
| Source LOC excluding tests | 10,839 | Supported |
| All Python LOC under `egmra/` | 13,957 | Supported at the audited snapshot |
| `test_*.py` files | 21 | Supported at the audited snapshot |
| EGMRA test functions/cases | 241 | Supported at the audited snapshot |
| Combined pytest cases | 420 | Supported by the Phase 1 clean run at the audited snapshot |
| Prior ledger rows marked `VERIFIED` | 120 | Supported as a description of the ledger, not of implementation truth |

Passing 420 tests is real software evidence. It is not evidence that 216 independently reconstructed requirements, four planes, three searches, or 18 acceptance behaviors are implemented.

**Post-baseline audit-addition note.** During this Phase 2 verification, the parent audit added the intentional TDD regression file `egmra/tests/test_adversarial_truth_security.py` after the audit-start measurement. It adds ten cases. The current collection is therefore 251 EGMRA cases and 430 combined cases, rather than the audited/prior-report snapshot's 241 and 420. This prior-claims audit did not create or modify that file; it is excluded from assessing what the prior report had verified.

## Assessment of the advertised claims

Verdicts in this table assess the advertised semantic claim, not merely whether a file or test with a matching name exists.

| # | Prior claim | Verdict | Evidence-based assessment |
|---:|---|---|---|
| 1 | 92 source modules | **SUPPORTED** | Reproduces exactly with source/test and `__init__.py` exclusions. |
| 2 | 22 packages | **SUPPORTED** | Reproduces as 22 initializer-bearing directories; one is the test package and one is the root package. |
| 3 | approximately 10.8k source LOC | **SUPPORTED** | Current source-only count is 10,839. |
| 4 | 241 EGMRA cases plus 179 baseline cases, 420 combined passing cases | **SUPPORTED** | The Phase 1 run reproduced the claimed snapshot. A concurrent later test file now makes the live counts 251 and 430; that does not retroactively strengthen the prior verification. |
| 5 | the ledger contains 120 rows and all say `VERIFIED` | **SUPPORTED** | `IMPLEMENTATION_LEDGER.md:24-239` contains 120 requirement rows, all labeled `VERIFIED`. |
| 6 | all requirements are verified | **FALSE** | The independent inventory has 216 requirements and requires reachability, integration, negative behavior, and faithful semantics. The findings below disprove numerous `VERIFIED` rows. |
| 7 | four operational planes | **PARTIAL** | Four package groupings and many plane-local objects exist, but the orchestration path does not integrate selection, search, Lean, learning, leases, or OEIS. Package presence is not operational plane separation. |
| 8 | three nested searches | **FALSE** | Search data structures and formulas exist, but `research()` does not import or call the program archive, AND/OR controller, or Lean proof-state search. |
| 9 | the listed subsystems are complete | **MISLEADING** | Some isolated subsystems, notably local OEIS transforms, have meaningful implementations. Others are declarative or injected facades, and most are unreachable from the claimed end-to-end loop. The subsystem table in `FINAL_VERIFICATION_REPORT.md:35-56` conflates these levels. |
| 10 | M0 complete | **FALSE** | The shipped policy is unsigned, unsigned policy documents are accepted, enforcement is absent from legacy verification/load paths, and quarantine/telemetry helpers are not production-reachable. |
| 11 | M1 genuine end-to-end | **FALSE** | The graph cannot be reconstructed from JSONL, SQLite is a projection of live memory, the loop has no integrated controller/blueprint/Lean worker, and the referee attacks are synthesized from one boolean. |
| 12 | M2 scale interfaces complete | **FALSE** | The PostgreSQL and container methods deliberately raise instead of operating; the milestone explicitly requires real PostgreSQL/leases/object storage/SCC transactions and containerized backends. |
| 13 | all 18 Section 13.6 acceptance criteria pass | **FALSE** | Eighteen test functions pass, but none demonstrates its full production acceptance behavior; several are direct helper assertions, label substitutions, conditional/vacuous assertions, or injected always-success functions. |
| 14 | no stubs | **MISLEADING** | A textual `TODO`/`NotImplementedError`/pass-only scan can be clean while `ContainerSandbox.run()` and `PostgresEventStore.connect()` always raise and service/topology modules remain descriptive. “No textual stub markers” is supported; “no functional stubs” is not. |
| 15 | unexercised external integrations are complete rather than unmet or blocked | **FALSE** | D-004/D-005 explicitly substitute interfaces and local mocks. F-REQ-167 specifically requires real PostgreSQL or an honest external blocker; the final report instead reports no blocked requirements (`FINAL_VERIFICATION_REPORT.md:93-96`). |

Verdict count: **5 SUPPORTED, 1 PARTIAL, 2 MISLEADING, 7 FALSE, 0 UNVERIFIABLE**.

## Requirement-indexed findings

### F-REQ-026, F-REQ-148, F-REQ-174 through F-REQ-191 — traceability was compressed and weakened

The prior ledger's 120-row count is not a faithful substitute for the 216 independently reconstructed contracts.

- `FABLE_INDEPENDENT_REQUIREMENTS.md:15-25` states the independent extraction and preserves all 18 acceptance criteria individually.
- `IMPLEMENTATION_LEDGER.md:24-37` merges multiple executive invariants into broad rows, then marks package/file presence and unit tests as verification.
- `IMPLEMENTATION_PLAN.md:156-159` says “20 acceptance tests,” contradicting both the specification and the actual 18 criteria/tests.
- `IMPLEMENTATION_LEDGER.md:176-180` marks M0, M1, M2, and all acceptance criteria verified without retaining each milestone's distinct technology and failure behavior.

This is not merely an ID-renaming difference. For example, “three searches” was credited because classes exist, while production reachability was not retained as a separate obligation.

### F-REQ-014, F-REQ-017, F-REQ-149 through F-REQ-156, F-REQ-174, F-REQ-179, F-REQ-204 — M0 safety closure is absent

The prior claim that urgent provenance and promotion safety are complete is contradicted by the implementation.

- `egmra/config/egmra_policy.json:18-19` ships an empty signature.
- `egmra/policy/__init__.py:152-168` verifies a signature only when one is present, accepts unsigned policy documents, and even signs a legacy bare document with the public development key.
- `egmra/policy/__init__.py:182-192` checks feature flags but does not authenticate the policy at enforcement time; `override=True` enables disabled non-release features.
- `egmra/tests/test_proof_pipeline.py:14-17` calls a policy “signed” while constructing `FeaturePolicy(flags=...)` with no signature; the permissive object is used for promotion at lines 331-334. `egmra/tests/test_m0_safety.py:25-29` does the same.
- `egmra/m0.py:107-162` defines legacy quarantine and telemetry helpers, but production searches find no loader or entry point calling them; they are exercised only by tests.
- `egmra/promote_verified_run.py:67-93` mutates `manifest.json` in place on both denied and allowed decisions instead of appending an authoritative promotion decision and deriving the manifest.
- `egmra/verification.py:119-132` admits a generic trusted record from caller-supplied `passed`, `kind`, verifier, and hashes rather than dispatching to closed kind-specific semantic validation.

This directly contradicts D-003, D-010, D-011 and the `VERIFIED` M0 row in `IMPLEMENTATION_LEDGER.md:176`.

### F-REQ-006, F-REQ-017, F-REQ-116 through F-REQ-118, F-REQ-153, F-REQ-157, F-REQ-178, F-REQ-181, F-REQ-197 — event sourcing and transactional graph claims are false

- `egmra/truth/events.py:60-78` records event metadata and object IDs/hashes, not the entity payloads needed to reconstruct problems, interpretations, claims, evidence, or edges.
- `egmra/truth/graph.py:45-55` initializes empty in-memory dictionaries and has no replay constructor. Mutations occur before event append, for example `add_problem()` at lines 59-69 and status changes at lines 182-207.
- `egmra/truth/views.py:18-81` drops and rebuilds SQLite tables from the current in-memory graph. SQLite is therefore a disposable view, not the claimed transactional authoritative graph.
- `egmra/truth/revocation.py:93-113` mutates evidence and then performs sequential logging/revalidation without a database transaction or rollback.
- `egmra/tests/test_truth_plane.py:111-138` manufactures formal trust with caller fields such as `kernel_verified=True` and an arbitrary certificate ID rather than replaying an issued certificate through persistence.

After restart, JSONL alone cannot recreate the graph. Therefore M1's “SQLite + JSONL transactional graph,” reproducible manifest, checkpoint/resume, and atomic SCC-revocation claims are unsupported.

### F-REQ-005, F-REQ-007 through F-REQ-012, F-REQ-018, F-REQ-043 through F-REQ-050, F-REQ-077, F-REQ-157 through F-REQ-165, F-REQ-173, F-REQ-205, F-REQ-206 — the claimed 17-step production loop is not implemented

`egmra/orchestrator/loop.py` is the advertised end-to-end path, but its dependencies and control flow establish a much smaller pipeline:

- Imports at lines 22-48 omit problem selection, the search controller, the AND/OR blueprint, the program archive, Lean, verified learning, OEIS, leases, and provider throttling.
- `runner = runner or DeterministicRunner()` at line 167 is dead within the function: `runner` is never subsequently called.
- Lines 180-188 retrieve locally and add only `nodes[0]`; there is no multi-interpretation branch policy or mandatory deep-search gate.
- Line 205 hard-codes `acquired = True`; lines 207-222 self-issue an intent certificate from method-name strings.
- Lines 224-250 repeatedly call the same `worker.work_branch()` rather than generate mechanism-distinct programs, select dynamic leaves, or execute a blueprint.
- Lines 258-269 manufacture every referee attack result from one `probe_failed` boolean and hard-coded diversity strings. No independent attack service runs.
- Lines 277-293 pass an empty replay-report list, create/sign a certificate, and only afterward evaluate promotion.
- `egmra/tests/test_orchestrator.py:50-65` checks phase-name strings, a local finite computation, compiler success, and log integrity. It does not prove the missing integrations are reachable.

The CLI reinforces the issue: `egmra/cli.py:43-56` constructs a one-theorem dummy corpus and fixture worker. The observed T2/I0/N1/S1/R0 result is released as an artifact even though promotion is denied. This is a deterministic demonstration path, not the minimum scientific loop specified by F-REQ-165.

### F-REQ-007, F-REQ-008, F-REQ-018, F-REQ-043 through F-REQ-046, F-REQ-049, F-REQ-061, F-REQ-067 through F-REQ-079, F-REQ-162, F-REQ-170, F-REQ-199, F-REQ-206 — search and control are mostly unreachable components

- `egmra/search/algorithms.py:14-28` is an algorithm-name dictionary; lines 31-50 provide formulas but no best-first, UCT/PUCT, portfolio, or MAP-Elites executors.
- `egmra/search/controller.py:130-147` computes a per-attempt allocation but does not guard `self.spent + amount` against the global budget and is not called by `research()`.
- `egmra/lean/proof_state.py:14-50` defines portfolio names and a PUCT formula/in-memory table; it does not perform proof-state search.
- `egmra/control/parallel.py:75-77` increments active verification without enforcing capacity.
- `egmra/control/leases.py` is an in-memory holder record without fencing tokens, problem/interpretation/budget binding, or transactional concurrency.
- Production reference searches show `ProblemSelector`, `SearchController`, `AndOrBlueprint`, `ProgramArchive`, `LeaseManager`, `VerifierPool`, and `ProviderThrottle` are imported by package exports and tests, not the orchestrator or CLI.

Thus the prior row `REQ-005` and report language “three nested searches” verify static component names, not the required integrated algorithms.

### F-REQ-004, F-REQ-022, F-REQ-036 through F-REQ-039, F-REQ-093, F-REQ-106, F-REQ-158, F-REQ-180, F-REQ-210 — intake weakens the translation firewall

- `egmra/intake/contract.py:28-41` stores source ID/hash/spans but not the complete source metadata required by F-REQ-036.
- `egmra/intake/statement_ir.py:330-357` treats differing parser IDs as independence; it does not establish implementation/model independence. The parsers at lines 179-261 are both local regex/heuristic implementations.
- `egmra/intake/probes.py:67-72` declares paraphrase invariance passed when no rule applies; lines 87-89 do the same for mutation covariance. Boundary and counterexample probes without a predicate return `passed=True` with “not run” at lines 118-121 and 138-141.
- `egmra/intake/target_package.py:67-82` accepts one to three candidates and defaults integrity flags to true without executing probes. `egmra/tests/test_lean.py:120-133` explicitly approves a one-candidate package, weakening the specified two-to-three candidate translation firewall.
- `egmra/tests/test_intake.py:145-152` contains a conditional assertion that can succeed without checking ambiguity behavior.

The intent certificate in the production loop is consequently based on caller/local helper state, not an independent translation firewall.

### F-REQ-005, F-REQ-030, F-REQ-040 through F-REQ-042, F-REQ-056 through F-REQ-059, F-REQ-087 through F-REQ-089, F-REQ-159, F-REQ-169 — retrieval claims exceed the implementation

- `egmra/retrieval/packet.py:121-176` implements one local TF-IDF-style corpus index, not four linked theorem/formal/citation/provenance indexes.
- `SourcePacket` is a mutable dataclass with mutable lists. Its hash at `egmra/retrieval/packet.py:80-89` omits fields including unresolved conflicts, snapshot time, re-entry reason, and full query-event identity, so it is not a complete immutable version identity.
- `egmra/retrieval/service.py:48-72` searches a supplied local corpus only.
- `ImportAuditor` at `egmra/retrieval/service.py:78-113` treats token-subset inclusion as whether a consequence follows; this is not theorem applicability or formal elaboration.
- `egmra/tests/test_retrieval.py:137-146` uses `assert ... if usable else True`, permitting the central elaboration assertion to pass vacuously.

The local packet is useful, but it does not establish mandatory theorem-level multi-source retrieval, formal premise checking, or the production M2 retrieval path.

### F-REQ-010, F-REQ-023, F-REQ-024, F-REQ-062, F-REQ-063, F-REQ-105, F-REQ-160, F-REQ-168, F-REQ-184, F-REQ-194 — computation is neither hardened nor independently replayed

- `egmra/compute/sandbox.py:23-50` monkey-patches selected networking APIs and clears environment variables; it does not isolate the filesystem or create a container boundary.
- `SubprocessSandbox.run()` at lines 78-109 executes a temporary script on the same host. `ContainerSandbox.run()` at lines 112-133 always raises.
- `egmra/compute/service.py:41-47` stores jobs/artifacts in memory. Lines 143-151 persist output/artifact metadata but not enough source/spec state to replay after restart.
- `replay_independently()` at `egmra/compute/service.py:111-127` reuses the same `SubprocessSandbox`; the independent-environment label merely changes a hash.
- `egmra/compute/artifact.py:65-79` and `egmra/compute/validators.py:79-108` trust caller-declared arithmetic mode, coverage text, and generator booleans.
- `egmra/tests/test_compute.py:85-92` calls the same service with an “independent” label; lines 95-105 inject a checker lambda over the artifact's own output.

D-008 openly substitutes a subprocess for the required container. That is an interpretation change, not verification of F-REQ-160 or acceptance F-REQ-184.

### F-REQ-003, F-REQ-009, F-REQ-013, F-REQ-019, F-REQ-064, F-REQ-069, F-REQ-088, F-REQ-090 through F-REQ-105, F-REQ-151, F-REQ-161, F-REQ-171, F-REQ-185, F-REQ-186 — Lean is an injectable facade, not a closed formal service

- `egmra/lean/service.py:187-198` “elaborates” with regex/static parsing rather than invoking Lean.
- `verify_declaration()` at lines 221-285 accepts `kernel_result=True` or the return of an injected runner. There is no locally enforced compiler/kernel boundary.
- `compare_statements()` at lines 287-293 treats any non-empty proof string as checked equivalence.
- Despite the module docstring, the service has no `searchPremises` or `tryActions` implementation.
- `egmra/lean/hardening.py:48-82` trusts a `clean_offline_build` boolean, an arbitrary archive object, and an injected independent checker.
- `egmra/lean/aristotle_routing.py:48-87` returns routing/licensing constants; it does not close vendor-status handling through a local kernel.
- `egmra/tests/test_lean.py:39-49`, 101-107, and 199-226 use always-success lambdas, arbitrary proof strings, and caller booleans as the decisive evidence.

These tests demonstrate adapter behavior, not the exact meaning of “Lean-verified” in F-REQ-003 or a clean pinned no-hole build in F-REQ-185.

### F-REQ-002, F-REQ-003, F-REQ-020, F-REQ-032, F-REQ-033, F-REQ-047, F-REQ-051, F-REQ-109 through F-REQ-115, F-REQ-120 through F-REQ-134, F-REQ-163, F-REQ-177, F-REQ-188, F-REQ-216 — truth and release evidence can be caller-manufactured or compressed

- `egmra/truth/validators.py:45-53` reads generator-supplied findings. Kind validators then trust booleans/strings such as kernel status, exactness, review lineage, or a non-null formal-certificate ID rather than resolve and authenticate the referenced evidence (`egmra/truth/validators.py:111-160`).
- The production loop creates all referee attack outcomes from one boolean and hard-coded diversity claims (`egmra/orchestrator/loop.py:258-269`), violating organizational independence and F-REQ-216.
- `egmra/verification/standards.py:38-62` can assign T5 from an `INDEPENDENT_CHECKER` kind or a caller hardening boolean without enforcing the complete T4/T5 contract.
- `egmra/release/certificate.py:18-75` has a public default development key and an incomplete certificate schema. The certificate is signed before promotion is evaluated.
- `summary_label()` at `egmra/release/gates.py:103-115` maps T2 to `verified_finite_or_conditional_result` without incorporating the intent, novelty, significance, or reproducibility axes. That contradicts the ledger claim that the summary is “non-collapsed.”
- `egmra/tests/test_release.py:32-43` constructs arbitrary reviewer identities; lines 151-166 directly constructs a `KERNEL_CHECKED` evidence profile without obtaining a formal certificate.

Five gate fields exist, but the evidence sources and communication label do not preserve the five independent semantics.

### F-REQ-066, F-REQ-166 through F-REQ-173, F-REQ-193 through F-REQ-201 — interfaces and topology were counted as integration

- `egmra/m2.py:31-54` defines `PostgresEventStore.connect()` only to raise; lines 79-99 assemble local JSONL, subprocess, and integer placeholders.
- `egmra/tests/test_m2_scale.py:14-16` checks protocol conformance; lines 28-32 assert that PostgreSQL raises; lines 35-40 inspect a container policy string without executing a container.
- `egmra/topology.py:12-23` is a descriptive service map. `ServiceTopology.register()` stores endpoint strings; `egmra/tests/test_meta.py:65-71` registers a literal `postgres://...` string without connecting.
- `egmra/services.py:28-79` defines descriptors and protocols, not reachable services.

D-004 and D-005 explicitly reinterpret external service requirements as “interface + local backend.” That can support an interface-ready or `BLOCKED-EXTERNAL` status. It cannot support `VERIFIED`, especially where F-REQ-167 requires real PostgreSQL/leases/object storage/SCC transactions.

### F-REQ-021, F-REQ-135 through F-REQ-147, F-REQ-164, F-REQ-191, F-REQ-192, F-REQ-207, F-REQ-210 through F-REQ-215 — evaluation is encoded, not executed

- `egmra/eval/levels.py:16-44` declares seven levels and tracks as constants.
- `FrozenEvalConfig.config_hash()` at `egmra/eval/protocol.py:33-38` omits status, tools, budget, and network policy despite claiming the evaluation configuration is frozen.
- `egmra/eval/ablations.py:7-21` lists 13 required ablations; `egmra/tests/test_eval.py:89-94` registers all 13 names and asserts the registry is complete. It runs no ablation arms and estimates no causal effect.
- `egmra/eval/datasets.py:15-23` records the requested composition as a dictionary, but only five local fixtures exist at lines 42-54; external datasets are manifest strings at lines 66-83.
- `egmra/tests/test_eval.py:47-60` inserts four baseline-name strings and tests a boolean predicate. No paired equal-cost baseline is run.
- The fixture loop test at lines 123-151 runs only two elementary fixtures through the reduced local orchestrator.

Accordingly, the evaluation APIs are useful scaffolding, but the controlled evaluation, architecture ablations, historical time capsules, calibration, and “honest final architectural claim” remain unverified.

## Section 13.6 acceptance-test adequacy

The 18 functions in `egmra/tests/test_acceptance.py` are correctly numbered, but “18 passing tests” was substituted for “18 acceptance behaviors demonstrated.” The following are the decisive gaps:

| F-REQ | Test lines | What is actually tested | Missing acceptance evidence |
|---|---:|---|---|
| 174 | 54-60 | Calls one enforcer repeatedly with entry-point name strings | Actual CLI, legacy loaders, verification, cache, and promotion entry points; unsigned/override cases |
| 175 | 62-66 | One identity compatibility comparison | Real cache lookup/resume across runner identity |
| 176 | 69-76 | Construction/comparison of identity data | Invalidation of every affected cache on each closure field change |
| 177 | 79-84 | A direct identity helper | Provenance obtained from an actual runner/adjudicator rather than caller labels |
| 178 | 87-97 | Adds a problem, interpretation, and claim in memory | Append-only gate/adjudication/promotion history and restart reconstruction |
| 179 | 100-105 | One synthetic legacy JSON file | All five named legacy record types through production loaders |
| 180 | 108-114 | Intake call plus a conditional assertion | Non-vacuous multi-interpretation release block through the release path |
| 181 | 116-140 | In-memory dependent-claim revocation | Transactional SCC propagation, persistence, and restart |
| 182 | 143-148 | Returns a pause dictionary; assertion is conditional | Backoff clock, lease preservation, resume, and no mathematical penalty through 120 seconds |
| 183 | 151-158 | Changes an in-memory lease holder | Crash recovery, fencing, and idempotent non-idempotent effects |
| 184 | 161-169 | Reuses `SubprocessSandbox` under a different label | Independent environment/container and result comparison |
| 185 | 172-185 | Injects a lambda returning kernel success | Clean pinned Lean build, source scan, no holes, independent checker |
| 186 | 188-196 | Injected vendor-status lambda rejects one label | Production vendor artifact path followed by local-kernel enforcement |
| 187 | 199-205 | Identity compatibility helper | Actual cached manifest/adjudicator mismatch rejection |
| 188 | 208-212 | Direct boolean gate-policy function | Conflicting referee bundles, precedence, taint, and release decision |
| 189 | 215-222 | OEIS result object is labeled T1 | Production workflow cannot promote it as proof/novelty |
| 190 | 225-228 | `novelty_gate("known")` identity mapping | A known historical Erdős problem run end-to-end and classified rediscovery |
| 191 | 231-234 | Direct baseline-validity boolean | Generated paired report with equal cost/Pareto evidence and rejection of an unpaired claim |

Count: **18 test functions exist and pass; 0 of 18 fully demonstrates the independently stated production acceptance criterion.** Some are valid unit checks for part of a criterion, especially F-REQ-181, F-REQ-186, and F-REQ-189, but partial unit coverage is not full acceptance.

## Circular, vacuous, or mock-as-integration test patterns

The following patterns recur and explain why a green suite did not validate the completion claims:

1. **Trusted fact supplied by the test:** Lean kernel success, formal equivalence, hardening, exactness, independent-checker success, and reviewer identity are injected as booleans, strings, or lambdas (`egmra/tests/test_lean.py:39-49,101-107,199-226`; `egmra/tests/test_release.py:151-166`).
2. **Label used as independence:** the same subprocess service is re-run with an “independent” environment label (`egmra/tests/test_compute.py:85-92`), and entry-point names are passed to one enforcer rather than invoking entry points (`egmra/tests/test_acceptance.py:54-60`).
3. **Conditional/vacuous assertions:** intake ambiguity, retrieval elaboration, and rate-limit acceptance include `... if condition else True` forms (`egmra/tests/test_intake.py:145-152`; `egmra/tests/test_retrieval.py:137-146`; `egmra/tests/test_acceptance.py:143-148`).
4. **Registry completeness treated as execution:** registering 13 ablation-name strings is treated as a complete ablation suite (`egmra/tests/test_eval.py:89-94`); storing a PostgreSQL endpoint string is treated as topology (`egmra/tests/test_meta.py:65-71`).
5. **Expected failure treated as implemented integration:** the M2 test asserts that PostgreSQL raises, and the container test checks policy metadata rather than execution (`egmra/tests/test_m2_scale.py:28-40`).

## Contradictions and interpretation changes

| Prior decision/claim | Contradictory evidence | Assessment |
|---|---|---|
| D-003: signed policy with enforcement regardless of environment | Empty shipped signature; unsigned policy accepted; direct `FeaturePolicy` objects need no signature | Material safety weakening |
| D-004: external services may be represented by interfaces/mocks | Requirements demand behavior and production reachability; report says none blocked | Interface readiness mislabeled `VERIFIED` |
| D-005: M2 PostgreSQL represented by an interface | F-REQ-167 explicitly requires real PostgreSQL or an honest blocker; implementation always raises | Direct requirement substitution |
| D-008: subprocess substitutes for container | Same-host subprocess lacks filesystem/container isolation and independent environment | Direct requirement substitution |
| D-010: every actionable requirement has real tested code | Data-only registries, unused controller/runner, always-raising adapters, and absent production paths | Contradicted |
| D-011: promotion uses signed policy | Promotion tests construct unsigned in-memory policy objects | Contradicted by tests |
| Ledger: gate summary is “non-collapsed” | `summary_label()` is driven by truth tier and omits I/N/S/R | Contradicted |
| Plan: `truth/graph.py` supplies SQLite + JSONL graph | SQLite is rebuilt from live graph in `truth/views.py`; event payloads cannot replay graph | Architecture drift |
| Plan: 20 acceptance tests | Specification, independent inventory, and suite contain 18 | Quantitative mismatch |
| Report: no blocked requirements | PostgreSQL/container deliberately unavailable; live external credentials/services unexercised | Status contradiction |

## Final disposition

The codebase merits credit for its size, organization, deterministic local utilities, typed models, local OEIS transform implementation, and green unit suite. Those facts support a status such as **substantial scaffold/prototype with selected implemented components**.

They do not support `VERIFIED` for all prior ledger rows or the final statement that this is a complete EGMRA system. At minimum, the prior statuses for M0, M1, M2, three nested searches, event-sourced persistence, formal verification, closed evidence validation, independent replay/refereeing, external integrations, evaluation/ablations, and all 18 acceptance criteria must be reopened and mapped one-to-one to F-REQ-001 through F-REQ-216.
