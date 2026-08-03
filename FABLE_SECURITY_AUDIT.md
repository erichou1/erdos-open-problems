# FABLE Security Audit

## Security verdict

The audit-start repository had **critical exploitable trust-boundary failures**.
Untrusted code ran on the host, unsigned/fallback-key records could authorize
promotion, a valid event-log suffix could be deleted undetected, caller fields
could manufacture exact/formal evidence and T5, stale/caller profiles could
authorize release, workers and the orchestrator could self-approve, the legacy
publisher accepted caller truth and arbitrary evidence paths, and the complete
green suite did not detect any of this.

The remediated local paths are materially safer and most now fail closed for
their original reproductions. They are **not a complete production security boundary**.
Real Lean, a compatible successful OCI computation image, PostgreSQL, external
model providers, Aristotle, live OEIS, citation/theorem retrieval, distributed
leases, key isolation, and a public API/release service were not exercised.
Several nonexternal architectural gaps also remain: local rollback has no
external monotonic anchor, prompt/retrieval injection has containment but no
live adversarial campaign, event/artifact stores lack total quotas, the model
gateway has no token limit, verified learning is not durable, and the legacy and
EGMRA paths have no compatible migration bridge (the legacy publisher is now
retired fail-closed). A second legacy pass also found a
direct status-only publisher, same-process identity notaries, unsafe Aristotle
child/archive paths, loader denial-of-service/race gaps, and retry/precedence
defects. A later pass additionally confirmed circular authentication of mutable
stage-cache files and symlink escapes at legacy artifact/problem roots. These
plus a fixture CLI that returned success without an actual release and an
event-integrity CLI that ignored real run identity are tracked separately rather
than hidden inside the earlier legacy-gate/orchestrator findings. A subsequent
CLI pass also found that an authentic release certificate could be accepted
after the surrounding result/contract identity was mutated. A final OEIS pass
found that transform enumeration silently omitted a path when internal
implementation code raised an unexpected exception. The final production
network scan also found certificate verification explicitly disabled at four
ingestion sites plus unsafe-scheme/unbounded-response paths; an equivalent
implicit-redirect/unbounded-body defect was then reproduced in the live OEIS
adapter.

The canonical required-field records for every confirmed issue are
FBL-001 through FBL-035 in `FABLE_REMEDIATION_LOG.md`. This report
introduces no second finding namespace and does not weaken those residuals.

## Scope and method

The threat model treats the system as an autonomous mathematical agent with all
of the capabilities named by the specification:

- immutable problem intake and semantic interpretation;
- external retrieval, OEIS and model calls;
- adversarial Python/mathematical code execution;
- generated Lean and proof promotion;
- signed persistent truth, artifact, lease, cache and learning state;
- concurrent/stale workers and separate agent authorities; and
- final gate, signing, rendering and publication authority.

The audit did not infer safety from class names, comments, mocks, or passing
tests. It ran direct pre-fix probes, wrote negative tests, verified red failures
before fixes where practical, retested the production call path, searched for
alternate/direct entry points, and separated local protocol behavior from live
external verification. Security statements below refer only to the tested
repository scope; a privileged local administrator or compromised deployment
host is outside the local M1 protection model unless explicitly stated.

## Assets and security objectives

| Asset | Required security property | Consequence of compromise |
|---|---|---|
| Exact source and active interpretation | Immutable bytes, complete semantic identity, independent approval | Correct proof attached to the wrong theorem or domain |
| Claim/evidence graph | Authentic, append-only, replayable, versioned, revocable | False support, resurrected evidence, lost dependency invalidation |
| Compute host and credentials | No hostile file/process/network/env capability; bounded use | Host compromise, secret theft, denial of service |
| Lean proof trust | Exact type/source/import/axiom/environment/kernel binding | Arbitrary text labeled kernel verified |
| Retrieval/OEIS inputs | Data-only handling, immutable provenance, no truth upgrade | Prompt injection, inapplicable imports, false novelty |
| Worker/control state | Least privilege, scoped packets, leases/fences/idempotency | Stale/forged writes, self-approval, resource theft |
| Release chain | Fresh exact-subject gates, promotion authorization, signature, render enforcement | Publication of false, stale, partial, or wrong-target result |
| Secrets/model identity | Confidential keys, authenticated immutable runner identity | Forged evidence/reviews/independence and credential disclosure |
| Learning/evaluation | Verified-only admission, sealed identity and no executable leakage | Persistent contamination and false performance claims |

## Trust boundaries and data flow

