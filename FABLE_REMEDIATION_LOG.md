# FABLE Remediation Log

## Scope and evidence policy

This is the canonical finding register for the independent audit. Pre-fix
observations refer to the isolated audit-start snapshot at commit
`4b4ec96f1c81492af02f814c65825a5106e0af60` and to red tests/probes written
against that behavior. File line ranges identify the current remediated symbols;
the superseded implementation remains reproducible from
`/tmp/erdos-baseline.t2afE1/src` during this audit. A green post-fix test proves
only the named local behavior. It does not turn an unexercised provider,
database, container, kernel, corpus, or distributed service into verified
production behavior.

The findings deliberately preserve architectural residuals. “Fixed locally”
means the original reproduction no longer succeeds through the tested local
entry point; it does not mean the complete affected F-REQ is `VERIFIED`.

## Finding index

| Finding | Severity | Short title | Local remediation | Material residual |
|---|---|---|---|---|
| FBL-001 | CRITICAL | Unsigned policy, public/fallback keys, permissive configuration | Fixed locally | Key isolation/rotation and exhaustive legacy-entry inventory remain |
| FBL-002 | CRITICAL | Non-authoritative event history and lost replay/concurrency semantics | Fixed for local M1 | Dual log/head rollback needs an external monotonic anchor; no live Postgres |
| FBL-003 | CRITICAL | Forged evidence and false computation could promote truth | Fixed for authenticated local path | Claim-specific semantic coverage checker remains narrower than full specification |
| FBL-004 | CRITICAL | Caller-manufactured Lean, equivalence, correspondence, and T4/T5 | Fixed as local protocol | Real Lean/Lake/Mathlib and independent checker not exercised |
| FBL-005 | CRITICAL | Host execution presented as a sandbox; unsafe fallback | Fixed/fail-closed locally | Successful compatible OCI computation and full backend portfolio blocked/unimplemented |
| FBL-006 | CRITICAL | Caller/stale release gates and bypassable signing/rendering | Fixed for EGMRA CLI slice | Legacy publisher is retired; no migration bridge or complete API-surface inventory exists |
| FBL-007 | CRITICAL | Disconnected orchestrator fabricated or ignored decisive state | Substantially remediated in CLI slice | No durable checkpointed distributed closed loop or live external services |
| FBL-008 | HIGH | Prompt-only authorities and leaking mutable blackboard | Fixed locally | Deployment-level identity/key separation absent |
| FBL-009 | HIGH | Incorrect and disconnected search/accounting semantics | Core local defects fixed and wired | Search persistence and real AO*/MCTS/MAP-Elites/Lean search remain partial |
| FBL-010 | HIGH | Mutable/incomplete retrieval provenance and lexical “proof” | Core local defects fixed | Four live indexes, formal elaboration, and injection campaign unverified |
| FBL-011 | HIGH | OEIS cache/type/match failures could fabricate support | Fixed locally | Live OEIS HTTP/rate/recovery/schema drift unexercised |
| FBL-012 | HIGH | Reviewer labels and booleans could manufacture verification | Fixed locally | Organizationally independent referee/provider service absent |
| FBL-013 | HIGH | Truthy records could contaminate persistent learning | Admission fixed locally | Stores remain process-local; no demonstrated later-behavior feedback loop |
| FBL-014 | HIGH | M2/external adapters were facades and local store was unsafe | Local store/config fixed, interfaces fail closed | Live Postgres/Lean/OEIS/providers/Aristotle/compatible OCI remain external or incomplete |
| FBL-015 | HIGH | Passing tests did not prove claimed architecture/acceptance | Major adversarial coverage added | Several full acceptance criteria remain unavailable or partial |
| FBL-016 | HIGH | CI excluded all EGMRA tests and pytest was undeclared | Fixed in manifests/workflow | No configured lint/type/security tool; local 3.10/3.12 parity unavailable |
| FBL-017 | HIGH | Statement IR lost semantics and unexecuted probes passed | Fixed for tested deterministic inputs | Independent semantic model parsing and complex math semantics remain partial |
| FBL-018 | HIGH | Secrets/config and caller model-attestation/cache identity defects | Fixed locally | No real provider attestation service or process-isolated signing key |
| FBL-019 | HIGH | Evaluation identity omitted behavior; fixture code execution | Local schemas/evaluator fixed | No external benchmark runner, sealed data, blind grading, or paired study |
| FBL-020 | HIGH | Leases/backoff/capacity failed under expiry, races, restart | Fixed for local persisted controller | Distributed partitions/deadlock/starvation/provider integration untested |
| FBL-021 | MEDIUM | Selection accepted invalid inputs and omitted hard constraints | Fixed locally | Selector remains a small local component, not a validated campaign policy |
| FBL-022 | CRITICAL | Legacy production gate trusted caller truth, labels, and arbitrary evidence paths | Fixed/fail-closed locally | Legacy browser runner is unattested and legacy publication is retired, not integrated with EGMRA |
| FBL-023 | HIGH | Checkpoints were mutable, forgeable, unrelated to history, and identity-free | Local boundary fixed | No durable production resume/reconstruction/continuation path |
| FBL-024 | CRITICAL | Direct legacy publisher trusted a forged gate status and accepted path-like categories | Closed by fail-closed retirement | Legacy publisher is unavailable; only the EGMRA certificate renderer may publish |
| FBL-025 | HIGH | Same-process attestation helpers could notarize asserted provider/checker identity | Fail-closed wiring improved | No isolated asymmetric provider/checker attestation gateway exists |
| FBL-026 | CRITICAL | Aristotle child-process, archive, and run-directory boundaries leaked secrets and followed attacker paths | Fixed/fail-closed locally | No live Aristotle service or hardened T5 execution was exercised; vendor projects remain quarantined |
| FBL-027 | HIGH | Legacy parsing/evidence loading could accept ambiguous or oversized input, block, race, over-consume resources, or inspect disabled formal evidence | Fixed for tested local attacks | Same-process evidence origin, hostile concurrent ancestor replacement and total-storage admission control remain |
| FBL-028 | HIGH | Adjudication could poison retry state and let model dissent override formal truth | Queue/auth fixed; direct materialized gate preserves encoded truth | Persisted production path, authenticated gateway and full dimensional adjudication remain partial/unavailable |
| FBL-029 | HIGH | Caller-writable model-stage cache used circular adjacent-digest authentication | Replay disabled; diagnostic writes only | Authenticated model-output replay and legacy restart/resume are unavailable |
| FBL-030 | HIGH | Symlinked legacy artifact/problem roots redirected production writes | Fixed for tested static substitution | Same-UID concurrent rename/TOCTOU and cross-file transaction risks remain |
| FBL-031 | HIGH | Fixture CLI reported verified success without promotion or release | Fixed for tested CLI path | Fixture success remains a local deterministic slice, not live end-to-end verification |
| FBL-032 | HIGH | Event-integrity CLI ignored the real run binding and crashed on production logs | Fixed for tested CLI path | Local log/head dual rollback and external run-ID discovery remain residual |
| FBL-033 | HIGH | Verified fixture expectation accepted an authentic certificate misbound to mutated result/contract identity | Fixed for tested CLI path | Result objects remain mutable and alternate consumer inventory is incomplete |
| FBL-034 | HIGH | External source adapters disabled or under-enforced TLS/redirect/body boundaries | Fixed for tested ingestion/OEIS paths | Live TLS/redirect recovery and deployment egress controls remain unverified |
| FBL-035 | LOW | OEIS transform enumeration silently swallowed internal implementation failures | Fixed locally | Live OEIS HTTP and end-to-end external failure recovery remain unexercised |

## Detailed findings

### FBL-001 — Unsigned policy, public/fallback keys, and permissive configuration

- **Finding ID:** FBL-001.
- **Severity:** CRITICAL.
- **Affected F-REQ IDs:** F-REQ-014, F-REQ-015, F-REQ-149,
  F-REQ-150, F-REQ-174, F-REQ-203, F-REQ-204.
- **Specification source:** §1 lines 74-76; §13.2 lines 2010-2011 and
  2019; §13.6 line 2060; §15 lines 2217-2238; §16 lines 2252-2294.
- **Files and line ranges:** `egmra/policy/__init__.py:66-187,204-258`;
  `egmra/config.py:17-147`; `egmra/cli.py:126-169,173-206`;
  `promote_verified_run.py:25-89`.
- **Symbols:** `FeaturePolicy`, `_resolve_key`, `sign_policy`,
  `verify_signature`, `load_policy`, `PolicyEnforcer.require`,
  `EgmraConfig.load`, `EgmraConfig.secret`, `cmd_policy_sign`.
- **Expected behavior:** one authenticated, closed-schema feature policy is
  enforced at every promotion-capable entry point; absent, weak, unknown,
  malformed, unsigned, duplicate-key, or wrong-key policy/configuration fails
  closed without exposing secrets.
- **Observed behavior (pre-fix):** an unsigned in-memory policy could enable and
  enforce promotion; trust domains used public/local fallback HMAC keys;
  unknown/type-confused values and duplicate JSON keys could be normalized;
  missing explicit config files were silently ignored; nested/case-varied
  secrets and arbitrary environment reads were insufficiently constrained.
- **Reproduction command or test:** pre-fix direct probe constructing
  `FeaturePolicy(flags={"promotion": True})`; red regression
  `egmra/tests/test_adversarial_truth_security.py::test_unsigned_feature_policy_fails_closed`;
  config/model red batch in `egmra/tests/test_adversarial_foundations.py`.
- **Root cause:** policy records and configuration shape were treated as trusted
  local inputs; authentication was optional and several trust domains shared
  convenience fallbacks.
- **Impact:** any caller able to reach the affected process could enable
  promotion or forge integrity records, defeating the P0 stop-false-promotion
  boundary and possibly persisting secrets.
- **Whether existing tests detected it:** no. Audit-start tests explicitly
  relied on unsigned policies and convenience keys.
- **Fix performed:** require `EGMRA_POLICY_KEY` of at least 32 bytes; use a
  closed immutable Boolean flag schema; reject unknown/duplicate/malformed
  documents; verify signature at enforcement; remove fallback keys; require
  explicit regular non-symlink config/policy files; recursively deny secret
  keys in config; allowlist secret reads; validate numerical and Boolean values;
  create signed policy output exclusively at mode 0600 without overwrite.
- **Regression test added:** the two policy tests in
  `test_adversarial_truth_security.py`; all tests in
  `test_adversarial_foundations.py`; CLI missing-key/overwrite/symlink tests.
- **Post-fix verification:** policy/truth focused suites passed as part of the
  42-test truth batch; the orchestrator/CLI focused suite passed 71 tests; the
  original unsigned-policy reproduction now raises/rejects.
- **Residual limitation:** the repository has no HSM/secret manager, key
  rotation/revocation protocol, or process-level separation among all local
  HMAC authorities. The legacy publisher is retired fail-closed, but there is no generated
  inventory proving a single policy transaction wraps every existing top-level
  script and future entry point.
- **Confidence:** high for the reproduced local paths; medium for exhaustive
  repository-wide entry-point coverage.

### FBL-002 — Event history was not authoritative, replayable, or concurrency-safe

- **Finding ID:** FBL-002.
- **Severity:** CRITICAL.
- **Affected F-REQ IDs:** F-REQ-006, F-REQ-017, F-REQ-106 through
  F-REQ-119, F-REQ-128, F-REQ-153, F-REQ-157, F-REQ-178, F-REQ-181,
  F-REQ-197, F-REQ-203.
- **Specification source:** §10.1 lines 1469-1567; §10.2 lines
  1569-1619; §10.3 lines 1621-1652; §10.4 lines 1654-1680; §13.3 line
  2025; §13.6 lines 2064 and 2067; §14.3 lines 2142-2149; §15 lines
  2217-2238.
- **Files and line ranges:** `egmra/truth/events.py:60-396`;
  `egmra/truth/graph.py:55-706`; `egmra/truth/revocation.py:1-161`;
  `egmra/truth/snapshots.py:17-145`.
- **Symbols:** `EventLog.append`, `EventLog.verify_integrity`,
  `EventLog._verify_head`, `EventLog._validate_optimistic_versions`,
  `EpistemicGraph._replay_events`, graph mutation methods, `TruthSnapshot`.
- **Expected behavior:** every state transition is signed, append-only,
  ordered, versioned, durable, replayable, and atomic; corruption, insertion,
  deletion, truncation, duplication, reordering, stale writers, and revocation
  loss are detected; the graph rehydrates all semantic state after restart.
- **Observed behavior (pre-fix):** a valid-prefix truncation verified; two
  writers could both begin at sequence zero; events omitted enough entity data
  that a fresh graph could not reconstruct claims/evidence/status; materialized
  status could change before a failed append; direct mutation and stale graph
  writers were not a closed boundary; SCC revocation was not demonstrated after
  restart.
- **Reproduction command or test:** direct truncate-and-reopen probe; red tests
  `test_event_log_detects_valid_prefix_truncation`,
  `test_event_log_serializes_concurrent_writers`,
  `test_graph_rehydrates_semantic_state_from_authoritative_events`,
  `test_failed_event_append_does_not_mutate_materialized_graph`, and
  `test_full_graph_revocation_and_branch_state_survive_restart` in
  `egmra/tests/test_adversarial_truth_security.py`.
- **Root cause:** a simple per-record chain was mistaken for an authoritative
  event-sourced database; there was no committed head, writer lock/CAS, complete
  reducer payload, or event-before-view transaction discipline.
- **Impact:** an attacker or crash could erase/replace apparent history, produce
  lost updates, resurrect revoked support, or leave signed records that did not
  determine the state released to users.
- **Whether existing tests detected it:** no. They inspected one live
  in-memory graph and verified only ordinary append/hash-chain behavior.
- **Fix performed:** strong event key; canonical signed payloads; duplicate-key
  rejection; authenticated sidecar head containing count/head/Merkle; OS file
  lock and optimistic versions; atomic/fsync mode-0600 writes; complete entity
  payloads and reducer replay; event-before-materialized mutation; private
  router authority; versioned intent/revocation/branch changes; replay-derived
  signed truth snapshots bound to event count/head/Merkle.
- **Regression test added:** 20+ truth-security cases covering corruption,
  truncation, insertion/deletion/reorder/duplicate/forgery, 32 concurrent
  writers, replay, atomicity, stale writers, direct mutation, and restart
  revocation; four snapshot tests in `test_truth_snapshots.py`.
- **Post-fix verification:** combined truth batches passed 42 tests; corrupted,
  truncated, reordered, duplicated, stale, and replay cases all fail closed.
- **Residual limitation:** a privileged attacker who rolls back both the JSONL
  log and its local authenticated head to the same earlier pair cannot be
  detected without an external monotonic anchor or replicated service. Live
  PostgreSQL transactions, migrations, partitions, and recovery were not run.
- **Confidence:** high for tested single-host M1 behavior; low for unexercised
  distributed/M2 behavior.

### FBL-003 — Forged evidence and false computation could promote claims

- **Finding ID:** FBL-003.
- **Severity:** CRITICAL.
- **Affected F-REQ IDs:** F-REQ-006, F-REQ-010, F-REQ-014,
  F-REQ-032, F-REQ-047, F-REQ-062, F-REQ-063, F-REQ-109,
  F-REQ-112, F-REQ-129, F-REQ-150, F-REQ-160, F-REQ-203.
- **Specification source:** §6.6 lines 714-732; §6.8 lines 733-765;
  §10.1 lines 1515-1539; §10.2 lines 1571-1582; §11.3 lines
  1733-1745; §13.2 lines 2011 and 2019; §13.3 line 2028.
- **Files and line ranges:** `egmra/truth/entities.py:180-340`;
  `egmra/truth/validators.py:32-371`; `egmra/truth/router.py:17-214`;
  `egmra/compute/service.py:99-588`;
  `egmra/orchestrator/loop.py:621-957,1132-1225`.
- **Symbols:** `Evidence`, `attest_evidence`, `validate_computation`,
  `validate_evidence`, `EvidenceRouter.admit`,
  `ComputeService.verify_certificate`, `_authenticate_computation_proposal`.
- **Expected behavior:** evidence is authenticated, immutable, claim-bound,
  replayable, and semantically validated by kind; generator status fields never
  substitute for artifact content, coverage, independent replay, or trusted
  checker output; false results cannot support claims.
- **Observed behavior (pre-fix):** caller metadata such as exactness,
  `result_verified`, independence, and certificate status could be signed or
  shaped into accepted evidence; a forged exact-computation record promoted a
  claim; `{"result": false}` retained exhaustive classification; an arbitrary
  caller checker lambda self-approved a certificate; worker-selected goal text
  and unbound compute output could reach the truth path.
- **Reproduction command or test:** red tests
  `test_unsigned_self_reported_computation_cannot_promote_claim`,
  `test_attestation_does_not_substitute_for_artifact_semantics`,
  `test_false_computation_output_cannot_claim_exhaustive_success`,
  `test_caller_supplied_certificate_checker_cannot_self_approve`, and
  orchestrator forged/unbound-computation tests.
- **Root cause:** shape/authentication of a caller assertion was confused with
  semantic verification; the service and router did not independently derive
  claim/artifact/checker/environment bindings.
- **Impact:** a malicious or buggy worker could convert false or irrelevant
  output into `SUPPORTED`, contaminate dependents/memory, and reach release.
- **Whether existing tests detected it:** no. Existing tests constructed the
  trusted metadata and a success lambda themselves.
- **Fix performed:** evidence HMAC with exact claim hashes, artifacts,
  provenance, replay, trust assumptions, and certificate bindings; current
  graph claim-hash verification; literal-true and immutable finite-coverage
  checks; immutable compute specs/artifacts; trusted checker deployment registry
  with implementation identity and durable checked-state attestation; server-
  side reconstruction of compute evidence from the service artifact and
  measured independent replay; generic worker evidence remains quarantined.
