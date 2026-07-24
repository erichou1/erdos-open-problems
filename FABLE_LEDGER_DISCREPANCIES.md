# FABLE Ledger Discrepancies

## Scope and method

This report compares the independent 216-requirement inventory in
`FABLE_INDEPENDENT_REQUIREMENTS.md` with `IMPLEMENTATION_LEDGER.md`,
`IMPLEMENTATION_PLAN.md`, `DECISIONS.md`, `FINAL_VERIFICATION_REPORT.md`, the
audit-start implementation, and the audit-start test suite. The comparison was
performed only after the independent inventory had been completed. All code and
line observations in the pre-fix sections below refer to the isolated audit-start
snapshot at commit `4b4ec96f1c81492af02f814c65825a5106e0af60`, not to later
remediation edits.

The prior ledger's rule was effectively "a named object exists and a test
passes." The specification requires substantially more: faithful semantics,
production reachability, integration, positive and negative runtime behavior,
and prescribed failure handling. Consequently, an apparent mapping to a prior
row does not validate an F-REQ.

## Executive discrepancy

The prior completion conclusion is rejected.

| Measure at audit start | Independently reproduced result | Meaning |
|---|---:|---|
| Prior ledger rows | 120 | Every row says `VERIFIED`; this is a ledger fact only. |
| Independent requirements | 216 | Includes separately testable failure, integration, milestone, acceptance, security, and evaluation obligations. |
| Difference | 96 | Not mechanically 96 omitted clauses: many prior rows merged multiple requirements, but the merge erased independently observable obligations. |
| EGMRA tests | 241 | Passed in the isolated audit baseline. |
| Combined tests | 420 plus 18 successful subtests | Passed, with no skip/warning categories. |
| Section 13.6 test functions | 18 | All passed, but 0/18 demonstrated the complete production acceptance criterion. |

The prior report confused four different levels of evidence:

1. a type, constant, protocol, or file exists;
2. a helper behaves on a local unit case;
3. a component is integrated and reachable from a production entry point; and
4. the specified end-to-end behavior, including failures, has run.

Only the fourth level can establish the architecture-wide completion claims.

## Assessment of each advertised claim

| Prior claim | Assessment | Evidence |
|---|---|---|
| 92 source modules | **SUPPORTED** | Exactly 92 non-test, non-`__init__.py` modules at audit start. |
| 22 packages | **SUPPORTED** | 22 initializer-bearing directories including the root package and the test package; not 22 operational services. |
| Approximately 10.8k source LOC | **SUPPORTED** | 10,839 non-test Python lines at audit start. |
| 241 EGMRA tests | **SUPPORTED** | Pytest collected and passed 241 audit-start EGMRA cases. |
| 420 passing tests overall | **SUPPORTED** | Isolated pytest run passed 420 collected cases plus 18 unittest subtests. |
| 120 requirements, all verified | **FALSE** | The file has 120 `VERIFIED` rows; independent extraction found 216 obligations and runtime counterexamples falsified numerous rows. |
| Four complete operational planes | **PARTIALLY SUPPORTED** | Four package groupings existed. Normal production did not integrate them, and the communication/release boundary trusted caller data. |
| Three complete nested searches | **FALSE** | Formula/data helpers existed; `research()` invoked none of the program archive, AND/OR controller, or Lean proof-state search. |
| All listed subsystems implemented | **MISLEADING** | Local transforms and schemas coexist with injected callables, constant registries, unreachable modules, and always-raising external adapters. |
| M0 safety repairs complete | **FALSE** | Unsigned policy could enable promotion; public fallback trust keys and disconnected quarantine/telemetry paths remained. |
| M1 end-to-end slice genuine | **FALSE** | The graph could not replay mathematical state, the loop hardcoded acquisition/referee evidence, and its release path bypassed intake release blocks. |
| M2 complete | **FALSE** | PostgreSQL and container methods deliberately raised; object storage/transactions/concurrent production services were not present. |
| All 18 Section 13.6 criteria passing | **FALSE** | Eighteen unit tests passed, but none proved its full production criterion. |
| No stubs, TODOs, placeholders, or errors | **MISLEADING** | Textual marker scan was clean; functional placeholders such as always-raising Postgres/container methods and status-only topology remained. |
| External interfaces correctly implemented | **UNVERIFIABLE / PARTIAL** | Some request shapes and fail-fast facades existed, but real services, responses, recovery, schema drift, cancellation, and readiness were not exercised. |