| Boundary | Untrusted side | Trusted decision side | Current enforcement | Residual |
|---|---|---|---|---|
| Source -> Statement IR | arbitrary bytes/math prose | contract, lattice, intent review | exact bytes/hash, strict UTF-8, immutable IR, dual families, probes, signed exact-binding intent | heuristic parsers and limited semantics; external reviewer isolation absent |
| Retrieval/OEIS -> solver packet | remote/source text and JSON | frozen search input only | strict/frozen packet, complete hash, source hashes, negation-safe import audit, OEIS never evidence | no live injection corpus, four-index source audit, or formal elaboration |
| Model/worker -> blackboard | generated text/proposals | scoped proposal admission | short-lived signed capabilities, immutable slice/packet hash, proposal allowlists | local HMAC issuer; no real provider identity/service isolation |
| Worker -> truth | claims, computation/formal status | evidence router | fence recheck, server reconstruction, evidence HMAC, claim/artifact/replay binding | arbitrary program-to-claim semantics still need scoped verifier |
| Code -> compute host | hostile program/spec/output | restricted/OCI executor and artifact service | AST capability subset, scrubbed environment, bounds, strict output, no fallback; hardened OCI command | local subset is not an OS sandbox; successful compatible OCI job blocked |
| Generated Lean -> proof trust | source/status/certificate | attested checker, correspondence, router | closed subprocess protocol and envelope bound to source/type/env/claim/artifacts plus signed review | real Lean/Mathlib/kernel/independent checker not exercised |
| Disk -> authoritative state | corrupted/reordered/truncated/cache/object files | log/graph/artifact/object loaders | strict JSON, HMAC/hash/Merkle/head, locks/CAS/fsync, no-symlink/content checks | simultaneous rollback of log+head; no replicated anchor/database |
| Truth -> release | mutable/cached profile or stale claim | snapshot, five gates, promotion, certificate, renderer | replay-derived snapshot, exact current head, distinct keys, subject/freshness chain, final recheck; legacy publisher retired unconditionally | no legacy-to-EGMRA migration bridge and no API inventory |
| Outcome -> long-term memory | speculative/truthy record | verified semantic store | current snapshot+log+T2/I2/R2 gate binding | process-local store and no demonstrated feedback into a later run |
| Fixture/benchmark -> evaluator | manifests/predicate text/answers | frozen evaluation record | full config hash and closed AST interpreter with no Python `eval` | no sealed external runner/contamination audit/blind grading |

## Adversary model

The audit assumes any of the following may be malicious, malformed, stale, or
compromised independently:

1. problem source bytes, retrieved documents, OEIS responses and cached files;
2. a model/provider response, program worker, formalization worker or referee;
3. submitted Python/source/output/certificate and generated Lean/import tree;
4. a stale worker retaining an expired lease/fence and replaying old output;
5. a process racing local event, lease, cache, artifact or object-store files;
6. a caller invoking a lower-level verifier/gate/render/publisher directly;
7. a caller forging status, reviewer/model identity, environment labels,
   certificate fields, result booleans or release metadata; and
8. unavailable, rate-limited, malformed, drifting or partially failing external
   infrastructure.

A fully privileged host administrator can replace code and read environment
secrets. The remediated M1 HMAC boundaries do not claim to resist that attacker.
Deployment separation, independent services/HSMs and an external append-only
anchor are required to raise that boundary.

## Mandatory security invariants

- Missing/weak trust keys or unsigned/wrong-key records fail closed.
- Authentication never substitutes for mathematical/artifact semantics.
- Caller/model/vendor booleans, strings, labels and confidence never establish
  truth, independence, formal verification, intent, correspondence or release.
- Every status transition is produced by the truth authority after exact
  kind-specific validation; direct mutation is forbidden.
- Every positive release is bound to one exact current claim, interpretation,
  evidence profile and event-log head and is revalidated at render/return.
- Untrusted executable content receives no host capability. If required
  isolation is unavailable, the job is unavailable—not silently unsandboxed.
- Retrieval and OEIS may propose searches/conjectures/import tasks but never
  become proof or novelty by themselves.
- An expired/stale worker cannot commit, even if its output is otherwise valid.
- Unknown, missing, correlated, conflicted or dissenting verification fails
  pessimistically.
- Cross-problem learning requires authenticated current replay and gates.

## Threat coverage matrix

Status meanings:

- **LOCALLY MITIGATED** — the named pre-fix reproduction is closed and has a
  local negative regression.
- **PARTIAL** — meaningful defenses exist, but the complete threat/acceptance
  condition has not been demonstrated.
- **BLOCKED-EXTERNAL** — a real external boundary is necessary and unavailable.
- **RESIDUAL** — a known repository-local limitation remains.
- **NOT REPRODUCED** — no exploit was demonstrated after targeted inspection;
  this is not a formal proof of absence.