- **Regression test added:** adversarial truth tests above; 58 compute-security
  cases plus nine legacy compute tests; orchestrator tests for goal substitution,
  unbound/false/forged computation and replay propagation.
- **Post-fix verification:** compute/security suite passed 67 tests; dependent
  truth/orchestrator cases passed; original forged and false-result
  reproductions no longer support the goal.
- **Residual limitation:** local exactness proves execution/coverage under the
  submitted finite specification. A complete automated proof that arbitrary
  submitted program semantics and coverage exactly represent every natural-
  language claim is not implemented; intent and correspondence boundaries must
  continue to block generalization.
- **Confidence:** high for tested artifact/binding attacks; medium for broad
  mathematical semantic correspondence.

### FBL-004 — Lean, equivalence, correspondence, and T4/T5 were caller-manufacturable

- **Finding ID:** FBL-004.
- **Severity:** CRITICAL.
- **Affected F-REQ IDs:** F-REQ-003, F-REQ-009, F-REQ-013,
  F-REQ-019, F-REQ-048, F-REQ-064, F-REQ-090 through F-REQ-105,
  F-REQ-110, F-REQ-129, F-REQ-131, F-REQ-151, F-REQ-161,
  F-REQ-171, F-REQ-185, F-REQ-186, F-REQ-203.
- **Specification source:** §9.1 lines 1234-1247; §9.2 lines
  1249-1311; §9.3 lines 1313-1349; §9.6 lines 1415-1417; §11.3
  lines 1733-1758; §13.6 lines 2071-2072.
- **Files and line ranges:** `egmra/lean/service.py:39-868`;
  `egmra/lean/correspondence.py:14-120`;
  `egmra/truth/validators.py:210-371`;
  `egmra/truth/router.py:138-208`; `egmra/verification/standards.py:38-82`.
- **Symbols:** `AttestedKernelRunner`, `CheckerAttestation`,
  `FormalCertificate`, `verify_formal_certificate`,
  `LeanService.verify_declaration`, `LeanService.compare_statements`,
  `sign_formal_correspondence_certificate`, `validate_lean_proof`,
  `truth_level`.
- **Expected behavior:** only a clean pinned local kernel run over the exact
  source/type/environment/import/axiom closure, plus approved intent and exact
  authenticated correspondence, can produce T4/T5/formal support; untrusted
  Lean requires quarantine and an independent checker; equivalence requires an
  exact checked biconditional/both implications.
- **Observed behavior (pre-fix):** `kernel_result=True`, lambdas, status strings,
  arbitrary `verification_method`, caller-constructed all-true
  `FormalCertificate`, unrelated proof text/certificate, raw reviewer names,
  and `hardened=True` could manufacture kernel/equivalence/F2/T5 state. Signed
  Lean booleans with a correspondence ID promoted truth without a proof
  envelope. L0 accepted one target and unexecuted probes; L2 skipped the direct
  target; frozen coverage weights could change; L4 allowed ambiguous grounding.
- **Reproduction command or test:** initial adversarial Lean/release run
  produced nine failures; focused forged-certificate/equivalence red run
  produced two failures; `test_signed_lean_booleans_with_real_correspondence_but_no_envelope_cannot_promote`
  promoted pre-fix; L0/L2/RFC/L4 red run produced four failures.
- **Root cause:** structural records and caller statuses were treated as verifier
  authority; certificates did not authenticate every binding; correspondence
  was detached from exact relation/proof hashes and independent review.
- **Impact:** arbitrary text or a compromised worker could claim formal proof,
  elevate truth, or release an unrelated theorem under a trusted label.
- **Whether existing tests detected it:** no. They supplied success lambdas,
  booleans, strings, and dummy archives as the expected proof evidence.
- **Fix performed:** pinned-executable `AttestedKernelRunner` with closed JSON
  protocol, executable hash, scrubbed environment, timeout, complete response
  schema and HMAC; authenticated certificate envelope binding exact source,
  environment, type, declaration, claim and artifact hashes; exact relation and
  proof-term binding for equivalence; router derives all expectations from the
  live graph/certificates; signed correspondence requires every named reviewer
  disclosure, no conflicts, and independence from formalizer/governor; caller
  booleans ignored; L0 requires 2-3 probed targets, L2 direct-first, frozen
  weight hash, and exactly one L4 grounding.
- **Regression test added:** 39 adversarial Lean/release tests plus
  `test_formal_correspondence_security.py`, truth formal-envelope tests, and
  formal-path orchestrator tests.
- **Post-fix verification:** focused Lean/release/truth/communication suite
  passed 132 tests; formal correspondence security tests are present; original
  caller-status, unrelated-proof, missing-envelope, and disclosure bypasses fail.
- **Residual limitation:** `lean` and `lake` are only Elan shims with no default
  toolchain; no real Lean/Mathlib clean build, import closure, proof kernel, or
  independent checker binary was exercised. Positive tests simulate the closed
  checker protocol. SearchPremises/tryActions, Aristotle quarantine, readable
  proof archive, and full formal farm remain partial or unimplemented.
- **Confidence:** high for local binding/authentication failure behavior; low
  for live formal correctness/readiness.

### FBL-005 — Host execution was called a sandbox and fallback was unsafe

- **Finding ID:** FBL-005.
- **Severity:** CRITICAL.
- **Affected F-REQ IDs:** F-REQ-010, F-REQ-023, F-REQ-024,
  F-REQ-062, F-REQ-063, F-REQ-105, F-REQ-160, F-REQ-168,
  F-REQ-184, F-REQ-194, F-REQ-203.
- **Specification source:** §6.8 lines 733-765; §9.6 lines 1415-1417;
  §13.3 line 2028; §13.4 line 2041; §13.6 line 2070; §14.1 line
  2104; §15 lines 2217-2238.
- **Files and line ranges:** `egmra/compute/sandbox.py:178-852`;
  `egmra/compute/spec.py:1-191`; `egmra/compute/service.py:99-711`.
- **Symbols:** `_validate_code`, `_validate_restricted_policy`,
  `RestrictedPythonExecutor.run`, `_wait_with_limits`, `ContainerSandbox.run`,
  `ComputeService.submit_experiment`, `ComputeService.replay`.
- **Expected behavior:** hostile jobs cannot read host files/secrets, traverse
  paths, spawn processes/shells, use network, escape via serialization, or evade
  CPU/RAM/PID/output/wall limits; unsupported isolation fails closed; exact
  artifacts persist and replay in an independent container.
- **Observed behavior (pre-fix):** a submitted job read `/etc/passwd` and used
  `_socket`; the wrapper executed unrestricted host Python while named sandbox;
  `ContainerSandbox.run()` was an always-raising placeholder; caller labels
  forged independence; jobs/artifacts/check results disappeared on restart;
  resource/schema/serialization controls were incomplete.
- **Reproduction command or test:** direct pre-fix file/socket probes; initial
  adversarial batch was 27 failed/1 passed; dedicated tests in
  `test_adversarial_compute_security.py` exercise file, import, process,
  environment, schema, timeout, CPU, memory, output, persistence, symlink,
  root-swap, replay identity, checker and OCI paths.
- **Root cause:** monkeypatches and a subprocess wrapper were mistaken for an OS
  security boundary; container/persistence/resource promises were not
  implemented as enforceable production behavior.
- **Impact:** arbitrary code execution with repository-user privileges,
  credential/source disclosure, host modification, denial of service, and
  forged reproducibility evidence.
- **Whether existing tests detected it:** no. They ran cooperative code and
  reused the same backend under a different label.
- **Fix performed:** an explicitly labeled capability-free restricted Python
  subset with AST allowlist, scrubbed child environment, closed descriptors,
  separate globals and no imports/attributes/private names; strict exact
  arithmetic and JSON/schema rules; bounded CPU/RAM/PIDs/output/log/wall time
  with process-group cleanup; content-addressed atomic mode-0600 persistence
  with hashes, fsync, symlink/root/corruption checks and restart replay; measured
  environment identity; a real Docker/Podman command path using immutable local
  image ID, no network, read-only root, nonroot UID, dropped capabilities,
  `no-new-privileges`, bounded cgroups/tmpfs/mounts and no host fallback.
- **Regression test added:** 58 adversarial compute/security cases plus nine
  legacy compute tests.
- **Post-fix verification:** 67 focused tests passed; Docker server 29.5.3 and
  local `postgres:17-alpine` exercised the real runc negative/entrypoint path;
  all host-capability probes are `policy_violation`; unavailable OCI produces a
  typed failure without fallback.
- **Residual limitation:** the restricted executor is defense in depth, not a
  kernel sandbox. No compatible pinned Python/Sage image was locally available,
  so a successful independent-container computation is `BLOCKED-EXTERNAL`.
  Sage/CAS/SAT/SMT/ILP/graph container backends remain incomplete. macOS memory
  monitoring is weaker than cgroups, and a hostile local filesystem writer
  remains outside the local M1 threat boundary.
- **Confidence:** high for tested fail-closed paths; low for successful
  compatible OCI/full backend behavior.

### FBL-006 — Release gates trusted caller/stale state and signing/rendering was bypassable

- **Finding ID:** FBL-006.
- **Severity:** CRITICAL.
- **Affected F-REQ IDs:** F-REQ-002, F-REQ-003, F-REQ-013,
  F-REQ-014, F-REQ-033, F-REQ-050, F-REQ-051, F-REQ-110,
  F-REQ-129 through F-REQ-134, F-REQ-163, F-REQ-188, F-REQ-203.
- **Specification source:** §11.3 lines 1733-1758; §11.4 lines
  1759-1769; §11.5 lines 1771-1823; §13.3 line 2031; §13.6 line
  2074.
- **Files and line ranges:** `egmra/release/gates.py:46-438`;
  `egmra/release/policy.py:27-224`; `egmra/release/certificate.py:24-328`;
  `egmra/comms/render.py:1-56`; `egmra/orchestrator/loop.py:993-1104`.
- **Symbols:** `run_five_gates`, `FiveGateResult.verify_attestation`,
  `PromotionPolicy.authorize`, `PromotionDecision.verify_authorization`,
  `ReleaseCertificate.sign`, `verify`, `render`, `ResearchResult.render`.
- **Expected behavior:** every release entry point consumes authoritative fresh
  state and independently enforces all mandatory truth/intent/correspondence/
  novelty/significance/reproducibility predicates; no cached, forged, partial,
  disabled, disagreeing, or stale gate can sign or render a positive result.
- **Observed behavior (pre-fix):** gates accepted raw caller
  `EvidenceProfile`/booleans; release used a fallback key, could sign before
  promotion, and was not bound to an event head; claim/interpretation/I2/F2
  substitution and direct/human render bypasses existed; unresolved axes could
  render verified-sounding text; a later event did not necessarily invalidate
  cached approval.
- **Reproduction command or test:** red raw-profile, sign-before-promotion,
  unsigned/direct render, stale timestamp, claim/interpretation substitution,
  mutated gate/certificate, stale-event and unresolved-axis tests in
  `test_adversarial_lean_release.py`; baseline `fx-true-square` released despite
  `contract.release_blocked` and intent I0.
- **Root cause:** descriptive gate/profile records were accepted as authorities
  rather than a single authenticated subject- and state-bound authorization
  chain.
- **Impact:** a false, wrong-target, stale, or only partly verified result could
  be published as solved/verified despite a mandatory gate failure.
- **Whether existing tests detected it:** no. Tests built high-tier profiles
  and success fields directly and did not enumerate alternate render paths.
- **Fix performed:** gates require replay-derived signed `TruthSnapshot` and
  current `EventLog`; bind exact claim/hash/version/evidence/run/head/Merkle plus
  source/interpretation/intent/correspondence/type; distinct strong gate,
  promotion and release keys; signed short-lived subject/policy-bound promotion
  authorization; sign only after authorization; every verify/render rechecks
  mandatory fields, HMAC, freshness and current event head; explicit release
  thresholds and honest-no-result language; final orchestrator recheck clears a
  certificate if truth/head changed.
- **Regression test added:** 30+ release/adversarial cases covering alternate
  entries, stale/malformed/forged metadata, disabled/cached gates, disagreements,
  substitution, mutation, partial failure and direct calls.
- **Post-fix verification:** 132-test focused Lean/release/truth/comms suite and
  71-test orchestrator/CLI suite passed; a new event immediately invalidates
  gate authorization, release verification, and rendering.
- **Residual limitation:** the pre-existing legacy publisher is now retired
  fail-closed rather than integrated with the EGMRA graph/referee/certificate.
  No legacy migration bridge or API/web/publication service exists to inventory.
  Local keys are separate values but may coexist in one trusted process.
- **Confidence:** high for tested EGMRA release paths; medium for repository-wide
  publication-path exhaustiveness.

### FBL-007 — Orchestrator ignored decisive components and fabricated authority

- **Finding ID:** FBL-007.
- **Severity:** CRITICAL.
- **Affected F-REQ IDs:** F-REQ-004 through F-REQ-012,
  F-REQ-034, F-REQ-044 through F-REQ-052, F-REQ-055, F-REQ-064,
  F-REQ-077, F-REQ-117 through F-REQ-122, F-REQ-163, F-REQ-165,
  F-REQ-173, F-REQ-193, F-REQ-203.
- **Specification source:** §5 lines 386-464; §7.9 lines 989-1055;
  §10.4 lines 1654-1680; §11.1 lines 1703-1716; §13.3 lines
  2025-2034; §14.1 lines 2093-2108.
- **Files and line ranges:** `egmra/orchestrator/loop.py:79-1305`;
  `egmra/cli.py:36-114,126-239`; `egmra/intake/review.py:20-114`;
  `egmra/tests/test_adversarial_orchestrator.py:139-757`.
- **Symbols:** `research`, `BudgetLedger`, `DeterministicWorker`,
  `MechanicalAttackEvaluator`, `_authenticate_computation_proposal`,
  `_build_blueprint`, `sign_intent_certificate`, `cmd_run`.
- **Expected behavior:** production entry points execute one connected,
  evidence-driven loop in which intake, state, selection, search, leases,
  workers, artifacts, verification, gates, learning and rendering consume one
  another's authenticated outputs; missing/failing stages block release.
- **Observed behavior (pre-fix):** selection was effectively unconditional;
  runner/search/controller/blueprint/leases/blackboard/Lean/OEIS/learning were
  absent or ignored; the loop trusted worker goal/evidence, fabricated ten
  referee passes from one Boolean, self-issued I2, omitted source bytes/status
  from replay, and could sign a release that contradicted intake state. Four
  “end-to-end” tests used a deterministic worker, one dummy theorem, local
  predicate, hardcoded metadata, and promotion disabled.
- **Reproduction command or test:** baseline five-fixture CLI run exposed two
  contradictions; adversarial production tests for budget, malformed input,
  stale fence, forged computation, sequence/OEIS, formal path, self-intent,
  replay, release freshness, ambiguity and referee failures were written red.
- **Root cause:** interfaces/classes were counted as integration; the central
  function synthesized or bypassed outputs rather than consuming those
  components under trust-boundary contracts.
- **Impact:** the apparent M1 slice could report complete/released results
  without the claimed scientific/control/security loop, while large portions of
  the architecture remained unreachable.
- **Whether existing tests detected it:** no. They tested fixture plumbing and
  local objects, often with the critical success fact injected.
- **Fix performed:** real 5% cold budget and runner call; frozen packet;
  `ProblemSelector`; mechanism-distinct programs/fingerprints/QD archive;
  direct-first AND/OR blueprint; controller/global spend/verified debt;
  branches, local fenced leases, signed authority tokens and immutable
  blackboard; server-authenticated compute/replay evidence; heuristic-only OEIS;
  formal envelope through router; exact source/status event replay; independent
  signed intent input; concrete pessimistic attack evaluator; truth snapshot,
  gates, authenticated memory, promotion/certificate and immediate final
  freshness recheck. CLI now requires a signed intent review for a verified
  fixture and returns nonzero on expectation mismatch.
- **Regression test added:** 17 production-path tests in
  `test_adversarial_orchestrator.py`, two intent-review security tests, and
  strengthened CLI/intake/orchestrator/eval tests.
- **Post-fix verification:** focused command over intake, intent, orchestrator,
  adversarial orchestrator, CLI and eval passed 71 tests in 6.83s; compileall
  passed. Exact compute and formal envelopes demonstrably reach truth/gates
  without allowing mock/static success to promote.
- **Residual limitation:** this is still a bundled-fixture CLI slice, not the
  legacy Erdős scheduler or a service deployment. Checkpoint/resume is not
  integrated per iteration; default leases/memory are local; learning does not
  durably change a later run; execution is serial; fresh multi-source status and
  full source URL/commit/license may be absent; all live external integrations
  are unavailable/unexercised.
- **Confidence:** high that the listed local objects are now consumed; low that
  the complete production architecture is implemented.

### FBL-008 — Agent authorities were prompt text and the blackboard leaked mutable state

- **Finding ID:** FBL-008.
- **Severity:** HIGH.
- **Affected F-REQ IDs:** F-REQ-011, F-REQ-027, F-REQ-035,
  F-REQ-044, F-REQ-060, F-REQ-122, F-REQ-163, F-REQ-177,
  F-REQ-202, F-REQ-203.
- **Specification source:** §4.3 lines 355-367; §5.1 lines 402-444;
  §6.5 lines 627-712; §11.1 lines 1703-1716; §14.6 lines
  2190-2215.
- **Files and line ranges:** `egmra/agents/authorities.py:22-257`;
  `egmra/truth/blackboard.py:16-177`;
  `egmra/orchestrator/loop.py:621-957`.
- **Symbols:** `AUTHORITY_PERMISSIONS`, `AuthorityToken`,
  `AuthorityTokenIssuer.issue/verify/require_independent`,
  `Blackboard.read_slice`, `Blackboard.write_proposal`.