Claim assessment count: 5 supported raw-count claims, 1 partially supported
architectural claim, 2 misleading claims, 6 false semantic claims, and 1
unverifiable/partial external-readiness claim. The raw counts do not rescue the
semantic completion conclusion.

## Requirement-indexed discrepancies

The `D-LEDGER-*` records below are requirement/ledger crosswalks, not duplicate
formal vulnerability records. Reproduction commands, severity, exact symbols,
root cause, fixes, regression tests, post-fix verification, residual limitations,
and confidence are recorded once under the corresponding `FBL-*` finding in
`FABLE_REMEDIATION_LOG.md` and `FABLE_SECURITY_AUDIT.md`.

### D-LEDGER-001 — Independent contracts were merged into presence-based rows

- **F-REQs:** F-REQ-001 through F-REQ-216, especially F-REQ-026,
  F-REQ-148, and F-REQ-174 through F-REQ-191.
- **Prior rows:** all 120 rows; particularly REQ-013, REQ-014, REQ-020q,
  REQ-141, REQ-142, and REQ-144.
- **Discrepancy:** The ledger collapses separately observable invariants,
  failures, integrations, and milestone technologies into broad component rows.
  It then treats file presence plus a passing unit test as verification.
- **Concrete contradictions:** `IMPLEMENTATION_PLAN.md` says “20 acceptance
  tests” while the specification and suite contain 18. REQ-144 marks the whole
  acceptance section verified because 18 functions pass. REQ-142 silently
  changes “M2 scalable MVP” into “interfaces + local backends.”
- **Impact:** Omitted failure behavior and unreachable integrations disappear
  from status accounting, allowing every row to be labeled `VERIFIED`.

### D-LEDGER-002 — M0 signed-policy and authoritative-decision obligations were weakened

- **F-REQs:** F-REQ-014, F-REQ-015, F-REQ-017, F-REQ-149 through
  F-REQ-156, F-REQ-174, F-REQ-175 through F-REQ-179, F-REQ-204.
- **Prior rows:** REQ-011, REQ-012, REQ-020b, REQ-020g, REQ-020h,
  REQ-061/061b, REQ-062, REQ-140, REQ-180.
- **Expected:** Authenticated policy at every real entry point; no fallback key;
  behavior-closure identity; closed kind validators; append-only promotion and
  adjudication decisions; deterministic derived manifests; production loader
  quarantine and complete telemetry.
- **Observed pre-fix:** The checked-in policy had an empty signature;
  `load_policy()` accepted it and legacy bare flags were signed with a public
  development key. `PolicyEnforcer` authenticated flags only conditionally.
  `promote_verified_run.py` rewrote `manifest.json` in place. Quarantine and
  telemetry helpers had only test callers. A generic verifier accepted caller
  `passed`, kind, verifier, and hashes.
- **Why prior evidence was inadequate:** Tests called unsigned in-memory
  `FeaturePolicy` instances “signed,” and acceptance 1 supplied entry-point
  *names* to one helper instead of invoking each entry point.
- **Prior decision conflict:** D-003 explicitly allowed a deterministic local
  dev key and D-011 asserted signed enforcement; the implementation did not
  satisfy the latter. The local-key interpretation materially weakened the
  threat model.

### D-LEDGER-003 — Event presence was reported as event-sourced truth