| Requested threat | Audit-start evidence | Remediation/runtime evidence | Status and residual | Findings |
|---|---|---|---|---|
| Prompt injection | source/retrieved/model text could enter prompts; no isolation campaign | model output is proposal-only; packets are immutable; workers cannot write truth/release; missing verification blocks | **PARTIAL** — containment is meaningful, but no live malicious-source/provider campaign or prompt data/instruction firewall was exercised | FBL-007, FBL-008, FBL-010, FBL-012 |
| Retrieval injection | lexical token containment erased negation and packet provenance was mutable | strict packet identity, SHA source provenance, negation preserved, retrieved records remain imports/search inputs | **PARTIAL** — live corpus poisoning, stale source, citation graph and formal applicability unverified | FBL-010 |
| Malicious source / provenance / licensing | local dummy records and caller metadata could stand in for audited sources; ingestion disabled TLS verification/accepted unsafe schemes and OEIS allowed implicit redirects/unbounded bodies | exact packet/query/source hashes and separate import audit; bounded HTTPS-only ingestion/OEIS adapters with default certificate validation and final-target checks; missing/conflicting source cannot become truth | **PARTIAL** — URL, upstream commit, retrieval time and license are absent when not supplied; no live source/licensing/TLS recovery audit | FBL-007, FBL-010, FBL-017, FBL-034 |
| Command injection / shell injection | host Python executed arbitrary code behind a sandbox name; vendor Lake projects were built on the host | no shell execution in audited compute/checker paths; restricted AST forbids imports/attributes/process calls; OCI uses argv and overrides image entrypoint; provider Lake projects are quarantined and never host-built | **PARTIAL** — local compute paths are mitigated, but external commands/services were not fuzzed end to end | FBL-005, FBL-014, FBL-019, FBL-026 |
| Arbitrary code execution | compute read `/etc/passwd`/opened `_socket`; fixture predicates used unrestricted `eval`; provider lakefiles/build hooks could run on host | capability-free restricted subset, closed AST fixture interpreter with no Python `eval`, process/env/network attacks and no-host-vendor-build behavior | **PARTIAL** — hostile arbitrary Python/Lean projects still require the unavailable OCI boundary for successful execution | FBL-005, FBL-019, FBL-026 |
| Sandbox escape | no real sandbox; `ContainerSandbox` raised and host wrapper ran jobs | hardened local restriction and real fail-closed OCI command path | **BLOCKED-EXTERNAL** for successful compatible OCI isolation; local subset is explicitly not an OS sandbox | FBL-005, FBL-014 |
| Filesystem access | unrestricted same-host jobs could read files | AST denies file/import/attribute capabilities; OCI root/read mounts constrained | **LOCALLY MITIGATED** for restricted executor; OCI success unverified | FBL-005 |
| Path traversal | evidence/object paths and publication categories could reference arbitrary locations | confined relative artifacts, SHA-only object keys, rooted stores, retired legacy publication, and validated artifact/problem roots | **PARTIAL** — static legacy root/category attacks are closed, while hostile concurrent path replacement and broader loader coverage remain residual | FBL-005, FBL-014, FBL-022, FBL-024, FBL-026, FBL-027, FBL-030 |
| Symlink attacks | evidence, object/artifact/cache/config, legacy artifact roots and Aristotle run paths could be substituted | no-follow/regular-file checks, component/root inode checks, exclusive fresh execution directories, dirfd-bound adjudication writes and symlink regressions | **PARTIAL** — tested static substitutions are closed; same-UID rename races and complete external-prover quarantine remain residual | FBL-001, FBL-005, FBL-011, FBL-014, FBL-022, FBL-026, FBL-027, FBL-030 |
| Process spawning | restricted host Python could import subprocess and Aristotle verification launched Lake in an untrusted project | AST/import/name/attribute denial; PID/process-group controls; OCI drops capabilities/PID limit; provider Lake builds are denied without quarantine | **PARTIAL** — restricted jobs are closed, but real quarantined external-prover builds are unavailable | FBL-005, FBL-026 |
| Network access | `_socket.socket()` worked; ingestion disabled certificate verification/accepted unsafe schemes and OEIS followed redirects implicitly | restricted code cannot import/access sockets; OCI command uses `--network none`; ingestion/OEIS require HTTPS, validate redirects/final URLs, preserve default TLS verification and bound bodies; OEIS restricts canonical hosts | **PARTIAL/BLOCKED-EXTERNAL** — negative enforcement tested, successful OCI job and live TLS/redirect recovery not; deployment DNS/egress controls absent | FBL-005, FBL-014, FBL-034 |
| Environment/credential exposure | host jobs and checker/provider subprocesses could inherit secrets; Aristotle copied the entire parent environment | scrubbed minimal environments, closed descriptors, config denylist, checker/Aristotle child secret-exposure tests | **PARTIAL** — no deployment log scanner/HSM; trusted host process still holds several keys and no live provider ran | FBL-001, FBL-004, FBL-005, FBL-018, FBL-022, FBL-025, FBL-026 |
| Sensitive log leakage | no systematic proof that exceptions/logs redact credentials | Postgres DSN errors redact userinfo; policy commands never print keys; checker/job env scrubbed | **PARTIAL** — no repository-wide structured logging/redaction test or external provider failure run | FBL-014, FBL-018, FBL-022 |
| Unsafe deserialization | permissive JSON/duplicates/nonfinite, archive extraction and caller record construction at critical boundaries | strict bounded UTF-8 JSON with duplicate/nonfinite/schema checks; bounded/type-checked archive handling; no pickle/dill/marshal in EGMRA | **PARTIAL** — critical boundaries tested, but not every JSON/archive reader was fuzzed | FBL-001 through FBL-006, FBL-010, FBL-011, FBL-014, FBL-022, FBL-026, FBL-027 |
| Malicious proof files | arbitrary source/status/certificate could claim formal success | checker executable/source/type/artifact envelope, exact hashes, strict protocol, no raw status authority | **PARTIAL** — real malicious Lean files were not built in an actual disposable Lean environment | FBL-004, FBL-005 |
| Malicious Lean imports / unsafe declarations / `sorry` / axioms | regex/status booleans and dummy archive could pass | placeholder/unsafe/import/axiom/full-audit fields are mandatory and authenticated; exact type/source closure bound | **BLOCKED-EXTERNAL/PARTIAL** — no real pinned Mathlib closure or independent kernel run | FBL-004 |
| Forged evidence/status | caller exact/formal fields, legacy `passed=True`, asserted identity, mutable cache files, a forged publisher gate string and an authentic certificate attached to a mutated result promoted/reported claims | HMAC exact claim/artifact/replay binding, complete result/contract/log/claim/interpretation/gate/promotion/certificate join, artifact-byte rehashing, no model-output cache replay, forged-status quarantine and unconditional publisher retirement | **PARTIAL** — direct local forgeries/misbinding are contained on named paths, but no isolated provider/checker attestor, immutable release envelope consumer inventory or authenticated replay cache exists | FBL-003, FBL-004, FBL-022, FBL-024, FBL-025, FBL-027, FBL-029, FBL-033 |
| Circular verification / circular imports | generators/review labels and unchecked dependencies could validate one another | graph dependencies, attack schemas, imported-theorem audit fields, pessimistic referee, no same-pass repair | **PARTIAL** — default referee is local mechanical and no real theorem/import reconstruction campaign ran | FBL-002, FBL-004, FBL-010, FBL-012 |
| Replay attacks / stale approvals | log truncation, mutable/identity-incomplete checkpoint/cache state, caller environment labels, stale gates, a verifier using the wrong default run ID and a valid certificate replayed against mutated result identity | authenticated head/Merkle, complete exact-run replay, mandatory CLI run binding, complete result/certificate subject join, measured environments, snapshot/gate/cert current-head binding and HMAC checkpoint prefix identity | **PARTIAL** — rolling back both local log and head remains possible; production resume does not consume checkpoint, run-ID discovery is external and alternate mutable-result consumers are not exhaustively inventoried | FBL-002, FBL-005, FBL-006, FBL-018, FBL-023, FBL-032, FBL-033 |
| Stale-worker writes | leases were disconnected/in-memory; output could arrive after transfer | monotonic fences persisted locally; fence checked after worker return and before output inspection | **LOCALLY MITIGATED** for deterministic local race; no multi-host partition test | FBL-007, FBL-008, FBL-020 |
| Race conditions / duplicate delivery | writers could share sequence zero; concurrent leases/capacity and check-then-open artifact paths were unsafe | event/lease locks and CAS, atomic persistence, one-winner acquire, bounded pool, directory-anchored evidence reads and dirfd-bound adjudication writes | **PARTIAL** — distributed/Postgres transactions, cross-file adjudication transactions and hostile same-UID rename schedules remain untested | FBL-002, FBL-005, FBL-014, FBL-020, FBL-027, FBL-028, FBL-030 |
| Denial of service | unbounded/invalid compute, retry arithmetic, cycles, FIFO blocking, archive expansion, unbounded remote bodies and per-record-only limits | CPU/RAM/wall/PID/output limits, cycle detection, finite validation, 120s cap, nonblocking bounded files, bounded remote streams and aggregate/archive limits | **PARTIAL** — global event/artifact/cache quotas, model tokens and full-service admission control remain incomplete | FBL-005, FBL-009, FBL-010, FBL-014, FBL-020, FBL-026, FBL-027, FBL-034 |
| Unbounded loops | hostile compute and blueprint cycles could run indefinitely | compute wall/CPU termination and blueprint cycle rejection | **PARTIAL** — arbitrary `max_iterations`/provider loops and all algorithms lack a unified campaign deadline | FBL-005, FBL-007, FBL-009, FBL-020 |
| Unbounded tokens | no live model gateway budget/token enforcement | local `BudgetLedger` charges branch work; deterministic runner only | **RESIDUAL** — `ModelRunner` has no max input/output token contract or provider cancellation | FBL-007, FBL-014, FBL-018 |
| Unbounded compute | compute/resource values and controller spend could evade bounds | strict compute limits and global/branch budget accounting | **PARTIAL** — distributed provider/container budgets and full campaign quotas unverified | FBL-005, FBL-009, FBL-020 |
| Unbounded storage | process-local stores, repeated evidence records and provider archives lacked strong aggregate bounds | per-document/artifact/output/object/archive bounds and atomic content addressing | **RESIDUAL** — no total event/artifact/cache retention quota, pruning, tenant quota or disk-full recovery campaign | FBL-002, FBL-005, FBL-011, FBL-014, FBL-026, FBL-027 |
| Evaluator hacking / benchmark-answer leakage | evaluation identity omitted behavior and executable fixture source used raw `eval`; registries were counted as studies | full local config identity, closed AST fixture interpreter, valid stats/dates, no expected outcome passed into research | **PARTIAL** — no sealed external datasets, contamination audit, blind graders or paired study | FBL-015, FBL-019 |
| Persistent memory contamination | truthy dictionaries entered cross-problem semantic memory | current truth snapshot/log/T2/I2/R2 gate required and speculative output quarantined | **PARTIAL** — memory is not durable/event-revoked and no later-run feedback was demonstrated | FBL-013 |
| Communication overstatement | incomplete I/N/S/R, a forged legacy gate string, candidate-only fixture success or certificate/result misbinding could render/report verified-sounding output | exact release thresholds, unresolved-axis honest-no-result and authenticated current release handoff required at render; legacy renderer retired; fixture success joins current replay/contract/claim/interpretation/gate/certificate/promotion state | **PARTIAL** — known paths are targeted, but no legacy migration bridge, immutable envelope boundary or complete API-surface inventory exists | FBL-006, FBL-007, FBL-022, FBL-024, FBL-031, FBL-033 |
| Verifier bypass | caller callbacks/booleans/reviewer labels/hardening and same-process identity notaries manufactured pass/T5 | trusted checker registry/protocol, authenticated formal/legacy evidence, exact run binding and pessimistic attack aggregation | **PARTIAL** — independent external referee/kernel/provider attestation is absent and full persisted dimensional model/formal precedence remains partial | FBL-003, FBL-004, FBL-012, FBL-022, FBL-025, FBL-028 |
| Gate bypass / cached approval | raw profile/direct render/sign-before-promotion/stale state/status-only publish, candidate-only or cross-context fixture success and caller-writable cache replay worked | truth snapshot -> attested gates -> promotion auth -> certificate -> complete current-subject join -> render/fixture success; legacy publisher retired; legacy model transcripts are diagnostic-only and never replayed | **PARTIAL** — the legacy path is unavailable rather than integrated, mutable alternate consumers remain and no absent API surface can be enumerated | FBL-006, FBL-007, FBL-022, FBL-024, FBL-028, FBL-029, FBL-031, FBL-033 |
| Self-approval / confused deputy | orchestrator self-issued I2; authorities were prompts; reviewer/provider/checker labels implied independence | signed exact disclosures, authority capabilities, lineage/same-pass restrictions and absent-attestor fail-closed behavior | **PARTIAL** — a same-process HMAC helper is not organizational independence | FBL-004, FBL-007, FBL-008, FBL-012, FBL-022, FBL-025 |
| Unsafe defaults | fallback keys, unsigned policy, host “sandbox,” optimistic missing probes/adapters | strong required keys; signed closed policy; OEIS offline/read-only; no sandbox fallback; unexecuted/unknown blocks; M2 readiness false | **LOCALLY MITIGATED** on named defaults; complete service deployment defaults unverified | FBL-001, FBL-005, FBL-011, FBL-014, FBL-017 |
| Weak key handling | public/local fallbacks, caller signatures and an external CLI inheriting all trust keys | minimum 32-byte per-domain secrets, key fingerprints, distinct release domains, config exclusion and minimal child environments | **PARTIAL** — symmetric keys lack rotation/HSM/mTLS; same-process notaries and pairwise separation remain limited | FBL-001, FBL-002, FBL-004, FBL-006, FBL-008, FBL-018, FBL-022, FBL-024 through FBL-026 |
| Fail-open behavior / silent degradation | malformed inputs became empty/pass, missing probes passed, external status/mock success and broad caller labels were optimistic; advisory state, mutable caches, candidate/cross-context fixture success, uncaught integrity errors, TLS verification bypass and an overbroad OEIS exception handler could consume, forge or silently omit later work | typed failures, strict schemas, unknown blocks, no unsandboxed/mock fallback, missing authority/review/gates reject without terminal success, advisory records remain retryable, legacy cache replay is disabled, verified fixture expectations require a complete current release join, event errors are structured, ingestion is HTTPS/TLS/bounds enforced and OEIS enumeration skips only typed transform-precondition failures | **PARTIAL** — external failure/recovery and every broad exception site were not live-tested; absent services remain unavailable | FBL-003 through FBL-014, FBL-017, FBL-020, FBL-022, FBL-024 through FBL-035 |

