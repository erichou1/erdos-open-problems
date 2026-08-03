# FABLE Independent Adversarial Audit Report

## Scope and evidence rule

This report is the final synthesis of the independent audit of
`AUTONOMOUS_MATH_RESEARCH_ARCHITECTURE_2026.md`. The controlling inventory is
the 216 independently extracted requirements in
[`FABLE_INDEPENDENT_REQUIREMENTS.md`](FABLE_INDEPENDENT_REQUIREMENTS.md), not
the prior agent's 120-row ledger. A requirement is called `VERIFIED` only when
its specified semantics, production reachability, required integration,
positive and negative behavior, runtime evidence, and failure behavior were all
demonstrated. A class, mock, interface, passing test, or locally authenticated
protocol does not establish an unavailable external service or a disconnected
production path.

The audit began from commit
`4b4ec96f1c81492af02f814c65825a5106e0af60` on the dedicated branch
`audit/egmra-independent-remediation-20260713`. The pre-existing dirty worktree
was preserved. The authoritative specification was not modified. Detailed
commands and environment evidence are in
[`FABLE_BASELINE_VERIFICATION.md`](FABLE_BASELINE_VERIFICATION.md) and
[`FABLE_FINAL_VERIFICATION.md`](FABLE_FINAL_VERIFICATION.md).

## Initial verdict

**MAJOR CORRECTNESS FAILURES**

Before remediation, zero of the 216 independent requirements met the audit's
full `VERIFIED` standard. Critical trust decisions accepted unsigned policy,
caller-supplied truth and formal status, forgeable or truncatable event state,
stale release metadata, and unsandboxed host execution. Important modules were
test-only, unreachable, or disconnected from the nominal production path. The
green baseline suite therefore did not support the claimed architecture.

## Final verdict

**PARTIAL IMPLEMENTATION**

The repository is materially stronger: all 35 confirmed local reproductions
were remediated at their tested entry points, the local deterministic CLI slice
now fails closed, and adversarial coverage increased substantially. It is still
not the complete architecture. Only 13 of 216 requirements meet the strict
`VERIFIED` standard. In particular, 126 remain `PARTIAL`, 9 `UNREACHABLE`, 18
`TEST-ONLY`, 22 `UNVERIFIED`, 25 `BLOCKED-EXTERNAL`, and 3 `OMITTED`. Those
nonexternal gaps forbid a completion verdict independently of the unavailable
live services.

## Quantitative summary

### Requirement status

| Status | Before remediation | After remediation |
|---|---:|---:|
| VERIFIED | 0 | 13 |
| PARTIAL | 18 | 126 |
| INCORRECT | 73 | 0 |
| UNREACHABLE | 48 | 9 |
| TEST-ONLY | 38 | 18 |
| UNVERIFIED | 25 | 22 |
| BLOCKED-EXTERNAL | 3 | 25 |
| OMITTED | 11 | 3 |
| **Total** | **216** | **216** |

### Audit and verification totals

| Measure | Result |
|---|---:|
| Independent requirements extracted | 216 |
| Original requirements verified | 0 |
| Original partial requirements | 18 |
| Original incorrect requirements | 73 |
| Original unreachable components/requirements | 48 |
| Original test-only components/requirements | 38 |
| Original unverified requirements | 25 |
| Original blocked-external requirements | 3 |
| Original omissions | 11 |
| Confirmed finding groups locally remediated | 35 |
| Findings by original severity | 10 CRITICAL; 23 HIGH; 1 MEDIUM; 1 LOW |
| Original reproductions still succeeding on tested local paths | 0 |
| Net additional collected regression/adversarial cases | 366 |
| Post-fix verified requirements | 13 |
| Residual blocked-external requirements | 25 |
| Baseline complete suite | 420 passed, plus 18 unittest subtests |
| Final EGMRA suite | 555 passed |
| Final adversarial/security selection | 349 passed, plus 25 unittest subtests |
| Final complete suite | 786 passed, plus 44 unittest subtests |
| Skipped tests | 0 baseline; 0 final |
| Unavailable live integration executions | Lean/lake/Mathlib, Aristotle, PostgreSQL, model providers, live OEIS/retrieval, and successful compatible OCI compute |

