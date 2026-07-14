# Phase 1 normative requirements audit: specification sections 10–16

Scope: this audit was derived only from `docs/AUTONOMOUS_MATH_RESEARCH_ARCHITECTURE_2026.md`, lines 1419–2302. IDs are temporary `S10-…` through `S16-…` identifiers, not final requirement IDs. “Not specified” means the cited source does not define the detail; it is not an inferred waiver. Dependencies name other temporary requirements where the relationship is explicit.

## Section 10 — Shared-state and provenance design

### S10-001 — Persist the Problem entity

- **Source:** §10.1 “Problem and interpretation,” lines 1423–1433.
- **Faithful summary:** Represent each problem with `problem_id`, source versions, hashes of original bytes and Statement IR, status claims, interpretation IDs, and a nullable active interpretation.
- **Category:** implementation; data model; provenance.
- **Inputs/outputs:** Source bytes, source versions, parsed statement, status records, interpretations → durable `Problem` record.
- **Invariants:** Original and normalized-statement identity are hash-bound; active interpretation is either null or references an interpretation associated with the problem.
- **Required failure behavior:** Not specified; invalid/missing references should not be inferred from the schema.
- **Required integrations:** Source ingestion, Statement IR, status subsystem, interpretation store.
- **Observable acceptance:** A serialized problem exposes every listed field and its hashes can be checked against the stored source and Statement IR.
- **Dependencies:** None stated in §§10–16.
- **Ambiguity/contradiction notes:** Field cardinalities, nullability other than `active_interpretation`, schema versioning, and referential-enforcement mechanism are unspecified.

### S10-002 — Persist explicit Interpretation entities

- **Source:** §10.1 “Problem and interpretation,” lines 1435–1447.
- **Faithful summary:** Store each interpretation with its parent problem, normalized statement, binders, hypotheses, conclusion, relation to parent, resolved/open ambiguities, formal candidates, and an intent verdict of pending, approved, or rejected.
- **Category:** implementation; semantic safety; data model.
- **Inputs/outputs:** Problem/source statement and interpretation analysis → version-addressable `Interpretation` record.
- **Invariants:** `relation_to_parent` is one of exact/plausible/stronger/weaker/special_case; intent status remains distinct from truth or formal-proof status.
- **Required failure behavior:** Unresolved intent remains `pending`/open and must not be silently treated as approved.
- **Required integrations:** Problem entity, intent review/certification, formal-candidate generation.
- **Observable acceptance:** Multiple interpretations can coexist for one problem and each exposes the exact listed semantic and verdict fields.
- **Dependencies:** S10-001; S10-007.
- **Ambiguity/contradiction notes:** Approval authority, versioning, and exact transition rules are not defined here.

### S10-003 — Persist multidimensional Claim entities

- **Source:** §10.1 “Claim,” lines 1449–1488.
- **Faithful summary:** Store claims with interpretation binding, canonical formula/hash, informal text, quantifiers, assumptions, scope, independent lifecycle and truth statuses, a five-dimensional evidence profile plus intent/formal-correspondence certificate links, evidence and graph relationships, formal/source/branch/verification links, risk/centrality/spend, version, creator/time, and supersession metadata.
- **Category:** implementation; epistemic state; provenance.
- **Inputs/outputs:** Interpretation, canonicalized proposition, evidence, relations, formal/source artifacts, branch activity → versioned `Claim` record.
- **Invariants:** Lifecycle is ACTIVE/SUPERSEDED/RETRACTED; truth is UNKNOWN/SUPPORTED/REFUTED/CONFLICTED; scope and each evidence dimension remain separately represented; status changes increment or otherwise respect `status_version`.
- **Required failure behavior:** Unsupported or unrecognized evidence may not be collapsed into a generic claim status; malformed enums/references are not admissible.
- **Required integrations:** Evidence store, certificate stores, claim graph, branches, source records, verification system, spend telemetry.
- **Observable acceptance:** A round-trip schema test preserves every listed field and demonstrates independent changes to lifecycle, truth, evidence dimensions, and scope.
- **Dependencies:** S10-002, S10-006–S10-009.
- **Ambiguity/contradiction notes:** Exact rules for `SUPPORTED`, numeric risk/centrality calibration, and optimistic-concurrency semantics are not specified in this schema.

### S10-004 — Keep evidence dimensions and scope independent

- **Source:** §10.1 “Claim,” line 1490.
- **Faithful summary:** Treat numerical, exact-computation, informal-review, formal-verification, external-import, scope, lifecycle, truth, and target-fidelity information as separate dimensions; one type of evidence must not imply another.
- **Category:** security; epistemic invariant; promotion safety.
- **Inputs/outputs:** Evidence of any kind and scope → only the matching evidence-profile dimension and scoped claim consequences.
- **Invariants:** Finite exact computation does not establish a general claim; audited import is not local kernel verification; certificates travel independently.
- **Required failure behavior:** Reject or quarantine any update that promotes unrelated dimensions by inference.
- **Required integrations:** Claim schema, evidence router, promotion logic, release certificates.
- **Observable acceptance:** Tests attach one evidence type and verify no unrelated dimension or broader scope changes.
- **Dependencies:** S10-003, S10-006, S10-011.
- **Ambiguity/contradiction notes:** The cross-dimension promotion matrix is not fully enumerated here.

### S10-005 — Persist Branch entities with budget, debt, failures, and leases

- **Source:** §10.1 “Branch,” lines 1492–1513.
- **Faithful summary:** Represent a research branch with goal claims, interpretation, mechanism fingerprint, assumptions, dependency-cone hash, ancestry/children, lifecycle status, value/cost posteriors, budget spend, verified debt, failure certificates, pause/reopen metadata, and lease.
- **Category:** implementation; orchestration; recovery.
- **Inputs/outputs:** Goals, interpretation, search mechanism, dependencies, controller estimates, worker ownership → durable `Branch` record.
- **Invariants:** Branch status is proposed/active/paused/killed/closed; dependency cone and mechanism are identity-bearing; pause/reopen and lease state remain explicit.
- **Required failure behavior:** Not specified beyond explicit paused/killed states and failure certificates.
- **Required integrations:** Claim graph, controller, budgeting, failure-certificate store, lease service.
- **Observable acceptance:** Branch serialization and lifecycle tests expose all fields and preserve ancestry, budget, failure, and lease data.
- **Dependencies:** S10-003, S10-009, S10-021.
- **Ambiguity/contradiction notes:** Posterior schema, lease schema, and legal state transitions are unspecified.

### S10-006 — Persist typed Evidence entities with replay and diversity provenance

- **Source:** §10.1 “Evidence/artifact,” lines 1515–1539.
- **Faithful summary:** Store evidence IDs, linked claims, a closed kind, assertion scope, artifact hashes, generator identity, verifier identities, diversity profile, environment hash, replay command/result, fidelity certificates, trust assumptions, and creation time.
- **Category:** implementation; provenance; reproducibility; security.
- **Inputs/outputs:** Generated/imported artifact plus producer/checker/replay metadata → typed `Evidence` record.
- **Invariants:** Evidence is claim- and scope-bound; kind is one of the listed values; replay is pass/fail/not_applicable/pending; diversity dimensions are recorded separately.
- **Required failure behavior:** Missing/failed replay or absent identity remains explicit and cannot be represented as success.
- **Required integrations:** Artifact store, replay workers, identity registry, certificate services, claims.
- **Observable acceptance:** Evidence records can be replayed from stored command/environment and retain hashes and all identity/diversity fields.
- **Dependencies:** S10-003, S10-007, S10-008.
- **Ambiguity/contradiction notes:** Closed-kind extensibility and the exact minimum identity fields per kind are not specified here.

### S10-007 — Issue IntentCertificates bound to source and informal claim

- **Source:** §10.1 “Evidence/artifact,” lines 1541–1552.
- **Faithful summary:** An intent certificate binds source bytes, interpretation, and informal-claim hashes; records specified review methods, reviewers and independence/conflicts; and gives APPROVED/REJECTED/UNRESOLVED verdict, version, and time.
- **Category:** semantic security; certification; provenance.
- **Inputs/outputs:** Source, interpretation, informal claim, review evidence → versioned `IntentCertificate`.
- **Invariants:** Certificate identity is hash-bound to all three semantic objects; verdict is closed-valued; reviewer independence/conflicts are retained.
- **Required failure behavior:** Failed or inconclusive review yields REJECTED or UNRESOLVED, never implicit approval.
- **Required integrations:** Interpretation/claim store, review subsystem, release pipeline.
- **Observable acceptance:** Mutating source, interpretation, or informal claim breaks certificate applicability; a valid certificate lists methods and reviewer provenance.
- **Dependencies:** S10-001–S10-003.
- **Ambiguity/contradiction notes:** Required method quorum and reviewer approval threshold are unspecified.

### S10-008 — Issue FormalCorrespondenceCertificates bound to exact Lean type

- **Source:** §10.1 “Evidence/artifact,” lines 1554–1567.
- **Faithful summary:** A formal-correspondence certificate references an intent certificate and binds the informal claim to a Lean declaration, elaborated type hash, notation/definition-map hash, specified semantic tests, reviewer independence/conflicts, verdict, version, and time.
- **Category:** semantic security; formal integration; certification.
- **Inputs/outputs:** Approved/identified intent, informal claim, Lean declaration/type, notation map, review evidence → versioned `FormalCorrespondenceCertificate`.
- **Invariants:** Exact elaborated type and mapping are hash-bound; verdict is APPROVED/REJECTED/UNRESOLVED; formal correspondence is distinct from kernel truth.
- **Required failure behavior:** Mismatch or unresolved review cannot be treated as approved correspondence.
- **Required integrations:** Intent certificates, Lean environment, semantic review, release pipeline.
- **Observable acceptance:** Type or notation-map mutation invalidates applicability; certificate readback names exact declaration and hashes.
- **Dependencies:** S10-007; S10-006.
- **Ambiguity/contradiction notes:** Required method quorum and handling of multiple Lean declarations are unspecified.

### S10-009 — Make semantic graph relations evidence-bearing claims

- **Source:** §10.1, line 1569.
- **Faithful summary:** Support `DEPENDS_ON`, `IMPLIES`, `EQUIVALENT_TO`, `REFUTES`, `SPECIAL_CASE_OF`, `GENERALIZES`, `FORMALIZES`, `IMPORTED_FROM`, `TESTED_BY`, and `SUPERSEDES`; implication/equivalence/generalization/refutation edges must have their own ID, formula/scope, evidence profile, provenance, lifecycle, and revocation behavior rather than being trusted arrows.
- **Category:** implementation; dependency integrity; revocation safety.
- **Inputs/outputs:** Claims plus proposed relations and evidence → typed, versioned relation/edge records.
- **Invariants:** Semantically meaningful edges are auditable mathematical claims and revocable.
- **Required failure behavior:** Bare, unsupported semantic arrows cannot participate as trusted dependencies.
- **Required integrations:** Claim/evidence graph, provenance, lifecycle/revocation engine.
- **Observable acceptance:** Each semantic edge is queryable with the listed metadata and can be invalidated with downstream effects.
- **Dependencies:** S10-003, S10-006, S10-013.
- **Ambiguity/contradiction notes:** Which metadata is required for nonsemantic relations is not stated.

### S10-010 — Admit new claims as unknown and route evidence by kind

- **Source:** §10.2 “Admission and revocation,” lines 1571–1580.
- **Faithful summary:** New claims enter with `truth_status: UNKNOWN` and empty evidence profile. Route source imports to exact-source/hypothesis audit; computation to independent replay/coverage; informal proofs to two-pass logical review; Lean proofs to clean kernel/axiom/target-fidelity validation; counterexamples to exact witness/domain validation; and expert review to authenticated identity/scope recording.
- **Category:** integration; admission safety; evidence validation.
- **Inputs/outputs:** Claim proposal and typed evidence → unknown claim plus kind-specific validation task/result.
- **Invariants:** No proposal begins pre-supported; every listed kind uses its specified validator path.
- **Required failure behavior:** Unknown or invalid routing cannot promote the claim; validator failure leaves evidence unadmitted/failed.
- **Required integrations:** All six validator subsystems, claim store, identity service.
- **Observable acceptance:** Routing tests cover every kind and verify initial empty/UNKNOWN state.
- **Dependencies:** S10-003, S10-006.
- **Ambiguity/contradiction notes:** Routing for evidence kinds listed in the schema but not named here (for example SAT certificates) is not explicit.

### S10-011 — Prohibit generic evidence pass flags

- **Source:** §10.2, line 1582.
- **Faithful summary:** Promotion must satisfy validator-specific obligations; a general `passed=true` field is invalid.
- **Category:** security; promotion gate; schema closure.
- **Inputs/outputs:** Kind-specific validator result and obligations → eligible/ineligible promotion decision.
- **Invariants:** Promotion evidence is semantically typed and cannot be reduced to a boolean.
- **Required failure behavior:** Reject generic boolean-only evidence at every promotion path.
- **Required integrations:** Evidence adapters, validators, promotion service, production entry points.
- **Observable acceptance:** Negative tests show no reachable path from a bare `passed=true` record to claim promotion.
- **Dependencies:** S10-004, S10-010.
- **Ambiguity/contradiction notes:** The complete obligation schema for each kind is defined elsewhere or remains to be specified.

### S10-012 — Quarantine conflicting strong evidence and block dependent promotion

- **Source:** §10.2, line 1584.
- **Faithful summary:** When strong evidence conflicts, mark the claim `CONFLICTED`, quarantine both evidence paths, audit scope/encoding/trusted-computing-base assumptions, never resolve by event-arrival overwrite, and block all dependent promotions.
- **Category:** failure behavior; security; transactional consistency.
- **Inputs/outputs:** Same-claim strong evidence with incompatible conclusions → `CONFLICTED` claim, quarantined paths, audit task, dependent blocks.
- **Invariants:** Arrival order cannot decide truth; both sides and their provenance remain preserved.
- **Required failure behavior:** Fail closed to `CONFLICTED` and quarantine until audit resolution.
- **Required integrations:** Claim graph, evidence store, audit workflow, promotion gate.
- **Observable acceptance:** Inject exact counterexample plus purported kernel proof and observe conflict state, two quarantines, audit event, and blocked dependent promotion.
- **Dependencies:** S10-003, S10-009–S10-011.
- **Ambiguity/contradiction notes:** “Strong evidence” and conflict-resolution exit criteria are not exhaustively defined.

### S10-013 — Separate evidence invalidation from mathematical refutation and propagate transactionally over SCCs

- **Source:** §10.2, lines 1586–1587.
- **Faithful summary:** Losing support downgrades rather than falsifies a claim; refutation is separate. Both changes propagate transactionally using the SCC condensation graph so cycles from equivalence/mutual reductions are handled coherently.
- **Category:** failure behavior; dependency integrity; transaction design.
- **Inputs/outputs:** Evidence invalidation or checked refutation root set → recomputed roots and reverse dependency closure.
- **Invariants:** Support loss is not falsehood; cyclic dependency components update coherently; propagation is transactional.
- **Required failure behavior:** Roll back rather than expose partial propagation; do not mark a claim REFUTED merely because evidence disappeared.
- **Required integrations:** Graph SCC/closure service, transaction store, claim-status recomputation.
- **Observable acceptance:** Cyclic and acyclic injected graphs update atomically with correct downgraded versus refuted statuses.
- **Dependencies:** S10-009, S10-012.
- **Ambiguity/contradiction notes:** Isolation level and exact downgrade lattice are unspecified.

### S10-014 — Implement the specified evidence-invalidation transaction

- **Source:** §10.2 pseudocode, lines 1588–1602.
- **Faithful summary:** In one transaction, mark evidence invalid with reason, recompute directly supported claims, compute reverse dependency closure via SCCs, process components in reverse topological order, recompute dependents, pause publication as needed, reopen relevant branches, append events, commit, and return affected objects.
- **Category:** implementation; revocation; recovery.
- **Inputs/outputs:** `evidence_id`, reason → committed invalidation events and affected claim set.
- **Invariants:** Direct roots precede downstream recomputation; every dependent is processed; publication/branch consequences are included in the same durable transaction.
- **Required failure behavior:** No partial visible update if any step fails; exact rollback mechanism is not specified.
- **Required integrations:** Evidence store, SCC graph, publication controller, branch controller, event log.
- **Observable acceptance:** End-to-end invalidation test verifies event commit, status recomputation order, publication pause, branch reopening, and returned closure.
- **Dependencies:** S10-013, S10-017.
- **Ambiguity/contradiction notes:** Idempotency and behavior for an already-invalid evidence ID are not specified.

### S10-015 — Implement exact-refutation handling

- **Source:** §10.2 pseudocode, lines 1604–1616.
- **Faithful summary:** Validate an exact counterexample or checked negation before opening a transaction; mark `CONFLICTED` if same-scope/encoding strong support survives, otherwise `REFUTED`; compute SCC-aware reverse dependency closure, propagate dependency downgrades, append events, commit, and return affected objects.
- **Category:** implementation; refutation safety; failure behavior.
- **Inputs/outputs:** `claim_id`, exact counterevidence → REFUTED/CONFLICTED state, downstream downgrades, events, affected set.
- **Invariants:** Only validated counterevidence enters the transaction; surviving strong same-scope evidence forces conflict rather than overwrite.
- **Required failure behavior:** Validation failure aborts before state mutation; transactional failure must not expose partial state.
- **Required integrations:** Exact witness/negation checker, graph closure, status service, event log.
- **Observable acceptance:** Tests distinguish invalid witness, clean refutation, and surviving-support conflict cases.
- **Dependencies:** S10-012–S10-014.
- **Ambiguity/contradiction notes:** Strength threshold and “same encoding” comparator are not specified.

### S10-016 — Map corrections to invalidation and replacements to supersession

- **Source:** §10.2, line 1619.
- **Faithful summary:** Imported-theorem corrections, formal-statement changes, and failed computation replays normally invalidate evidence; only exact counterexamples or checked proofs of negation refute. Replacing a statement creates a superseding claim instead of rewriting history.
- **Category:** lifecycle; provenance; failure behavior.
- **Inputs/outputs:** Correction, replay failure, refuting evidence, or replacement statement → invalidation, refutation, or new superseding claim respectively.
- **Invariants:** Historical claim identity is immutable; refutation requires mathematical negative evidence.
- **Required failure behavior:** Do not convert correction/replay failure into REFUTED and do not mutate old claim text in place.
- **Required integrations:** Evidence invalidation/refutation, supersession edges, append-only history.
- **Observable acceptance:** Scenario tests produce the three distinct operations and retain the original claim record.
- **Dependencies:** S10-009, S10-014, S10-015.
- **Ambiguity/contradiction notes:** “Normally” leaves exceptional operation selection undefined.

### S10-017 — Record every state change as a signed append-only event

- **Source:** §10.3 “Append-only audit log,” lines 1621–1650.
- **Faithful summary:** Every state change emits an event carrying event/sequence/run/time, actor type/ID/model/version/prompt hash, action, object IDs, prior/new versions, input/output hashes, run-contract hash, budget delta, reason code/text, and signature.
- **Category:** implementation; audit; security; observability.
- **Inputs/outputs:** Any mutating action plus actor, objects, hashes, budget, reason → ordered signed event.
- **Invariants:** State mutations are event-backed; prior/new versions and artifact hashes make changes traceable; sequence is ordered.
- **Required failure behavior:** A mutation lacking a valid event/signature must not become authoritative; exact signing failure policy is not stated.
- **Required integrations:** All mutating services, identity/model registry, contract store, telemetry, signing service.
- **Observable acceptance:** Mutation coverage tests reconcile materialized changes to complete ordered events and verify signatures/hashes.
- **Dependencies:** S10-003, S10-006, S10-009.
- **Ambiguity/contradiction notes:** Signature algorithm, key management, canonical serialization, and sequence allocation are unspecified here.

### S10-018 — Treat event log and artifact store as authoritative

- **Source:** §10.3, line 1652.
- **Faithful summary:** Dashboards are disposable projections; the event log and artifact store are the source of truth.
- **Category:** architecture; recovery; audit.
- **Inputs/outputs:** Authoritative events/artifacts → reconstructable derived dashboards/materialized views.
- **Invariants:** No dashboard-only state is authoritative.
- **Required failure behavior:** Rebuild or discard inconsistent projections instead of rewriting authoritative history from them.
- **Required integrations:** Event store, artifact store, projection/dashboard builders.
- **Observable acceptance:** Delete/rebuild a dashboard and reproduce the same view from events/artifacts.
- **Dependencies:** S10-017.
- **Ambiguity/contradiction notes:** Artifact-retention and event-compaction policies are unspecified.

### S10-019 — Capture complete resumable checkpoints

- **Source:** §10.4 “Checkpoint and resume,” lines 1654–1667.
- **Faithful summary:** A checkpoint includes last event sequence/Merkle root; problem/source/interpretation hashes; graph view/schema; program archive/AND-OR blueprint; controller state, budgets, seeds; leases; exact model/prompt/tool/environment/dependency/external-service versions; actual per-stage runner/provider/model/context including adjudicator/retrieval policy; caches/replay policies; and rate-limit/quota state.
- **Category:** implementation; provenance; recovery.
- **Inputs/outputs:** Consistent running-system snapshot → durable checkpoint bound to event-chain position.
- **Invariants:** Behavioral identity and operational state are complete enough to test compatibility; checkpoint is hash-bound to authoritative history.
- **Required failure behavior:** Incomplete/incompatible metadata cannot support blind resume or cache reuse.
- **Required integrations:** Event log, graph, controller, identity registry, caches, leases, provider quota manager.
- **Observable acceptance:** Checkpoint readback contains every listed class and validates its Merkle/event binding.
- **Dependencies:** S10-017, S10-018.
- **Ambiguity/contradiction notes:** Checkpoint atomicity boundary, encoding, frequency, and retention are unspecified.

### S10-020 — Resume through integrity and compatibility checks

- **Source:** §10.4, lines 1669–1678.
- **Faithful summary:** Resume must verify event-chain integrity; rebuild state or verify snapshot hash; compare full behavior/import closure to the run contract; invalidate only incompatible caches; recover expired leases atomically; replay high-trust artifacts after formal/tool changes; mark interrupted calls censored without spending math retries; and continue at the highest compatible durable stage.
- **Category:** recovery; security; cache correctness.
- **Inputs/outputs:** Checkpoint, event chain, current environment/contract, interrupted calls → restored compatible state and resumed work.
- **Invariants:** No incompatible cache survives; interrupted operational calls do not consume mathematical retry budget; ownership transfer is atomic.
- **Required failure behavior:** Integrity/compatibility failure must stop unsafe resume and invalidate affected caches/artifacts rather than assume compatibility.
- **Required integrations:** Checkpoint/event stores, contract fingerprinting, cache manager, lease service, replay workers, retry accounting.
- **Observable acceptance:** Fault-injection tests cover all eight ordered steps and resume only the highest compatible stage.
- **Dependencies:** S10-019, S10-021.
- **Ambiguity/contradiction notes:** “High-trust,” compatibility granularity, and handling of unreplayable artifacts are not fully defined.

### S10-021 — Lease workers with heartbeat identity and compatible crash takeover

- **Source:** §10.4, line 1680.
- **Faithful summary:** Workers renew leases with host/PID, branch, stage, and heartbeat; after a grace period a crashed worker loses ownership, and a replacement may reuse only compatible immutable artifacts.
- **Category:** concurrency; recovery; idempotency safety.
- **Inputs/outputs:** Worker identity/activity and lease timing → renewed, expired, or atomically transferred lease.
- **Invariants:** Ownership is lease-bound to work context; mutable or incompatible artifacts are never reused after takeover.
- **Required failure behavior:** Expire crashed ownership after grace and recover without unsafe reuse.
- **Required integrations:** Scheduler, branch store, checkpoint/cache/artifact compatibility checks.
- **Observable acceptance:** Crash test shows lease expiry/takeover, one owner, and only compatible immutable artifact reuse.
- **Dependencies:** S10-005, S10-019, S10-020.
- **Ambiguity/contradiction notes:** Grace duration, renewal interval, fencing token, and non-idempotent action protocol are unspecified here.

### S10-022 — Apply provenance rules to imports, generated/formal artifacts, novelty, reviews, and reasoning

- **Source:** §10.5 “Provenance rules,” lines 1682–1689.
- **Faithful summary:** Imported claims retain immutable bytes/hash, verbatim theorem/hypotheses, source/version/span, correction/publication status, and extraction provenance; generated artifacts retain hash, producer code/prompt/model/tool, inputs, seed, environment; formal artifacts retain theorem/source-tree hashes, imports, toolchain, axiom report, replay; novelty claims retain search log/databases/cutoff/synonyms/access gaps; human reviews retain scope/conflicts; hidden model reasoning is never provenance, only durable artifacts/events are.
- **Category:** provenance; security; audit.
- **Inputs/outputs:** Each import/artifact/novelty assertion/review → complete kind-specific provenance record.
- **Invariants:** Provenance is immutable, explicit, and based on auditable artifacts/events, not hidden reasoning.
- **Required failure behavior:** Missing provenance leaves the relevant import, novelty, review, or formal status unaudited/unresolved.
- **Required integrations:** Source ingest, artifact store, formal replay, retrieval logs, human review, event log.
- **Observable acceptance:** Kind-specific schema tests reject or quarantine records missing any required provenance class and can trace accepted records to bytes/artifacts.
- **Dependencies:** S10-006–S10-008, S10-017, S10-018.
- **Ambiguity/contradiction notes:** Retention periods, privacy redaction, and exact minimum representation of conflicts/access gaps are unspecified.

### S10-023 — Enforce memory-tier promotion and reuse policy