## Security finding cross-reference

Every row below points to a complete required-field record in
`FABLE_REMEDIATION_LOG.md`. “Closed” means the original local reproduction is
green; it does not erase the stated residual.

| Finding | Initial security consequence | Regression/fix evidence | Security disposition |
|---|---|---|---|
| FBL-001 | unauthenticated feature enablement and forged trust records | signed closed policy/config/CLI adversarial tests | Original bypass closed; deployment key management partial |
| FBL-002 | history erasure/lost update/revocation resurrection | corruption/truncation/concurrency/replay/snapshot tests | Local M1 closed; anti-rollback/distributed residual |
| FBL-003 | false/irrelevant worker output promoted truth | truth/compute/orchestrator forged-evidence tests | Original bypass closed; general semantic coverage partial |
| FBL-004 | arbitrary text/status labeled Lean/equivalent/T5 | 132 focused formal/release tests and correspondence security | Protocol bypass closed; live formal stack blocked |
| FBL-005 | host code execution/credential theft/DoS | 67 compute/security tests and Docker negative path | Local attacks closed; true OCI success blocked |
| FBL-006 | stale/wrong-target/partial result signed and rendered | gate mutation/substitution/freshness/direct render tests | EGMRA chain closed; legacy publisher retired with no migration bridge |
| FBL-007 | self-approved/fabricated “end to end” release | 71 production-path tests | CLI slice substantially fixed; complete orchestration partial |
| FBL-008 | privilege escalation/data leakage/self-approval | authority scope/tamper/expiry/permission tests | Local capability boundary closed; deployment isolation partial |
| FBL-009 | resource abuse/poisoned posterior/fake progress/cycle DoS | 32 search tests | Local invariants closed; durable/full algorithms partial |
| FBL-010 | provenance/cache substitution/injection/inapplicable theorem | 16 retrieval tests | Packet boundary closed; live retrieval security partial |
| FBL-011 | cache poisoning/query injection/false OEIS truth | 21 OEIS tests | Local boundary closed; live service partial |
| FBL-012 | forged/correlated reviewer result promoted release | 19 verification plus orchestrator referee tests | Local aggregation closed; organizational independence partial |
| FBL-013 | false persistent memory poisoning | 15 learning plus orchestrator quarantine tests | Original admission closed; durable feedback loop absent |
| FBL-014 | object traversal/substitution/DSN secret leak and fake M2 | 18 M2/object/DSN tests | Local store closed; real external services unverified |
| FBL-015 | security bypasses coexisted with green suite | new adversarial suites | Detection materially improved; external acceptance gaps remain |
| FBL-016 | CI silently omitted architecture security suite | workflow/locked pytest | Exclusion closed; static tooling/parity residual |
| FBL-017 | wrong-target/domain/vacuity and self-intent release | intake/intent/orchestrator tests | Tested elementary semantics closed; general translation partial |
| FBL-018 | secret persistence/cache poisoning/false identity | foundation/config/model identity tests | Caller forgery closed; real provider/key isolation partial |
| FBL-019 | fixture arbitrary code and invalid benchmark claims | AST/config/stat/date, no-`eval`, and bare-helper tests | Local exploit closed; real sealed evaluation absent |
| FBL-020 | stale worker/double acquire/retry DoS/starvation | 19 control plus stale-output tests | Local controller closed; distributed control partial |
| FBL-021 | numerical poison/unsafe acquisition | 19 selection tests | Local input boundary closed; campaign validation partial |
| FBL-022 | real legacy gate false promotion/arbitrary file read | legacy trust tests and complete historical unittest run | Original gate/loader bypasses contained; unattested browser runner advisory and publisher retired |
| FBL-023 | forged/mutable checkpoint, unrelated-history resume and unsafe cache reuse | 14 checkpoint adversarial tests; 38 dependent tests | Local checkpoint boundary closed; durable production resume absent |
| FBL-024 | direct forged gate status published arbitrary verified output and category escaped root | unconditional-retirement and forged-run-status quarantine regressions | Original publisher bypass closed by retirement; legacy publication intentionally unreachable |
| FBL-025 | local signer notarized asserted provider/checker identity | canonical binding, artifact-byte rehash, relabel and no-attestor fail-closed tests | Field/materialization forgery narrowed; same-process HMAC is not independent identity and real gateway is blocked/unreachable |
| FBL-026 | Aristotle child inherited signing keys, followed run symlinks, expanded unbounded archives and executed vendor Lake configuration | minimal-env/redaction, ancestry/symlink, bounded archive/type and no-host-vendor-build regressions | Original local attacks closed/fail-closed; live Aristotle and hardened T5 service unverified |
| FBL-027 | duplicate/oversized/FIFO/resource/TOCTOU/policy-order defects in legacy parsing and evidence loading | strict duplicate/numeric bounds, nonblocking/aggregate/anchored-open/policy-order and materialization-byte regressions | Original local loader attacks closed; same-process evidence origin and service-wide quotas remain residual |
| FBL-028 | unavailable/advisory adjudication poisoned retry and model dissent overrode formal truth | no-call/no-marker, advisory rediscovery and direct materialized formal-truth regressions | Queue/auth fixed and direct gate preserves encoded truth; persisted production path, gateway and full dimensional adjudication remain partial/absent |
| FBL-029 | caller-writable stage response plus adjacent digest replayed as authenticated model output | response+metadata forgery and fresh-provider-call regressions | Unauthenticated replay closed by disabling model-output cache reads; authenticated restart replay remains unavailable |
| FBL-030 | symlinked artifact/problem roots redirected proof and adjudication writes | root/problem symlink, zero-provider-call and unchanged-outside-tree regressions | Static substitutions closed locally; same-UID concurrent rename and cross-file transaction residuals remain |
| FBL-031 | fixture CLI exited 0 for “verified” while promotion was disabled and release was null | policy-blocked negative and real-release positive CLI regressions | Candidate-only false success closed on the fixture CLI; live end-to-end verification remains unavailable |
| FBL-032 | event-integrity CLI used a hidden default run ID and crashed on real logs | exact-run success, wrong-run and tampered-event public-CLI regression | Operational verifier fixed locally; external run registry and anti-rollback witness remain absent |
| FBL-033 | authentic release certificate was accepted after surrounding result/contract identity mutation | cross-contract replay plus missing/forged/stale certificate CLI regressions | Complete current-subject join fixed on fixture CLI; mutable alternate consumers remain a residual |
| FBL-034 | external-source adapters disabled or under-enforced TLS, scheme, redirect, host, body and cleanup boundaries | five ingestion plus two OEIS regressions (OEIS red `2 failed`, then green), 52-test ingestion and 24-test OEIS batches, clean production Bandit medium/high scan | Local network boundaries fixed; live TLS/recovery and deployment DNS/egress controls remain unverified |
| FBL-035 | unexpected OEIS transform defects were swallowed and silently removed a transformed query path | monkeypatched `RuntimeError` propagation regression plus 167-test dependent batch | Enumeration now skips only `TransformError`; local boundary closed, live OEIS and external failure recovery remain unexercised |