Unavailable integrations were not hidden behind skips; they were recorded as
unexercised or `BLOCKED-EXTERNAL`. Consequently, zero skipped tests does not
mean those live integrations passed.

All 35 finding groups retain a documented material limitation. Classified by
the original severity of the confirmed defect, those residual-bearing groups
are 10 CRITICAL, 23 HIGH, 1 MEDIUM, and 1 LOW. This is not a claim that all 35
original exploits remain open: their named local reproductions are closed. It
is a statement that each correction stops short of proving the complete
affected requirement, as recorded in
[`FABLE_REMEDIATION_LOG.md`](FABLE_REMEDIATION_LOG.md).

## Section 13.6 acceptance criteria

The prior report merged 18 separate acceptance requirements into one ledger
row. The independent inventory preserves them as F-REQ-174 through F-REQ-191.
All 18 functions bearing acceptance-test names pass, but only four criteria are
fully verified:

- F-REQ-180: ambiguity creates multiple interpretations and blocks release;
- F-REQ-181: a false central lemma revokes all dependents;
- F-REQ-186: vendor-only `COMPLETE` cannot establish formal verification; and
- F-REQ-189: OEIS remains heuristic and cannot establish truth.

The other 14 criteria remain partial, unreachable, unverified, test-only, or
blocked by an external dependency. Therefore the prior statement “all §13.6
acceptance criteria pass” is false even though all 18 named test functions are
green. The criterion-by-criterion evidence is in
[`FABLE_TRACEABILITY_MATRIX.md`](FABLE_TRACEABILITY_MATRIX.md).

## Prior-claim assessment

| Previous claim | Assessment | Evidence-based conclusion |
|---|---|---|
| 92 source modules across 22 packages | **SUPPORTED** | The file count is reproducible under the prior counting convention. It is a structural count, not evidence that the modules are production-reachable or complete. |
| Approximately 10.8k lines of new code | **SUPPORTED** | The measured implementation count was 10,839 lines under the prior scope. LOC does not establish semantic coverage. |
| 241 EGMRA tests | **SUPPORTED** | The isolated baseline collected and passed 241 EGMRA tests. |
| 420 tests passing overall | **SUPPORTED** | The clean isolated baseline passed 420 collected cases, plus 18 unittest subtests, with no skips. |
| 120 requirements, all verified | **FALSE** | The independent inventory contains 216 requirements. Before fixes, none met the strict verification standard; many prior rows merged, weakened, or omitted requirements. |
| All four planes implemented | **PARTIALLY SUPPORTED** | Local truth, search, control, and communication components exist and were hardened, but complete persistence, distributed operation, production reachability, and release integration are not demonstrated. |
| All three searches implemented | **FALSE** | The specification's AO*, MCTS, MAP-Elites, and proof-state search obligations are not all implemented as integrated, persistent production searches; several are absent or only small local helpers. |
| All listed subsystems implemented | **MISLEADING** | Most subsystem names have interfaces or local classes, but live retrieval, complete sandboxing, Lean kernel replay, independent authorities, durable learning, closed-loop orchestration, and production evaluation remain partial, test-only, unreachable, or blocked. |
| M0 safety repairs complete | **FALSE** | The audit reproduced critical policy, event, evidence, formal-status, release, sandbox, legacy-gate, and publisher bypasses in the claimed M0 state. |
| M1 end-to-end slice genuine | **FALSE** | The pre-fix slice fabricated decisive state and could report success without promotion/release. The repaired slice is a genuine local deterministic flow, but it uses a restricted interpreter and local HMAC review, has no live formal kernel proof, and is not the specification's complete M1. |
| All §13.6 criteria passing | **FALSE** | Eighteen named tests pass; only 4 of 18 independently specified acceptance criteria are fully verified. |
| No stubs, TODOs, placeholders, or errors | **MISLEADING** | Marker counts did not expose the material defects: no-op/facade integrations, unreachable paths, permissive fallbacks, false success, and security errors existed without TODO labels. |
| External interfaces correctly implemented | **MISLEADING** | Some strict local interfaces and failure paths now exist, but live Lean, model providers, Aristotle, OEIS, Postgres, retrieval indexes, and successful compatible OCI execution were not exercised; several original adapters were facades or unsafe. |