- **Expected behavior:** authenticated least-privilege actions, scoped data,
  separation of duties, no self-approval/confused deputy/cross-agent forgery,
  immutable input packets, and truth/release status writable only by the proper
  authority.
- **Observed behavior (pre-fix):** authorities were role records/prompts and
  forbidden-action tuples with no enforcement in the orchestrator; blackboard
  state was mutable and broadly visible; caller labels could imply reviewer
  independence; direct tool/action calls were not capability checked.
- **Reproduction command or test:** adversarial tests attempt unauthenticated
  access, scope tampering/expiry, cross-branch access, packet substitution,
  forbidden proposal kinds, release permission by a worker, and self-approval.
- **Root cause:** descriptive policy was mistaken for an authorization boundary.
- **Impact:** privilege escalation, information leakage, proposal forgery,
  confused-deputy use of privileged components, and self-approved release.
- **Whether existing tests detected it:** no. They asserted role constants and
  prompt strings, not production enforcement.
- **Fix performed:** strong authority key; short-lived HMAC capability token
  bound to authority, permission, resource, branch, packet and lineage; exact
  permission map; expiry/tamper/scope/independence enforcement; deeply immutable
  dependency-cone slices; packet-content-hash check; authority-specific proposal
  kind allowlists; own-proposal visibility; orchestrator uses lease fence and
  tokens around worker proposals.
- **Regression test added:** four direct adversarial authority tests plus stale
  fence/forged worker/cross-boundary orchestrator tests.
- **Post-fix verification:** combined authorities/agents/truth batch passed 32
  tests; stale and overprivileged output is rejected before evidence admission.
- **Residual limitation:** HMAC capability issuance is local-process security,
  not mTLS/service identity or hardware-isolated keys. Several trust keys can be
  present in the same trusted host process, and a real malicious/unavailable
  model-provider campaign was not executed.
- **Confidence:** high for tested local privilege boundaries; medium for a
  deployed multi-service threat model.

### FBL-009 — Search utility, budget, posterior, fingerprint, debt, and reachability defects

- **Finding ID:** FBL-009.
- **Severity:** HIGH.
- **Affected F-REQ IDs:** F-REQ-007, F-REQ-008, F-REQ-018,
  F-REQ-028, F-REQ-044 through F-REQ-049, F-REQ-061, F-REQ-067
  through F-REQ-078, F-REQ-162, F-REQ-170, F-REQ-199, F-REQ-203.
- **Specification source:** §7.1 lines 796-829; §7.2 lines 831-848;
  §7.3 lines 850-871; §7.4 lines 873-899; §7.9 lines 989-1055;
  §13.3 line 2029; §13.4 line 2043; §14.4 lines 2154-2170.
- **Files and line ranges:** `egmra/search/controller.py:20-267`;
  `egmra/search/mechanism.py:1-99`; `egmra/search/verified_debt.py:1-110`;
  `egmra/search/blueprint.py:1-102`; `egmra/orchestrator/loop.py:531-957`.
- **Symbols:** `branch_action_utility`, `Controller`, `BranchPosterior`,
  `MechanismFingerprint`, `verified_debt`, `delta_verified_debt`, `Blueprint`.
- **Expected behavior:** finite additive utility; protected exploration;
  posterior updates that distinguish censoring from mathematical failure;
  actual per-branch/global budget enforcement; fingerprints consumed by a QD
  archive; frozen non-gameable target-relative debt; typed acyclic AND/OR
  search; persistent state influences work and future decisions.
- **Observed behavior (pre-fix):** actual spend was not correctly charged;
  branches could overspend globally; negative/unknown/NaN inputs were accepted;
  rate limits polluted mathematical posterior; protected exploration could
  starve; fingerprints omitted expected falsifiers and were not consumed;
  negative/disappearing obligations gamed debt; cycles recursed; all helpers
  were disconnected from `research()`.
- **Reproduction command or test:** nine independent tests in
  `test_adversarial_search.py`, including a hand-recomputed additive value,
  global spend, censoring, protected lane, fingerprint, debt and cycle attacks;
  orchestrator runner/budget test proves production consumption.
- **Root cause:** local formulas and registries were implemented without closed
  numerical/state invariants or a production caller.
- **Impact:** unbounded or misallocated compute, false learning from outages,
  search starvation, duplicate/correlated branch credit, fake progress and
  possible recursion denial of service.
- **Whether existing tests detected it:** no. They used toy values and called
  helpers directly, without global budget/restart/production effects.
- **Fix performed:** validate finite inputs/weights/posteriors; true per-branch
  and global spend; reject negative/unknown allocations and duplicates; additive
  utility with posterior sample confined to outcome term; rate-limit censoring;
  protected-lane selection; bind falsifiers into fingerprint; immutable/frozen
  debt inventory with disappearance/negative rejection; cycle detection; wire
  selector/programs/fingerprints/QD/blueprint/controller/debt into research.
- **Regression test added:** `test_adversarial_search.py` plus orchestrator
  production-path state assertions.
- **Post-fix verification:** 32 combined search tests passed; representative
  expected values are independently calculated.
- **Residual limitation:** controller/archive/blueprint state is not durably
  checkpointed/restarted in `research`; there is no real AO*/PUCT/MCTS/
  MAP-Elites/Lean proof-state executor or large concurrent branch competition;
  closed-loop learned priors are not demonstrated.
- **Confidence:** high for local arithmetic/invariants; low-to-medium for the
  specified full search architecture.

### FBL-010 — Retrieval packets/provenance were mutable and lexical matching was called applicability

- **Finding ID:** FBL-010.
- **Severity:** HIGH.
- **Affected F-REQ IDs:** F-REQ-005, F-REQ-030, F-REQ-040
  through F-REQ-042, F-REQ-056 through F-REQ-059, F-REQ-087
  through F-REQ-089, F-REQ-120, F-REQ-159, F-REQ-169, F-REQ-203.
- **Specification source:** §6.2-§6.4 lines 519-625; §8.4 lines
  1167-1197; §8.5 lines 1199-1222; §13.3 line 2027; §13.4 line
  2042; §15 lines 2217-2238.
- **Files and line ranges:** `egmra/retrieval/records.py:1-100`;
  `egmra/retrieval/packet.py:25-215`;
  `egmra/retrieval/service.py:23-161`;
  `egmra/orchestrator/loop.py:489-529`.
- **Symbols:** `TheoremRecord`, `LiteratureQuery`, `SourcePacket`,
  `QueryEvent`, `RetrievalService.build_packet`, `ImportAuditor.audit`,
  `NoveltyQueryLog`.
- **Expected behavior:** immutable complete packet/query provenance across
  bibliographic/mathematical/formal/experimental indexes; separate retrieval
  ranking from truth and source/import auditing; malformed/stale/offline/
  injected data cannot become verified mathematical evidence.
- **Observed behavior (pre-fix):** packet/nested fields were mutable; packet hash
  omitted query events, coverage, negatives/gaps, conflicts, snapshot/corpus and
  re-entry metadata; duplicate IDs/invalid limits passed; source hashes were not
  required; a token-subset “logical consequence” audit erased negation; CLI used
  one dummy local theorem and never executed formal applicability or live
  multi-index retrieval.
- **Reproduction command or test:** five tests in
  `test_adversarial_retrieval.py` mutate every material packet field, nested
  collections and full query contract; try duplicate IDs/limits/nonhash source;
  and show negation cannot be erased.
- **Root cause:** content identity covered a display subset and lexical
  convenience ranking was presented as semantic/source verification.
- **Impact:** cache/provenance substitution, retrieved-source prompt injection,
  use of inapplicable/negated theorems, false novelty/status, and irreproducible
  solver/referee packets.
- **Whether existing tests detected it:** no; one assertion was conditional
  (`... if usable else True`) and live/stale/malformed/injection paths were not run.
- **Fix performed:** frozen/deeply immutable packets/records; packet hash binds
  full query/events/results/coverage/negatives/conflicts/snapshot/corpus/
  predecessor/re-entry; strict limits/duplicate IDs; query hash binds the full
  contract; SHA-256 source audit; exact normalized consequence with negation
  preserved; orchestrator freezes the cold-pass packet before deep work.
- **Regression test added:** `test_adversarial_retrieval.py` and packet-use
  assertions in adversarial orchestrator tests.
- **Post-fix verification:** 16 combined retrieval tests passed; changing any
  tested provenance field changes identity and malformed provenance fails closed.
- **Residual limitation:** only a local lexical index is exercised. No live four-
  index citation/theorem/formal/experimental service, cache freshness/retry/
  cancellation/schema drift, adversarial prompt-injection corpus campaign, or
  real Lean elaboration of retrieved premises ran. `compiled_in_context` remains
  a service assertion unless a real formal checker supplies it.
- **Confidence:** high for local immutability/identity; low for live retrieval
  correctness and injection resistance.

### FBL-011 — OEIS cache, typing, and match semantics could fabricate support

- **Finding ID:** FBL-011.
- **Severity:** HIGH.
- **Affected F-REQ IDs:** F-REQ-055, F-REQ-081 through F-REQ-086,
  F-REQ-159, F-REQ-169, F-REQ-189, F-REQ-203.
- **Specification source:** §8.2 lines 1082-1085; §8.3 lines
  1087-1165; §13.3 line 2027; §13.4 line 2042; §13.6 line 2075.
- **Files and line ranges:** `egmra/oeis/client.py:25-225`;
  `egmra/oeis/transforms.py:20-308`; `egmra/oeis/matching.py:1-177`;
  `egmra/orchestrator/loop.py:621-957`.
- **Symbols:** `OEISClient._load_cache/_store_cache/_query`,
  `apply_transform`, `TransformStep`, `verify_held_out`,
  `conjecture_from_match`.
- **Expected behavior:** exact typed transforms with explicit domains and
  provenance; immutable hash-verified query-bound cache; read-only throttled
  HTTP with strict schema; honest offline/malformed handling; held-out checks
  use actual data; no match or match is only heuristic and never proof/novelty.
- **Observed behavior (pre-fix):** integer transforms accepted floats/bools;
  missing parameters and mutable transform steps were underchecked; empty
  held-out data could pass and reported count was caller supplied; a no-match
  path could report T1; corrupted cache was trusted; malformed HTTP JSON could
  silently become empty results; query values were insufficiently validated;
  the orchestrator never called OEIS.
- **Reproduction command or test:** seven tests in
  `test_adversarial_oeis.py` cover typing, missing params, empty held-out,
  no-match T0, impossible prefix metadata, corrupted cache, malformed JSON and
  query injection; orchestrator sequence test covers reachable heuristic use.
- **Root cause:** local transform utilities, cache files and caller metadata
  were treated as trusted integration results; missing/error cases were
  optimistically normalized.
- **Impact:** incorrect sequence transformations, cache poisoning, false
  numerical support/novelty, and external query manipulation.
- **Whether existing tests detected it:** no. They used a fake fetcher and toy
  positives and directly asserted a T1 descriptor.
- **Fix performed:** exact integer-only validation; typed transform errors and
  immutable step params; held-out nonempty/actual count and prefix metadata
  validation; no match/no held-out stays T0; strict duplicate-key JSON/schema;
  A-number/query validation and URL encoding; immutable response; cache stores
  exact response text plus content/query hash, rejects symlinks/corruption, and
  writes atomically mode 0600; thread-safe throttle/read-only policy; production
  sequence proposals may query an injected client but remain non-evidence.
- **Regression test added:** `test_adversarial_oeis.py` and
  `test_generated_sequence_reaches_read_only_oeis_without_becoming_truth`.
- **Post-fix verification:** 21 combined OEIS tests passed; corrupted/malformed/
  empty/no-match cases fail closed or remain T0.
- **Residual limitation:** live OEIS HTTP, real rate limiting, cancellation,
  schema drift and recovery were not exercised. The loop does not independently
  recompute every live candidate field, and full transform inverse/large-value
  coverage is not exhaustive.
- **Confidence:** high for local tested behavior; low for live integration.

### FBL-012 — Reviewer labels and booleans could manufacture verification

- **Finding ID:** FBL-012.
- **Severity:** HIGH.
- **Affected F-REQ IDs:** F-REQ-011, F-REQ-020, F-REQ-032,
  F-REQ-050, F-REQ-064, F-REQ-122 through F-REQ-132, F-REQ-163,
  F-REQ-177, F-REQ-188, F-REQ-216.
- **Specification source:** §11.1 lines 1703-1716; §11.2 lines
  1718-1731; §11.3 lines 1733-1758; §11.4 lines 1759-1769;
  §13.6 lines 2063 and 2074; §15 line 2248.
- **Files and line ranges:** `egmra/verification/attacks.py:1-83`;
  `egmra/verification/referee.py:1-107`;
  `egmra/verification/standards.py:38-82`;
  `egmra/verification/aggregation.py:16-95`;
  `egmra/orchestrator/loop.py:119-205,965-990`.
- **Symbols:** `AttackResult`, `AttackReport`, `AdversarialReferee`,
  `truth_level`, `ReviewVerdict`, `aggregate`, `MechanicalAttackEvaluator`.
- **Expected behavior:** T0-T5 and I/F/N/S/R follow exact predicates; higher
  tiers add real checks; unknown/correlated/forged reviewer results cannot
  promote; one valid central defect blocks; organizational independence and
  attack results influence truth/release state pessimistically.
- **Observed behavior (pre-fix):** caller `hardened=True` promoted kernel result
  to T5; unknown/correlated reviews could produce optimistic aggregation;
  reviewer duplicates and internally contradictory attack results were
  accepted; referee residual uncertainty/nonindependence did not reliably
  block; orchestrator fabricated ten all-pass attacks from one Boolean and
  hardcoded diversity labels.
- **Reproduction command or test:** six tests in
  `test_adversarial_verification.py`; release caller-hardening test; orchestrator
  independent-defect and missing-attack tests.
- **Root cause:** result containers and identity labels were trusted rather than
  derived from authenticated tools/authorities, and pessimistic invariants were
  incomplete.
- **Impact:** false-positive truth/release, consensus masquerading as proof,
  suppressed dissent and self-review.
- **Whether existing tests detected it:** no. Existing cases directly
  constructed pass verdicts, lineages and high tiers.
- **Fix performed:** T5 only from independent-checker method, never caller
  `hardened`; validate verdict vocabulary and attack consistency; reject
  duplicate reviewers/attacks; unknown/correlated all-pass cannot promote;
  frozen reports; residual/nonindependence blocks release; no attacks after
  finalization; default evaluator runs concrete checks, and missing required
  attacks fail closed.
- **Regression test added:** `test_adversarial_verification.py`, hardening tests
  in `test_adversarial_lean_release.py`, and referee production tests.
- **Post-fix verification:** 19 combined verification tests and the 71-test
  orchestrator batch passed; forged/unknown/correlated/missing attacks block.
- **Residual limitation:** the default evaluator is local mechanical code, not
  an organizationally independent model/tool/human service. `DiversityProfile`
  still represents measured paths as data; full independence requires attested
  provider/tool identities and isolated contexts. No false-positive/false-
  negative campaign against real mathematical reviews was run.
- **Confidence:** high for local aggregation failure behavior; low-to-medium for
  real independent-referee efficacy.

### FBL-013 — Truthy records could contaminate cross-problem learning

- **Finding ID:** FBL-013.
- **Severity:** HIGH.
- **Affected F-REQ IDs:** F-REQ-012, F-REQ-020, F-REQ-052,
  F-REQ-065, F-REQ-121, F-REQ-140 through F-REQ-147, F-REQ-172,
  F-REQ-203, F-REQ-204.
- **Specification source:** §6.11 lines 775-786; §10.6 lines
  1691-1701; §12.3-§12.6 lines 1872-1987; §13.4 line 2045; §15
  lines 2217-2238.
- **Files and line ranges:** `egmra/learning/memory.py:27-151`;
  `egmra/learning/calibration.py:1-108`;
  `egmra/orchestrator/loop.py:1027-1041`.
- **Symbols:** `MemoryStore`, `LongTermMemory.promote_verified_fact`,
  `promote_external_import`, `record_negative`, calibration record/ledger.
- **Expected behavior:** persistent cross-problem semantic learning only from
  authenticated current-toolchain replay and current truth/gates; separate
  memory kinds; invalidation/revalidation on environment/source changes; later
  behavior changes only because an applicable verified record exists.
- **Observed behavior (pre-fix):** a truthy dictionary with expected field names
  could enter verified semantic memory; public store admission exposed bypass;
  calibration shapes/probabilities/bins were insufficiently validated; stores
  were in memory and disconnected from selection/orchestration.
- **Reproduction command or test:** `test_truthy_dicts_alone_cannot_promote_persistent_semantic_memory`
  and invalid calibration tests in `test_adversarial_learning.py`.
- **Root cause:** field presence/truthiness was confused with authenticated truth
  and replay; memory type names were treated as enforcement.
- **Impact:** false or stale facts could bias later research and recursively
  amplify into truth/release decisions.
- **Whether existing tests detected it:** no; a legacy test explicitly expected
  a truthy record to be admitted.
- **Fix performed:** public direct semantic admission rejects; promotion requires
  a fresh current `TruthSnapshot`, exact claim/hash, current event log, signed
  fresh gates bound to that snapshot, truth T2+, I2 and R2; records retain
  snapshot/gate digests; strict calibration validation; orchestrator quarantines
  speculative outputs locally and invokes authenticated semantic promotion only
  after release gates.
- **Regression test added:** `test_adversarial_learning.py` and
  `test_cold_and_branch_learning_is_quarantined_problem_local`; legacy positive
  expectation corrected to reject unauthenticated data.
- **Post-fix verification:** 15 combined learning tests and the production-path
  learning assertions passed.
- **Residual limitation:** stores are process-local and have no durable event-
  sourced revocation/applicability index. No second run was demonstrated to
  change selection/program priors from a verified record, so the specified
  closed learning loop remains partial.
- **Confidence:** high for blocking the original contamination; low for complete
  durable learning behavior.