- **Source:** §10.6 “Temporary versus persistent memory,” lines 1691–1701.
- **Faithful summary:** Raw scratch/transcripts may be false, never cross problems, and are never promoted; problem-local episodic memory may contain labeled falsehoods, crosses only as negative/search hints, and expires/quarantines; mechanically verified semantic memory crosses problems only after replay/dependency audit within recorded trust assumptions; audited imports cross as sourced premises after exact audit and per-use applicability/correction checks; procedural memory is only a proposal prior and is rechecked per exact goal; negative memory states falsified scope and requires counterexample/first-error evidence; calibration memory admits no unauthenticated labels and requires exact pipeline/outcome provenance.
- **Category:** security; persistent memory; cross-problem integration.
- **Inputs/outputs:** Candidate memory object, tier, provenance, intended reuse → reject/quarantine/expire or policy-constrained persistent reuse.
- **Invariants:** No unverified semantic claim silently enters cross-problem trusted memory; scope and trust assumptions travel with reused content.
- **Required failure behavior:** Fail closed to quarantine/no cross-problem use when tier proof or provenance is absent.
- **Required integrations:** Memory store, kernel/certificate replay, dependency/source audits, goal checker, calibration pipeline.
- **Observable acceptance:** Policy tests exercise every row of the table, including cross-problem denial, expiry/quarantine, replay, per-use audit, and unauthenticated-label rejection.
- **Dependencies:** S10-004, S10-006, S10-009, S10-022.
- **Ambiguity/contradiction notes:** Expiration duration, quarantine-release process, and definition of “no known false claims” are unspecified.

## Section 11 — Adversarial verification protocol

### S11-001 — Make the referee organizationally independent

- **Source:** §11.1 “Organizational independence,” lines 1705–1714.
- **Faithful summary:** The referee does not see generator hidden scratch; uses fresh contexts and, for high-value claims, a different model family/tool path; is rewarded for valid defects and calibrated abstention rather than acceptance; may demand sources, rerun computation, perturb examples, and formalize suspect steps; cannot repair the proof in the same adjudication pass; and reports to the release auditor rather than the research governor.
- **Category:** security; organizational control; verification.
- **Inputs/outputs:** Candidate proof/evidence bundle → independent defect/abstention/acceptance report and requested checks.
- **Invariants:** Generator and referee incentives, context, authority, and (for high-value work) model/tool path are separated; adjudication and repair are separated.
- **Required failure behavior:** A referee finding uncertainty or defects may abstain/block; it must not self-repair and approve in one pass.
- **Required integrations:** Referee runner, source/compute/formal tools, release auditor, research governor.
- **Observable acceptance:** Trace audit demonstrates context isolation, reporting line, reward target, requested artifacts, and no same-pass repair.
- **Dependencies:** S10-006, S10-017.
- **Ambiguity/contradiction notes:** “High-value,” reward implementation, and minimum different-family evidence are unspecified.

### S11-002 — Record independence as separate evidenced dimensions

- **Source:** §11.1, line 1716.
- **Faithful summary:** A fresh conversation ID is insufficient. Record generator/model diversity, checker/TCB diversity, replay-environment diversity, and human-review independence separately; do not confuse reproducibility in a second environment or model-family diversity with independent mathematical judgment.
- **Category:** provenance; security; evaluation validity.
- **Inputs/outputs:** Generator/checker/environment/reviewer identities and relationships → explicit diversity profile.
- **Invariants:** Independence is never inferred from conversation ID, environment count, or provider/family name alone.
- **Required failure behavior:** Missing or merely correlated evidence cannot be credited as independent review.
- **Required integrations:** Evidence diversity profile, identity registry, replay metadata, reviewer conflict records.
- **Observable acceptance:** Independence scoring tests reject fresh-context-only and environment-only claims while preserving separate reproducibility credit.
- **Dependencies:** S10-006, S10-022, S11-001.
- **Ambiguity/contradiction notes:** Quantitative thresholds for genuine independence are deliberately not defined.

### S11-003 — Perform a target-diff attack

- **Source:** §11.2 “Required attacks,” line 1720.
- **Faithful summary:** Compare original bytes, Statement IR, active interpretation, informal theorem, and Lean declaration.
- **Category:** required verification attack; semantic security.
- **Inputs/outputs:** Five target representations → explicit diff/mismatch report.
- **Invariants:** All five representations are included; no later representation is assumed faithful by construction.
- **Required failure behavior:** Any unresolved material mismatch blocks target-fidelity acceptance.
- **Required integrations:** Source store, Statement IR, interpretation store, informal claim, Lean elaboration.
- **Observable acceptance:** Mutation tests at each representation are detected and localized.
- **Dependencies:** S10-001–S10-003, S10-008.
- **Ambiguity/contradiction notes:** Materiality threshold and canonical diff representation are unspecified.

### S11-004 — Perform a quantifier/domain attack

- **Source:** §11.2, line 1721.
- **Faithful summary:** Audit reordered quantifiers, empty/degenerate domains, constants, asymptotic regimes, regularity, finiteness, and choice assumptions.
- **Category:** required verification attack; semantic safety.
- **Inputs/outputs:** Claim and domain/quantifier specification → audit findings and countercases.
- **Invariants:** Every named semantic dimension is considered.
- **Required failure behavior:** Unresolved quantifier/domain defects block promotion of the affected scope.
- **Required integrations:** Statement IR, boundary probes, exact counterexample search, semantic reviewer.
- **Observable acceptance:** A seeded defect suite across all named dimensions is caught.
- **Dependencies:** S10-002–S10-004.
- **Ambiguity/contradiction notes:** Required depth and exhaustive versus sampled coverage are unspecified.

### S11-005 — Rebuild the dependency trace independently

- **Source:** §11.2, line 1722.
- **Faithful summary:** Independently reconstruct the proof DAG and require every nontrivial step to reference an admitted claim or source.
- **Category:** required verification attack; dependency integrity.
- **Inputs/outputs:** Candidate proof and admitted source/claim graph → independently reconstructed DAG and missing-support defects.
- **Invariants:** No nontrivial unsupported step; reconstruction is independent of rhetorical proof structure.
- **Required failure behavior:** Missing or unadmitted support blocks the dependent conclusion.
- **Required integrations:** Claim graph, source records, independent referee.
- **Observable acceptance:** Injected unsupported steps are reported and taint dependents.
- **Dependencies:** S10-003, S10-009, S11-001.
- **Ambiguity/contradiction notes:** The threshold for “nontrivial” is unspecified.

### S11-006 — Detect circularity including imported target dependence

- **Source:** §11.2, line 1723.
- **Faithful summary:** Detect paths from the conclusion or equivalent reformulations back into premises, including cited/imported results whose proofs depend on the target.
- **Category:** required verification attack; dependency security.
- **Inputs/outputs:** Proof/import dependency graph and equivalence relations → circularity findings.
- **Invariants:** Indirect, reformulated, and imported cycles count as circularity.
- **Required failure behavior:** A detected/unresolved cycle taints and blocks the conclusion.
- **Required integrations:** SCC/dependency graph, semantic equivalence edges, literature provenance.
- **Observable acceptance:** Direct, indirect, equivalent-form, and imported cycles are found in fixtures.
- **Dependencies:** S10-009, S10-013, S10-022.
- **Ambiguity/contradiction notes:** Handling of benign mutual definitions versus proof circularity is unspecified.

### S11-007 — Challenge every cited theorem at source

- **Source:** §11.2, line 1724.
- **Faithful summary:** Open every citation and compare exact hypotheses, version, parameter regime, and notation.
- **Category:** required verification attack; source applicability.
- **Inputs/outputs:** Cited theorem references and local use sites → applicability/version/notation audit.
- **Invariants:** Citation metadata or paraphrase alone is insufficient; every citation is checked against source content.
- **Required failure behavior:** Unavailable/conflicting/mismatched citations remain unresolved and block their dependent use.
- **Required integrations:** Source packet, import auditor, notation map, dependency graph.
- **Observable acceptance:** Tests detect dropped hypotheses, wrong versions, regime errors, and notation mismaps.
- **Dependencies:** S10-022, S11-005.
- **Ambiguity/contradiction notes:** Acceptable handling of inaccessible sources is specified later as unresolved, not here.

### S11-008 — Search for countermodels adversarially

- **Source:** §11.2, line 1725.
- **Faithful summary:** Test smallest exact cases, boundaries, random/adversarial instances, alternate models, and formal negation.
- **Category:** required verification attack; falsification.
- **Inputs/outputs:** Claim/domain and generators/negation → exact witnesses, coverage evidence, or scoped no-witness report.
- **Invariants:** A no-counterexample search is scope-labeled and never itself a general proof.
- **Required failure behavior:** A valid counterexample invokes exact refutation/conflict handling.
- **Required integrations:** Exact computation, generators, formal system, refutation service.
- **Observable acceptance:** Attack suite exercises all five strategies and routes exact witnesses correctly.
- **Dependencies:** S10-004, S10-015.
- **Ambiguity/contradiction notes:** Search budgets and required coverage per claim class are unspecified.

### S11-009 — Independently replay or reimplement computations

- **Source:** §11.2, line 1726.
- **Faithful summary:** Reimplement or replay computations with separate code/environment and compare hashes and coverage.
- **Category:** required verification attack; reproducibility.
- **Inputs/outputs:** Computation artifacts, inputs, claimed coverage → independent results and comparison report.
- **Invariants:** Separate implementation/environment evidence and coverage comparison are explicit; matching output alone is insufficient.
- **Required failure behavior:** Mismatch quarantines computational evidence and removes its support.
- **Required integrations:** Compute sandbox, artifact store, environment identity, evidence invalidation.
- **Observable acceptance:** Independent replay fixtures detect code, hash, and coverage divergence.
- **Dependencies:** S10-006, S10-014, S10-022.
- **Ambiguity/contradiction notes:** How much code independence is required is unspecified.

### S11-010 — Audit formal artifacts in a clean environment

- **Source:** §11.2, line 1727.
- **Faithful summary:** Check clean build, placeholders, axioms, unsafe metaprograms, imports, theorem hash, and semantic correspondence.
- **Category:** required verification attack; formal security.
- **Inputs/outputs:** Formal source/build/target bundle → formal audit and exact accepted/rejected encoded theorem.
- **Invariants:** Kernel success alone does not omit axiom/import/unsafe/semantic checks.
- **Required failure behavior:** Any placeholder, unsafe/unapproved trust path, hash mismatch, or correspondence defect blocks the intended-target certificate.
- **Required integrations:** Pinned Lean farm, axiom/unsafe scanner, import closure, correspondence certificate.
- **Observable acceptance:** Seeded formal defects in every named class fail the audit.
- **Dependencies:** S10-008, S10-022.
- **Ambiguity/contradiction notes:** The approved axiom/unsafe allowlist is not defined in this excerpt.

### S11-011 — Require independent proof reconstruction

- **Source:** §11.2, line 1728.
- **Faithful summary:** A referee writes a concise independent proof skeleton without copying rhetorical transitions.
- **Category:** required verification attack; independent review.
- **Inputs/outputs:** Candidate proof and admitted dependencies → independently authored proof skeleton.
- **Invariants:** Reconstruction demonstrates mathematical dependency understanding rather than stylistic paraphrase.
- **Required failure behavior:** Inability to reconstruct a central argument leaves it unverified at the required informal tier.
- **Required integrations:** Referee subsystem, claim/dependency graph.
- **Observable acceptance:** Review artifact is independently generated and maps steps to admitted dependencies.
- **Dependencies:** S11-001, S11-005.
- **Ambiguity/contradiction notes:** Similarity threshold and minimum skeleton completeness are unspecified.

### S11-012 — Separate novelty/significance audit from proof review

- **Source:** §11.2, line 1729.
- **Faithful summary:** A separate auditor searches prior art and determines whether the result answers the actual question non-vacuously.
- **Category:** required verification attack; organizational separation; evaluation.
- **Inputs/outputs:** Result claim, target, prior-art corpus/search packet → novelty and significance findings.
- **Invariants:** Proof correctness cannot self-establish novelty or responsiveness.
- **Required failure behavior:** Unresolved prior art or vacuity prevents novelty/significance promotion, without negating truth.
- **Required integrations:** Retrieval/search logs, domain auditor, release certificate.
- **Observable acceptance:** Auditor identity is distinct and produces search and non-vacuity evidence.
- **Dependencies:** S10-022, S11-001.
- **Ambiguity/contradiction notes:** Required domain-expert qualifications and corpus coverage thresholds are unspecified.

### S11-013 — Propagate dependency taint until discharged

- **Source:** §11.2, line 1731.
- **Faithful summary:** Propagate circular, unreviewed-import, numerical-only, and semantic-risk labels to every dependent conclusion until the underlying issue is discharged.
- **Category:** dependency integrity; failure behavior.
- **Inputs/outputs:** Tainted node/edge and graph → taint on full dependent closure, later cleared only after discharge.
- **Invariants:** Dependents cannot outrank unresolved supporting risk; taint origin remains traceable.
- **Required failure behavior:** Block affected promotions/releases while taint persists.
- **Required integrations:** Claim graph closure, promotion/release gates, audit workflow.
- **Observable acceptance:** Inject and discharge each taint type and observe correct propagation/removal.
- **Dependencies:** S10-009, S10-013, S11-005–S11-010.
- **Ambiguity/contradiction notes:** Discharge evidence and whether multiple taints clear independently are not fully specified.

### S11-014 — Enforce the T0–T5 truth hierarchy

- **Source:** §11.3 “Verification standards,” lines 1733–1745.
- **Faithful summary:** Allow T0 speculation only as clearly marked hypothesis; T1 supported conjecture only with reproducible scoped tests and counterexample search; T2 finite/conditional result only with exact witness, exhaustive finite coverage, or checked certificate and explicit scope; T3 rigorous informal result only after complete dependency/source audit and, for high-value claims, two genuinely independent hostile reconstructions; T4 only after clean pinned kernel replay, exact expected-type check, transitive axiom/import audit, and no holes, for the encoded statement only; T5 only after T4 plus isolated immutable target module and independent checker/trust path for untrusted generated Lean.
- **Category:** evaluation; promotion; truth certification.
- **Inputs/outputs:** Claim plus scoped evidence/audits/replays → highest justified T-level.
- **Invariants:** Levels are monotone obligation sets; scope remains explicit; T4 says nothing beyond the exact encoding.
- **Required failure behavior:** Assign only the highest fully satisfied level; holes or missing obligations prevent the higher label.
- **Required integrations:** Evidence router, source/dependency audit, independent referees, Lean kernel/checker, target module isolation.
- **Observable acceptance:** Tier conformance suite demonstrates every boundary and rejects one-missing-obligation upgrades.
- **Dependencies:** S10-004, S10-010–S10-012, S11-001–S11-013.
- **Ambiguity/contradiction notes:** “High-value,” exhaustive coverage proof format, and independent trust path threshold are unspecified.

### S11-015 — Report independent release dimensions and their allowed states

- **Source:** §11.3, lines 1746–1755.
- **Faithful summary:** Keep intent fidelity (I0 unresolved, I1 reviewed with caveats, I2 approved hash-binding certificate), formal correspondence (F0/F1/F2 or N/A for informal-only), novelty/status (N0/N1/N2), significance (S0/S1/S2), reproducibility (R0/R1/R2), and autonomy intervention taxonomy/counts independent from truth.
- **Category:** release schema; evaluation; epistemic separation.
- **Inputs/outputs:** Certificates, audits, searches, replays, intervention logs → multidimensional release profile.
- **Invariants:** No dimension implies another; autonomy is phase-specific metadata, not a scalar.
- **Required failure behavior:** Missing evidence stays at unresolved/unreplayed state rather than inheriting truth confidence.
- **Required integrations:** Intent/formal certificates, novelty/significance audits, replay, intervention telemetry.
- **Observable acceptance:** Profile can express mixed states and rejects invalid cross-dimensional shortcuts.
- **Dependencies:** S10-007, S10-008, S10-022, S11-012, S11-014.
- **Ambiguity/contradiction notes:** Exact evidence thresholds for I1/F1/N1/N2/S1/S2 and autonomy categories are only summarized.

### S11-016 — Restrict “Lean-verified” and publication labels

- **Source:** §11.3, line 1757, first two sentences.
- **Faithful summary:** “Lean-verified” is allowed at T4 only for the exact encoded theorem; publication of untrusted generated Lean requires T5.
- **Category:** communication security; release gate.
- **Inputs/outputs:** T4/T5 formal result and trust provenance → permitted label/publication eligibility.
- **Invariants:** T4 label scope is the encoding; untrusted generated code cannot be published as formal evidence below T5.
- **Required failure behavior:** Block broader/intended-target wording or publication when the corresponding obligations are absent.
- **Required integrations:** Formal verifier, communication layer, release gate.
- **Observable acceptance:** Label-policy tests distinguish T4 encoded theorem from T5 publishable formal bundle.
- **Dependencies:** S11-014, S10-008.
- **Ambiguity/contradiction notes:** “Publication” channel and definition of untrusted generation are not further specified.

### S11-017 — Bind intended-statement claims to truth and fidelity certificates

- **Source:** §11.3, line 1757, third and fourth sentences.
- **Faithful summary:** An informal proof establishes the intended statement only with T3+I2; a formal proof only with T5+I2+F2; both require a current status decision.
- **Category:** release; semantic safety; integration.
- **Inputs/outputs:** Truth tier, intent certificate, formal-correspondence certificate where applicable, current status → intended-statement release eligibility.
- **Invariants:** Truth, intent, formal correspondence, and status are conjunctive and remain distinct.
- **Required failure behavior:** Any missing/stale dimension blocks intended-statement release without changing valid narrower evidence.
- **Required integrations:** Truth hierarchy, certificates, status audit, release gate.
- **Observable acceptance:** Truth-table tests reject every incomplete combination and accept only the two specified profiles with current status.
- **Dependencies:** S10-007, S10-008, S11-014–S11-016.
- **Ambiguity/contradiction notes:** The allowed “current status decision” values are not enumerated here.

### S11-018 — Gate “novel autonomous resolution” and never collapse the profile

- **Source:** §11.3, line 1757, final two sentences.
- **Faithful summary:** “Novel autonomous resolution” additionally requires N2, S2, R2, and explicit autonomy metadata; report all dimensions as a profile, never a single V-level.
- **Category:** release; evaluation; communication.
- **Inputs/outputs:** Intended-statement-qualified result plus novelty, significance, reproducibility, autonomy evidence → permitted composite claim and full profile.
- **Invariants:** All requirements are conjunctive; profile dimensions remain visible.
- **Required failure behavior:** Missing any dimension blocks the composite label and cannot be hidden by aggregation.
- **Required integrations:** Release certificate, novelty/significance experts, independent replay, telemetry.
- **Observable acceptance:** Rendering/promotion tests refuse composite claims for N1/S1/R1 or absent autonomy and never emit a collapsed V-level.
- **Dependencies:** S11-015, S11-017.
- **Ambiguity/contradiction notes:** No contradiction; “autonomous” remains taxonomic rather than thresholded.

### S11-019 — Use pessimistic reviewer aggregation

- **Source:** §11.4 “Pessimistic aggregation,” lines 1759–1761.
- **Faithful summary:** Do not average reviewer scores; one valid central defect blocks promotion.
- **Category:** verification policy; failure behavior.
- **Inputs/outputs:** Reviewer findings and defect centrality/validity → blocked or eligible promotion.
- **Invariants:** Central valid defects are vetoes, not diluted scores.
- **Required failure behavior:** Fail closed on a valid central defect.
- **Required integrations:** Review normalization, claim graph centrality, promotion gate.
- **Observable acceptance:** A test with many approvals and one valid central defect remains blocked.
- **Dependencies:** S11-001, S11-013.
- **Ambiguity/contradiction notes:** Defect-validity and centrality adjudication are not fully specified.

### S11-020 — Adjudicate conflicting reviews with a blinded new adjudicator

- **Source:** §11.4, lines 1761–1767.
- **Faithful summary:** Normalize the disputed issue, collect evidence targeted to it, use a new adjudicator blinded to reviewer identities/status, resolve formally or executably where possible, and return `unknown` if conflict persists.
- **Category:** failure behavior; adjudication; organizational security.
- **Inputs/outputs:** Conflicting reviews → normalized issue, targeted evidence, blinded adjudication, resolved result or `unknown`.
- **Invariants:** Adjudicator is new and identity/status-blinded; unresolved conflict never becomes acceptance by majority.
- **Required failure behavior:** Persisting disagreement ends at `unknown`.
- **Required integrations:** Review store, evidence collectors, formal/compute tools, adjudicator runner.
- **Observable acceptance:** Conflict fixture records all five steps and yields `unknown` when executable/formal evidence is inconclusive.
- **Dependencies:** S11-019, S11-001.
- **Ambiguity/contradiction notes:** Retry count and authority to select the new adjudicator are unspecified.

### S11-021 — Do not promote truth from correlated consensus

- **Source:** §11.4, line 1769.
- **Faithful summary:** Consensus among correlated models may increase search priority but must not raise truth tier.
- **Category:** security; controller/evaluation separation.
- **Inputs/outputs:** Correlated model agreement → optional search-priority update, no truth-state update.
- **Invariants:** Heuristic consensus and evidentiary truth are separate.
- **Required failure behavior:** Reject any truth promotion whose only new input is correlated agreement.
- **Required integrations:** Branch controller, identity/diversity profile, truth promotion gate.
- **Observable acceptance:** Consensus changes queue priority while claim T-level and evidence profile stay unchanged.
- **Dependencies:** S11-002, S11-014.
- **Ambiguity/contradiction notes:** Correlation detection and amount of priority change are unspecified.

### S11-022 — Build and sign a complete ReleaseCertificate

- **Source:** §11.5 “Final release certificate,” lines 1771–1821.
- **Faithful summary:** Release bundles bind problem contract, active interpretation, result claim, formal target type, proof bundle, truth certificates/trust policy/axiom report/checkers, intent certificate, formal correspondence, novelty/search packet, significance, reproducibility/environments, phase-specific autonomy/interventions/trace, unresolved risks, and a canonicalized cryptographic signature with signer/key/time.
- **Category:** implementation; release; security; provenance.
- **Inputs/outputs:** All final artifacts, profiles, telemetry, risks, signer → signed `ReleaseCertificate`.
- **Invariants:** Hashes bind exact released objects; dimensions are separate; unresolved risks remain visible; signature records canonicalization, algorithm, identity, key, value, and time.
- **Required failure behavior:** Missing/invalid required fields or signature prevents certified release; unresolved dimensions retain unresolved verdicts.
- **Required integrations:** Contracts, interpretation/claim/proof stores, truth/certificate services, search packet, replay, telemetry, signing service.
- **Observable acceptance:** Schema/signature verification plus hash mutation tests; complete readback of every nested field.
- **Dependencies:** S10-017, S11-014–S11-018.
- **Ambiguity/contradiction notes:** Required versus nullable formal fields for informal-only releases and cryptographic algorithms are unspecified.

### S11-023 — Render release dimensions separately

- **Source:** §11.5, line 1823.
- **Faithful summary:** The communication layer must display release fields separately and never compress them into a self-reported numerical confidence such as 95%.
- **Category:** communication; safety; acceptance.
- **Inputs/outputs:** ReleaseCertificate → dimension-preserving public/internal presentation.
- **Invariants:** No scalar confidence replaces the evidence profile.
- **Required failure behavior:** Reject or flag renderers that omit dimensions or synthesize a confidence percentage.
- **Required integrations:** Release certificate renderer, publication/reporting surfaces.
- **Observable acceptance:** Snapshot/schema tests show separate fields and absence of synthetic confidence.
- **Dependencies:** S11-022.
- **Ambiguity/contradiction notes:** Presentation order and whether calibrated probabilities may appear separately are not specified.

## Section 12 — Evaluation plan

### S12-001 — Evaluate across seven specified difficulty levels

- **Source:** §12.1 “Seven difficulty levels,” lines 1827–1837.
- **Faithful summary:** Use seven levels: (1) elementary/false/ambiguous tasks for parsing and basic formal proof, with exact answer/kernel ground truth; (2) pinned formal olympiad sets for reasoning/autoformalization/retrieval, with versioned statements/proofs; (3) pinned harder Putnam/IMO sets with kernel replay plus human statement audit; (4) fresh literature-dependent tasks with hidden source packet/expert grading; (5) construction/enumeration/finite-reduction tasks with independent executable verifier/proof; (6) cutoff-hidden solved Erdős problems with dated sources/held-out solution; and (7) currently unsolved Erdős problems assessed by blind experts, formal artifacts, and later literature rather than an answer key.
- **Category:** evaluation design; coverage.
- **Inputs/outputs:** Frozen tasks per level and corresponding ground truth/auditors → per-level capability results.
- **Invariants:** Difficulty sets, primary capability, and ground-truth mode remain level-specific; Level 7 has no answer key.
- **Required failure behavior:** Do not substitute an easier ground-truth regime or report Level 7 as ordinary accuracy.
- **Required integrations:** Benchmark/source versioning, Lean replay, executable verifiers, expert review, historical snapshots.
- **Observable acceptance:** Evaluation manifest assigns every task a level and the exact ground-truth mechanism listed for that level.
- **Dependencies:** S11-014–S11-023.
- **Ambiguity/contradiction notes:** Exact dataset versions, sample sizes, and level-assignment rubric are not specified here.

### S12-002 — Separate three Level 2–3 evaluation tracks

- **Source:** §12.1, line 1839.
- **Faithful summary:** Report (A) proof search from an audited supplied Lean statement, (B) natural-language-to-Lean autoformalization with independent semantic grading before proof search, and (C) end-to-end work from raw source; treat a supplied Lean theorem as a versioned target, not unique semantic truth.
- **Category:** evaluation; semantic safety.
- **Inputs/outputs:** Same level tasks under three input regimes → separately reported track results.
- **Invariants:** Results are not pooled across semantic-assistance regimes; track B semantic grading precedes search.
- **Required failure behavior:** Mis-scoped or ungraded autoformalizations cannot be credited as proof-search success for the intended statement.
- **Required integrations:** Benchmark versioning, semantic grader, Lean search, raw-source ingestion.
- **Observable acceptance:** Reports have distinct A/B/C denominators and provenance; supplied targets are versioned.
- **Dependencies:** S12-001, S10-007, S10-008.
- **Ambiguity/contradiction notes:** Whether identical task instances must appear in all tracks is unspecified.

### S12-003 — Keep training corpora and capability trackers out of held-out proof gold

- **Source:** §12.1, line 1841.
- **Faithful summary:** Do not treat Lean Workbook-style training/retrieval corpora as held-out gold; use rotating formalization sets only with exact toolchain and semantic audits; use FrontierMath-like benchmarks as capability trackers, not proof substitutes; provenance-version benchmark corrections.
- **Category:** evaluation validity; provenance.
- **Inputs/outputs:** Candidate corpus/benchmark and version history → classified evaluation role and versioned provenance.
- **Invariants:** Training/retrieval exposure disqualifies held-out-gold status; benchmark corrections remain traceable.
- **Required failure behavior:** Reclassify/qualify contaminated or corrected benchmarks and rerun where policy later requires.
- **Required integrations:** Dataset registry, contamination audit, toolchain/semantic audit, provenance store.
- **Observable acceptance:** Evaluation manifests label corpus role and exact benchmark version/corrections.
- **Dependencies:** S10-022, S12-001.
- **Ambiguity/contradiction notes:** The named resources are examples and may drift; minimum semantic-audit protocol is unspecified.