## Critical and high-severity remediation summary

The table below covers every CRITICAL and HIGH finding. “Closed” means the
specific reproduction no longer succeeds on the named local path; the final
column identifies the regression evidence. Full required-field records,
affected F-REQ IDs, source lines, symbols, and residual limitations are in
[`FABLE_REMEDIATION_LOG.md`](FABLE_REMEDIATION_LOG.md).

| Finding | Severity | What was wrong | How it was reproduced | Correction | Regression evidence |
|---|---|---|---|---|---|
| FBL-001 | CRITICAL | Unsigned policy, public/fallback HMAC keys, permissive config, and secret-bearing values could authorize promotion. | Constructed an unsigned `FeaturePolicy` with promotion enabled and exercised malformed/duplicate/secret config. | Required a closed signed policy, explicit strong domain keys, strict regular-file/config schemas, allowlisted secret reads, and mode-0600 exclusive policy output. | `test_unsigned_feature_policy_fails_closed`; `test_adversarial_foundations.py`; CLI key/overwrite/symlink cases. |
| FBL-002 | CRITICAL | Event logs accepted surviving prefixes, lost concurrent writes, and could resurrect invalidated state on replay. | Deleted/reordered/duplicated events, raced writers, restarted replay, and revoked SCC dependencies. | Added canonical HMAC/hash chaining, signed head and Merkle commitment, locked CAS/fsync persistence, complete replay projections, and event-first SCC/transitive revocation. | Corruption/truncation/insertion/reorder/concurrency/restart tests in `test_adversarial_truth_security.py` and `test_truth_snapshots.py`. |
| FBL-003 | CRITICAL | Caller-supplied exact/formal fields and irrelevant computation could promote a false claim. | Forged evidence kind/status, mismatched claim/artifact, false computation, and stale-worker result submissions. | Reconstructed typed evidence server-side and bound it to claim, interpretation, artifacts, replay, checker, current fence, and qualifying promotion rules. | Forged-evidence, false-computation, mismatch, and stale-output tests across truth, compute, and orchestrator adversarial suites. |
| FBL-004 | CRITICAL | Arbitrary proof text, booleans, equivalence labels, and vendor `COMPLETE` could manufacture Lean/T4/T5 status. | Supplied injected-success checker callbacks, malformed proof artifacts, unrelated types, unsafe declarations/imports, and vendor-only completion. | Added a closed authenticated checker protocol bound to source/type/environment/claim/artifacts, exact correspondence, no-hole/unsafe scans, and fail-closed level transitions. | `test_adversarial_lean_release.py`, `test_formal_correspondence_security.py`, and vendor-status rejection tests. |
| FBL-005 | CRITICAL | A host Python wrapper was called a sandbox; hostile code could read files/env, use sockets, spawn processes, and fall back unsafely. | Executed file, environment, network, subprocess, timeout, output, and fallback attacks; exercised the real Docker command path. | Replaced host evaluation with a capability-free exact AST interpreter, strict resource/output schemas, scrubbed environment, and OCI-only fail-closed boundary with no host fallback. | `test_adversarial_compute_security.py`; filesystem/network/process/env/timeout/cleanup cases; Docker negative-path smoke test. |
| FBL-006 | CRITICAL | Caller-provided or stale gate state could be signed/rendered and direct rendering bypassed mandatory gates. | Mutated target/evidence/head after approval, forged gate metadata, called renderer directly, and replayed cached approval. | Derived gates from replayed current truth, bound all five gates and promotion to one exact subject/head, signed a fresh certificate, and revalidated at rendering/return. | Gate mutation/substitution/freshness/direct-render tests in release, truth-snapshot, and CLI adversarial suites. |
| FBL-007 | CRITICAL | The orchestrator ignored decisive components and fabricated self-approved “end-to-end” success. | Ran false computations, unavailable workers, disabled promotion, stale fences, and nominal success with no release. | Wired the deterministic production CLI slice through intake, interpretation, controlled work, evidence persistence/replay, truth transition, gates, promotion, certificate, and render; failures now triage. | `test_adversarial_orchestrator.py`, `test_orchestrator.py`, `test_cli.py`, including true/false and fail-at-stage cases. |
| FBL-008 | HIGH | Agent authority existed mainly in prompts, while mutable blackboard state enabled cross-role access and self-approval. | Reused/forged/expired capabilities, invoked prohibited tools directly, mutated returned state, and attempted cross-agent approval. | Added short-lived signed scoped capabilities, immutable/copy-on-read packets, operation allowlists, separation-of-duties checks, and authoritative admission. | Authority scope/tamper/expiry/direct-invocation/confused-deputy tests in `egmra/tests/test_adversarial_authorities.py`. |
| FBL-009 | HIGH | Fingerprints were not consumed, AND/OR debt and posterior/utility accounting were wrong, cycles and invalid numbers passed, and budgets were disconnected. | Independently recomputed utility/posterior values; injected NaN/negative costs, cycles, frozen-debt changes, failure, and budget exhaustion. | Implemented validated fingerprints, explicit AND/OR semantics, frozen verified debt, finite posterior/utility accounting, branch competition, failure charging, checkpoint state, and CLI consumption. | Search arithmetic, fingerprint, cycle, debt, failure, budget, persistence, and resume cases in `test_adversarial_search.py`. |
| FBL-010 | HIGH | Retrieval provenance packets were mutable/incomplete and lexical overlap was treated as theorem applicability. | Mutated cached packets, supplied duplicate/malformed/stale/injected sources, and tested negated or inapplicable statements. | Froze complete query/source identities, ranked/deduplicated defensively, separated imports from proof, preserved negation, and made offline/malformed behavior fail closed. | Retrieval provenance, injection, mutation, negation, cache, and malformed/offline tests in `test_adversarial_retrieval.py`. |
| FBL-011 | HIGH | OEIS cache corruption, loose integer typing, and empty/no-match held-out logic could fabricate support. | Used corrupt/symlink cache, floats-as-integers, empty/duplicate/negative/large sequences, and degenerate no-match cases. | Added strict immutable response/cache schemas and hashes, exact transform typing, bounded held-out validation, and a hard rule that OEIS never creates truth evidence. | Transform property/edge cases, cache attacks, malformed HTTP, and no-truth tests in `test_adversarial_oeis.py`. |
| FBL-012 | HIGH | Caller-created reviewer labels/booleans and correlated reviewers could manufacture a verification tier. | Submitted forged, self-approved, correlated, missing, conflicted, and dissenting review records. | Added authenticated scoped reviewer results, pessimistic dimension-specific aggregation, escalation, separation of duties, and release-state impact. | Tier T0-T5 forgery, correlation, dissent, escalation, false-positive, and false-negative tests in `test_adversarial_verification.py`. |
| FBL-013 | HIGH | Any truthy learning record could poison cross-problem memory and future selection. | Admitted unsupported/stale/wrong-problem records and observed process-local learning acceptance. | Required authenticated current replay, semantic identity, and T2/I2/R2 gate binding before admission; quarantined failed outcomes. | Verified-only admission, stale/wrong-target/quarantine, and orchestrator learning tests in `test_adversarial_learning.py`. |
| FBL-014 | HIGH | M2/external adapters were largely facades; the local object store allowed unsafe paths/symlinks and DSN errors leaked secrets. | Traversed/substituted object paths, used symlinks, malformed DSNs/config, and invoked unavailable adapters. | Added SHA-addressed confined atomic objects, no-symlink checks, redacted/validated config, explicit unavailable failures, and an OCI-only M2 assembly boundary. | Object traversal/symlink/corruption, DSN redaction, fail-closed adapter, and M2 assembly cases in `test_adversarial_m2.py`. |
| FBL-015 | HIGH | The baseline tests asserted shapes and self-derived constants while missing critical bypasses, yet were cited as proof of acceptance. | Mutation-style bypasses left baseline tests green; independent negative cases failed against the pre-fix code. | Added production-path, adversarial, persistence, restart, revocation, concurrency, forgery, and failure-injection suites and withheld unsupported acceptance claims. | Net final collection increase plus the independent adversarial/security suites cataloged in `FABLE_TEST_QUALITY_REPORT.md`. |
| FBL-016 | HIGH | CI omitted the entire EGMRA suite and `pytest` was undeclared, so the claimed architecture tests were not part of reproducible verification. | Inspected the workflow/test commands and performed a clean locked install and suite collection. | Declared the test dependency in locked manifests and changed CI to collect/run legacy and EGMRA suites together. | Clean-environment dependency installation, collection-count, and complete-suite verification in the baseline/final reports. |
| FBL-017 | HIGH | Statement IR lost quantifiers/domains/constraints/definitions, contradictory interpretations could pass, and executable probes were not required to execute. | Parsed ambiguous, quantified, malformed, contradictory, and round-trip examples; bypassed probe execution and selected a raw-text path. | Preserved structured semantic fields, built/reconciled two parser families and a lattice, executed probes, locked selected interpretation, and bound downstream intent/release. | `test_adversarial_intake.py`, `test_intent_review_security.py`, and orchestrator wrong-target/vacuity cases. |
| FBL-018 | HIGH | Secret config and caller-supplied provider/runner/cache identities permitted leakage, relabeling, and false cache reuse. | Injected nested/case-varied secrets, forged model family/runner identity, and changed behavior closure while replaying cache. | Enforced recursive secret denial/allowlisted access, measured immutable stage identity and behavior closure, and disabled unauthenticated model-output replay. | Foundation/config secret tests, model identity/relabel tests, and cache mismatch/fresh-provider-call regressions. |
| FBL-019 | HIGH | Evaluation identity omitted behavior and fixture predicates used Python `eval`, permitting arbitrary code and constant-success helper abuse. | Supplied a predicate that attempted a side effect and a bare `_isprime` helper that would evaluate truthy. | Bound full behavior/config identity and replaced Python `eval` with a closed recursive AST interpreter that accepts only the specified expression subset. | `test_fixture_predicates_do_not_execute_through_python_eval`, `test_fixture_predicate_rejects_bare_helper_as_constant_success`, and adversarial eval/config/statistics tests. |
| FBL-020 | HIGH | Lease races, stale writes, restart behavior, retry classification/backoff, exact 120-second cap, and verifier capacity were incorrect or disconnected. | Used controlled clocks and concurrent acquisition to test expiry/reassignment, stale commit, duplicate delivery, nonfinite values, retry exhaustion, and starvation. | Added durable atomic lease state, locks, monotonic fences, post-work fence checks, typed failure classification, bounded exponential backoff, idempotency, and reserved verifier capacity. | Deterministic concurrency/restart/stale-worker/backoff/capacity tests in `test_adversarial_control.py`. |
| FBL-022 | CRITICAL | The legacy production gate trusted `passed=True`, descriptive labels, and arbitrary evidence paths. | Invoked the real legacy promotion path with forged status/identity and evidence outside the allowed root. | Required authenticated materialized evidence and current bindings where possible, quarantined unattested browser output, and made unsafe legacy release fail closed. | Legacy trust-boundary tests plus the complete historical unittest suite. |
| FBL-023 | HIGH | Checkpoints were mutable, forgeable, identity-free, unrelated to event history, and unsafe to resume. | Edited checkpoint state, replayed it under another run/policy/history, truncated its prefix, and attempted unsafe cache reuse. | Added canonical HMAC authentication, run/policy/stage identity, event-prefix/head binding, strict schema/regular-file handling, and safe rejection. | Fourteen checkpoint forgery/cross-run/history/truncation/symlink tests and dependent restart tests. |
| FBL-024 | CRITICAL | A direct legacy publisher accepted a forged gate-status string and path-like category, allowing arbitrary “verified” publication. | Called the publisher directly with forged `verified` state and traversal-like category. | Retired the legacy publisher unconditionally; only the EGMRA certificate-enforcing renderer can publish verified output. | Direct forged-status and category-escape quarantine regressions. |
| FBL-025 | HIGH | Same-process helper code could notarize a caller-asserted provider/checker identity and relabeled artifact. | Relabeled provider/checker fields, changed artifact bytes, and invoked the path without an attestor. | Canonicalized signed material, rehashed current artifact bytes, bound checker/provider/environment identity, and failed closed without attestation. | Canonical-binding, byte-rehash, relabel, and no-attestor regressions. |
| FBL-026 | CRITICAL | Aristotle children inherited secrets, followed attacker-controlled run symlinks, expanded unbounded archives, and could execute vendor Lake configuration on the host. | Used a fake child to inspect environment, symlinked run paths, crafted hostile/oversized archives, and supplied vendor Lake hooks. | Switched to minimal scrubbed environments, exclusive ancestry-checked run dirs, bounded typed archive handling, cleanup, and quarantine that forbids host vendor builds. | Minimal-env/redaction, ancestry/symlink, archive-limit/type, cleanup, and no-host-vendor-build regressions. |
| FBL-027 | HIGH | Legacy JSON/evidence readers accepted duplicate/oversized input, could block on FIFOs, race paths, exceed aggregate limits, and inspected disabled formal evidence. | Fed duplicate keys/nonfinite/oversized records, FIFOs, symlink/TOCTOU substitutions, aggregate overflow, and disabled-policy evidence. | Added strict bounded JSON/numeric schemas, regular-file/nonblocking/anchored opens, aggregate quotas, byte revalidation, and policy-before-evidence ordering. | Duplicate/numeric/FIFO/aggregate/anchored-open/TOCTOU/policy-order/materialization-byte regressions. |
| FBL-028 | HIGH | Unavailable/advisory adjudication poisoned retry state and model dissent could override materialized formal truth. | Injected unavailable and advisory outcomes, replayed retry state, and submitted dissent against encoded formal evidence. | Separated transient queue state from mathematical state, authenticated accepted adjudication, rediscovered advisory work, and made formal materialization dominate model opinion. | No-call/no-marker, advisory rediscovery, retry, and formal-truth-precedence regressions. |
| FBL-029 | HIGH | A caller-writable stage response and adjacent digest could be edited together and replayed as authenticated model output. | Modified the cached response, recomputed its sidecar digest, and observed cache acceptance without a provider call. | Disabled model-output cache reads; retained writes only as diagnostics until an independent authenticated replay service exists. | Response+metadata forgery and mandatory-fresh-provider-call regressions. |
| FBL-030 | HIGH | Symlinked legacy artifact/problem roots redirected proof/adjudication writes outside the repository tree. | Replaced the configured root/problem directory with a symlink and checked writes outside the intended tree. | Validated root ancestry/components and identity before provider calls, used anchored/dirfd-bound operations, and rejected unsafe substitution without external writes. | Root/problem symlink, zero-provider-call, and unchanged-outside-tree regressions. |
| FBL-031 | HIGH | The fixture CLI exited zero and called a result “verified” while promotion was disabled and release was null. | Ran the true fixture under a policy that blocked promotion and inspected exit status/disposition/release. | Made verified success require an actual current promotion and nonnull valid release; otherwise the command returns honest triage/failure. | Policy-blocked negative and actual-release positive CLI tests. |
| FBL-032 | HIGH | Event verification silently used a hidden default run ID and crashed or verified the wrong subject on real logs. | Ran the public verifier against a production log with its actual and a wrong run ID, then tampered an event. | Required explicit `--run-id`, verified the exact subject and head, and returned structured failure instead of crashing. | Exact-run success, wrong-run rejection, and tampered-event public CLI regressions. |
| FBL-033 | HIGH | An authentic release certificate remained accepted after the surrounding result/contract identity was mutated. | Produced a valid release, mutated result/contract identity, and replayed the unchanged certificate. | Joined and revalidated result, contract, log, claim, interpretation, gates, promotion, current head, and certificate subject before reporting success. | Cross-contract replay plus missing/forged/stale certificate tests in `test_cli.py`. |
| FBL-034 | HIGH | Source and OEIS ingestion disabled or failed to enforce TLS, accepted unsafe schemes/redirects, and allowed unbounded or insufficiently closed responses. | Bandit found `verify=False`; mocked `file:`/HTTP inputs, downgrade redirects, oversized bodies, default TLS arguments, and response cleanup; both OEIS cases failed before the fix. | Centralized HTTPS-only/no-credentials transport, default certificate verification, validated manual redirects with a five-hop cap, bounded streamed bodies, strict UTF-8, and guaranteed close. | `tests/test_ingestion_network_security.py`, OEIS live-HTTP transport adversarial tests, focused ingestion suites, and clean medium/high Bandit scans. |

