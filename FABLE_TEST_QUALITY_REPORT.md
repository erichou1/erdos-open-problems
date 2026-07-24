# FABLE Test Quality Report

## Conclusion

The audit-start suite was broad but architecturally weak. Its 241 EGMRA cases
were useful unit/contract tests, yet they frequently supplied the trusted fact
being tested, replaced an external or independent component with a lambda or
label, called a helper instead of a production entry point, or asserted registry
contents rather than behavior. The isolated baseline passed all 241 EGMRA and
420 combined cases while unsigned policy, forged evidence, event truncation,
host-file access, caller-created formal status, release-gate bypasses, and a
disconnected orchestrator remained possible.

The remediation suite adds independent negative, concurrency, restart,
corruption, revocation, freshness, privilege, network-boundary, and integration
tests. Final collection contains 786 cases versus the 420-case baseline—a net
366 additional collected regressions—plus 44 successful subtests versus 18 at
baseline. EGMRA grew from 241 to 555 cases and legacy coverage from 179 to 231,
across 22 additional test files as well as strengthened existing files. These
tests materially improve confidence, but they do not convert unavailable real
Lean, model-provider, PostgreSQL, successful OCI-computation, retrieval, or
evaluation behavior into verified behavior.

## Method

The audit inspected every audit-start EGMRA test file and asked:

> What meaningful defect could exist while every current test still passes?

“Current” in the subsystem gap table means the **audit-start 241-test suite**,
the suite on which the prior completion claim relied. New regression tests are
reported separately. A test was considered strong only when it:

- exercises a production path rather than merely a helper;
- independently computes expected behavior rather than importing the same
  implementation constant/helper;
- includes a meaningful failing/negative case;
- does not inject the critical success fact as a Boolean, status string, lambda,
  reviewer label, or mock of the component under test;
- tests prescribed failure behavior and state effects;
- covers persistence/restart, corruption/revocation, concurrency/fencing, or
  recovery where the requirement is durable/concurrent; and
- would fail if a relevant safety check were replaced with a permissive constant.

## Audit-start test inventory

| Surface | Files / cases | Result | Quality limitation |
|---|---:|---|---|
| Legacy `tests/` | 23 files / 179 cases plus 18 subtests | All passed | Does not invoke EGMRA research; CI selected only this tree. |
| EGMRA `egmra/tests/` | 21 files / 241 cases | All passed | Pytest undeclared and excluded from CI; mostly local helper/contract tests. |
| Combined audit-only pytest | 420 cases plus 18 subtests | All passed | Green result coexisted with reproduced security/correctness defects. |
| Section 13.6 | 18 functions | All passed | 0/18 proved the complete production acceptance criterion. |
| Skips / xfail / deselection / warnings | 0 reported | N/A | The issue was not hidden skips; it was insufficient test semantics. |

## Weak-test patterns found

### 1. The test supplies the fact being “verified”

- Lean tests passed `kernel_result=True`, injected a lambda returning
  `kernel_verified`, supplied arbitrary proof strings, or set
  `clean_offline_build=True`.
- Release tests directly constructed `KERNEL_CHECKED`/high-tier profiles and
  arbitrary reviewer identities.
- Evidence tests put `kernel_verified`, exactness, independence, or certificate
  IDs into caller-controlled findings and then checked the resulting status.

Such tests establish object plumbing, not kernel verification, independence, or
semantic validity.

### 2. A label substitutes for independence

- Computation replay reused the same service/host but changed
  `environment_label` to `independent`.
- Entry-point reachability passed strings such as `scheduler`, `verifier`, and
  `promoter` to one enforcer rather than invoking those paths.
- Parser/model/reviewer independence was established with differing string IDs.

### 3. Conditional or vacuous assertions

- Intake ambiguity used an `if not agreed` guard, so the critical release-block
  assertion could be skipped.
- Retrieval used `assert … if usable else True`, allowing the formal
  applicability check to disappear.
- Rate-limit acceptance used conditional assertions over a returned dictionary
  instead of driving a clock/lease/retry state machine.

### 4. Registry completeness is treated as execution