- **F-REQs:** F-REQ-006, F-REQ-017, F-REQ-106 through F-REQ-119,
  F-REQ-128, F-REQ-153, F-REQ-157, F-REQ-178, F-REQ-181, F-REQ-183,
  F-REQ-197, F-REQ-200.
- **Prior rows:** REQ-004, REQ-029, REQ-045, REQ-060 through REQ-063,
  REQ-141, REQ-164.
- **Expected:** The append-only signed event stream and artifacts reconstruct
  the typed graph; concurrent/stale writers are fenced; checkpoints capture
  complete identity; corruption, revocation, and SCC changes survive restart.
- **Observed pre-fix:** Events contained IDs/status metadata but not problem,
  interpretation, claim, evidence, relation, or certificate bodies.
  `EpistemicGraph` always started with empty dictionaries. SQLite was rebuilt
  from live memory. Mutations happened before append. The log used a public
  fallback key, had no lock/CAS/fsync, and a valid-prefix truncation was
  accepted. Leases were in-memory and lacked fencing tokens.
- **Runtime counterexample:** Constructing a new graph over an existing event
  file yielded no mathematical state; removing a valid suffix preserved hash
  integrity; two writers could begin from the same sequence.
- **Why prior evidence was inadequate:** Acceptance 5 created three objects in
  one process and never reconstructed them; acceptance 8 revoked an in-memory
  chain without transactional restart evidence.

### D-LEDGER-004 — The 17-step loop and four planes were replaced with a deterministic fixture script

- **F-REQs:** F-REQ-005, F-REQ-007 through F-REQ-012, F-REQ-018,
  F-REQ-034, F-REQ-035, F-REQ-040 through F-REQ-052, F-REQ-077,
  F-REQ-157 through F-REQ-165, F-REQ-173, F-REQ-193, F-REQ-205,
  F-REQ-206.
- **Prior rows:** REQ-003 through REQ-010, REQ-013, REQ-014,
  REQ-024 through REQ-032, REQ-044 through REQ-049, REQ-089,
  REQ-141, REQ-143, REQ-181, REQ-182.
- **Expected:** A reachable closed loop in which state changes selection,
  selection leases real work, work produces authenticated evidence, evidence
  changes epistemic state, verification changes future control, and release and
  learning consume current verified state.
- **Observed pre-fix:** `research()` ignored its effective runner and budget,
  discarded cold-pass output, hardcoded acquisition, selected only the first
  interpretation, repeatedly invoked one deterministic worker, and synthesized
  all referee attacks from one Boolean. It did not import/call selection,
  search controller/blueprint/archive, Lean service, OEIS, learning, leases, or
  throttling. The existing repository search/continuous pipelines did not import
  the EGMRA orchestrator.
- **Why prior evidence was inadequate:** Four orchestrator tests asserted phase
  labels and a local finite computation. A directory per plane and a
  `research()` function named for 17 stages are not integration evidence.

### D-LEDGER-005 — Three nested searches were names and formulas, not executors

- **F-REQs:** F-REQ-007, F-REQ-008, F-REQ-018, F-REQ-043 through
  F-REQ-046, F-REQ-049, F-REQ-061, F-REQ-067 through F-REQ-079,
  F-REQ-162, F-REQ-170, F-REQ-198, F-REQ-199, F-REQ-206.
- **Prior rows:** REQ-005, REQ-006, REQ-025, REQ-028, REQ-046,
  REQ-080 through REQ-089, REQ-162, REQ-163, REQ-182.
- **Observed pre-fix:** `algorithms.py` was a name registry plus scoring
  functions; `proof_state.py` held a formula/table but ran no Lean action;
  controller allocation could overspend its global budget; program archive,
  blueprint, controller, lease manager, verifier pool, and throttle were not
  called from the CLI flow.
- **Why prior evidence was inadequate:** Unit arithmetic and enum completeness
  were substituted for search-state transitions, branch competition,
  persistence, restart, failure, budget exhaustion, and production handoffs.