The MEDIUM FBL-021 correction rejects nonfinite/invalid selector inputs and
enforces tested hard constraints. The LOW FBL-035 correction prevents OEIS
transform enumeration from swallowing unexpected implementation failures.
Their complete records and residuals are also in the remediation log.

## M1 production-slice result

The repaired local slice now demonstrates a meaningful but narrow flow: it
accepts a finite fixture claim, creates and locks structured interpretation,
executes deterministic exact computation through the restricted interpreter,
persists and replays evidence, derives `SUPPORTED`, evaluates mandatory local
gates, signs a subject-bound release, and renders the true result. A false
fixture produces honest triage with no proof or release. Stage-failure tests are
fail-closed, and the public event verifier requires the exact run identity.

This does not satisfy the complete M1 claim. The slice has
`runner_attested=false`, no live model/retrieval/OEIS service, no successful
isolated OCI computation using a compatible image, no real Lean/Mathlib kernel
replay or persisted compiled proof, and no organizationally independent
referee. Its positive formal/review portions are local authenticated protocol
fixtures, not live proof verification.

## Remaining limitations

### Verified local behavior

- Thirteen requirements meet the full local verification standard, including
  the four acceptance properties identified above.
- The named local reproductions for all 35 findings now fail closed.
- Signed local policy, current-subject event replay, SCC-aware invalidation,
  typed evidence routing, stale-fence rejection, certificate-bound rendering,
  and the deterministic true/false CLI slice have positive and negative runtime
  evidence.