### S12-004 — Freeze the complete evaluation contract for every level

- **Source:** §12.2 “Protocol,” lines 1843–1847.
- **Faithful summary:** Before each level, freeze problem bytes, status, toolchain, library commit, models, prompts, tools, budgets, network policy, and rubric.
- **Category:** evaluation; reproducibility; contract security.
- **Inputs/outputs:** Evaluation campaign configuration → immutable versioned evaluation contract.
- **Invariants:** All listed behavior-affecting inputs are fixed and provenance-bound before runs.
- **Required failure behavior:** Runs outside the frozen contract are incompatible and must be separated or rerun.
- **Required integrations:** Run contracts, source/status snapshots, model/tool registries, budget/network controls, rubric registry.
- **Observable acceptance:** Campaign manifest hashes every listed component and detects mutation.
- **Dependencies:** S10-017, S10-019, S12-001.
- **Ambiguity/contradiction notes:** Freeze timing and allowed emergency corrections are unspecified.

### S12-005 — Audit de-duplication against training/retrieval sources

- **Source:** §12.2, line 1848.
- **Faithful summary:** De-duplicate evaluation problems against training and retrieval sources as far as auditable.
- **Category:** evaluation validity; contamination control.
- **Inputs/outputs:** Evaluation set and known corpora → de-duplication/contamination report.
- **Invariants:** Residual uncertainty is disclosed rather than treated as absence of contamination.
- **Required failure behavior:** Detected duplicates must be flagged/handled, not silently retained as clean held-out cases.
- **Required integrations:** Corpus indexes, retrieval logs, evaluation manifest.
- **Observable acceptance:** Each task has a de-duplication result and documented coverage/gaps.
- **Dependencies:** S12-003, S12-004.
- **Ambiguity/contradiction notes:** Match method and exclusion threshold are unspecified.

### S12-006 — Run four minimum baselines/system conditions

- **Source:** §12.2, lines 1849–1853.
- **Faithful summary:** At minimum run a raw strongest-model-with-tools baseline, raw open/local-model baseline, current repository pipeline, and EGMRA full system.
- **Category:** evaluation; baseline integration.
- **Inputs/outputs:** Frozen evaluation tasks and four systems → comparable result sets.
- **Invariants:** All four named conditions appear; “raw” baselines remain distinguishable from orchestration.
- **Required failure behavior:** Do not claim system gain if required baselines are absent.
- **Required integrations:** Model gateway, current pipeline, EGMRA, common evaluator/telemetry.
- **Observable acceptance:** Report includes matched denominators and contracts for all four conditions.
- **Dependencies:** S12-004.
- **Ambiguity/contradiction notes:** Exact raw baseline prompt/tool wrapper is not specified.

### S12-007 — Match total cost or report a verified-progress Pareto curve

- **Source:** §12.2, line 1854.
- **Faithful summary:** Equalize total cost across comparisons or report verified progress versus cost as a Pareto curve.
- **Category:** evaluation; efficiency fairness.
- **Inputs/outputs:** Verified outcomes and complete costs → matched-cost comparison or Pareto frontier.
- **Invariants:** Cost-blind comparisons are not valid system-effect evidence.
- **Required failure behavior:** With unmatched costs, suppress scalar “beats baseline” claims and use the Pareto presentation.
- **Required integrations:** Cost telemetry, verified-progress scoring, baseline runner.
- **Observable acceptance:** Each comparison documents matching or plots frontier with exact cost units.
- **Dependencies:** S12-006, S13-011.
- **Ambiguity/contradiction notes:** Cost aggregation across dollars, compute, and expert time is not specified.

### S12-008 — Preserve failure-complete execution records

- **Source:** §12.2, line 1855.
- **Faithful summary:** Preserve successes, failures, rate limits, timeouts, human interventions, and discarded branches.
- **Category:** evaluation; audit; failure observability.
- **Inputs/outputs:** Every run event/outcome → complete durable evaluation log.
- **Invariants:** Selection does not erase failed/censored/discarded work.
- **Required failure behavior:** Missing events make the run incomplete for aggregate evaluation rather than being treated as success-only data.
- **Required integrations:** Append-only events, branch store, provider telemetry, intervention taxonomy.
- **Observable acceptance:** Log reconciliation accounts for every scheduled attempt and terminal/censored disposition.
- **Dependencies:** S10-017, S10-018.
- **Ambiguity/contradiction notes:** Retention and privacy filtering are deferred to §12.6.

### S12-009 — Grade formal and informal artifacts with different evidence paths

- **Source:** §12.2, line 1856.
- **Faithful summary:** Grade formal artifacts through clean replay and informal artifacts through blinded domain experts.
- **Category:** evaluation; validation integration.
- **Inputs/outputs:** Formal or informal artifact → replay result or blinded expert grade.
- **Invariants:** Model self-grades and nonclean formal builds are insufficient.
- **Required failure behavior:** Replay failure or unresolved expert review prevents positive grading.
- **Required integrations:** Clean replay workers, expert-review portal, identity/blinding controls.
- **Observable acceptance:** Every graded artifact carries the correct path’s verifier/reviewer provenance.
- **Dependencies:** S11-001, S11-010, S11-014.
- **Ambiguity/contradiction notes:** Expert grading scale and number of experts are specified later only for high-value claims.

### S12-010 — Separate novelty/status graders from proof graders

- **Source:** §12.2, line 1857.
- **Faithful summary:** Novelty/status assessment must be performed separately from proof grading.
- **Category:** organizational security; evaluation.
- **Inputs/outputs:** Result bundle → independently produced truth/proof grade and novelty/status grade.
- **Invariants:** Correctness does not influence novelty judgment by shared grader role.
- **Required failure behavior:** Combined/unseparated grading cannot support the independent release dimensions.
- **Required integrations:** Proof evaluator, novelty/status auditor, identity records.
- **Observable acceptance:** Reviewer-role audit shows disjoint assignments or explicit independence controls.
- **Dependencies:** S11-012, S11-015.
- **Ambiguity/contradiction notes:** Whether one human may serve both roles in separate blinded phases is unspecified.

### S12-011 — Analyze calibration and false success before aggregate publication

- **Source:** §12.2, line 1858.
- **Faithful summary:** Run calibration and false-success analysis before publishing aggregate performance.
- **Category:** evaluation gate; safety.
- **Inputs/outputs:** Predictions, outcomes, censoring, promotions → calibration and false-success report preceding aggregate release.
- **Invariants:** Aggregate performance cannot precede these safety analyses.
- **Required failure behavior:** Withhold/qualify aggregate publication when analysis is missing or indicates uncontrolled false promotion.
- **Required integrations:** Calibration ledger, evaluation outcomes, release/reporting pipeline.
- **Observable acceptance:** Publication bundle timestamps/depends on completed analyses.
- **Dependencies:** S10-023, S12-008.
- **Ambiguity/contradiction notes:** Quantitative publication thresholds are unspecified.

### S12-012 — Run controlled causal orchestration ablations

- **Source:** §12.2, line 1860, first two sentences.
- **Faithful summary:** For causal ablations, hold model versions, prompts, tool entitlements, retrieval snapshots, network access, wall-time/cost ceilings, seeds where available, and evaluator policy fixed; change only the architectural component under test.
- **Category:** evaluation; causal inference.
- **Inputs/outputs:** Frozen base contract and one component toggle → matched ablation results.
- **Invariants:** Exactly one architectural factor changes; listed confounders remain fixed.
- **Required failure behavior:** Treat a run with other changes as noncausal/incomparable.
- **Required integrations:** Contract fingerprinting, experiment runner, evaluator, telemetry.
- **Observable acceptance:** Automated contract diff identifies only the registered component change.
- **Dependencies:** S12-004, S12-007.
- **Ambiguity/contradiction notes:** Seeds need be fixed only where available; acceptable nondeterminism is not quantified.

### S12-013 — Report best-available-system comparisons separately

- **Source:** §12.2, line 1860, final two sentences.
- **Faithful summary:** When EGMRA receives stronger models, larger budgets, or more tools, report a separate best-available comparison and interpret it as deployment capability, not causal orchestration value.
- **Category:** evaluation; reporting integrity.
- **Inputs/outputs:** Unequal-capability runs → separately labeled deployment comparison.
- **Invariants:** Such results are never mixed with controlled ablation estimates.
- **Required failure behavior:** Reject causal architecture claims based only on unequal-capability comparisons.
- **Required integrations:** Evaluation report, contract diff, baseline registry.
- **Observable acceptance:** Report sections and labels distinguish causal and deployment comparisons.
- **Dependencies:** S12-012.
- **Ambiguity/contradiction notes:** No required normalization for the deployment comparison is stated beyond separate reporting.

### S12-014 — Construct Level 6 time-capsule evaluations

- **Source:** §12.2, lines 1862–1868.
- **Faithful summary:** Select Erdős problems open at cutoff `t` and solved later; hide all post-`t` sources and the solution; audit training contamination separately; score rediscovery, alternative proof, useful lemmas, and status mistakes; compare output to later literature for novelty leakage.
- **Category:** evaluation; historical contamination control.
- **Inputs/outputs:** Dated source snapshot, held-out later solution/literature, run outputs → scoped Level 6 scores and leakage audit.
- **Invariants:** Runtime access is cutoff-bounded; unknowable training contamination is disclosed, not assumed absent.
- **Required failure behavior:** Post-cutoff leakage invalidates/qualifies the affected evaluation.
- **Required integrations:** Frozen retrieval packet, network policy, status snapshot, later-literature auditor.
- **Observable acceptance:** Access audit shows no post-cutoff sources and scoring includes all named outcome classes.
- **Dependencies:** S12-001, S12-004, S12-005.
- **Ambiguity/contradiction notes:** Cutoff selection, number of cases, and leakage severity policy are unspecified.

### S12-015 — Score Level 7 only by externally verified contribution

- **Source:** §12.2, line 1870.
- **Faithful summary:** Never report Level 7 “accuracy”; record externally verified contributions, open-subgoal movement, counterexamples, finite reductions, formal libraries, and well-supported no-result reports; never count a result from the system’s own declaration.
- **Category:** evaluation; communication safety.
- **Inputs/outputs:** Unsolved-problem run and external evidence → contribution ledger, not accuracy/solve rate.
- **Invariants:** Self-attestation has zero outcome authority.
- **Required failure behavior:** Unverified declarations are excluded; inconclusive work may be recorded as a supported no-result.
- **Required integrations:** External referees, formal/executable verifiers, claim graph progress metrics.
- **Observable acceptance:** Level 7 reports contain no accuracy field and every counted contribution links external evidence.
- **Dependencies:** S12-001, S11-017–S11-023.
- **Ambiguity/contradiction notes:** “Externally verified” and subgoal-movement scoring weights are not quantified.

### S12-016 — Measure final outcomes including false successes

- **Source:** §12.3 “Final outcomes,” lines 1872–1879.
- **Faithful summary:** Count exact full proofs/disproofs meeting T3+I2 or T5+I2+F2 plus required novelty/significance/replay; detection of false/ambiguous/misquoted/already-solved tasks; correct abstention/no-result on labeled Levels 1–6 (Level 7 only current calibrated belief/evidence); and incorrect “solved” declarations prominently, never averaged away.
- **Category:** evaluation metrics; safety.
- **Inputs/outputs:** Verified releases and labeled outcomes → final-outcome metric table.
- **Invariants:** Qualification profile is conjunctive; false-solved count remains separately prominent.
- **Required failure behavior:** Do not score unsupported solves or force definitive Level 7 classifications.
- **Required integrations:** Release certificates, labeled datasets, status/ambiguity auditors, calibration.
- **Observable acceptance:** Metric schema includes every named outcome and preserves false solves as a top-level measure.
- **Dependencies:** S11-017, S11-018, S12-015.
- **Ambiguity/contradiction notes:** Exact required novelty/significance/replay profile varies by claim and is not restated here.

### S12-017 — Measure durable intermediate mathematical progress

- **Source:** §12.3 “Intermediate mathematical progress,” lines 1881–1888.
- **Faithful summary:** Measure number/centrality of newly verified lemmas, useful counterexamples/killed conjectures, verified proof-debt reduction, reusable formal/computational infrastructure, independently confirmed literature/status corrections, and closed-subgoal/dependent-path percentages.
- **Category:** evaluation metrics; progress.
- **Inputs/outputs:** Verified claim graph and artifacts before/after run → intermediate-progress metrics.
- **Invariants:** Only verified/audited objects contribute; centrality and downstream effects remain visible.
- **Required failure behavior:** Exclude unverified candidates and unconfirmed corrections.
- **Required integrations:** Claim graph, proof-debt model, artifact reuse registry, source audit.
- **Observable acceptance:** Metric values trace to durable object IDs and graph deltas.
- **Dependencies:** S10-003, S10-009, S12-023.
- **Ambiguity/contradiction notes:** Centrality and proof-debt formulas are not fully defined.

### S12-018 — Compute risk-weighted formal coverage as specified

- **Source:** §12.3 “Rigor and dependency integrity,” lines 1890–1900.
- **Faithful summary:** Compute RFC as the sum of `w_c` for adequately verified proof claims divided by total proof weights, where `w_c = centrality × semanticRisk × downstreamLoss`.
- **Category:** evaluation metric; rigor.
- **Inputs/outputs:** Proof-claim set, verification indicator, centrality, semantic risk, downstream loss → RFC.
- **Invariants:** Numerator and denominator use the same frozen claim set/weights; zero or invalid denominators require explicit handling.
- **Required failure behavior:** Do not report RFC from missing weights or an unaudited proof set.
- **Required integrations:** Claim graph, risk/centrality estimators, verification profiles.
- **Observable acceptance:** Reproducible calculation matches the stated formula on fixtures.
- **Dependencies:** S10-003, S11-014.
- **Ambiguity/contradiction notes:** “Adequately verified,” weight normalization, zero weights, and downstream-loss computation are unspecified.

### S12-019 — Freeze an independently audited blueprint and weights before scoring

- **Source:** §12.3, line 1902.
- **Faithful summary:** Before RFC or subgoal-closure scoring, freeze an independently audited proof blueprint and weights to prevent replacing a hard target with many easy nodes or hiding difficulty in helpers.
- **Category:** evaluation security; anti-gaming.
- **Inputs/outputs:** Proposed blueprint/weights and independent audit → immutable scoring baseline.
- **Invariants:** The system being scored cannot retrospectively redefine denominator, nodes, or core difficulty.
- **Required failure behavior:** Reject/re-audit scores after material blueprint/weight mutation.
- **Required integrations:** AND/OR blueprint, independent auditor, contract/hash store, metric engine.
- **Observable acceptance:** Post-freeze graph gaming attempts invalidate the score or trigger a new preregistered baseline.
- **Dependencies:** S12-018, S10-017.
- **Ambiguity/contradiction notes:** Allowed refinements and auditor independence threshold are unspecified.

### S12-020 — Measure dependency and replay integrity

- **Source:** §12.3, lines 1904–1911.
- **Faithful summary:** Measure raw claim percentages along every evidence-profile dimension, independently audited dependency-edge correctness, citation/hypothesis applicability, revocation precision/recall on injected false lemmas, formal/informal correspondence, and clean replay rate across independent environments.
- **Category:** evaluation metrics; security.
- **Inputs/outputs:** Claims, graph audits, injected-fault results, certificates, replay runs → integrity metric suite.
- **Invariants:** Evidence dimensions are reported separately; audits/replays are independent where stated.
- **Required failure behavior:** Missing audit/replay data remains missing and cannot be imputed as pass.
- **Required integrations:** Evidence profile, graph/source auditors, fault injector, correspondence certificates, replay farm.
- **Observable acceptance:** Report includes all six metric families with exact denominators.
- **Dependencies:** S10-004, S10-013, S11-002, S11-013.
- **Ambiguity/contradiction notes:** Sampling and confidence intervals are specified generally later, not per metric.

### S12-021 — Measure search quality rather than agent count

- **Source:** §12.3 “Search quality,” lines 1913–1922.
- **Faithful summary:** Measure mechanism-family coverage, fingerprint/behavioral diversity, semantic duplicate rate, repeated-error rate/time-to-stop, counterexample rate, useful-branch budget fraction, reopened-branch success, and verification backlog/congestion.
- **Category:** evaluation metrics; orchestration.
- **Inputs/outputs:** Branch/program/archive/event data → search-quality metric suite.
- **Invariants:** Unique mechanisms, not nominal agents, define coverage; usefulness is outcome-backed.
- **Required failure behavior:** Do not credit duplicated agents as diversity or hide repeated failures/backlog.
- **Required integrations:** Mechanism fingerprints, semantic dedup, branch controller, failure certificates, verifier queues.
- **Observable acceptance:** Each metric traces to branch/event IDs and distinguishes nominal versus behavioral diversity.
- **Dependencies:** S10-005, S10-017.
- **Ambiguity/contradiction notes:** Similarity thresholds and “eventually useful” window are unspecified.

### S12-022 — Measure verified efficiency and its Pareto frontier

- **Source:** §12.3 “Efficiency,” lines 1924–1931.
- **Faithful summary:** Measure cost/tokens/wall time/deterministic compute/expert hours per verified lemma; cost per central proof-debt unit; time to first counterexample/admitted lemma/final certificate; compatible cache hit rate; orchestration gain over raw baseline; and verified-progress Pareto frontier, not a cost-blind solve rate.
- **Category:** evaluation metrics; efficiency.
- **Inputs/outputs:** Complete telemetry and verified milestones → efficiency metrics/frontier.
- **Invariants:** Denominators are verified objects; cache hits require compatibility.
- **Required failure behavior:** Censored/missing costs are reported rather than omitted; no cost-blind headline.
- **Required integrations:** Telemetry, proof-debt graph, cache provenance, baselines, certificates.
- **Observable acceptance:** Metric report supplies exact units/denominators and reconstructable milestone timestamps.
- **Dependencies:** S12-007, S12-008, S12-017.
- **Ambiguity/contradiction notes:** Multi-resource cost conversion remains unspecified.

### S12-023 — Evaluate posterior calibration including censoring and false promotion

- **Source:** §12.3 “Calibration,” lines 1933–1942.
- **Faithful summary:** For problem and branch posteriors report Brier/log scores, expected calibration error/reliability diagrams, credible-interval coverage, calibration under censoring, abstention/selective-risk curve, and false-promotion probability with confidence bounds.
- **Category:** evaluation metrics; calibration; safety.
- **Inputs/outputs:** Timestamped posterior distributions, outcomes/censoring, promotion events → calibration suite.
- **Invariants:** Calibration is assessed at problem and branch levels; censored data and uncertainty bounds remain explicit.
- **Required failure behavior:** Do not treat censored outcomes as ordinary failures/successes or report point false-promotion rates without bounds.
- **Required integrations:** Controller posteriors, calibration ledger, event/outcome telemetry, statistical engine.
- **Observable acceptance:** Reproducible report contains every named statistic/plot and exact sample counts.
- **Dependencies:** S10-005, S10-023, S12-008.
- **Ambiguity/contradiction notes:** Binning, censoring model, and confidence method are unspecified.

### S12-024 — Count progress only when a durable qualifying object is created

- **Source:** §12.4 “Distinguishing progress from verbose output,” lines 1944–1954.
- **Faithful summary:** Research progress requires at least one admitted claim with new evidence, exact counterexample, verified reduction/equivalence, reproducible experiment crossing a preregistered evidence/update threshold or killing a branch, audited prior-art/status correction, reusable formal/computational component, or failure certificate preventing a defined repeated error.
- **Category:** acceptance; evaluation; anti-gaming.
- **Inputs/outputs:** Run artifacts/events → binary/countable progress objects.
- **Invariants:** At least one listed durable object is necessary; experiment thresholds are preregistered.
- **Required failure behavior:** Runs producing none are no-progress regardless of volume.
- **Required integrations:** Claim/evidence graph, exact computation, experiment registry, source audit, artifact store, failure certificates.
- **Observable acceptance:** Every credited unit links to a durable object ID satisfying one listed predicate.
- **Dependencies:** S10-003, S10-006, S10-009, S12-019.
- **Ambiguity/contradiction notes:** Reusability and “prevents” criteria require operational definitions.

### S12-025 — Assign zero direct progress value to verbosity proxies

- **Source:** §12.4, line 1956.
- **Faithful summary:** Token count, agent count, candidate-lemma count, self-rated completeness, reviewer consensus, and polished exposition have zero direct progress value; an unverified long manuscript ranks below an exact counterexample.
- **Category:** evaluation security; anti-gaming.
- **Inputs/outputs:** Non-evidentiary output metrics → no direct progress credit.
- **Invariants:** Presentation/volume proxies cannot substitute for durable verified evidence.
- **Required failure behavior:** Reject scoring formulas that give these proxies positive direct progress weight.
- **Required integrations:** Metric engine, reporting layer, durable-object ledger.
- **Observable acceptance:** Adding verbosity without durable objects leaves progress score unchanged.
- **Dependencies:** S12-024.
- **Ambiguity/contradiction notes:** These signals may still affect operational cost or search diagnostics; only direct progress value is prohibited.

### S12-026 — Run the complete required ablation suite

- **Source:** §12.5 “Required ablations,” lines 1958–1974.
- **Faithful summary:** Run factorial or staged comparisons for literature (none/cold/two-pass), OEIS (none/structured), memory (transcript/claim graph/graph+revocation), scouts versus tool-differentiated archive, fixed revisions versus dynamic controller, late formalization versus risk-weighted sentinels, same-model versus different-family/tool referee, no computation versus executable falsification, protected exploration at none/10%/20%/adaptive, multiplicative heuristic versus posterior utility, no versus verified-only expert iteration, single versus routed model portfolio, and orchestration versus equal-cost raw model.
- **Category:** evaluation; integration; causal ablation.
- **Inputs/outputs:** Frozen tasks and each enumerated treatment set → ablation effects with costs/verified progress.
- **Invariants:** Every named factor/level is represented; causal controls follow S12-012.
- **Required failure behavior:** Missing treatments preclude claims about that component; no cherry-picking unregistered comparisons.
- **Required integrations:** Retrieval/OEIS/memory/branch/formal/referee/compute/exploration/expert/model-routing subsystems and experiment runner.
- **Observable acceptance:** Preregistered matrix maps completed runs and results to all 13 named ablation families.
- **Dependencies:** S12-012, S12-013.
- **Ambiguity/contradiction notes:** Factorial versus staged choice, interaction coverage, and sample size are unspecified.

### S12-027 — Preregister primary metrics and stop conditions

- **Source:** §12.5, line 1976.
- **Faithful summary:** Register primary metrics and stopping rules before ablations to prevent architectural overfitting to a small set.
- **Category:** evaluation security; experimental governance.
- **Inputs/outputs:** Experiment hypothesis/design → immutable preregistration before outcomes.
- **Invariants:** Primary endpoints and termination cannot be selected after observing results.
- **Required failure behavior:** Deviations are labeled exploratory and cannot support preregistered claims without disclosure.
- **Required integrations:** Experiment registry, run contract, reporting pipeline.
- **Observable acceptance:** Timestamped preregistration predates runs and report reconciles deviations.
- **Dependencies:** S12-012, S12-026.
- **Ambiguity/contradiction notes:** Registration venue and amendment policy are unspecified.

### S12-028 — Report exact denominators, intervals, budgets, and censoring

- **Source:** §12.6 “Statistical policy,” line 1980.
- **Faithful summary:** Every statistical report includes exact denominators, uncertainty intervals, budgets, and censored runs.
- **Category:** evaluation; statistical reporting.
- **Inputs/outputs:** Run-level outcomes/costs/censoring → complete aggregate statistics.
- **Invariants:** No hidden denominator or silently dropped censoring.
- **Required failure behavior:** Incomplete statistics are not publication-ready.
- **Required integrations:** Telemetry, outcome ledger, statistical engine.
- **Observable acceptance:** Report-schema validation requires all four fields for every aggregate.
- **Dependencies:** S12-008, S12-023.
- **Ambiguity/contradiction notes:** Interval type/confidence level is unspecified.

### S12-029 — Pair problems and seeds where possible

- **Source:** §12.6, line 1981.
- **Faithful summary:** Prefer paired problem instances and seeds across compared conditions.
- **Category:** evaluation; statistical design.
- **Inputs/outputs:** Comparison conditions and task/seed schedule → paired observations where feasible.
- **Invariants:** Unpaired cases are disclosed rather than presented as paired.
- **Required failure behavior:** Not specified; infeasibility is allowed by “where possible.”
- **Required integrations:** Experiment scheduler, seed registry.
- **Observable acceptance:** Pairing rate and unmatched cases are reported.
- **Dependencies:** S12-004, S12-012.
- **Ambiguity/contradiction notes:** Criteria for infeasibility and analysis of partial pairing are unspecified.

### S12-030 — Never compare unmatched pass@k or token/tool budgets

- **Source:** §12.6, line 1982.
- **Faithful summary:** Do not compare pass@1 to pass@32/1024 or systems with unmatched token/tool budgets as if equivalent.
- **Category:** evaluation safety; fairness.
- **Inputs/outputs:** Candidate comparison contracts → valid matched comparison or rejection/separate Pareto report.
- **Invariants:** Sampling multiplicity and resource entitlements are comparison-critical.
- **Required failure behavior:** Reject/qualify unmatched comparisons.
- **Required integrations:** Contract diff, budget telemetry, report validator.
- **Observable acceptance:** Automated comparison guard detects pass@k and token/tool mismatch.
- **Dependencies:** S12-007, S12-012.
- **Ambiguity/contradiction notes:** A Pareto comparison may still be possible but is not restated on this line.

### S12-031 — Separate development and sealed source packets

- **Source:** §12.6, line 1983.
- **Faithful summary:** Keep development source packets distinct from sealed evaluation packets.
- **Category:** security; evaluation contamination control.
- **Inputs/outputs:** Source corpus and campaign phase → access-controlled development or sealed packet.
- **Invariants:** Sealed packet contents do not enter development/retrieval context before evaluation.
- **Required failure behavior:** Leakage invalidates or qualifies affected sealed results.
- **Required integrations:** Artifact/access store, retrieval policy, evaluation contracts, audit log.
- **Observable acceptance:** Access logs and hashes demonstrate separation and detect cross-packet reads.
- **Dependencies:** S12-004, S12-014.
- **Ambiguity/contradiction notes:** Access-control model and leak-remediation threshold are unspecified.