### D-LEDGER-006 — Intake did not enforce the stated translation firewall

- **F-REQs:** F-REQ-004, F-REQ-022, F-REQ-029, F-REQ-036 through
  F-REQ-039, F-REQ-093, F-REQ-106, F-REQ-158, F-REQ-180, F-REQ-210.
- **Prior rows:** REQ-002, REQ-020m, REQ-021, REQ-040, REQ-091,
  REQ-141, REQ-144.
- **Observed pre-fix:** Complete source metadata was not frozen. Two local
  heuristic parsers were deemed independent by different `parser_id` strings.
  Missing boundary/counterexample probes returned `passed=True` while saying
  “not run.” The target package accepted one candidate and defaulted integrity
  flags true. A parser disagreement set `release_blocked`, but the CLI still
  signed and rendered a verified-sounding release for `fx-true-square`.
- **Weak test:** The ambiguity test used a conditional assertion; acceptance 7
  stopped at the lattice and never exercised release.
- **Prior decision conflict:** D-002 treated two local parsers as independent,
  despite the specification requiring different model families or a
  deterministic parser plus a separately implemented semantic model.

### D-LEDGER-007 — Retrieval packet and import-audit semantics were overstated

- **F-REQs:** F-REQ-005, F-REQ-030, F-REQ-040 through F-REQ-042,
  F-REQ-056 through F-REQ-059, F-REQ-087 through F-REQ-089,
  F-REQ-159, F-REQ-169.
- **Prior rows:** REQ-014, REQ-023, REQ-043, REQ-053 through REQ-055,
  REQ-141, REQ-142, REQ-183.
- **Observed pre-fix:** Only one caller-supplied local lexical index existed,
  not four linked indexes. `SourcePacket` and nested collections were mutable;
  its hash omitted conflicts, snapshot time, re-entry reason, full query events,
  and coverage. `ImportAuditor` used token containment as logical consequence,
  erasing important distinctions such as negation. The CLI used one dummy
  theorem and did not run a formal applicability audit.
- **Weak test:** A central retrieval assertion used `... if usable else True`.
  Live retrieval, stale cache behavior, malformed results, and prompt injection
  were not exercised.

### D-LEDGER-008 — OEIS local utilities were reported as a complete integration

- **F-REQs:** F-REQ-055, F-REQ-081 through F-REQ-086, F-REQ-159,
  F-REQ-169, F-REQ-189.
- **Prior rows:** REQ-020j, REQ-042, REQ-051, REQ-052, REQ-141.
- **Observed pre-fix:** Twenty local transforms and a requests-capable client
  existed, but the orchestrator never called them and tests injected a fake
  fetcher. Integer transforms accepted floats; malformed remote JSON could
  silently become empty results; cache content was not cryptographically
  checked; empty held-out sets could pass; a no-match path could be labeled T1.
- **Why prior evidence was inadequate:** Transform unit examples and a direct
  `T1` label assertion did not prove production triggering, provenance,
  malformed/offline behavior, or that OEIS could never promote truth/novelty.

### D-LEDGER-009 — The computation “sandbox” and independent replay labels were not security evidence

- **F-REQs:** F-REQ-010, F-REQ-023, F-REQ-024, F-REQ-062,
  F-REQ-063, F-REQ-105, F-REQ-160, F-REQ-168, F-REQ-184,
  F-REQ-194, F-REQ-203.
- **Prior rows:** REQ-008, REQ-020d, REQ-047, REQ-141, REQ-142.
- **Observed pre-fix:** The same-host subprocess monkey-patched selected Python
  networking and cleared env variables but could read `/etc/passwd`, import
  `_socket`, access the host filesystem, and offered no container boundary.
  `ContainerSandbox.run()` always raised. “Independent replay” reused the same
  backend and trusted a caller label. Caller metadata could classify a false
  result as exhaustive/certificate-checked evidence.