### FBL-014 — M2 and external integrations were facades; local object storage was unsafe

- **Finding ID:** FBL-014.
- **Severity:** HIGH.
- **Affected F-REQ IDs:** F-REQ-010, F-REQ-019, F-REQ-040,
  F-REQ-056, F-REQ-064, F-REQ-066, F-REQ-098, F-REQ-104,
  F-REQ-105, F-REQ-167 through F-REQ-173, F-REQ-184 through
  F-REQ-186, F-REQ-193, F-REQ-194, F-REQ-200, F-REQ-203.
- **Specification source:** §13.4 lines 2038-2046; §13.6 lines
  2070-2072; §14.1 lines 2093-2108; §14.5 lines 2172-2188; §15
  lines 2217-2238.
- **Files and line ranges:** `egmra/m2.py:26-231`;
  `egmra/compute/sandbox.py:715-852`; `egmra/lean/service.py:248-868`;
  `egmra/agents/runner.py:27-91`; `egmra/oeis/client.py:63-225`;
  `egmra/lean/aristotle_routing.py:1-95`.
- **Symbols:** `PostgresEventStore`, `ContentAddressedObjectStore`,
  `M2Assembly`, `ContainerSandbox`, `AttestedRunner`, `OEISClient`,
  Aristotle request/routing records.
- **Expected behavior:** real typed, reachable, configured and recoverable
  integrations for PostgreSQL, content-addressed object storage, OCI math
  backends, Lean/Lake/Mathlib, model providers, Aristotle, OEIS, citation/
  theorem services, with authentication, timeouts, retries, cancellation,
  idempotency, schema drift and observability; interface-only/mock status is not
  completion.
- **Observed behavior (pre-fix):** PostgreSQL and container methods always
  raised while tests counted that as M2; no package/migration/API/service
  runtime existed; model/Lean/OEIS/Aristotle positives used injected callables;
  local object store accepted path-like digests, did not verify content on read,
  followed symlink/prefix substitutions, lacked size/private atomic guarantees,
  and assembly accepted unsafe capacity/host defaults; DSN failures could expose
  credential text or accept malformed configuration.
- **Reproduction command or test:** baseline `test_m2_scale.py` proved only
  expected failure; 13 new red cases in `test_adversarial_m2.py` covered digest
  traversal, corruption, symlink/prefix/root replacement, size/mode/type,
  malformed DSNs, secret redaction and unsafe assembly. Live service probes are
  recorded in baseline/compute/Lean reports.
- **Root cause:** an interface/facade and local substitute were reported as a
  scalable integration, and the substitute lacked adversarial storage/config
  invariants.
- **Impact:** path traversal/data substitution/credential disclosure locally;
  more broadly, false production-readiness claims and unavailable failure/
  recovery behavior.
- **Whether existing tests detected it:** no. They considered “raises” and
  static policy strings successful external coverage.
- **Fix performed:** validate lowercase SHA-256 digests; bounded bytes-only
  objects; root inode identity; reject root/prefix/file symlinks and nonregular
  files; content hash on read; atomic exclusive publication, fsync and mode
  0600/0700; strict Postgres DSN with redacted public form/connect timeout/schema
  init and nonsecret errors; capacity validation; no default host sandbox;
  `m2_ready()` remains honestly false without Postgres+OCI; external adapters
  fail closed when unconfigured rather than silently mocking.
- **Regression test added:** `test_adversarial_m2.py` (14 collected cases by
  parametrization) plus four existing M2 tests.
- **Post-fix verification:** `.venv/bin/python -m pytest -q
  egmra/tests/test_adversarial_m2.py egmra/tests/test_m2_scale.py` returned
  `18 passed in 0.07s`.
- **Residual limitation:** no PostgreSQL server/client or migrations were
  exercised; no successful compatible Python/Sage OCI job; no real Lean,
  provider, Aristotle, OEIS HTTP, theorem/citation source or service recovery.
  The object store is local filesystem M1/M2 scaffolding, not cloud object-store
  readiness. These items are `BLOCKED-EXTERNAL`, `PARTIAL`, or `UNREACHABLE`,
  never verified by interface tests.
- **Confidence:** high for the local object/DSN reproductions; low for all live
  external readiness claims.

### FBL-015 — The passing suite and acceptance tests did not prove the claims

- **Finding ID:** FBL-015.
- **Severity:** HIGH.
- **Affected F-REQ IDs:** F-REQ-026, F-REQ-136 through F-REQ-147,
  F-REQ-148, F-REQ-164, F-REQ-174 through F-REQ-192, F-REQ-203,
  F-REQ-207.
- **Specification source:** §12 lines 1825-1987; §13 lines
  1991-2091, especially §13.6 lines 2058-2077; §16 lines 2252-2294.
- **Files and line ranges:** audit-start `egmra/tests/test_acceptance.py:1-235`;
  current `egmra/tests/test_adversarial_truth_security.py:1-627`;
  `egmra/tests/test_adversarial_compute_security.py:1-661`;
  `egmra/tests/test_adversarial_lean_release.py:1-1069`;
  `egmra/tests/test_adversarial_orchestrator.py:1-757`;
  `FABLE_TEST_QUALITY_REPORT.md:1-542`.
- **Symbols:** all 18 `test_acc*` functions and subsystem test helpers.
- **Expected behavior:** tests independently exercise production entry points,
  positive and negative semantics, persistence/restart/revocation/concurrency/
  recovery and real required integrations; every §13.6 criterion is demonstrated
  as written, not by a similarly named helper.
- **Observed behavior (pre-fix):** all 241 EGMRA/420 combined tests passed while
  unsigned policy, event truncation, forged evidence, host-file access, fake
  Lean, gate bypass and disconnected orchestration remained. Tests asserted
  existence/types/constants, supplied trusted booleans/lambdas/labels, used
  conditionals/vacuity, or treated a raising adapter as implemented. All 18
  named acceptance functions passed, but 0/18 demonstrated the complete
  production criterion.
- **Reproduction command or test:** isolated baseline
  `python -m pytest -q -ra` => 420 passed plus 18 subtests; direct adversarial
  probes listed in FBL-001 through FBL-014 succeeded against that same snapshot.
- **Root cause:** the prior author controlled implementation, tests, ledger and
  expected status, and equated local contract coverage with integration/runtime
  evidence.
- **Impact:** severe completion exaggeration and a green suite incapable of
  preventing false promotion/security regressions.
- **Whether existing tests detected it:** by definition no; this finding is the
  demonstrated inadequacy of that suite.
- **Fix performed:** add independent adversarial, corruption, concurrency,
  restart, revocation, freshness, privilege, malformed-input, semantic-binding,
  resource and production-path suites; strengthen formerly permissive fixtures;
  independently calculate expected arithmetic; exercise mutation-style bypasses
  during remediation.
- **Regression test added:** final collection contains 366 net additional cases
  over baseline across adversarial, corruption, concurrency, restart,
  integration, network and strengthened legacy suites; parameterized subtests
  are reported separately.
- **Post-fix verification:** the fresh final full run returned `786 passed, 44
  subtests passed`; the focused adversarial/security selection returned `349
  passed, 25 subtests passed`; no skip, warning, failure or error category was
  reported. Criterion-level gaps remain in the traceability matrix.
- **Residual limitation:** test strengthening cannot verify absent real services,
  full M2, distributed concurrency, external benchmarks or all 18 acceptance
  criteria. Several requirements must remain partial/blocked/unverified.
- **Confidence:** high.

### FBL-016 — CI excluded the EGMRA suite and pytest was undeclared

- **Finding ID:** FBL-016.
- **Severity:** HIGH.
- **Affected F-REQ IDs:** F-REQ-026, F-REQ-148, F-REQ-164,
  F-REQ-174 through F-REQ-191, F-REQ-203, F-REQ-207.
- **Specification source:** §13 lines 1991-2091; §15 lines
  2217-2238; §16 lines 2252-2294.
- **Files and line ranges:** `.github/workflows/test.yml:1-40`;
  `requirements.txt:1-5`; `requirements.lock:1-20`;
  `SETUP_GUIDE.md:1-185`.
- **Symbols:** GitHub Actions test steps and dependency manifests.
- **Expected behavior:** clean documented installation has all test dependencies
  and CI executes legacy, EGMRA, acceptance/security and compilation surfaces on
  supported Python versions.
- **Observed behavior (pre-fix):** workflow ran only
  `unittest discover -s tests`; all 241 EGMRA pytest tests were excluded;
  `pytest` was undeclared, so pointing unittest at `egmra/tests` caused 16 import
  errors before audit-only install and zero collected tests afterward.
- **Reproduction command or test:** isolated baseline commands and exit codes in
  `FABLE_BASELINE_VERIFICATION.md`, including 179 legacy pass, 16 import errors,
  then audit-only 241/420 pytest pass.
- **Root cause:** test framework/dependency and directory selection were not
  integrated into documented CI despite using their count in the completion
  report.
- **Impact:** security/correctness regressions in the claimed architecture could
  merge while advertised tests remained green.
- **Whether existing tests detected it:** no; CI configuration caused the
  exclusion.
- **Fix performed:** declare and lock pytest; add `python -m pytest -q
  egmra/tests` to the workflow; document legacy, EGMRA and corpus commands;
  retain compilation step.
- **Regression test added:** workflow/manifests are the corrective coverage;
  final clean-install collection is recorded in the final verification report.
- **Post-fix verification:** current manifests include pytest 9.x and workflow
  line 34 invokes `egmra/tests`; local EGMRA invocations collect normally.
- **Residual limitation:** Python 3.10/3.12 interpreters were not locally
  available for parity; no ruff/black/mypy/pyright/bandit/semgrep configuration
  exists, and no package build metadata/API/migration command exists.
- **Confidence:** high.

### FBL-017 — Statement IR lost semantics and unexecuted probes passed

- **Finding ID:** FBL-017.
- **Severity:** HIGH.
- **Affected F-REQ IDs:** F-REQ-004, F-REQ-022, F-REQ-029,
  F-REQ-036 through F-REQ-039, F-REQ-093, F-REQ-106, F-REQ-158,
  F-REQ-180, F-REQ-203, F-REQ-210.
- **Specification source:** §2.3 lines 214-226; §6.1 lines
  466-517; §9.2 lines 1251-1259; §13.3 line 2026; §13.6 line
  2066.
- **Files and line ranges:** `egmra/intake/statement_ir.py:43-559`;
  `egmra/intake/probes.py:40-235`; `egmra/intake/contract.py:1-136`;
  `egmra/intake/review.py:20-114`; `egmra/orchestrator/loop.py:432-487`.
- **Symbols:** `StatementIR`, `GrammarParser`, `ClauseParser`, `ModelParser`,
  `reconcile`, `run_integrity_probes`, `build_problem_contract`,
  `verify_intent_certificate`.
- **Expected behavior:** exact source bytes/spans; dual independent structured
  parses preserve quantifier order/scope, domains, constraints, definitions,
  hypotheses and conclusions; ambiguities remain distinct; executable probes
  really execute and unknown/failure blocks intended-target release; downstream
  stages use the selected interpretation.
- **Observed behavior (pre-fix):** source decoding replaced invalid bytes;
  semantic identity omitted domains/definitions/constraints; nested quantifiers
  and positive-domain scope were lost; parsers invented binder `x` or English
  single-letter binders and truncated clauses; parser independence was a string
  ID; missing paraphrase/mutation/boundary/counterexample work returned passed;
  `release_blocked` was bypassed; the loop self-approved intent.
- **Reproduction command or test:** nine tests in
  `test_adversarial_intake.py`; baseline `fx-true-even-sum`/`fx-true-square`
  contradictions; orchestrator malformed-input, unresolved-interpretation and
  self-intent tests.
- **Root cause:** heuristic text extraction and “not run means harmless” defaults
  were treated as the translation firewall; semantic identity was incomplete.
- **Impact:** proving the wrong theorem/domain/quantifier, vacuous or out-of-
  scope probes, and releasing a result against an unapproved interpretation.
- **Whether existing tests detected it:** no; a critical ambiguity assertion was
  conditional and acceptance 7 stopped before release.
- **Fix performed:** exact raw-byte hash/spans and invalid UTF-8 rejection;
  immutable IR; explicit binder quantifier/domain/scope/constraints and
  definitions in semantic identity; nested quantified phrase extraction;
  strict model-parser schema; parser-family separation; unexecuted probes are
  explicit `executed=False`, `passed=False`; filter tested points to domain/
  constraints; missing probes/reconciliation block release; independently
  authenticated exact-binding intent review required; selected interpretation
  drives claims/computation/formal/release.
- **Regression test added:** `test_adversarial_intake.py`,
  `test_intent_review_security.py`, and relevant orchestrator/CLI cases.
- **Post-fix verification:** 71-test intake/orchestration batch passed; exact
  nested quantifier/domain/definition and unexecuted-probe cases behave as
  required locally.
- **Residual limitation:** two local regex/heuristic parser families are not a
  demonstrated independent semantic model family; complex notation,
  higher-order definitions, equivalence and round-trip behavior are incomplete.
  Probe artifact dictionaries are local data, and external human semantic
  review/process separation is deployment-dependent.
- **Confidence:** high for tested elementary statements; low-to-medium for
  general mathematical language.

### FBL-018 — Configuration secrets and model/cache identity were caller-controlled

- **Finding ID:** FBL-018.
- **Severity:** HIGH.
- **Affected F-REQ IDs:** F-REQ-015, F-REQ-020, F-REQ-025,
  F-REQ-078, F-REQ-091, F-REQ-117, F-REQ-120, F-REQ-152,
  F-REQ-175 through F-REQ-177, F-REQ-187, F-REQ-195, F-REQ-203,
  F-REQ-216.
- **Specification source:** §1 lines 76-78; §9.1 lines 1240-1244;
  §10.4 lines 1654-1680; §13.2 line 2013; §13.6 lines 2061-2063
  and 2073; §14.2 lines 2110-2140; §15 line 2248.
- **Files and line ranges:** `egmra/config.py:17-147`;
  `egmra/provenance/stage_identity.py:25-266`;
  `egmra/agents/runner.py:19-91`; `egmra/models/registry.py:30-64`.
- **Symbols:** `EgmraConfig`, `AttestedModelIdentity`,
  `attest_model_identity`, `verify_model_attestation`, `StageIdentity`,
  `AttestedRunner`, `ModelRegistry.pin_best`.
- **Expected behavior:** secrets remain out of files/logs/worker sandboxes;
  provider immutable identity is authenticated, not caller-labeled; every
  behavior/context/artifact/policy/tool identity binds cache/replay; model
  changes invalidate reuse and different labels do not prove independence.
- **Observed behavior (pre-fix):** secret rejection inspected only selected top-
  level names; arbitrary env names could be read; missing files/unknown keys/
  duplicate JSON/invalid values were permissive; `attested=True` was a caller
  Boolean; context/artifacts/schema and several behavior fingerprints did not
  bind cache compatibility; different string labels could imply independence.
- **Reproduction command or test:** all tests in
  `test_adversarial_foundations.py`, including forged attestation, duplicate
  artifacts, nonhash fields, cache field mutation, nested secrets, arbitrary
  secret read and invalid config values.
- **Root cause:** identity/attestation was represented as caller metadata and
  configuration was treated as benign local input.
- **Impact:** cache poisoning/stale adjudicator reuse, false reviewer/model
  independence, credential persistence/disclosure and unsafe operational
  defaults.
- **Whether existing tests detected it:** no; acceptance used string labels and
  direct Boolean identity fields.
- **Fix performed:** HMAC model identity with strong separate key and exact
  provider/model/version/build/surface/account binding; unattested labels cannot
  be independent or pinned; stage key includes every recorded behavior field,
  context, artifacts and schema and validates SHA-256/duplicates; recursive
  case-folded secret denylist; allowlisted secret reads; strict duplicate/
  unknown/file/symlink/size/type/range config validation; checker subprocess
  environment scrubbing.
- **Regression test added:** `test_adversarial_foundations.py` and Lean checker
  secret-exposure test.
- **Post-fix verification:** adversarial foundation/config batch passed as part
  of the strengthened suite; caller attestation Boolean no longer exists.
- **Residual limitation:** the local adapter itself issues HMAC after an injected
  provider call; no real provider-signed response or live API was verified.
  Anyone holding the process attestation key can issue identities. No key
  rotation, HSM, service-to-service identity, sensitive-log scanner, or monthly
  live bake-off was demonstrated.
- **Confidence:** high for local forgery/cache checks; low for real provider
  identity readiness.

### FBL-019 — Evaluation identity omitted behavior and fixture predicates allowed code execution

- **Finding ID:** FBL-019.
- **Severity:** HIGH.
- **Affected F-REQ IDs:** F-REQ-021, F-REQ-025, F-REQ-135
  through F-REQ-147, F-REQ-164, F-REQ-191, F-REQ-192, F-REQ-203,
  F-REQ-207, F-REQ-210 through F-REQ-215.
- **Specification source:** §12 lines 1825-1987; §13.3 line 2033;
  §13.6 line 2077; §13.7 lines 2079-2091; §15 lines 2217-2238.
- **Files and line ranges:** `egmra/eval/protocol.py:23-139`;
  `egmra/eval/datasets.py:28-231`; `egmra/eval/stats.py:1-58`;
  `egmra/eval/ablations.py:1-58`.
- **Symbols:** `FrozenEvalConfig`, `TimeCapsule`, `EvalRun`,
  `FixtureProblem.predicate`, `_compile_fixture_predicate`, `ReportedResult`,
  `AblationRegistry`.
- **Expected behavior:** immutable full evaluation identity/budget/network/tools;
  no answer/code leakage; valid dates/stats; sealed/preregistered paired equal-
  cost baselines/ablations; external datasets and blind grading actually run;
  no superiority/solve-rate claim without evidence.