### S12-032 — Version benchmarks and rerun after corrections

- **Source:** §12.6, line 1984.
- **Faithful summary:** Version every benchmark and rerun after statement or toolchain corrections.
- **Category:** provenance; evaluation maintenance.
- **Inputs/outputs:** Benchmark/toolchain correction → new version and rerun results.
- **Invariants:** Results remain bound to exact benchmark and toolchain versions.
- **Required failure behavior:** Supersede/qualify stale results rather than silently rewriting them.
- **Required integrations:** Benchmark registry, run contracts, scheduler, append-only results.
- **Observable acceptance:** Correction creates a new version and linked rerun while preserving old records.
- **Dependencies:** S10-016, S12-003, S12-004.
- **Ambiguity/contradiction notes:** Scope of reruns for partial corrections is unspecified.

### S12-033 — Publish failure-complete logs subject to licensing and privacy

- **Source:** §12.6, line 1985.
- **Faithful summary:** Publish logs that include failures as well as successes, constrained by licensing and privacy.
- **Category:** transparency; compliance; evaluation.
- **Inputs/outputs:** Complete internal logs plus license/privacy policy → redacted/authorized public logs.
- **Invariants:** Permitted redaction does not become success-only selection; constraints are documented.
- **Required failure behavior:** Withhold protected material while disclosing the resulting gap/aggregation rather than violating constraints.
- **Required integrations:** Event log, license metadata, privacy/redaction review, publication system.
- **Observable acceptance:** Published log manifest reconciles with internal outcomes and lists redactions/reasons.
- **Dependencies:** S12-008, S10-022.
- **Ambiguity/contradiction notes:** Specific privacy standard, licenses, and minimum public granularity are unspecified.

### S12-034 — Use at least two blind referees for high-value informal claims

- **Source:** §12.6, line 1986.
- **Faithful summary:** High-value informal claims require blind expert review by at least two referees, with disagreements resolved explicitly.
- **Category:** verification; organizational security; evaluation.
- **Inputs/outputs:** High-value informal claim and reviewer assignments → at least two blinded reviews plus disagreement disposition.
- **Invariants:** Reviewer count ≥2; blinding and explicit conflict resolution are recorded.
- **Required failure behavior:** Missing quorum or unresolved disagreement prevents the required high-value informal acceptance.
- **Required integrations:** Expert portal, blinding/identity service, adjudication workflow.
- **Observable acceptance:** Review bundle proves reviewer count, blindness, and resolution trace.
- **Dependencies:** S11-001, S11-020, S12-009.
- **Ambiguity/contradiction notes:** “High-value,” expert qualification, and blind dimensions are unspecified.

### S12-035 — Treat recent preprints as hypotheses until independently replayed

- **Source:** §12.6, line 1987.
- **Faithful summary:** Very recent preprint claims remain hypotheses until an independent rerun or artifact replay.
- **Category:** source-import security; evidence policy.
- **Inputs/outputs:** Recent preprint claim and replay evidence → hypothesis-only or independently corroborated status.
- **Invariants:** Recency/source publication alone never establishes admitted truth.
- **Required failure behavior:** Without independent replay, keep the claim explicitly hypothetical/unresolved.
- **Required integrations:** Source importer, independent compute/formal replay, claim status.
- **Observable acceptance:** Recent-preprint fixture cannot be promoted before qualifying replay provenance is attached.
- **Dependencies:** S10-010, S10-022, S11-009.
- **Ambiguity/contradiction notes:** “Very recent” and acceptable independent rerun forms are unspecified.

## Section 13 — Minimal viable implementation

### S13-001 — Preserve the distinct M0, M1, and M2 milestone semantics

- **Source:** §13 opening, lines 1989–1991.
- **Faithful summary:** Implement three deliberately separate milestones: M0 repairs unsafe evidence/provenance in the current code; M1 is the smallest end-to-end scientific vertical slice; M2 is a scalable controlled-research MVP. Do not call all three simply “the MVP.”
- **Category:** milestone; program governance.
- **Inputs/outputs:** Implementation roadmap → three separately scoped/gated milestone deliverables.
- **Invariants:** Safety work is not deferred behind unnecessary M1/M2 infrastructure; milestone labels remain unambiguous.
- **Required failure behavior:** A milestone lacking its scoped obligations cannot be represented as the later milestone or generic completed MVP.
- **Required integrations:** Planning, release/version labeling, acceptance suite.
- **Observable acceptance:** Roadmap and release artifacts identify M0/M1/M2 separately with their defined purpose.
- **Dependencies:** Sections 10–12 requirements generally.
- **Ambiguity/contradiction notes:** Schedule, owners, and quantitative milestone deadlines are unspecified.

### S13-002 — Reuse and extend the named repository foundations

- **Source:** §13.1 “Reuse from the current repository,” lines 1993–2004.
- **Faithful summary:** Keep source snapshots/hashes from `erdos_ingest.py`; cards/ranking families from `erdos_searcher.py` only as transparent weak priors; content-addressed partial run contracts/schema-v3 caches extended to complete per-stage identities; append-only ledger extended to every attempt and terminal outcome; atomic queue claims and 4:1 protected exploration; normalized terminal dispositions; adaptive shared rate limiting capped at 120 seconds; and deterministic rejection/regulator distinction as conservative shells, not the generic evidence-acceptance path.
- **Category:** integration; migration; implementation.
- **Inputs/outputs:** Existing named components and new requirements → reused, extended, or constrained components.
- **Invariants:** Reused weak priors remain transparent/weak; production ledger is attempt-complete; 4:1 and 120-second cap remain; generic acceptance is not preserved.
- **Required failure behavior:** Existing artifacts lacking complete identity/evidence semantics are not silently grandfathered.
- **Required integrations:** Ingest/searcher/contracts/caches/ledger/queue/rate limiter/regulator.
- **Observable acceptance:** Component-level audit maps each named retained feature to its extension/constraint and regression coverage.
- **Dependencies:** S10-011, S10-017, S10-019, S12-008.
- **Ambiguity/contradiction notes:** “4:1” means a protected-exploration structure but exact scheduling interpretation is not restated; implementation filenames may evolve.

### S13-003 — Keep M0 search-neutral while making evidence replayable

- **Source:** §13.2 “M0 — Safety and provenance patch,” lines 2006–2008.
- **Faithful summary:** M0 changes no mathematical search strategy; it makes the existing pipeline honest and replayable.
- **Category:** milestone scope; safety.
- **Inputs/outputs:** Existing pipeline → safety/provenance patch with unchanged search strategy.
- **Invariants:** M0 evaluation is not confounded by a search-strategy redesign.
- **Required failure behavior:** Search changes are deferred/reclassified rather than smuggled into M0.
- **Required integrations:** Existing pipeline, provenance, replay, validation gates.
- **Observable acceptance:** Behavioral diff shows search policy unchanged while safety/replay requirements pass.
- **Dependencies:** S13-001, S13-002.
- **Ambiguity/contradiction notes:** Changes necessary to stop unsafe paths could indirectly alter outcomes; acceptable incidental effects are unspecified.

### S13-004 — Enforce one signed feature policy at every M0 entry point

- **Source:** §13.2, line 2010.
- **Faithful summary:** Apply one signed feature policy to every scheduler, verifier, evidence loader, cache replay, gate, promotion, and standalone-script entry point.
- **Category:** M0 implementation; security; policy enforcement.
- **Inputs/outputs:** Signed policy and attempted operation → consistently authorized or denied operation plus audit evidence.
- **Invariants:** No listed entry point has a divergent or bypass policy.
- **Required failure behavior:** Missing/invalid policy or disabled feature fails closed.
- **Required integrations:** All seven entry-point classes, signature verification, event log.
- **Observable acceptance:** Entry-point matrix tests every disabled feature through every path and finds no bypass.
- **Dependencies:** S10-017, S13-002.
- **Ambiguity/contradiction notes:** Policy schema, signing keys, rollout, and emergency override are unspecified.

### S13-005 — Disable promotion until four evidence kinds have closed validators

- **Source:** §13.2, line 2011.
- **Faithful summary:** Keep promotion disabled until formal, computational, expert, and source-import evidence each has a closed kind-specific schema and validator.
- **Category:** M0 security; promotion gate.
- **Inputs/outputs:** Evidence kind schemas/validators and promotion request → disabled or validator-qualified promotion.
- **Invariants:** All four evidence classes are covered; generic/open payload acceptance is prohibited.
- **Required failure behavior:** Any missing/unrecognized schema or validator keeps promotion disabled.
- **Required integrations:** Evidence adapters/validators, feature policy, promotion service.
- **Observable acceptance:** Production-path tests reject each evidence kind before validator availability and reject out-of-schema fields afterward.
- **Dependencies:** S10-010, S10-011, S13-004.
- **Ambiguity/contradiction notes:** Expert-evidence validator semantics are not exhaustively defined in the excerpt.

### S13-006 — Require three formal-release checks in M0

- **Source:** §13.2, line 2012.
- **Faithful summary:** Formal evidence can support release only after local pinned-kernel replay, an approved intent certificate, and a checked formal-correspondence certificate.
- **Category:** M0 security; formal integration; release gate.
- **Inputs/outputs:** Formal artifact, local replay, intent and correspondence certificates → formal release eligibility.
- **Invariants:** All three checks are conjunctive and exact-artifact-bound.
- **Required failure behavior:** Any absent/failed/stale check blocks release support while preserving narrower artifact history.
- **Required integrations:** Pinned Lean environment, certificate services, release gate.
- **Observable acceptance:** Combination tests accept only three-pass bundles and detect artifact/hash mutation.
- **Dependencies:** S10-007, S10-008, S11-017.
- **Ambiguity/contradiction notes:** “Checked” correspondence may mean certificate validation plus verdict; implementation details are not stated.

### S13-007 — Bind stage caches to actual runner identity

- **Source:** §13.2, line 2013.
- **Faithful summary:** Bind each cached stage to provider, immutable model/version when available, UI/API surface, account/tool-entitlement class, context ID, prompt, adjudicator policy, and response hash; store caller-supplied names only as unattested labels, not model identity.
- **Category:** M0 implementation; cache security; provenance.
- **Inputs/outputs:** Actual execution context/result → identity-complete cache record and compatibility key.
- **Invariants:** Cache identity comes from observed provenance; caller text never becomes attestation.
- **Required failure behavior:** Missing/mismatched identity prevents compatible replay or independence credit.
- **Required integrations:** Model gateway, runner adapters, cache manager, contract fingerprinting, adjudicator policy.
- **Observable acceptance:** Change each identity dimension and observe cache miss/invalidation; spoofed model name remains labeled unattested.
- **Dependencies:** S10-019, S11-002.
- **Ambiguity/contradiction notes:** Immutable model version may be unavailable, so the required degraded/nonreproducible state needs a concrete schema.

### S13-008 — Make gate/adjudication/evidence/promotion records append-only

- **Source:** §13.2, line 2014.
- **Faithful summary:** Record gate, adjudication, evidence, and promotion history append-only and derive `manifest.json` as a materialized view rather than overwriting history.
- **Category:** M0 implementation; audit; recovery.
- **Inputs/outputs:** Lifecycle events → immutable history and deterministic manifest projection.
- **Invariants:** Manifest is derived, never authoritative; no history overwrite.
- **Required failure behavior:** Projection inconsistency triggers rebuild/failure, not retroactive event mutation.
- **Required integrations:** Event store, artifact/evidence store, manifest projector.
- **Observable acceptance:** Rebuild from identical history is deterministic and prior decisions remain queryable.
- **Dependencies:** S10-017, S10-018.
- **Ambiguity/contradiction notes:** Manifest schema/canonical ordering are unspecified.

### S13-009 — Quarantine identity-incomplete legacy records

- **Source:** §13.2, line 2015.
- **Faithful summary:** Quarantine legacy manifests and stale root claim files lacking complete identity, explicitly including records 601, 661, 724, 782, and 849, until a migration proves their bindings.
- **Category:** M0 migration; security; failure behavior.
- **Inputs/outputs:** Legacy record and migration evidence → quarantined or explicitly migrated record.
- **Invariants:** Legacy presence/previous success never implies trusted migration; named records are included.
- **Required failure behavior:** Fail closed to quarantine when bindings cannot be proven.
- **Required integrations:** Legacy loader, quarantine store, migration validator, feature/promotion gate.
- **Observable acceptance:** Each named fixture is inaccessible as evidence before proven migration and retains quarantine audit trail.
- **Dependencies:** S13-004, S13-007, S13-008.
- **Ambiguity/contradiction notes:** Exact bindings and migration proof format are unspecified.

### S13-010 — Implement explicit M0 evidence precedence

- **Source:** §13.2, line 2016.
- **Faithful summary:** A model referee may block intent, applicability, novelty, or significance but cannot overrule a clean kernel proof of the exact locked proposition; a checked same-scope counterexample or proof of negation creates `CONFLICTED` and triggers encoding/axiom/TCB audit.
- **Category:** M0 security; conflict policy; release.
- **Inputs/outputs:** Kernel result, model review, hard counterevidence and dimension → truth/other-dimension decisions or conflict audit.
- **Invariants:** Exact formal truth and release dimensions remain separate; hard contradiction does not overwrite by precedence.
- **Required failure behavior:** Model dissent cannot erase exact kernel truth, but it can block nontruth dimensions; incompatible hard evidence fails to `CONFLICTED`.
- **Required integrations:** Kernel verifier, referee, certificates/audits, conflict handler, release gate.
- **Observable acceptance:** Precedence matrix tests every stated combination and audit trigger.
- **Dependencies:** S10-012, S11-015–S11-020.
- **Ambiguity/contradiction notes:** Treatment of kernel proof with discovered unsafe axioms is governed by “clean”/TCB audit but thresholds are unspecified.

### S13-011 — Instrument complete M0 resource and outcome telemetry

- **Source:** §13.2, line 2017.
- **Faithful summary:** Record tokens, calls, wall time, rate limits, deterministic compute, reviewer time, cache provenance, and terminal disposition to enable later baseline comparison.
- **Category:** M0 implementation; observability; evaluation integration.
- **Inputs/outputs:** Every attempt/resource event → authenticated run-level telemetry.
- **Invariants:** Both model and nonmodel costs, cache provenance, censored operations, and terminal outcomes are attributable.
- **Required failure behavior:** Missing telemetry makes equal-cost claims unsupported rather than imputing zero.
- **Required integrations:** Model gateway, compute workers, rate limiter, reviewer portal, caches, outcome ledger.
- **Observable acceptance:** Telemetry reconciliation covers every attempt and feeds matched-cost reports.
- **Dependencies:** S10-017, S12-007, S12-008.
- **Ambiguity/contradiction notes:** Units and aggregation across providers/human time are unspecified.

### S13-012 — Meet the M0 completion gate

- **Source:** §13.2, line 2019.
- **Faithful summary:** M0 is complete only when stop-ship defects have regression tests and the old generic `passed=true` route is unreachable from every production entry point.
- **Category:** milestone acceptance; security.
- **Inputs/outputs:** Stop-ship defect list, production path inventory, regression suite → M0 pass/fail.
- **Invariants:** Both regression coverage and global route unreachability are necessary.
- **Required failure behavior:** Any uncovered stop-ship defect or reachable generic path fails M0.
- **Required integrations:** Test suite, static/dynamic route analysis, all production entry points.
- **Observable acceptance:** Tests reproduce each stop-ship defect and negative reachability evidence covers the entry-point matrix.
- **Dependencies:** S13-004–S13-011.
- **Ambiguity/contradiction notes:** The complete stop-ship defect inventory is not enumerated within lines 1419–2302.

### S13-013 — Build the M1 transactional local graph/event store

- **Source:** §13.3 “M1 — Small end-to-end vertical slice,” lines 2021–2025.
- **Faithful summary:** Use SQLite plus append-only JSONL events, a materialized claim/dependency/evidence view, and transactional invalidation.
- **Category:** M1 implementation; storage; revocation.
- **Inputs/outputs:** Claims/evidence/dependency events → local authoritative event history and queryable materialized view.
- **Invariants:** Events append; materialized view is rebuildable; invalidation is transactional.
- **Required failure behavior:** Roll back incomplete invalidations and rebuild inconsistent views.
- **Required integrations:** Claim graph, JSONL event log, SQLite projection.
- **Observable acceptance:** Restart/rebuild and injected-failure tests preserve consistent state.
- **Dependencies:** S13-012, S10-013–S10-018.
- **Ambiguity/contradiction notes:** Division of authority between SQLite and JSONL and crash-atomic commit protocol are unspecified.

### S13-014 — Build one dual-parser Statement IR path with probes

- **Source:** §13.3, line 2026.
- **Faithful summary:** M1 includes one dual-parser Statement IR, explicit interpretations, source/status record, and exact boundary/counterexample probes.
- **Category:** M1 implementation; semantic safety.
- **Inputs/outputs:** Raw source/problem → two parses, Statement IR, interpretation records, source/status record, probe results.
- **Invariants:** Parser disagreement/open ambiguity remains explicit; probes are exact.
- **Required failure behavior:** Ambiguity or parser conflict blocks intended-target release rather than being silently reconciled.
- **Required integrations:** Ingest, interpretations, source/status audit, exact compute.
- **Observable acceptance:** Controlled ambiguous/false inputs exercise parser divergence and probes.
- **Dependencies:** S10-001, S10-002, S11-003, S11-004.
- **Ambiguity/contradiction notes:** The two parser implementations and reconciliation policy are unspecified.

### S13-015 — Build the minimal M1 retrieval plane

- **Source:** §13.3, line 2027.
- **Faithful summary:** Provide one frozen literature-packet path with verbatim theorem/hypothesis records, one Mathlib declaration retriever, and a read-only OEIS client with typed local transforms.
- **Category:** M1 implementation; retrieval integration; source safety.
- **Inputs/outputs:** Frozen sources, Mathlib query, OEIS query/local transform → provenance-complete candidate premises/data.
- **Invariants:** Literature text/hypotheses are verbatim and frozen; OEIS is read-only and transforms are typed.
- **Required failure behavior:** Retrieval matches remain candidates/unresolved until applicability or proof checks; no external mutation.
- **Required integrations:** Source packet, Mathlib index, OEIS API/client, transform layer, provenance.
- **Observable acceptance:** Replay retrieves identical packet records/declarations/typed results and blocks writes.
- **Dependencies:** S10-022, S11-007.
- **Ambiguity/contradiction notes:** Packet construction and typed-transform catalog are unspecified.

### S13-016 — Build one sandboxed exact Python backend with independent replay

- **Source:** §13.3, line 2028.
- **Faithful summary:** M1 uses one sandboxed exact Python backend with immutable inputs/outputs and independent replay; first jobs are enumeration and witness checking, not unrestricted CAS automation.
- **Category:** M1 implementation; compute security; reproducibility.
- **Inputs/outputs:** Immutable exact computation job → hashed output/certificate plus independent replay result.
- **Invariants:** Sandbox and exactness; immutable I/O; initial scope excludes unrestricted CAS.
- **Required failure behavior:** Failed/mismatched replay quarantines evidence; sandbox violations abort without admission.
- **Required integrations:** Compute service, artifact store, replay worker, evidence validator.
- **Observable acceptance:** Enumeration/witness jobs replay identically and attempted unrestricted/networked behavior is denied.
- **Dependencies:** S10-006, S11-009.
- **Ambiguity/contradiction notes:** Exact Python libraries, sandbox boundary, and independent environment definition are unspecified.

### S13-017 — Build the minimal pinned M1 Lean path

- **Source:** §13.3, line 2029.
- **Faithful summary:** M1 includes one pinned Lean/Mathlib project, target-sentinel tests, goal capsules, and one Lean proof worker; Aristotle may generate candidates but is optional.
- **Category:** M1 implementation; formal integration.
- **Inputs/outputs:** Exact formal target/goal capsule → candidate proof and clean replay/audit result.
- **Invariants:** Lean/Mathlib is pinned; target sentinels guard intended type; optional vendor candidates have no special trust.
- **Required failure behavior:** Target mismatch/build failure/placeholder blocks certificate; vendor unavailability does not block M1.
- **Required integrations:** Lean worker/project, target review, goal capsules, optional vendor adapter.
- **Observable acceptance:** Sentinel detects target mutation and locally accepted proof replays in the pinned project.
- **Dependencies:** S13-006, S11-010, S11-014.
- **Ambiguity/contradiction notes:** Sentinel catalog, capsule schema, and exact pinned version are unspecified.

### S13-018 — Run distinct branches under a simple controller and blueprint

- **Source:** §13.3, line 2030.
- **Faithful summary:** M1 runs two or three genuinely method-distinct branches with a simple best-first/UCB controller, AND/OR blueprint, semantic duplicate checks, and failure certificates.
- **Category:** M1 implementation; orchestration.
- **Inputs/outputs:** Goals/program proposals/budget → 2–3 active distinct branches, allocation decisions, dedup and failure artifacts.
- **Invariants:** Distinction is methodological, not label-only; failures and blueprint dependencies persist.
- **Required failure behavior:** Duplicate branches merge/reject; defined failures produce certificates and stop repetition.
- **Required integrations:** Branch graph, mechanism fingerprints, controller, blueprint, failure-certificate store.
- **Observable acceptance:** Run trace shows 2–3 distinct mechanisms, controller decisions, duplicate detection, and failure artifacts.
- **Dependencies:** S10-005, S10-009, S12-021.
- **Ambiguity/contradiction notes:** Choice between best-first and UCB and “genuinely distinct” threshold are unspecified.

### S13-019 — Add one independent falsifier/referee and five-axis release bundle

- **Source:** §13.3, line 2031.
- **Faithful summary:** M1 includes one independent falsifier/referee and a release certificate bundle covering the five release axes.
- **Category:** M1 integration; verification; release.
- **Inputs/outputs:** Candidate results → independent attacks/review and multidimensional release/no-release artifact.
- **Invariants:** Falsification/refereeing is independent; axes are not collapsed.
- **Required failure behavior:** Valid defect or unresolved required axis blocks release.
- **Required integrations:** Referee, exact compute/formal tools, release certificates.
- **Observable acceptance:** End-to-end M1 run produces independent review and separately rendered axes.
- **Dependencies:** S11-001–S11-023.
- **Ambiguity/contradiction notes:** “Five-axis” likely refers intent/truth/novelty/significance/reproducibility; autonomy is separately recorded elsewhere, creating terminology tension but not a direct contradiction.

### S13-020 — Maintain a compact heterogeneous M1 test suite

- **Source:** §13.3, line 2032.
- **Faithful summary:** The M1 suite covers ambiguous/false statements, formal olympiad tasks, computation-plus-proof tasks, and historically solved Erdős problems under frozen cutoffs.
- **Category:** M1 evaluation; acceptance coverage.
- **Inputs/outputs:** Four task families → repeatable safety/capability regression results.
- **Invariants:** All four families appear; historical cases use frozen cutoffs.
- **Required failure behavior:** Missing family prevents claiming the complete M1 evaluation slice.
- **Required integrations:** Intake, Lean, compute, historical retrieval/status evaluation.
- **Observable acceptance:** Suite manifest contains at least one (later §13.7 suggests approximate counts) from every family with frozen provenance.
- **Dependencies:** S12-001, S12-014, S13-014–S13-019.
- **Ambiguity/contradiction notes:** Exact compact-suite size is deferred to the approximate §13.7 set.

### S13-021 — Complete the minimum useful research loop

- **Source:** §13.3, line 2034.
- **Faithful summary:** M1 must execute intake → falsification/retrieval → branching → computation/formalization → adversarial review → replayable release or honest no-result.
- **Category:** M1 milestone; end-to-end integration.
- **Inputs/outputs:** Raw controlled problem → certified replayable result or evidence-backed no-result.
- **Invariants:** Every stage is connected; no-result is a legitimate terminal outcome; release is replayable.
- **Required failure behavior:** Failure/uncertainty terminates honestly rather than fabricating release.
- **Required integrations:** All M1 components S13-013–S13-020.
- **Observable acceptance:** At least one fixture traverses each successful path and one traverses the honest no-result path with full events.
- **Dependencies:** S13-013–S13-020.
- **Ambiguity/contradiction notes:** Required success/no-result fixture counts are unspecified.

### S13-022 — Gate M2 on M1 safety and baseline tests

- **Source:** §13.4 “M2 — Scalable MVP,” lines 2036–2038.
- **Faithful summary:** Add M2 scale features only after M1 passes its safety and baseline tests.
- **Category:** milestone gate; sequencing.
- **Inputs/outputs:** M1 safety/baseline evidence → authorization to start/claim M2 additions.
- **Invariants:** Scale cannot precede truth-plane validation.
- **Required failure behavior:** Failed/incomplete M1 gate blocks M2 milestone status.
- **Required integrations:** M1 acceptance suite, baseline evaluation, implementation governance.
- **Observable acceptance:** M2 release record references passing M1 safety and baseline artifacts.
- **Dependencies:** S13-021, S12-006–S12-011.
- **Ambiguity/contradiction notes:** Exact M1 test thresholds are not quantified.

### S13-023 — Scale M2 storage and SCC-aware revocation

- **Source:** §13.4, line 2040.
- **Faithful summary:** Add PostgreSQL event sourcing, leases/heartbeats, object storage, and transactional SCC-aware revocation.
- **Category:** M2 implementation; storage; concurrency; revocation.
- **Inputs/outputs:** M1 event/graph/artifacts and concurrent workload → scalable durable storage/recovery.
- **Invariants:** Append-only authority and transactional SCC semantics survive migration.
- **Required failure behavior:** Crashes/concurrency do not expose partial revocation or duplicate ownership.
- **Required integrations:** PostgreSQL, object store, lease service, graph closure.
- **Observable acceptance:** Migration, concurrency, crash, and cyclic-revocation tests pass.
- **Dependencies:** S13-013, S10-013, S10-021, S13-022.
- **Ambiguity/contradiction notes:** Migration strategy, topology, and transaction isolation are unspecified.

### S13-024 — Add containerized solver backends with proof adapters