- The complete final local test suite, lint, production type checks, compile
  checks, dependency audit, and medium/high security scan are green except for
  the separately documented repository-wide format-check failure.

### Behavior exercised against real services

- No decisive mathematical external integration was successfully exercised.
- A real local Docker daemon was reached only to demonstrate the OCI command's
  fail-closed negative path; the available image lacked Python and returned
  execution failure. That is not a successful isolated computation.
- Dependency installation contacted package infrastructure, but it is not
  evidence for any architecture integration.

### Behavior verified only with controlled fakes or mocks

- Positive Lean checker envelopes and formal transitions use controlled
  checker output, not a Lean kernel.
- Model-provider identity, retrieval ranking/results, OEIS response behavior,
  Aristotle responses, and several Postgres/service contracts are tested with
  local fakes or mocked transports.
- The local referee and review signatures establish protocol binding, not
  organizational or provider independence.

### Behavior supported only by static inspection

- Several service/topology descriptors, optional backend protocols, agent role
  declarations, and full-scale deployment policies have no running production
  daemon or API path.
- Static scans support the absence of known marker patterns and medium/high
  Bandit findings; they do not prove absence of unreachable code, all future
  entry points, prompt injection, or semantic mathematical defects.

### Blocked by credentials or infrastructure

- Lean/lake has no configured toolchain or pinned Mathlib environment.
- Aristotle CLI, PostgreSQL tools/service, external model credentials, and live
  retrieval/OEIS services were unavailable or intentionally not invoked.