## External integration security/readiness ladder

The columns implement the requested seven-level distinction. “Yes” never
implies a later column.

| Integration | 1 Interface exists | 2 Config validation | 3 Mock/protocol tests | 4 Local integration | 5 Real service exercised | 6 Failure/recovery exercised | 7 Production readiness |
|---|---|---|---|---|---|---|---|
| Lean/Lake/Mathlib | Yes | Partial pinned identity/protocol | Yes, structured checker simulation | Protocol subprocess only | **No**; Elan shims have no toolchain | Timeout/malformed/protocol failure yes; real recovery no | **No** |
| Independent Lean checker | Yes | executable/hash/key validation | Yes | Simulated executable response | **No real checker** | malformed/secret/timeout paths yes | **No** |
| Model providers | `ModelRunner`/`AttestedRunner` | identity/key fields only | Deterministic/injected runner | Deterministic local | **No** | unconfigured fail-closed only | **No** |
| Aristotle CLI/service | Request/routing/legacy adapter | signed policy, minimal environment, bounds | Yes | fake CLI plus real filesystem/archive quarantine | **No** | malformed/archive/symlink/timeout/vendor-only rejection yes; live recovery no | **No** |
| OEIS HTTP | Yes | offline/read-only/query/cache/rate fields | Fake fetcher plus strict parser | local cache/transforms/orchestrator injected client | **No live HTTP** | malformed/cache/offline yes; live rate recovery no | **No** |
| Citation/literature/theorem retrieval | local interfaces/records | packet/query validation | local corpus | one local lexical index | **No live indexes** | malformed/local conflicts partial | **No** |
| PostgreSQL | `PostgresEventStore` | strict redacted DSN and schema/connect timeout | config/failure tests | **No server** | **No** | missing dependency/connection failure only | **No** |
| Docker/OCI | `ContainerSandbox` | runtime/local immutable image/policy | command/fail-closed tests | Docker 29.5.3 real runc negative/entrypoint path | Runtime yes; **no successful compatible math job** | unavailable/cleanup/entrypoint failure yes | **No** |
| Sage/CAS/SAT/SMT/ILP/graph backends | protocols/small local checkers | Partial | local helper tests | no container portfolio | **No** | not meaningfully | **No** |
| Local object store | Yes | size/root/digest/mode validation | Yes | Yes, local filesystem | N/A, not remote | corruption/symlink/root/concurrency tested | Local M1 only; **not scale-ready** |