- **Source:** §13.4, line 2041.
- **Faithful summary:** M2 adds containerized SageMath and selected CAS, SAT/SMT, ILP, and graph-enumeration backends, each with proof/certificate adapters.
- **Category:** M2 implementation; compute integration; security.
- **Inputs/outputs:** Typed solver jobs → immutable result plus independently checkable proof/certificate where supported.
- **Invariants:** Backends are containerized and evidence flows through type-specific adapters.
- **Required failure behavior:** Uncheckable/malformed solver output cannot become admitted evidence.
- **Required integrations:** Compute lab, container runtime, evidence router, certificate checkers.
- **Observable acceptance:** One accepted and one rejected fixture per selected backend validates adapter and sandbox.
- **Dependencies:** S13-016, S10-010, S13-022.
- **Ambiguity/contradiction notes:** “Selected CAS” and required certificate availability per backend are unspecified.

### S13-025 — Scale M2 retrieval with frozen packets and caches

- **Source:** §13.4, line 2042.
- **Faithful summary:** Add production OEIS transform/query caching, citation-graph retrieval, broader theorem indexing, and frozen solver/referee packets.
- **Category:** M2 implementation; retrieval/caching integration.
- **Inputs/outputs:** Queries, typed transforms, citation/theorem indexes, campaign contracts → provenance-bound cached results and frozen packets.
- **Invariants:** Cache/packet compatibility is contract-bound; external matches remain evidence candidates.
- **Required failure behavior:** Policy/index/packet changes invalidate affected caches; unverified matches do not promote claims.
- **Required integrations:** OEIS service, citation graph, theorem index, solver/referee runners, cache provenance.
- **Observable acceptance:** Cache-key mutation tests and frozen-packet replay demonstrate deterministic compatibility.
- **Dependencies:** S13-007, S13-015, S13-022.
- **Ambiguity/contradiction notes:** Production cache TTL and index coverage targets are unspecified.

### S13-026 — Scale M2 branch allocation with congestion-aware policies

- **Source:** §13.4, line 2043.
- **Faithful summary:** Run three to five concurrent method-distinct programs with posterior Thompson/UCB allocation, protected exploration, pause/reopen rules, and verification-congestion pricing.
- **Category:** M2 implementation; orchestration.
- **Inputs/outputs:** Branch posteriors, budgets, congestion, new evidence → allocations, pauses, reopens for 3–5 programs.
- **Invariants:** Method diversity and protected exploration remain; verification capacity affects generation price.
- **Required failure behavior:** Congestion throttles/redirects generation; low-value work pauses with reopen conditions rather than silent loss.
- **Required integrations:** Branch controller, posterior/calibration ledger, verifier queue, failure/reopen events.
- **Observable acceptance:** Controlled runs demonstrate bounds, exploration share, allocation updates, pause/reopen, and congestion response.
- **Dependencies:** S13-018, S12-021, S13-022.
- **Ambiguity/contradiction notes:** Thompson versus UCB choice, priors, exact exploration fraction, and price function are unspecified.

### S13-027 — Add an M2 Lean portfolio and independent referee family

- **Source:** §13.4, line 2044.
- **Faithful summary:** Add multiple open Lean provers/code agents, proof-state caching, and a separate model/tool family for high-value refereeing.
- **Category:** M2 implementation; formal search; verification independence.
- **Inputs/outputs:** Goal capsules/proof states → portfolio candidates, compatible cached states, independent high-value review.
- **Invariants:** Cached proof states are environment/goal compatible; high-value referee uses separate family/path.
- **Required failure behavior:** Incompatible proof-state cache is invalidated; correlated/self-review does not earn independence credit.
- **Required integrations:** Lean farm, model gateway, cache identity, referee subsystem.
- **Observable acceptance:** Portfolio routing/replay tests and identity traces demonstrate separation and compatible caching.
- **Dependencies:** S13-007, S13-017, S11-001, S13-022.
- **Ambiguity/contradiction notes:** Portfolio members and high-value threshold are campaign-selected, not fixed.

### S13-028 — Add authenticated M2 calibration/expert-iteration telemetry, but no learned value model yet

- **Source:** §13.4, line 2045.
- **Faithful summary:** M2 telemetry must support calibration and verified-only expert iteration with authenticated data, while deferring training of a learned value model.
- **Category:** M2 implementation; telemetry; learning safety.
- **Inputs/outputs:** Authenticated runs/outcomes/reviews → calibration ledger and verified-only learning dataset.
- **Invariants:** Only verified outcomes enter expert iteration; learned value-model training is outside M2.
- **Required failure behavior:** Unauthenticated/unverified labels are excluded/quarantined.
- **Required integrations:** Telemetry/signatures, calibration ledger, reviewer outcomes, learning-data exporter.
- **Observable acceptance:** Dataset lineage verifies every label and no learned value model is required for M2 completion.
- **Dependencies:** S10-023, S12-023, S13-011, S13-022.
- **Ambiguity/contradiction notes:** Authentication method and “verified-only” exact tiers are unspecified.

### S13-029 — Use the bounded runtime role layout and scale only for independent bottlenecks

- **Source:** §13.5 “Runtime role layout,” lines 2047–2054.
- **Faithful summary:** Normally use four concurrent M1 roles—governor/intake, one or two method-specific program workers, compute/formal worker chosen by bottleneck, and adversarial verifier—and scale M2 workers only when the queue has independent bottlenecks.
- **Category:** runtime architecture; resource control.
- **Inputs/outputs:** Queue/bottleneck state → role activation and bounded worker count.
- **Invariants:** Verification role remains explicit; scale responds to independent work, not idle role proliferation.
- **Required failure behavior:** Do not spawn scale workers without independent bottlenecks; exact enforcement response is unspecified.
- **Required integrations:** Scheduler, queue dependency analysis, controller, verifier pool.
- **Observable acceptance:** M1 trace uses the role layout and M2 scaling events cite independent queued bottlenecks.
- **Dependencies:** S13-018, S13-021, S13-026.
- **Ambiguity/contradiction notes:** “Only four concurrent roles” coexists with “one or two” program workers; roles and processes/workers are distinct but exact concurrency count can be read as four role classes rather than four processes.

### S13-030 — Implement tools as services, not idle chat roles

- **Source:** §13.5, line 2056.
- **Faithful summary:** Retrieval, OEIS, computation, Lean, and graph capabilities are callable services, not continuously idle chat tabs.
- **Category:** runtime architecture; integration; efficiency.
- **Inputs/outputs:** Worker requests → on-demand typed service calls/results.
- **Invariants:** Capability identity/provenance belongs to services and calls, not nominal chat-role persistence.
- **Required failure behavior:** Unused service capacity does not consume standing agent slots; service errors follow their typed failure paths.
- **Required integrations:** Retrieval/OEIS/compute/Lean/graph APIs, scheduler/model workers.
- **Observable acceptance:** Architecture/process trace shows on-demand service invocation and no permanent idle chat worker for these capabilities.
- **Dependencies:** S13-015–S13-017, S13-029.
- **Ambiguity/contradiction notes:** Deployment granularity (process, container, library) is not prescribed.

### S13-031 — Acceptance bullet 1/18: disabled features are unreachable everywhere

- **Source:** §13.6 “Acceptance tests,” line 2060.
- **Faithful summary:** Every disabled feature must remain unreachable both through direct scripts and through the scheduler.
- **Category:** acceptance; security; feature policy.
- **Inputs/outputs:** Disabled-feature policy and invocations via both path classes → deterministic denial.
- **Invariants:** Entry-point parity; no script bypass.
- **Required failure behavior:** Fail closed before side effects and log the denial.
- **Required integrations:** Signed feature policy, scheduler, all direct scripts.
- **Observable acceptance:** Parameterized tests invoke every disabled feature from each path and observe no execution/state mutation.
- **Dependencies:** S13-004.
- **Ambiguity/contradiction notes:** “Every” requires an authoritative entry-point/feature inventory, not defined here.

### S13-032 — Acceptance bullet 2/18: adjudication cache cannot cross runner identity

- **Source:** §13.6, line 2061.
- **Faithful summary:** A cached adjudication cannot be replayed under a different runner/model identity.
- **Category:** acceptance; cache security.
- **Inputs/outputs:** Cached adjudication plus current runner identity → compatible replay or rejection/cache miss.
- **Invariants:** Runner/model identity is part of compatibility.
- **Required failure behavior:** Mismatch invalidates/denies replay; it must not silently recompute under the old identity label.
- **Required integrations:** Cache manager, runner/model registry, contract fingerprint.
- **Observable acceptance:** Identity mutation yields cache miss/invalidation and a new provenance record.
- **Dependencies:** S13-007.
- **Ambiguity/contradiction notes:** Identity-equivalence rules across aliases are unspecified.

### S13-033 — Acceptance bullet 3/18: all behavior-changing inputs invalidate affected caches/contracts

- **Source:** §13.6, line 2062.
- **Faithful summary:** Changes to literature packet, adjudicator policy, feature policy, Lean/import closure, evidence adapter, or validator invalidate every affected run contract/cache.
- **Category:** acceptance; cache correctness; provenance.
- **Inputs/outputs:** Old/new fingerprint for any of six components → complete affected-cache/contract invalidation set.
- **Invariants:** Full dependency closure, not only direct cache keys, is invalidated.
- **Required failure behavior:** Uncertain dependency fails toward invalidation rather than unsafe reuse.
- **Required integrations:** Dependency fingerprint graph, cache manager, contract store.
- **Observable acceptance:** One mutation test per named component proves all and only affected entries are invalidated.
- **Dependencies:** S13-007, S10-020.
- **Ambiguity/contradiction notes:** “Every affected” requires a dependency map; precision expectations beyond safety are not quantified.

### S13-034 — Acceptance bullet 4/18: caller model labels cannot establish identity or independence

- **Source:** §13.6, line 2063.
- **Faithful summary:** Caller-provided model labels are either attested to provider/UI state or explicitly marked unattested and never credited as independent-model evidence.
- **Category:** acceptance; identity security.
- **Inputs/outputs:** Caller label and provider/UI attestation → attested identity or unattested label.
- **Invariants:** Unattested text has zero identity/independence authority.
- **Required failure behavior:** Missing attestation preserves label only as unattested and denies independence credit.
- **Required integrations:** Provider/UI adapters, identity registry, diversity profile.
- **Observable acceptance:** Spoofed-label tests cannot alter model identity or review independence.
- **Dependencies:** S13-007, S11-002.
- **Ambiguity/contradiction notes:** Required UI attestation mechanism is unspecified.

### S13-035 — Acceptance bullet 5/18: append-only history and reproducible manifest

- **Source:** §13.6, line 2064.
- **Faithful summary:** Gate, adjudication, and promotion history is append-only, and deterministic manifest projection is reproducible.
- **Category:** acceptance; audit; recovery.
- **Inputs/outputs:** Ordered history → deterministic manifest.
- **Invariants:** No overwrite/deletion of decisions; identical history produces identical projection.
- **Required failure behavior:** Projection mismatch fails verification and is rebuilt/investigated without rewriting events.
- **Required integrations:** Event store, manifest projector, hash/canonicalization.
- **Observable acceptance:** Rebuilds are byte/hash identical and historical decisions remain queryable.
- **Dependencies:** S13-008.
- **Ambiguity/contradiction notes:** Evidence history is included in M0 line 2014 but omitted from this acceptance bullet; omission should not be read as permission to overwrite evidence.

### S13-036 — Acceptance bullet 6/18: quarantine identity-incomplete legacy records

- **Source:** §13.6, line 2065.
- **Faithful summary:** Legacy records lacking complete identity are quarantined, never silently upgraded.
- **Category:** acceptance; migration security.
- **Inputs/outputs:** Legacy record and identity proof → quarantine or explicit audited migration.
- **Invariants:** No implicit migration based on previous labels/status.
- **Required failure behavior:** Incomplete proof stays quarantined.
- **Required integrations:** Legacy loader, quarantine/migration service, promotion gate.
- **Observable acceptance:** Fixture lacking each identity dimension cannot support evidence after load.
- **Dependencies:** S13-009.
- **Ambiguity/contradiction notes:** Migration success acceptance is not detailed here.

### S13-037 — Acceptance bullet 7/18: ambiguity produces alternatives and blocks intended release

- **Source:** §13.6, line 2066.
- **Faithful summary:** Injected ambiguous statements create multiple interpretations and block intended-target release.
- **Category:** acceptance; semantic safety.
- **Inputs/outputs:** Ambiguous statement fixture → multiple interpretation records and blocked release.
- **Invariants:** Ambiguity is represented, not normalized away; no active approved target is assumed.
- **Required failure behavior:** Fail closed on intended-target release while ambiguity remains unresolved.
- **Required integrations:** Dual parser, interpretation lattice, intent gate, release pipeline.
- **Observable acceptance:** Test asserts ≥2 interpretations and denial reason tied to unresolved intent.
- **Dependencies:** S13-014, S10-002, S11-017.
- **Ambiguity/contradiction notes:** The acceptance line does not state whether human resolution can later select one interpretation.

### S13-038 — Acceptance bullet 8/18: revoke a false central lemma and downgrade all dependents

- **Source:** §13.6, line 2067.
- **Faithful summary:** An injected false central lemma is detected, revoked, and every dependent is downgraded.
- **Category:** acceptance; revocation; dependency integrity.
- **Inputs/outputs:** False-lemma injection and exact counterevidence → revoked/refuted root and downgraded reverse closure.
- **Invariants:** No dependent retains unsupported promotion; propagation covers cycles.
- **Required failure behavior:** Detection triggers transactional fail-closed propagation.
- **Required integrations:** Falsifier, exact checker, SCC graph, revocation engine.
- **Observable acceptance:** Injected graph fixture yields the exact full dependent closure with atomic state/events.
- **Dependencies:** S10-013–S10-016, S13-013.
- **Ambiguity/contradiction notes:** “Revoked” may refer evidence/claim support rather than lifecycle `RETRACTED`; exact status transition must be made explicit in implementation.

### S13-039 — Acceptance bullet 9/18: rate limits do not spend proof attempts or kill claims

- **Source:** §13.6, line 2068.
- **Faithful summary:** Work resumes after rate limits without consuming proof attempts or killing claims.
- **Category:** acceptance; operational failure recovery.
- **Inputs/outputs:** Rate-limit event and retry state → censored pause/backoff then resumed same mathematical work.
- **Invariants:** Mathematical retry budget and claim truth/lifecycle are unchanged by provider throttling.
- **Required failure behavior:** Record/pause as operational censoring, honor backoff, resume compatibly.
- **Required integrations:** Rate limiter, scheduler/lease, attempt accounting, claim store.
- **Observable acceptance:** Injected 429/limit leaves attempt count/status unchanged and eventually resumes within policy.
- **Dependencies:** S10-020, S13-002.
- **Ambiguity/contradiction notes:** Maximum total wait/campaign termination policy is unspecified; per-backoff cap is 120 seconds elsewhere.

### S13-040 — Acceptance bullet 10/18: recover crashed leases without duplicate non-idempotent actions

- **Source:** §13.6, line 2069.
- **Faithful summary:** Recover a crashed worker’s lease without duplicating non-idempotent actions.
- **Category:** acceptance; concurrency; failure recovery.
- **Inputs/outputs:** Crash during leased work and recovery worker → single effective action and transferred/resumed lease.
- **Invariants:** At-most-once effect for non-idempotent operations; one fenced owner.
- **Required failure behavior:** Delay/abort uncertain takeover until action state is reconciled; never blindly repeat.
- **Required integrations:** Lease/heartbeat/fencing, idempotency/action ledger, checkpoint/resume.
- **Observable acceptance:** Crash at each commit boundary results in exactly one externally visible action.
- **Dependencies:** S10-021, S13-023.
- **Ambiguity/contradiction notes:** The spec requires the outcome but does not define fencing/idempotency-key protocol.

### S13-041 — Acceptance bullet 11/18: independently replay every exact computation

- **Source:** §13.6, line 2070.
- **Faithful summary:** Every exact computation replays in an independent container.
- **Category:** acceptance; reproducibility; compute security.
- **Inputs/outputs:** Exact computation artifact/I/O → independent-container replay result.
- **Invariants:** Universal coverage; container independence is provenance-recorded.
- **Required failure behavior:** Replay failure/mismatch quarantines evidence and revokes dependents as required.
- **Required integrations:** Compute backend, container runtime, replay worker, invalidation graph.
- **Observable acceptance:** Evidence inventory has a passing independent replay for every exact-computation ID.
- **Dependencies:** S13-016, S11-009.
- **Ambiguity/contradiction notes:** Independence from image/toolchain source is not quantified.

### S13-042 — Acceptance bullet 12/18: clean pinned Lean builds with no placeholders

- **Source:** §13.6, line 2071.
- **Faithful summary:** Every Lean certificate builds cleanly in the pinned environment with no placeholders.
- **Category:** acceptance; formal security.
- **Inputs/outputs:** Lean certificate/source and pinned environment → clean build plus placeholder/axiom audit.
- **Invariants:** Universal certificate coverage; exact pinned closure; no holes.
- **Required failure behavior:** Any build failure or placeholder rejects the certificate.
- **Required integrations:** Lean replay farm, environment registry, placeholder scanner.
- **Observable acceptance:** Inventory-wide clean replay report and seeded-hole negative test.
- **Dependencies:** S13-017, S11-010, S11-014.
- **Ambiguity/contradiction notes:** Allowed axioms are addressed by broader formal audit but this bullet only explicitly says no placeholders.

### S13-043 — Acceptance bullet 13/18: reject vendor-only COMPLETE

- **Source:** §13.6, line 2072.
- **Faithful summary:** Reject a result whose only basis is a vendor `COMPLETE` status.
- **Category:** acceptance; third-party trust security.
- **Inputs/outputs:** Vendor completion response without local evidence → rejected/unadmitted result.
- **Invariants:** Vendor status is not a proof/certificate or local replay.
- **Required failure behavior:** Preserve vendor artifact/provenance but deny promotion/release.
- **Required integrations:** Vendor adapter, evidence validator, promotion gate, local replay.
- **Observable acceptance:** Vendor-only fixture cannot create admitted formal evidence or release.
- **Dependencies:** S10-011, S13-006.
- **Ambiguity/contradiction notes:** Vendor results accompanied by replayable proof may be accepted through the ordinary local path.

### S13-044 — Acceptance bullet 14/18: adjudicator/model changes invalidate caches and cannot fake independence

- **Source:** §13.6, line 2073.
- **Faithful summary:** Changing the adjudicator/model invalidates incompatible stage caches and cannot produce a false “independent model” manifest.
- **Category:** acceptance; cache/identity security.
- **Inputs/outputs:** Adjudicator/model change and prior caches → invalidated incompatible caches plus provenance-correct manifest.
- **Invariants:** Actual lineage determines compatibility and independence; label changes alone do not.
- **Required failure behavior:** Fail cache reuse and deny independence credit on incomplete/correlated provenance.
- **Required integrations:** Model/adjudicator identity, cache graph, manifest projector, diversity profiler.
- **Observable acceptance:** Swap/alias/spoof tests invalidate correctly and never increase independence dimension falsely.
- **Dependencies:** S13-007, S13-032–S13-035.
- **Ambiguity/contradiction notes:** Compatible changes and model-lineage correlation criteria are unspecified.

### S13-045 — Acceptance bullet 15/18: enforce truth versus review precedence

- **Source:** §13.6, line 2074.
- **Faithful summary:** Model-referee dissent against a kernel proof follows the explicit truth/intent/novelty/significance precedence policy.
- **Category:** acceptance; conflict policy.
- **Inputs/outputs:** Clean kernel proof plus model dissent tagged by concern dimension → exact truth retained or relevant release dimension blocked/audited.
- **Invariants:** Model dissent does not negate exact kernel truth; nontruth dimensions remain independently blockable.
- **Required failure behavior:** Route incompatible hard evidence to conflict; route semantic/status concerns to their gates.
- **Required integrations:** Referee issue taxonomy, kernel verifier, promotion/release gates, conflict audit.
- **Observable acceptance:** Scenario matrix matches S13-010 for truth, intent, applicability, novelty, and significance dissent.
- **Dependencies:** S13-010.
- **Ambiguity/contradiction notes:** Applicability appears in S13-010 but not this bullet’s shortened list; it remains part of the source policy.

### S13-046 — Acceptance bullet 16/18: OEIS remains heuristic until proof

- **Source:** §13.6, line 2075.
- **Faithful summary:** An OEIS match stays heuristic until independently proved.
- **Category:** acceptance; retrieval evidence safety.
- **Inputs/outputs:** OEIS sequence/match and optional independent proof → heuristic candidate or admitted proved claim.
- **Invariants:** Match quality, transform, or metadata never self-promotes truth.
- **Required failure behavior:** Without proof, keep only candidate/search-prior status.
- **Required integrations:** Read-only OEIS client, typed transforms, claim/evidence router, proof verifier.
- **Observable acceptance:** High-confidence exact match does not change truth tier until independent evidence is attached.
- **Dependencies:** S13-015, S10-004, S11-009.
- **Ambiguity/contradiction notes:** “Independent proof” may be informal/formal/exact depending on claim scope; required tier is not specified.

### S13-047 — Acceptance bullet 17/18: classify known solutions as rediscovery

- **Source:** §13.6, line 2076.
- **Faithful summary:** A known solved Erdős problem must be classified as rediscovery, not novel.
- **Category:** acceptance; novelty/status integrity.
- **Inputs/outputs:** Produced result and dated status/prior-art evidence → `rediscovery`/known classification.
- **Invariants:** Mathematical correctness does not imply novelty.
- **Required failure behavior:** Prior-art match blocks novel label while preserving truth/progress evidence.
- **Required integrations:** Historical status snapshot, literature auditor, novelty certificate/report.
- **Observable acceptance:** Held-out known-solution fixtures never receive N2/new-result wording.
- **Dependencies:** S12-014, S11-012, S11-015.
- **Ambiguity/contradiction notes:** Alternative genuinely novel proofs of known theorems may need a finer novelty label not specified here.

### S13-048 — Acceptance bullet 18/18: baseline superiority requires paired evidence

- **Source:** §13.6, line 2077.
- **Faithful summary:** The system may not claim to beat a baseline unless paired evaluation supports the claim.
- **Category:** acceptance; evaluation reporting.
- **Inputs/outputs:** Paired system/baseline outcomes and uncertainty → supported or prohibited superiority statement.
- **Invariants:** No anecdotal/unpaired superiority claim.
- **Required failure behavior:** Suppress/qualify “beats” wording without paired support.
- **Required integrations:** Evaluation runner, pairing/seed registry, statistical report validator.
- **Observable acceptance:** Claim checker requires paired denominators/effect evidence before allowing superiority language.
- **Dependencies:** S12-006, S12-007, S12-029, S12-030.
- **Ambiguity/contradiction notes:** Statistical significance/effect-size threshold for “supports” is unspecified.

### S13-049 — Use the approximate M1/MVP evaluation-set composition

- **Source:** §13.7 “Evaluation set,” lines 2079–2089.
- **Faithful summary:** Use roughly 20 false/ambiguous elementary statements, a miniF2F/ProofNet# regression subset, 20 Putnam/IMO-style formal tasks, 10 literature-retrieval problems, 10 computation-plus-proof tasks, 20 historically solved Erdős problems across domains/cutoffs, and a small unsolved deployment set with no solve-rate claim.
- **Category:** evaluation dataset; milestone acceptance.
- **Inputs/outputs:** Versioned task sources → heterogeneous frozen evaluation manifest.
- **Invariants:** All seven categories appear; historical cases span domains/cutoffs; unsolved set has no solve-rate headline.
- **Required failure behavior:** Missing/contaminated categories are reported and block full-set claims.
- **Required integrations:** Benchmark registry, historical cutoff packets, sealed unsolved deployment set.
- **Observable acceptance:** Manifest counts approximate the listed targets and exposes provenance/category/cutoff for each item.
- **Dependencies:** S13-020, S12-001–S12-003.
- **Ambiguity/contradiction notes:** “Roughly,” “subset,” and “small” intentionally leave exact counts flexible.

### S13-050 — Optimize the MVP for safe measurable verified progress

- **Source:** §13.7, line 2091.
- **Faithful summary:** The milestone goal is safe, measurable, verified progress, not an immediate open-problem headline.
- **Category:** milestone objective; communication safety.
- **Inputs/outputs:** MVP runs/results → evidence-backed progress reporting with conservative claims.
- **Invariants:** Headline novelty/solve claims never substitute for the specified safety and measurement gates.
- **Required failure behavior:** Withhold headline claims when verification/evaluation is incomplete; issue honest no-result/progress report.
- **Required integrations:** Progress metrics, release certificate, communication layer.
- **Observable acceptance:** Milestone report leads with verified objects, false-success/calibration/cost evidence, and respects unsolved-set claim restrictions.
- **Dependencies:** S12-011, S12-015–S12-025, S13-048, S13-049.
- **Ambiguity/contradiction notes:** This is a priority principle rather than a quantitative pass threshold.

## Section 14 — Full-scale implementation

### S14-001 — Implement the specified full-scale service topology

- **Source:** §14.1 “Service topology,” lines 2095–2108.
- **Faithful summary:** Use PostgreSQL append-only events with optimistic object versions and transactional revocation; content-addressed object storage for sources/code/proof trees/builds/logs/containers; PostgreSQL graph adjacency/materialized closure initially and a dedicated graph engine only if profiling justifies it; hybrid lexical/vector/formula/type retrieval plus citation/dependency graphs; durable idempotent leased scheduler with heartbeats/quotas/preemption; isolated OCI/VM compute with network off by default; pinned multi-version Lean workers/live proof state/clean replay/independent checker; model gateway with exact identities, prompt hashes, cost/token telemetry, deterministic structured-output validation; event-derived observability for evidence/debt/branches/costs/limits/backlog; and a reproducible release builder, five-gate certificates, and human-review portal.
- **Category:** full-scale implementation; integration; security.
- **Inputs/outputs:** M2 state/workloads → integrated scalable truth, search, observability, and release services.
- **Invariants:** Authoritative events/artifacts remain append-only/content-addressed; network defaults off in compute; graph-engine complexity is profiling-gated; replay/checking remains separate from generation.
- **Required failure behavior:** Incompatible/unsafe/malformed work is rejected by typed service boundaries; transactional and lease recovery follow earlier requirements.
- **Required integrations:** All ten topology layers named in the source table.
- **Observable acceptance:** Deployment inventory and end-to-end trace demonstrate each layer, boundary, provenance link, and default network policy.
- **Dependencies:** S13-023–S13-030, S10-017–S10-021.
- **Ambiguity/contradiction notes:** Product choices, scale targets, SLAs, and profiling threshold for a graph engine are unspecified.