- **Observed behavior (pre-fix):** config hash omitted status/tools/budget/network
  and nested budget was mutable; dates used lexical comparison; impossible
  result intervals/counts could be represented; fixture predicate source was
  passed to unrestricted `eval`; the CLI fixture worker replaced
  `_isprime(n)` with `True`, so a false finite claim could receive an optimistic
  computation; preregistration accepted blank/duplicate records; packages were
  schemas/constants with no evaluation runner or stored external results.
- **Reproduction command or test:** `test_adversarial_eval.py` changes each
  omitted identity field, mutates budget, supplies invalid stats/dates, and uses
  `__import__`, attribute traversal, `open`, and comprehension payloads.
- **Root cause:** evaluation manifests and local trusted fixtures were assumed
  safe, and registry presence was reported as execution.
- **Impact:** arbitrary code execution if fixture data is changed/imported,
  benchmark leakage/config drift, invalid statistical claims and false
  architecture superiority.
- **Whether existing tests detected it:** no; acceptance 18 tested only a two-
  Boolean helper and external benchmark manifests were never fetched/run.
- **Fix performed:** freeze/deep-freeze and hash every behavior/cost field;
  validate canonical ISO dates; validate denominators/intervals/censoring/
  pairing; replace Python `eval` with a closed recursive interpreter over an
  AST-allowlisted integer/Boolean expression language containing only `n` and
  explicit `_isprime(...)`, with complexity/constant limits and rejection of a
  bare helper as constant success; reject blank/duplicate
  preregistration; fixture computation now includes a real deterministic
  primality implementation; CLI no longer uses expected outcome inside the
  solver and reports mismatch nonzero.
- **Regression test added:** `test_adversarial_eval.py` code-execution payloads,
  Python-`eval` replacement, bare-helper and schema cases, plus strengthened
  CLI/evaluation cases.
- **Post-fix verification:** the final focused eval/CLI command passed 54 tests;
  malicious fixture expressions are rejected and Bandit reports no medium/high
  EGMRA production findings.
- **Residual limitation:** there is still no runner for the seven levels, four
  baselines, 13 ablations, external pinned datasets, sealed time capsules,
  paired seeds/costs, blind graders, contamination audit or stored results.
  Local elementary fixtures are not evidence of evaluation completeness.
- **Confidence:** high for local schema/code-execution fix; high that the broader
  evaluation is incomplete.

### FBL-020 — Lease, retry, and verifier capacity failed under expiry/race/restart

- **Finding ID:** FBL-020.
- **Severity:** HIGH.
- **Affected F-REQ IDs:** F-REQ-046, F-REQ-049, F-REQ-076,
  F-REQ-078, F-REQ-079, F-REQ-117 through F-REQ-119, F-REQ-170,
  F-REQ-183, F-REQ-196 through F-REQ-200, F-REQ-203.
- **Specification source:** §7.10 line 1064; §10.4 lines
  1654-1680; §13.6 line 2069; §14.3 lines 2142-2152; §14.5 lines
  2172-2188.
- **Files and line ranges:** `egmra/control/leases.py:1-232`;
  `egmra/control/throttle.py:1-70`; `egmra/control/parallel.py:1-98`;
  `egmra/orchestrator/loop.py:621-957`.
- **Symbols:** `LeaseManager.acquire/renew/assert_current/release`,
  retry delay/state functions, `VerifierReservedPool`.
- **Expected behavior:** atomic acquisition/renewal/expiry/reassignment with
  monotonic fencing and stale-write rejection across restart; exact provider-
  aware exponential backoff capped at 120 seconds without mathematical penalty;
  bounded verifier-reserved capacity and no starvation/deadlock/duplicate
  delivery effects.
- **Observed behavior (pre-fix):** expired holders could renew; fencing tokens
  and lease state were process-local/reusable; concurrent acquisition could
  race; corrupt persistence was not fail-closed; verifier pool capacity and
  under/overflow were weak; nonfinite/negative/huge retry values could overflow
  or evade the exact cap; none was a production boundary.
- **Reproduction command or test:** eight tests in
  `test_adversarial_control.py`; production stale-fence injection in
  `test_adversarial_orchestrator.py`.
- **Root cause:** in-memory illustrative state and formulas lacked durable
  locking/validation and were disconnected.
- **Impact:** stale/duplicate worker commits, lost work, split-brain truth,
  resource starvation and denial of service.
- **Whether existing tests detected it:** no; they used a fake clock and direct
  local helpers without restart/race/stale output.
- **Fix performed:** optional durable JSON state with regular-file/root checks,
  OS lock, atomic fsync and mode 0600; monotonic persisted fences; reject expired
  renew/stale release/commit; compatible transfer; thread-safe bounded
  generation/verifier slots; finite validation; overflow-safe exponential
  calculation and exact 120-second cap; strict Retry-After; orchestrator checks
  the fence after worker return and before reading/admitting any output.
- **Regression test added:** `test_adversarial_control.py` and stale-worker
  orchestrator case.
- **Post-fix verification:** 19 combined control tests passed and stale output is
  rejected before evidence admission.
- **Residual limitation:** local file locking is not a PostgreSQL/distributed
  lease transaction; no network partition, multi-host clock/heartbeat, large
  starvation/deadlock schedule, provider Retry-After integration or durable
  orchestrator resume was exercised.
- **Confidence:** high locally; low for distributed control.

### FBL-021 — Selection accepted invalid state and omitted hard constraints

- **Finding ID:** FBL-021.
- **Severity:** MEDIUM.
- **Affected F-REQ IDs:** F-REQ-008, F-REQ-043, F-REQ-053,
  F-REQ-054, F-REQ-067, F-REQ-068, F-REQ-143, F-REQ-203.
- **Specification source:** §6.2 lines 519-557; §7.1 lines 796-829;
  §7.2 lines 831-848; §12.3 lines 1900-1914.
- **Files and line ranges:** `egmra/selection/features.py:1-104`;
  `egmra/selection/posterior.py:1-89`;
  `egmra/selection/acquisition.py:1-148`;
  `egmra/orchestrator/loop.py:531-554`.
- **Symbols:** `ProblemFeatures`, `CompetingRiskPosterior`,
  `ProblemSelector.select`, `acquisition_score`.
- **Expected behavior:** complete feature families and hard exclusions precede
  acquisition; finite calibrated posteriors/weights; duplicate IDs/invalid k
  rejected; state/cost/uncertainty alters selection without becoming truth.
- **Observed behavior (pre-fix):** source authorization/license/wellformedness/
  false-promotion risk/duplicate constraints were absent or not enforced;
  malformed/NaN ranges/posteriors/outcomes/weights, duplicate IDs and invalid k
  could enter local selection; selector was disconnected.
- **Reproduction command or test:** five parametrized tests in
  `test_adversarial_selection.py`.
- **Root cause:** permissive dataclasses and toy-call assumptions without a
  closed acquisition boundary.
- **Impact:** unsafe or duplicate problems can consume budget; numerical poison
  can distort acquisition and evaluation.
- **Whether existing tests detected it:** no; they covered only ordinary toy
  ranking cases.
- **Fix performed:** add/enforce specified hard fields; validate all numerical
  ranges and posterior schema/positive finite alpha/censoring; reject duplicate
  IDs/invalid k/weights/components; production orchestrator calls selector and
  records acquisition before branch creation.
- **Regression test added:** `test_adversarial_selection.py` and orchestrator
  budget/malformed-input tests.
- **Post-fix verification:** 19 combined selection tests passed.
- **Residual limitation:** selection is not persisted, calibrated from a sealed
  evaluation ledger, or connected to the legacy global queue; no campaign-scale
  protected/cheap-probe/separate-queue experiment was run.
- **Confidence:** high for local validation; medium for production policy effect.

### FBL-022 — Legacy production gate trusted caller truth, labels, and arbitrary evidence paths

- **Finding ID:** FBL-022.
- **Severity:** CRITICAL.
- **Affected F-REQ IDs:** F-REQ-013 through F-REQ-015, F-REQ-020,
  F-REQ-027, F-REQ-032, F-REQ-109, F-REQ-112, F-REQ-120,
  F-REQ-122, F-REQ-129, F-REQ-149 through F-REQ-152, F-REQ-174,
  F-REQ-177, F-REQ-186, F-REQ-187, F-REQ-203, F-REQ-204,
  F-REQ-216.
- **Specification source:** §1 lines 65-78 and 83-85; §10.1 lines
  1515-1539; §10.2 lines 1571-1582; §11.1 lines 1703-1716; §11.3
  lines 1733-1758; §13.2 lines 2010-2013; §13.6 lines 2060, 2063
  and 2072-2073; §15 lines 2217-2248.
- **Files and line ranges:** `verification.py:16-418`;
  `run_verified_pipeline.py:35-192,219-300,350-450`;
  `promote_verified_run.py:25-215`; `aristotle_verifier.py:136-203,339-450`;
  `tests/test_legacy_trust_boundaries.py:1-190`.
- **Symbols:** `Review`, `VerificationEvidence`, `sign_review`,
  `sign_verification_evidence`, `evaluate_gate`, `load_evidence`, `promote`,
  legacy Aristotle evidence serialization, `ChatGPTBrowserRunner`.
- **Expected behavior:** the pre-existing production publisher must enforce the
  same stop-false-promotion principles: policy before untrusted input, closed
  kind-specific authenticated evidence bound to exact statement/candidate/
  scope/artifact, no expert/model consensus as truth, genuine independent
  reviewer identity, confined bounded artifact loading, and vendor-only
  Aristotle status never passing.
- **Observed behavior (pre-fix):** legacy `verification.py` accepted caller
  `passed=True` and `expert_review` as mathematical truth; fresh-context and
  caller model labels stood in for independent authority; promotion parsed/
  followed attacker-controlled evidence before checking a disabled policy;
  evidence JSON could reference absolute/arbitrary host files or symlinks; mixed
  receipts from different candidates were insufficiently bound, and mutually
  agreeing receipts could promote when the caller omitted canonical statement,
  candidate, problem, run-contract, execution and run-context anchors; legacy
  Aristotle conversion discarded vendor/local method provenance and could
  preserve optimistic status.
- **Reproduction command or test:** eight cases in
  `tests/test_legacy_trust_boundaries.py`, especially forged review/evidence,
  expert-as-truth, same-lineage, cross-candidate mix, policy-before-load and
  symlink/hash/duplicate-key loader tests; updated Aristotle integration tests
  assert vendor-only evidence is nonpassing.
- **Root cause:** the legacy gate predated the EGMRA trust model and treated
  caller result fields, labels and filesystem paths as trusted workflow input;
  policy enforcement occurred too late.
- **Impact:** this was a real top-level publication path, so forged status or a
  malicious evidence document could promote a false candidate and read/hash
  arbitrary host files even if the newer EGMRA path was secure.
- **Whether existing tests detected it:** no. Legacy tests constructed
  `passed=True`, treated expert approval as evidence, and exercised trusted
  local artifact paths.
- **Fix performed:** HMAC-authenticated closed `Review` and
  `VerificationEvidence` schemas with strong separate keys; exact statement,
  candidate, scope, artifact, certificate, coverage, validator and method
  binding; mandatory canonical problem/statement/candidate/run-contract/
  execution/run-context identity at the gate and in every signed receipt; only
  formal proof/exact computation evidence kinds; expert review
  excluded from truth; authenticated authority/model version/lineage and
  adjudicator-lineage checks; post-signature mutation/cross-candidate rejection;
  signed policy checked before touching evidence; bounded regular-file strict
  JSON loader confined to the evidence directory with relative no-symlink paths
  and content-hash validation; vendor-only Aristotle output serializes
  `passed=false` and retains verification method.
- **Regression test added:** `tests/test_legacy_trust_boundaries.py` (including
  missing-anchor, cross-run/candidate, policy/loader and forgery cases) plus
  updated legacy verification, pipeline and Aristotle
  suites.
- **Post-fix verification:** the dedicated legacy trust suite and the fresh
  final 231-case unittest discovery pass. A combined legacy/formal-
  correspondence spot check returned `14 passed in 0.10s`. The policy-before-
  load test proves the malicious loader is never called when disabled. All new
  legacy/checkpoint trust keys are also in the recursive config denylist and
  documented secret inventory.
- **Residual limitation:** the shipped `ChatGPTBrowserRunner` has no provider-
  attested immutable model gateway, so it cannot satisfy authenticated review
  independence and remains advisory/unreachable for promotion. The legacy gate
  and manifest remain quarantined compatibility data; the publisher is retired
  and there is no bridge to the EGMRA event graph/referee/five-gate certificate.
- **Confidence:** high for the reproduced legacy boundaries; medium for an
  exhaustive inventory of every older publication script.

### FBL-023 — Checkpoints were mutable, forgeable, unrelated to history, and identity-free

- **Finding ID:** FBL-023.
- **Severity:** HIGH.
- **Affected F-REQ IDs:** F-REQ-015, F-REQ-049, F-REQ-116
  through F-REQ-119, F-REQ-152, F-REQ-175, F-REQ-176, F-REQ-182,
  F-REQ-187, F-REQ-200, F-REQ-203.
- **Specification source:** §10.3 lines 1621-1652; §10.4 lines
  1654-1680; §13.2 line 2013; §13.6 lines 2061-2062, 2068 and
  2073; §14.5 lines 2172-2188.
- **Files and line ranges:** `egmra/orchestrator/checkpoint.py:48-508`;
  `egmra/tests/test_adversarial_checkpoint.py:51-324`;
  `audit/checkpoint_remediation.md:1-294`.
- **Symbols:** `Checkpoint`, `checkpoint_hash`, `verify_checkpoint_hash`,
  `take_checkpoint`, `_prefix_matches`, `resume`, cache/schema validators.
- **Expected behavior:** an immutable authenticated checkpoint commits complete
  durable execution identity; resume proves the exact event prefix, validates
  each stage cache by actual compatibility identity, classifies only recorded
  interrupted calls, recovers leases/replays high-trust artifacts, reconstructs
  state, and continues from the highest compatible stage.
- **Observed behavior (pre-fix):** nested state was mutable; the hash omitted
  controller, interpretations, budgets, seeds, leases, caches, rate state and
  schema; a caller could recompute a public digest after forgery; `resume()`
  accepted any internally valid but unrelated event log; cache reuse was one
  global string rather than per-stage actual identity; arbitrary caller IDs
  became censored interruptions; the only existing test still passed.
- **Reproduction command or test:** initial adversarial checkpoint run returned
  `8 failed, 1 passed`; later focused red tests showed unrecorded censoring and
  recomputed-hash forgery each accepted. Named cases include cross-log resume,
  exact-field mutation, missing stage identity, corrupted log and resealed
  inconsistent prefix.
- **Root cause:** a shallow frozen dataclass/content digest was mistaken for an
  authenticated durable recovery record, and current-log integrity was confused
  with checkpoint-to-prefix identity.
- **Impact:** an attacker or corrupt process could inject budget/controller/
  cache state, resume against another history, falsely classify failures as
  censored, or reuse incompatible model/adjudicator artifacts.
- **Whether existing tests detected it:** no. The single prior test repeated one
  global closure comparison and inspected one cache name.
- **Fix performed:** recursive immutable detachment; strict complete top-level/
  nested schemas and finite/digest validation; canonical record covering every
  current field; strong `EGMRA_CHECKPOINT_KEY` HMAC seal; exact run/sequence/last
  event/prefix Merkle verification while allowing a valid appended tail;
  per-stage artifact/compatibility/replay-policy/durable-stage identity and
  precise invalidation; authenticated in-flight call registry and subset check;
  new key documented and excluded from public config.
- **Regression test added:** 14 tests in
  `test_adversarial_checkpoint.py` covering deep immutability, every-field hash,
  wrong/missing key, public rehash forgery, unrelated/corrupt/resealed logs,
  appended tails, malformed schemas, duplicate/unrecorded calls and precise
  cache invalidation.
- **Post-fix verification:** focused checkpoint/orchestrator/acceptance command
  returned `38 passed in 1.01s`; compilation passed.
- **Residual limitation:** the object has no canonical durable file/database
  serializer/store, atomic persistence/read path, retention or external anchor;
  `research()` does not call checkpoint/resume; content omits several explicit
  graph/archive/blueprint/service identities; resume does not rebuild/compare
  the graph, transfer real leases, replay high-trust artifacts, restore
  controller/RNG objects, select/launch a stage or continue work. Per-stage
  fingerprints are supplied rather than independently derived from live
  `StageIdentity` objects.
- **Confidence:** high for local authentication/prefix/schema behavior; low for
  actual restart/resume capability.

### FBL-024 — Direct legacy publisher trusted a forged gate status and path-like category

- **Finding ID:** FBL-024.
- **Severity:** CRITICAL.
- **Affected F-REQ IDs:** F-REQ-002, F-REQ-014, F-REQ-034,
  F-REQ-130, F-REQ-131, F-REQ-133, F-REQ-134, F-REQ-149,
  F-REQ-150, F-REQ-174, F-REQ-203.
- **Specification source:** §1 lines 28-35 and 74-76; §5.1 lines
  387-394; §11.3 lines 1746-1758; §11.5 lines 1771-1823; §13.2
  lines 2010-2011 and 2019; §13.6 line 2060; §15 lines 2217-2238.
- **Files and line ranges:** `run_verified_pipeline.py:350-363`;
  `promote_verified_run.py:135-215`; `run_status.py:9-202`;
  `run_sol2_batch.py:43-51`; publication/status
  regressions in `tests/test_proof_pipeline.py:479-546` and
  `tests/test_run_status.py:60-94`.
- **Symbols:** `publish_verified_result`, `promote`, `has_verified_result`,
  `problem_disposition`, `should_skip_problem`.
- **Expected behavior:** every publication entry point consumes a current,
  authenticated, subject-bound release authorization derived from the complete
  gate result; a mutable status string is never authority. Output paths are
  confined beneath the configured output root and cannot be selected with an
  absolute path or traversal component.