## Key and secret boundary audit

Current named trust domains include policy, event, evidence, truth snapshot,
checkpoint, Lean checker, intent review, formal correspondence, authority,
model attestation, gate, promotion, release, legacy review and legacy evidence.
All are documented as environment-only secrets and included in
`EgmraConfig.SECRET_ENV_VARS`; config loading recursively rejects them.
Individual authorities require at least 32 bytes. Gate/promotion/release keys
must be mutually distinct before a release can be signed.

This is appropriate local test scaffolding, not production key management:

- there is no rotation, expiry, revocation or historical verification-key set;
- there is no HSM/KMS, mTLS identity, separate Unix account/container or
  per-service secret mount demonstrated;
- other trust domains do not all enforce pairwise key inequality;
- tests intentionally place many keys in one process environment; and
- a privileged host process can read/forge every local HMAC domain it owns.

Therefore HMAC evidence establishes integrity relative to the configured local
authority, not organizational independence against a compromised host.

## Persistence and concurrency security

Local M1 persistence is now meaningfully hardened:

- event records and committed head are authenticated; payloads are complete
  enough to replay the graph; writers lock and compare optimistic versions;
- truth snapshots bind claim status/version/profile/evidence to run, count,
  head and Merkle root;
- compute and object artifacts use content identity, bounded regular files,
  atomic/fsync publication and corruption/symlink/root checks;