### S14-002 — Select and pin model versions by monthly local bake-off

- **Source:** §14.2 “Suggested model assignments,” lines 2110–2112.
- **Faithful summary:** Because model names drift quickly, choose exact versions through a monthly frozen local bake-off and pin them for each campaign.
- **Category:** operations; model governance; reproducibility.
- **Inputs/outputs:** Candidate exact versions and frozen bake-off → selected pinned campaign model registry.
- **Invariants:** Campaign execution does not float to mutable aliases; selection is local/task-relevant and versioned.
- **Required failure behavior:** Provider version drift creates a new contract/rebenchmark rather than transparent substitution.
- **Required integrations:** Model gateway, bake-off evaluation, run contracts, campaign configuration.
- **Observable acceptance:** Campaign manifest references exact version and preceding frozen bake-off dated within the selection cycle.
- **Dependencies:** S13-007, S12-004.
- **Ambiguity/contradiction notes:** “Monthly” cadence versus long campaign duration and provider inability to expose immutable versions need operational policy.

### S14-003 — Route each task class to the specified model/tool class and criterion

- **Source:** §14.2 table, lines 2114–2125.
- **Faithful summary:** Use two different frontier reasoning families plus symbolic parser for intake, selected by mutation/faithfulness accuracy; mixed fast/low-cost and one open model for program generation, selected by verified novel-branch yield/cost; strongest long-context model for central bottlenecks, selected by blind historical-Erdős progress; retrieval/reranker/source auditor for literature, selected by theorem/hypothesis precision/recall; strong sandboxed coding agent plus deterministic tools for experiments, selected by artifact validity/repair; specialized open Lean prover plus general code agent for Lean, selected by clean proof at matched cost/toolchain; optional proprietary formal service only for additional locally replayed proofs; different frontier family plus tools for informal referee, selected by first-error recall/low false acceptance; kernels/certificate checkers for final truth with deterministic acceptance only; and retrieval plus human domain experts for novelty/significance, with no model-only substitute.
- **Category:** full-scale integration; routing; evaluation.
- **Inputs/outputs:** Typed task and frozen candidate bake-off → routed model/tool pipeline and task-specific selection metric.
- **Invariants:** Final truth is deterministic; novelty/significance retain human experts; optional vendor output still replays locally; intake/referee diversity is explicit.
- **Required failure behavior:** Tool/model candidates that fail their task criterion or local replay are not selected/admitted.
- **Required integrations:** Symbolic parser, model portfolio, retrieval, sandbox, Lean, vendor adapter, deterministic checkers, experts.
- **Observable acceptance:** Router policy and bake-off report map every task class to its stated class and selection criterion.
- **Dependencies:** S14-002, S11-001, S11-014, S13-024, S13-027.
- **Ambiguity/contradiction notes:** Candidate product names are starting points, not mandates; exact thresholds and current models change over time.

### S14-004 — Never route by vendor score alone; persist reproducible identity

- **Source:** §14.2, line 2127.
- **Faithful summary:** Do not select routes solely from vendor benchmark scores; evaluate task-specific strengths and persist exact model identity because generic brand/UI names are not reproducible versions.
- **Category:** security; model governance; provenance.
- **Inputs/outputs:** Vendor scores, local task evidence, actual identity → routing decision and exact provenance.
- **Invariants:** Vendor marketing score has no sole authority; generic names remain unattested/insufficient.
- **Required failure behavior:** Deny reproducibility/independence credit when exact identity is missing.
- **Required integrations:** Bake-off, model gateway, cache/contract identity.
- **Observable acceptance:** Router ignores a higher vendor score when local criteria fail and stores immutable identity fields.
- **Dependencies:** S13-007, S14-002, S14-003.
- **Ambiguity/contradiction notes:** Acceptable fallback when providers expose no immutable identity remains unspecified.

### S14-005 — Parallelize only the specified independent work

- **Source:** §14.3 “Parallelization strategy,” lines 2129–2140.
- **Faithful summary:** Parallelize independent interpretations/status queries, genuinely different programs, independent AND-node leaves, proof/counterexample twins, retrieval modes/citation expansion, disjoint experiment parameters/seeds, Lean tactic branches from immutable goals, and independent verification/replay.
- **Category:** concurrency; orchestration; integration.
- **Inputs/outputs:** Dependency/bottleneck graph and immutable work units → concurrent jobs/results.
- **Invariants:** Parallel units are independent or immutable-snapshot-based; concurrency does not race shared truth state.
- **Required failure behavior:** Work discovered to share a mutable dependency is serialized/transactionally coordinated.
- **Required integrations:** Scheduler, AND/OR graph, branch fingerprints, retrieval/compute/Lean/replay services.
- **Observable acceptance:** Scheduler trace labels dependency rationale for each concurrent class and no forbidden shared-state races occur.
- **Dependencies:** S13-029, S10-021.
- **Ambiguity/contradiction notes:** Independence detection algorithm and maximum parallelism are unspecified.

### S14-006 — Serialize or transactionally coordinate shared truth/control changes

- **Source:** §14.3, lines 2142–2149.
- **Faithful summary:** Serialize or transactionally coordinate interpretation approval/target-hash changes, claim promotion/revocation, graph-schema migration, final proof assembly, release certificates, and provider quota/backoff state.
- **Category:** concurrency security; transactional integrity.
- **Inputs/outputs:** Concurrent mutations to six shared resources → ordered/atomic committed state.
- **Invariants:** No lost updates, split target identity, partial release, or quota race.
- **Required failure behavior:** Conflicts retry/abort atomically; partial externally authoritative state is prohibited.
- **Required integrations:** Transaction store, schema migration tooling, proof/release builder, quota manager.
- **Observable acceptance:** Concurrency tests across every listed resource produce one consistent serializable outcome.
- **Dependencies:** S10-013–S10-021, S14-001.
- **Ambiguity/contradiction notes:** Exact isolation level and whether serialization is global or keyed are unspecified.

### S14-007 — Constrain work stealing, bind leases completely, and reserve verifiers

- **Source:** §14.3, line 2151.
- **Faithful summary:** Permit work stealing only between compatible workers; bind a lease to problem, interpretation, branch, exact run contract, and budget; reserve a verification-worker pool so proof generation cannot starve truth admission.
- **Category:** scheduler security; resource isolation; recovery.
- **Inputs/outputs:** Queued job, worker capability/contract, verifier capacity → compatible assignment or denial and reserved service.
- **Invariants:** Lease context is complete; verification capacity cannot be consumed entirely by generation.
- **Required failure behavior:** Incompatible workers cannot steal; congestion throttles generation rather than eliminating truth checks.
- **Required integrations:** Scheduler, capability registry, leases, budgets, verifier queue.
- **Observable acceptance:** Compatibility/lease-field tests and saturation tests demonstrate reserved verifier throughput.
- **Dependencies:** S10-021, S13-026, S14-005.
- **Ambiguity/contradiction notes:** Reserved-pool size and worker compatibility predicate are unspecified.

### S14-008 — Maintain a quality-diversity archive of research-program families

- **Source:** §14.4 “Full-scale research programs,” lines 2153–2168.
- **Faithful summary:** At scale, use a quality-diversity archive rather than a fixed agent count, covering direct/structural, contradiction/minimal-counterexample, extremal/invariant, probabilistic/analytic, additive/combinatorial, algebraic/spectral, geometric/topological, ergodic/dynamical, computational finite reduction, formal-library-first, literature transfer, and counterexample/model construction profiles.
- **Category:** full-scale search implementation; diversity.
- **Inputs/outputs:** Domain/goal and program proposals/outcomes → archive entries across named mechanism families.
- **Invariants:** Diversity is mechanism-based, not role count; archive preserves quality/outcome evidence.
- **Required failure behavior:** Semantic/mechanistic duplicates do not inflate diversity.
- **Required integrations:** Mechanism fingerprints, branch controller, program archive, evaluation metrics.
- **Observable acceptance:** Archive schema can represent every family and diversity reports deduplicate equivalent programs.
- **Dependencies:** S12-021, S13-018, S13-026.
- **Ambiguity/contradiction notes:** The list may be extensible; quality metric and archive niche boundaries are unspecified.

### S14-009 — Instantiate programs only when compatible and give each controls

- **Source:** §14.4, line 2170.
- **Faithful summary:** The governor activates only profiles compatible with domain/current bottleneck, may protect cross-domain exploration, and gives every active program a falsifier, budget, and kill/pause criterion.
- **Category:** orchestration; safety; resource governance.
- **Inputs/outputs:** Domain/bottleneck/archive/profile → activated program with controls or nonactivation.
- **Invariants:** Every active program has all three controls; protected exploration is explicit.
- **Required failure behavior:** Incompatible profiles are not instantiated; exhausted/failed criteria pause or kill according to policy.
- **Required integrations:** Governor, domain classifier, falsifier, budget controller, branch lifecycle.
- **Observable acceptance:** Active-program inventory has compatibility rationale, falsifier, budget, and criteria for every entry.
- **Dependencies:** S10-005, S13-026, S14-008.
- **Ambiguity/contradiction notes:** Compatibility scoring, cross-domain fraction, and kill versus pause threshold are unspecified.

### S14-010 — Recover from rate limits/quotas without truth effects

- **Source:** §14.5 “Failure recovery,” line 2176.
- **Faithful summary:** On rate limit/quota, honor `Retry-After`, use jittered backoff no longer than 120 seconds, pause the lease, and reroute only if the contract allows; record a censored operational event with no truth effect.
- **Category:** failure behavior; provider integration.
- **Inputs/outputs:** Rate-limit/quota response and run contract → paused/backed-off/rerouted work and censored event.
- **Invariants:** Claim truth and mathematical retry budget are unchanged; reroute is contract-gated.
- **Required failure behavior:** No busy-loop, claim kill, or uncontracted provider switch.
- **Required integrations:** Provider adapter, quota/backoff manager, lease service, event log.
- **Observable acceptance:** Fault test verifies Retry-After/cap/jitter, pause, permitted reroute, and unchanged truth/retry state.
- **Dependencies:** S13-039, S14-007.
- **Ambiguity/contradiction notes:** If `Retry-After` exceeds 120 seconds, the line requires both honoring it and a backoff ≤120s; this needs interpretation (for example repeated capped pauses versus one longer wait).

### S14-011 — Recover from timeouts/process crashes compatibly

- **Source:** §14.5, line 2177.
- **Faithful summary:** On timeout/crash, checkpoint, expire/transfer the lease, and resume a compatible stage; truth is unchanged unless an artifact is incomplete.
- **Category:** failure behavior; recovery.
- **Inputs/outputs:** Timeout/crash and last durable state → checkpoint/recovered ownership/resumed compatible work.
- **Invariants:** Operational failure alone has no truth effect; incomplete artifacts are not admitted.
- **Required failure behavior:** Expire/transfer ownership safely and mark incomplete artifact rather than reuse it as complete.
- **Required integrations:** Checkpoints, leases, stage compatibility, artifact validator.
- **Observable acceptance:** Crash-boundary tests resume highest compatible stage with no duplicate action or false evidence.
- **Dependencies:** S10-020, S10-021, S13-040.
- **Ambiguity/contradiction notes:** Timeout thresholds and precise truth/evidence change for incomplete artifact are unspecified.

### S14-012 — Bound repair retries for malformed model output

- **Source:** §14.5, line 2178.
- **Faithful summary:** Preserve raw malformed output, attempt schema repair/retry only a bounded number of times, and admit no claim until valid.
- **Category:** failure behavior; model gateway security.
- **Inputs/outputs:** Malformed response → raw artifact, bounded repair attempts, valid typed result or terminal failure.
- **Invariants:** Raw evidence is retained; malformed payload never becomes an admitted claim.
- **Required failure behavior:** Stop after bounded attempts and record failure.
- **Required integrations:** Structured-output validator, artifact store, retry accounting, evidence router.
- **Observable acceptance:** Repeated-malformation fixture stops at configured bound and creates no admitted claim.
- **Dependencies:** S10-010, S14-001.
- **Ambiguity/contradiction notes:** Retry bound and permitted repair transformations are unspecified.

### S14-013 — Keep unavailable/conflicting sources unresolved

- **Source:** §14.5, line 2179.
- **Faithful summary:** Cache the known source version, mark a provenance gap, seek alternate source or human task, and keep novelty/import unresolved when a source is unavailable or conflicting.
- **Category:** failure behavior; retrieval/source integrity.
- **Inputs/outputs:** Failed/conflicting source access → cached known bytes, gap record, alternative/human task, unresolved dimension.
- **Invariants:** Absence/conflict never becomes positive novelty/applicability evidence.
- **Required failure behavior:** Fail closed to unresolved while preserving available provenance.
- **Required integrations:** Source cache, provenance gaps, retrieval, human task queue, release profile.
- **Observable acceptance:** Unavailable/conflict fixtures cannot reach audited import/novelty state and create remediation tasks.
- **Dependencies:** S10-022, S11-007, S12-010.
- **Ambiguity/contradiction notes:** Required alternate-source equivalence proof and timeout for human escalation are unspecified.

### S14-014 — Recover from wrong interpretation by changing lattice node and downgrading dependents

- **Source:** §14.5, line 2180.
- **Faithful summary:** Create or reselect an interpretation-lattice node, revoke dependent formal correspondence, and downgrade dependent claims when the interpretation is wrong.
- **Category:** failure behavior; semantic recovery; revocation.
- **Inputs/outputs:** Wrong-interpretation finding → new/reselected interpretation, revoked certificates/edges, dependent downgrades.
- **Invariants:** Proof of the old encoding remains historically distinct; intended-target support cannot survive invalid correspondence.
- **Required failure behavior:** Transactionally remove affected correspondence and fail closed downstream.
- **Required integrations:** Interpretation lattice, correspondence certificates, dependency graph, revocation.
- **Observable acceptance:** Interpretation mutation fixture preserves old history but blocks/downgrades all dependent intended-target claims.
- **Dependencies:** S10-002, S10-008, S10-013, S13-037.
- **Ambiguity/contradiction notes:** Whether a wrong interpretation is rejected or retained as a valid special-case node depends on relation semantics and is unspecified.

### S14-015 — Recover from a false lemma with exact graph revocation

- **Source:** §14.5, line 2181.
- **Faithful summary:** Attach the counterexample, transactionally revoke the dependent closure, reopen alternatives, and record the explicit graph update.
- **Category:** failure behavior; mathematical refutation.
- **Inputs/outputs:** Valid counterexample to lemma → evidence, root status, revoked/downgraded closure, reopened branches/events.
- **Invariants:** Counterexample is retained; propagation is atomic and alternatives are reconsidered.
- **Required failure behavior:** No dependent promotion survives and no partial closure update appears.
- **Required integrations:** Exact witness checker, claim graph, branch controller, event log.
- **Observable acceptance:** False-lemma injection meets S13-038 plus alternative reopening.
- **Dependencies:** S10-015, S13-038.
- **Ambiguity/contradiction notes:** “Revoke closure” should be implemented as evidence/status recomputation rather than necessarily lifecycle retraction of every claim.

### S14-016 — Contain Lean statement mismatch to the old encoded theorem

- **Source:** §14.5, line 2182.
- **Faithful summary:** Reject the certificate for the intended target, repair target candidates, and retain the formal proof only for the old exact encoded theorem.
- **Category:** failure behavior; formal semantic safety.
- **Inputs/outputs:** Correspondence mismatch → rejected intended-target certificate, candidate repair work, scoped old-theorem proof.
- **Invariants:** Kernel truth of old encoding is not erased or generalized to intent.
- **Required failure behavior:** Block intended-target release and initiate target repair.
- **Required integrations:** Correspondence validator, Lean artifact store, interpretation/target candidate generator.
- **Observable acceptance:** Mismatch test leaves T4-like evidence bound only to old type and denies intended claim.
- **Dependencies:** S10-008, S11-016, S14-014.
- **Ambiguity/contradiction notes:** Whether repaired target requires a wholly new claim/declaration is implied by immutability but not restated.

### S14-017 — Scope and pause formal-library-gap work

- **Source:** §14.5, line 2183.
- **Faithful summary:** On a formal library gap, create a scoped local-library project, estimate cost, and pause or redirect the branch.
- **Category:** failure behavior; formal engineering; resource control.
- **Inputs/outputs:** Missing formal dependency → scoped project/cost estimate and branch decision.
- **Invariants:** Library work has explicit scope/cost and does not silently consume unlimited proof budget.
- **Required failure behavior:** Pause/redirect until the gap is funded/resolved.
- **Required integrations:** Lean library project manager, cost estimator, branch controller.
- **Observable acceptance:** Missing-dependency fixture creates a linked project and branch state/reason rather than repeated proof failures.
- **Dependencies:** S10-005, S13-017.
- **Ambiguity/contradiction notes:** Cost threshold and reuse/publication policy for local libraries are unspecified.

### S14-018 — Quarantine computation mismatches and revoke support

- **Source:** §14.5, line 2184.
- **Faithful summary:** On computation mismatch, quarantine the artifact, independently reimplement, revoke dependents, and remove relevant evidence.
- **Category:** failure behavior; compute integrity.
- **Inputs/outputs:** Replay/reimplementation mismatch → quarantined artifact, new independent job, evidence invalidation, dependent downgrades.
- **Invariants:** Mismatched output remains preserved for audit but has no supporting authority.
- **Required failure behavior:** Fail closed immediately and propagate transactional evidence removal.
- **Required integrations:** Compute replay, quarantine, evidence invalidation, claim graph.
- **Observable acceptance:** Mismatch fixture removes all dependent support and schedules independent reimplementation.
- **Dependencies:** S10-014, S11-009, S13-041.
- **Ambiguity/contradiction notes:** Whether one matching reimplementation rehabilitates the original artifact is unspecified.

### S14-019 — Invalidate and replay evaluator reward hacks

- **Source:** §14.5, line 2185.
- **Faithful summary:** If an evaluator is hacked, invalidate the fitness run, strengthen the multi-objective checker, replay the population, and admit no winner from the compromised run.
- **Category:** failure behavior; evaluation security; evolutionary integration.
- **Inputs/outputs:** Reward-hack detection and population/artifacts → invalidated fitness run, patched checker, replayed results.
- **Invariants:** Compromised fitness cannot select/admit a winner; old evidence remains auditable.
- **Required failure behavior:** Fail entire affected fitness run closed, not only the discovered individual.
- **Required integrations:** Evolutionary search, evaluator/checker, run invalidation, population replay.
- **Observable acceptance:** Adversarial fixture invalidates all affected winners and only post-patch replay may admit results.
- **Dependencies:** S10-014, S12-019.
- **Ambiguity/contradiction notes:** Scope of affected population and checker-hardening approval are unspecified.

### S14-020 — Version provider drift under a new run contract

- **Source:** §14.5, line 2186.
- **Faithful summary:** On model/provider version drift, create a new run contract, invalidate incompatible caches, re-benchmark, and retain old verified artifacts as versioned artifacts.
- **Category:** failure behavior; provenance; cache recovery.
- **Inputs/outputs:** Detected drift → new contract/cache state/bake-off while preserving old artifacts.
- **Invariants:** No mutable alias silently changes campaign behavior; old valid evidence remains bound to its old environment.
- **Required failure behavior:** Block incompatible replay/continuation until new contract and benchmark are established.
- **Required integrations:** Model gateway, contract/cache manager, bake-off, artifact store.
- **Observable acceptance:** Drift simulation creates a new contract hash, cache misses, rebenchmark task, and unchanged old artifact record.
- **Dependencies:** S13-007, S14-002, S14-004.
- **Ambiguity/contradiction notes:** Drift detection source and compatibility exceptions are unspecified.

### S14-021 — Price congestion and reserve verification during backlog

- **Source:** §14.5, line 2187.
- **Faithful summary:** On verification backlog, apply congestion pricing, throttle generators, and reserve verifier workers; truth status is not downgraded merely due to backlog.
- **Category:** failure behavior; scheduling; truth separation.
- **Inputs/outputs:** Verifier queue/congestion metrics → generation throttle/allocation changes.
- **Invariants:** Operational backlog does not change mathematical truth; verifier capacity remains available.
- **Required failure behavior:** Slow/stop new generation before starving truth admission.
- **Required integrations:** Scheduler/controller, telemetry, verifier pool.
- **Observable acceptance:** Saturation test reduces generation and maintains verifier service without claim downgrade.
- **Dependencies:** S13-026, S14-007.
- **Ambiguity/contradiction notes:** Price/throttle formula and backlog threshold are unspecified.

### S14-022 — Pause stagnating branches and escalate methods without false killing

- **Source:** §14.5, line 2188.
- **Faithful summary:** On repeated stagnation, retrieve targeted sources, try counterfactual variants and a new method family, and escalate to a human; pause the branch rather than falsely killing it.
- **Category:** failure behavior; search recovery.
- **Inputs/outputs:** Stagnation signal → remediation tasks, paused state, human escalation/reopen conditions.
- **Invariants:** Lack of progress is not mathematical refutation; pause preserves reopenability.
- **Required failure behavior:** Stop repeated waste while retaining branch history/possibility.
- **Required integrations:** Repetition detector, retrieval, program archive, branch controller, human queue.
- **Observable acceptance:** Stagnation fixture triggers each remediation class and `paused`, not false/`killed`, status.
- **Dependencies:** S10-005, S12-021, S14-008, S14-009.
- **Ambiguity/contradiction notes:** “Repeated” threshold and whether all remedies are mandatory or alternatives are unspecified.

### S14-023 — Design around stated compute bottlenecks and mitigations

- **Source:** §14.6 “Compute bottlenecks,” lines 2190–2201.
- **Faithful summary:** Capacity planning must account for semantic/expert review, formalization/library engineering, Lean search, retrieval/index maintenance, exact enumeration, branch explosion, model inference, and reproducibility storage. Mitigate with direct-first proofs, risk-weighted formalization, exact caches, safe live Lean snapshots, premise retrieval, branch caps, verification-congestion pricing, and verified-progress-per-cost routing.
- **Category:** performance; resource architecture; risk mitigation.
- **Inputs/outputs:** Workload/cost/queue/storage metrics → capacity and routing decisions using the listed mitigations.
- **Invariants:** Verification and semantics can be binding bottlenecks; more model inference/branches is not assumed better.
- **Required failure behavior:** Congestion/explosion triggers caps/pricing/rerouting rather than uncontrolled scale.
- **Required integrations:** Expert/Lean/retrieval/compute/storage services, controller, cost telemetry.
- **Observable acceptance:** Load tests/operational dashboards expose all eight bottleneck classes and demonstrate applicable mitigations.
- **Dependencies:** S12-021, S12-022, S13-026, S14-021.
- **Ambiguity/contradiction notes:** The text says “mitigate with” but does not assign each mitigation to a bottleneck or specify SLOs.

### S14-024 — Keep required human roles explicit and record every intervention

- **Source:** §14.7 “Human role in the scaled system,” lines 2203–2215.
- **Faithful summary:** Humans remain required to resolve genuine intent ambiguity; access/understand specialized or unavailable literature; adjudicate significance/publication novelty; review central convincing but incompletely formalized claims; authorize public submissions and OEIS interactions; set value weights/acceptable risk; and respond to potential major results. Minimize routine labor without hiding it under “autonomous”; record every intervention.
- **Category:** human integration; governance; transparency; security.
- **Inputs/outputs:** Escalation/authorization/review/value-setting events → authenticated human decisions and intervention telemetry.
- **Invariants:** Listed authority is not silently delegated to model-only substitutes; interventions remain visible in autonomy profile.
- **Required failure behavior:** Block actions requiring human authority until obtained; record unresolved escalation rather than impersonating approval.
- **Required integrations:** Human task/review portal, submission/OEIS controls, value/risk configuration, event/autonomy logs.
- **Observable acceptance:** Workflow tests require authenticated approval for each governed action and release reports enumerate interventions.
- **Dependencies:** S10-022, S11-015, S11-022, S14-013.
- **Ambiguity/contradiction notes:** Reviewer qualifications, authorization hierarchy, and response protocol for major results are unspecified.

## Section 15 — Major unresolved engineering and research risks

### S15-001 — Mitigate wrong-formalization risk

- **Source:** §15 risk table, line 2221.
- **Faithful summary:** Treat proving a convenient wrong theorem as high-likelihood/critical; mitigate with an interpretation lattice, multiple translations, mutation tests, and human target review while acknowledging semantic equivalence can remain hard.
- **Category:** security risk; semantic mitigation.
- **Inputs/outputs:** Source/target/formal candidates → reviewed interpretations, mutation evidence, approved/unresolved target.
- **Invariants:** Formal success never substitutes for semantic fidelity.
- **Required failure behavior:** Unresolved equivalence blocks intended-target claim.
- **Required integrations:** Interpretation lattice, parsers, mutation suite, human review, correspondence certificate.
- **Observable acceptance:** Wrong-target injections are detected before intended release.
- **Dependencies:** S10-002, S10-008, S11-003, S14-014.
- **Ambiguity/contradiction notes:** Residual uncertainty is explicit; no complete equivalence decision procedure is promised.

### S15-002 — Mitigate false admission by LLM verifiers

- **Source:** §15 risk table, line 2222.
- **Faithful summary:** Treat false central-fact admission by an LLM verifier as high/critical; use evidence-specific validators, kernel/exact replay, and revocation, recognizing many research claims lack hard checkers.
- **Category:** security risk; truth admission.
- **Inputs/outputs:** Model review and candidate evidence → typed hard validation or unresolved/informal review status.
- **Invariants:** LLM approval alone is not hard truth evidence.
- **Required failure behavior:** Fail closed or retain lower tier when hard checks are unavailable; revoke on later failure.
- **Required integrations:** Evidence router, kernel/compute checkers, revocation graph.
- **Observable acceptance:** Model-approved false fixture cannot pass a hard-evidence gate and injected admission can be revoked.
- **Dependencies:** S10-010–S10-015, S11-014.
- **Ambiguity/contradiction notes:** Residual claims without checkers rely on T3/human processes rather than eliminating the risk.

### S15-003 — Mitigate hidden circularity and opaque imports