- **Observed behavior (pre-fix):** `publish_verified_result` accepted any object
  whose `gate.status` string was `verified_proved` or `verified_disproved`, read
  an arbitrary candidate/manifest directory, and emitted a verified-labelled
  file without policy, receipts, replay or a release certificate. Because
  `base_dir / ... / category` discards its prefix when `category` is absolute,
  an absolute category wrote outside the output root; traversal components had
  the same confinement problem.
- **Reproduction command or test:** the independent audit constructed a
  `PipelineResult` for problem `424242` with a forged
  `GateDecision("verified_proved")`, a candidate and `{}` manifest, then called
  `publish_verified_result`; the verified-labelled file was created. Repeating
  with an absolute temporary directory as `category` wrote there rather than
  below `base_dir/outputs/chatgpt`.
- **Root cause:** the renderer was treated as a trusted continuation of the
  promoter, but it was a public function with no unforgeable handoff; path input
  was concatenated without a closed category grammar or resolved-root check.
- **Impact:** any direct caller could publish an arbitrary claim as verified and
  overwrite/delete verified-looking outputs outside the intended category
  tree. This bypassed all truth and communication gates even when the newer
  EGMRA release path was correct.
- **Whether existing tests detected it:** no. Existing publication tests reached
  the function only from a normal pipeline result and never forged the object
  or supplied absolute/traversal categories.
- **Fix performed:** retire the legacy publication authority completely.
  `publish_verified_result` now raises unconditionally before reading a
  candidate/manifest, creating directories, deleting stale outputs or using the
  category. Callers are directed to the EGMRA event-derived, independently
  signed `ReleaseCertificate` communication renderer. This deliberately avoids
  adding a public same-process signer that would merely notarize mutable legacy
  status.
- **Regression test added:**
  `ProofPipelineTests::test_external_evidence_promotes_but_legacy_publication_is_disabled`
  proves even a legacy result that passes the local evidence checks and reaches
  `awaiting_authenticated_release`, plus `../../outside`, cannot publish or
  create the output tree;
  `RunStatusTests::test_forged_verified_manifest_is_quarantined_not_completed`
  proves forged verified manifest/done-marker status is not treated as complete.
- **Post-fix verification:** the publication regression passed alone
  (`1 passed in 0.09s`); the run-status/adjudication focused batch passed
  `13 passed in 0.10s`. The former direct forged-result/path reproduction now
  raises before any filesystem side effect.
- **Residual limitation:** the repository has no compatible legacy-to-EGMRA
  publication bridge; callers of `promote(..., publish=True)` now fail closed
  rather than publish. This is intentionally `UNREACHABLE`, not a completed
  second release path. Verified output must use the EGMRA certificate renderer.
- **Confidence:** high; both status forgery and path escape were reproduced with
  direct public calls.

### FBL-025 — Same-process attestation helpers could notarize asserted identity

- **Finding ID:** FBL-025.
- **Severity:** HIGH.
- **Affected F-REQ IDs:** F-REQ-015, F-REQ-020, F-REQ-032,
  F-REQ-109, F-REQ-120, F-REQ-122, F-REQ-152, F-REQ-177,
  F-REQ-187, F-REQ-195, F-REQ-203, F-REQ-216.
- **Specification source:** §1 lines 76-77 and 83-85; §10.1 lines
  1515-1539; §10.5 lines 1682-1689; §11.1 lines 1703-1716;
  §13.2 line 2013; §13.6 lines 2063 and 2073; §14.2 lines
  2110-2127; §15 lines 2217-2248.
- **Files and line ranges:** `verification.py:115-158,219-358,361-545`;
  `proof_pipeline.py:314-380,930-1012`; `run_adjudication.py:289-418`;
  `tests/test_proof_pipeline.py:1-650`;
  `tests/test_legacy_trust_boundaries.py:1-412`.
- **Symbols:** `sign_review`, `sign_verification_evidence`,
  `verify_review_attestation`, `verify_verification_evidence`,
  `VerificationBinding`, `ProofPipeline._attest_review`,
  `verification_evidence_provider`.
- **Expected behavior:** only an isolated gateway that actually identifies the
  provider/model/checker and validates the returned artifact may issue an
  independent receipt. The receipt binds exact request, response/artifact,
  problem, statement, candidate, contract, execution and context. Generator
  code cannot self-assign lineage, checker identity or independence.
- **Observed behavior (pre-fix):** labels and context URLs stood in for model
  identity, and a caller could attach `passed=True`. During remediation, the
  new HMAC helpers closed field mutation but remained public same-process
  notaries: tests supplied one fake attestor that assigned asserted lineages to
  one fake runner, and the evidence provider signed dummy repeated hashes for a
  nonexistent artifact/certificate without invoking a checker. A public
  materialization wrapper also cannot by itself establish provenance: a caller
  holding the same evidence key can sign arbitrary metadata and supply bytes
  chosen to match it. The production browser runner has no attestation gateway,
  so its positive release path is unreachable rather than verified.
- **Reproduction command or test:** audit inspection plus the existing test
  fixtures `attest_test_review` and `evidence_provider`; replacing their claimed
  provider/lineage/checker strings and dummy hashes still produces locally
  signed fixtures. `LegacyTrustBoundaryTests::test_claimed_materialization_hash_is_recomputed_from_actual_bytes`
  demonstrates that a mismatched claimed digest is now rejected, but a caller
  that can invoke `sign_verification_evidence` remains in the same trust domain
  as `MaterializedVerificationEvidence`; no test can turn that co-residence into
  independent origin authentication. Cross-candidate/run relabel attempts now
  fail, but actual provider/checker provenance is not established.
- **Root cause:** message integrity was conflated with origin authentication.
  A symmetric key held by the same process that constructs caller fields cannot
  prove organizational independence or that a provider/checker ran.
- **Impact:** careless deployment of these helpers as a production gateway
  would turn self-asserted model/checker metadata into apparently authenticated
  evidence and reintroduce correlated-consensus or fake-verifier promotion.
  In the current default deployment it instead prevents genuine completion.
- **Whether existing tests detected it:** no. They intentionally use local fake
  signers and therefore prove protocol shape/mutation resistance, not real
  authority, provider identity or artifact verification.
- **Fix performed:** receipts now require canonical problem/statement/candidate/
  run-contract/execution/run-context bindings; the evidence provider receives a
  typed `VerificationBinding`; omission or cross-run/cross-candidate reuse fails;
  materialized artifact payloads are immutably copied and their SHA-256 is
  recomputed inside `evaluate_gate`; no review attestor means reviews are
  blockers only; gate-mutating adjudication fails before a provider call or
  persistent marker; and every otherwise-passing legacy decision stops at
  `awaiting_authenticated_release` rather than truth promotion/publication.
- **Regression test added:** missing-canonical-anchor, metadata-without-artifact,
  mismatched-materialized-bytes and mixed/cross-run receipt tests in
  `test_legacy_trust_boundaries.py`; binding relabel regression in
  `tests/test_proof_pipeline.py`; no-attestor adjudication regression in
  `tests/test_run_adjudication.py`.
- **Post-fix verification:**
  `.venv/bin/python -m pytest -q tests/test_legacy_trust_boundaries.py tests/test_verification.py tests/test_run_status.py`
  returned `33 passed in 0.10s`. No live or asymmetric provider/checker gateway
  was available, so positive independence remains `BLOCKED-EXTERNAL` and the
  production browser path remains `UNREACHABLE` for verified release.
- **Residual limitation:** the repository has no isolated asymmetric
  provider-attestation service, hardware/workload identity, independently
  operated evidence signer, or live checker-origin verification. The local HMAC
  helpers must be treated as test/protocol scaffolding, not independent proof.
- **Confidence:** high that the residual exists; low regarding behavior of any
  future external gateway because none was exercised.

### FBL-026 — Aristotle child, archive, and run-directory boundaries were unsafe

- **Finding ID:** FBL-026.
- **Severity:** CRITICAL.
- **Affected F-REQ IDs:** F-REQ-014, F-REQ-019, F-REQ-091,
  F-REQ-104, F-REQ-105, F-REQ-109, F-REQ-120, F-REQ-151,
  F-REQ-186, F-REQ-194, F-REQ-203.
- **Specification source:** §1 lines 74-76 and 81-84; §9.1 lines
  1240-1244; §9.6 lines 1405-1417; §10.1 lines 1515-1539; §10.5
  lines 1682-1689; §13.2 line 2012; §13.6 line 2072; §14.1 line
  2104; §15 lines 2217-2238.
- **Files and line ranges:** `aristotle_verifier.py:92-450,471-587,592-730,745-951`;
  `lean_verify.py:82-149` (the pre-fix host-build target, no longer called by
  this adapter); `tests/test_aristotle_verifier.py:152-540`.
- **Symbols:** `_load_dotenv_files`, `AristotleConfig.from_env`,
  `AristotleClient._default_runner`, `AristotleClient.prove`,
  `write_formal_proof_evidence`, `verify_run`.
- **Expected behavior:** the external CLI receives only its minimum required
  environment, never EGMRA trust keys or unrelated credentials; every run/input/
  output directory is a confined non-symlink tree; downloaded archives have
  bounded compressed/expanded size, member count and regular-file types before
  extraction. Vendor `lakefile.lean`/`lakefile.toml`, generated Lean and build
  hooks never execute on the host; kernel checking occurs only in a credential-
  free hardened quarantine and remains non-promotable without the required
  independent replay/correspondence evidence.
- **Observed behavior (pre-fix):** `_default_runner` copied all of
  `os.environ`, exposing policy, event, evidence, checkpoint, gate, release and
  other signing keys to the externally configured Aristotle executable.
  `verify_run` and `write_formal_proof_evidence` followed a pre-created
  `run_dir/aristotle` symlink and wrote statement, candidate, Lean, summary,
  fidelity and evidence outside the run. `tar.extractall(filter="data")`
  addressed traversal but imposed no archive member, type or expanded-byte
  budget, permitting archive bombs/resource exhaustion. More critically,
  `assess_project(run_kernel=True)` passed the vendor-extracted tree to
  `lean_verify.verify_project`, whose default runner executed
  `lake exe cache get` and `lake build` in the directory containing the
  untrusted vendor lakefile. A malicious Lake configuration/build hook could
  therefore execute arbitrary host code before any proof decision.
- **Reproduction command or test:** a mocked `subprocess.run` captured EGMRA
  signing keys in the child `env`; a temporary `aristotle` symlink to an outside
  directory caused four or more generated files to appear outside the run; a
  many-member/large-expanded tar was accepted for extraction. An injected
  recording kernel runner confirmed both `lake exe cache get` and `lake build`
  were invoked with the vendor project as `cwd`; the default runner uses the
  same commands through `subprocess.run`. These probes were converted to the
  focused Aristotle regressions listed below.
- **Root cause:** the adapter inherited a developer shell environment and used
  convenience `Path.mkdir`/`write_text`/bulk extraction as though provider
  output and run directories were trusted.
- **Impact:** a malicious/replaced CLI could steal every co-resident symmetric
  trust key and forge later policy/evidence/release records; a local symlink
  attacker could overwrite arbitrary writable files; a provider archive could
  exhaust disk, memory or inode resources; and a malicious Lake build file could
  execute arbitrary code with verifier-process privileges and credentials.
- **Whether existing tests detected it:** no. The fake CLI ran in-process,
  archives were tiny and benign, and temporary run trees contained no hostile
  symlinks.
- **Fix performed:** the provider child now receives only an explicit runtime
  allowlist plus `ARISTOTLE_API_KEY`; dotenv loading imports only Aristotle
  configuration and provider/child failures redact process secrets. Run,
  parent/grandparent, Aristotle and input directories are opened through pinned
  no-follow descriptors; manifest/problem/candidate/output files are bounded
  regular single-link files; writes reject existing symlinks. Downloaded archive
  bytes, member count, per-member and aggregate expanded size, paths, duplicate
  names, sparse entries, links and non-regular types are validated before
  extraction. Vendor projects are inventory-only quarantine data:
  `assess_project` never calls `lake exe cache get`, `lake build`, or an injected
  kernel runner and always returns unverified/nonpassing legacy evidence.
- **Regression test added:** child-environment secret noninheritance/redaction,
  dotenv allowlist, run/parent/grandparent/Aristotle/input/output symlink,
  bounded run inputs, archive link member, excessive member count, oversized
  compressed archive and no-host-vendor-Lake-build tests in
  `tests/test_aristotle_verifier.py`.
- **Post-fix verification:** `.venv/bin/python -m py_compile aristotle_verifier.py`
  exited 0. `.venv/bin/python -m pytest -q tests/test_aristotle_verifier.py`
  returned `34 passed, 8 subtests passed in 0.54s`. The remediation agent also
  ran full legacy unittest discovery with `221/221` passing and `git diff
  --check` at exit 0. The original child-secret, static symlink, link-member,
  archive-flood/size and host-vendor-Lake probes now fail closed.
- **Residual limitation:** no real Aristotle credentials/service was used and
  vendor Lean is deliberately not compiled here. A separate hardened T5 service
  with independent replay/correspondence attestation remains an external and
  integration limitation; filesystem-wide quotas and hostile same-UID ancestor
  replacement beyond the pinned ancestry remain deployment concerns.
- **Confidence:** high for the local pre-fix exploits; none of this demonstrates
  live provider correctness.

### FBL-027 — Legacy parsing and evidence loading were ambiguous, unbounded, and policy-unsafe

- **Finding ID:** FBL-027.
- **Severity:** HIGH.
- **Affected F-REQ IDs:** F-REQ-014, F-REQ-015, F-REQ-104,
  F-REQ-105, F-REQ-109, F-REQ-120, F-REQ-149, F-REQ-150,
  F-REQ-174, F-REQ-194, F-REQ-200, F-REQ-203.
- **Specification source:** §1 lines 74-77; §9.6 lines 1405-1417;
  §10.1 lines 1515-1539; §10.5 lines 1682-1689; §13.2 lines
  2010-2011 and 2019; §13.6 line 2060; §14.1 line 2104; §14.5
  lines 2172-2188; §15 lines 2217-2238.
- **Files and line ranges:** `verification.py:126-620`;
  `proof_pipeline.py:220-296`; `run_verified_pipeline.py:39-348`;
  `promote_verified_run.py:37-215`; regressions in
  `tests/test_verification.py:83-117`, `tests/test_proof_pipeline.py:398-426`
  and `tests/test_legacy_trust_boundaries.py:140-409`.
- **Symbols:** `candidate_contract`, `_json_object`, `_strict_json_object`,
  `_read_regular_at`, `_open_evidence_document`, `inspect_evidence`,
  `load_evidence`, `_enforce_promotion_policy`, `_validated_run_candidate`,
  `promote`, `MaterializedVerificationEvidence`, `evaluate_gate`.
- **Expected behavior:** a verified signed policy is enforced before any
  untrusted path or content side effect; only the concrete authenticated policy
  authority is accepted. JSON is closed and duplicate-key unambiguous; hostile
  numeric fields fail closed without unbounded conversion or exceptions. Input
  opening is nonblocking, no-follow and anchored to an already-open directory;
  record count and aggregate unique artifact work are bounded; a disabled
  formal path cannot inspect formal artifacts; a caller assertion is not proof
  that artifact bytes were loaded and validated.
- **Observed behavior (pre-fix):** duplicate review/evidence keys used ambiguous
  last-value behavior, and an arbitrarily long decimal candidate score/count
  reached `int()` instead of yielding a deterministic rejected contract.
  `os.open(O_RDONLY)` blocked on a FIFO before `fstat` could reject it;
  component-by-component `is_symlink` followed by a separate final open left a
  path-swap window; per-file limits allowed many records to repeatedly hash
  artifacts without an aggregate/count budget. `formal_promotion` was checked
  only after formal evidence/artifacts were loaded; arbitrary duck-typed objects
  with a no-op `require` could stand in for `PolicyEnforcer`; promotion read a
  manifest before the generic policy check. An intermediate attempted fix used
  the importable module object `verification._MATERIALIZATION_TOKEN`; a direct
  caller wrapped signed dummy metadata plus its claimed hash and obtained
  `verified_proved` without a real artifact file.
- **Reproduction command or test:** a subprocess calling the old bounded reader
  on a FIFO exceeded its timeout; a 707 KiB document with roughly 1000 repeated
  records was accepted and repeatedly processed; a mock loader was invoked with
  promotion enabled but formal promotion disabled; and a no-op duck enforcer
  bypassed the intended authority type. The importable-token probe constructed
  the old materialized wrapper around a signed dummy receipt and returned
  `GateDecision(status='verified_proved')`. The converted regressions are
  `LegacyTrustBoundaryTests::test_evidence_loader_rejects_symlink_escape_duplicate_keys_and_hash_drift`,
  `::test_evidence_loader_rejects_fake_policy_fifo_and_record_flood`,
  `::test_formal_policy_is_checked_before_artifact_loader`,
  `::test_claimed_materialization_hash_is_recomputed_from_actual_bytes`,
  `VerificationGateTests::test_oversized_numeric_candidate_field_fails_closed_without_raising`,
  and `ProofPipelineTests::test_duplicate_review_keys_fail_closed_instead_of_last_wins`.
  Path-swap risk was established from the check/open sequence and remediated
  with directory-anchored opens rather than a timing-dependent exploit.
- **Root cause:** isolated per-file checks were added without treating the whole
  load as one adversarial transaction or the policy object as a capability;
  policy selection depended on evidence type discovered only after loading it.
- **Impact:** an attacker could indefinitely occupy a worker, amplify CPU/I/O,
  race artifact selection, cause disabled-feature reads, or bypass policy using
  a caller object. In a privileged verifier this is a denial-of-service and
  confidentiality/integrity boundary failure.