- No compatible local OCI Python image completed a sandboxed job.
- Live timeout, rate-limit, cancellation, schema-drift, restart, and recovery
  behavior for those services therefore remains unverified.

### Unresolved repository-local defects and omissions

- 126 requirements remain `PARTIAL`, 9 `UNREACHABLE`, 18 `TEST-ONLY`, 22
  `UNVERIFIED`, and 3 `OMITTED`; these are not excused by external limits.
- There is no durable distributed closed loop that checkpoints, resumes, and
  learns across real jobs; several stores remain process-local.
- AO*, MCTS, MAP-Elites, proof-state search, production evaluation, known-solved
  rediscovery, and equal-cost paired baseline experiments are not complete
  integrated workflows.
- There is no public API/release service or exhaustive inventory/migration
  bridge proving every legacy and alternate release entry point uses the EGMRA
  certificate chain. The legacy publisher is safely retired, not integrated.
- Event-log/head rollback still needs an external monotonic witness; total
  event/artifact/cache storage quotas and a provider token limit remain absent.
- Same-process HMAC identities are not independently isolated provider,
  checker, referee, or release authorities.
- Formatting is not configured as a repository contract and the audit-only
  formatter check reports widespread pre-existing reformatting differences;
  these were not mass-rewritten over the user's dirty worktree.