- Listing 13 ablation names was treated as an ablation suite.
- Recording four baseline names was treated as a paired equal-cost evaluation.
- A 10-layer topology dictionary and endpoint string were treated as running
  services.
- Algorithm-name tables and method-family constants were treated as three search
  engines and a program archive.

### 5. Expected failure is treated as an implemented integration

- The PostgreSQL test expected `connect()` to raise.
- The container test inspected a policy/command string while `run()` always
  raised.
- Model/Lean/OEIS tests injected fake callables and then credited the real
  interface.

### 6. Direct helper tests bypass production enforcement

- Acceptance tests called gate/policy/identity functions directly without CLI,
  cache, scheduler, graph, renderer, or publisher paths.
- Blackboard, revocation, leases, selection, search, learning, and aggregation
  had unit tests but no orchestrator caller.
- The 18 acceptance functions mostly asserted one local predicate rather than
  the required state transition and failure behavior.

## Major-subsystem defect-survival analysis and independent coverage

### Foundations, policy, and provenance

**What could pass all audit-start tests?** An unsigned policy enabling promotion;
a public fallback signing key; unknown or type-confused flags; duplicate JSON
keys; policy authentication performed at load but not enforcement; cache identity
strings supplied by callers rather than measured runners; mutable manifest
decisions outside the event log.

Audit-start tests explicitly expected an unsigned `FeaturePolicy(flags=...)` to
authorize promotion. Acceptance 1 tested three strings through one enforcer, not
three real entry points.

Independent coverage now includes:

- `test_unsigned_feature_policy_fails_closed`;
- `test_signed_feature_policy_is_bound_to_the_verification_key`;
- CLI default-policy, signing, overwrite, symlink, secret-denylist, and key
  absence tests; and
- negative policy schema/key verification in foundation/M0 tests.

Residual test gap: there is still no exhaustive runtime inventory proving one
policy decision is enforced by every legacy and EGMRA scheduler/cache/verifier/
publisher path.

### A. Truth plane

**What could pass all audit-start tests?** Valid-prefix truncation; deletion or
reordering of events; duplicate records; public-key forgery; two writers using
the same sequence/version; process restart losing all graph state; status
mutation before a failed append; forged exact/formal findings; direct status
mutation; revocation lost on restart; stale writer overwriting new state.

The audit-start tests created and inspected one live in-memory graph. They did
not reconstruct mathematical entities from JSONL and frequently supplied
trusted evidence fields.

Independent coverage now includes 20 truth-security tests plus four truth
snapshot tests:

- corrupted, truncated, missing, reordered, duplicated, payload-mutated and
  forged event histories;
- 32 concurrent writers and stale optimistic versions;
- complete problem/interpretation/claim/evidence/relation/branch replay;
- event-before-materialized-view failure atomicity;
- exact claim-bound HMAC evidence and semantic false-result rejection;
- denied direct status mutation;
- persisted transitive/SCC revocation; and
- signed replay-derived snapshots with claim/status/version/evidence/event-head
  freshness and intent binding.

Residual test gap: deleting/rolling back both the log and its local committed
head is not detectable without an external monotonic anchor; M2 database
transaction and multi-process/distributed recovery remain untested.

### B. Search plane

**What could pass all audit-start tests?** Controller overspending globally;
negative/unknown allocations; NaN/Inf utility; censored rate limits updating a
mathematical posterior; protected exploration starvation; fingerprints omitting
falsifiers; debt gaming by negative/disappearing obligations; blueprint cycles;
and every search object remaining unreachable from `research()`.

Independent expected values are now recomputed in
`test_additive_utility_matches_independent_arithmetic`; adversarial tests cover
finite input validation, real branch/global spend, censored failure updates,
protected selection, complete fingerprints, debt invariants, and cycle rejection.
Orchestrator tests show program/fingerprint/archive/blueprint/controller objects
are consumed in the CLI slice.

Residual test gap: no durable/restart search state, AO*/MCTS/MAP-Elites executor
comparison, full branch race, or genuine Lean proof-state search has run.

### C. Control plane