- leases persist monotonic fences and reject expired/stale owners; and
- release/gate/certificate verification consumes the current event head.

Material residuals remain:

- local rollback of both event log and head has no external witness;
- checkpoint/resume, controller/search state, memory and cache compatibility are
  not one demonstrated crash-consistent transaction;
- no PostgreSQL SCC/revocation/lease transaction or multi-host partition ran;
- no total storage quota/disk-full/retention/compaction recovery exists; and
- filesystem defenses do not claim immunity from every nanosecond TOCTOU by a
  hostile process with write access to the same directories.

## Security verification evidence

The following focused evidence was observed during remediation. These counts are
subsystem evidence, not the final full-suite count:

```text
compute/security:                         67 passed
truth/security/snapshot combined batch:  42 passed
Lean/release/truth/comms focused batch:  132 passed
authority/agents/truth combined batch:   32 passed
search combined batch:                   32 passed
retrieval combined batch:                16 passed
OEIS combined batch:                     24 passed
OEIS failure-propagation/dependent batch: 167 passed
verification combined batch:             19 passed
learning combined batch:                 15 passed
control combined batch:                  19 passed
selection combined batch:                19 passed
orchestrator/intake/CLI/eval batch:       71 passed in 6.83s
checkpoint/orchestrator/acceptance batch: 38 passed in 1.01s
M2/object/DSN batch:                      18 passed in 0.07s
legacy trust/verification/status:         33 passed in 0.10s
proof/adjudication/cache:                 35 passed, 5 subtests in 0.34s
Aristotle adapter/filesystem/archive:     34 passed, 8 subtests in 0.54s
fixture CLI release expectation:           2 passed in 0.56s
event CLI exact-run integrity:              1 passed in 0.10s
CLI certificate/result binding (`-W error`): 23 passed in 2.63s
ingestion/network boundary focused:       52 passed
complete legacy unittest discovery:      231 passed in 1.414s
current legacy/CLI focused consolidation: 121 passed, 13 subtests in 2.66s
EGMRA Ruff:                              all checks passed
production mypy source scan (tests excluded): no issues in 153 source files
EGMRA Bandit production scan (medium+):  no findings (tests excluded)
final EGMRA suite (`-W error`):           555 passed in 11.34s
final complete suite (`-W error`):        786 passed, 44 subtests in 13.19s
```