## Evidence index

1. [`FABLE_INDEPENDENT_REQUIREMENTS.md`](FABLE_INDEPENDENT_REQUIREMENTS.md) —
   216 independently extracted, source-located requirements.
2. [`FABLE_LEDGER_DISCREPANCIES.md`](FABLE_LEDGER_DISCREPANCIES.md) — omitted,
   merged, weakened, and unsupported prior-ledger claims.
3. [`FABLE_CODE_INVENTORY.md`](FABLE_CODE_INVENTORY.md) — package/module purpose,
   callers, dependencies, tests, and reachability classification.
4. [`FABLE_BASELINE_VERIFICATION.md`](FABLE_BASELINE_VERIFICATION.md) — clean
   baseline commands, counts, exclusions, and environment.
5. [`FABLE_TRACEABILITY_MATRIX.md`](FABLE_TRACEABILITY_MATRIX.md) — one row for
   every F-REQ with pre/post status, implementation, call path, tests, runtime
   evidence, fixes, and residuals.
6. [`FABLE_TEST_QUALITY_REPORT.md`](FABLE_TEST_QUALITY_REPORT.md) — weak-test and
   mutation-style analysis plus independent test coverage.
7. [`FABLE_SECURITY_AUDIT.md`](FABLE_SECURITY_AUDIT.md) — threat model,
   trust-boundary analysis, exploits, mitigations, and residual risks.
8. [`FABLE_REMEDIATION_LOG.md`](FABLE_REMEDIATION_LOG.md) — canonical
   required-field records for FBL-001 through FBL-035.
9. [`FABLE_FINAL_VERIFICATION.md`](FABLE_FINAL_VERIFICATION.md) — fresh post-fix
   installation, static, test, CLI, recovery, external, and scan evidence.

## Direct final answer

> Is the final repository now a faithful, integrated, working implementation of
> the complete specification?

**No.** It is a substantially hardened partial implementation with a meaningful
local deterministic slice, but it is not faithful and complete across the 216
requirements. The many remaining nonexternal partial, unreachable, test-only,
unverified, and omitted requirements independently preclude completion; the 25
blocked external requirements add further limitations.