**What could pass all audit-start tests?** Expired lease renewal, reused fencing
tokens after restart, concurrent double acquisition, stale-worker writes,
corrupt persisted state acceptance, verifier capacity overflow/underflow,
non-finite backoff, overflow at huge attempts, and no production caller.

Independent coverage now uses controlled clocks/threads and persistent state:

- expiration/renew/reassign/fence rejection;
- restart with monotonic tokens and corrupt-state failure;
- exactly one concurrent acquisition winner;
- bounded thread-safe verifier pool; and
- exact 120-second backoff cap and invalid-input rejection.

The orchestrator adversarial suite also injects a stale fencing token and proves
worker output is rejected before evidence admission.

Residual test gap: no PostgreSQL/distributed lease transaction, multi-host
partition, large-scale starvation/deadlock schedule, or provider Retry-After
integration has been exercised.

### D. Communication plane and rendering

**What could pass all audit-start tests?** A verified-sounding summary with I0,
unknown novelty/significance/replay, unsigned or stale certificate rendering,
alternate direct render calls bypassing gates, signed fields mutated after
approval, or a release certificate created before promotion.

Independent Lean/release tests now cover unresolved-axis language, all render
paths for unsigned/forged/stale certificates, exact claim/interpretation/truth-
snapshot/gate/promotion subject binding, field mutation, stale event heads,
placeholder hashes, autonomy metadata, and sign-before-promotion rejection.

Residual test gap: `comms/render.py` and human intervention remain disconnected
from the main CLI renderer, and no API/web/publication output surface exists to
enumerate.

### E. Intake and Statement IR

**What could pass all audit-start tests?** Invented fallback binders, loss of
domains or definitions, empty input accepted, same-family parsers called
independent, a missing executable probe called passed, structured IR built and
then ignored in favor of raw text, and `release_blocked` bypassed by the
certificate path.

Strengthened tests now require both parsers to preserve binder/domain/conclusion
for a simple quantified statement; untyped binders and empty statements block;
semantic identity changes with domain/definition; and orchestrator/CLI tests
prove unresolved interpretation prevents certificate creation.

Residual test gap: the default still uses two local deterministic parsers rather
than demonstrated independent semantic model families; executable semantic
probes are necessarily limited by caller predicates; complex round-trip and
definition equivalence remain under-covered.

### F. Retrieval

**What could pass all audit-start tests?** Mutating a frozen packet after hashing;
changing conflicts/snapshot/coverage/query events without changing its ID;
duplicate theorem IDs; malformed hashes; negative meaning erased by token sets;
stale or partial results accepted; prompt injection treated as an instruction;
and one local index counted as four live indexes.

Independent tests now mutate every packet field, attempt nested collection
mutation, bind query hashes to the complete contract, reject duplicate IDs and
invalid limits, require SHA-256 provenance, and prove negation is not silently
removed by the import auditor.

Residual test gap: no live multi-source theorem/citation/provenance indexes,
cache freshness/retry/cancellation, prompt-injection corpus campaign, or actual
Lean elaboration of retrieved premises has run.

### G. OEIS transforms and HTTP

**What could pass all audit-start tests?** Floats/bools accepted as integers;
missing transform parameters; mutable transform steps; empty held-out data
passing; impossible prefix metadata; no-match promoted to T1; corrupted cache;
malformed JSON silently interpreted as no results; query injection; and OEIS
never reached by production.

Independent tests cover exact typing, parameter errors, immutable steps,
held-out counts, no-match T0, metadata constraints, cache hash/query binding,
malformed response and query validation. Orchestrator tests show generated
sequences can reach read-only OEIS without producing truth evidence.

Residual test gap: no live OEIS HTTP/rate-limit/schema-drift/recovery exercise;
the production loop does not independently recompute every match field from a
live response.

### H. Sandboxed computation

**What could pass all audit-start tests?** Host file/network/process/env access;
unbounded stdout; weak CPU/memory/wall enforcement; permissive non-JSON output;
false result retaining exhaustive classification; caller-supplied coverage;
caller label forging an independent replay; arbitrary checker self-approval;
restart loss/corruption/symlink attacks; container fallback to host execution.