- **Source:** §15 risk table, line 2223.
- **Faithful summary:** Treat hidden circularity/import dependency as medium-high/critical; mitigate with source/dependency graph, independent proof reconstruction, and taint analysis while exposing opaque literature dependencies as residual uncertainty.
- **Category:** dependency security risk.
- **Inputs/outputs:** Proof/import graph and source availability → cycle/taint/reconstruction report.
- **Invariants:** Opaque dependencies do not become clean dependencies by omission.
- **Required failure behavior:** Unresolved cycles/opacity taint and block dependents.
- **Required integrations:** Graph/SCC, source audit, independent referee, taint propagation.
- **Observable acceptance:** Cycle/opaque-import fixtures propagate taint and cannot promote.
- **Dependencies:** S11-005, S11-006, S11-013.
- **Ambiguity/contradiction notes:** Full literature proof closure may be unattainable; unresolved state is required.

### S15-004 — Mitigate rediscovery-as-novelty risk

- **Source:** §15 risk table, line 2224.
- **Faithful summary:** Treat rediscovery marketed as novelty as high/high; use frozen broad retrieval, citation graphs, separate novelty audit, and experts, while admitting absence of prior art cannot be proved.
- **Category:** novelty risk; evaluation/communication security.
- **Inputs/outputs:** Claim and frozen search space → search packet, expert novelty verdict, disclosed gaps.
- **Invariants:** Truth does not imply novelty; negative search is not proof of absence.
- **Required failure behavior:** Gaps/unresolved prior art prevent strong novelty label.
- **Required integrations:** Retrieval/citation graph, novelty auditor, experts, release profile.
- **Observable acceptance:** Known-solution fixtures become rediscoveries and search gaps remain visible.
- **Dependencies:** S11-012, S13-047, S14-024.
- **Ambiguity/contradiction notes:** No finite search can eliminate residual uncertainty.

### S15-005 — Mitigate evaluator/reward hacking

- **Source:** §15 risk table, line 2225.
- **Faithful summary:** Treat reward hacking as high in evolutionary search/high impact; use an independent checker, multi-objective fitness, and adversarial tests, while recognizing specification loopholes remain.
- **Category:** evaluation security risk.
- **Inputs/outputs:** Candidate/evaluator behavior → independent multi-objective validation and adversarial findings.
- **Invariants:** One exploitable scalar evaluator cannot admit winners.
- **Required failure behavior:** Invalidate compromised fitness runs and replay under strengthened checker.
- **Required integrations:** Evolution engine, checker, adversarial suite, invalidation/replay.
- **Observable acceptance:** Reward-hack fixtures fail or invalidate population results.
- **Dependencies:** S14-019.
- **Ambiguity/contradiction notes:** Independent checker design and objective weights remain open.

### S15-006 — Mitigate correlated multi-agent consensus

- **Source:** §15 risk table, line 2226.
- **Faithful summary:** Treat correlated consensus as high/high; require tool/model/information independence metadata and never promote from consensus alone, recognizing model families may share training data.
- **Category:** verification security risk.
- **Inputs/outputs:** Multiple reviews/proposals and provenance → diversity profile and search signal only.
- **Invariants:** Consensus has no direct truth-tier authority.
- **Required failure behavior:** Deny independence/truth credit when evidence of separation is insufficient.
- **Required integrations:** Identity/diversity profile, truth promotion, controller.
- **Observable acceptance:** Correlated-agreement fixture changes at most search priority.
- **Dependencies:** S11-002, S11-021.
- **Ambiguity/contradiction notes:** True information independence is often unknowable; metadata is evidence, not proof.

### S15-007 — Mitigate branch explosion and nontermination

- **Source:** §15 risk table, line 2227.
- **Faithful summary:** Treat branch explosion/nontermination as high/high; mitigate with posterior budgets, deduplication, pause rules, and verification-congestion controls, while acknowledging initially weak value estimates.
- **Category:** orchestration risk; resource safety.
- **Inputs/outputs:** Branch proposals/posteriors/congestion → bounded allocations, merges, pauses.
- **Invariants:** Search cannot grow unbounded; weak priors remain uncertain.
- **Required failure behavior:** Cap/pause low-value or duplicate work and preserve reopen conditions.
- **Required integrations:** Branch controller, fingerprint dedup, budgets, verifier queue.
- **Observable acceptance:** Stress test bounds active branches/spend and avoids verifier starvation.
- **Dependencies:** S13-026, S14-009, S14-021–S14-023.
- **Ambiguity/contradiction notes:** Branch caps/budget thresholds are unspecified.

### S15-008 — Mitigate easy-domain selector feedback

- **Source:** §15 risk table, line 2228.
- **Faithful summary:** Treat self-reinforcement toward easy domains as medium-high/medium; use protected exploration, hierarchical calibration, and domain quotas while recognizing verified outcomes are sparse.
- **Category:** selection/evaluation risk; fairness/coverage.
- **Inputs/outputs:** Problem candidates, domain labels, posterior data → quota/exploration-aware selection.
- **Invariants:** Short-term easy-domain yield cannot consume all selection capacity.
- **Required failure behavior:** Sparse calibration widens uncertainty/protects exploration rather than overconfident exclusion.
- **Required integrations:** Problem selector, domain classifier, calibration, protected exploration.
- **Observable acceptance:** Simulation preserves quota/exploration coverage under skewed easy-domain rewards.
- **Dependencies:** S12-023, S13-026.
- **Ambiguity/contradiction notes:** Domain taxonomy and quotas are unspecified.

### S15-009 — Mitigate benchmark contamination and saturation

- **Source:** §15 risk table, line 2229.
- **Faithful summary:** Treat benchmark contamination/saturation as high/high; use rotating or sealed sets, dated snapshots, and mutation suites while acknowledging opaque model training data.
- **Category:** evaluation risk; contamination security.
- **Inputs/outputs:** Benchmark/model exposure evidence → sealed/rotating campaign and contamination caveats.
- **Invariants:** Absence of known overlap is not proof of clean training.
- **Required failure behavior:** Detected leakage qualifies/invalidates held-out claims.
- **Required integrations:** Dataset registry, access control, dated packets, mutation generator.
- **Observable acceptance:** Evaluation reports include exposure audit and sealed/dated provenance.
- **Dependencies:** S12-005, S12-014, S12-031.
- **Ambiguity/contradiction notes:** Rotation frequency and contamination thresholds are unspecified.

### S15-010 — Mitigate erroneous benchmarks

- **Source:** §15 risk table, line 2230.
- **Faithful summary:** Treat benchmark error as medium/high; version sources/statements, conduct semantic audits, and issue corrections, recognizing expert datasets still contain errors.
- **Category:** evaluation risk; provenance.
- **Inputs/outputs:** Benchmark source/statement/audit → versioned accepted target or correction/new version.
- **Invariants:** Benchmark is not infallible ground truth; corrections preserve history.
- **Required failure behavior:** Correct and rerun affected evaluations rather than silently patching scores.
- **Required integrations:** Benchmark registry, semantic review, rerun scheduler.
- **Observable acceptance:** Seeded benchmark error yields a correction version and linked reruns.
- **Dependencies:** S12-003, S12-032.
- **Ambiguity/contradiction notes:** Semantic-audit quorum and correction severity are unspecified.

### S15-011 — Mitigate unsafe formal trust paths

- **Source:** §15 risk table, line 2231.
- **Faithful summary:** Treat unsafe formal trust paths as medium/critical; require clean environment, axiom/unsafe scan, and independent checker, while acknowledging proof-assistant/toolchain bugs remain possible.
- **Category:** formal/security risk.
- **Inputs/outputs:** Formal bundle/environment → TCB/axiom/unsafe/checker audit.
- **Invariants:** Kernel result is scoped to audited TCB and imports.
- **Required failure behavior:** Unsafe/unapproved path blocks hardened formal release.
- **Required integrations:** Lean farm, scanners, independent checker, release certificate.
- **Observable acceptance:** Unsafe metaprogram/axiom/toolchain fixtures are rejected or explicitly disclosed below T5.
- **Dependencies:** S11-010, S11-014, S13-042.
- **Ambiguity/contradiction notes:** No system can eliminate underlying checker bugs; trust assumptions must remain recorded.

### S15-012 — Mitigate proprietary service drift/outage

- **Source:** §15 risk table, line 2232.
- **Faithful summary:** Treat proprietary drift/outage as high/medium; maintain provider abstraction, an open baseline, and exact version contracts, while recognizing strongest features may stay closed.
- **Category:** integration/availability risk; reproducibility.
- **Inputs/outputs:** Vendor service/version/availability → compatible provider route or censored/unavailable result.
- **Invariants:** Core truth/replay path does not depend solely on mutable hosted status.
- **Required failure behavior:** Drift/outage does not masquerade as math failure; invalidate/recontract/reroute only as allowed.
- **Required integrations:** Provider abstraction, open baseline, model contracts, local verification.
- **Observable acceptance:** Outage/drift simulation preserves open baseline and provenance-correct recovery.
- **Dependencies:** S12-006, S14-020.
- **Ambiguity/contradiction notes:** Capability degradation during outage is accepted residual risk.

### S15-013 — Mitigate irreproducible or numerically unsound computation

- **Source:** §15 risk table, line 2233.
- **Faithful summary:** Treat compute irreproducibility/numerical unsoundness as medium/high; use exact arithmetic, containers, seeds, coverage, and certificates, while recognizing huge runs strain independent replay.
- **Category:** compute/security risk.
- **Inputs/outputs:** Computational claim/job → exact/provenance-bound artifact, coverage and replay/certificate.
- **Invariants:** Numerical approximation does not become exact evidence; seed and environment are retained.
- **Required failure behavior:** Replay/coverage mismatch quarantines and revokes evidence.
- **Required integrations:** Compute lab, replay containers, certificate adapters, evidence graph.
- **Observable acceptance:** Numeric-unsoundness and nondeterminism fixtures fail exact evidence admission.
- **Dependencies:** S11-009, S13-016, S13-041, S14-018.
- **Ambiguity/contradiction notes:** Very large computations may need certificate rather than full independent rerun; threshold is unspecified.

### S15-014 — Mitigate literature access and licensing gaps

- **Source:** §15 risk table, line 2234.
- **Faithful summary:** Treat literature access/licensing gaps as medium/high; preserve source provenance, use authorized human access, and keep novelty `unknown` when coverage is incomplete.
- **Category:** source/compliance risk.
- **Inputs/outputs:** Inaccessible/licensed source → gap record, authorized human task, unresolved novelty.
- **Invariants:** Access gaps are disclosed and never interpreted as absence of prior art.
- **Required failure behavior:** Respect licenses/privacy and fail novelty/import to unknown.
- **Required integrations:** Source store, access controls, human review, novelty certificate.
- **Observable acceptance:** Inaccessible-source fixture produces a gap and no N2 claim.
- **Dependencies:** S14-013, S14-024, S12-033.
- **Ambiguity/contradiction notes:** No universal full-text corpus is assumed; authorization process is unspecified.

### S15-015 — Mitigate malicious source, code, or Lean metaprograms

- **Source:** §15 risk table, line 2235.
- **Faithful summary:** Treat malicious inputs/code/Lean metaprograms as medium/critical; use sandboxing, network-off defaults, allowlisted imports/tools, and a minimal trusted computing base, with ongoing supply-chain risk acknowledged.
- **Category:** cybersecurity; sandbox/security risk.
- **Inputs/outputs:** Untrusted source/code/formal artifact → isolated execution, allowlist decision, security audit/result.
- **Invariants:** Network is off by default; only allowlisted imports/tools cross the boundary; TCB is minimized/documented.
- **Required failure behavior:** Deny/terminate violations, preserve forensic artifacts safely, admit no resulting claim.
- **Required integrations:** OCI/VM sandbox, network policy, allowlist, formal scanner, supply-chain verification.
- **Observable acceptance:** Escape/network/import/metaprogram adversarial tests are contained and logged.
- **Dependencies:** S14-001, S13-016, S11-010.
- **Ambiguity/contradiction notes:** Concrete sandbox hardening and supply-chain update policy are unspecified.

### S15-016 — Mitigate persistent-memory contamination

- **Source:** §15 risk table, line 2236.
- **Faithful summary:** Treat persistent-memory contamination as medium/critical; permit verified-only semantic memory, quarantine uncertain material, and support revocation, while acknowledging validators may still be wrong.
- **Category:** memory security risk.
- **Inputs/outputs:** Candidate/revoked memory object → trusted tier, quarantine, or propagated removal.
- **Invariants:** Cross-problem semantic reuse is evidence- and scope-bound.
- **Required failure behavior:** Validator/evidence failure revokes affected memory and dependents.
- **Required integrations:** Memory-tier policy, replay/audit, quarantine, graph revocation.
- **Observable acceptance:** False-memory injection cannot contaminate trusted cross-problem results and later invalidation propagates.
- **Dependencies:** S10-023, S10-014.
- **Ambiguity/contradiction notes:** “Verified-only” still carries stated TCB assumptions; no infallibility claim.

### S15-017 — Mitigate communication overstatement

- **Source:** §15 risk table, line 2237.
- **Faithful summary:** Treat evidence overstatement as high/high; generate a five-gate certificate mechanically and use fixed vocabulary, while acknowledging external summaries may strip caveats.
- **Category:** communication safety risk.
- **Inputs/outputs:** Release profile → fixed-vocabulary certificate/rendering.
- **Invariants:** Evidence dimensions/caveats remain explicit in primary communication.
- **Required failure behavior:** Block unsupported labels/confidence compression; retain machine-readable certificate even if summaries diverge.
- **Required integrations:** Release builder, vocabulary validator, communication layer.
- **Observable acceptance:** Claim-lint tests reject overbroad labels and primary release carries all gates.
- **Dependencies:** S11-022, S11-023, S13-019.
- **Ambiguity/contradiction notes:** Downstream third-party summaries cannot be fully controlled; “five-gate” versus six dimensions including autonomy should be documented.

### S15-018 — Mitigate the human verification bottleneck

- **Source:** §15 risk table, line 2238.
- **Faithful summary:** Treat human verification scarcity as high/high; prioritize central risks, use proof assistants and reviewer tooling, while accepting major proofs still require scarce experts.
- **Category:** resource risk; human integration.
- **Inputs/outputs:** Review backlog and graph risk/centrality → prioritized human assignments/tool-assisted review.
- **Invariants:** Scarcity does not justify skipping central review or pretending autonomy.
- **Required failure behavior:** Lower-priority work waits/pauses; unreviewed central claims remain unreleased.
- **Required integrations:** Risk-weighted graph, reviewer portal, proof assistants, congestion controller.
- **Observable acceptance:** Review queue prioritizes central risk and release blocks on missing required expert review.
- **Dependencies:** S12-018, S14-021, S14-024.
- **Ambiguity/contradiction notes:** Reviewer-capacity SLO and prioritization formula are unspecified.

### S15-019 — Experimentally validate the interpretation lattice

- **Source:** §15 “Research risks specific to the proposed innovations,” line 2242.
- **Faithful summary:** Test whether the interpretation lattice prevents enough wrong-target work to justify the extra search it creates.
- **Category:** research-risk evaluation; ablation.
- **Inputs/outputs:** Lattice-on/off controlled runs → wrong-target prevention, cost, search-multiplication effect.
- **Invariants:** The lattice is a hypothesis, not presumed beneficial.
- **Required failure behavior:** Do not claim advantage if prevention does not justify cost under preregistered metrics.
- **Required integrations:** Interpretation subsystem, ablation runner, cost/false-target metrics.
- **Observable acceptance:** Controlled result reports both avoided defects and overhead.
- **Dependencies:** S12-012, S12-027, S15-001.
- **Ambiguity/contradiction notes:** “Enough” requires a preregistered utility threshold.

### S15-020 — Ablate cold-pass budget at 0%, 5%, and 10%

- **Source:** §15 research risks, line 2243.
- **Faithful summary:** Because a cold pass may waste budget or still anchor on pretrained literature, compare 0%, 5%, and 10% allocations.
- **Category:** research-risk evaluation; ablation.
- **Inputs/outputs:** Fixed campaigns with three cold-pass fractions → verified progress/cost/anchoring results.
- **Invariants:** Fractions are explicitly controlled; pretrained anchoring remains a caveat.
- **Required failure behavior:** Do not claim cold-pass benefit without the ablation.
- **Required integrations:** Retrieval policy, budget controller, contamination/anchoring evaluation.
- **Observable acceptance:** Report contains all three treatment arms under causal controls.
- **Dependencies:** S12-012, S12-026.
- **Ambiguity/contradiction notes:** §12.5 describes literature modes but not these exact fractions; the requirements are complementary, not contradictory.

### S15-021 — Validate posterior branch allocation against simple search

- **Source:** §15 research risks, line 2244.
- **Faithful summary:** Treat posterior branch-controller benefit as uncertain because sparse/nonstationary outcomes may make it worse than simple best-first search.
- **Category:** research-risk evaluation; controller.
- **Inputs/outputs:** Matched controller runs/data regime → verified progress/cost/calibration comparison.
- **Invariants:** Learned/posterior complexity is not presumed superior.
- **Required failure behavior:** Retain/fallback to simple best-first when evidence does not support posterior allocation.
- **Required integrations:** Both controller implementations, calibration, ablation runner.
- **Observable acceptance:** Equal-contract comparison reports uncertainty and nonstationarity sensitivity.
- **Dependencies:** S12-026, S13-018, S13-026.
- **Ambiguity/contradiction notes:** Required fallback threshold and data sufficiency are unspecified.

### S15-022 — Test risk-weighted Lean sentinels for missed subtle steps

- **Source:** §15 research risks, line 2245.
- **Faithful summary:** Evaluate whether centrality/risk estimates used for Lean sentinels miss the true subtle step.
- **Category:** research-risk evaluation; formalization.
- **Inputs/outputs:** Frozen proof blueprint/risk ranking and known/injected subtle steps → sentinel coverage/miss metrics.
- **Invariants:** Risk estimates are hypotheses and cannot certify unsentinelized steps by omission.
- **Required failure behavior:** Misses trigger recalibration/expanded review rather than false coverage claims.
- **Required integrations:** Risk graph, target sentinels, formalization/review, ablation.
- **Observable acceptance:** Seeded-subtlety suite reports recall weighted by downstream risk.
- **Dependencies:** S12-018–S12-020, S13-017.
- **Ambiguity/contradiction notes:** Ground truth for subtle research steps may require expert audit.

### S15-023 — Credit verified DAG nodes by downstream unlock, not count

- **Source:** §15 research risks, line 2246.
- **Faithful summary:** A verified lemma may be useless to the target; measure downstream paths unlocked rather than node count.
- **Category:** research-risk evaluation; anti-gaming.
- **Inputs/outputs:** Newly verified node and before/after blueprint reachability → downstream-unlock credit.
- **Invariants:** Raw verified-node count is insufficient value evidence.
- **Required failure behavior:** Give no/limited progress credit to isolated lemmas with no target/reuse effect, except separately valued reusable infrastructure.
- **Required integrations:** AND/OR graph, proof-debt/unlock metrics, progress scorer.
- **Observable acceptance:** Test distinguishes many isolated easy lemmas from one central path-unlocking lemma.
- **Dependencies:** S12-017, S12-019, S12-025.
- **Ambiguity/contradiction notes:** Reusable cross-problem value may justify separate credit; exact combination is unspecified.

### S15-024 — Test cross-problem reuse reward for distortion

- **Source:** §15 research risks, line 2247.
- **Faithful summary:** Evaluate whether rewarding cross-problem reuse biases search toward library work and away from decisive problem-specific insight.
- **Category:** research-risk evaluation; reward design.
- **Inputs/outputs:** Reward-on/off or weighted runs → reuse, target progress, cost, opportunity-cost metrics.
- **Invariants:** Reuse is not assumed valuable without downstream effect.
- **Required failure behavior:** Reduce/remove reward if it harms decisive verified target progress under preregistered criteria.
- **Required integrations:** Cross-problem library, controller fitness, downstream-reuse tracking, ablation.
- **Observable acceptance:** Controlled report measures both actual reuse and displaced target progress.
- **Dependencies:** S12-012, S15-023.
- **Ambiguity/contradiction notes:** Required experimental arms/weights are not specified.

### S15-025 — Do not equate different providers with proof independence

- **Source:** §15 research risks, line 2248.
- **Faithful summary:** Shared corpora/training mean provider diversity is not proof independence.
- **Category:** verification security; research-risk interpretation.
- **Inputs/outputs:** Cross-provider reviews and provenance → limited diversity evidence, not independent-proof status.
- **Invariants:** Provider label alone has zero proof-independence authority.
- **Required failure behavior:** Deny independence credit absent separate mathematical/checker/information evidence.
- **Required integrations:** Diversity profile, reviewer assignment, truth promotion.
- **Observable acceptance:** Cross-provider-only fixture cannot satisfy independent-checker/reconstruction requirements.
- **Dependencies:** S11-002, S15-006.
- **Ambiguity/contradiction notes:** Provider diversity can still be one recorded dimension; it is simply insufficient alone.

### S15-026 — Label all seven innovations as experimental hypotheses

- **Source:** §15 research risks, line 2250.
- **Faithful summary:** Treat the interpretation lattice, cold pass, posterior controller, risk-weighted sentinels, verified-DAG credit, cross-problem reuse reward, and different-provider verification claims as experimental hypotheses, not established advantages.
- **Category:** evaluation governance; communication.
- **Inputs/outputs:** Architecture claims and ablation evidence → hypothesis status or evidence-qualified conclusion.
- **Invariants:** Deployment does not itself establish causal benefit.
- **Required failure behavior:** Block unqualified advantage claims before controlled evidence.
- **Required integrations:** Preregistration, ablation reports, claim-lint/release communication.
- **Observable acceptance:** Documentation/report labels each innovation and cites completed controlled evidence before advantage wording.
- **Dependencies:** S15-019–S15-025, S12-012, S12-027.
- **Ambiguity/contradiction notes:** No performance conclusion is established in the cited section.

## Section 16 — Prioritized recommendations

### S16-001 — P0: enforce one signed feature policy universally

- **Source:** §16 P0, line 2256.
- **Faithful summary:** As a stop-priority action, enforce one signed feature policy at every scheduler, verifier, evidence loader, cache, gate, promotion, and standalone entry point, and keep promotion disabled until required validators exist.
- **Category:** P0 implementation; security.
- **Inputs/outputs:** Signed policy, entry-point operation, validator readiness → deny/allow plus promotion-disabled state.
- **Invariants:** Universal policy coverage and fail-closed promotion.
- **Required failure behavior:** Invalid/missing policy or validator denies action/promotion.
- **Required integrations:** All named entry points, signing, validator registry.
- **Observable acceptance:** Complete entry-point bypass suite and promotion readiness gate pass.
- **Dependencies:** S13-004, S13-005, S13-031.
- **Ambiguity/contradiction notes:** “Cache” here is broader wording than “cache-replay” in M0; implement the superset.

### S16-002 — P0: remove generic evidence acceptance

- **Source:** §16 P0, line 2257.
- **Faithful summary:** Replace generic evidence acceptance with closed, kind-specific schemas and semantic validators for formal proofs, computations, expert review, and imported sources.
- **Category:** P0 security; evidence implementation.
- **Inputs/outputs:** Typed evidence artifact → kind-specific validation result/obligations.
- **Invariants:** Closed schemas; boolean status is insufficient.
- **Required failure behavior:** Reject unknown, open-ended, or generic `passed` evidence.
- **Required integrations:** Evidence router, four adapter/validator classes, promotion gate.
- **Observable acceptance:** Schema mutation and generic-boolean reachability tests fail closed.
- **Dependencies:** S10-010, S10-011, S13-005.
- **Ambiguity/contradiction notes:** Exact expert-review semantic validator remains underspecified.

### S16-003 — P0: require replay and both semantic certificates for formal promotion

- **Source:** §16 P0, line 2258.
- **Faithful summary:** Formal evidence supports promotion only after clean local Lean kernel replay, independent statement-intent approval, and checked formal correspondence.
- **Category:** P0 security; formal release.
- **Inputs/outputs:** Lean artifact, replay, intent review, correspondence review → promotion eligibility.
- **Invariants:** All three exact-bound checks are conjunctive.
- **Required failure behavior:** Missing/failing check blocks formal promotion.
- **Required integrations:** Local Lean, intent/correspondence certificates, promotion gate.
- **Observable acceptance:** Truth-table and target-mutation tests accept only complete bundles.
- **Dependencies:** S13-006, S11-017.
- **Ambiguity/contradiction notes:** “Independent statement-intent approval” should be recorded in the certificate’s reviewer-independence fields; threshold remains unspecified.

### S16-004 — P0: preserve Aristotle metadata and mark mutable hosted output nonreproducible

- **Source:** §16 P0, line 2259.
- **Faithful summary:** Preserve Aristotle request, model, and build metadata instead of reducing it to `passed`; pin the local client/protocol; mark an unattested mutable hosted service as nonreproducible.
- **Category:** P0 vendor integration; provenance; security.
- **Inputs/outputs:** Vendor request/response/client/service identity → complete vendor artifact record and reproducibility verdict.
- **Invariants:** Vendor result is never a bare boolean; client/protocol is pinned; unattested mutable hosting cannot receive replay credit.
- **Required failure behavior:** Keep output nonreproducible/unadmitted until locally replayed and validated.
- **Required integrations:** Aristotle/vendor adapter, artifact store, local Lean replay, model identity.
- **Observable acceptance:** Metadata readback is complete; mutable/unattested fixture is labeled nonreproducible and vendor-only COMPLETE is rejected.
- **Dependencies:** S13-043, S13-007.
- **Ambiguity/contradiction notes:** Hosted service may not expose immutable build identity; the required result is explicit nonreproducibility, not fabricated identity.

### S16-005 — P0: bind caches to actual execution and derive independence from artifacts

- **Source:** §16 P0, line 2260.
- **Faithful summary:** Bind every stage cache to actual runner/provider/model/surface/context and calculate independence only from recorded artifact provenance; a caller-supplied UI label is not attestation.
- **Category:** P0 cache/identity security.
- **Inputs/outputs:** Actual stage execution provenance → cache compatibility identity and evidence-diversity record.
- **Invariants:** Observed provenance overrides labels; cache and independence share identity facts but remain separate judgments.
- **Required failure behavior:** Identity gaps deny cache replay/independence credit.
- **Required integrations:** Runner/model registry, cache manager, evidence profile.
- **Observable acceptance:** Spoof and identity-change tests meet S13-032/S13-034/S13-044.
- **Dependencies:** S13-007, S13-032, S13-034, S13-044.
- **Ambiguity/contradiction notes:** Provider/model/surface/context is a minimum; M0 also lists entitlement, prompt, adjudicator, response hash and should be treated as additional required fields.