As optimization-safety defense-in-depth, removable assertions in the lease,
checkpoint, blackboard, compute-persistence and Lean-service invariant paths
were replaced with explicit typed errors. Those guards therefore remain active
under `python -O`; this hardening is not recorded as a separate finding.

External observations:

- Docker server 29.5.3 was reachable and a local image exercised the actual
  runc negative/entrypoint path; a compatible Python image pull blocked in the
  credential helper and was interrupted.
- `lean --version` and `lake --version` exited 1 because no default Elan
  toolchain is configured.
- PostgreSQL client/server were absent.
- No live model provider, Aristotle, OEIS, citation/theorem service, benchmark
  grader or public release API was exercised.

The clean full-suite result, warnings, skips, exact final counts and final search
for unsafe markers belong to `FABLE_FINAL_VERIFICATION.md`; they are not
predeclared here.

## Remaining security limitations

### Verified locally

- signed closed policy/key absence behavior;
- event corruption/truncation/reorder/duplicate/concurrency/replay detection,
  subject to the dual-rollback caveat;
- exact claim-bound evidence and direct status-mutation resistance;
- restricted-executor capability/resource/schema controls and no fallback;
- formal/gate/certificate binding protocol and direct bypass rejection;
- local authority scopes, fencing, object/artifact integrity;
- legacy policy-before-load, confined evidence and artifact-byte rehashing;
- legacy publisher/run-status quarantine, advisory retry/auth preflight, and
  diagnostic-only model stage transcripts; and
- Aristotle minimal-child-environment, static symlink/archive bounds and
  no-host-vendor-project execution.

### Verified only with protocol simulations/mocks

- positive Lean/checker certificate issuance;
- positive provider/model identity adapter behavior;
- OEIS response handling;
- formal-correspondence and independent-referee organizational identity; and
- external retrieval/import applicability.

### Blocked by credentials/infrastructure or absent implementation

- successful compatible OCI mathematical computation and full backend suite;
- real Lean/Lake/Mathlib clean rebuild and independent checker;
- live Postgres, external models, Aristotle, OEIS, citation/theorem retrieval;
- distributed scheduler/lease/recovery and production service topology;
- HSM/KMS/service identity/anti-rollback anchor; and
- public API/release portal and external benchmark evaluation.

### Unresolved repository-local risks

- model token limits, total storage quotas and full campaign admission control;
- no live prompt/retrieval injection campaign;
- no durable learning feedback into a subsequent selection;
- no compatible legacy-to-EGMRA publication migration bridge (legacy output is
  intentionally unavailable);
- incomplete general mathematical parsing/probe/formal correspondence; and
- local co-residence of several symmetric trust keys.

## Cross-document consistency notes

The following current-language statements elsewhere in the audit artifacts are
stale relative to the code and regressions recorded here; those files were not
silently rewritten as part of this focused report update:

- `FABLE_CODE_INVENTORY.md` still describes the legacy publisher as a separate,
  disconnected authority. `publish_verified_result` now raises unconditionally,
  and legacy `has_verified_result` always returns false. The accurate current
  classification is **retired/unreachable with no EGMRA migration bridge**, not
  a second active publisher.
- `FABLE_CODE_INVENTORY.md` and some `FABLE_TRACEABILITY_MATRIX.md` cache wording
  can be read as if the legacy model-stage cache supports compatible replay.
  FBL-029 deliberately removed all such reads: transcripts are diagnostic only,
  and authenticated replay/restart remains partial rather than verified.
- `audit/orchestrator_integration_remediation.md` retains a current-tense HIGH
  residual for incomplete formal-correspondence reviewer disclosure. The later
  `egmra/lean/correspondence.py` validation and
  `egmra/tests/test_formal_correspondence_security.py` regressions require exact
  reviewer disclosure, independence from formalization/governance and empty
  conflicts. Local symmetric-key/process-isolation and live-reviewer limitations
  remain, but the named disclosure-shape defect is no longer current.
- Phase 1-4 audit files and audit-start test totals remain valid historical
  snapshots when explicitly labeled as such; they are not post-remediation
  verification evidence.

## Security conclusion

The repository no longer supports the pre-audit statement “no security flaws.”
The canonical finding index contains ten CRITICAL, twenty-three HIGH, one MEDIUM,
and one LOW finding. The tested local remediation closes or fail-closes the named
original local critical exploit paths and adds meaningful negative coverage. It does
not establish production isolation, organizational independence, distributed
durability or external-service readiness. The complete architecture must remain
less than verified while these residual and blocked requirements exist.