Pre-fix direct probes reproduced `/etc/passwd` and `_socket` access. The first
independent adversarial batch produced **27 failures and 1 pass**. A later
checker-bypass red run produced **2 failures, 54 deselected**. The final focused
compute run recorded in `audit/compute_sandbox_remediation.md` passed **67/67**,
and four dependent truth/acceptance/orchestrator checks passed.

The adversarial suite covers capability denial, exact arithmetic, literal-true
classification, schema/serialization, stdout/output, CPU/memory/wall/process
limits, cleanup, measured independent executors, immutable service identity,
restart/corruption/symlink/root-swap handling, trusted checker registry, checked
certificate persistence, and no unsandboxed fallback.

Residual test gap: no compatible pinned Python/Sage OCI image completed a real
computation, so independent-container replay and full CAS/SAT/SMT/Sage backends
remain externally blocked/partial. The restricted interpreter is not an OS
sandbox.

### I. Lean L0-L5 and proof verification

**What could pass all audit-start tests?** Caller Boolean kernel success;
arbitrary status strings; any nonempty proof counted as equivalence; unrelated
certificate relabeled for a different relation; caller-created formal
certificate self-authentication; regex parse called trusted elaboration;
`hardened=True` creating T5; secrets exposed to checker; incomplete
import/axiom/proof audit; stale certificate used after truth changes.

The adversarial Lean/release suite now tests all of those cases and a positive
structured checker path. It binds the authenticated envelope to exact source,
environment, type, declaration, claims, artifacts, relation, and checker
identity; it rejects missing full audit fields and prevents secrets reaching the
checker subprocess.

Residual test gap: there is no installed pinned Lean/Mathlib toolchain, clean
offline `lake build`, real kernel replay, real proof-state portfolio, or live
Aristotle output. Local certificate-envelope behavior is meaningful; formal
mathematics remains `BLOCKED-EXTERNAL`.

### J. Agent authorities

**What could pass all audit-start tests?** Direct blackboard read/write without
authentication; cross-branch/packet access; token tampering/replay/expiry;
program worker granting itself release authority; self-approval; forged packet
hash; mutable shared slice; unauthorized proposal kind; confused-deputy
cross-lineage approval.

Four authority tests and orchestrator integration now cover authenticated scoped
access, tamper/expiry/cross-branch denial, packet-hash verification, immutable
slices, authority-specific proposal kinds, no release permission for program
workers, and separate lineage for approval.

Residual test gap: no distributed identity service, malicious real provider,
multi-process token revocation list, or human authority service has run.

### K. Adversarial verification T0-T5

**What could pass all audit-start tests?** Caller `hardened=True` creates T5;
unknown or correlated reviews promote; duplicate reviewer counted independent;
an attack says `passed=False` with no defect; residual uncertainty or
nonindependence ignored; finalized report mutated; higher tiers add only labels;
orchestrator synthesizes every attack from one Boolean.

Independent verification tests now reject each malformed/forged condition.
Orchestrator tests require all attacks, inject an independent defect, prove it
blocks release, and fail closed on a missing attack. The local mechanical
evaluator marks unavailable checks failed rather than manufacturing success.

Residual test gap: organizational independence and false-negative performance
have not been measured against multiple real model/tool families or blinded
experts; diversity fields remain partly attested labels.

### L. Release gates

**What could pass all audit-start tests?** Caller profile and booleans authorize
gates; one claim's gate authorizes another; stale/cached gate reused after new
truth event; intent/correspondence binding changes; one gate failure ignored by
an alternate entry point; certificate signed before promotion; public key allows
forgery.

Independent tests now require replay-derived `TruthSnapshot`, current event-log
head, exact claim/interpretation/intent/correspondence binding, distinct strong
keys, gate authorization HMAC, promotion authorization, and mutation/freshness
checks across sign/render paths.

Residual test gap: legacy publisher remains a separate authority, and live
novelty/significance/human decisions are not independently exercised.

### M. Selection, learning, orchestration, and evaluation