- **Whether existing tests detected it:** only partially. An earlier loader test
  covered one duplicate-key evidence object, one final symlink, one hash mismatch
  and disabled generic promotion. It did not cover duplicate review keys,
  oversized numeric conversion, FIFO blocking, aggregate/count amplification,
  duck-typed policy, formal-policy ordering, component races or the importable
  materialization token.
- **Fix performed:** add strict duplicate-key parsing and a nine-digit lexical
  bound before candidate numeric conversion; use nonblocking regular-file opens;
  require the concrete `PolicyEnforcer`; enforce generic policy before manifest
  reads and formal policy before artifact loads; impose closed record-count,
  per-artifact and aggregate-byte limits; reject duplicate artifact paths and
  digests; and traverse artifacts through pinned directory descriptors with
  no-follow opens. Manifest/candidate/run identities are recomputed rather than
  trusted from JSON. The importable token was removed: materialized payloads are
  immutable byte copies and `evaluate_gate` independently recomputes every
  included digest. Even an otherwise passing legacy decision now stops at
  `awaiting_authenticated_release`; it cannot publish.
- **Regression test added:** duplicate review/evidence key, oversized numeric,
  mismatched materialized bytes, FIFO/nonblocking, wrong enforcer type,
  policy-before-manifest, formal-policy-before-artifact, excessive record count,
  aggregate artifact budget, duplicate-artifact accounting and hostile
  component cases in the three files listed above.
- **Post-fix verification:**
  `.venv/bin/python -m pytest -q tests/test_legacy_trust_boundaries.py tests/test_verification.py tests/test_run_status.py`
  returned `33 passed in 0.10s`. The FIFO rejects promptly, disabled policy
  invokes no attacker-controlled loader/read, oversized input rejects
  deterministically, duplicate keys fail closed, and mismatched materialized
  bytes cannot satisfy the gate.
- **Residual limitation:** artifact-byte integrity does not prove independent
  verifier origin while the signer and wrapper remain in one Python process
  (FBL-025). A hostile process with concurrent write access to every ancestor
  directory is beyond the tested local guarantee; total run/artifact retention
  quotas, disk-full recovery and service-level admission control remain
  incomplete. The complete affected F-REQs therefore remain partial.
- **Confidence:** high for the reproduced duplicate/numeric/FIFO/policy/resource
  defects and tested anchored artifact opens; medium for exhaustive TOCTOU
  resistance and independent evidence origin.

### FBL-028 — Adjudication could poison retry state and override formal truth

- **Finding ID:** FBL-028.
- **Severity:** HIGH.
- **Affected F-REQ IDs:** F-REQ-015, F-REQ-020, F-REQ-025,
  F-REQ-032, F-REQ-122, F-REQ-127, F-REQ-129, F-REQ-132,
  F-REQ-187, F-REQ-188, F-REQ-200, F-REQ-203, F-REQ-216.
- **Specification source:** §1 lines 76-77 and 83-85; §2.2 line
  212 and §2.6 lines 255-270; §11.1 lines 1703-1716; §11.2 lines
  1729-1731; §11.3 lines 1733-1745; §11.4 lines 1759-1769;
  §13.6 lines 2073-2074; §14.5 lines 2172-2188; §15 lines
  2217-2248.
- **Files and line ranges:** `run_adjudication.py:69-213,285-435`;
  `verification.py:355-545`; `egmra/m0.py:1-163` evidence-precedence helper;
  `tests/test_run_adjudication.py:182-298`;
  `tests/test_legacy_trust_boundaries.py:179-213`.
- **Symbols:** `find_adjudicatable_runs`, `adjudicate_run`,
  `adjudicate_awaiting`, `evaluate_gate`, `evidence_precedence`.
- **Expected behavior:** unavailable/malformed/unauthenticated adjudication is
  retryable and cannot create a terminal completion marker or mutate the gate.
  Authenticated disagreement is adjudicated by dimension: model dissent cannot
  overrule exact kernel truth, though it may block statement fidelity,
  applicability, novelty or significance; same-scope evidence conflict remains
  unresolved/escalated.
- **Observed behavior (pre-fix):** the default queue provided no attestor; a
  syntactically valid response was then classified malformed and persisted a
  terminal adjudication file, so the next scan skipped the still-unadjudicated
  run (`before=1`, `malformed=True`, `after=0`). Advisory-only calls could also
  leave a marker that blocked a later authenticated attempt. Separately,
  `evaluate_gate` treated any dissenting model review as a truth rejection even
  when authenticated hardened formal evidence established the encoded theorem,
  contradicting the specification's explicit kernel/model precedence.
- **Reproduction command or test:** the queue-state probe above; a fake runner
  call count/marker/pending assertion; and an independently signed formal-proof
  evidence fixture with one authenticated adjudicator dissent, which returned
  `candidate_rejected` instead of preserving formal truth while separating the
  disputed dimension.
- **Root cause:** one file represented both advisory attempt telemetry and
  successful terminal adjudication; the gate collapsed truth, intent,
  applicability, novelty and significance into one unanimous model-review
  Boolean.
- **Impact:** transient configuration/model failures could permanently starve
  work, while an untrusted/correlated model could incorrectly erase formal truth
  or force an overbroad rejection. Both behaviors corrupt campaign state and
  the public disposition.
- **Whether existing tests detected it:** no. Tests injected a signing attestor
  for happy paths, treated advisory marker creation as harmless, and did not put
  authenticated formal evidence in conflict with model dissent.
- **Fix performed:** gate-mutating adjudication now requires an authenticated
  review gateway before any manifest read, provider call or marker; absent
  gateway leaves every byte unchanged and the run pending. Advisory/malformed
  telemetry is explicitly unauthenticated/unapplied, and discovery treats a
  marker as terminal only when both `authenticated` and `applied` are exactly
  `true`, so a later authenticated attempt remains eligible. The direct legacy
  gate now checks valid materialized hardened formal evidence before model-review
  dissent and returns `awaiting_authenticated_release`, preserving encoded truth
  without authorizing publication.
- **Regression test added:**
  `RunAdjudicationTests::test_malformed_output_is_advisory_only`,
  `::test_default_cli_advisory_path_records_parsed_but_unauthenticated_verdict`,
  `::test_gate_mutation_without_attestor_is_rejected_before_provider_or_marker`,
  and
  `LegacyTrustBoundaryTests::test_hardened_formal_truth_is_not_overruled_by_model_dissent`.
- **Post-fix verification:**
  `.venv/bin/python -m pytest -q tests/test_proof_pipeline.py tests/test_run_adjudication.py tests/test_stage_cache_contract.py`
  returned `35 passed, 5 subtests passed in 0.34s`; the combined legacy
  trust/verification/status command returned `33 passed in 0.10s`. The
  no-attestor path performs zero provider calls and writes no marker; advisory
  and malformed records are rediscovered; and the direct materialized-evidence
  gate preserves hardened encoded truth at the retired release boundary.
- **Residual limitation:** the shipped CLI has no authenticated production
  adjudicator gateway and therefore cannot complete gate mutation. The persisted
  legacy adjudication path reconstructs evidence metadata, not a freshly
  materialized artifact bundle, so the direct formal-precedence test does not
  establish full production-path precedence. Preserving encoded theorem truth
  does not imply I2/F2/N2/S2, and the scalar legacy schema cannot express which
  dimension a dissent targets. These limitations keep the affected requirements
  partial/unreachable even though queue poisoning is fixed.
- **Confidence:** high for both queue-poisoning fixes and the direct gate's
  encoded-truth behavior; high that production identity and full dimensional
  precedence remain absent.

### FBL-029 — Caller-writable stage cache used circular adjacent-digest authentication

- **Finding ID:** FBL-029.
- **Severity:** HIGH.
- **Affected F-REQ IDs:** F-REQ-015, F-REQ-016, F-REQ-117,
  F-REQ-118, F-REQ-120, F-REQ-152, F-REQ-175, F-REQ-176,
  F-REQ-187, F-REQ-200, F-REQ-203.
- **Specification source:** §1 lines 76-78; §10.3 lines 1621-1652;
  §10.4 lines 1654-1680; §13.2 line 2013; §13.6 lines 2061-2062
  and 2073; §14.5 lines 2172-2188; §15 lines 2217-2238.
- **Files and line ranges:** `proof_pipeline.py:452-543,633-637`;
  `tests/test_proof_pipeline.py:151-239`;
  `tests/test_stage_cache_contract.py:155-172,389-405`.
- **Symbols:** `ProofPipeline._run`, `ProofPipeline.solve`,
  `_stage_cache`, `stage_cache_context_id`.
- **Expected behavior:** model/adjudicator output is replayable only from an
  authenticated artifact whose immutable provider/runner identity, exact
  prompt/response and complete behavior closure are independently verified.
  Caller-writable cache metadata cannot authenticate adjacent caller-writable
  output or restore an asserted context. An incomplete run resumes only through
  the specified authenticated checkpoint/event path.
- **Observed behavior (pre-fix):** a stage response and its SHA-256/context
  metadata were stored together under the caller-selected artifact root. An
  attacker could replace both files, recompute the unkeyed response digest and
  make the cache replay forged reviewer/model text while restoring an attacker
  context. The solver also reused caller-writable incomplete execution
  directories as though they were authoritative restart checkpoints.
- **Reproduction command or test:**
  `ProofPipelineTests::test_stage_cache_is_never_trusted_even_if_response_and_metadata_match`
  writes a forged approval, updates the adjacent `response_sha256` and context,
  and then invokes the production `_run` path. On the audit-start behavior the
  forged response was the cache hit; the remediated path calls the provider.
  `StageCacheContractTests::test_no_caller_writable_incomplete_execution_directory_is_resumed`
  covers the analogous execution-directory reuse.
- **Root cause:** an unkeyed digest stored in the same mutable trust domain as
  its payload was mistaken for provenance, and a directory-name/manifest match
  was mistaken for an authenticated checkpoint.
- **Impact:** a local artifact-tree writer could inject pass-looking reviewer or
  adjudicator output, manufacture context provenance and influence gate/manifest
  state without a fresh provider call. Reusing an incomplete run could mix
  outputs across executions and make restart claims non-reproducible.
- **Whether existing tests detected it:** no. Prior cache tests generated both
  files honestly and asserted successful replay/context restoration; they did
  not mutate the response and metadata together or distinguish a diagnostic
  transcript from an authenticated replay artifact.
- **Fix performed:** remove all model-stage cache reads and context restoration.
  Stage files are now atomic diagnostic transcripts only; every `_run` obtains
  fresh output from its configured isolated runner. `solve` always allocates a
  fresh exclusive mode-0700 execution and stage directory and never treats an
  incomplete caller-writable run as a resume source. Exact run contracts remain
  recorded for audit but do not confer cache authority.
- **Regression test added:** the two named tests above plus
  `StageCacheContractTests::test_exact_contract_is_recorded_but_never_replays_model_output`.
- **Post-fix verification:**
  `.venv/bin/python -m pytest -q tests/test_proof_pipeline.py tests/test_run_adjudication.py tests/test_stage_cache_contract.py`
  returned `35 passed, 5 subtests passed in 0.34s`. The forged pair is ignored,
  a fresh provider call occurs, no forged context is restored and a copied
  incomplete execution remains untouched.
- **Residual limitation:** authenticated model-output replay is not implemented;
  restart/resume through this legacy path is intentionally disabled rather than
  complete. The full event/checkpoint reconstruction loop remains partial under
  FBL-023, so affected cache/recovery requirements are not `VERIFIED`.
- **Confidence:** high for the circular-cache reproduction and local fix; high
  that authenticated restart/replay remains absent.

### FBL-030 — Symlinked legacy artifact and problem roots redirected production writes

- **Finding ID:** FBL-030.
- **Severity:** HIGH.
- **Affected F-REQ IDs:** F-REQ-014, F-REQ-016, F-REQ-120,
  F-REQ-149, F-REQ-150, F-REQ-174, F-REQ-200, F-REQ-203.
- **Specification source:** §1 lines 74-77; §9.6 lines 1405-1417;
  §10.1 lines 1515-1539; §13.2 lines 2010-2013 and 2019; §13.6
  lines 2060 and 2072; §14.1 line 2104; §15 lines 2217-2238.
- **Files and line ranges:** `proof_pipeline.py:142-180,498-543`;
  `run_adjudication.py:69-157,160-213,285-418`;
  `tests/test_proof_pipeline.py:240-266`;
  `tests/test_run_adjudication.py:230-280`.
- **Symbols:** `_require_real_directory`,
  `_create_or_validate_real_directory`, `ProofPipeline.solve`,
  `_require_confined_run_directory`, `_write_json_confined`, `_run_dirs`,
  `find_adjudicatable_runs`, `adjudicate_run`.
- **Expected behavior:** caller-controlled artifact, problem and run directories
  are real confined directories; no provider call or artifact write occurs
  through a symlink. Critical reads are bounded/no-follow and output replacement
  is anchored to already-open directory descriptors.
- **Observed behavior (pre-fix):** `Path.mkdir(..., exist_ok=True)`, `is_dir`,
  direct `read_text`/`write_text` and path-based replacement followed symlinked
  artifact/problem/run components. Supplying a symlinked artifact root or a
  pre-created `problem_<n>` symlink caused proof/adjudication artifacts to be
  read or written in the symlink target outside the intended tree.
- **Reproduction command or test:**
  `ProofPipelineTests::test_symlinked_artifact_root_and_problem_directory_fail_before_writes`
  and
  `RunAdjudicationTests::test_symlinked_artifact_or_problem_directory_is_rejected_without_writes`
  construct root/problem symlinks to an outside directory, invoke the production
  solve/discovery/adjudication entry points, and assert zero provider calls,
  unchanged manifest bytes and no outside files. Those assertions failed on the
  audit-start path and pass after remediation.
- **Root cause:** path strings were treated as stable confinement capabilities;
  symlink-following convenience APIs separated validation from use and allowed
  writes below attacker-selected directory objects.
- **Impact:** an artifact-tree attacker could redirect model transcripts,
  manifests and adjudication records into another writable tree, overwrite
  trusted-looking run state, or make the verifier consume another run's data.
- **Whether existing tests detected it:** no. Temporary artifact roots were
  always newly created real directories and no test substituted root/problem
  components or asserted that the provider remained uncalled.
- **Fix performed:** proof solving lstat-validates root/problem/run directories,
  creates a fresh exclusive mode-0700 execution and refuses static symlink
  components before any provider call or write. Adjudication bounds every input
  read with `O_NOFOLLOW|O_NONBLOCK`, validates the root/problem/run chain, and
  writes temporary JSON plus atomic replacement through pinned no-follow
  root/problem/run directory descriptors.
- **Regression test added:** the two named symlink tests plus
  `RunAdjudicationTests::test_gate_mutation_without_attestor_is_rejected_before_provider_or_marker`,
  which also proves the preflight changes zero bytes.
- **Post-fix verification:** the same `35 passed, 5 subtests passed in 0.34s`
  focused command passed. Static root/problem substitution is rejected before a
  provider call and leaves the external target unchanged.
- **Residual limitation:** proof solving still uses path-based writes after its
  initial lstat checks, so a hostile same-UID process capable of concurrent
  rename/substitution is not exhaustively excluded. Adjudication writes are
  directory-fd anchored, but its two JSON replacements are individually atomic,
  not one cross-file transaction; scanner/read paths have not undergone a full
  hostile-filesystem race campaign.
- **Confidence:** high for the static symlink exploit and regression; medium for
  exhaustive concurrent-filesystem resistance.

### FBL-031 — Fixture CLI reported verified success without promotion or release

- **Finding ID:** FBL-031.
- **Severity:** HIGH.
- **Affected F-REQ IDs:** F-REQ-002, F-REQ-014, F-REQ-034,
  F-REQ-130, F-REQ-131, F-REQ-133, F-REQ-134, F-REQ-149,
  F-REQ-150, F-REQ-163, F-REQ-174, F-REQ-203, F-REQ-204.
- **Specification source:** §1 lines 28-35 and 74-76; §5.1 lines
  387-394; §11.3 lines 1746-1758; §11.5 lines 1771-1823;
  §13.2 lines 2010-2019; §13.3 line 2030; §13.6 line 2060;
  §15 lines 2217-2238.
- **Files and line ranges:** `egmra/cli.py:66-121`;
  `egmra/tests/test_cli.py:106-140`.
- **Symbols:** `cmd_run`, `_fixture_expectation_met`, `ResearchResult.render`.
- **Expected behavior:** a fixture whose expected outcome is `verified` exits 0
  only when the actual current run has a complete compiled proof, promoted
  decision, valid current five-gate attestation, valid current release
  certificate, nonblocked referee/policy state and a release outcome consistent
  with the gate summary. Candidate-side progress cannot satisfy a release
  expectation.
- **Observed behavior (pre-fix):** with promotion disabled by signed policy, the
  true fixture returned `release_blocked_by_policy`, `proof_complete=false` and
  `release=null`; nevertheless `_fixture_expectation_met("verified", result)`
  returned true, `expectation_met` was printed true and the CLI exited 0. The
  prior positive fixture test itself used `promotion=False` and asserted only
  candidate/expectation fields, thereby codifying the false success.
- **Reproduction command or test:**
  `egmra/tests/test_cli.py::test_cli_verified_expectation_requires_actual_release_not_candidate_only`
  runs the real fixture CLI with signed policy `promotion=False` and asserts
  exit 3, false expectation, incomplete proof, null release and the exact blocked
  outcome. It failed before the predicate correction and passes now.
- **Root cause:** fixture expectation logic conflated a successful candidate or
  intermediate research disposition with verified release, instead of consuming
  the same certificate/gate/promotion invariants used by communication output.
- **Impact:** CLI smoke tests, automated acceptance jobs and reported M1 evidence
  could claim verified success and exit cleanly while the mandatory promotion
  policy had explicitly blocked release. This exaggerated integration status
  even though no verified artifact was actually published.