- **Weak tests:** The same service was rerun under label `independent`; a caller
  checker lambda inspected the artifact's own output. Acceptance 11 did not use
  a distinct measured environment.
- **Prior decision conflict:** D-008 explicitly substituted subprocess controls
  for container isolation. That is a documented weakening, not verification.

### D-LEDGER-010 — Lean and L0-L5 were injectable facades

- **F-REQs:** F-REQ-003, F-REQ-009, F-REQ-013, F-REQ-019,
  F-REQ-064, F-REQ-069, F-REQ-088, F-REQ-090 through F-REQ-105,
  F-REQ-151, F-REQ-161, F-REQ-171, F-REQ-185, F-REQ-186.
- **Prior rows:** REQ-007, REQ-011, REQ-020, REQ-020e, REQ-048,
  REQ-054, REQ-090 through REQ-099, REQ-09A, REQ-141, REQ-142.
- **Observed pre-fix:** “Elaboration” was regex/static parsing;
  `verify_declaration()` accepted caller `kernel_result=True` or an injected
  lambda; any non-empty proof string could establish equivalence; hardening
  trusted booleans and a dummy archive. `searchPremises`/`tryActions` were not
  implemented as real operations, and no pinned Lean project/toolchain existed.
- **Weak tests:** Always-success lambdas, status strings, arbitrary proof text,
  and caller hardening booleans supplied the very facts under test. Acceptance
  12 was not a kernel build; acceptance 13 covered only one direct helper path.

### D-LEDGER-011 — Truth tiers, referee independence, gates, and release could be caller-manufactured

- **F-REQs:** F-REQ-002, F-REQ-003, F-REQ-020, F-REQ-027,
  F-REQ-032, F-REQ-033, F-REQ-047, F-REQ-050, F-REQ-051,
  F-REQ-109 through F-REQ-115, F-REQ-120 through F-REQ-134,
  F-REQ-163, F-REQ-177, F-REQ-188, F-REQ-216.
- **Prior rows:** REQ-001, REQ-009, REQ-020f, REQ-020p,
  REQ-027, REQ-049, REQ-061/061b, REQ-110 through REQ-114,
  REQ-141.
- **Observed pre-fix:** Evidence validators trusted HMAC-unbound generator
  findings such as `kernel_verified`, exactness, independence, and formal
  certificate IDs. T5 could arise from caller `hardened=True`. The orchestrator
  manufactured ten referee passes from one Boolean and hardcoded diversity
  strings. Release gates accepted a caller-created `EvidenceProfile` and
  booleans. Release used a public fallback key and signed before promotion.
  `summary_label()` was truth-tier-driven and could compress I/N/S/R.
- **Weak tests:** Tests constructed `KERNEL_CHECKED` profiles, arbitrary reviewer
  lineages, and success flags directly. They proved serialization of assertions,
  not the assertions' provenance.

### D-LEDGER-012 — Authority prompts and tuples were reported as least privilege

- **F-REQs:** F-REQ-027, F-REQ-035, F-REQ-044, F-REQ-046,
  F-REQ-060, F-REQ-119, F-REQ-122, F-REQ-173, F-REQ-196 through
  F-REQ-198, F-REQ-202, F-REQ-203.
- **Prior rows:** REQ-020k, REQ-024, REQ-031, REQ-044,
  REQ-110, REQ-143, REQ-162, REQ-166.
- **Observed pre-fix:** `Authority` records, forbidden-action tuples, role
  prompts, and blackboard read-slice dataclasses existed, but no authenticated
  capability boundary enforced actions. Blackboard was not called by the
  orchestrator. Model/authority identity was caller-supplied.
- **Why prior evidence was inadequate:** Prompt text and `is_forbidden()` unit
  predicates do not prevent direct method calls, cross-agent forgery,
  self-approval, confused-deputy behavior, or stale-worker writes.

### D-LEDGER-013 — Learning and selection were disconnected in-memory records