**What could pass all audit-start tests?** Missing hard constraints; invalid
feature/posterior ranges; duplicate problem IDs; state never affecting
selection; learning accepting truthy dictionaries; no persistent/revocable
facts; budget/runner ignored; false compute supporting claim; OEIS/Lean objects
unreachable; replay omitted from gate; unresolved interpretation released;
referee absent; benchmark answers leaked; ablations never run.

Independent selection tests cover all specified hard constraints, ranges,
posterior shapes, duplicate IDs/k, and finite acquisition inputs. Learning tests
reject forged calibration and truthy-dictionary memory promotion. Orchestrator
tests show budget/runner consumption, nonpositive/malformed rejection,
fence/evidence/claim binding, OEIS/Lean reachability without trust inflation,
problem-local learning quarantine, false compute rejection, replay-to-gate
handoff, current certificate, ambiguity block, referee defect, and missing-attack
failure.

Residual test gap: persistent learning does not yet change a real model or later
campaign; controller/posterior state is not restored as a full checkpoint;
external benchmark/equal-cost/ablation/time-capsule runs do not exist; no proof
that benchmark answers cannot leak through a real retrieval/model stack.

### External integrations and M2

**What could pass all audit-start tests?** Every live adapter fails or is never
called; authentication/timeout/retry/cancellation/rate-limit/schema-drift/
idempotency behavior is wrong; endpoint strings are counted as services;
Postgres/container methods always raise; no migrations or health checks.

Current negative tests improve fail-closed local boundaries, especially strict
OEIS response/cache handling, OCI unavailability, strong-key configuration,
checker secret isolation, and explicit unsupported paths. They do not prove real
service success/recovery.

Residual test gap: live Lean/lake, model providers, Aristotle, OEIS HTTP,
PostgreSQL, compatible OCI computation, theorem/citation retrieval, migrations,
and service topology remain unexecuted or unavailable.

## Section 13.6 test-quality result

The 18 audit-start functions are individually analyzed in
`FABLE_LEDGER_DISCREPANCIES.md`. In summary:

- all 18 passed;
- several were valid unit checks of a small subpredicate;
- none invoked and demonstrated its complete production criterion;
- acceptance 5 did not replay the graph;
- acceptance 10 did not test crash/fencing/idempotent effects;
- acceptance 11 relabeled the same subprocess;
- acceptance 12 injected kernel success;
- acceptance 18 called a Boolean predicate instead of running paired baselines.

Passing function names that mirror specification prose are not acceptance
evidence without the specified production state transition and negative case.

## New adversarial regression inventory at report snapshot

Static function counts below are not runtime parameter counts and are not a
completion metric.

| New file | Static tests | Principal coverage |
|---|---:|---|
| `test_adversarial_truth_security.py` | 20 | Policy, event attacks/concurrency/replay, evidence forgery, false compute, status authority, atomicity, stale writers, restart revocation. |
| `test_truth_snapshots.py` | 4 | Replay-derived current snapshots and intent binding. |
| `test_adversarial_authorities.py` | 4 | Capability scope, tamper/expiry, packet/proposal authority, self-approval. |
| `test_adversarial_control.py` | 8 | Durable fenced leases, concurrency/corruption, pool bounds, backoff validation. |
| `test_adversarial_search.py` | 9 | Independent arithmetic, budgets, censoring, exploration, fingerprints, debt, cycles. |
| `test_adversarial_retrieval.py` | 5 | Complete packet/query identity, deep immutability, duplicate/provenance/negation. |
| `test_adversarial_oeis.py` | 7 | Exact typing, held-out semantics, cache integrity, malformed HTTP/query handling. |
| `test_adversarial_compute_security.py` | 36 functions / 58 runtime cases in the recorded focused suite | Capability/resource/schema/replay/persistence/checker/OCI security. |
| `test_adversarial_lean_release.py` | 31 | Kernel/equivalence/certificate/gate/promotion/render/truth freshness and checker boundary. |
| `test_adversarial_verification.py` | 6 | T5 forgery, aggregation, referee immutability/independence. |
| `test_adversarial_selection.py` | 5 | Hard constraints and numeric/schema validation. |
| `test_adversarial_learning.py` | 4 | Calibration validation and forged persistent fact rejection. |
| `test_adversarial_orchestrator.py` | 15 | Real closed-loop handoffs and fail-closed failure injection. |
| **Total** | **154 static tests** | Additional strengthened tests also exist in original files. |