- **Whether existing tests detected it:** no. `test_cli_run_fixture` used a
  disabled-promotion policy and asserted `expectation_met` without requiring a
  release certificate, complete proof or release-consistent outcome.
- **Fix performed:** the verified predicate now requires nonnull gates,
  certificate, promoted authorization and complete compiled proof; T2+ truth,
  I2 intent, current event-log verification of both gate attestation and release
  certificate; exact outcome/gate-summary agreement; unblocked release policy;
  and a nonblocking referee result. The positive fixture test now enables
  promotion and asserts `proof_complete`, nonnull release and the exact verified
  outcome.
- **Regression test added:** the negative test above plus the strengthened
  `egmra/tests/test_cli.py::test_cli_run_fixture` positive case.
- **Post-fix verification:**
  `.venv/bin/python -m pytest -q egmra/tests/test_cli.py::test_cli_run_fixture egmra/tests/test_cli.py::test_cli_verified_expectation_requires_actual_release_not_candidate_only`
  returned `2 passed in 0.56s`.
- **Residual limitation:** this verifies the bundled deterministic fixture and
  current local certificate chain only. It does not exercise live models,
  retrieval, Lean, Postgres, distributed control or public release service, and
  therefore cannot establish complete M1/M2 production readiness.
- **Confidence:** high; the false zero exit and null-release state were directly
  reproduced through the CLI and the exact negative/positive paths are covered.

### FBL-032 — Event-integrity CLI ignored the real run binding and crashed on production logs

- **Finding ID:** FBL-032.
- **Severity:** HIGH.
- **Affected F-REQ IDs:** F-REQ-006, F-REQ-116, F-REQ-133,
  F-REQ-153, F-REQ-178, F-REQ-200, F-REQ-203.
- **Specification source:** §2.2 line 212 and §2.6 lines 255-270;
  §10.3 lines 1621-1652; §11.5 lines 1771-1821; §13.2 line
  2014; §13.6 line 2064; §14.5 lines 2172-2188; §15 lines
  2217-2238.
- **Files and line ranges:** `egmra/cli.py:187-196,205-284`;
  `egmra/tests/test_cli.py:169-197`.
- **Symbols:** `cmd_verify_events`, `build_parser`, `main`, `EventLog`,
  `EventLogError`.
- **Expected behavior:** the operational integrity command verifies the exact
  intended run/subject binding in addition to signatures, order, chain and
  Merkle state. A correct production log exits 0 with its run ID and integrity
  result; a wrong-run or corrupted log fails closed with structured nonzero
  output rather than an uncaught traceback.
- **Observed behavior (pre-fix):** `verify-events --events <path>` constructed
  `EventLog` with its hidden default `run_id="run"`. Real CLI logs are bound to
  their problem/run identifier (for example `fx-true-square`), so the shipped
  verifier rejected its own production output. `EventLogError` was absent from
  `main`'s handled error set and escaped as a traceback. Conversely, the command
  offered no explicit expected-subject argument, so a log using the implicit
  default was not verified against an operator-selected run identity.
- **Reproduction command or test:** the audit ran the old
  `egmra verify-events --events <fx-true-square.jsonl>` path against a real
  fixture log and observed run-ID rejection plus an uncaught `EventLogError`.
  The converted regression
  `egmra/tests/test_cli.py::test_cli_verify_events_requires_exact_run_binding_and_fails_closed`
  covers exact-binding success, wrong-run rejection and post-write event
  tampering through the public CLI entry point.
- **Root cause:** the event store's security-critical run ID was left at a
  library convenience default instead of being an explicit CLI input, and the
  top-level structured error boundary did not include the event-log exception.
- **Impact:** operators and automation could not use the documented integrity
  tool on real CLI-generated logs; failures appeared as crashes rather than
  auditable structured denials, and the command did not prove which run the
  caller intended to verify. This weakened operational replay/release evidence.
- **Whether existing tests detected it:** no. Prior CLI tests covered fixtures,
  policy commands and expectation exits but did not run `verify-events` against
  a nondefault run ID, a wrong run or tampered content.
- **Fix performed:** make `--run-id` mandatory; construct `EventLog` with that
  exact expected subject; include `run_id` in successful JSON; and catch
  `EventLogError` in the same structured CLI error path as policy/snapshot/input
  failures.
- **Regression test added:** the single three-phase public-CLI regression named
  above.
- **Post-fix verification:**
  `.venv/bin/python -m pytest -q egmra/tests/test_cli.py::test_cli_verify_events_requires_exact_run_binding_and_fails_closed`
  returned `1 passed in 0.10s`. The current exact-run command exits 0 with
  `integrity=true`; wrong-run and tampered logs exit 2 with JSON
  `error="EventLogError"`.
- **Residual limitation:** the caller must obtain the expected run ID from a
  trusted launch/registry context; the local log plus signed-head pair still has
  no external monotonic anti-rollback witness, and no remote/replicated audit
  service was exercised.
- **Confidence:** high; the incompatibility was reproduced with a real
  CLI-produced log and the exact positive, wrong-subject and corruption paths
  are now covered.

### FBL-033 — Verified fixture expectation accepted a certificate misbound to mutated result identity

- **Finding ID:** FBL-033.
- **Severity:** HIGH.
- **Affected F-REQ IDs:** F-REQ-131, F-REQ-133, F-REQ-134,
  F-REQ-165, F-REQ-203.
- **Specification source:** §11.3 lines 1757-1758; §11.5 lines
  1771-1823; §13.3 line 2034; §15 lines 2217-2238.
- **Files and line ranges:** `egmra/cli.py:68-146`;
  `egmra/tests/test_cli.py:145-210`.
- **Symbols:** `_fixture_expectation_met`, `cmd_run`, `ResearchResult`,
  `ProblemContract`, `ReleaseCertificate`, `EpistemicGraph`.
- **Expected behavior:** a `verified` CLI expectation is true only when every
  current result component describes the same exact run, problem contract,
  replayed supported goal, approved/replayed interpretation, gate digest and
  promotion authorization as a fresh authenticated release certificate. A
  valid certificate from one context cannot authorize a mutated or substituted
  result/contract context.
- **Observed behavior (pre-fix):** after a genuine fixture release was produced,
  a caller could mutate `result.problem_id`, `result.contract.problem_id` and
  `result.contract.source_id` while retaining the authentic certificate and
  original event log. The current contract hash then differed from
  `certificate.problem_contract_hash`, but
  `_fixture_expectation_met("verified", result)` still returned true and the CLI
  reported successful expectation/exit 0. Certificate self-verification alone
  proved the old certificate/log pair, not its binding to the mutated result
  object being reported.
- **Reproduction command or test:**
  `egmra/tests/test_cli.py::test_cli_verified_expectation_rejects_certificate_misbound_to_contract`
  obtains a real locally released fixture result through the production
  `research` path, mutates the result and contract identities without changing
  the certificate, confirms the current contract hash mismatch, and invokes the
  public CLI. The pre-fix predicate accepted it; the corrected CLI exits 3 with
  `expectation_met=false`.
- **Root cause:** the fixture predicate verified selected release objects in
  isolation but did not recompute and compare the complete subject-binding join
  across the mutable result, contract, event replay, claim, interpretation,
  gates, promotion authorization and certificate.
- **Impact:** an authentic release certificate could be replayed as apparent
  success for a different/mutated result context, producing a false verified
  CLI/acceptance signal despite a contract-hash mismatch. This undermined the
  release certificate's subject integrity and exaggerated M1 end-to-end
  correctness.
- **Whether existing tests detected it:** no. The prior FBL-031 regression
  required a nonnull fresh certificate and separately covered missing, forged
  and stale certificates, but no test attached an otherwise authentic current
  certificate to a mutated result/contract identity.
- **Fix performed:** `_fixture_expectation_met` now replays a fresh
  `EpistemicGraph` and requires equality among result, contract and log run IDs;
  exact current contract hash; certificate/compiled goal ID; replayed SUPPORTED
  goal and canonical claim hash; approved contract and replayed interpretation
  IDs/hashes; current gate digest; exact promotion authorization; and verified
  fresh gate/release attestations against the current log. Missing structure or
  replay/binding failure returns false, while forged/stale certificate failures
  remain structured CLI errors.
- **Regression test added:** the contract-misbinding test above and the
  parameterized
  `test_cli_verified_expectation_fails_closed_for_invalid_certificate` covering
  missing, forged and stale certificates.
- **Post-fix verification:**
  `.venv/bin/python -m pytest -q -W error egmra/tests/test_cli.py`
  returned `23 passed in 2.63s`.
- **Residual limitation:** `ResearchResult` and nested contract/release objects
  remain mutable Python objects, so every alternate consumer must perform the
  same complete authenticated join or consume an immutable serialized release
  envelope. This focused fix covers the fixture CLI; no exhaustive API/report
  consumer inventory or live external release service was exercised.
- **Confidence:** high; an authentic certificate/current-contract mismatch was
  directly reproduced and the production predicate now checks each named
  binding plus missing, forged and stale certificate cases.

### FBL-034 — External source adapters disabled or under-enforced TLS/redirect/body boundaries

- **Finding ID:** FBL-034.
- **Severity:** HIGH.
- **Affected F-REQ IDs:** F-REQ-036, F-REQ-080, F-REQ-169, F-REQ-203.
- **Specification source:** §5.2 lines 503-513; §6.1 lines 650-663;
  §8.1 lines 1064-1080; §13.4 lines 2043-2047; §15 lines 2217-2238.
- **Files and line ranges:** `erdos_ingest.py:35,67-153`;
  `fetch_erdos.py:22-53`; `fetch_categories.py:20-53`;
  `sync_problem_catalog.py:11-28`; `egmra/oeis/client.py:18-25,221-299`;
  `tests/test_ingestion_network_security.py:49-162`;
  `egmra/tests/test_adversarial_oeis.py:51-81`.
- **Symbols:** `_require_https_url`, `fetch_url`, `download_yaml`,
  `fetch_latex_source`, `fetch_source`, `_require_oeis_https_url`,
  `_requests_fetcher`, `IngestionNetworkSecurityTests`.
- **Expected behavior:** all source-ingestion entry points use authenticated
  HTTPS with normal certificate verification, reject unsafe schemes and
  embedded credentials before transport, validate every final and redirect
  target before following it, bound redirects and response bytes, and close
  responses on success or failure. Retrieval failure must not silently weaken
  provenance or substitute local-file/custom-scheme content.
- **Observed behavior (pre-fix):** four production `requests.get` calls passed
  `verify=False` while suppressing insecure-request warnings. Two alternate
  `urlopen` paths accepted caller-controlled schemes such as `file:` and
  followed redirects implicitly. Response bodies were not consistently
  bounded or explicitly closed. After those ingestion paths were repaired, the
  equivalent live OEIS adapter was found to follow redirects implicitly and
  read an unbounded `.text` body without final-host validation or explicit
  cleanup. A network attacker could therefore substitute corpus/OEIS bytes,
  and a caller-controlled ingestion URL could reach local/custom handlers.
- **Reproduction command or test:**
  `bandit -q -r -ll --exclude egmra/tests,tests *.py` reported four HIGH B501
  certificate-validation findings and the unsafe `urlopen` paths were confirmed
  by direct scheme probes. The five regressions in
  `tests/test_ingestion_network_security.py` exercise pre-transport scheme
  rejection, default TLS verification, final-URL downgrade rejection,
  redirect-target downgrade rejection, and bounded close-on-error behavior.
  The two OEIS regressions were first run against the prior adapter and returned
  `2 failed`; both now pass after hardening.
- **Root cause:** each ingestion script implemented its own permissive network
  call and treated warning suppression or a URL-shaped string as a sufficient
  transport boundary; there was no shared fail-closed fetch primitive.
- **Impact:** man-in-the-middle source poisoning could corrupt the frozen
  mathematical corpus and its provenance; unsafe schemes could expose local
  files or custom handlers; unbounded bodies could exhaust memory. Retrieved
  bytes are upstream of search, evaluation, and proof work, so compromise could
  misdirect the autonomous pipeline even though retrieval alone cannot promote
  truth.
- **Whether existing tests detected it:** no. Existing ingestion tests mocked
  successful responses and did not assert certificate defaults, schemes,
  redirects, size limits, or cleanup.
- **Fix performed:** centralize legacy ingestion in `erdos_ingest.fetch_url`; require
  HTTPS/no credentials before the first request and for every final/redirect
  URL; preserve Requests' default certificate verification; disable implicit
  redirects and cap validated manual redirects at five; stream with 16 MiB
  catalog/YAML and 4 MiB LaTeX limits; always close responses; and route all
  four ingestion entry points through that primitive. Apply the same default-
  TLS, manual-redirect, final-URL, streaming, cleanup and 4 MiB bounds to the
  live OEIS adapter, additionally restricting redirects to canonical OEIS hosts.
- **Regression test added:** the five adversarial mocked tests in
  `tests/test_ingestion_network_security.py` and two live-adapter boundary tests
  in `egmra/tests/test_adversarial_oeis.py`.
- **Post-fix verification:** the ingestion-focused batch returned `52 passed`;
  the OEIS suite returned `24 passed`; the final full suite returned
  `786 passed, 44 subtests passed`; production
  Bandit at medium/high severity returned no findings. The original
  `verify=False`, warning-suppression, and unsafe-`urlopen` patterns are absent
  from production code; the OEIS adapter no longer uses implicit redirects or
  unbounded `.text` reads.
- **Residual limitation:** no live TLS failure, remote redirect chain,
  rate-limit/retry, OEIS schema drift, or upstream recovery was exercised. The
  legacy shared boundary does not resolve/pin DNS/IP destinations; the OEIS
  adapter restricts canonical hostnames but still depends on deployment DNS and
  egress policy against rebinding or compromised resolution.
- **Confidence:** high for the confirmed local transport defects and mocked
  fail-closed paths; medium for behavior against unexercised live networks.

### FBL-035 — OEIS transform enumeration silently swallowed internal implementation failures

- **Finding ID:** FBL-035.
- **Severity:** LOW.
- **Affected F-REQ IDs:** F-REQ-074, F-REQ-082, F-REQ-083, F-REQ-203.
- **Specification source:** §7.6 lines 936-952; §8.2 lines 1086-1112;
  §15 lines 2217-2238.
- **Files and line ranges:** `egmra/oeis/matching.py:15,114-136`;
  `egmra/oeis/transforms.py:20-21,269-308`;
  `egmra/tests/test_adversarial_oeis.py:84-90`.
- **Symbols:** `enumerate_transform_paths`, `apply_path`, `TransformError`,
  `test_transform_enumeration_does_not_swallow_internal_failures`.
- **Expected behavior:** local enumeration skips only a typed
  `TransformError` that reports a transform-precondition failure. Unexpected
  implementation defects must propagate and fail visibly so an incomplete
  transformed-query set is never mistaken for successful enumeration.
- **Observed behavior (pre-fix):** `enumerate_transform_paths` caught every
  `Exception` around `apply_path` and continued. A `RuntimeError` from an
  internal transform defect was therefore converted into an omitted transform
  path with no error, failure record, or indication that enumeration was
  incomplete.
- **Reproduction command or test:** `egmra/tests/test_adversarial_oeis.py::`
  `test_transform_enumeration_does_not_swallow_internal_failures` monkeypatches
  `matching.apply_path` to raise `RuntimeError("transform implementation defect")`.
  The pre-fix function swallowed that exception and returned paths; after the
  fix the test observes the original `RuntimeError`.
- **Root cause:** a broad `except Exception` fallback conflated expected,
  typed transform-precondition failures with unexpected defects in transform
  implementation or integration code.
- **Impact:** callers could receive an incomplete and misleading set of OEIS
  query transformations while an internal defect remained hidden, reducing
  search coverage and diagnosability. This path only generates OEIS
  conjecture/search inputs, so the defect did not directly promote mathematical
  truth or authorize release.
- **Whether existing tests detected it:** no. Existing transform tests covered
  valid results and expected precondition failures, but none injected an
  unexpected implementation exception through enumeration.
- **Fix performed:** `matching.py` now imports `TransformError` and catches only
  that type; all other exceptions propagate. As defense-in-depth in the same
  hardening pass, optimization-removable invariant assertions in lease,
  checkpoint, blackboard, compute-persistence, and Lean-service paths were
  replaced by explicit typed errors so `python -O` cannot remove those guards;
  this assertion hardening is not a separate confirmed finding.
- **Regression test added:**
  `test_transform_enumeration_does_not_swallow_internal_failures` preserves the
  unexpected-exception propagation contract with a monkeypatched
  `RuntimeError`.
- **Post-fix verification:** the focused OEIS/dependent batch returned
  `167 passed`; EGMRA Ruff and mypy checks were clean, and the production-code
  Bandit scan (excluding test fixtures) reported no medium/high-severity
  findings.
- **Residual limitation:** no live OEIS HTTP request, schema-drift response,
  remote rate-limit recovery, or complete end-to-end external failure campaign
  was exercised. The regression proves the local failure-propagation boundary.
- **Confidence:** high for the local defect and fix: the broad catch is visible
  in the audit-start source, the regression directly reproduces its silent
  omission, and the corrected path catches only the documented precondition
  exception.

## Remediation status conclusion

The canonical index now contains thirty-five findings: ten CRITICAL, twenty-three HIGH,
one MEDIUM, and one LOW. The tested critical local bypasses were closed or made
unreachable on their named paths. That is a substantial safety improvement, not
proof of complete-spec implementation. FBL-002, FBL-004 through FBL-007,
FBL-009 through FBL-014, FBL-017 through FBL-020, FBL-022 through FBL-023,
FBL-025 through FBL-035 retain material architectural, recovery,
race, or external limitations.
The final traceability matrix must therefore leave affected requirements
`PARTIAL`, `BLOCKED-EXTERNAL`, `UNREACHABLE`, or `UNVERIFIED` where the complete
acceptance condition has not run.