- **F-REQs:** F-REQ-008, F-REQ-012, F-REQ-043, F-REQ-052 through
  F-REQ-054, F-REQ-065, F-REQ-067, F-REQ-068, F-REQ-121,
  F-REQ-143, F-REQ-172, F-REQ-207, F-REQ-214, F-REQ-215.
- **Prior rows:** REQ-006, REQ-010, REQ-020i, REQ-022,
  REQ-041, REQ-04A, REQ-065, REQ-081, REQ-132, REQ-183.
- **Observed pre-fix:** Selection posteriors and memory buckets were in-memory
  and not reached by orchestration. `LongTermMemory` admitted records using
  truthy field-presence checks; no current graph snapshot, release-gate
  attestation, replay, revocation, or persistence bound a verified fact.
  Calibration/evaluation did not change a later production decision.
- **Weak tests:** Tests passed truthy dictionaries and asserted a list grew;
  selector tests called formulas directly but never showed production state
  changing future work.

### D-LEDGER-014 — Evaluation declarations were counted as experiments

- **F-REQs:** F-REQ-021, F-REQ-025, F-REQ-135 through F-REQ-147,
  F-REQ-164, F-REQ-191, F-REQ-192, F-REQ-207, F-REQ-210 through
  F-REQ-215.
- **Prior rows:** REQ-130 through REQ-135, REQ-145, REQ-170,
  REQ-183.
- **Observed pre-fix:** Evaluation levels, baseline names, ablation names, metric
  dataclasses, and benchmark manifests existed. No benchmark runner, paired
  equal-cost experiment, ablation arm, causal estimate, time-capsule evaluation,
  blind expert workflow, or external dataset was executed. The frozen config
  hash omitted material fields. `ProgressLedger.signal_value()` returned zero
  for every input.
- **Weak tests:** Registering 13 strings was treated as running 13 ablations;
  storing four baseline names was treated as a comparison; a two-Boolean helper
  stood in for acceptance 18.

### D-LEDGER-015 — Full-scale/M2 protocols and descriptions were counted as services

- **F-REQs:** F-REQ-066, F-REQ-166 through F-REQ-173,
  F-REQ-193 through F-REQ-201, F-REQ-207, F-REQ-209.
- **Prior rows:** REQ-04B, REQ-142, REQ-143, REQ-160 through
  REQ-165, REQ-183.
- **Observed pre-fix:** `PostgresEventStore.connect()` always raised;
  `ContainerSandbox.run()` always raised; `ServiceTopology` stored endpoint
  strings; service modules were protocols/descriptors; no worker processes,
  health checks, network boundary, transactional SCC updates, compatible work
  stealing, or congestion-controlled service runtime existed.
- **Weak tests:** M2 tests *expected* PostgreSQL to raise and inspected a
  container policy string. Registering `postgres://...` was counted as a
  topology test.
- **Prior decision conflict:** D-004/D-005 redefined required integrations as
  interfaces and mocks, while `FINAL_VERIFICATION_REPORT.md` declared zero
  blocked requirements. F-REQ-167 expressly requires real PostgreSQL behavior
  or an honest external blocker.

## Section 13.6 acceptance-test discrepancy

The audit-start file contains exactly 18 numbered functions and all passed. The
table distinguishes partial unit evidence from the specified acceptance behavior.