Final collected counts may change while remediation finishes; the exact final
count must be taken from a fresh `pytest --collect-only` run in
`FABLE_FINAL_VERIFICATION.md`.

## Mutation-style validation

### Committed-head bypass mutant

A current source copy was isolated at `/tmp/fable-mutation-head`. One protection
was intentionally removed only in that temporary copy: the call to
`EventLog._verify_head(events)` during load. The targeted regression then failed
as required:

```text
cd /tmp/fable-mutation-head
/tmp/erdos-baseline.t2afE1/venv/bin/python -m pytest -q \
  egmra/tests/test_adversarial_truth_security.py::test_event_log_detects_valid_prefix_truncation

FAILED: DID NOT RAISE EventLogError
1 failed in 0.08s
```

The unmodified working implementation passed the identical test:

```text
cd /Users/eric/workspace/erdos/erdos_problems
/tmp/erdos-baseline.t2afE1/venv/bin/python -m pytest -q \
  egmra/tests/test_adversarial_truth_security.py::test_event_log_detects_valid_prefix_truncation

1 passed in 0.06s
```

This proves the truncation regression is sensitive to a real critical safety
bypass rather than merely checking object existence or a repeated constant.

### Natural pre-fix mutants and red/green TDD evidence

The audit-start implementations served as natural mutants for many protections:

- arbitrary compute checker injection: red **2 failed, 54 deselected**, then
  green inside the recorded **67 passed** focused compute suite;
- host capability access/false classification/persistence loss: first
  adversarial compute batch **27 failed, 1 passed**, then **67 passed** after
  remediation;
- unsigned policy, event truncation/concurrent sequence, forged evidence, false
  computation, caller T5, packet mutation, cache corruption, lease fence reuse,
  and truthy-memory admission were each reproduced before their regression was
  made green.

Only compute retains full raw red-count evidence in
`audit/compute_sandbox_remediation.md`; other red-first observations were made
during TDD but final claims should rely on the reproducible pre-fix scripts/tests
and fresh final green commands, not on an unpreserved console transcript.

## Tests that would still pass after constant replacement at audit start

Representative examples:

- Returning a fixed list of the 13 required ablation names would pass the
  “ablation” test.
- Returning the configured topology-layer strings would pass topology tests even
  if no service could start.
- Returning `True` from injected kernel/checker lambdas passed Lean/formal tests.
- Returning a fixed gate profile created by the test could pass gate tests
  without any graph evidence.
- Treating all PostgreSQL calls as “unavailable” passed because failure was the
  expected test result.
- Returning the supplied “independent” environment label passed replay
  independence.
- Returning `passed=True` for non-executed intake probes could pass intent tests.

The added tests target these constant-survival defects by deriving expectations
from independent arithmetic/state, corrupting or mutating inputs, invoking
production handoffs, and requiring failures to change persisted/release state.

## Honest final quality assessment

The test suite is now substantially more adversarial and much better aligned
with the local M1 trust boundaries. It meaningfully detects bypasses in event
integrity, evidence promotion, resource/authority/fence checks, packet/cache
identity, formal/gate authorization, HTTPS/TLS ingestion, and orchestration
handoffs. The final warning-as-error runs passed 555 EGMRA cases and 786 total
cases plus 44 subtests; the fresh focused adversarial/security run passed 349
cases plus 25 subtests. All 18 §13.6-named test functions passed, but only 4 of
the 18 full criteria meet the traceability matrix's complete `VERIFIED`
standard.

It remains insufficient evidence for complete specification conformance because
large classes of behavior are absent or externally blocked: real kernel proof,
full OCI compute, distributed PostgreSQL transactions, model/provider
independence, live retrieval/OEIS, service deployment, persistent learning, and
controlled benchmark/ablation evaluation. Those limitations must remain
`PARTIAL`, `UNVERIFIED`, `UNREACHABLE`, `TEST-ONLY`, or `BLOCKED-EXTERNAL`, not be
upgraded by test count.