### S16-006 — P0: fingerprint the full behavior and import closure

- **Source:** §16 P0, line 2261.
- **Faithful summary:** Fingerprint the full import, executable, and service closure plus adjudicator, feature policy, validator, formal environment, and literature policy.
- **Category:** P0 implementation; contract/cache security.
- **Inputs/outputs:** Complete transitive behavior dependencies → deterministic closure fingerprint.
- **Invariants:** Compatibility includes transitive behavior, not just top-level version labels.
- **Required failure behavior:** Unfingerprinted or changed dependencies invalidate affected contract/cache.
- **Required integrations:** Dependency/import scanners, service registry, policies, formal/retrieval environments, contract store.
- **Observable acceptance:** Mutation in any named closure component changes fingerprint and affected compatibility.
- **Dependencies:** S10-020, S13-033.
- **Ambiguity/contradiction notes:** Canonical closure traversal and external-service fingerprint granularity are unspecified.

### S16-007 — P0: replace manifest overwrites with append-only events

- **Source:** §16 P0, line 2262.
- **Faithful summary:** Replace mutable manifest history with append-only gate, adjudication, evidence, and promotion events and a deterministic materialized view.
- **Category:** P0 implementation; audit.
- **Inputs/outputs:** Decision/evidence lifecycle changes → immutable events and reproducible manifest.
- **Invariants:** Events/artifacts are authoritative; view is derived.
- **Required failure behavior:** Projection faults trigger rebuild/failure, never event overwrite.
- **Required integrations:** Event store, manifest projector, evidence/promotion services.
- **Observable acceptance:** Byte/hash-stable rebuild and full historical query.
- **Dependencies:** S13-008, S13-035.
- **Ambiguity/contradiction notes:** No new contradiction; this explicitly includes evidence events omitted from the shorter acceptance bullet.

### S16-008 — P0: codify exact formal-evidence precedence

- **Source:** §16 P0, line 2263.
- **Faithful summary:** Kernel acceptance establishes only the exact encoded theorem under audited axioms; model review cannot overrule that truth, but intent, applicability, novelty, or significance review may block release; incompatible hard evidence yields `CONFLICTED`.
- **Category:** P0 security; truth/release policy.
- **Inputs/outputs:** Kernel/audit result, model findings, hard counterevidence → exact truth, independent dimension blocks, or conflict.
- **Invariants:** Exact truth scope and release dimensions are separate; hard conflict is preserved.
- **Required failure behavior:** Block appropriate release dimensions; quarantine/audit hard conflicts.
- **Required integrations:** Kernel/axiom audit, referee taxonomy, conflict handler, release gate.
- **Observable acceptance:** Complete precedence matrix matches S13-010/S13-045.
- **Dependencies:** S13-010, S13-045, S10-012.
- **Ambiguity/contradiction notes:** “Kernel acceptance” is qualified by audited axioms; unsafe TCB findings mean the premise of this precedence rule is not met.

### S16-009 — P0: quarantine named legacy manifests and claim files

- **Source:** §16 P0, line 2264.
- **Faithful summary:** Quarantine identity-incomplete legacy manifests and stale claim files, including 601, 661, 724, 782, and 849, rather than treating them as migrated evidence.
- **Category:** P0 migration security.
- **Inputs/outputs:** Legacy artifacts and identity evidence → quarantine or explicit audited migration.
- **Invariants:** Named records are covered; status is not silently inherited.
- **Required failure behavior:** Unproven bindings remain quarantined and cannot promote.
- **Required integrations:** Legacy importer, quarantine/migration validator, promotion gate.
- **Observable acceptance:** Named-regression fixtures meet S13-036.
- **Dependencies:** S13-009, S13-036.
- **Ambiguity/contradiction notes:** No migration algorithm is prescribed.

### S16-010 — P0: add leases/heartbeats and bounded provider backoff

- **Source:** §16 P0, line 2265.
- **Faithful summary:** Add leases and heartbeats plus provider-aware backoff while keeping the 120-second cap; rate limits pause work and never spend a mathematical retry.
- **Category:** P0 operations; failure recovery.
- **Inputs/outputs:** Worker/provider state and rate-limit events → leased pause/backoff/resume.
- **Invariants:** One owner; bounded backoff; mathematical retry count unchanged.
- **Required failure behavior:** Operational throttling is censored, not a claim failure.
- **Required integrations:** Scheduler, lease store, provider quota manager, retry accounting.
- **Observable acceptance:** Rate-limit/crash tests meet S13-039/S13-040 and backoff cap.
- **Dependencies:** S10-021, S13-039, S13-040, S14-010.
- **Ambiguity/contradiction notes:** Same `Retry-After` versus cap tension noted in S14-010 applies.

### S16-011 — P0: record telemetry sufficient for equal-cost baselines

- **Source:** §16 P0, line 2266.
- **Faithful summary:** Record complete cost, call, rate-limit, cache, deterministic-compute, intervention, and terminal-outcome telemetry so equal-cost baselines are possible.
- **Category:** P0 observability; evaluation integration.
- **Inputs/outputs:** Every run/attempt/resource/intervention → authenticated complete telemetry.
- **Invariants:** Failures/censoring/interventions and cache effects are included.
- **Required failure behavior:** Missing telemetry prevents equal-cost superiority claims.
- **Required integrations:** All runners/services, event log, cost/evaluation engine.
- **Observable acceptance:** Reconciliation supports matched baseline denominators and exact cost accounting.
- **Dependencies:** S13-011, S12-007, S12-008, S13-048.
- **Ambiguity/contradiction notes:** Financial and nonfinancial cost aggregation remains unspecified.

### S16-012 — P1: implement the append-only claim/evidence graph and revocation

- **Source:** §16 P1, line 2270.
- **Faithful summary:** Build the append-only claim/evidence graph with transactional revocation.
- **Category:** P1 implementation; truth plane.
- **Inputs/outputs:** Claim/evidence/edge events → durable graph and atomic invalidation/refutation effects.
- **Invariants:** History appends; semantic edges are evidenced; revocation is closure-consistent.
- **Required failure behavior:** Roll back partial revocation and block stale dependents.
- **Required integrations:** Event/artifact stores, SCC graph, promotion/release.
- **Observable acceptance:** Graph, cycle, conflict, and revocation suites pass.
- **Dependencies:** S10-003–S10-018, S13-013.
- **Ambiguity/contradiction notes:** P1 priority label does not override M1/M2 storage sequencing; SQLite may satisfy the first slice before PostgreSQL scale.

### S16-013 — P1: add Statement IR, interpretations, and semantic probes

- **Source:** §16 P1, line 2271.
- **Faithful summary:** Implement Statement IR, explicit interpretations, and mutation/boundary probes.
- **Category:** P1 implementation; semantic truth plane.
- **Inputs/outputs:** Raw source → structured interpretations and adversarial probe results.
- **Invariants:** Ambiguity and boundary behavior remain explicit.
- **Required failure behavior:** Unresolved semantic defects block intended-target release.
- **Required integrations:** Source ingest, parsers, interpretation graph, probe engine.
- **Observable acceptance:** Ambiguous/false/mutated fixtures are detected and correctly gated.
- **Dependencies:** S10-001, S10-002, S13-014, S13-037.
- **Ambiguity/contradiction notes:** Does not specify parser count here; M1 requires dual parser.

### S16-014 — P1: add sandboxed exact computation and independent replay

- **Source:** §16 P1, line 2272.
- **Faithful summary:** Build an exact-computation service in a sandbox and independently replay its results.
- **Category:** P1 implementation; compute truth plane.
- **Inputs/outputs:** Typed immutable jobs → exact artifacts and replay evidence.
- **Invariants:** Sandbox/exactness/replay provenance.
- **Required failure behavior:** Mismatch or sandbox violation quarantines and removes evidence.
- **Required integrations:** Compute lab, containers, artifact/evidence graph, replay.
- **Observable acceptance:** Every exact artifact passes independent replay; mismatch tests revoke support.
- **Dependencies:** S13-016, S13-041, S14-018.
- **Ambiguity/contradiction notes:** Exact backend scope grows from Python in M1 to multiple solvers in M2.

### S16-015 — P1: add pinned Lean targets, capsules, and sentinels

- **Source:** §16 P1, line 2273.
- **Faithful summary:** Build a pinned Lean project with target review, goal capsules, and central sentinels.
- **Category:** P1 implementation; formal truth plane.
- **Inputs/outputs:** Intended claim/goal → reviewed formal target, immutable capsule, sentinel results, proof artifacts.
- **Invariants:** Environment and type are pinned; central-risk probes precede broad trust.
- **Required failure behavior:** Target/sentinel/build failure blocks intended formal release.
- **Required integrations:** Lean farm, intent/correspondence review, risk graph.
- **Observable acceptance:** Target mutation and placeholder/axiom fixtures fail; clean replay passes.
- **Dependencies:** S13-017, S13-042, S15-022.
- **Ambiguity/contradiction notes:** Sentinel selection threshold remains experimental.

### S16-016 — P1: build frozen theorem-level retrieval before deep proof search

- **Source:** §16 P1, line 2274.
- **Faithful summary:** Before deep proof search, build frozen theorem-level literature packets, formal-declaration retrieval, and import/applicability auditing.
- **Category:** P1 implementation; sequencing; retrieval security.
- **Inputs/outputs:** Source/formal corpora and target → frozen cited premises/declarations plus applicability decisions.
- **Invariants:** Retrieved theorem text/hypotheses/version are exact and audited before use.
- **Required failure behavior:** Unavailable/mismatched premises remain unresolved and block dependent proof claims.
- **Required integrations:** Literature packet, theorem index, formal declarations, source auditor, search controller.
- **Observable acceptance:** Deep-search job depends on completed frozen packet/audit and citation defect tests fail.
- **Dependencies:** S13-015, S11-007, S14-013.
- **Ambiguity/contradiction notes:** “Deep proof search” boundary is unspecified.

### S16-017 — P1: add typed provenance-complete OEIS and independently verify imports

- **Source:** §16 P1, line 2275.
- **Faithful summary:** Implement typed OEIS transforms, queries, and cache with complete provenance; independently verify every imported claim.
- **Category:** P1 implementation; retrieval/evidence security.
- **Inputs/outputs:** OEIS query/transformation → cached heuristic match/provenance and, separately, proof evidence if verified.
- **Invariants:** Universal independent verification for imported claims; matches alone remain heuristic.
- **Required failure behavior:** Unverified match has no claim-promotion authority.
- **Required integrations:** OEIS service, typed transform engine, cache, proof/compute validators.
- **Observable acceptance:** Transform/cache provenance is replayable and S13-046 passes.
- **Dependencies:** S13-015, S13-025, S13-046.
- **Ambiguity/contradiction notes:** Scope of “every imported claim” includes any mathematical assertion derived from a match; metadata-only facts may need classification.

### S16-018 — P1: split release into five certificates

- **Source:** §16 P1, line 2276.
- **Faithful summary:** Separate release certification into intent, truth, novelty, significance, and reproducibility.
- **Category:** P1 implementation; release safety.
- **Inputs/outputs:** Dimension-specific evidence → five separately verdict-bearing certificate components.
- **Invariants:** No cross-dimension implication or scalar collapse.
- **Required failure behavior:** Any missing required component stays unresolved and blocks labels that require it.
- **Required integrations:** Intent/formal truth, search/expert novelty, significance review, replay.
- **Observable acceptance:** Release bundle/rendering exposes all five independently.
- **Dependencies:** S11-015, S11-022, S13-019.
- **Ambiguity/contradiction notes:** Formal correspondence and autonomy are additional explicit fields elsewhere; “five certificates” should not erase them.

### S16-019 — P2: convert the DAG to a typed dynamic AND/OR blueprint

- **Source:** §16 P2, line 2280.
- **Faithful summary:** Replace the current fixed DAG representation with a typed AND/OR blueprint whose leaves can change dynamically.
- **Category:** P2 implementation; search architecture.
- **Inputs/outputs:** Existing proof DAG and evolving claims/subgoals → typed AND/OR dependency/search graph.
- **Invariants:** AND/OR semantics and node/edge types are explicit; dynamic leaves preserve provenance/versioning.
- **Required failure behavior:** Invalid rewrites cannot silently alter the frozen scoring target or admitted dependencies.
- **Required integrations:** Claim graph, proof planner, branch controller, evaluation blueprint.
- **Observable acceptance:** Graph supports AND requirements, OR alternatives, leaf expansion/replacement, and immutable history.
- **Dependencies:** S10-009, S12-019, S13-018.
- **Ambiguity/contradiction notes:** Rewrite rules and distinction between operational blueprint and frozen evaluation blueprint must be specified.

### S16-020 — P2: add fingerprints, dedup, failure certificates, and pause/reopen

- **Source:** §16 P2, line 2281.
- **Faithful summary:** Implement mechanism fingerprints, semantic duplicate detection, failure certificates, and branch pause/reopen rules.
- **Category:** P2 implementation; search control.
- **Inputs/outputs:** Program/branch proposals and outcomes → deduplicated archive, durable failures, lifecycle changes.
- **Invariants:** Nominally different but semantically/mechanistically duplicate work does not inflate diversity; pauses retain reopen conditions.
- **Required failure behavior:** Repetition/low value produces failure/pause records, not silent deletion or false mathematical kill.
- **Required integrations:** Branch entities, archive, semantic checker, event log.
- **Observable acceptance:** Duplicate/repeated-error/new-evidence fixtures exercise merge, certificate, pause, and reopen.
- **Dependencies:** S10-005, S12-021, S14-022.
- **Ambiguity/contradiction notes:** Fingerprint/semantic similarity thresholds and pause policy are unspecified.

### S16-021 — P2: parallelize tool-differentiated workers and retire standing tabs

- **Source:** §16 P2, line 2282.
- **Faithful summary:** Dispatch workers differentiated by method/tool in parallel and remove idle permanent chat-tab roles.
- **Category:** P2 runtime implementation; efficiency.
- **Inputs/outputs:** Independent queued bottlenecks → compatible on-demand worker/service assignments.
- **Invariants:** Diversity is operational/method-based; idle role count is not progress.
- **Required failure behavior:** Do not spawn workers without compatible independent work; preserve verifier capacity.
- **Required integrations:** Scheduler, tool services, program archive, worker capability registry.
- **Observable acceptance:** Runtime traces satisfy service topology and only parallelize compatible work.
- **Dependencies:** S13-029, S13-030, S14-005, S14-007.
- **Ambiguity/contradiction notes:** Exact worker pool size is intentionally workload-dependent.

### S16-022 — P2: implement posterior allocation with protected exploration and wide priors

- **Source:** §16 P2, line 2283.
- **Faithful summary:** Allocate branch budget posteriorly while reserving protected exploration, starting with wide priors.
- **Category:** P2 implementation; controller; calibration.
- **Inputs/outputs:** Branch features/outcomes/costs and priors → posterior allocation/exploration decisions.
- **Invariants:** Initial uncertainty is broad; exploration cannot collapse prematurely.
- **Required failure behavior:** Sparse/nonstationary evidence triggers conservative uncertainty/fallback rather than overconfident pruning.
- **Required integrations:** Branch controller, calibration ledger, budget manager, protected queue.
- **Observable acceptance:** Initialization and allocation tests show wide priors and nonzero protected exploration.
- **Dependencies:** S13-026, S15-008, S15-021.
- **Ambiguity/contradiction notes:** Prior family/width, update model, and exploration percentage are unspecified/experimental.

### S16-023 — P2: localize the regulator to failed dependency cones

- **Source:** §16 P2, line 2284.
- **Faithful summary:** Apply the existing regulator only to dependency cones associated with failures rather than globally.
- **Category:** P2 implementation; recovery/search control.
- **Inputs/outputs:** Failure certificate/root and dependency graph → scoped regulator action.
- **Invariants:** Unrelated branches are not penalized by local failure; affected cone is traceable.
- **Required failure behavior:** Stop/restrict repeated work inside failed cone while leaving independent search available.
- **Required integrations:** Regulator, claim/dependency graph, failure certificates, branch controller.
- **Observable acceptance:** Two-independent-cone fixture shows regulation only on the failed closure.
- **Dependencies:** S10-009, S13-002, S16-020.
- **Ambiguity/contradiction notes:** Existing regulator semantics and cone direction/boundary are not defined in this excerpt.

### S16-024 — P3: run the seven-level evaluation with equal-cost raw baselines

- **Source:** §16 P3, line 2288.
- **Faithful summary:** Execute the full seven-level evaluation and include raw-model baselines at equal cost.
- **Category:** P3 evaluation; scaling gate.
- **Inputs/outputs:** Seven-level frozen suite and matched baseline/system contracts → comparative results.
- **Invariants:** All levels and equal-cost raw baselines are represented; Level 7 retains nonaccuracy rules.
- **Required failure behavior:** Missing/unmatched baselines prohibit superiority/orchestration-gain claims.
- **Required integrations:** Evaluation harness, model gateway, telemetry, release graders.
- **Observable acceptance:** Report satisfies S12-001, S12-006, S12-007, and Level 7 constraints.
- **Dependencies:** S12-001–S12-015, S16-011.
- **Ambiguity/contradiction notes:** “Equal-cost” must reconcile tool/expert/deterministic resources; method is unspecified.

### S16-025 — P3: collect authenticated outcomes, costs, censoring, and expert reviews

- **Source:** §16 P3, line 2289.
- **Faithful summary:** Gather authenticated mathematical outcomes, resource costs, censored events, and expert reviews.
- **Category:** P3 telemetry; data security.
- **Inputs/outputs:** Runs and reviewers → signed/provenance-complete calibration/learning dataset.
- **Invariants:** No unauthenticated labels; censoring and review identity/scope are explicit.
- **Required failure behavior:** Exclude/quarantine incomplete or unauthenticated observations.
- **Required integrations:** Event/signing, cost telemetry, calibration ledger, expert portal.
- **Observable acceptance:** Dataset audit traces each record to exact contract, outcome evidence, cost, censoring, and reviewer provenance as applicable.
- **Dependencies:** S10-017, S10-023, S13-028, S16-011.
- **Ambiguity/contradiction notes:** Authentication mechanism and minimal expert-review payload are unspecified.

### S16-026 — P3: delay calibration until comparable data is sufficient

- **Source:** §16 P3, line 2290.
- **Faithful summary:** Calibrate problem and branch models only after enough comparable authenticated data exists.
- **Category:** P3 learning/evaluation governance.
- **Inputs/outputs:** Comparable outcome dataset and sufficiency test → calibrated model or deferred calibration.
- **Invariants:** Heterogeneous/inadequate samples do not justify a fitted confidence model.
- **Required failure behavior:** Defer and retain wide priors/uncertainty when data is insufficient.
- **Required integrations:** Dataset registry, comparability contract, statistical calibration, controller.
- **Observable acceptance:** Calibration job enforces preregistered minimum/comparability checks and records deferral.
- **Dependencies:** S16-025, S12-023, S16-022.
- **Ambiguity/contradiction notes:** “Enough” and “comparable” require quantitative preregistration.

### S16-027 — P3: perform verified-only expert iteration

- **Source:** §16 P3, line 2291.
- **Faithful summary:** Use expert iteration for tactics, proof plans, retrieval, and routing only from verified outcomes.
- **Category:** P3 learning; memory/security.
- **Inputs/outputs:** Verified artifacts/outcomes and expert annotations → updated tactic/plan/retrieval/routing priors or components.
- **Invariants:** Unverified/self-labeled successes never enter the positive learning target.
- **Required failure behavior:** Quarantine/exclude labels whose verification later fails and propagate revocation to derived datasets/models as policy requires.
- **Required integrations:** Verification graph, training-data lineage, four learner domains, revocation.
- **Observable acceptance:** Every learning example traces to qualifying evidence and invalidation removes affected examples.
- **Dependencies:** S10-023, S13-028, S16-025.
- **Ambiguity/contradiction notes:** Minimum qualifying truth tier and treatment of negative/failure examples are unspecified.

### S16-028 — P3: restrict evolutionary search to hard-evaluator branches

- **Source:** §16 P3, line 2292.
- **Faithful summary:** Introduce executable evolutionary search only on branches with hard evaluators.
- **Category:** P3 implementation; evaluation security.
- **Inputs/outputs:** Branch/evaluator qualification → enabled evolutionary population or denial.
- **Invariants:** Model-only or soft subjective fitness is insufficient to enable evolution.
- **Required failure behavior:** Disable/stop evolution and admit no winner if evaluator qualification fails or is hacked.
- **Required integrations:** Branch controller, hard certificate/executable checker, evolution engine, reward-hack recovery.
- **Observable acceptance:** Soft-evaluator fixture is rejected; compromised hard evaluator invalidates/replays per S14-019.
- **Dependencies:** S14-019, S15-005.
- **Ambiguity/contradiction notes:** “Hard evaluator” qualification and acceptable false-negative rate are unspecified.

### S16-029 — P3: build local formal libraries and measure actual reuse

- **Source:** §16 P3, line 2293.
- **Faithful summary:** Build cross-problem local formal libraries and measure their real downstream reuse.
- **Category:** P3 implementation; formal memory; evaluation.
- **Inputs/outputs:** Verified reusable declarations and later problem uses → local library plus reuse evidence.
- **Invariants:** Only trust-audited formal content persists across problems; value is use-based, not upload/node count.
- **Required failure behavior:** Invalidated dependencies revoke/quarantine affected library elements and uses.
- **Required integrations:** Lean library, verified memory, dependency graph, reuse metrics.
- **Observable acceptance:** Reuse dashboard links later verified goals to exact library declarations and reports unused assets separately.
- **Dependencies:** S10-023, S15-023, S15-024, S14-017.
- **Ambiguity/contradiction notes:** What counts as “actual downstream reuse” and library admission tier are unspecified.

### S16-030 — P3: scale workers only when throughput and ablations justify it

- **Source:** §16 P3, line 2294.
- **Faithful summary:** Increase worker count only after verification throughput and controlled ablation evidence justify the scale.
- **Category:** P3 scaling gate; efficiency.
- **Inputs/outputs:** Queue/verification throughput, congestion, ablation/cost results → authorized or denied worker-scale change.
- **Invariants:** More workers is not presumed beneficial; truth verification remains capacity-protected.
- **Required failure behavior:** Do not scale into backlog/cost regression; throttle or retain smaller pool.
- **Required integrations:** Scheduler, verifier metrics, ablation/economics report, capacity governance.
- **Observable acceptance:** Every scale event cites passing throughput and ablation criteria; saturation test preserves verifier service.
- **Dependencies:** S12-026, S14-007, S14-021, S16-024.
- **Ambiguity/contradiction notes:** Quantitative thresholds and approval authority are unspecified.

### S16-031 — Adopt the hierarchical epistemic-blackboard architecture

- **Source:** §16 “Final architectural judgment,” lines 2296–2298.
- **Faithful summary:** The selected target architecture is a hierarchical blackboard whose shared state is an epistemic graph, whose inner loops use search algorithms matched to abstraction level, and whose trust is formal/executable evidence plus independent semantic review.
- **Category:** architecture; integration; trust model.
- **Inputs/outputs:** Problems, claims, programs, evidence, reviews → graph-coordinated multi-level research and certified outputs.
- **Invariants:** Shared state is epistemic/evidence-bearing; search method matches representation; neither hard evidence nor semantic review alone establishes all release dimensions.
- **Required failure behavior:** Unsupported graph state or missing hard/semantic trust path cannot support release.
- **Required integrations:** Claim/evidence graph, branch/search controllers, formal/compute validators, independent referee.
- **Observable acceptance:** System topology/data flow demonstrably implements all three defining clauses.
- **Dependencies:** S10-001–S10-023, S11-001–S11-023, S16-012–S16-023.
- **Ambiguity/contradiction notes:** This is an architectural judgment, not a performance result or precise component API.

### S16-032 — Prioritize closing the formal trust hole, first-class claims/computations, then dynamic allocation

- **Source:** §16 final judgment, line 2300.
- **Faithful summary:** Preserve useful operational foundations, but next close the formal-evidence trust hole, make claims and computations first-class, and only then let a dynamic controller allocate diverse workers against explicit mathematical bottlenecks; do not optimize for more browser tabs or role names.
- **Category:** sequencing; implementation priority.
- **Inputs/outputs:** Existing repository foundations and roadmap → ordered safety/truth/search implementation program.
- **Invariants:** Dynamic scale follows trust/data-plane repair; nominal role count has no architectural value.
- **Required failure behavior:** Do not scale unsafe generic evidence paths or treat additional roles as completion.
- **Required integrations:** M0 formal gates, claim/evidence/compute services, branch controller.
- **Observable acceptance:** Roadmap/release ordering demonstrates M0/P1 before P2/P3 scaling and ties workers to bottlenecks.
- **Dependencies:** S13-001–S13-012, S16-001–S16-023.
- **Ambiguity/contradiction notes:** The statement describes the current repository from the spec author’s snapshot; only the normative sequencing is stable.

### S16-033 — Validate the integration claim by verified cost, safety, calibration, and blind/formal evaluation

- **Source:** §16 final judgment, line 2302.
- **Faithful summary:** Treat EGMRA’s claimed rigor/scientific defensibility as an unproven original integration claim; establish success through verified progress per cost, false-success rate, calibration, and blind expert/formal evaluation—not generated-mathematics volume.
- **Category:** final acceptance; evaluation; communication.
- **Inputs/outputs:** Controlled evaluation, costs, promotions/errors, calibration, expert/formal grades → evidence for or against the integration claim.
- **Invariants:** Architecture implementation is not performance proof; verbosity has no success authority.
- **Required failure behavior:** Retain hypothesis/unproven wording and withhold superiority claims when evidence is absent, unmatched, or unsafe.
- **Required integrations:** Seven-level evaluation, telemetry, false-success analysis, calibration, blinded experts, formal replay, reporting policy.
- **Observable acceptance:** Final report contains all named metrics/evaluations with exact contracts and makes only statistically/evidentially supported claims.
- **Dependencies:** S12-001–S12-035, S13-048–S13-050, S15-026, S16-024–S16-030.
- **Ambiguity/contradiction notes:** No numerical success threshold is supplied; this line explicitly denies that the integration claim is already a result.