| F-REQ | What the prior test actually did | Material evidence it omitted |
|---|---|---|
| F-REQ-174 | Called one policy helper using entry-point-name strings. | Actual scheduler, cache, verifier, CLI, legacy loader, and promotion entry points; unsigned/override bypasses. |
| F-REQ-175 | Compared two identity values. | A real cache lookup/resume rejected across runner identity. |
| F-REQ-176 | Constructed identity data. | Every behavior-closure mutation invalidating each affected cache. |
| F-REQ-177 | Called an identity helper. | Identity captured from a real runner/adjudicator, not caller labels. |
| F-REQ-178 | Added three in-memory graph objects. | Restart reconstruction and append-only gate/adjudication/promotion history. |
| F-REQ-179 | Quarantined one synthetic JSON file. | All five named legacy record types through production loaders. |
| F-REQ-180 | Built intake and asserted conditionally. | Non-vacuous ambiguity and release blocking at every release entry point. |
| F-REQ-181 | Revoked an in-memory dependency chain. | Transactional SCC propagation persisted and replayed after restart. |
| F-REQ-182 | Returned a pause dictionary with conditional assertion. | Controlled clock, Retry-After, 120-second cap, lease preservation, resume, and no mathematical penalty. |
| F-REQ-183 | Changed an in-memory lease holder. | Crash recovery with monotonically fenced, idempotent external effects. |
| F-REQ-184 | Reused the same subprocess with a new label. | Distinct measured environment/container and comparison of durable artifacts. |
| F-REQ-185 | Injected a lambda returning kernel success. | Clean pinned offline Lean build, no holes/unsafe imports/axioms, and independent checker. |
| F-REQ-186 | Rejected one injected vendor label. | Every vendor promotion path followed by mandatory local kernel replay. |
| F-REQ-187 | Compared identity values. | Cached manifest rejection after actual adjudicator change. |
| F-REQ-188 | Called a direct Boolean gate policy. | Conflicting referee bundles, taint, precedence, and production release disposition. |
| F-REQ-189 | Constructed a T1 OEIS result. | Production workflow proving it cannot affect truth or novelty promotion. |
| F-REQ-190 | Mapped the string `known` to a novelty verdict. | End-to-end historical known-problem run classified as rediscovery. |
| F-REQ-191 | Called a two-Boolean baseline helper. | Generated paired equal-cost/Pareto report and rejection of an unpaired superiority claim. |

Conclusion: **18/18 functions existed and passed; 0/18 demonstrated the full
criterion before remediation.** Several were useful unit checks, but none
justified the aggregate acceptance claim.

## Contradictions among plan, decisions, code, tests, and report

| Prior statement | Contradictory evidence | Finding |
|---|---|---|
| D-003 / D-011: signed policy is enforced | Empty signature accepted, public local key, unsigned test policies | Safety requirement weakened. |
| D-004: interfaces/mocks complete external requirements | Real services unexercised and recovery/schema behavior absent | Interface readiness mislabeled as completion. |
| D-005: Postgres interface satisfies M2 | `connect()` always raises; no transactional behavior | Direct substitution for F-REQ-167. |
| D-008: subprocess is a sandbox | Host filesystem and low-level network modules reachable | Direct substitution for F-REQ-160/F-REQ-194. |
| D-010: all actionable requirements have real tested code | Status registries, unused controller, always-raising adapters, absent production paths | Contradicted. |
| REQ-001: summary is non-collapsed | Summary label was primarily truth-tier-driven | Communication semantics contradicted. |
| REQ-029/REQ-062: event log authoritative | Events could not recreate graph bodies | Architecture drift. |
| Plan: 20 acceptance tests | Specification and suite contain 18 | Quantitative contradiction. |
| Report: no blocked requirements | Lean, Postgres, container, provider, Aristotle, live OEIS unavailable/unexercised | Status contradiction. |
| Report: M1 genuine | CLI true case could release despite `release_blocked`; another expected-verified fixture triaged | Runtime contradiction. |

## Disposition

The prior ledger is useful as a catalog of intended files and local unit tests,
but not as an authoritative completion ledger. Every `VERIFIED` status must be
reopened against F-REQ-001 through F-REQ-216. In particular, package presence,
protocol conformance, injected success, and local mocks must be classified as
`UNREACHABLE`, `TEST-ONLY`, `PARTIAL`, `UNVERIFIED`, or `BLOCKED-EXTERNAL` as
appropriate rather than promoted to `VERIFIED`.
