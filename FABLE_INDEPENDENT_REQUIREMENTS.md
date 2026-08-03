# FABLE Independent Requirements Inventory

## Independence statement

This inventory was reconstructed from the complete 2,302-line `docs/AUTONOMOUS_MATH_RESEARCH_ARCHITECTURE_2026.md` before opening `IMPLEMENTATION_LEDGER.md`, `IMPLEMENTATION_PLAN.md`, `DECISIONS.md`, `FINAL_VERIFICATION_REPORT.md`, the claimed EGMRA implementation, or its tests. File names observed while locating the specification were not treated as evidence. Requirement boundaries below were chosen independently of the previous agent's IDs or claimed count.

## Interpretation policy

- The specification is treated as authoritative. Normative language in the executive decisions, module contracts, algorithms, milestones, acceptance criteria, full-scale topology, risk mitigations, and prioritized recommendations is in scope.
- Repeated requirements are consolidated only when they impose the same externally observable behavior. A later, more precise clause is retained as additional source provenance rather than weakened.
- M0, M1, M2, and full-scale requirements remain separately identified when their implementation technology or acceptance differs.
- Claims explicitly labeled `Original proposal`, `plausible`, `unmeasured`, or an experimental hypothesis are requirements to implement and evaluate only where the specification says to do so; they are not assumed performance facts.
- `VERIFIED` in the later traceability matrix will require faithful semantics, production reachability, integration, meaningful positive and negative runtime tests, and required failure behavior.

## Required-field key

Each record contains: **Source**, **Category**, **Requirement**, **Inputs/outputs**, **Invariants**, **Failure behavior**, **Integrations**, **Acceptance**, **Dependencies**, and **Ambiguity/contradiction notes**. `None stated` means the specification did not prescribe a special item; it does not waive ordinary fail-closed behavior.

## Extraction summary

- Independent consolidated requirements: **216**.
- Normative source-coverage clauses cross-checked: **641** across all top-level sections.
- Independent section passes before consolidation: **125** temporary records for §§1–9 and **214** for §§10–16.
- Section 13.6 acceptance criteria: **18 of 18**, preserved individually as F-REQ-174 through F-REQ-191.
- Material specification ambiguities flagged during extraction: **19**, principally milestone ownership, configurable numerical defaults, M0/P0 overlap, T3 referee count, M1→M2 persistence migration, and network-boundary scope. Each affected requirement records the relevant ambiguity rather than silently choosing weaker semantics.

## Top-level section coverage

| Specification section | Inventory treatment |
|---|---|
| 1. Executive summary | Global evidence semantics, five gates, urgent provenance controls, architecture objectives |
| 2. Literature map | Translation firewall, executable-evolution boundary, symbolic-checker boundary, benchmark provenance |
| 3. Comparison | Hybrid is a design hypothesis requiring ablation, not a measured completion/performance fact |
| 4. Current-pipeline critique | Separation of spec/code, preserved invariants, removal of generic evidence and unsafe promotion |
| 5. Proposed architecture | Four planes, three searches, least privilege, and the complete 17-step production flow |
| 6. Detailed modules | Intake, selection, OEIS, retrieval, authorities, state, search, computation, Lean, verification, memory, service contracts |
| 7. Search/allocation | Acquisition and branch formulas, Lean debt, diversity, deduplication, failure, pause/reopen, budgets, main loop |
| 8. External databases | Status hygiene, OEIS request/response/transforms/ranking, immutable literature packets, formal retrieval, source priority |
| 9. Lean/Aristotle | Immediate trust repair, L0-L5, service/certificate APIs, missing-library flow, coverage, external-prover quarantine |
| 10. State/provenance | Typed graph schemas, admission, conflict, SCC revocation, event log, checkpoint/resume, provenance and memory |
| 11. Adversarial verification | Independence, ten attacks, taint, T0-T5 and orthogonal profiles, pessimistic adjudication, signed release certificate |
| 12. Evaluation | Seven levels, tracks, protocol, causal ablations, metrics, durable-progress rule, statistical policy |
| 13. Minimal implementation | Reuse, M0, M1, M2, runtime layout, all 18 acceptance criteria, evaluation-set composition |
| 14. Full scale | Service topology, versioned routing, parallel/serialized operations, leases, program archive, recovery, human authority |
| 15. Risks | Mandatory mitigations and explicit residual uncertainty; proposed innovations must be experimentally tested |
| 16. Recommendations | P0-P3 ordering and the prohibition on treating the integration claim as a performance result |

## Independent requirements

### F-REQ-001 — Evidence-first design objective

- **Source:** §§1, lines 3-16
- **Category:** Global objective / evidence semantics
- **Requirement:** Optimize for rigorous, intended, novel, reproducible mathematical progress; cost is subordinate. Preserve the four support labels and test every original proposal instead of presenting it as established.
- **Inputs/outputs:** Inputs: candidate results, evidence, cost. Outputs: correctly qualified progress claims and optimization decisions.
- **Invariants:** Evidence strength and epistemic qualification remain explicit; cost cannot justify weakening rigor.
- **Failure behavior:** If rigor, intent, novelty, or replay is unresolved, report that dimension as unresolved and do not claim completion.
- **Integrations:** Controller, release, evaluation, communication.
- **Acceptance:** A result with low cost but missing any required evidentiary dimension is not promoted, and original proposals are evaluated rather than asserted.
- **Dependencies:** None.
- **Ambiguity/contradiction notes:** The objective is global; later sections define gate thresholds and when novelty/significance are required.

### F-REQ-002 — Five independent release gates

- **Source:** §1 lines 28-35; §5.2 lines 462-464; §11.3 lines 1746-1757
- **Category:** Release / truth plane
- **Requirement:** Decide statement fidelity, mathematical truth, novelty, significance, and reproducibility independently; no positive gate substitutes for another.
- **Inputs/outputs:** Inputs: candidate, graph, referee report, gate-specific evidence. Outputs: five separate verdicts/certificates.
- **Invariants:** No scalar confidence or consensus collapses the axes.
- **Failure behavior:** Any mandatory failed or unknown gate blocks the corresponding release label and produces an honest narrower disposition.
- **Integrations:** Claim graph, referee, release auditor, renderer.
- **Acceptance:** Forging or passing four gates while one mandatory gate fails cannot release a solved/novel result.
- **Dependencies:** F-REQ-001.
- **Ambiguity/contradiction notes:** Informal/formal releases use different truth/correspondence thresholds, specified in §11.3.

### F-REQ-003 — Exact meaning of Lean-verified

- **Source:** Preamble line 16; §11.3 lines 1751-1757
- **Category:** Formal verification / communication
- **Requirement:** Use “Lean-verified” only for kernel acceptance of the exact encoded proposition in a specified environment; never imply informal correspondence, novelty, or significance from kernel acceptance.
- **Inputs/outputs:** Inputs: pinned replay certificate and exact type. Outputs: T4 encoded-theorem label plus separate correspondence/novelty/significance fields.
- **Invariants:** Formal truth and semantic correspondence remain separate.
- **Failure behavior:** Missing kernel replay or environment/type identity prevents the label; missing I2/F2 prevents claiming the intended theorem was formally proved.
- **Integrations:** Lean service, correspondence certificates, renderer.
- **Acceptance:** A compiling or vendor-reported proof without local kernel/type evidence cannot be labeled Lean-verified.
- **Dependencies:** F-REQ-002.
- **Ambiguity/contradiction notes:** Publication of untrusted generated Lean additionally requires T5.

### F-REQ-004 — Immutable source and interpretation lattice

- **Source:** §1 lines 36-40; §5.2 lines 448-451
- **Category:** Intake / truth plane
- **Requirement:** Freeze exact source bytes and metadata, build structured interpretations, reconcile only justified equivalents, and retain materially different readings as lattice nodes rather than silently normalizing one statement.
- **Inputs/outputs:** Inputs: source bytes, history, context definitions. Outputs: source record, Statement IR candidates, interpretation lattice.
- **Invariants:** Every interpretation remains linked to immutable source spans/hashes.
- **Failure behavior:** Unresolved material ambiguity blocks intended-target release while allowing labeled per-node exploration.
- **Integrations:** Source store, dual parsers, probes, claim graph, release.
- **Acceptance:** An injected ambiguous statement yields multiple linked interpretations and cannot receive intended-target approval until resolved.
- **Dependencies:** F-REQ-001.
- **Ambiguity/contradiction notes:** Human resolution may be required; exploration is not necessarily blocked.

### F-REQ-005 — Cold pass followed by mandatory retrieval

- **Source:** §1 lines 38-39, 81-82; §5.2 lines 452-454
- **Category:** Search / retrieval protocol
- **Requirement:** Spend 5–10% of the initial budget on literature-blind scratch/falsification, then perform theorem-level literature, OEIS, and formal-library retrieval before expensive proof search.
- **Inputs/outputs:** Inputs: interpretations and initial budget. Outputs: cold hypotheses/query leads and a frozen solver packet.
- **Invariants:** Cold output is never publication evidence; deep work consumes a provenance-bound packet.
- **Failure behavior:** Unavailable or conflicting retrieval leaves status/novelty/import unresolved and blocks deep-release claims rather than silently proceeding as if novel.
- **Integrations:** Controller, falsifier, literature/OEIS/theorem services.
- **Acceptance:** The production flow records a cold budget within 5–10%, then packet construction before deep branch execution.
- **Dependencies:** F-REQ-004.
- **Ambiguity/contradiction notes:** §7 pseudocode uses exactly 5%; §15 requires ablation of 0%, 5%, 10%, so 5% is an initial implementation value, not an established optimum.

### F-REQ-006 — Append-only typed epistemic graph with revocation

- **Source:** §1 lines 40-41; §5.2 lines 458-460
- **Category:** Truth plane / persistence
- **Requirement:** Represent claims, typed evidence, dependencies, contradictions, and lifecycle changes in an append-only graph; refutations and evidence invalidation cascade to dependents.
- **Inputs/outputs:** Inputs: structured proposals and validated artifacts. Outputs: immutable events and derived graph status.
- **Invariants:** Weak evidence may guide search but never silently upgrades or becomes a stronger premise.
- **Failure behavior:** Invalid or refuted support transactionally downgrades affected claims, pauses release, and reopens relevant branches.
- **Integrations:** Evidence router, event store, controller, release.
- **Acceptance:** Corrupting or revoking a central item downgrades its full dependent closure after replay.
- **Dependencies:** F-REQ-004.
- **Ambiguity/contradiction notes:** Detailed SCC semantics are specified in §10.2.

### F-REQ-007 — Three nested search levels

- **Source:** §1 lines 40-42; §5.1 lines 389-400
- **Category:** Search architecture
- **Requirement:** Implement research-program search, claim/lemma AND-OR search, and exact Lean proof-state search as distinct but connected levels.
- **Inputs/outputs:** Inputs: contract, program archive, graph, formal goals. Outputs: mechanism branches, proof blueprints, formal action results.
- **Invariants:** Success at a lower level cannot bypass truth/release gates.
- **Failure behavior:** Unavailable formal search leaves formal debt explicit; it does not convert informal success into formal verification.
- **Integrations:** Controller, blueprint, program workers, Lean service.
- **Acceptance:** Production orchestration reaches and updates all three levels on an eligible task, with typed handoffs between them.
- **Dependencies:** F-REQ-006.
- **Ambiguity/contradiction notes:** M1 may use simple best-first/UCB and one Lean worker; full algorithm portfolios arrive later.

### F-REQ-008 — Posterior utility allocation with protected exploration

- **Source:** §1 lines 41-43; §5.2 lines 455-461
- **Category:** Control / selection
- **Requirement:** Allocate problem and branch compute using uncertainty-aware posterior expected utility, value of information, downstream unlock, reuse, diversity, cost, duplication, and semantic risk, while preserving a protected-exploration lane.
- **Inputs/outputs:** Inputs: features, posteriors, graph, costs, budgets. Outputs: selected problems/actions, budgets, rationale.
- **Invariants:** Allocation scores are not truth scores and do not hard-kill low-score mathematical branches.
- **Failure behavior:** Operational censoring, rate limits, or sparse data widen uncertainty/pause work rather than count as mathematical failure.
- **Integrations:** Selector, controller, telemetry, graph.
- **Acceptance:** Changing authenticated state/cost/uncertainty changes selections, and protected exploration receives its configured share.
- **Dependencies:** F-REQ-001, F-REQ-006.
- **Ambiguity/contradiction notes:** Initial protected fraction is 15–25% by §6/§7; pseudocode uses 20%.

### F-REQ-009 — Early risk-weighted Lean sentinels

- **Source:** §1 lines 42-44; §5.2 line 460
- **Category:** Formalization / search
- **Requirement:** Use Lean during intake/search for the target, definitions, boundary cases, and high-centrality/high-semantic-risk claims rather than only post-hoc formatting.
- **Inputs/outputs:** Inputs: approved interpretation and risk-ranked claims. Outputs: formal target candidates, sentinel declarations, diagnostics.
- **Invariants:** Sentinel success proves only its exact encoding; target correspondence remains separately certified.
- **Failure behavior:** Mismatch or counterexample invalidates the affected prose/formal cone and redirects the blueprint.
- **Integrations:** Intake, graph, Lean service, controller.
- **Acceptance:** A high-risk false assumption is exposed before final assembly and changes branch state.
- **Dependencies:** F-REQ-003, F-REQ-004.
- **Ambiguity/contradiction notes:** Low-risk glue may remain informal with explicit debt.

### F-REQ-010 — Replayable executable mathematics

- **Source:** §1 lines 43-45; §5.1 lines 415-429
- **Category:** Computation / evidence
- **Requirement:** Run Python/Sage/CAS/SAT/SMT/ILP or other exact experiments as immutable, sandboxed jobs with independently replayable artifacts and checked classifications/certificates.
- **Inputs/outputs:** Inputs: immutable experiment specification. Outputs: frozen artifacts, replay and certificate reports.
- **Invariants:** Floating-point or solver testimony cannot prove an exact general statement without validated bounds/reconstruction.
- **Failure behavior:** Timeout, crash, mismatch, missing certificate, or failed replay quarantines evidence and downgrades dependents; no unsandboxed fallback.
- **Integrations:** Compute lab, artifact store, evidence router, referee.
- **Acceptance:** Independent replay reproduces exact output/hash and malicious jobs cannot access prohibited host resources.
- **Dependencies:** F-REQ-006.
- **Ambiguity/contradiction notes:** True isolation may require containers/VMs; unavailable infrastructure must be reported, not simulated.

### F-REQ-011 — Organizationally independent adversarial referee

- **Source:** §1 lines 44-46; §5.1 lines 424-432
- **Category:** Verification / authority
- **Requirement:** Operate a referee separate from generators/governor, with no reward for agreement, to attack claims and report to the release auditor.
- **Inputs/outputs:** Inputs: locked statement, graph, sources, candidate, raw artifacts. Outputs: defect graph, recalculations, verification profile.
- **Invariants:** Referee review is not itself hard truth evidence and cannot repair in the same adjudication pass.
- **Failure behavior:** A valid central defect or unresolved conflict blocks promotion.
- **Integrations:** Claim graph, replay tools, release auditor.
- **Acceptance:** Self-approval, shared hidden scratchpad, or generator-issued referee metadata cannot satisfy independent-review requirements.
- **Dependencies:** F-REQ-002, F-REQ-006.
- **Ambiguity/contradiction notes:** Different model families diversify review but do not prove mathematical independence.

### F-REQ-012 — Verified-only persistent learning

- **Source:** §1 lines 45-46; §5.2 line 464
- **Category:** Learning / persistence
- **Requirement:** Persist cross-problem semantic and learning artifacts only after authenticated replay; quarantine speculative problem-local memory and keep evidence types distinct.
- **Inputs/outputs:** Inputs: replayed outcomes, certificates, failures, costs. Outputs: verified semantic, audited import, procedural, negative, and calibration memories.
- **Invariants:** Model consensus or summaries never upgrade evidence; external imports remain sourced imports.
- **Failure behavior:** Toolchain/source correction triggers revalidation or applicability review; invalid memory is revoked, not blindly reused.
- **Integrations:** Graph, artifact replay, learning, selector/controller.
- **Acceptance:** Unauthenticated or non-replayable results cannot affect later calibrated selection or truth status.
- **Dependencies:** F-REQ-006, F-REQ-010.
- **Ambiguity/contradiction notes:** Procedural hints may be reused only as proposals and must be rechecked.

### F-REQ-013 — Local kernel and correspondence prerequisites

- **Source:** §1 lines 65-75
- **Category:** Stop-ship formal security
- **Requirement:** Before formal evidence affects promotion, require local kernel replay plus approved statement intent and formal-statement correspondence; vendor `COMPLETE` is insufficient.
- **Inputs/outputs:** Inputs: formal source, pinned environment, intent and correspondence certificates. Outputs: admissible formal evidence or explicit rejection.
- **Invariants:** Provider status is candidate-generation metadata, never a trust root.
- **Failure behavior:** Unavailable local replay or unreviewed fidelity rejects formal promotion.
- **Integrations:** Aristotle adapter, Lean verifier, evidence loader, promotion.
- **Acceptance:** A vendor-only complete response is rejected through every production entry point.
- **Dependencies:** F-REQ-003.
- **Ambiguity/contradiction notes:** None; described as immediate and non-overridable later.

### F-REQ-014 — Promotion disabled until closed validators and policy enforcement

- **Source:** §1 lines 74-76
- **Category:** Feature policy / release security
- **Requirement:** Keep every promotion path disabled until each evidence kind has a closed semantic schema/validator and release feature flags are centrally enforced.
- **Inputs/outputs:** Inputs: signed policy and typed evidence. Outputs: allow/deny decision with reason.
- **Invariants:** Scheduler, verifier, scripts, loaders, caches, gates, and promoters use the same policy.
- **Failure behavior:** Unknown evidence kind, disabled feature, invalid signature, or missing validator fails closed.
- **Integrations:** All production entry points and cache replay.
- **Acceptance:** Direct scripts and alternate calls cannot reach disabled verification or promotion behavior.
- **Dependencies:** F-REQ-002, F-REQ-013.
- **Ambiguity/contradiction notes:** The signer/key lifecycle is not fully specified; this must not justify accepting unsigned policy.

### F-REQ-015 — Complete runtime identity and compatible cache replay

- **Source:** §1 lines 76-77
- **Category:** Provenance / cache
- **Requirement:** Bind every stage to actual provider/model/runner, adjudicator and literature policy, formal environment, validator version, prompts, tools, response/artifacts, and reject incompatible cached reuse.
- **Inputs/outputs:** Inputs: full behavior/import/service closure and stage artifact. Outputs: attested/unattested provenance and cache compatibility decision.
- **Invariants:** Caller labels never masquerade as attested identity; cached provenance comes from the cached artifact.
- **Failure behavior:** Any relevant identity/policy/closure change invalidates affected cache entries.
- **Integrations:** Run contracts, cache, scheduler, adjudicator, retrieval, Lean, evidence adapters.
- **Acceptance:** A cached adjudication cannot replay under a different runner/model or create false independence metadata.
- **Dependencies:** F-REQ-014.
- **Ambiguity/contradiction notes:** Immutable provider model versions may be unavailable; record unattested/mutable status explicitly.

### F-REQ-016 — Preserve conservative operational invariants

- **Source:** §1 line 77; §4.4 lines 369-383
- **Category:** Compatibility / safety
- **Requirement:** Retain source snapshots, exact statement locks, compatible content-addressed caches, deterministic protected-exploration queues, atomic claims, append-only records, capped rate-limit waits, deterministic rejection, and proof-vs-plan regulator semantics while extending them.
- **Inputs/outputs:** Inputs: existing operational records and new EGMRA contracts. Outputs: migrated compatible behavior without weakened safeguards.
- **Invariants:** Extensions must close known identity/evidence gaps rather than bypass existing rejection.
- **Failure behavior:** Identity-incomplete/stale artifacts are quarantined or migrated explicitly, never silently upgraded.
- **Integrations:** Legacy pipeline, queue, cache, event log, regulator.
- **Acceptance:** Regression tests show all listed invariants survive the EGMRA production paths.
- **Dependencies:** F-REQ-014, F-REQ-015.
- **Ambiguity/contradiction notes:** Some existing implementations were called valuable but defective; preservation means semantic invariant, not unchanged code.

### F-REQ-017 — Append-only authoritative decisions and derived manifests

- **Source:** §1 lines 78-79
- **Category:** Persistence / audit
- **Requirement:** Replace mutable proof/manifest authority with append-only gate, adjudication, evidence, and promotion events; manifests are deterministic disposable projections.
- **Inputs/outputs:** Inputs: decision events. Outputs: event chain and reproducible manifest view.
- **Invariants:** History cannot be overwritten or reordered without detection.
- **Failure behavior:** Projection mismatch or event-chain failure blocks resume/release.
- **Integrations:** Event store, gate, adjudicator, promoter, manifest builder.
- **Acceptance:** Replaying the same valid event stream deterministically reproduces the manifest and preserves all prior decisions.
- **Dependencies:** F-REQ-006.
- **Ambiguity/contradiction notes:** Cryptographic event integrity details are elaborated in §10.

### F-REQ-018 — Replace fixed proof loop with hierarchical search

- **Source:** §1 lines 78-80
- **Category:** Search integration
- **Requirement:** Replace the fixed scout/synthesis/whole-proof loop with dynamic research-program and AND/OR search, using executable falsification and high-risk Lean sentinels before scaling agent count.
- **Inputs/outputs:** Inputs: contract, packet, graph, budgets. Outputs: dynamic branches, blueprint, validated local claims.
- **Invariants:** Agent/role count has no value absent distinct mechanism/tool/information boundaries.
- **Failure behavior:** Failure localizes to dependency cones and produces pause/reopen/failure data rather than blind whole-proof retries.
- **Integrations:** Programs, controller, graph, computation, Lean.
- **Acceptance:** Production orchestration launches distinct branches and locally revises failed cones; legacy fixed census is not the only reachable path.
- **Dependencies:** F-REQ-007, F-REQ-009, F-REQ-010.
- **Ambiguity/contradiction notes:** M1 requires only two or three method-distinct branches; M2 scales to three to five.

### F-REQ-019 — External provers are candidate workers only

- **Source:** §1 lines 81-84
- **Category:** External integration / trust
- **Requirement:** Treat Aristotle and all proprietary/hosted provers as optional candidate generators, never as trusted checkers or formal-promotion roots.
- **Inputs/outputs:** Inputs: locked bounded target and provider artifacts. Outputs: quarantined candidate source plus provider metadata.
- **Invariants:** Local pinned replay and independent trust checks govern admission.
- **Failure behavior:** Status-only, missing-source, mutable-version, or unreplayable provider output remains non-reproducible testimony.
- **Integrations:** Model gateway, external prover adapter, sandbox, Lean farm.
- **Acceptance:** Removing the provider entirely leaves local verification semantics intact, and forged provider success cannot promote.
- **Dependencies:** F-REQ-013.
- **Ambiguity/contradiction notes:** Provider identity can diversify search but not the Lean trust base.

### F-REQ-020 — Authenticated outcomes and no consensus evidence

- **Source:** §1 lines 83-85
- **Category:** Learning / verification
- **Requirement:** Learn only from authenticated replayable outcomes; model consensus may prioritize search but is never independent truth evidence.
- **Inputs/outputs:** Inputs: outcome labels, replay artifacts, model provenance. Outputs: calibrated learning data and search priorities.
- **Invariants:** Training/evaluator lineages and pipeline fingerprints remain recorded and separated.
- **Failure behavior:** Unauthenticated, correlated, or non-replayable labels are quarantined from learning and promotion.
- **Integrations:** Learning, controller, referee, telemetry.
- **Acceptance:** Replacing a hard checker with unanimous models does not raise truth tier or populate verified semantic memory.
- **Dependencies:** F-REQ-011, F-REQ-012.
- **Ambiguity/contradiction notes:** Human reviews require authenticated identity/scope but may still carry conflicts.

### F-REQ-021 — Equal-cost controlled evaluation

- **Source:** §1 lines 84-85; §3 lines 300-315
- **Category:** Evaluation / scientific claims
- **Requirement:** Evaluate EGMRA against raw frontier/open/current-pipeline baselines at matched cost or on a verified-progress/cost Pareto curve, using blind expert review and versioned formal replay; treat the hybrid as an unmeasured hypothesis until ablated.
- **Inputs/outputs:** Inputs: frozen tasks, baselines, budgets, artifacts. Outputs: paired metrics, intervals, failure-complete logs.
- **Invariants:** Orchestration claims cannot be inferred from unequal models/tools/budgets.
- **Failure behavior:** Without paired evidence, emit no “beats baseline” or measured-winner claim.
- **Integrations:** Evaluation harness, telemetry, reviewers, formal replay.
- **Acceptance:** Any reported performance advantage points to matched, versioned runs with exact denominators and costs.
- **Dependencies:** F-REQ-001.
- **Ambiguity/contradiction notes:** Best-available deployment comparisons are allowed but must be labeled non-causal.

### F-REQ-022 — Translation firewall

- **Source:** §2.3 lines 214-226
- **Category:** Intake / formal semantics
- **Requirement:** Generate multiple candidate translations, independently backtranslate them, test examples/counterexamples/vacuity, global paraphrase invariance and local mutation covariance, attempt formal equivalence where feasible, and approve a target hash independently.
- **Inputs/outputs:** Inputs: raw statement and candidate formal/informal translations. Outputs: test artifacts and approved/rejected target/correspondence certificates.
- **Invariants:** Compilation is neither faithfulness nor equivalence.
- **Failure behavior:** A meaning-changing mutation that leaves the candidate unchanged, or unresolved divergence, blocks correspondence approval.
- **Integrations:** Dual parser, probe engine, Lean compareStatements, intent auditor.
- **Acceptance:** Adversarial paraphrase and local mutation suites distinguish semantics and prevent a wrong but provable target from promotion.
- **Dependencies:** F-REQ-004, F-REQ-003.
- **Ambiguity/contradiction notes:** Formal equivalence may be infeasible; then the result remains reviewed/caveated rather than formally equivalent.

### F-REQ-023 — Safe boundary for evolutionary discovery

- **Source:** §2.4 lines 228-240
- **Category:** Search / executable safety
- **Requirement:** Use evolutionary search only for executable constructions, algorithms, decompositions, counterexample generators, or formal proof programs with exact/certificate-backed fitness, an independent checker, separate novelty/complexity objectives, mechanism diversity, and out-of-environment replay.
- **Inputs/outputs:** Inputs: executable candidates and frozen evaluator. Outputs: replayed winners and full population provenance.
- **Invariants:** Unrestricted prose proof evolution under an LLM judge cannot promote truth.
- **Failure behavior:** Evaluator hacks or failed replay invalidate the run and all winners.
- **Integrations:** Compute lab, formal checker, quality-diversity archive, novelty audit.
- **Acceptance:** A candidate that only moves difficulty into an unproved helper receives no verified-debt credit and cannot win on plausibility.
- **Dependencies:** F-REQ-010, F-REQ-020.
- **Ambiguity/contradiction notes:** General proof-strategy evolution is explicitly speculative.

### F-REQ-024 — Symbolic solver semantic and certificate boundary

- **Source:** §2.5 lines 242-253; §6.12 lines 790-801
- **Category:** ATP/SAT/SMT integration
- **Requirement:** Route supported leaves to mature solvers, preserve source-to-solver semantics, and reconstruct successful proofs in Lean or attach independently checked proof/model/certificate artifacts.
- **Inputs/outputs:** Inputs: source-claim hash, supported-fragment encoding, premises, translator version and translation obligations. Outputs: proof/model/certificate plus reconstruction status.
- **Invariants:** A `proved`, `SAT`, or `unsat` label alone is solver testimony.
- **Failure behavior:** Unsupported translation, missing proof trace, or failed reconstruction prevents promotion.
- **Integrations:** Claim graph, solver adapters, Lean/certificate checker.
- **Acceptance:** A correct certificate for a deliberately mistranslated formula cannot support the source claim.
- **Dependencies:** F-REQ-010, F-REQ-003.
- **Ambiguity/contradiction notes:** Where a solver cannot emit checkable traces, its output remains heuristic/testimony.

### F-REQ-025 — Versioned benchmark provenance

- **Source:** §2.2 line 212; §2.6 lines 255-270
- **Category:** Evaluation provenance
- **Requirement:** Every benchmark comparison records exact statement/corpus commit, pass@k, token/tool budget, toolchain/Mathlib version, and semantic audit status; parsing, retrieval, novelty, proof, and formalization are scored separately.
- **Inputs/outputs:** Inputs: benchmark snapshot and run contract. Outputs: versioned track-specific results.
- **Invariants:** Training resources and currently unsolved deployments are not treated as held-out labeled benchmarks.
- **Failure behavior:** Unmatched pass@k/budgets or drifting/corrected benchmarks cannot support aggregate comparative claims.
- **Integrations:** Evaluation harness, corpus store, run contracts.
- **Acceptance:** Changing benchmark/toolchain versions creates a distinct result lineage and triggers replay.
- **Dependencies:** F-REQ-021.
- **Ambiguity/contradiction notes:** No single accuracy number covers the entire architecture.

### F-REQ-026 — Specification and implementation must remain distinct

- **Source:** §4.1 lines 319-330
- **Category:** Audit / communication
- **Requirement:** Do not report target architecture, interfaces, test counts, or candidate manifests as implemented mathematical capability without production code, reachability, artifacts, and verified results.
- **Inputs/outputs:** Inputs: specification, code paths, tests, runtime artifacts. Outputs: evidence-qualified capability report.
- **Invariants:** Tests establish software behavior only for what they actually exercise; they do not prove theorem performance.
- **Failure behavior:** Missing runtime evidence is classified unverified/unreachable/test-only rather than complete.
- **Integrations:** Audit reports, observability, release communication.
- **Acceptance:** A disconnected class or mock-only test cannot satisfy a complete-system requirement.
- **Dependencies:** F-REQ-001.
- **Ambiguity/contradiction notes:** This is an audit/reporting invariant as well as a design constraint.

### F-REQ-027 — Conditional durable authorities, not standing role theater

- **Source:** §4.3 lines 355-367; §6.5 lines 627-639
- **Category:** Agent authority / orchestration
- **Requirement:** Implement seven durable least-privilege authorities and conditionally dispatch specialist method profiles only when their distinct tools, priors, objectives, or information boundaries are needed.
- **Inputs/outputs:** Inputs: bottlenecks, branch state, authority policy. Outputs: scoped dispatches and structured authority-specific results.
- **Invariants:** Prompt role names are not an access-control boundary; each authority is technically prohibited from forbidden state changes.
- **Failure behavior:** Unauthorized actions, self-approval, or confused-deputy requests are rejected and logged.
- **Integrations:** Governor, intake/retrieval, programs, computation, formalization, referee, release auditor.
- **Acceptance:** Direct tool invocation cannot exceed an authority's allowed actions; same-context same-model chats do not count as independent.
- **Dependencies:** F-REQ-011, F-REQ-018.
- **Ambiguity/contradiction notes:** “Seven durable authorities” are services/authorities; runtime M1 normally uses four concurrent roles.

### F-REQ-028 — Additive utility rather than multiplicative priority

- **Source:** §4.3 line 362; §7.3 lines 852-879
- **Category:** Control / selection mathematics
- **Requirement:** Use additive posterior expected utility and information value with explicit safety constraints; do not multiply subjective factors so a near-zero estimate can veto a branch.
- **Inputs/outputs:** Inputs: outcome probabilities, values, information, unlock, reuse, diversity, falsification, cost, duplication, semantic risk. Outputs: U(b,a) and selected actions.
- **Invariants:** Hard safety constraints are evaluated separately from numeric utility.
- **Failure behavior:** Invalid/missing estimates widen uncertainty or block only through explicit constraints, not implicit zero multiplication.
- **Integrations:** Controller, calibration store, budget manager.
- **Acceptance:** Independent recomputation of representative U values matches the specified additive formula and branch order.
- **Dependencies:** F-REQ-008.
- **Ambiguity/contradiction notes:** Weights require project policy and calibration; wide priors are mandatory initially.

### F-REQ-029 — Ambiguity blocks publication but not all exploration

- **Source:** §4.3 line 363; §6.1 line 517
- **Category:** Intake / release
- **Requirement:** Permit cheap, separately labeled exploration of unresolved interpretation nodes while blocking release as the intended problem.
- **Inputs/outputs:** Inputs: lattice node and unresolved ambiguity. Outputs: branch-scoped work plus blocked intent gate.
- **Invariants:** Every result remains bound to its interpretation ID.
- **Failure behavior:** No fallback to raw text or a default interpretation may erase the ambiguity.
- **Integrations:** Intake, controller, graph, release.
- **Acceptance:** Alternate interpretations can produce separate evidence, but a forged active/default node cannot bypass I2.
- **Dependencies:** F-REQ-004.
- **Ambiguity/contradiction notes:** A human may resolve ambiguity later and trigger revalidation.

### F-REQ-030 — Controlled two-pass retrieval with targeted re-entry

- **Source:** §4.3 line 364; §8.4 lines 1167-1197
- **Category:** Retrieval / provenance
- **Requirement:** Use a blind scratch pass, an immutable frozen solver packet, and provenance-linked targeted re-entry only for an exact missing theorem/query.
- **Inputs/outputs:** Inputs: cold hypotheses, full query bundle, missing gap. Outputs: packet versions with query logs and lineage.
- **Invariants:** Existing packets are immutable; targeted re-entry never rewrites history.
- **Failure behavior:** Stale, malformed, inaccessible, or conflicting sources remain explicit gaps and cannot silently become verified facts.
- **Integrations:** Literature service, source store, controller, novelty auditor.
- **Acceptance:** Packet content changes produce a new hash/version and invalidate all affected downstream contracts.
- **Dependencies:** F-REQ-005, F-REQ-015.
- **Ambiguity/contradiction notes:** The system is neither permanently offline nor unconstrained live browsing.

### F-REQ-031 — Risk-selective formalization

- **Source:** §4.3 line 365; §9.5 lines 1376-1403
- **Category:** Formalization allocation
- **Requirement:** Formalize the target, definitions, boundary cases, and claims with high centrality, semantic risk, dispute probability, downstream loss, or reuse; leave low-risk glue as explicit formalization debt when necessary.
- **Inputs/outputs:** Inputs: graph risk/cost features. Outputs: formalization priority F(c), sentinel queue, explicit debt.
- **Invariants:** F(c) is a queue priority, never a truth score.
- **Failure behavior:** Prohibitive formalization cost downgrades the evidence label and exposes debt; it never permits a “formally verified” claim.
- **Integrations:** Graph, controller, Lean service, renderer.
- **Acceptance:** Independent recomputation of F(c) selects high-risk affordable claims and the output profile accurately labels unformalized steps.
- **Dependencies:** F-REQ-009.
- **Ambiguity/contradiction notes:** A T3+I2 rigorous informal publication may be possible without full formalization, but not a formal-verification label.

### F-REQ-032 — Model review cannot manufacture truth tiers

- **Source:** §4.3 line 366; §6.6 lines 714-718
- **Category:** Truth admission
- **Requirement:** A stateless/model verifier may route or criticize work but cannot admit high-centrality facts or upgrade evidence; downstream uses retain the source tier.
- **Inputs/outputs:** Inputs: model review and claim proposal. Outputs: search hint/defect proposal, not automatic truth promotion.
- **Invariants:** No model summary upgrades evidence.
- **Failure behavior:** Unsupported model approval leaves truth UNKNOWN and dependent release blocked.
- **Integrations:** Evidence router, claim graph, referee, controller.
- **Acceptance:** Replacing validators with constant positive model outputs yields no SUPPORTED/high truth status.
- **Dependencies:** F-REQ-006, F-REQ-020.
- **Ambiguity/contradiction notes:** T3 rigorous informal review requires two genuinely independent hostile reconstructions, not ordinary consensus.

### F-REQ-033 — Orthogonal truth, intent, novelty, and significance state

- **Source:** §4.3 line 367; §11.3 lines 1746-1757
- **Category:** Epistemic state
- **Requirement:** Store and report truth, intended correspondence, novelty, significance, reproducibility, and autonomy as orthogonal states/profiles.
- **Inputs/outputs:** Inputs: dimension-specific evidence. Outputs: separate status fields and certificates.
- **Invariants:** No consensus score, Lean build, or single V-level collapses dimensions.
- **Failure behavior:** Unknown/conflicting dimensions remain unknown/conflicted and block only labels that require them.
- **Integrations:** Graph schema, release certificate, renderer.
- **Acceptance:** A T5 encoded theorem with N0 or I0 is reported exactly that way and is not called a novel intended solution.
- **Dependencies:** F-REQ-002, F-REQ-003.
- **Ambiguity/contradiction notes:** Formal correspondence is N/A only for informal-only results.

### F-REQ-034 — Four-plane separation

- **Source:** §5.1 lines 387-394
- **Category:** Architecture / authority
- **Requirement:** Separate truth, search, control, and communication planes with the responsibilities enumerated by the specification.
- **Inputs/outputs:** Inputs: shared durable events/artifacts. Outputs: plane-specific decisions and views.
- **Invariants:** Search/control/communication cannot directly mutate epistemic truth or bypass release.
- **Failure behavior:** Cross-plane unauthorized writes are rejected and audited.
- **Integrations:** All core services.
- **Acceptance:** Direct calls from governor, worker, or renderer cannot promote a claim or release a result without truth-plane events and gates.
- **Dependencies:** F-REQ-006, F-REQ-027.
- **Ambiguity/contradiction notes:** The diagram calls one subgraph “Search and tool plane”; it corresponds to the specified search responsibilities, not a fifth release authority.

### F-REQ-035 — Least-privilege blackboard writes

- **Source:** §5.1 lines 402-444
- **Category:** Security / data flow
- **Requirement:** Give agents only relevant claim-graph slices and frozen source packets; accept structured proposals while reserving epistemic-status changes to the truth plane.
- **Inputs/outputs:** Inputs: authority identity, branch capsule. Outputs: filtered reads and proposal events.
- **Invariants:** Unrestricted shared transcripts are not authoritative state.
- **Failure behavior:** Forbidden reads/writes, forged authority, or malformed proposals are denied and logged.
- **Integrations:** Authorization, graph API, dispatcher, packet store.
- **Acceptance:** A program worker cannot read withheld falsifier material or directly set `SUPPORTED` even through low-level interfaces.
- **Dependencies:** F-REQ-027, F-REQ-034.
- **Ambiguity/contradiction notes:** Prompt text alone is insufficient enforcement.

### F-REQ-036 — Freeze complete source provenance

- **Source:** §5.2 line 448; §6.1 lines 487-492
- **Category:** Intake / provenance
- **Requirement:** Store exact source bytes, URI/repository commit, status fields, page spans, retrieval date, licenses, hashes, prior versions/edit history, surrounding definitions, and status labels as claims.
- **Inputs/outputs:** Inputs: first-party source and metadata. Outputs: immutable source records.
- **Invariants:** Source/version identity is content-addressed and status is not baked in as truth.
- **Failure behavior:** Missing or conflicting provenance produces a gap/status uncertainty and blocks affected release/import decisions.
- **Integrations:** Source store, intake, retrieval, run contract.
- **Acceptance:** Source mutation or version drift changes hashes and invalidates dependent contracts.
- **Dependencies:** F-REQ-004.
- **Ambiguity/contradiction notes:** Original sources may later be corrected; truth uses claim-specific source priority.

### F-REQ-037 — Dual-parser structured Statement IR

- **Source:** §5.2 line 449; §6.1 lines 494-516
- **Category:** Intake / semantics
- **Requirement:** Use two independently implemented parses to extract binders, domains, quantifiers/scopes, definitions, hypotheses, conclusion, requested outcome, parameter regime, edge cases, ambiguities, variants, and source spans.
- **Inputs/outputs:** Inputs: frozen source/context. Outputs: typed Statement IR candidates and reconciliation record.
- **Invariants:** Different prompts to the same model are correlated, not independent; only exact/semantically justified matches reconcile.
- **Failure behavior:** Malformed or contradictory parses remain separate/rejected and cannot silently fall back to raw text.
- **Integrations:** Parsers, probe engine, lattice, downstream packet/graph.
- **Acceptance:** Round-trip tests preserve quantifiers, domains, constraints, definitions, and selected interpretation through downstream execution.
- **Dependencies:** F-REQ-004, F-REQ-022, F-REQ-036.
- **Ambiguity/contradiction notes:** One deterministic parser plus a separately implemented semantic model is permitted.

### F-REQ-038 — Explicit interpretation relations and release block

- **Source:** §5.2 line 450; §6.1 lines 508-525
- **Category:** Intake / graph
- **Requirement:** Record exact, plausible, stronger, weaker, equivalent, and special-case interpretation/variant relations with unresolved decisions and fidelity risk.
- **Inputs/outputs:** Inputs: reconciled parses and probes. Outputs: lattice, ProblemContract, risk and status-audit request.
- **Invariants:** Relations are explicit and provenance-bound; materially distinct readings do not merge.
- **Failure behavior:** Unresolved ambiguity produces nodes and blocks intended-target release.
- **Integrations:** Statement IR, graph, controller, release.
- **Acceptance:** Contradictory interpretations remain distinct and the selected ID is actually used by computation/formalization/release.
- **Dependencies:** F-REQ-029, F-REQ-037.
- **Ambiguity/contradiction notes:** Later §10 treats semantic relations themselves as evidentiary claims.

### F-REQ-039 — Executable integrity probes

- **Source:** §5.2 line 451; §6.1 lines 513-516
- **Category:** Intake / falsification
- **Requirement:** Run type/dimension, trivial/boundary, finite exact enumeration, symmetry/metamorphic, paraphrase/mutation, and smallest-domain counterexample probes.
- **Inputs/outputs:** Inputs: interpretation candidates. Outputs: immutable probe artifacts and discovered contradictions/counterexamples.
- **Invariants:** Probe scope and arithmetic mode are explicit; finite evidence does not generalize silently.
- **Failure behavior:** Probe failure, malformed input, or counterexample changes interpretation/claim state and blocks incompatible release.
- **Integrations:** Intake, compute backend, graph, falsifier.
- **Acceptance:** Meaning-preserving transformations retain behavior and meaning-changing mutations alter expected behavior on adversarial fixtures.
- **Dependencies:** F-REQ-010, F-REQ-022, F-REQ-037.
- **Ambiguity/contradiction notes:** Not every problem supports every probe; unsupported probes must be explicit, not silently successful.

### F-REQ-040 — Fresh multi-source status audit

- **Source:** §5.2 line 452; §8.1 lines 1068-1080
- **Category:** Retrieval / status
- **Requirement:** Audit exact wording, objects, authors, references/citations, later papers, MathOverflow, Erdős history, OEIS, and formal libraries; classify known/open/false/misquoted/ambiguous/status-uncertain with dated provenance.
- **Inputs/outputs:** Inputs: source contract and interpretations. Outputs: status claims/conflicts and literature tasks.
- **Invariants:** Open/novel status is a sourced dated claim, never inferred from one database or filename.
- **Failure behavior:** Conflict or stale status yields `status_uncertain`; every deep run refreshes or uses a recent signed snapshot.
- **Integrations:** Literature/OEIS/theorem retrieval, selector, novelty gate.
- **Acceptance:** A known solved historical problem is classified as rediscovery/known rather than novel.
- **Dependencies:** F-REQ-005, F-REQ-036.
- **Ambiguity/contradiction notes:** The specification does not define “recent”; policy must version the threshold.

### F-REQ-041 — Cold hypotheses are search inputs only

- **Source:** §5.2 line 453
- **Category:** Search / evidence boundary
- **Requirement:** Use the short literature-blind pass only to produce hypotheses and improved queries, never publication or imported-fact evidence.
- **Inputs/outputs:** Inputs: interpretations and 5–10% budget. Outputs: quarantined hypotheses/query terms.
- **Invariants:** Cold-pass confidence/consensus does not raise truth or novelty.
- **Failure behavior:** Any attempt to route cold output directly into promotion is rejected.
- **Integrations:** Programs, retrieval query builder, graph working memory.
- **Acceptance:** A seemingly complete cold proof remains UNKNOWN until normal evidence/gates validate it.
- **Dependencies:** F-REQ-005, F-REQ-032.
- **Ambiguity/contradiction notes:** None.

### F-REQ-042 — Frozen theorem-level solver packet

- **Source:** §5.2 line 454; §6.4 lines 597-625
- **Category:** Retrieval / artifact
- **Requirement:** Build an immutable packet of exact theorem records, hypotheses, applicability checks, formal declarations, negative results, and provenance; give solvers selected records while source auditors retain full citations.
- **Inputs/outputs:** Inputs: query bundle and audited sources. Outputs: versioned packet hash and theorem records.
- **Invariants:** Retrieved claims remain proposals until exact-source/applicability audit.
- **Failure behavior:** Malformed, stale, inaccessible, injection-bearing, or conflicting records remain untrusted/unresolved and cannot become usable facts.
- **Integrations:** Literature service, import auditor, packet store, workers, cache identity.
- **Acceptance:** Changing any theorem/hypothesis/source span changes packet identity and affected caches.
- **Dependencies:** F-REQ-030, F-REQ-040.
- **Ambiguity/contradiction notes:** Negative search is coverage evidence, never proof of novelty.

### F-REQ-043 — Problem scoring uses complete feature families

- **Source:** §5.2 line 455; §6.2 lines 529-545
- **Category:** Selection
- **Requirement:** Score with status, statement, literature, formal, computational, mathematical, operational, reuse, and locally measured tool-fit features.
- **Inputs/outputs:** Inputs: contract, packet, probes, authenticated telemetry. Outputs: feature vector with uncertainty.
- **Invariants:** Vendor reputation, prize value, popularity, or presence of a formal statement is never a solvability oracle.
- **Failure behavior:** Missing/sparse features produce wide intervals and weak priors, not fabricated certainty.
- **Integrations:** Intake, retrieval, computation, formal, telemetry, selector.
- **Acceptance:** Feature changes from real state alter posterior/acquisition decisions and are traceable.
- **Dependencies:** F-REQ-008, F-REQ-040.
- **Ambiguity/contradiction notes:** Expected conceptual depth remains subjective and must carry uncertainty.

### F-REQ-044 — Mechanism-distinct program generation

- **Source:** §5.2 line 456; §6.5 lines 641-653
- **Category:** Search / diversity
- **Requirement:** Dispatch program workers that differ in at least two specified mechanism/tool/source/objective/model/representation/counterfactual dimensions; each declares falsifiers and bottlenecks.
- **Inputs/outputs:** Inputs: interpretation, packet slice, method profile. Outputs: normalized claims, dependencies, proof/experiment, falsifier, bottleneck, cost.
- **Invariants:** Same-model identical-context role prompts count as one correlated method.
- **Failure behavior:** Workers may not import uncited theorems, strengthen assumptions, label evidence, or hide failed mechanisms.
- **Integrations:** Dispatcher, authority policy, program archive, graph.
- **Acceptance:** Diversity metrics consume actual fingerprints/information boundaries, not role names.
- **Dependencies:** F-REQ-018, F-REQ-027.
- **Ambiguity/contradiction notes:** Different model family is optional if other independent dimensions suffice.

### F-REQ-045 — Direct-first typed AND/OR blueprint

- **Source:** §5.2 line 457; §7.4 lines 910-921; §9.2 lines 1273-1277
- **Category:** Search / proof planning
- **Requirement:** Attempt the target directly first; on failure encode alternative sufficient lemma sets, prerequisites, centrality, semantic risk, formalization targets, and dynamic leaves with true AND/OR semantics.
- **Inputs/outputs:** Inputs: target and admitted/working claims. Outputs: versioned proof blueprint and frontier.
- **Invariants:** Unproved helpers are explicit debt and cannot merely restate/imply the target.
- **Failure behavior:** Failed leaves localize repair and can reopen alternatives; malformed/cyclic semantics do not collapse to a fake single goal.
- **Integrations:** Graph, architect, controller, Lean.
- **Acceptance:** Independent cases demonstrate AND requires all children, OR requires one valid alternative, and helper debt never disappears.
- **Dependencies:** F-REQ-006, F-REQ-007.
- **Ambiguity/contradiction notes:** Quarantined development blueprints may contain `sorry`; production evidence cannot import them.

### F-REQ-046 — Leased dynamic-leaf execution

- **Source:** §5.2 line 458
- **Category:** Control / workers
- **Requirement:** Execute independent frontier leaves in parallel using disjoint branch capsules, scoped tools/information, explicit budgets, leases, and structured outputs.
- **Inputs/outputs:** Inputs: selected actions and run contracts. Outputs: claim/source/experiment/formal proposals and immutable artifacts.
- **Invariants:** Each action is idempotent or fenced against duplicate non-idempotent effects.
- **Failure behavior:** Crash/timeout/rate limit yields censored operational events, lease recovery, and no fabricated mathematical failure.
- **Integrations:** Controller, scheduler, authorities, artifact store.
- **Acceptance:** Concurrent workers cannot write outside their capsules or duplicate a fenced external side effect after lease recovery.
- **Dependencies:** F-REQ-027, F-REQ-035.
- **Ambiguity/contradiction notes:** Detailed lease/fencing requirements follow in §§10 and 14.

### F-REQ-047 — Evidence-type admission with retained weak tiers

- **Source:** §5.2 line 459
- **Category:** Truth admission
- **Requirement:** Route each artifact to its kind-specific validator, assign only justified evidence/truth tiers, and retain unverified claims solely as labeled search guidance.
- **Inputs/outputs:** Inputs: frozen artifacts and graph context. Outputs: admission/rejection events and affected closure.
- **Invariants:** A general status/`passed=true` is invalid and no weak claim silently becomes a premise.
- **Failure behavior:** Validation failure rejects/quarantines evidence; refutation or invalidation propagates correctly.
- **Integrations:** Evidence router, validators, graph, controller.
- **Acceptance:** Forged evidence metadata/status cannot promote without underlying semantic validation.
- **Dependencies:** F-REQ-006, F-REQ-014, F-REQ-032.
- **Ambiguity/contradiction notes:** Evidence losing support causes downgrade, not automatic refutation.

### F-REQ-048 — Bidirectional informal/formal synchronization

- **Source:** §5.2 line 460; §9.2 lines 1294-1303
- **Category:** Formal integration
- **Requirement:** Share claim IDs between informal and formal artifacts; every logically substantive sentence links to a Lean declaration, audited source theorem, or explicit formal debt, and changes propagate both directions.
- **Inputs/outputs:** Inputs: graph claims, prose proof, Lean declarations/diagnostics. Outputs: synchronized dependency cones and revocations.
- **Invariants:** A formal counterexample/revised hypothesis invalidates prose dependents; informal clarification invalidates correspondence until reapproved.
- **Failure behavior:** Divergence blocks release and reopens repair work.
- **Integrations:** Graph, proof compiler, Lean service, correspondence auditor.
- **Acceptance:** Mutating either side invalidates the linked certificate/cone and cannot leave cached approval active.
- **Dependencies:** F-REQ-009, F-REQ-033, F-REQ-045.
- **Ambiguity/contradiction notes:** Formalization debt may remain only under accurately weaker release labels.

### F-REQ-049 — Adaptive allocation and operational censoring

- **Source:** §5.2 line 461
- **Category:** Control / failure
- **Requirement:** Allocate adaptively from posterior utility, information gain, unlock, reuse, diversity, cost, duplication, and semantic risk; rate limits pause work and never mark a branch failed.
- **Inputs/outputs:** Inputs: frontier, telemetry, provider state. Outputs: action selections, pauses, reroutes, posterior updates.
- **Invariants:** Mathematical outcome and operational failure remain distinct.
- **Failure behavior:** Rate limits and interruptions are censored; incompatible artifacts are not reused.
- **Integrations:** Controller, scheduler, provider gateway, learning.
- **Acceptance:** Controlled clocks show rate-limit handling preserves retry count/claim state and later resumes.
- **Dependencies:** F-REQ-008, F-REQ-046.
- **Ambiguity/contradiction notes:** The exact backoff behavior is specified later.

### F-REQ-050 — Assemble only admitted claims and attack independently

- **Source:** §5.2 line 462; §7.9 lines 1048-1052
- **Category:** Proof compilation / verification
- **Requirement:** Compile candidate proofs from admitted graph claims/blueprints, build the formal dependency cone where feasible, and run an independent hostile referee before gates.
- **Inputs/outputs:** Inputs: admitted graph and blueprint. Outputs: candidate proof, referee report, gate inputs.
- **Invariants:** Whole-proof rhetoric cannot hide UNKNOWN nodes or missing dependencies.
- **Failure behavior:** Compiler/referee defects or missing admitted dependencies block gate execution/release.
- **Integrations:** Proof compiler, graph, Lean, referee, release.
- **Acceptance:** Injecting one unknown/tainted dependency prevents candidate release even if prose is complete.
- **Dependencies:** F-REQ-011, F-REQ-045, F-REQ-047.
- **Ambiguity/contradiction notes:** T3 rigorous informal candidates may retain explicit formal debt but require their own standard.

### F-REQ-051 — Evidence-accurate final dispositions

- **Source:** §5.2 line 463
- **Category:** Communication / release
- **Requirement:** Render proof, disproof, verified partial result, rediscovery, formally proved-but-novelty-unresolved, rigorous-informal partial progress, or honest no-result according to the five-axis profile.
- **Inputs/outputs:** Inputs: candidate and gate certificates. Outputs: fixed-vocabulary disposition and supporting bundle.
- **Invariants:** No stronger label than the evidence profile allows.
- **Failure behavior:** Any missing mandatory field or gate produces a narrower/unknown/no-result response, not a success default.
- **Integrations:** Release auditor, renderer, evaluation ledger.
- **Acceptance:** False, partial, known, and gate-disagreement cases each render the correct non-solved outcome through every release entry point.
- **Dependencies:** F-REQ-002, F-REQ-033.
- **Ambiguity/contradiction notes:** The exact public vocabulary is distributed across §§11-13.

### F-REQ-052 — Authenticated learning after current-toolchain replay

- **Source:** §5.2 line 464; §6.11 lines 775-786
- **Category:** Learning
- **Requirement:** Distill proof patterns, tactics, outcomes, failure classes, and routing only after replay under the current toolchain; keep source-import, semantic, procedural, negative, and calibration stores separate.
- **Inputs/outputs:** Inputs: certificates, graph, pipeline fingerprints, outcomes. Outputs: versioned learning records.
- **Invariants:** Different evaluators from trained models and frozen evaluation periods govern value/policy learning.
- **Failure behavior:** Tool/source correction triggers revalidation; speculative memory remains local/quarantined.
- **Integrations:** Replay, persistent stores, selector/controller, evaluator.
- **Acceptance:** A later run changes behavior only when authenticated learning exists and exact compatibility/applicability checks pass.
- **Dependencies:** F-REQ-012, F-REQ-020.
- **Ambiguity/contradiction notes:** M2 gathers telemetry without yet requiring a learned value model.

### F-REQ-053 — Complete selection outcome posterior

- **Source:** §6.2 lines 545-560
- **Category:** Selection / calibration
- **Requirement:** Model full novel resolution, rediscovery/known identification, correct refutation, verified partial, reusable infrastructure, status correction, no progress, and invalid/false promotion as competing outcomes with posterior cost.
- **Inputs/outputs:** Inputs: features and authenticated/censored outcomes. Outputs: probability distributions, credible intervals, survival/cost estimates.
- **Invariants:** Outcomes are mutually competing in the model and wide intervals/weak priors are published until data suffices.
- **Failure behavior:** Timeout/rate limit is censored operational data, not `no_progress` or invalid mathematics.
- **Integrations:** Selector, calibration ledger, telemetry, evaluation.
- **Acceptance:** Independent probability/cost calculations and censoring fixtures match expected posterior update behavior.
- **Dependencies:** F-REQ-008, F-REQ-020, F-REQ-043.
- **Ambiguity/contradiction notes:** The precise Bayesian/ensemble implementation is flexible if calibrated semantics hold.

### F-REQ-054 — Selection exclusions, cheap probes, and separate queues

- **Source:** §6.2 lines 562-570
- **Category:** Selection policy
- **Requirement:** Hard-exclude only malformed, unauthorized, or provably duplicate tasks; give eligible tasks a standard cheap probe, reserve 15–25% exploration, and maintain distinct full-solve, useful-partial, formalization, finite-computation, and reuse rankings.
- **Inputs/outputs:** Inputs: contracts/posteriors/policy. Outputs: exclusion reasons, probes, separate ranked queues.
- **Invariants:** Prize, popularity, and formal-statement availability are not solvability evidence.
- **Failure behavior:** Low score pauses/deprioritizes but does not misclassify mathematical impossibility.
- **Integrations:** Intake, selector, queue, controller.
- **Acceptance:** Boundary tests show only the three hard-exclusion classes are removed and protected lanes remain populated.
- **Dependencies:** F-REQ-008, F-REQ-039, F-REQ-053.
- **Ambiguity/contradiction notes:** The later M1/M2 controllers may implement simplified allocation initially.

### F-REQ-055 — OEIS invocation is deterministic and event-driven

- **Source:** §6.3 lines 572-576
- **Category:** OEIS / orchestration
- **Requirement:** Invoke a deterministic OEIS service when integer sequences arise, specified combinatorial/extremal/recurrence/coefficient signals appear, or source records contain OEIS links/possible markers.
- **Inputs/outputs:** Inputs: exact terms, claim/source metadata, construction. Outputs: typed query request and provenance events.
- **Invariants:** OEIS is a service plus source auditor, never a free-form proof authority.
- **Failure behavior:** Unsupported/noninteger/undefined inputs fail visibly and do not fabricate a query.
- **Integrations:** Computation, intake, retrieval, graph.
- **Acceptance:** Production events demonstrate the trigger conditions and non-trigger cases without test-only wiring.
- **Dependencies:** F-REQ-010, F-REQ-042.
- **Ambiguity/contradiction notes:** Rational exact-ratio transforms are typed outputs despite integer source terms.

### F-REQ-056 — Four linked retrieval indexes and query bundles

- **Source:** §6.4 lines 578-596
- **Category:** Retrieval
- **Requirement:** Retrieve across bibliographic, mathematical, formal, and experimental indexes using exact statements, type/objects/regimes, equivalent forms, techniques/obstructions, citation neighborhoods, formal signatures/premises, and OEIS references.
- **Inputs/outputs:** Inputs: contract, interpretation, cold hypotheses. Outputs: query log and candidate records from all enabled indexes.
- **Invariants:** Retrieved text is untrusted data and separate from verified evidence.
- **Failure behavior:** Offline/unavailable/malformed/injection-bearing results are recorded as coverage gaps and cannot execute instructions or upgrade claims.
- **Integrations:** Literature, theorem DB, OEIS, source auditor.
- **Acceptance:** Adversarial sources cannot alter system policy; query construction and provenance are inspectable and deduplicated.
- **Dependencies:** F-REQ-030, F-REQ-040.
- **Ambiguity/contradiction notes:** Live external coverage may be BLOCKED-EXTERNAL when credentials/access are unavailable.

### F-REQ-057 — TheoremRecord provenance and applicability schema

- **Source:** §6.4 lines 597-616
- **Category:** Retrieval / data model
- **Requirement:** Store canonical theorem, exact hypotheses/conclusion/notation, immutable source URI/version/hash/span/verbatim extract, extraction provenance/confidence, author/date/status/corrections, formal declarations, applicability conditions/checks, citations, independent status, and license constraints.
- **Inputs/outputs:** Inputs: retrieved source bytes and extraction. Outputs: immutable TheoremRecord.
- **Invariants:** Theorem statement and hypotheses travel together; summaries/snippets are query leads only.
- **Failure behavior:** Missing exact source/hypotheses or failed applicability leaves the record unaudited and unusable as a premise.
- **Integrations:** Packet store, import auditor, graph, licensing policy.
- **Acceptance:** A theorem with a silently omitted hypothesis is rejected by an independent negative test.
- **Dependencies:** F-REQ-036, F-REQ-042.
- **Ambiguity/contradiction notes:** OCR/model extraction confidence does not itself determine truth.

### F-REQ-058 — Retrieval ranking is relevance, not truth

- **Source:** §6.4 lines 618-619
- **Category:** Retrieval ranking
- **Requirement:** Rank by semantic/formula match, hypothesis compatibility, source authority/freshness, corroboration, formal linkage, citation proximity, and query diversity; never treat citation count as truth.
- **Inputs/outputs:** Inputs: candidate TheoremRecords and query. Outputs: ranked candidates with component scores.
- **Invariants:** Ranking cannot change evidence/truth status.
- **Failure behavior:** Malformed scores or absent fields degrade ranking/flag uncertainty rather than admit facts.
- **Integrations:** Retriever, packet builder, import auditor.
- **Acceptance:** Independent scoring fixtures show a highly cited but inapplicable theorem ranks/validates below an applicable exact source.
- **Dependencies:** F-REQ-057.
- **Ambiguity/contradiction notes:** Exact weight values are unspecified and require evaluation.

### F-REQ-059 — Retriever and import auditor are separate functions

- **Source:** §6.4 lines 620-625
- **Category:** Retrieval / separation of duties
- **Requirement:** Use a recall-oriented retriever to propose uncertain matches and an independent import auditor to verify exact source, hypotheses, scope, version, and consequence; only audited imports become usable graph facts.
- **Inputs/outputs:** Inputs: candidate records and target use. Outputs: audited-source admission or rejection with reasons.
- **Invariants:** Novelty review has a separate query log and no incentive to support proof.
- **Failure behavior:** Self-audit, missing source bytes, scope mismatch, or unavailable evidence prevents import use.
- **Integrations:** Retriever, auditor, graph, novelty service.
- **Acceptance:** A relevant-looking but inapplicable source is retrieved yet rejected from premise use.
- **Dependencies:** F-REQ-042, F-REQ-057.
- **Ambiguity/contradiction notes:** Independence must be enforced technically, not by prompt alone.

### F-REQ-060 — Authority action restrictions are enforced

- **Source:** §6.5 lines 629-712
- **Category:** Agent authorization
- **Requirement:** Enforce the allowed/forbidden actions and required structured outputs for governor, intake/retrieval, program workers, computational falsifier, formalization authority, referee, and release auditor.
- **Inputs/outputs:** Inputs: authenticated authority/action/request. Outputs: authorized event/result or explicit denial.
- **Invariants:** Governor cannot change truth; intake cannot write proofs into truth; workers cannot label evidence; formalization cannot decide novelty; referee cannot repair same pass; release cannot generate repair same pass.
- **Failure behavior:** Privilege escalation, cross-agent forgery, self-approval, or confused-deputy attempts fail closed and are audited.
- **Integrations:** Dispatcher, graph API, tools, release.
- **Acceptance:** Direct low-level invocation tests prove each prohibited action is rejected, including malicious/unavailable agents.
- **Dependencies:** F-REQ-027, F-REQ-035.
- **Ambiguity/contradiction notes:** The spec gives objectives in prose; repository policy must translate them into machine-enforced capabilities.

### F-REQ-061 — Algorithm matched to each search topology

- **Source:** §6.7 lines 720-731
- **Category:** Search algorithms
- **Requirement:** Use contextual Thompson/UCB across programs/tools, quality-diversity best-first/MAP-Elites for mechanisms, AO*/best-first for AND/OR blueprints, PUCT/MCTS plus beam/best-first for Lean, evolutionary islands only for executable candidates, and debate only for proposals/defects.
- **Inputs/outputs:** Inputs: level-specific state and authenticated feedback. Outputs: algorithm-appropriate frontier/selection updates.
- **Invariants:** Debate and learned values are not truth oracles; executable evolution requires hard fitness.
- **Failure behavior:** Unavailable algorithms degrade explicitly to a documented compatible policy without falsely claiming the specified portfolio.
- **Integrations:** Selector, program archive, blueprint, Lean search, compute evolution.
- **Acceptance:** Production routing sends representative tasks to the correct search level and consumes results in future decisions.
- **Dependencies:** F-REQ-007, F-REQ-023, F-REQ-028.
- **Ambiguity/contradiction notes:** M1 permits a simpler best-first/UCB controller; full portfolio is a later/full-scale requirement.

### F-REQ-062 — Immutable computation service contract

- **Source:** §6.8 lines 733-754
- **Category:** Computation API
- **Requirement:** Expose submit, poll, artifact, independent replay, and certificate verification over immutable ExperimentSpecs containing claim purpose, code commit/entry point, exact domain/coverage, tool versions, arithmetic/precision, seed/limits, output/checker schema, and network/sandbox policy.
- **Inputs/outputs:** Inputs: fully specified ExperimentSpec. Outputs: job ID, status, ComputationalArtifact, ReplayReport, CertificateReport.
- **Invariants:** Inputs and artifacts are content-addressed and cannot mutate after submission.
- **Failure behavior:** Missing/invalid fields, resource violations, timeout, or unavailable backend fail closed with cleanup and no evidence admission.
- **Integrations:** Compute scheduler, sandbox, artifact store, evidence router.
- **Acceptance:** Restart/replay of an exact job yields the same output/hash and immutable records reject mutation.
- **Dependencies:** F-REQ-010, F-REQ-046.
- **Ambiguity/contradiction notes:** M1 initially supports exact Python enumeration/witness checking; broader tools are conditional on backend availability.

### F-REQ-063 — Checked computational evidence classification

- **Source:** §6.8 lines 756-765
- **Category:** Computation / truth
- **Requirement:** Classify each artifact as exactly one of heuristic/numerical, candidate counterexample, exact counterexample, exhaustive finite subcase, certificate-checked lemma, or complete justified finite reduction, and validate rather than trust the label.
- **Inputs/outputs:** Inputs: artifact, scope/coverage, arithmetic, checker result. Outputs: typed evidence profile and admission/rejection.
- **Invariants:** Scope never expands beyond demonstrated coverage; floating point, CAS, and SAT/SMT require their specified error/certificate paths.
- **Failure behavior:** Forged class/status, zero coverage, missing exact witness, failed independent replay, or invalid certificate rejects/downgrades evidence.
- **Integrations:** Compute backend, certificate adapters, graph.
- **Acceptance:** Adversarial metadata cannot turn a heuristic or finite sample into exact/general proof.
- **Dependencies:** F-REQ-047, F-REQ-062.
- **Ambiguity/contradiction notes:** Complete finite reduction additionally needs a justified proof that the reduction covers the original claim.

### F-REQ-064 — Lean and verification are active independent evidence services

- **Source:** §6.9 lines 767-769; §6.10 lines 771-773
- **Category:** Formal / verification architecture
- **Requirement:** Integrate Lean from intake onward and operate verification with independent models, tools, caches, and success metrics expressed as discharged obligations, not scalar confidence.
- **Inputs/outputs:** Inputs: formal targets/goals/candidates and verification obligations. Outputs: proof states/certificates and obligation reports.
- **Invariants:** A formal worker cannot decide novelty and a verifier cannot generate truth by agreement.
- **Failure behavior:** Missing independence/provenance or incomplete obligations leaves the corresponding status unresolved.
- **Integrations:** Intake, controller, Lean, referee, release.
- **Acceptance:** Alternate direct entry points still invoke target audit, clean replay, and gate policy.
- **Dependencies:** F-REQ-009, F-REQ-011, F-REQ-060.
- **Ambiguity/contradiction notes:** Model/tool independence is evidenced across separate dimensions, not inferred from process names.

### F-REQ-065 — Typed memory stores never conflate evidence

- **Source:** §6.11 lines 775-786
- **Category:** Memory / learning
- **Requirement:** Maintain distinct problem-local, mechanically verified semantic, audited external-import, procedural, negative, and calibration memories with their specific reuse/revalidation rules.
- **Inputs/outputs:** Inputs: typed graph events, sources, tactics, failures, telemetry. Outputs: separated stores and guarded lookup results.
- **Invariants:** Audited external theorems remain sourced imports; procedural hints are rechecked; no unauthenticated labels enter calibration.
- **Failure behavior:** Correction/version drift triggers revalidation or applicability review and revocation from dependents.
- **Integrations:** Graph, learning, retrieval, Lean, selector.
- **Acceptance:** Persistence/restart tests show false local claims do not leak cross-problem while replayable semantic records do.
- **Dependencies:** F-REQ-012, F-REQ-052.
- **Ambiguity/contradiction notes:** Problem-local failures may be reused only as labeled negative/search hints.

### F-REQ-066 — Typed minimal service interfaces

- **Source:** §6.12 lines 788-801
- **Category:** Integration contracts
- **Requirement:** Provide typed literature, theorem DB, OEIS, computation, Lean, ATP/SMT/SAT, claim-graph, and controller request/response interfaces with exact provenance and no truth upgrade from retrieval/solver testimony.
- **Inputs/outputs:** Inputs/outputs: the minimal requests and trusted responses listed in the §6.12 table.
- **Invariants:** Every response stays within its trust boundary; semantic translation obligations remain explicit.
- **Failure behavior:** Malformed/schema-drifted/untrusted responses fail closed or remain proposals; they cannot be coerced into success.
- **Integrations:** All service adapters and orchestrator.
- **Acceptance:** Contract and production integration tests exercise positive, malformed, timeout, cancellation, and stale-version paths.
- **Dependencies:** F-REQ-024, F-REQ-055, F-REQ-059, F-REQ-062, F-REQ-064.
- **Ambiguity/contradiction notes:** Interfaces alone do not satisfy live integration readiness.

### F-REQ-067 — Problem acquisition formula and competing costs

- **Source:** §7.2 lines 811-845
- **Category:** Selection mathematics
- **Requirement:** Maintain π_o(p) over the specified outcome set and posterior total cost, then compute A_p using expected outcome value, exploration SD, EIG, reuse, portfolio diversity, freshness, cost exponent α∈[0.7,1], and explicit ambiguity/staleness/library-gap penalties.
- **Inputs/outputs:** Inputs: calibrated outcome/cost distributions and project-set V_o/weights. Outputs: acquisition score with interval/rationale.
- **Invariants:** Values come from project policy, not models; SD applies only in protected exploration.
- **Failure behavior:** Malformed probabilities/costs or unsupported source/license/false-promotion risk block allocation explicitly.
- **Integrations:** Selector, calibration, controller, policy.
- **Acceptance:** Independent numeric fixtures recompute numerator, denominator, penalties, α bounds, and expected ordering without implementation helpers.
- **Dependencies:** F-REQ-053, F-REQ-054.
- **Ambiguity/contradiction notes:** EIG/reuse/diversity estimators are flexible but must be provenance- and uncertainty-aware.

### F-REQ-068 — Posterior sampling, exploration range, and hard constraints

- **Source:** §7.2 lines 839-848
- **Category:** Selection policy
- **Requirement:** Use posterior sampling in exploitation, reserve 15–25% exploration, report point estimates and intervals, and evaluate hard authorization/source/license/risk constraints separately.
- **Inputs/outputs:** Inputs: posterior distributions, constraints, lane budget. Outputs: sampled acquisitions and blocked reasons.
- **Invariants:** A low numeric score never means mathematically impossible.
- **Failure behavior:** Constraint failure blocks allocation; uncertainty alone routes to exploration or deferral.
- **Integrations:** Selector, queue, policy.
- **Acceptance:** Deterministic seeded tests show sampling diversity and exact protected share while forbidden tasks never enter either lane.
- **Dependencies:** F-REQ-067.
- **Ambiguity/contradiction notes:** The controller pseudocode selects 20%, a valid value inside the required range.

### F-REQ-069 — Lean PUCT with exact state transpositions

- **Source:** §7.3 lines 881-890
- **Category:** Formal search
- **Requirement:** Score Lean actions with Q, prior, visit counts, ΔverifiedDebt, and cost; key transpositions by Lean/Mathlib, imports/options, elaborated local context, exact target, and trust policy.
- **Inputs/outputs:** Inputs: GoalCapsule, action statistics, debt/cost. Outputs: PUCT score and cache lookup.
- **Invariants:** Pretty-printed text alone is never a state key.
- **Failure behavior:** Any environment/context/trust change misses/invalidates the cache rather than reusing stale proof state.
- **Integrations:** Lean service, proof-state cache, controller.
- **Acceptance:** Independent formula fixtures and collision tests distinguish visually identical but elaborationally different goals.
- **Dependencies:** F-REQ-009, F-REQ-015.
- **Ambiguity/contradiction notes:** c_puct, β, and γ are policy/calibration parameters.

### F-REQ-070 — Frozen target-relative verified debt

- **Source:** §7.3 lines 886-892
- **Category:** Search metric / anti-gaming
- **Requirement:** Define verified debt as the frozen risk/cost-weighted frontier of all target-reachable proof, helper, semantic-correspondence, and import obligations; credit D_before−D_after.
- **Inputs/outputs:** Inputs: locked target and audited blueprint. Outputs: debt snapshot and delta.
- **Invariants:** New helper obligations are included; a helper restating/implying the target gets zero or negative credit; weights remain frozen during evaluation.
- **Failure behavior:** Blueprint/weight mutation invalidates the metric run and prevents progress claims.
- **Integrations:** Graph, blueprint, Lean search, evaluation.
- **Acceptance:** Mutation-style tests show moving difficulty into one unproved helper cannot improve score.
- **Dependencies:** F-REQ-045, F-REQ-067.
- **Ambiguity/contradiction notes:** Weights are independently audited before evaluation rather than learned mid-run.

### F-REQ-071 — Mechanism fingerprint consumed by quality-diversity archive

- **Source:** §7.4 lines 894-921
- **Category:** Search diversity
- **Requirement:** Fingerprint target interpretation, reformulation, method, central lemma, introduced objects, external theorems, computation, falsifiers, and formal route; use it in diversity bins, duplicate penalties, selection, and branch archives.
- **Inputs/outputs:** Inputs: program proposal. Outputs: canonical fingerprint, bin assignment, overlap metrics.
- **Invariants:** Fingerprint is operationally consumed, not decorative metadata.
- **Failure behavior:** Missing/invalid fingerprint prevents independent-branch credit and defaults to correlated/duplicate handling.
- **Integrations:** Program worker, archive, deduplication, controller.
- **Acceptance:** Changing mechanism fields changes archive/selection behavior while label-only changes do not.
- **Dependencies:** F-REQ-044.
- **Ambiguity/contradiction notes:** Crossovers may combine verified subgraphs only.

### F-REQ-072 — Permitted branch generation preserves semantics

- **Source:** §7.4 lines 910-921
- **Category:** Search branching
- **Requirement:** Support direct, contrapositive/minimal-counterexample, equivalent representation, explicit stronger/weaker variant, sufficient-lemma, counterexample twin, retrieved theorem, computational invariant, formal decomposition, and verified-subgraph crossover branches.
- **Inputs/outputs:** Inputs: target/graph/archive. Outputs: related branches with explicit relation/obligations.
- **Invariants:** Assumption and variant relations remain explicit and evidenced.
- **Failure behavior:** Silent strengthening, unverified crossover, or missing relation evidence rejects/penalizes the branch.
- **Integrations:** Lattice, graph, architect, archive.
- **Acceptance:** Property tests show every branch retains the correct target/assumption relationship and dependents.
- **Dependencies:** F-REQ-038, F-REQ-071.
- **Ambiguity/contradiction notes:** Not all branch types are applicable to every problem.

### F-REQ-073 — Cascade duplicate detection and safe merging

- **Source:** §7.5 lines 923-934
- **Category:** Search deduplication
- **Requirement:** Detect duplicates through exact formal context, formula/dependency isomorphism, premise/fingerprint MinHash, plan embeddings, behavior vectors, and borderline comparison; merge only exact duplicates and penalize semantic near-duplicates.
- **Inputs/outputs:** Inputs: branch states/fingerprints/tests. Outputs: exact merge, near-duplicate penalty, or distinct result.
- **Invariants:** Different assumptions, falsifiers, or obligations remain separate; exact merges preserve evidence and cost histories.
- **Failure behavior:** Uncertain/borderline matches stay separate rather than destructive merge.
- **Integrations:** Archive, graph, controller, cache.
- **Acceptance:** Adversarial near-duplicate fixtures cannot lose distinct obligations, and exact duplicates do not double-count utility/evidence.
- **Dependencies:** F-REQ-071, F-REQ-072.
- **Ambiguity/contradiction notes:** Embedding/model comparison is last-resort and not authoritative.

### F-REQ-074 — Structured failure certificates and honest kill semantics

- **Source:** §7.6 lines 936-952
- **Category:** Failure / search
- **Requirement:** Record branch/fingerprint, exact failed obligation, first invalid claim/missing premise, evidence, actions/cost, learned scope, reopen condition, and related branches; kill only for valid counterexample, logical impossibility, dominated identical state, or policy constraint.
- **Inputs/outputs:** Inputs: failed action/branch evidence. Outputs: immutable failure certificate and paused/killed decision.
- **Invariants:** Resource exhaustion or “model could not finish” is censored, not mathematical failure.
- **Failure behavior:** Incomplete failures pause with explicit scope/reopen conditions rather than erase the branch.
- **Integrations:** Controller, negative memory, graph, telemetry.
- **Acceptance:** Timeout fixtures do not kill; exact counterexamples do and propagate their scoped consequences.
- **Dependencies:** F-REQ-046, F-REQ-049.
- **Ambiguity/contradiction notes:** “Logical impossibility” itself requires adequate checked evidence.

### F-REQ-075 — Pause, terminate, and reopen state machine

- **Source:** §7.7 lines 954-970
- **Category:** Control state
- **Requirement:** Pause only after all four stagnation conditions hold for K reviews; terminate only on falsification, stronger verified subsumption, semantic invalidity, or prohibition; reopen on the six specified evidence/tool/human changes.
- **Inputs/outputs:** Inputs: review history, marginal value/cost, debt/information, signatures, exploration duties, triggers. Outputs: state transition event.
- **Invariants:** Transitions are append-only, justified, and preserve resumable state.
- **Failure behavior:** Invalid/stale trigger or incomplete K history cannot silently kill or reopen.
- **Integrations:** Controller, graph, retrieval, tool registry, human steering.
- **Acceptance:** Controlled-clock/state tests cover every legal/illegal transition and restart preservation.
- **Dependencies:** F-REQ-074.
- **Ambiguity/contradiction notes:** K is configurable but must be recorded in the run contract.

### F-REQ-076 — Progressive compute bands and reserves

- **Source:** §7.8 lines 972-987
- **Category:** Budget control
- **Requirement:** Use bands 0–5 with their specified purposes/actions/expansion conditions and maintain a 10–20% reserve for surprises, independent verification, and recovery.
- **Inputs/outputs:** Inputs: evidence/progress and global budget. Outputs: band transitions and reserved capacity.
- **Invariants:** Compute expands because evidence warrants it, not to occupy a fixed worker count.
- **Failure behavior:** Missing verification capacity or expansion evidence prevents entering deeper bands.
- **Integrations:** Controller, selector, verifier pool.
- **Acceptance:** Fixtures cover every band transition and prove reserve cannot be consumed by ordinary generation.
- **Dependencies:** F-REQ-008, F-REQ-070.
- **Ambiguity/contradiction notes:** Percentages/counts are initial defaults requiring ablation, not measured optima.

### F-REQ-077 — Integrated closed-loop production orchestration

- **Source:** §7.9 lines 989-1055
- **Category:** End-to-end orchestration
- **Requirement:** Implement the full intake→probes/status→cold pass/packet→acquisition→graph/archive/blueprint→leased execution→artifact validation/revocation→posterior/debt update→stagnation→checkpoint→compile/referee/five gates→learning/render loop.
- **Inputs/outputs:** Inputs: problem source and global budget. Outputs: replayable release or honest triage/no-result.
- **Invariants:** Every state-changing result is frozen, validated, evented, and consumed by later control/release decisions.
- **Failure behavior:** Failure at any stage is fail-closed, persisted, and recoverable at the highest compatible durable stage.
- **Integrations:** Every EGMRA subsystem.
- **Acceptance:** A non-mocked M1 true and false claim traverse production entry points; state/evidence changes affect future selection and all injected stage failures block release.
- **Dependencies:** F-REQ-004 through F-REQ-076 as applicable.
- **Ambiguity/contradiction notes:** External services may be optional/unavailable, but the local M1 loop must remain genuine.

### F-REQ-078 — Verification capacity, routing, budget rationale, and full cost

- **Source:** §7.10 lines 1057-1064
- **Category:** Control safeguards
- **Requirement:** Reserve verification capacity before opening proof branches; route models/tools by locally measured task fit; require a governor event for oversized branch budgets; count expert review/formal debt; benchmark after version changes.
- **Inputs/outputs:** Inputs: queue/backlog, local benchmarks, costs, budget policy. Outputs: reserved slots, routes, throttle/rationale events.
- **Invariants:** Generators cannot starve truth admission; vendor benchmark reputation alone does not route.
- **Failure behavior:** Verification congestion throttles generators without downgrading truth.
- **Integrations:** Scheduler, model gateway, telemetry, controller, evaluation.
- **Acceptance:** Concurrency tests show verifier-reserved capacity and starvation resistance under generator load.
- **Dependencies:** F-REQ-008, F-REQ-020.
- **Ambiguity/contradiction notes:** The configured per-branch fraction is policy-defined but recorded.

### F-REQ-079 — Provider-aware backoff capped at 120 seconds

- **Source:** §7.10 line 1064
- **Category:** Control / retry
- **Requirement:** Honor provider-specific state and `Retry-After`, use exponential backoff with jitter capped at exactly 120 seconds per attempt, pause leases, and never consume a mathematical retry.
- **Inputs/outputs:** Inputs: classified provider error, Retry-After, attempt, controlled clock. Outputs: delay/pause/resume event.
- **Invariants:** Transient rate limits are distinct from permanent failures and math outcomes.
- **Failure behavior:** Malformed Retry-After is safely bounded; retry exhaustion follows policy without killing a mathematical claim.
- **Integrations:** Provider gateway, scheduler, leases, telemetry.
- **Acceptance:** Deterministic clock tests cover 120-second cap, jitter bounds, resume, duplicate delivery, and retry accounting.
- **Dependencies:** F-REQ-049.
- **Ambiguity/contradiction notes:** The spec says honor Retry-After and cap per attempt; a larger Retry-After must be represented as repeated pauses or quota state without sleeping above the cap.

### F-REQ-080 — Pinned Erdős corpus and separated status evidence

- **Source:** §8.1 lines 1068-1080
- **Category:** Corpus / status provenance
- **Requirement:** Pin an exact upstream snapshot and store YAML, website, original source, later papers, and expert commentary as separate evidence records with status-change and solution dates.
- **Inputs/outputs:** Inputs: upstream snapshot and source records. Outputs: versioned corpus/status claims.
- **Invariants:** Counts/categories are snapshot-specific and may drift; no single source proves open/novel status.
- **Failure behavior:** Conflict produces status uncertainty and a literature task.
- **Integrations:** Ingest, source store, status audit, selector.
- **Acceptance:** Changing upstream commit produces a distinct corpus identity and stale deep runs cannot reuse status silently.
- **Dependencies:** F-REQ-036, F-REQ-040.
- **Ambiguity/contradiction notes:** The numerical counts at commit 8b46f270 are context/evidence, not immutable global constants.

### F-REQ-081 — OEIS caching, rate, and human-submission policy

- **Source:** §8.2 lines 1082-1085
- **Category:** OEIS / external policy
- **Requirement:** Cache OEIS JSON responses with retrieval time/content hash, respect usage/rate limits, forbid AI-generated editorial/Pink Box/bulk submissions, and require an identified responsible human for any permitted submission.
- **Inputs/outputs:** Inputs: read-only query and policy. Outputs: cached response or denied submission action.
- **Invariants:** Default OEIS integration is read-only research use.
- **Failure behavior:** Rate limit pauses; prohibited submission or missing human authorization is denied and audited.
- **Integrations:** OEIS client, cache, feature policy, human authorization.
- **Acceptance:** Direct client calls cannot submit or bypass rate policy; cached stale results are labeled/versioned.
- **Dependencies:** F-REQ-055, F-REQ-060.
- **Ambiguity/contradiction notes:** No live submission is required for implementation completeness.

### F-REQ-082 — Complete OEIS request and transform budget

- **Source:** §8.2 lines 1086-1110
- **Category:** OEIS API
- **Requirement:** Accept the specified query/problem/claim IDs, exact string terms, value/index/construction/generator artifact, enumerated local transforms, and default/explicit maximum of 20 remote queries; locally generate and deduplicate transforms while preserving exact transform paths.
- **Inputs/outputs:** Inputs: typed OEIS request. Outputs: bounded unique transformed queries with provenance.
- **Invariants:** Offsets/sign/normalization/subsequence choices are never forgotten.
- **Failure behavior:** Invalid terms/IDs/budget/transform or duplicate path fails/normalizes visibly without exceeding max_queries.
- **Integrations:** Transform registry, OEIS client, artifact store.
- **Acceptance:** Independent examples enumerate every claimed transform, honor 20-query cap, and preserve path/offset metadata.
- **Dependencies:** F-REQ-055, F-REQ-081.
- **Ambiguity/contradiction notes:** The list contains parameterized transforms whose precise parameter syntax must be defined by the implementation.

### F-REQ-083 — Typed OEIS transforms with explicit preconditions

- **Source:** §8.2 lines 1110-1112
- **Category:** OEIS transforms / correctness
- **Requirement:** Each transform declares domains, parameters, preconditions, and relevant inverse; exact ratios reject zero denominators, Dirichlet inversion requires invertibility, complements require a universe/baseline, normalization a nonzero scale, and subsequences an index map.
- **Inputs/outputs:** Inputs: typed sequence plus parameters. Outputs: typed sequence and path/inverse metadata.
- **Invariants:** Undefined transforms never silently emit a query.
- **Failure behavior:** Empty/degenerate/negative/duplicate/overflow-prone/precondition-failing inputs return explicit typed errors without partial remote calls.
- **Integrations:** OEIS query builder, exact arithmetic.
- **Acceptance:** Independent calculations cover identity, shifts, prefixes, signs, absolute, complements, gcd normalization, differences/sums, ratios, subsequences, splits, binomial/inverse, Euler, Möbius, and Dirichlet inverse including round trips where defined.
- **Dependencies:** F-REQ-082.
- **Ambiguity/contradiction notes:** Coefficient ring and overflow policy must be explicit; Python big integers can satisfy integer overflow safety locally.

### F-REQ-084 — OEIS response provenance schema

- **Source:** §8.2 lines 1114-1140
- **Category:** OEIS data model
- **Requirement:** Return ranked matches with A-number, score, transform path, offset, prefix overlap/exactness, descriptive/formula/program/cross-reference/reference fields, keywords, entry version/time/hash, no-match transforms, and rate-limit state.
- **Inputs/outputs:** Inputs: OEIS responses and local matching. Outputs: normalized immutable response.
- **Invariants:** Raw/malformed external fields remain untrusted data and cannot execute instructions.
- **Failure behavior:** Missing/schema-drifted/malformed responses are rejected or partially represented with explicit gaps, never as successful proof.
- **Integrations:** OEIS client, cache, retrieval packet.
- **Acceptance:** Malformed JSON, duplicate A-numbers, stale versions, and injection text are handled without truth upgrade or policy execution.
- **Dependencies:** F-REQ-081, F-REQ-082.
- **Ambiguity/contradiction notes:** Scoring implementation is specified separately.

### F-REQ-085 — OEIS ranking and held-out verification workflow

- **Source:** §8.3 lines 1142-1163
- **Category:** OEIS verification
- **Requirement:** Score exact-prefix rarity, independently generated terms, offset, construction similarity, formula/recurrence, linked sources, transform complexity, and collision risk; compute at least 5–10 exact query terms when feasible, hold out more terms, test formulas, retrieve sources, and create only NUMERICAL_EVIDENCE claims.
- **Inputs/outputs:** Inputs: generated terms and OEIS candidates. Outputs: ranked heuristic matches, held-out tests, source tasks, conjectural claim events.
- **Invariants:** Held-out terms are not sent in the original query.
- **Failure behavior:** Formula/offset mismatch or insufficient/common prefix reduces/rejects match; no match is not novelty.
- **Integrations:** Compute backend, OEIS, retrieval, graph.
- **Acceptance:** Independent term calculations and collision fixtures distinguish real matches from short-prefix coincidences.
- **Dependencies:** F-REQ-063, F-REQ-084.
- **Ambiguity/contradiction notes:** “When feasible” requires a recorded reason when fewer than five terms exist.

### F-REQ-086 — OEIS never proves a formula or novelty

- **Source:** §8.3 lines 1162-1165
- **Category:** OEIS / truth boundary
- **Requirement:** Treat OEIS matches only as conjecture/literature leads; independently prove or import-audit every formula used, and never infer novelty from no match.
- **Inputs/outputs:** Inputs: match/no-match and candidate formula. Outputs: heuristic claim plus proof/import task.
- **Invariants:** OEIS status cannot exceed numerical evidence by itself.
- **Failure behavior:** Direct use as a proof premise or novelty certificate is rejected.
- **Integrations:** Evidence router, graph, novelty/import auditor.
- **Acceptance:** A forged high-score match cannot promote and a no-match case leaves novelty unresolved.
- **Dependencies:** F-REQ-047, F-REQ-085.
- **Ambiguity/contradiction notes:** None.

### F-REQ-087 — Immutable LiteratureQuery and SourcePacket versions

- **Source:** §8.4 lines 1167-1197
- **Category:** Literature API
- **Requirement:** Implement the typed query and packet fields including contract/interpretation binding, exact/formula/object/technique/equivalence terms, author/seeds/cutoff, citation/formal flags, full query log, records, negative coverage, conflicts, snapshot/corpus versions, and packet hash.
- **Inputs/outputs:** Inputs: LiteratureQuery. Outputs: immutable SourcePacket; targeted re-entry yields linked version.
- **Invariants:** Packet mutation is impossible; new searches create lineage.
- **Failure behavior:** Hash/version mismatch, stale cache, missing query log, or unresolved conflict blocks affected imports/novelty.
- **Integrations:** Retrieval, packet store, run contracts, cache.
- **Acceptance:** Canonical packet serialization is deterministic and any content/policy change invalidates dependent cache keys.
- **Dependencies:** F-REQ-030, F-REQ-042.
- **Ambiguity/contradiction notes:** Live query engines may vary, but schema/provenance and offline behavior remain mandatory.

### F-REQ-088 — Formal premise retrieval with elaboration check

- **Source:** §8.5 lines 1199-1215
- **Category:** Formal retrieval
- **Requirement:** Retrieve premises from natural claim plus exact Lean goal/context/imports/Mathlib using dense, lexical, type-shape, dependency, and sketch-reflect modes; return exact declaration/type/import/source/dependencies/scores and current-context compile status.
- **Inputs/outputs:** Inputs: typed retrievePremises request. Outputs: PremiseCandidate list.
- **Invariants:** A worker may use a candidate only after elaboration; informal linkage is separately audited for strengthening.
- **Failure behavior:** Wrong environment/import/type or elaboration failure makes the premise unusable.
- **Integrations:** Theorem index, Lean environment, source auditor.
- **Acceptance:** Tests distinguish same-named declarations/types across commits/imports and reject inaccessible premises.
- **Dependencies:** F-REQ-015, F-REQ-057, F-REQ-064.
- **Ambiguity/contradiction notes:** M1 requires one Mathlib declaration retriever; all five retrieval modes are broader/full behavior.

### F-REQ-089 — Claim-specific source priority

- **Source:** §8.6 lines 1217-1230
- **Category:** Provenance / evidence policy
- **Requirement:** Select primary/corroborating evidence by claim type: original wording, corrected truth, encoded formal truth, intended interpretation, current status, or novelty, with the caveats in the source-priority matrix.
- **Inputs/outputs:** Inputs: claim purpose and competing sources. Outputs: sourced audit decision with caveats.
- **Invariants:** No universal paper/formal/database total order; snippets/summaries are leads only.
- **Failure behavior:** Unresolved corrections/access/correspondence/status gaps remain explicit and block affected gates.
- **Integrations:** Source auditor, intent, formal, status, novelty.
- **Acceptance:** Fixtures with errata, formal mismatch, stale databases, and absent prior art choose the correct evidence path without overclaiming.
- **Dependencies:** F-REQ-033, F-REQ-040, F-REQ-057.
- **Ambiguity/contradiction notes:** Absence after search can support N1 “not found,” never proof of novelty.

### F-REQ-090 — Non-overridable kernel requirement and vendor-status rejection

- **Source:** §9.1 lines 1234-1240
- **Category:** Formal stop-ship security
- **Requirement:** Set `require_kernel=true` as a non-overridable promotion default and reject `verification_method="aristotle_reported"` as proof evidence while preserving verification/provider metadata.
- **Inputs/outputs:** Inputs: formal evidence record and policy. Outputs: accepted local-kernel method or rejection.
- **Invariants:** No caller/config/script can override the kernel requirement for promotion.
- **Failure behavior:** Vendor-only, missing-method, malformed, or locally unavailable replay is rejected.
- **Integrations:** Evidence schema/loader, Aristotle, Lean, promotion, scripts.
- **Acceptance:** Configuration tampering and alternate entry points cannot make vendor COMPLETE count as formal proof.
- **Dependencies:** F-REQ-013, F-REQ-014.
- **Ambiguity/contradiction notes:** External candidate generation remains permitted behind policy.

### F-REQ-091 — Pinned formal identity and full behavior closure

- **Source:** §9.1 lines 1240-1244
- **Category:** Formal provenance / cache
- **Requirement:** Validate intent/correspondence IDs, provider request/model/build IDs, toolchain/imports/axioms/replay hashes; pin Lean/Lake/Mathlib/client/dependencies, gate standalone scripts, and fingerprint literature/adjudication/Aristotle/Lean/evidence behavior closure.
- **Inputs/outputs:** Inputs: formal run contract and evidence. Outputs: reproducibility classification and compatible cache identity.
- **Invariants:** Mutable unattested hosted model is explicitly non-reproducible.
- **Failure behavior:** Any missing/mismatched closure element blocks replay/promotion and invalidates affected caches.
- **Integrations:** Run contracts, feature policy, cache, external adapter, Lean.
- **Acceptance:** Changing each listed closure component independently invalidates the relevant contract/cache.
- **Dependencies:** F-REQ-015, F-REQ-090.
- **Ambiguity/contradiction notes:** Client version cannot attest server model revision.

### F-REQ-092 — Clean offline formal rebuild and unsafe-source scan

- **Source:** §9.1 lines 1245-1247
- **Category:** Formal hardening
- **Requirement:** Before promotion, build from a clean pinned checkout offline and scan the full relevant source/import closure for placeholders, `sorry`, unsafe axioms/mechanisms, and import violations.
- **Inputs/outputs:** Inputs: immutable target/candidate source tree and policy. Outputs: build, placeholder, axiom/import, replay reports.
- **Invariants:** A successful ordinary `lake build` alone is insufficient.
- **Failure behavior:** Any hole, unauthorized unsafe/axiom/import, network dependency, or rebuild mismatch rejects admission.
- **Integrations:** Lean farm, sandbox, source scanner, certificate.
- **Acceptance:** Adversarial proof files hiding holes in imported/alternate files are detected, not only the selected file.
- **Dependencies:** F-REQ-003, F-REQ-090.
- **Ambiguity/contradiction notes:** Allowed classical axioms are governed by explicit whitelist.

### F-REQ-093 — L0 semantic target package

- **Source:** §9.2 lines 1249-1259
- **Category:** Formalization L0
- **Requirement:** Create 2–3 Lean target candidates from the approved interpretation, define/reuse objects semantically, backtranslate, test examples/anti-examples, attempt equivalence, run paraphrase/mutation checks, and freeze the approved declaration hash.
- **Inputs/outputs:** Inputs: I2 interpretation. Outputs: target candidates, test/equivalence artifacts, locked target hash.
- **Invariants:** Candidate code cannot later redefine the approved target.
- **Failure behavior:** Divergent candidates or failed semantic tests leave F0/F1 and block intended formal promotion.
- **Integrations:** Intake, Lean, correspondence auditor.
- **Acceptance:** Target mutations and anti-examples invalidate approval; exact locked target is used downstream.
- **Dependencies:** F-REQ-022, F-REQ-037, F-REQ-090.
- **Ambiguity/contradiction notes:** Formal equivalence is required when feasible, otherwise correspondence remains appropriately qualified.

### F-REQ-094 — L1 sentinel coverage

- **Source:** §9.2 lines 1261-1271
- **Category:** Formalization L1
- **Requirement:** Formalize type/domain sanity, boundary/degenerate cases, monotonicity/symmetry/invariance assumptions, guiding finite cases, and the central lemma ranked by dependency centrality, semantic risk, and false-branch cost.
- **Inputs/outputs:** Inputs: locked target and graph risk. Outputs: sentinel declarations/results.
- **Invariants:** Hidden regularity/finiteness/choice/decidability/nonzero assumptions become explicit.
- **Failure behavior:** Sentinel failure revises/invalidates the blueprint; it cannot be ignored for final proof.
- **Integrations:** Graph, Lean, controller.
- **Acceptance:** Adversarial edge-case fixtures surface each hidden-assumption class.
- **Dependencies:** F-REQ-009, F-REQ-031, F-REQ-093.
- **Ambiguity/contradiction notes:** The exact central-risk calibration is policy-dependent.

### F-REQ-095 — L2 quarantined formal blueprint

- **Source:** §9.2 lines 1273-1277
- **Category:** Formalization L2
- **Requirement:** Represent holes as graph nodes with source claim, exact goal, expected premises, semantic invariants, and dependencies; allow `sorry` only in a quarantined development branch that production evidence never imports.
- **Inputs/outputs:** Inputs: direct-search failure and target. Outputs: formal declaration blueprint with isolated holes.
- **Invariants:** Direct attempt precedes decomposition; helpers must be smallest justified and not restate/hide target.
- **Failure behavior:** Any production import/release dependency on the quarantined branch rejects certification.
- **Integrations:** Lean project layout, graph, import scanner.
- **Acceptance:** Direct-import and transitive-import attacks from a `sorry` branch are detected and blocked.
- **Dependencies:** F-REQ-045, F-REQ-092, F-REQ-093.
- **Ambiguity/contradiction notes:** Development use of `sorry` is permitted only with a technically enforced trust boundary.

### F-REQ-096 — L3 proof-state portfolio and diagnostic routing

- **Source:** §9.2 lines 1279-1292
- **Category:** Formalization L3
- **Requirement:** Support direct compiler-feedback agents, premise/best-first search, multi-goal trees, generate/repair provers, optional Aristotle, domain tactics, checked ATP export, formal negation, tactic segments, and helper proposals; route diagnostic classes to different repair policies.
- **Inputs/outputs:** Inputs: immutable GoalCapsule and budget. Outputs: action results, proof terms, counterexamples, classified diagnostics.
- **Invariants:** Every external success reconstructs/checks locally and all actions preserve exact goal context.
- **Failure behavior:** Syntax, missing-premise, false-target, library-gap, and decomposition failures are not conflated; bounded attempts end honestly.
- **Integrations:** Lean service, theorem retrieval, external provers, controller.
- **Acceptance:** Production tests exercise each diagnostic route and prove mocked COMPLETE cannot count as closure.
- **Dependencies:** F-REQ-061, F-REQ-069, F-REQ-088.
- **Ambiguity/contradiction notes:** Not every optional prover/backend must be live locally; unavailable levels remain external limitations.

### F-REQ-097 — L5 hardened formal release

- **Source:** §9.2 lines 1304-1311
- **Category:** Formalization L5
- **Requirement:** Eliminate holes/generated axioms/unauthorized unsafe, minimize imports, compute transitive axiom closure against an explicit whitelist, build cleanly offline, require a second checker for untrusted generated Lean, archive source/manifests/toolchain/log/environment/theorem hashes, and link readable proof.
- **Inputs/outputs:** Inputs: assembled candidate and locked target. Outputs: T5 FormalCertificate and archived bundle.
- **Invariants:** The immutable target module and independent checker path are mandatory for untrusted generated Lean publication.
- **Failure behavior:** Any unsafe finding, unexpected axiom/import, missing archive item, or checker mismatch blocks T5/release.
- **Integrations:** Lean farm, independent checker, artifact store, renderer.
- **Acceptance:** Malicious imports, `sorryAx`, generated axioms, unauthorized `unsafe`, and stale build artifacts all fail closed.
- **Dependencies:** F-REQ-092, F-REQ-095, F-REQ-096.
- **Ambiguity/contradiction notes:** A T4 label may exist for encoded theorem without full T5 publication hardening, but untrusted generated Lean publication requires T5.

### F-REQ-098 — Lean service operations are environment-bound

- **Source:** §9.3 lines 1313-1345
- **Category:** Lean API
- **Requirement:** Implement createEnvironment, elaborate, goalState, searchPremises, tryActions, verifyDeclaration, and compareStatements with the specified hashes, budgets, cleanReplay, placeholder, axiom, and independent-checker controls.
- **Inputs/outputs:** Inputs/outputs: exact typed calls and results in §9.3.
- **Invariants:** Every operation is bound to an EnvironmentId derived from pinned versions/project/trust policy.
- **Failure behavior:** Unknown/mismatched environment, file, target, type, or resource budget fails without unsafe fallback.
- **Integrations:** Lean farm, cache, retrieval, verification.
- **Acceptance:** API integration tests use production entry points and cover malformed source, timeout, cancellation, stale IDs, and successful exact proof.
- **Dependencies:** F-REQ-064, F-REQ-091.
- **Ambiguity/contradiction notes:** A simulated backend cannot satisfy local Lean-integration verification.

### F-REQ-099 — FormalCertificate locks target, type, source, trust, and checkers

- **Source:** §9.3 lines 1336-1349
- **Category:** Formal certificate
- **Requirement:** Record expected elaborated type, candidate declaration/proof-term, immutable target module, full source/import tree, transitive axioms/whitelist, placeholder/unsafe results, trust policy, checker and independent checker IDs/logs; compare exact elaborated type, not names.
- **Inputs/outputs:** Inputs: verifyDeclaration request and replay outputs. Outputs: complete FormalCertificate.
- **Invariants:** Candidate code cannot redefine target imports/namespaces/options/macros/declaration.
- **Failure behavior:** Any hash/name-only match, missing field, target redefinition, or checker inconsistency rejects certificate.
- **Integrations:** Lean service, artifact store, evidence validator.
- **Acceptance:** Adversarial same-name/wrong-type and macro/import redefinition proofs are rejected.
- **Dependencies:** F-REQ-093, F-REQ-097, F-REQ-098.
- **Ambiguity/contradiction notes:** Certificate canonical serialization/signature details share release/event integrity policy.

### F-REQ-100 — Formal equivalence requires checked implications

- **Source:** §9.3 lines 1342-1349
- **Category:** Formal correspondence
- **Requirement:** Report `equivalent` only with a checked biconditional or both implication artifacts; model judgment/backtranslation may report only plausibly corresponding.
- **Inputs/outputs:** Inputs: two declarations and requested relation. Outputs: EquivalenceAttempt with proof artifacts/status.
- **Invariants:** Text/model similarity never equals formal equivalence.
- **Failure behavior:** Failed/missing implication returns non-equivalent/unresolved and cannot merge claims/targets.
- **Integrations:** Lean compareStatements, lattice, correspondence certificates.
- **Acceptance:** One-way implication and superficially similar non-equivalent cases do not receive equivalent status.
- **Dependencies:** F-REQ-022, F-REQ-093, F-REQ-098.
- **Ambiguity/contradiction notes:** Semantic intended correspondence still requires I2/F2 even after formal equivalence.

### F-REQ-101 — Explicit axiom and native-mechanism trust policy

- **Source:** §9.3 lines 1351-1352
- **Category:** Formal trust
- **Requirement:** Store/enforce an explicit axiom whitelist and transitive closure, reject `sorryAx` and unapproved user axioms, and forbid kernel-bypassing native mechanisms or treat them as external computation with separate checked certificates.
- **Inputs/outputs:** Inputs: proof term/source, trust policy. Outputs: axiom/unsafe decision and trust assumptions.
- **Invariants:** Policy hash binds certificate/cache/release.
- **Failure behavior:** Unknown/unapproved axioms or unchecked native computation block formal admission.
- **Integrations:** Lean verifier, source scanner, compute certificate path.
- **Acceptance:** Tests cover allowed classical axioms, rejected user axioms, `sorryAx`, and `native_decide` policy behavior.
- **Dependencies:** F-REQ-092, F-REQ-099.
- **Ambiguity/contradiction notes:** The listed classical whitelist is “typical,” so project policy may differ but must be explicit and no weaker silently.

### F-REQ-102 — GoalCapsule exact cache key

- **Source:** §9.3 lines 1353-1360
- **Category:** Formal cache
- **Requirement:** Key goal capsules by Lean version, Mathlib commit, project/import/options hash, elaborated local context, exact target expression, and trust policy.
- **Inputs/outputs:** Inputs: elaborated proof state/environment. Outputs: canonical GoalCapsule key.
- **Invariants:** Pretty-printed textual goals are insufficient.
- **Failure behavior:** Any component change invalidates reuse; ambiguous/noncanonical context prevents cache hit.
- **Integrations:** Lean service, proof-state cache, controller.
- **Acceptance:** Collision tests show shadowed binders/options/imports/trust changes produce distinct keys.
- **Dependencies:** F-REQ-015, F-REQ-069.
- **Ambiguity/contradiction notes:** Canonical elaborated serialization must be pinned/versioned.

### F-REQ-103 — Missing-library result workflow

- **Source:** §9.4 lines 1362-1374
- **Category:** Formal library engineering
- **Requirement:** Verify absence under equivalent names/types, audit the informal result, create a claim-linked sourced local namespace, decompose/prove/test reusable lemmas independently, assign reuse value, and upstream only after human/license review.
- **Inputs/outputs:** Inputs: missing premise and source theorem. Outputs: scoped local library project, proofs, provenance, reuse estimate.
- **Invariants:** The final target cannot serve as the only test of the new library lemma.
- **Failure behavior:** Unverified absence/source/applicability/proof/license blocks import or upstreaming.
- **Integrations:** Theorem retrieval, source audit, Lean, graph, human review.
- **Acceptance:** A hidden existing equivalent is found rather than duplicated, and a new lemma remains independently buildable after restart.
- **Dependencies:** F-REQ-057, F-REQ-088, F-REQ-097.
- **Ambiguity/contradiction notes:** Upstream submission is human-authorized and not required for local completion.

### F-REQ-104 — External prover requests preserve locked context and licensing

- **Source:** §9.6 lines 1405-1415
- **Category:** External integration
- **Requirement:** Send hosted provers only the locked formal target, exact project/toolchain, bounded goal/leaf, and provenance packet after licensing/confidentiality/data-residency checks; request full source and record provider IDs/time/raw I/O/client.
- **Inputs/outputs:** Inputs: policy-approved bounded request. Outputs: full quarantined provider artifact and reproducibility metadata.
- **Invariants:** Unattested server revision is labeled non-reproducible.
- **Failure behavior:** Policy denial, missing full source, malformed response, timeout/cancellation, or auth/config error yields no admissible proof.
- **Integrations:** External gateway, policy, packet store, artifact store.
- **Acceptance:** Sensitive/unauthorized packets are never transmitted and response metadata/schema drift fails closed.
- **Dependencies:** F-REQ-019, F-REQ-091.
- **Ambiguity/contradiction notes:** Live service behavior cannot be claimed if not exercised.

### F-REQ-105 — Untrusted generated Lean executes only in hardened quarantine

- **Source:** §9.6 lines 1415-1417
- **Category:** Sandbox / formal security
- **Requirement:** Build returned Lean only in disposable unprivileged isolation with no network/credentials, read-only source/dependencies, bounded CPU/RAM/time/processes, captured output, then scan/audit/correspondence-check/exact-type-check/independently-check before admission.
- **Inputs/outputs:** Inputs: untrusted source and locked target. Outputs: quarantined logs and validated/rejected certificate.
- **Invariants:** Never execute untrusted generated Lean directly on the host or with secrets.
- **Failure behavior:** Sandbox unavailable means no execution/admission; escape attempt, timeout, crash, symlink/path/import attack triggers cleanup and rejection.
- **Integrations:** Sandbox, Lean farm, credential manager, scanners, evidence validator.
- **Acceptance:** Adversarial filesystem/network/process/env/unsafe-import tests fail within the actual isolation boundary.
- **Dependencies:** F-REQ-010, F-REQ-097, F-REQ-104.
- **Ambiguity/contradiction notes:** If Docker/VM infrastructure is unavailable, true isolation remains BLOCKED-EXTERNAL; local wrappers are not equivalent.

### F-REQ-106 — Problem and Interpretation graph schemas

- **Source:** §10.1 lines 1421-1447
- **Category:** Truth graph schema
- **Requirement:** Persist Problem source/IR/status/interpretation fields and Interpretation normalized semantics, binders, hypotheses, conclusion, relation, resolved/open ambiguity, formal candidates, and intent verdict exactly as separate versioned entities.
- **Inputs/outputs:** Inputs: frozen intake artifacts. Outputs: schema-valid Problem/Interpretation nodes.
- **Invariants:** Active interpretation may remain null; intent begins pending and cannot be forged from child fields.
- **Failure behavior:** Invalid IDs/hashes/relations or contradictory state rejects the event/transaction.
- **Integrations:** Intake, graph store, release.
- **Acceptance:** Serialization/replay preserves every field and malformed or forged approved interpretations fail validation.
- **Dependencies:** F-REQ-036, F-REQ-038.
- **Ambiguity/contradiction notes:** The schema examples are minimal; implementation may add fields without weakening validation.

### F-REQ-107 — Multidimensional Claim schema and scope

- **Source:** §10.1 lines 1449-1490
- **Category:** Truth graph schema
- **Requirement:** Persist canonical/informal claim semantics, quantifiers, assumptions, scope, lifecycle, truth status, each evidence-profile dimension/certificate, relations, sources/formal declarations/branches/attempts, risk/centrality/cost, version, provenance, and supersession separately.
- **Inputs/outputs:** Inputs: claim proposal/events. Outputs: versioned Claim view.
- **Invariants:** Finite/external/formal/informal evidence does not implicitly change other dimensions or scope.
- **Failure behavior:** Forged status without supporting events, invalid version, or scope expansion is rejected.
- **Integrations:** Graph, evidence router, controller, release.
- **Acceptance:** A finite exact result supports only finite scope and restart/replay reconstructs identical multidimensional status.
- **Dependencies:** F-REQ-006, F-REQ-033.
- **Ambiguity/contradiction notes:** `SUPPORTED` thresholds depend on validator-specific obligations, not the schema alone.

### F-REQ-108 — Branch schema includes debt, posteriors, failure, and lease

- **Source:** §10.1 lines 1492-1513
- **Category:** Search/control state
- **Requirement:** Persist goal claims, interpretation, mechanism fingerprint, assumptions, dependency-cone hash, parent/children, lifecycle, value/cost posteriors, spend, verified debt, failure certificates, pause/reopen data, and lease.
- **Inputs/outputs:** Inputs: branch/controller events. Outputs: replayable Branch view.
- **Invariants:** Branch identity is bound to interpretation/dependency cone and state transitions.
- **Failure behavior:** Stale version/fencing/lease or mismatched cone rejects worker updates.
- **Integrations:** Graph, controller, scheduler.
- **Acceptance:** Checkpoint/restart and concurrent race tests preserve state and reject stale writes.
- **Dependencies:** F-REQ-046, F-REQ-071, F-REQ-075.
- **Ambiguity/contradiction notes:** Fencing tokens are implied by safe lease semantics and explicitly demanded by the audit brief, though not named in this schema.

### F-REQ-109 — Evidence schema records generator, verifier, diversity, replay, and trust

- **Source:** §10.1 lines 1515-1539
- **Category:** Evidence schema
- **Requirement:** Persist kind/scope/artifact hashes, generator identity, verifier identities, diversity across lineages/trust bases/environments/humans, environment, replay command/result, intent/correspondence IDs, trust assumptions, and time.
- **Inputs/outputs:** Inputs: artifact and validation events. Outputs: immutable Evidence node.
- **Invariants:** Diversity fields are evidenced separately; second environment is reproducibility, not automatically independent judgment.
- **Failure behavior:** Unknown kind, missing scope/artifact/provenance, forged identity, or failed replay prevents admission.
- **Integrations:** Artifact store, validators, graph, release.
- **Acceptance:** Cross-agent forgery and caller-supplied identity cannot create independent-review or formal status.
- **Dependencies:** F-REQ-015, F-REQ-047.
- **Ambiguity/contradiction notes:** Authentication/signing mechanism must be defined by repository policy.

### F-REQ-110 — Intent and formal-correspondence certificate schemas

- **Source:** §10.1 lines 1541-1567
- **Category:** Semantic certificates
- **Requirement:** Bind IntentCertificate to source/interpretation/informal hashes and required semantic methods/reviewers/conflicts/verdict/version; bind FormalCorrespondenceCertificate to an approved intent certificate, informal hash, declaration, elaborated type, notation map, methods/reviewers/conflicts/verdict/version.
- **Inputs/outputs:** Inputs: audit artifacts and identities. Outputs: APPROVED/REJECTED/UNRESOLVED versioned certificates.
- **Invariants:** Approval is hash-specific and invalidates on any bound semantic artifact change.
- **Failure behavior:** Missing method/conflict/identity, stale hash, or non-approved parent intent blocks F2/I2.
- **Integrations:** Intake, Lean, graph, release.
- **Acceptance:** Forged metadata, stale cached approval, and changed notation/type all invalidate certificates.
- **Dependencies:** F-REQ-022, F-REQ-093, F-REQ-099.
- **Ambiguity/contradiction notes:** Reviewer independence is recorded but exact minimum differs by release profile.

### F-REQ-111 — Semantic graph edges are evidenced mathematical claims

- **Source:** §10.1 lines 1569-1570
- **Category:** Truth graph relations
- **Requirement:** Represent dependency, implication, equivalence, refutation, special/general case, formalization, import, testing, and supersession; semantic relations have IDs, formulas/scopes, evidence profiles, provenance, lifecycle, and revocation.
- **Inputs/outputs:** Inputs: proposed relation and evidence. Outputs: admitted/rejected versioned edge claim.
- **Invariants:** Bare arrows cannot carry truth; edge evidence/status participates in propagation.
- **Failure behavior:** Invalidated/refuted relation downgrades dependent reasoning and cannot remain an active shortcut.
- **Integrations:** Graph, validators, deduplication, blueprint.
- **Acceptance:** Injecting a false equivalence/refutation edge is detected/revoked and dependent paths change accordingly.
- **Dependencies:** F-REQ-006, F-REQ-100.
- **Ambiguity/contradiction notes:** Administrative edges may need different validation, but semantic edges cannot be trusted structurally.

### F-REQ-112 — Kind-specific evidence routing and admission

- **Source:** §10.2 lines 1571-1582
- **Category:** Evidence validation
- **Requirement:** Start claims UNKNOWN/empty; route source imports, computation, informal proofs, Lean proofs, counterexamples, and expert reviews to their exact validators and obligations.
- **Inputs/outputs:** Inputs: proposed evidence. Outputs: typed admission/rejection and evidence-profile recomputation.
- **Invariants:** A general `passed=true` is invalid.
- **Failure behavior:** Unknown/malformed evidence or validator unavailable leaves claim UNKNOWN and logs rejection/pending status.
- **Integrations:** Source auditor, replay/coverage, referees, Lean validator, witness/domain checker, identity auth.
- **Acceptance:** Each kind has positive and negative semantic tests, and swapping labels cannot fool the router.
- **Dependencies:** F-REQ-047, F-REQ-057, F-REQ-063, F-REQ-099.
- **Ambiguity/contradiction notes:** Two-pass informal referee detail is specified by T3 and §11.

### F-REQ-113 — Hard-evidence conflicts quarantine rather than overwrite

- **Source:** §10.2 lines 1582-1585
- **Category:** Truth conflict
- **Requirement:** When strong same-claim evidence conflicts, mark CONFLICTED, quarantine both paths, audit scope/encoding/TCB, and block every dependent promotion.
- **Inputs/outputs:** Inputs: purported proof and counterevidence. Outputs: CONFLICTED events, quarantine and audit tasks.
- **Invariants:** Arrival order or reviewer consensus never resolves hard conflict.
- **Failure behavior:** Any conflict left unresolved remains blocked; it cannot fall back to last-write-wins.
- **Integrations:** Graph, validators, controller, release.
- **Acceptance:** Checked counterexample versus kernel proof produces CONFLICTED and propagates, while model dissent follows separate precedence.
- **Dependencies:** F-REQ-006, F-REQ-111, F-REQ-112.
- **Ambiguity/contradiction notes:** Different scopes/encodings may not truly conflict and require exact audit.

### F-REQ-114 — Evidence invalidation differs from mathematical refutation

- **Source:** §10.2 lines 1586-1619
- **Category:** Revocation semantics
- **Requirement:** Invalid support downgrades without declaring false; only an exact counterexample or checked negation refutes. Propagate both transactionally through SCC condensation in reverse topological order, pausing publication and reopening branches.
- **Inputs/outputs:** Inputs: evidence invalidation or checked refutation. Outputs: recomputed profiles/status and affected closure events.
- **Invariants:** Cycles are handled SCC-aware; transactions are atomic and status is recomputed from surviving evidence.
- **Failure behavior:** Partial propagation/transaction failure rolls back; surviving strong same-scope support yields CONFLICTED, not blind REFUTED.
- **Integrations:** Graph DB/event log, controller, release.
- **Acceptance:** Concurrent, cyclic, transitive, and surviving-support tests independently verify affected closures and statuses.
- **Dependencies:** F-REQ-111, F-REQ-113.
- **Ambiguity/contradiction notes:** M1 requires transactional invalidation in SQLite; M2 requires scalable transactional SCC revocation in PostgreSQL.

### F-REQ-115 — Supersession never rewrites historical claims

- **Source:** §10.2 lines 1618-1619
- **Category:** Event sourcing / lifecycle
- **Requirement:** A corrected/replaced statement creates a superseding claim and preserves the old one; imported corrections, formal changes, and replay failures invalidate evidence rather than rewriting history.
- **Inputs/outputs:** Inputs: correction/replacement. Outputs: new claim, SUPERSEDES edge, invalidation events.
- **Invariants:** Old source/status/evidence remains auditable.
- **Failure behavior:** In-place mutation of authoritative claim state is rejected/detected.
- **Integrations:** Graph, event log, manifest projection.
- **Acceptance:** Replay shows both versions and exact historical dependents, with current view selecting the superseding active claim.
- **Dependencies:** F-REQ-017, F-REQ-111, F-REQ-114.
- **Ambiguity/contradiction notes:** Materialized views may update in place only as disposable projections.

### F-REQ-116 — Signed append-only event schema is authoritative

- **Source:** §10.3 lines 1621-1652
- **Category:** Event log / security
- **Requirement:** Record every state change with unique ID/sequence/run/time, actor identity/version/prompt, action/objects, optimistic prior/new versions, input/output/run-contract hashes, budget, reason, human reason, and signature; event log/artifacts are authoritative.
- **Inputs/outputs:** Inputs: validated state transition. Outputs: canonical signed append event and derived views.
- **Invariants:** Global sequence/order, optimistic versions, and canonical serialization detect insertion, deletion, truncation, duplication, reordering, mutation, and forgery across restarts/concurrency.
- **Failure behavior:** Signature/chain/version/canonicalization failure blocks replay/resume/release; no permissive repair.
- **Integrations:** Event store, key management, manifest/dashboard projections.
- **Acceptance:** Adversarial tests corrupt, omit, reorder, duplicate, forge, truncate, and concurrently append events; all invalid histories are detected.
- **Dependencies:** F-REQ-017, F-REQ-114.
- **Ambiguity/contradiction notes:** The example says `signature` but not a specific HMAC/hash-chain/Merkle scheme; implementation must provide cryptographic integrity and secure key handling consistent with checkpoint Merkle roots.

### F-REQ-117 — Checkpoint captures complete durable execution identity

- **Source:** §10.4 lines 1654-1667
- **Category:** Checkpoint / persistence
- **Requirement:** Checkpoint last sequence/Merkle root, source/interpretation hashes, schema/versioned graph view, archive/blueprint, controller posteriors/budgets/seeds, leases, all model/prompt/tool/environment/dependency/service identities, per-stage runner/adjudicator/retrieval policy, caches/replay policies, and rate/quota state.
- **Inputs/outputs:** Inputs: committed runtime state. Outputs: immutable/hash-verified checkpoint.
- **Invariants:** Checkpoint corresponds exactly to a committed event sequence.
- **Failure behavior:** Missing/mismatched fields invalidate only safe compatible caches or the entire checkpoint as required; never synthesize provenance.
- **Integrations:** Event log, graph, controller, scheduler, gateways.
- **Acceptance:** Restart from checkpoint reproduces materialized state and decisions under the same seed/contract.
- **Dependencies:** F-REQ-015, F-REQ-108, F-REQ-116.
- **Ambiguity/contradiction notes:** Snapshot is optional optimization; event replay remains authoritative.

### F-REQ-118 — Resume verifies integrity, compatibility, leases, and high-trust artifacts

- **Source:** §10.4 lines 1669-1680
- **Category:** Restart / recovery
- **Requirement:** Verify chain/snapshot, compare full behavior closure, invalidate only incompatible caches, atomically transfer expired leases, replay high-trust artifacts after environment change, mark interruptions censored, and resume highest compatible stage.
- **Inputs/outputs:** Inputs: checkpoint, events, current contract/clock. Outputs: reconstructed state, cache/lease decisions, resumed work.
- **Invariants:** Only compatible immutable artifacts are reused and interrupted calls do not spend math retries.
- **Failure behavior:** Integrity failure blocks resume; expired/stale workers cannot write after reassignment.
- **Integrations:** Event store, caches, scheduler, artifact replay.
- **Acceptance:** Crash/restart, environment drift, stale-worker race, and partial-call tests produce exactly the required recovery behavior.
- **Dependencies:** F-REQ-079, F-REQ-116, F-REQ-117.
- **Ambiguity/contradiction notes:** A grace period is required but its duration is policy-defined and checkpointed.

### F-REQ-119 — Worker heartbeat identity and stale-worker rejection

- **Source:** §10.4 line 1680; §14.3 lines 2151-2152
- **Category:** Leases / concurrency
- **Requirement:** Renew leases with host/PID, branch, stage, exact run contract and heartbeat; bind problem/interpretation/branch/budget, atomically reassign after expiry, and use fencing so stale owners cannot commit.
- **Inputs/outputs:** Inputs: acquire/renew/write/reassign requests with clock/fencing token. Outputs: lease state or stale denial.
- **Invariants:** At most one current fenced owner may perform a non-idempotent action.
- **Failure behavior:** Expired/stale/foreign renewal or write is rejected; duplicate delivery is idempotently deduplicated.
- **Integrations:** Scheduler, graph/event transactions, external action adapters.
- **Acceptance:** Deterministic concurrency races prove expiration, renewal, reassignment, stale rejection, crash recovery, and no duplicate non-idempotent effect.
- **Dependencies:** F-REQ-046, F-REQ-108, F-REQ-118.
- **Ambiguity/contradiction notes:** The spec implies fencing via safe ownership transfer; the audit brief makes explicit fencing-token testing mandatory.

### F-REQ-120 — Complete provenance by artifact and review type

- **Source:** §10.5 lines 1682-1689
- **Category:** Provenance
- **Requirement:** Record exact immutable source theorem/hypothesis/extraction data; generated code/prompt/model/tool/inputs/seed/environment; formal theorem/source/import/toolchain/axiom/replay; novelty query coverage/gaps; and human scope/conflicts.
- **Inputs/outputs:** Inputs: every imported/generated/formal/novelty/human artifact. Outputs: content-addressed provenance records.
- **Invariants:** Hidden model reasoning is not provenance.
- **Failure behavior:** Missing mandatory provenance prevents affected evidence from promotion/reuse.
- **Integrations:** Artifact/source stores, graph, evaluator, release.
- **Acceptance:** Traceability can reconstruct every admitted claim from immutable inputs and explicit events without relying on transient chats.
- **Dependencies:** F-REQ-036, F-REQ-109, F-REQ-116.
- **Ambiguity/contradiction notes:** Privacy/licensing may restrict publication but not internal evidence qualification.

### F-REQ-121 — Memory promotion matrix

- **Source:** §10.6 lines 1691-1701
- **Category:** Memory policy
- **Requirement:** Enforce the per-memory false-claim, cross-problem-use, and promotion rules for scratch, local episodic, mechanically verified semantic, audited imports, procedural, negative, and calibration data.
- **Inputs/outputs:** Inputs: candidate memory record and requested use. Outputs: allowed/quarantined/denied decision.
- **Invariants:** False/speculative data never becomes cross-problem semantic truth; imports are rechecked at every use.
- **Failure behavior:** Policy/version/applicability failure denies use and can revoke downstream support.
- **Integrations:** Memory stores, graph, controller, learning.
- **Acceptance:** Direct and restart tests show each matrix row allows only its specified reuse/promotion behavior.
- **Dependencies:** F-REQ-065.
- **Ambiguity/contradiction notes:** Negative memory scope must remain explicit to avoid overgeneralizing a failed mechanism.

### F-REQ-122 — Referee organizational independence and reward

- **Source:** §11.1 lines 1703-1716
- **Category:** Adversarial authority
- **Requirement:** Use fresh non-shared contexts, different model/tool paths for high-value claims, defect/calibrated-abstention reward, replay/source/formal attack access, no same-pass repair, and reporting to release rather than governor; record diversity dimensions separately.
- **Inputs/outputs:** Inputs: locked artifacts without generator scratchpad. Outputs: defect/abstention/obligation report and independence profile.
- **Invariants:** Fresh conversation IDs or provider diversity alone are insufficient.
- **Failure behavior:** Shared context, self-review, missing conflict metadata, or same-pass repair invalidates claimed independence.
- **Integrations:** Dispatcher, referee tools, release auditor, telemetry.
- **Acceptance:** Authority tests prevent generator/governor from controlling referee verdicts or reading/forging independence state.
- **Dependencies:** F-REQ-011, F-REQ-060.
- **Ambiguity/contradiction notes:** Different families may share training data, so independence remains qualified.

### F-REQ-123 — Target and quantifier/domain attacks

- **Source:** §11.2 lines 1718-1722
- **Category:** Adversarial verification
- **Requirement:** Diff original bytes, IR, active interpretation, informal theorem, and Lean declaration; audit quantifier order, domains, degenerate cases, constants/regimes, regularity, finiteness, and choice.
- **Inputs/outputs:** Inputs: all target representations. Outputs: normalized semantic defects or discharged checks.
- **Invariants:** Any representation mismatch remains tainted until resolved.
- **Failure behavior:** A valid target/domain defect blocks intent/correspondence/release and invalidates dependents.
- **Integrations:** Intake, graph, Lean, referee.
- **Acceptance:** Mutation fixtures for every listed semantic error are detected through production verification.
- **Dependencies:** F-REQ-022, F-REQ-110, F-REQ-122.
- **Ambiguity/contradiction notes:** Not all domain properties apply, but N/A requires a reason.

### F-REQ-124 — Dependency, circularity, and import attacks

- **Source:** §11.2 lines 1722-1725
- **Category:** Adversarial verification
- **Requirement:** Independently rebuild the proof DAG, require every nontrivial step to link to admitted evidence, detect conclusion/equivalent/import circularity, and open every cited theorem to compare exact hypotheses/version/regime/notation.
- **Inputs/outputs:** Inputs: candidate, graph, sources. Outputs: reconstructed DAG and first invalid dependency/import.
- **Invariants:** Imported theorems depending on the target count as circular.
- **Failure behavior:** Missing/invalid/circular dependency taints and blocks all affected conclusions.
- **Integrations:** Graph, source auditor, proof compiler, referee.
- **Acceptance:** Adversarial circular and silently strengthened import fixtures fail even if all model reviewers approve.
- **Dependencies:** F-REQ-057, F-REQ-111, F-REQ-122.
- **Ambiguity/contradiction notes:** Opaque literature dependencies may leave truth unresolved rather than falsely passed.

### F-REQ-125 — Countermodel and independent computation attacks

- **Source:** §11.2 lines 1725-1727
- **Category:** Adversarial verification
- **Requirement:** Search smallest/boundary/random/adversarial/alternate/formal-negation cases and independently replay or reimplement computation in a separate environment while comparing hashes and coverage.
- **Inputs/outputs:** Inputs: target/key lemmas and artifacts. Outputs: counterexamples, replay/reimplementation reports.
- **Invariants:** Candidate proof details are initially withheld from the falsifier as specified by authority boundaries.
- **Failure behavior:** Exact counterexample refutes/conflicts; replay mismatch invalidates evidence and dependents.
- **Integrations:** Falsifier, computation, Lean, graph.
- **Acceptance:** Known false claims and deliberately nondeterministic/tampered artifacts are caught.
- **Dependencies:** F-REQ-062, F-REQ-063, F-REQ-122.
- **Ambiguity/contradiction notes:** Independent environment alone establishes reproducibility, not independent mathematical judgment.

### F-REQ-126 — Formal audit and independent proof reconstruction

- **Source:** §11.2 lines 1727-1729
- **Category:** Adversarial verification
- **Requirement:** Perform clean build, hole/axiom/unsafe/import/type/correspondence checks and have a referee reconstruct a concise skeleton without copying rhetoric.
- **Inputs/outputs:** Inputs: proof bundle and graph. Outputs: formal audit and independent skeleton/first-error report.
- **Invariants:** A clean encoded proof does not discharge intended correspondence automatically.
- **Failure behavior:** Any formal or reconstruction gap blocks the relevant truth level.
- **Integrations:** Lean hardening, referee, graph.
- **Acceptance:** Malicious proof sources and persuasive prose with a hidden logical gap fail independent reconstruction.
- **Dependencies:** F-REQ-097, F-REQ-122, F-REQ-124.
- **Ambiguity/contradiction notes:** Formal audit may be N/A for informal-only claims, but T3 reconstruction remains mandatory.

### F-REQ-127 — Independent novelty and significance firewall

- **Source:** §11.2 lines 1729-1731
- **Category:** Adversarial verification / release
- **Requirement:** Use a separate auditor to search prior art and determine actual non-vacuous responsiveness; propagate circular, unreviewed-import, numerical-only, and semantic-risk taint until discharged.
- **Inputs/outputs:** Inputs: result, status packet/query log, graph taints. Outputs: novelty/significance verdicts and taint closure.
- **Invariants:** Novelty auditor has no incentive to support proof and proof correctness cannot clear novelty/significance.
- **Failure behavior:** Known result becomes rediscovery; insufficient search/expert review remains N0/S0; taint blocks dependents.
- **Integrations:** Retrieval, graph, release auditor, experts.
- **Acceptance:** Known historical solutions, vacuous true claims, and tainted imports cannot receive novel/full labels.
- **Dependencies:** F-REQ-033, F-REQ-040, F-REQ-124.
- **Ambiguity/contradiction notes:** Absence of prior art is never mathematically proven; N2 requires expert audit.

### F-REQ-128 — Taint-aware dependency propagation

- **Source:** §11.2 line 1731
- **Category:** Truth graph / verification
- **Requirement:** Propagate circular, unreviewed-import, numerical-only, and semantic-risk labels to every dependent conclusion until each obligation is discharged.
- **Inputs/outputs:** Inputs: evidence/edge taints and dependency graph. Outputs: derived taint state and blocked promotions.
- **Invariants:** Taint removal requires corresponding evidence events, not metadata edits.
- **Failure behavior:** Stale cached approvals are invalidated on new/revoked taint.
- **Integrations:** Graph propagation, release, cache.
- **Acceptance:** Transitive/SCC fixtures independently verify taint addition/removal and gate effects.
- **Dependencies:** F-REQ-114, F-REQ-127.
- **Ambiguity/contradiction notes:** Taint is distinct from truth REFUTED and may coexist with otherwise strong support.

### F-REQ-129 — Truth hierarchy T0 through T5

- **Source:** §11.3 lines 1733-1745
- **Category:** Verification standards
- **Requirement:** Enforce exact labels and obligations: T0 speculation; T1 reproducible scoped numerics/counterexample search; T2 exact finite/conditional witness/coverage/certificate; T3 full dependency/source audit plus two independent hostile reconstructions for high-value claims; T4 clean pinned kernel/exact type/axiom/import/no-hole encoded theorem; T5 T4 plus immutable target and independent trust path.
- **Inputs/outputs:** Inputs: evidence profile and obligations. Outputs: highest justified truth level.
- **Invariants:** Higher levels include all stated lower/relevant hard obligations and never derive from status labels alone.
- **Failure behavior:** Any missing obligation yields lower/unknown status; forged level is rejected.
- **Integrations:** Evidence router, graph, referee, Lean, release.
- **Acceptance:** Positive and one-failure-per-obligation cases prove each transition and prevent vendor/model shortcuts.
- **Dependencies:** F-REQ-112, F-REQ-122 through F-REQ-126.
- **Ambiguity/contradiction notes:** T3’s two hostile reconstructions are explicitly for high-value claims; policy must define and record high-value classification.

### F-REQ-130 — I/F/N/S/R and autonomy profile

- **Source:** §11.3 lines 1746-1755
- **Category:** Release dimensions
- **Requirement:** Represent I0-I2 intent, F0-F2 formal correspondence/N-A, N0-N2/known novelty, S0-S2 significance, R0-R2 replay, and phase-by-phase autonomy interventions/counts.
- **Inputs/outputs:** Inputs: dimension evidence and intervention log. Outputs: orthogonal profile.
- **Invariants:** No scalar autonomy/confidence and no cross-dimension substitution.
- **Failure behavior:** Missing evidence yields level 0/unresolved, not optimistic default.
- **Integrations:** Graph, certificates, telemetry, renderer.
- **Acceptance:** Profile transition tests exercise every state and reject forged/cached stale levels.
- **Dependencies:** F-REQ-033, F-REQ-110.
- **Ambiguity/contradiction notes:** Human/expert roles are necessary for some I/N/S decisions, so full autonomy is not assumed.

### F-REQ-131 — Exact release-label thresholds

- **Source:** §11.3 lines 1757-1758
- **Category:** Release policy
- **Requirement:** Allow Lean-verified at T4 only for exact encoding; require T5 for untrusted-generated publication; intended informal proof needs T3+I2; intended formal proof needs T5+I2+F2; both need current status; novel autonomous resolution additionally needs N2+S2+R2 and autonomy metadata.
- **Inputs/outputs:** Inputs: full profile/status. Outputs: permitted labels or blocked reasons.
- **Invariants:** All conjunctive thresholds are fail-closed and reported separately.
- **Failure behavior:** Any missing/stale/failed conjunct prevents that label while permitting accurate narrower labels.
- **Integrations:** Release auditor, renderer, status service.
- **Acceptance:** Truth-table tests independently fail each conjunct and every release entry point blocks bypass.
- **Dependencies:** F-REQ-002, F-REQ-129, F-REQ-130.
- **Ambiguity/contradiction notes:** A rigorous informal partial label can be valid without F2, but still needs its specified truth/intent/significance scope.

### F-REQ-132 — Pessimistic disagreement adjudication

- **Source:** §11.4 lines 1759-1769
- **Category:** Adjudication
- **Requirement:** A single valid central defect blocks promotion; normalize conflicts, gather targeted evidence, use a new blinded adjudicator, prefer formal/executable resolution, and return unknown if unresolved; never average reviewer scores.
- **Inputs/outputs:** Inputs: conflicting reviews/evidence. Outputs: normalized issue, new evidence/adjudication event, resolved or unknown status.
- **Invariants:** Correlated consensus raises search priority only, never truth.
- **Failure behavior:** Partial failure, gate disagreement, stale/cached approval, or remaining conflict blocks promotion.
- **Integrations:** Referee, adjudicator, graph, release.
- **Acceptance:** Tests cover false positive/negative reviewers, identity blinding, central dissent, kernel-vs-model precedence, and unresolved unknown.
- **Dependencies:** F-REQ-113, F-REQ-122, F-REQ-129.
- **Ambiguity/contradiction notes:** Model dissent cannot overrule exact kernel truth but may block intent/applicability/novelty/significance.

### F-REQ-133 — Complete signed ReleaseCertificate

- **Source:** §11.5 lines 1771-1821
- **Category:** Release artifact / security
- **Requirement:** Produce the full source/interpretation/result/formal/proof hashes; truth levels/certificates/trust/axioms/checkers; intent/formal/novelty/significance/replay; autonomy interventions/trace; unresolved risks; canonical signature algorithm/signer/key fingerprint/value/time.
- **Inputs/outputs:** Inputs: all final gate evidence/events. Outputs: canonically serialized signed ReleaseCertificate.
- **Invariants:** Certificate is bound to immutable artifacts/policies and cannot omit unresolved risks.
- **Failure behavior:** Missing/unknown/malformed field, bad signature, stale hash/key, or gate mismatch rejects release.
- **Integrations:** Release auditor, key management, artifact store, renderer.
- **Acceptance:** Mutation/insertion/deletion/reordering/forgery tests invalidate certificate; deterministic serialization/signature verification survives restart.
- **Dependencies:** F-REQ-116, F-REQ-129, F-REQ-130, F-REQ-131.
- **Ambiguity/contradiction notes:** Signing algorithm/key lifecycle is policy-defined but must be secure and auditable.

### F-REQ-134 — Communication never compresses evidence profile

- **Source:** §11.5 lines 1822-1823
- **Category:** Communication gate
- **Requirement:** Render every release dimension, caveat, and unresolved risk separately; never replace it with self-reported confidence such as 95%.
- **Inputs/outputs:** Inputs: validated ReleaseCertificate. Outputs: evidence-accurate human/machine presentation.
- **Invariants:** Renderer consumes signed current certificate, not caller metadata or cached approval.
- **Failure behavior:** Malformed/stale/unsigned certificate or any failed mandatory gate prevents output release.
- **Integrations:** Communication plane, release service, all CLI/API/report entry points.
- **Acceptance:** Alternate/direct rendering, forged metadata, disabled gates, stale cache, and partial gate failures all fail closed.
- **Dependencies:** F-REQ-051, F-REQ-133.
- **Ambiguity/contradiction notes:** Progress reports may discuss uncertainty but cannot masquerade as release.

### F-REQ-135 — Seven-level evaluation and separate formalization tracks

- **Source:** §12.1 lines 1825-1841
- **Category:** Evaluation design
- **Requirement:** Evaluate Levels 1–7 with their specified sets/capabilities/ground truth; for Levels 2–3 report supplied-audited-statement proof search, independently graded autoformalization, and raw-source end-to-end tracks separately.
- **Inputs/outputs:** Inputs: versioned level/task/track snapshots. Outputs: track-specific results and artifacts.
- **Invariants:** Training corpora, unsolved research deployment, and supplied formal targets are not conflated with unique semantic ground truth.
- **Failure behavior:** Missing semantic/toolchain/version audit prevents aggregation.
- **Integrations:** Evaluation harness, corpus, Lean, expert review.
- **Acceptance:** Evaluation inventory covers every level/track and reports N/A/external limitations honestly.
- **Dependencies:** F-REQ-021, F-REQ-025.
- **Ambiguity/contradiction notes:** Level 7 has no answer key and cannot be scored by accuracy.

### F-REQ-136 — Frozen equal-footing evaluation protocol

- **Source:** §12.2 lines 1843-1858
- **Category:** Evaluation protocol
- **Requirement:** Freeze bytes/status/toolchain/library/models/prompts/tools/budgets/network/rubric; deduplicate audibly; run strongest raw, open/local raw, current pipeline, and EGMRA; equalize cost/Pareto; retain all outcomes/interventions; clean-replay/blind-grade; separate novelty graders; analyze calibration/false success.
- **Inputs/outputs:** Inputs: frozen run matrix. Outputs: failure-complete artifacts and comparisons.
- **Invariants:** Discarded branches, timeouts, and rate limits remain in denominators.
- **Failure behavior:** Missing baselines/provenance/complete logs prevents performance claims.
- **Integrations:** Run contracts, telemetry, evaluators, replay.
- **Acceptance:** A benchmark smoke run demonstrates all four baselines or explicitly records unavailable ones without comparison claims.
- **Dependencies:** F-REQ-021, F-REQ-120, F-REQ-135.
- **Ambiguity/contradiction notes:** A repository can implement the harness without credentials/models to execute all live baselines; such runs remain external limitations.

### F-REQ-137 — Causal ablation versus best-available comparison

- **Source:** §12.2 lines 1860-1861
- **Category:** Evaluation causal validity
- **Requirement:** For architectural ablations hold model/prompt/tool/retrieval/network/budget/seeds/evaluator fixed and change one component; separately label stronger-model/tool/budget best-available comparisons as deployment capability.
- **Inputs/outputs:** Inputs: paired run contracts. Outputs: causal ablation and deployment comparison reports.
- **Invariants:** No mixed comparison is described as orchestration gain.
- **Failure behavior:** Contract mismatch invalidates causal attribution.
- **Integrations:** Evaluation runner, cache/run identity, telemetry.
- **Acceptance:** Automated contract diff rejects multi-factor ablation pairs.
- **Dependencies:** F-REQ-015, F-REQ-136.
- **Ambiguity/contradiction notes:** Seeds are fixed where available; nondeterminism must still be recorded.

### F-REQ-138 — Historical Erdős time-capsule evaluation

- **Source:** §12.2 lines 1862-1868
- **Category:** Evaluation / contamination
- **Requirement:** Choose problems open at cutoff t but solved later, hide all post-t sources/solution, audit training contamination separately, score rediscovery/alternate proof/lemmas/status errors, and compare later literature for leakage.
- **Inputs/outputs:** Inputs: dated corpus/source snapshots and held-out solutions. Outputs: contamination-aware Level 6 results.
- **Invariants:** Post-cutoff retrieval is prohibited in the solver packet.
- **Failure behavior:** Leakage or unavailable audit invalidates affected novelty/rediscovery metric.
- **Integrations:** Corpus store, retrieval firewall, evaluation.
- **Acceptance:** Injected post-cutoff source cannot enter a time-capsule run and is reported if detected.
- **Dependencies:** F-REQ-040, F-REQ-080, F-REQ-135.
- **Ambiguity/contradiction notes:** Opaque model training contamination cannot be eliminated, only audited/labeled.

### F-REQ-139 — Level 7 reports contributions, never accuracy

- **Source:** §12.2 lines 1870-1871
- **Category:** Evaluation / communication
- **Requirement:** For currently unsolved problems record only externally verified contributions, subgoal movement, counterexamples, reductions, libraries, and supported no-results; never count the system’s own solve declaration or report accuracy.
- **Inputs/outputs:** Inputs: deployment artifacts and external reviews. Outputs: evidence-qualified contribution ledger.
- **Invariants:** No solve-rate claim on the small unsolved deployment set.
- **Failure behavior:** Unverified self-declaration has zero outcome credit.
- **Integrations:** Evaluation, release, expert review.
- **Acceptance:** A self-labeled solved output without external/formal evidence scores zero and is surfaced as false-success risk.
- **Dependencies:** F-REQ-026, F-REQ-135.
- **Ambiguity/contradiction notes:** Later literature may retroactively inform outcomes but remains versioned.

### F-REQ-140 — Final-outcome and false-success metrics

- **Source:** §12.3 lines 1872-1879
- **Category:** Evaluation metrics
- **Requirement:** Measure qualifying full proofs/disproofs, false/ambiguous/misquoted/already-solved detection, correct abstention/no-result for Levels 1–6, and prominently report incorrect solved declarations.
- **Inputs/outputs:** Inputs: release profiles and ground truth/reviews. Outputs: exact outcome denominators and false-success counts.
- **Invariants:** Incorrect solved claims are never averaged away.
- **Failure behavior:** Missing required gate evidence prevents counting a success.
- **Integrations:** Evaluation, release, expert/formal grading.
- **Acceptance:** Metric tests independently recalculate counts from raw outcome records.
- **Dependencies:** F-REQ-129, F-REQ-131, F-REQ-136.
- **Ambiguity/contradiction notes:** Level 7 uses current belief/evidence, not correct-abstention labels.

### F-REQ-141 — Intermediate verified-progress metrics

- **Source:** §12.3 lines 1881-1888
- **Category:** Evaluation metrics
- **Requirement:** Measure central newly verified lemmas, counterexamples/killed conjectures, verified proof-debt reduction, reusable formal/compute infrastructure, confirmed status corrections, subgoal closure, and paths unlocked.
- **Inputs/outputs:** Inputs: frozen graph/blueprint and authenticated events. Outputs: intermediate progress metrics.
- **Invariants:** Only durable validated objects count; node/agent/token volume alone does not.
- **Failure behavior:** Unverified or disconnected outputs receive no progress credit.
- **Integrations:** Graph, controller, evaluation.
- **Acceptance:** Independent event recomputation matches metrics and resists duplicate/easy-node inflation.
- **Dependencies:** F-REQ-070, F-REQ-077.
- **Ambiguity/contradiction notes:** Utility of a verified lemma requires downstream unlock, not mere existence.

### F-REQ-142 — Risk-weighted formal coverage is frozen against gaming

- **Source:** §12.3 lines 1890-1911
- **Category:** Evaluation / rigor
- **Requirement:** Compute RFC from independently audited frozen proof blueprint and weights centrality×semanticRisk×downstreamLoss; also measure evidence dimensions, edge correctness, citation applicability, revocation precision/recall, correspondence, and independent replay.
- **Inputs/outputs:** Inputs: frozen blueprint/weights and audit results. Outputs: RFC and rigor-integrity metric set.
- **Invariants:** Blueprint/weights freeze before scoring; hard target cannot be replaced by easy nodes/helpers.
- **Failure behavior:** Post-hoc graph/weight changes invalidate the metric.
- **Integrations:** Graph, formal/replay, source auditor, evaluation.
- **Acceptance:** Mutation tests prove helper inflation/weight changes do not improve valid RFC and injected false lemmas exercise revocation metrics.
- **Dependencies:** F-REQ-070, F-REQ-114, F-REQ-128.
- **Ambiguity/contradiction notes:** “Adequately verified” depends on claim risk/profile and must be preregistered.

### F-REQ-143 — Search, efficiency, and calibration metrics

- **Source:** §12.3 lines 1913-1942
- **Category:** Evaluation metrics
- **Requirement:** Measure mechanism/behavior diversity, semantic duplicates/repeated errors/counterexamples/useful budget/reopen/backlog; full cost/time/cache/orchestration/Pareto; Brier/log/ECE/reliability/interval/censoring/abstention/false-promotion.
- **Inputs/outputs:** Inputs: authenticated traces/outcomes/costs. Outputs: exact metric suite with intervals.
- **Invariants:** Agent count and raw tokens have no intrinsic progress value; censoring is modeled.
- **Failure behavior:** Missing telemetry or incomparable pipeline fingerprints prevents affected metrics/claims.
- **Integrations:** Telemetry, archive, controller, calibration, evaluation.
- **Acceptance:** Independent small datasets reproduce every metric and version drift separates cohorts.
- **Dependencies:** F-REQ-020, F-REQ-053, F-REQ-071, F-REQ-078.
- **Ambiguity/contradiction notes:** Exact estimator choices may vary but definitions/denominators must be published.

### F-REQ-144 — Durable-object threshold for research progress

- **Source:** §12.4 lines 1944-1956
- **Category:** Evaluation / communication
- **Requirement:** Count progress only for an admitted claim with new evidence, exact counterexample, verified reduction/equivalence, preregistered-threshold experiment/branch kill, audited status correction, reusable formal/compute component, or failure certificate preventing a defined repeat.
- **Inputs/outputs:** Inputs: output artifacts/events. Outputs: count/no-count classification.
- **Invariants:** Tokens, agents, candidate lemmas, self-rated completion, consensus, and polish have zero direct value.
- **Failure behavior:** Verbose output with only unverified nodes scores below an exact counterexample and cannot support progress claims.
- **Integrations:** Graph, evaluator, renderer.
- **Acceptance:** Constant/prose-only systems score zero on independent fixtures even if current tests pass.
- **Dependencies:** F-REQ-026, F-REQ-141.
- **Ambiguity/contradiction notes:** Experiment thresholds must be preregistered.

### F-REQ-145 — Required architecture ablations

- **Source:** §12.5 lines 1958-1976
- **Category:** Evaluation / experiments
- **Requirement:** Run/preregister the 13 listed ablation families covering retrieval, OEIS, memory/revocation, scouts/archive, revisions/controller, formalization timing, referee diversity, computation, exploration fractions, utility formula, expert iteration, model routing, and raw baseline.
- **Inputs/outputs:** Inputs: frozen paired configurations. Outputs: staged/factorial ablation results with primary metrics/stop conditions.
- **Invariants:** Only the named component changes in causal comparisons.
- **Failure behavior:** Absent ablations mean the corresponding architectural advantage remains unverified, not positive by design.
- **Integrations:** Evaluation harness and every subsystem toggle.
- **Acceptance:** Configuration inventory and smoke tests can execute every contrast without unsafe production bypass.
- **Dependencies:** F-REQ-137.
- **Ambiguity/contradiction notes:** Full statistically powered live execution may be externally/cost blocked; harness support alone is not empirical validation.

### F-REQ-146 — Statistical reporting policy

- **Source:** §12.6 lines 1978-1987
- **Category:** Evaluation statistics
- **Requirement:** Report denominators/intervals/budgets/censored runs, pair problems/seeds, avoid unmatched pass@k/budgets, separate development/sealed packets, version/rerun benchmarks after corrections, publish failure-complete logs subject to policy, use two blind referees for high-value informal claims, and treat recent preprints as hypotheses.
- **Inputs/outputs:** Inputs: raw evaluation records and policies. Outputs: compliant statistical report.
- **Invariants:** No cherry-picking or hidden failures.
- **Failure behavior:** Insufficient/mismatched evidence prevents aggregate claims and is disclosed.
- **Integrations:** Evaluation, source packets, reviewers, publication.
- **Acceptance:** Automated report checks reject missing denominators, unmatched comparisons, leakage, and one-referee high-value T3 claims.
- **Dependencies:** F-REQ-120, F-REQ-129, F-REQ-136.
- **Ambiguity/contradiction notes:** Privacy/licensing may redact content but counts/failure semantics must remain honest.

### F-REQ-147 — Experimental innovations remain hypotheses until ablated

- **Source:** §§15-16 lines 2240-2250, 2296-2302
- **Category:** Scientific claim governance
- **Requirement:** Treat interpretation lattice cost, cold-pass value, posterior controller, sentinel ranking, verified-DAG credit, reuse reward, and provider diversity as explicit experimental hypotheses; validate via false-success, calibration, verified progress/cost, and blind expert/formal evaluation.
- **Inputs/outputs:** Inputs: preregistered ablations and runtime evidence. Outputs: supported/unsupported/unknown design claims.
- **Invariants:** Implementation/test presence is not performance validation.
- **Failure behavior:** No adequate evaluation means no superiority or completion-performance claim.
- **Integrations:** Evaluation, audit report, communication.
- **Acceptance:** Final reports distinguish local software verification from empirical architecture effectiveness.
- **Dependencies:** F-REQ-021, F-REQ-145, F-REQ-146.
- **Ambiguity/contradiction notes:** The final architecture statement is an original integration claim, not a measured result.

### F-REQ-148 — Distinct M0, M1, M2 milestones and conservative reuse

- **Source:** §13 lines 1989-2004
- **Category:** Implementation milestones
- **Requirement:** Treat M0 safety/provenance, M1 smallest scientific vertical slice, and M2 scalable controlled-run MVP as distinct gates; reuse only the listed source/ranking/cache/event/queue/outcome/rate-limit/rejection/regulator foundations with their required extensions.
- **Inputs/outputs:** Inputs: legacy repository and milestone policy. Outputs: staged implementation/evidence with preserved compatible invariants.
- **Invariants:** Safety does not depend on unbuilt M1/M2 infrastructure and legacy generic evidence acceptance is not preserved.
- **Failure behavior:** A later milestone cannot be called complete if its predecessor safety/baseline gate failed.
- **Integrations:** Legacy pipeline and all new services.
- **Acceptance:** Milestone-specific test/report evidence distinguishes implementation and external limitations rather than one blanket MVP claim.
- **Dependencies:** F-REQ-016.
- **Ambiguity/contradiction notes:** P0/P1/P2 overlap but are not fully cross-mapped; this inventory treats explicit immediate/M0 safety as blocking all release.

### F-REQ-149 — M0 signed feature policy at every entry point

- **Source:** §13.2 line 2010
- **Category:** M0 security
- **Requirement:** Enforce one signed feature policy at scheduler, verifier, evidence loader, cache replay, gate, promotion, and standalone script entry points.
- **Inputs/outputs:** Inputs: signed policy and requested action. Outputs: consistent allow/deny event.
- **Invariants:** No alternate or direct invocation bypasses policy; policy hash binds caches/evidence.
- **Failure behavior:** Disabled, missing, invalid, stale, or mismatched policy fails closed.
- **Integrations:** All named production entry points.
- **Acceptance:** Direct-script, low-level method, scheduler, forged-policy, and disabled-feature tests all deny identically.
- **Dependencies:** F-REQ-014, F-REQ-116.
- **Ambiguity/contradiction notes:** Signer/key details are unspecified but unsigned policy cannot be treated as signed.

### F-REQ-150 — M0 closed validators and unreachable generic success

- **Source:** §13.2 lines 2011, 2019
- **Category:** M0 evidence security
- **Requirement:** Disable promotion until formal, computational, expert, and source-import evidence have closed kind-specific schemas/validators, stop-ship regressions pass, and the old generic `passed=true` path is unreachable from every production entry.
- **Inputs/outputs:** Inputs: typed evidence and validator registry. Outputs: validator-specific decision or hard rejection.
- **Invariants:** No unknown/custom evidence kind or status field can fall through to success.
- **Failure behavior:** Missing/unavailable/malformed validator blocks promotion.
- **Integrations:** Evidence loader/router, all promoters/gates/scripts.
- **Acceptance:** Mutation/bypass tests replace each underlying proof with `passed=true`; all fail.
- **Dependencies:** F-REQ-014, F-REQ-112, F-REQ-149.
- **Ambiguity/contradiction notes:** The spec names four M0 kinds while broader schemas include additional kinds; safest faithful rule is closed enumeration with no generic fallback for all reachable kinds.

### F-REQ-151 — M0 formal evidence prerequisites

- **Source:** §13.2 line 2012
- **Category:** M0 formal security
- **Requirement:** Require local pinned-kernel replay, approved intent, and checked formal-correspondence before formal evidence supports release.
- **Inputs/outputs:** Inputs: T4/T5 certificate plus I2/F2 certificates. Outputs: admissible formal support or rejection.
- **Invariants:** Vendor status and ordinary build are insufficient.
- **Failure behavior:** Any missing/stale/failed prerequisite rejects formal release support.
- **Integrations:** Lean, intent/correspondence, evidence router, release.
- **Acceptance:** One-negative-case-per-prerequisite and vendor-only COMPLETE all fail through production.
- **Dependencies:** F-REQ-090, F-REQ-110, F-REQ-131.
- **Ambiguity/contradiction notes:** Untrusted generated Lean publication also requires T5; M0 must either satisfy it or limit promotion to a trusted-source profile.

### F-REQ-152 — M0 actual runner identity in every stage cache

- **Source:** §13.2 line 2013
- **Category:** M0 cache provenance
- **Requirement:** Bind cache to provider, immutable model/version when available, surface, account/tool entitlement, context, prompt, adjudicator policy, response hash, and actual runner; mark caller labels unattested.
- **Inputs/outputs:** Inputs: execution and cached artifact provenance. Outputs: compatibility decision and independence metadata.
- **Invariants:** Current object/caller labels cannot overwrite cached provenance.
- **Failure behavior:** Any changed/missing identity invalidates affected cache and cannot create independent-model evidence.
- **Integrations:** Stage cache, gateways, adjudicator, manifest projection.
- **Acceptance:** Every listed identity dimension has an independent invalidation test.
- **Dependencies:** F-REQ-015.
- **Ambiguity/contradiction notes:** Provider versions may be unattested; explicit non-reproducible labels are required.

### F-REQ-153 — M0 append-only decisions and deterministic projection

- **Source:** §13.2 line 2014
- **Category:** M0 persistence
- **Requirement:** Make gate, adjudication, evidence, and promotion records append-only and derive manifest.json deterministically.
- **Inputs/outputs:** Inputs: immutable decision events. Outputs: verifiable history and projection.
- **Invariants:** No authoritative manifest overwrite.
- **Failure behavior:** History/projection mismatch blocks release/resume.
- **Integrations:** Event log, manifest builder, gates/promoter.
- **Acceptance:** Mutation and replay tests cover all four event classes and deterministic projection.
- **Dependencies:** F-REQ-017, F-REQ-116.
- **Ambiguity/contradiction notes:** None.

### F-REQ-154 — M0 legacy quarantine including five named records

- **Source:** §13.2 line 2015
- **Category:** M0 migration
- **Requirement:** Quarantine identity-incomplete legacy manifests and stale root claim files, explicitly problems 601, 661, 724, 782, and 849, until a migration proves bindings.
- **Inputs/outputs:** Inputs: legacy records. Outputs: quarantine disposition or evidence-backed migration events.
- **Invariants:** Legacy status never silently upgrades into current evidence.
- **Failure behavior:** Incomplete/ambiguous identity remains quarantined and excluded from learning/release.
- **Integrations:** Migration tool, manifest projection, learning, release.
- **Acceptance:** All named records and synthetic stale variants are found/quarantined through production loaders.
- **Dependencies:** F-REQ-016, F-REQ-115.
- **Ambiguity/contradiction notes:** Actual files may drift; identification must use record identity/provenance, not only paths.

### F-REQ-155 — M0 explicit evidence precedence

- **Source:** §13.2 line 2016
- **Category:** M0 conflict policy
- **Requirement:** Model referees may block intent, applicability, novelty, or significance but not clean exact locked kernel truth; checked same-scope counterevidence creates CONFLICTED and audits encoding/axioms/TCB.
- **Inputs/outputs:** Inputs: kernel certificate, model review, hard counterevidence and scope. Outputs: dimension-specific block or conflict.
- **Invariants:** Truth of exact encoding and release eligibility remain separate.
- **Failure behavior:** Incompatible hard evidence never resolves by model vote or arrival order.
- **Integrations:** Graph, adjudicator, Lean, release.
- **Acceptance:** Truth-table tests cover kernel-vs-model dissent and same/different-scope hard conflict.
- **Dependencies:** F-REQ-113, F-REQ-132.
- **Ambiguity/contradiction notes:** A model can identify a valid kernel/TCB issue only by producing targeted evidence, not by status.

### F-REQ-156 — M0 complete baseline telemetry

- **Source:** §13.2 line 2017
- **Category:** M0 observability
- **Requirement:** Instrument tokens, calls, wall time, rate limits, deterministic compute, reviewer time, cache provenance, and terminal disposition.
- **Inputs/outputs:** Inputs: every attempt/stage/tool/review outcome. Outputs: authenticated event-derived telemetry.
- **Invariants:** Every attempt, not only terminal successes, is recorded and tied to run contract.
- **Failure behavior:** Missing telemetry prevents equal-cost/performance claims but cannot be imputed.
- **Integrations:** Gateways, scheduler, compute, review, cache, evaluation.
- **Acceptance:** Success/failure/timeout/cache/rate/review fixtures produce complete exact counters without double counting.
- **Dependencies:** F-REQ-116, F-REQ-143.
- **Ambiguity/contradiction notes:** Cost currency/rates must be versioned; exact provider cost may be unavailable.

### F-REQ-157 — M1 SQLite plus JSONL transactional graph

- **Source:** §13.3 line 2025
- **Category:** M1 persistence
- **Requirement:** Implement SQLite plus append-only JSONL events with materialized claim/dependency/evidence view and transactional invalidation.
- **Inputs/outputs:** Inputs: graph events/transactions. Outputs: durable JSONL and SQLite view.
- **Invariants:** JSONL/event history is authoritative; invalidation is atomic and replayable across restarts.
- **Failure behavior:** Crash/corruption/partial transaction is detected and cannot leave falsely promoted view.
- **Integrations:** Graph, event log, checkpoint.
- **Acceptance:** Restart, corruption, concurrent write, rollback, and full rebuild tests pass using production persistence.
- **Dependencies:** F-REQ-114, F-REQ-116.
- **Ambiguity/contradiction notes:** M2 migration to PostgreSQL lacks an explicit compatibility contract; event semantics must remain portable.

### F-REQ-158 — M1 structured intake and exact probes

- **Source:** §13.3 line 2026
- **Category:** M1 intake
- **Requirement:** Provide one genuine dual-parser Statement IR, explicit interpretations, source/status record, and exact boundary/counterexample probes.
- **Inputs/outputs:** Inputs: controlled finite claim source. Outputs: contract/lattice/status/probe artifacts.
- **Invariants:** Selected interpretation is consumed downstream and ambiguity blocks intent release.
- **Failure behavior:** Malformed/contradictory input or false probe fails closed/honestly.
- **Integrations:** Intake, compute, graph, release.
- **Acceptance:** Ambiguous, malformed, true, and false fixtures traverse production paths without raw-text reversion.
- **Dependencies:** F-REQ-037 through F-REQ-040.
- **Ambiguity/contradiction notes:** “One dual-parser” means two independent parse implementations in one M1 service, not one parser called twice.

### F-REQ-159 — M1 frozen retrieval, Mathlib, and read-only OEIS path

- **Source:** §13.3 line 2027
- **Category:** M1 retrieval
- **Requirement:** Provide a frozen packet containing verbatim theorem/hypothesis records, one Mathlib declaration retriever, and read-only OEIS client with typed local transforms.
- **Inputs/outputs:** Inputs: M1 claim/query. Outputs: immutable packet, premises, typed OEIS matches.
- **Invariants:** Imports/OEIS remain proposals until audit/proof and OEIS has no write path.
- **Failure behavior:** Offline/malformed/stale results remain explicit gaps without fail-open evidence.
- **Integrations:** Literature, formal index, OEIS, packet store.
- **Acceptance:** Production and negative offline/injection/malformed/transform tests exercise all three services.
- **Dependencies:** F-REQ-057, F-REQ-081 through F-REQ-088.
- **Ambiguity/contradiction notes:** Live services may be unavailable; local/frozen behavior can be verified separately from real HTTP.

### F-REQ-160 — M1 sandboxed exact Python and independent replay

- **Source:** §13.3 line 2028
- **Category:** M1 computation
- **Requirement:** Implement sandboxed exact Python enumeration and witness checking with immutable inputs/outputs and independent replay; do not substitute unrestricted CAS.
- **Inputs/outputs:** Inputs: exact finite ExperimentSpec. Outputs: classified artifact and replay report.
- **Invariants:** No host/network/credential access and no floating approximation for exact claim.
- **Failure behavior:** Sandbox unavailable/escape/resource violation/replay mismatch yields no admitted evidence and cleans up.
- **Integrations:** Compute service, artifact store, graph.
- **Acceptance:** Genuine security-boundary tests plus true/false enumeration and witness cases run through production.
- **Dependencies:** F-REQ-062, F-REQ-063.
- **Ambiguity/contradiction notes:** “Independent container” appears in §13.6; if containers are unavailable this acceptance remains BLOCKED-EXTERNAL, not simulated.

### F-REQ-161 — M1 pinned Lean project, sentinels, capsules, and proof worker

- **Source:** §13.3 line 2029
- **Category:** M1 formal
- **Requirement:** Provide a pinned Lean/Mathlib project, target-sentinel tests, exact goal capsules, and one real Lean proof worker; Aristotle is optional.
- **Inputs/outputs:** Inputs: approved M1 target. Outputs: sentinel/proof artifacts and clean certificate.
- **Invariants:** Local Lean kernel is trust root and no mocked result counts.
- **Failure behavior:** Lean unavailable/mismatch/hole/unsafe source leaves formal gate unverified.
- **Integrations:** Lean service, graph, release.
- **Acceptance:** At least one actual local proof compiles/replays and false/malformed proof cases fail.
- **Dependencies:** F-REQ-093 through F-REQ-102.
- **Ambiguity/contradiction notes:** Real Lean integration may depend on installed toolchain but repository-local defects must still be fixed.

### F-REQ-162 — M1 distinct branches and integrated controller/blueprint

- **Source:** §13.3 line 2030
- **Category:** M1 search/control
- **Requirement:** Run two or three genuinely method-distinct branches with simple best-first/UCB, typed AND/OR blueprint, semantic duplicate checks, and failure certificates.
- **Inputs/outputs:** Inputs: M1 contract/packet/graph. Outputs: selected actions, branch results, updated blueprint/failures.
- **Invariants:** Mechanism distinctions affect selection/work and failures localize.
- **Failure behavior:** Budget exhaustion pauses/honest no-result; duplicates and false branches cannot fabricate progress.
- **Integrations:** Programs, controller, blueprint, graph.
- **Acceptance:** State changes selection, real work produces evidence, evidence updates graph/future selection, and false branch adapts.
- **Dependencies:** F-REQ-044, F-REQ-045, F-REQ-071, F-REQ-073, F-REQ-074.
- **Ambiguity/contradiction notes:** Two/three branches need not equal concurrent worker count.

### F-REQ-163 — M1 independent falsifier/referee and five-axis bundle

- **Source:** §13.3 line 2031
- **Category:** M1 verification/release
- **Requirement:** Provide one independent falsifier/referee authority and five-axis release-certificate bundle in production.
- **Inputs/outputs:** Inputs: M1 candidate/graph/artifacts. Outputs: hostile report and signed dimension bundle.
- **Invariants:** One process cannot self-approve generator work or bypass any gate.
- **Failure behavior:** Any injected stage/gate failure blocks release and renders an honest narrower outcome.
- **Integrations:** Falsifier/referee, release, communication.
- **Acceptance:** True/false candidates and each gate failure run without mocking the sequence.
- **Dependencies:** F-REQ-122 through F-REQ-134.
- **Ambiguity/contradiction notes:** T3 high-value claims require two independent hostile reconstructions; a single M1 authority must perform independently evidenced passes or cannot issue T3.

### F-REQ-164 — M1 mixed controlled evaluation suite

- **Source:** §13.3 line 2032
- **Category:** M1 evaluation
- **Requirement:** Include ambiguous/false statements, formal olympiad tasks, computation-plus-proof tasks, and historically solved Erdős problems under frozen cutoffs.
- **Inputs/outputs:** Inputs: versioned fixtures. Outputs: baseline/acceptance outcomes and artifacts.
- **Invariants:** Benchmark answers/post-cutoff sources never leak into solving packet.
- **Failure behavior:** Leakage, unavailable ground truth, or mocked production paths invalidates the task result.
- **Integrations:** Evaluation harness, intake, compute, Lean, retrieval.
- **Acceptance:** Smoke tests cover every suite class including negative and rediscovery behavior.
- **Dependencies:** F-REQ-135, F-REQ-138.
- **Ambiguity/contradiction notes:** Full approximate counts are in §13.7; M1 may use compact subsets.

### F-REQ-165 — M1 minimum end-to-end scientific loop

- **Source:** §13.3 line 2034
- **Category:** M1 end-to-end
- **Requirement:** Demonstrate intake→falsification/retrieval→branching→computation/formalization→adversarial review→replayable release or honest no-result through real production entry points.
- **Inputs/outputs:** Inputs: finite true and false mathematical claims. Outputs: persisted/replayed evidence, state transitions, verifier/gates, final disposition.
- **Invariants:** No test mocks the whole sequence or bypasses persistence/gates.
- **Failure behavior:** Injected failure at every stage fails closed and remains recoverable/auditable.
- **Integrations:** All M1 components.
- **Acceptance:** The exact ten-stage slice required by the audit brief is reproduced with persisted artifacts and false-claim rejection/triage.
- **Dependencies:** F-REQ-077, F-REQ-157 through F-REQ-164.
- **Ambiguity/contradiction notes:** External integrations may be absent but the local slice must be genuine.

### F-REQ-166 — M2 begins only after M1 safety and baseline pass

- **Source:** §13.4 lines 2036-2039
- **Category:** Milestone gate
- **Requirement:** Block M2 scaling until M1 safety and baseline tests pass.
- **Inputs/outputs:** Inputs: signed/recorded M1 verification evidence. Outputs: M2 enable/deny event.
- **Invariants:** No scalability feature enables unsafe promotion or substitutes for failed M1.
- **Failure behavior:** Missing/failing/stale M1 evidence keeps M2 production policy disabled.
- **Integrations:** Feature policy, release, deployment config.
- **Acceptance:** Attempting to enable M2 with failed M1 gate is rejected across direct/config/scheduler paths.
- **Dependencies:** F-REQ-149, F-REQ-165.
- **Ambiguity/contradiction notes:** Full-scale has no explicit later graduation gate; safest implementation keeps analogous evidence gates.

### F-REQ-167 — M2 PostgreSQL, leases, object storage, and SCC transactions

- **Source:** §13.4 line 2040
- **Category:** M2 persistence/control
- **Requirement:** Add PostgreSQL event sourcing, leases/heartbeats, content-addressed object storage, and transactional SCC-aware revocation.
- **Inputs/outputs:** Inputs: distributed graph/action events and artifacts. Outputs: durable transactional state and fenced work.
- **Invariants:** Semantics match M1 event/revocation behavior across migration.
- **Failure behavior:** Postgres/object store unavailable fails configuration/startup or runs explicitly non-M2; no in-memory substitute presented as durable M2.
- **Integrations:** Database migrations, scheduler, graph, artifact store.
- **Acceptance:** Real local Postgres migration/restart/concurrency/revocation tests pass, or status is BLOCKED-EXTERNAL.
- **Dependencies:** F-REQ-114, F-REQ-119, F-REQ-157, F-REQ-166.
- **Ambiguity/contradiction notes:** Lossless M1 SQLite/JSONL migration is not specified but is necessary for continuity.

### F-REQ-168 — M2 containerized mathematical backends with certificates

- **Source:** §13.4 line 2041
- **Category:** M2 computation
- **Requirement:** Add containerized Sage plus selected CAS, SAT/SMT, ILP, and graph-enumeration backends with proof/certificate adapters.
- **Inputs/outputs:** Inputs: typed supported ExperimentSpecs. Outputs: isolated artifacts and checked certificates.
- **Invariants:** Every backend retains exact provenance/scope and no unsandboxed fallback.
- **Failure behavior:** Unavailable backend/certificate checker reports limitation and cannot admit hard evidence.
- **Integrations:** OCI runtime, compute service, solver/certificate checkers.
- **Acceptance:** At least configured backends run local integration/security/timeout/cleanup/certificate tests; unexercised ones are not claimed live.
- **Dependencies:** F-REQ-024, F-REQ-062, F-REQ-166.
- **Ambiguity/contradiction notes:** “Selected” does not require every named vendor tool, but the implemented set and gaps must be explicit.

### F-REQ-169 — M2 production OEIS, citation, theorem, and frozen referee retrieval

- **Source:** §13.4 line 2042
- **Category:** M2 retrieval
- **Requirement:** Add production OEIS transform/query caching, citation-graph retrieval, broader theorem indexing, and separate frozen solver/referee packets.
- **Inputs/outputs:** Inputs: live/versioned sources and policies. Outputs: caches/indexes and immutable role-specific packets.
- **Invariants:** Referee information boundary and source provenance remain separate from solver incentives.
- **Failure behavior:** Rate/source/index/schema drift or unavailable live services degrades explicitly without truth upgrade.
- **Integrations:** OEIS HTTP, citation index, theorem index, packet store.
- **Acceptance:** Local/live level evidence is reported separately; cache/staleness/injection/rate/failure tests pass.
- **Dependencies:** F-REQ-030, F-REQ-056 through F-REQ-059, F-REQ-081.
- **Ambiguity/contradiction notes:** Credentials/network may block live readiness.

### F-REQ-170 — M2 concurrent posterior controller and congestion pricing

- **Source:** §13.4 line 2043
- **Category:** M2 search/control
- **Requirement:** Run three to five concurrent method-distinct programs with posterior Thompson/UCB, protected exploration, pause/reopen rules, and verification-congestion pricing.
- **Inputs/outputs:** Inputs: branch/verification state and budgets. Outputs: concurrent leases/selections/throttles.
- **Invariants:** Reserved verification capacity and compatible work stealing prevent starvation/deadlock.
- **Failure behavior:** Budget/rate/crash is censored/recovered; generator backlog throttles rather than bypasses validation.
- **Integrations:** Controller, scheduler, verifier pool, telemetry.
- **Acceptance:** Deterministic concurrency tests prove competition, protected share, starvation/deadlock resistance, and crash resume.
- **Dependencies:** F-REQ-061, F-REQ-068, F-REQ-075, F-REQ-078, F-REQ-119.
- **Ambiguity/contradiction notes:** Program count, active workers, and Band-2 branch count differ; implementation must expose each.

### F-REQ-171 — M2 Lean portfolio, proof cache, and separate high-value referee

- **Source:** §13.4 line 2044
- **Category:** M2 formal/verification
- **Requirement:** Add a portfolio of open Lean provers/code agents, exact proof-state caching, and a separate model/tool family for high-value refereeing.
- **Inputs/outputs:** Inputs: GoalCapsules and high-value candidate. Outputs: diverse formal attempts and independent referee report.
- **Invariants:** All proof outputs replay under the same local trust policy; referee diversity does not replace hard checking.
- **Failure behavior:** Unavailable prover/referee is reported and cannot be simulated as live/independent.
- **Integrations:** Lean gateway, model gateway, cache, referee.
- **Acceptance:** Configured real/local portfolio integration and incompatible-cache/diversity tests pass; mock-only levels remain labeled.
- **Dependencies:** F-REQ-096, F-REQ-102, F-REQ-122, F-REQ-166.
- **Ambiguity/contradiction notes:** Exact models are chosen/pinned by local bake-off and may change monthly.

### F-REQ-172 — M2 calibration and verified expert iteration without learned value model

- **Source:** §13.4 line 2045
- **Category:** M2 learning
- **Requirement:** Collect authenticated telemetry sufficient for calibration and verified-only expert iteration while not yet requiring/training a learned value model.
- **Inputs/outputs:** Inputs: comparable replayed outcomes/costs/censoring. Outputs: calibration cohorts and verified procedural datasets.
- **Invariants:** Sparse data uses wide priors; learned value is not falsely reported.
- **Failure behavior:** Unauthenticated/incomparable data is quarantined.
- **Integrations:** Telemetry, learning, selector, evaluation.
- **Acceptance:** Later routing/procedural behavior changes only from authenticated records and cohort fingerprints.
- **Dependencies:** F-REQ-020, F-REQ-052, F-REQ-156, F-REQ-166.
- **Ambiguity/contradiction notes:** Policy may support non-learned Bayesian/ensemble posteriors before a trained value model.

### F-REQ-173 — M1 runtime roles and services are demand-driven

- **Source:** §13.5 lines 2047-2056
- **Category:** Runtime topology
- **Requirement:** Normally use four concurrent role classes—governor/intake, one or two method workers, bottleneck-selected compute/formal worker, adversarial verifier—and treat retrieval/OEIS/compute/Lean/graph as services, scaling only for independent bottlenecks.
- **Inputs/outputs:** Inputs: queue/bottleneck state. Outputs: scoped worker/service activations.
- **Invariants:** No idle chat-tab census and no role count as diversity/progress.
- **Failure behavior:** Unavailable/malicious worker is isolated/reassigned without granting broader authority.
- **Integrations:** Dispatcher, scheduler, services.
- **Acceptance:** Reachability traces show services invoked from production and role count follows bottlenecks.
- **Dependencies:** F-REQ-027, F-REQ-046, F-REQ-162.
- **Ambiguity/contradiction notes:** Two/three program branches can time-share one/two program workers.

### F-REQ-174 — Acceptance 1/18 — disabled features unreachable everywhere

- **Source:** §13.6 line 2060
- **Category:** Acceptance / feature security
- **Requirement:** Every disabled feature remains unreachable through direct scripts as well as scheduler paths.
- **Inputs/outputs:** Inputs: disabled signed policy and each entry-point call. Outputs: consistent denial.
- **Invariants:** No test-only or low-level bypass.
- **Failure behavior:** Deny before side effects and record reason.
- **Integrations:** Scheduler, scripts, verifiers, gates, promoters.
- **Acceptance:** Independent negative tests enumerate every public/direct entry point and observe no protected side effect.
- **Dependencies:** F-REQ-149.
- **Ambiguity/contradiction notes:** None.

### F-REQ-175 — Acceptance 2/18 — cache cannot cross runner identity

- **Source:** §13.6 line 2061
- **Category:** Acceptance / cache
- **Requirement:** A cached adjudication cannot replay under a different runner/model identity.
- **Inputs/outputs:** Inputs: cached adjudication and changed runner/model contract. Outputs: cache miss/invalidation.
- **Invariants:** Cached artifact provenance, not current objects, controls compatibility.
- **Failure behavior:** Reject incompatible replay.
- **Integrations:** Cache, adjudicator, run contracts.
- **Acceptance:** Independent runtime test changes each identity and proves adjudicator is re-executed/no false reuse.
- **Dependencies:** F-REQ-152.
- **Ambiguity/contradiction notes:** None.

### F-REQ-176 — Acceptance 3/18 — all behavior-closure changes invalidate affected caches

- **Source:** §13.6 line 2062
- **Category:** Acceptance / cache
- **Requirement:** Changing literature packet, adjudicator policy, feature policy, Lean/import closure, evidence adapter, or validator invalidates every affected contract/cache.
- **Inputs/outputs:** Inputs: baseline artifact plus one changed closure component. Outputs: dependency-aware invalidation.
- **Invariants:** Unaffected caches may remain only when dependency graph proves compatibility.
- **Failure behavior:** Any stale affected hit is a failure and blocks release.
- **Integrations:** Contract fingerprinting and all named services.
- **Acceptance:** Six independent mutation cases plus transitive dependency cases miss affected caches.
- **Dependencies:** F-REQ-015, F-REQ-091.
- **Ambiguity/contradiction notes:** “Every affected” requires explicit cache dependency mapping.

### F-REQ-177 — Acceptance 4/18 — caller labels cannot fabricate model independence

- **Source:** §13.6 line 2063
- **Category:** Acceptance / provenance
- **Requirement:** Caller-supplied model labels are provider/UI-attested or explicitly unattested and never count as independent-model evidence.
- **Inputs/outputs:** Inputs: caller label and provider/UI state. Outputs: attestation record or unattested label.
- **Invariants:** Unattested labels cannot populate lineage diversity.
- **Failure behavior:** Mismatch/absence remains unattested and prevents independence credit.
- **Integrations:** Model gateway, evidence diversity, manifest.
- **Acceptance:** Spoofed distinct labels for one runner produce zero independent-model evidence.
- **Dependencies:** F-REQ-109, F-REQ-152.
- **Ambiguity/contradiction notes:** Provider attestation availability varies; honesty is mandatory.

### F-REQ-178 — Acceptance 5/18 — append-only history and reproducible manifest

- **Source:** §13.6 line 2064
- **Category:** Acceptance / event sourcing
- **Requirement:** Gate, adjudication, and promotion history is append-only and deterministic manifest projection is reproducible.
- **Inputs/outputs:** Inputs: valid event stream. Outputs: identical manifest across replay.
- **Invariants:** Prior decisions persist and event order/integrity is verified.
- **Failure behavior:** Mutation/projection mismatch blocks use.
- **Integrations:** Event log, projector.
- **Acceptance:** Adversarial history tests and repeated projection produce expected detection/byte-stable canonical view.
- **Dependencies:** F-REQ-116, F-REQ-153.
- **Ambiguity/contradiction notes:** Evidence events are also append-only under M0 though this bullet names three histories.

### F-REQ-179 — Acceptance 6/18 — identity-incomplete legacy stays quarantined

- **Source:** §13.6 line 2065
- **Category:** Acceptance / migration
- **Requirement:** Identity-incomplete legacy records are quarantined rather than silently upgraded.
- **Inputs/outputs:** Inputs: legacy/incomplete records. Outputs: quarantine reason or proven migration.
- **Invariants:** No legacy evidence affects release/learning before migration.
- **Failure behavior:** Unknown identity fails closed.
- **Integrations:** Loaders, migration, graph, release.
- **Acceptance:** Named and synthetic incomplete records never appear as current admitted evidence.
- **Dependencies:** F-REQ-154.
- **Ambiguity/contradiction notes:** None.

### F-REQ-180 — Acceptance 7/18 — ambiguity creates multiple interpretations and blocks release

- **Source:** §13.6 line 2066
- **Category:** Acceptance / intake
- **Requirement:** Injected ambiguous statements create multiple interpretations and block intended-target release.
- **Inputs/outputs:** Inputs: adversarial ambiguous source. Outputs: lattice nodes and failed intent gate.
- **Invariants:** No default/raw-text fallback erases ambiguity.
- **Failure behavior:** Remain unresolved until explicit evidence/human resolution.
- **Integrations:** Intake, graph, release.
- **Acceptance:** Independent injection reaches production release and is blocked despite successful proof of one reading.
- **Dependencies:** F-REQ-038, F-REQ-158.
- **Ambiguity/contradiction notes:** None.

### F-REQ-181 — Acceptance 8/18 — false central lemma revokes all dependents

- **Source:** §13.6 line 2067
- **Category:** Acceptance / revocation
- **Requirement:** An injected false central lemma is detected, revoked/refuted appropriately, and every dependent is downgraded.
- **Inputs/outputs:** Inputs: graph with central false lemma and exact counterevidence. Outputs: SCC-aware affected closure/state changes.
- **Invariants:** Unaffected claims remain intact; conflict semantics apply when strong support survives.
- **Failure behavior:** Partial propagation or stale release is forbidden.
- **Integrations:** Falsifier, graph, controller, release.
- **Acceptance:** Independent cyclic/transitive fixture verifies precise closure, reopened branches, and blocked release.
- **Dependencies:** F-REQ-114, F-REQ-128.
- **Ambiguity/contradiction notes:** Detection evidence determines invalidation versus REFUTED.

### F-REQ-182 — Acceptance 9/18 — rate limits resume without mathematical penalty

- **Source:** §13.6 line 2068
- **Category:** Acceptance / retry
- **Requirement:** Rate limits resume without consuming proof attempts or killing claims.
- **Inputs/outputs:** Inputs: classified rate-limit responses/clock. Outputs: paused lease/backoff/resumed action.
- **Invariants:** No truth/branch-failure update.
- **Failure behavior:** Retry exhaustion remains operational/censored.
- **Integrations:** Provider gateway, scheduler, controller.
- **Acceptance:** Controlled-clock test proves exact retry counts and eventual resume under 120-second cap.
- **Dependencies:** F-REQ-079.
- **Ambiguity/contradiction notes:** None.

### F-REQ-183 — Acceptance 10/18 — crashed lease recovers idempotently

- **Source:** §13.6 line 2069
- **Category:** Acceptance / concurrency
- **Requirement:** Recover a crashed worker lease without duplicate non-idempotent actions.
- **Inputs/outputs:** Inputs: acquired action, simulated crash/expiry/reassignment. Outputs: one committed effect and recovered work.
- **Invariants:** Fencing/idempotency rejects stale/duplicate delivery.
- **Failure behavior:** Stale owner cannot commit after transfer.
- **Integrations:** Scheduler, event DB, external side-effect adapter.
- **Acceptance:** Deterministic race test counts exactly one non-idempotent effect.
- **Dependencies:** F-REQ-119.
- **Ambiguity/contradiction notes:** None.

### F-REQ-184 — Acceptance 11/18 — exact computation replays independently

- **Source:** §13.6 line 2070
- **Category:** Acceptance / computation
- **Requirement:** Every exact computation replays in an independent container.
- **Inputs/outputs:** Inputs: admitted exact artifact. Outputs: independent-environment replay pass.
- **Invariants:** Environment/code/input/output hashes and coverage match.
- **Failure behavior:** Missing container or replay mismatch blocks exact evidence/release.
- **Integrations:** Compute service, OCI runtime, artifact store.
- **Acceptance:** All admitted exact test artifacts replay; tampering/nondeterminism fails.
- **Dependencies:** F-REQ-160, F-REQ-168.
- **Ambiguity/contradiction notes:** When container infrastructure is unavailable, this criterion is BLOCKED-EXTERNAL, not replaced by same-process replay.

### F-REQ-185 — Acceptance 12/18 — Lean certificate clean pinned build with no holes

- **Source:** §13.6 line 2071
- **Category:** Acceptance / Lean
- **Requirement:** Every Lean certificate builds cleanly under the pinned environment with no placeholders.
- **Inputs/outputs:** Inputs: all certificate bundles. Outputs: clean replay/scan reports.
- **Invariants:** Full relevant source/import closure and exact type are checked.
- **Failure behavior:** Any hole/import/axiom/mismatch rejects certificate.
- **Integrations:** Lean farm, scanners, certificate store.
- **Acceptance:** Positive certificates and hidden-hole/malicious-import cases run against real Lean.
- **Dependencies:** F-REQ-092, F-REQ-097, F-REQ-161.
- **Ambiguity/contradiction notes:** T5 independent checker is additionally required for untrusted generated publication.

### F-REQ-186 — Acceptance 13/18 — vendor-only COMPLETE rejected

- **Source:** §13.6 line 2072
- **Category:** Acceptance / external prover
- **Requirement:** Reject a vendor-only `COMPLETE` result.
- **Inputs/outputs:** Inputs: provider status without local trusted proof. Outputs: candidate-only/non-reproducible rejection.
- **Invariants:** Provider status never maps to formal truth.
- **Failure behavior:** No permissive fallback when Lean unavailable.
- **Integrations:** Aristotle adapter, evidence router, promotion.
- **Acceptance:** Live/mock vendor statuses both fail without local artifact/replay; mock does not itself prove live service.
- **Dependencies:** F-REQ-090, F-REQ-151.
- **Ambiguity/contradiction notes:** None.

### F-REQ-187 — Acceptance 14/18 — changed adjudicator cannot forge independent manifest

- **Source:** §13.6 line 2073
- **Category:** Acceptance / provenance
- **Requirement:** Changing adjudicator/model invalidates incompatible stage caches and cannot create a false independent-model manifest.
- **Inputs/outputs:** Inputs: resumed run with changed adjudicator/model. Outputs: invalidation/new run provenance.
- **Invariants:** Manifest derives independence from actual artifact origins.
- **Failure behavior:** Cached same-runner output remains correlated/unusable as cross-model review.
- **Integrations:** Cache, adjudicator, event projector.
- **Acceptance:** Resume regression reproduces the historical collision and now cannot report false independence.
- **Dependencies:** F-REQ-175, F-REQ-177.
- **Ambiguity/contradiction notes:** Overlaps criterion 2 but adds final-manifest/provenance behavior.

### F-REQ-188 — Acceptance 15/18 — referee dissent follows dimension precedence

- **Source:** §13.6 line 2074
- **Category:** Acceptance / adjudication
- **Requirement:** Model-referee dissent versus kernel proof follows explicit truth/intent/novelty/significance precedence.
- **Inputs/outputs:** Inputs: exact kernel proof and dissent scoped to each dimension. Outputs: exact encoded truth retained; relevant release gate blocked/resolved.
- **Invariants:** Model cannot negate kernel fact by vote and kernel cannot clear semantic/novelty/significance.
- **Failure behavior:** Unresolved relevant dissent yields unknown/blocked release.
- **Integrations:** Adjudicator, graph, release.
- **Acceptance:** Independent truth-table tests cover all dissent scopes and direct bypasses.
- **Dependencies:** F-REQ-155.
- **Ambiguity/contradiction notes:** Applicability/reproducibility may also be attacked with concrete evidence.

### F-REQ-189 — Acceptance 16/18 — OEIS remains heuristic

- **Source:** §13.6 line 2075
- **Category:** Acceptance / OEIS
- **Requirement:** An OEIS match remains heuristic until independent proof.
- **Inputs/outputs:** Inputs: exact/high-score OEIS match. Outputs: numerical conjecture and proof/import task.
- **Invariants:** No score/entry formula upgrades truth.
- **Failure behavior:** Direct promotion is rejected.
- **Integrations:** OEIS, graph, release.
- **Acceptance:** Known match with no proof cannot satisfy target truth gate.
- **Dependencies:** F-REQ-086.
- **Ambiguity/contradiction notes:** None.

### F-REQ-190 — Acceptance 17/18 — known solved problem is rediscovery

- **Source:** §13.6 line 2076
- **Category:** Acceptance / novelty
- **Requirement:** Classify a known solved Erdős problem as rediscovery, not novel.
- **Inputs/outputs:** Inputs: frozen historical task and current prior-art evidence. Outputs: known/rediscovery novelty verdict.
- **Invariants:** Correct proof does not change novelty status.
- **Failure behavior:** Incomplete search remains N0/N1, never automatic novel.
- **Integrations:** Status/novelty audit, release, evaluation.
- **Acceptance:** At least one held-out historical solved problem traverses full production classification.
- **Dependencies:** F-REQ-040, F-REQ-127, F-REQ-138.
- **Ambiguity/contradiction notes:** Time-capsule rediscovery scoring differs from present-day release novelty; cutoff is recorded.

### F-REQ-191 — Acceptance 18/18 — no unpaired baseline superiority claim

- **Source:** §13.6 line 2077
- **Category:** Acceptance / evaluation honesty
- **Requirement:** The system makes no “beats baseline” claim unless paired evaluation supports it.
- **Inputs/outputs:** Inputs: claimed comparison and evaluation records. Outputs: supported qualified statement or refusal.
- **Invariants:** Test counts/LOC/architecture labels never substitute for paired results.
- **Failure behavior:** Missing/mismatched pair suppresses the claim.
- **Integrations:** Evaluation report generator, communication.
- **Acceptance:** Report validation rejects superiority wording without matching run contracts and metrics.
- **Dependencies:** F-REQ-021, F-REQ-137.
- **Ambiguity/contradiction notes:** None.

### F-REQ-192 — Evaluation-set composition and no solve-rate deployment claim

- **Source:** §13.7 lines 2079-2091
- **Category:** Evaluation corpus
- **Requirement:** Use roughly 20 false/ambiguous elementary, miniF2F/ProofNet# regression subset, 20 Putnam/IMO formal, 10 retrieval, 10 computation-plus-proof, 20 historical Erdős across domains/cutoffs, and a small unsolved set with no solve-rate claim.
- **Inputs/outputs:** Inputs: versioned task corpus. Outputs: categorized evaluation manifest.
- **Invariants:** Goal is safe measurable verified progress, not headline generation.
- **Failure behavior:** Missing categories/count deviations are disclosed; unsolved set never yields aggregate solve-rate claims.
- **Integrations:** Evaluation harness, corpus store.
- **Acceptance:** Manifest/count/domain/cutoff checks and leakage safeguards pass.
- **Dependencies:** F-REQ-135, F-REQ-164.
- **Ambiguity/contradiction notes:** “Roughly” permits justified deviations; exact counts and reasons must be reported.

### F-REQ-193 — Full-scale service topology is real and reachable

- **Source:** §14.1 lines 2093-2108
- **Category:** Full-scale architecture
- **Requirement:** Provide reachable production layers for PostgreSQL events/versions/revocation, content-addressed artifacts, graph views, hybrid retrieval, durable fenced scheduler, isolated compute, pinned Lean farm/independent checker, exact model gateway, event-derived observability, and five-gate release portal.
- **Inputs/outputs:** Inputs: production requests/events. Outputs: durable service results and release bundles.
- **Invariants:** A class/interface/mock does not satisfy a layer; no in-memory substitute is labeled full-scale durable.
- **Failure behavior:** Missing configuration/dependency fails startup or marks the layer unavailable without fail-open fallback.
- **Integrations:** All full-scale services.
- **Acceptance:** Production entrypoint reachability and local integration/API smoke tests exist per configured layer; external services are leveled honestly.
- **Dependencies:** F-REQ-166 through F-REQ-172.
- **Ambiguity/contradiction notes:** A dedicated graph engine is optional until profiling; PostgreSQL adjacency/materialized closure is the initial required approach.

### F-REQ-194 — Network/data-flow separation in full-scale compute

- **Source:** §14.1 line 2104; §9.6 lines 1415-1417
- **Category:** Full-scale security
- **Requirement:** Run untrusted computation with network off by default and separate it from networked retrieval/hosted-service gateways using explicit allowlisted egress and data policies.
- **Inputs/outputs:** Inputs: job/service authority and network policy. Outputs: isolated execution or policy-approved gateway call.
- **Invariants:** Compute/Lean sandboxes never inherit gateway credentials or unrestricted egress.
- **Failure behavior:** Undefined/disabled egress denies access; no unsandboxed network fallback.
- **Integrations:** OCI/VM network, gateway, credential manager, authority policy.
- **Acceptance:** Network, DNS, credential, environment, and confused-deputy escape tests fail from untrusted jobs.
- **Dependencies:** F-REQ-035, F-REQ-105, F-REQ-193.
- **Ambiguity/contradiction notes:** The spec says network off by default while retrieval is networked; this requirement resolves it by process/authority separation, not global network denial.

### F-REQ-195 — Monthly local model bake-off and campaign pinning

- **Source:** §14.2 lines 2110-2127
- **Category:** Model routing / reproducibility
- **Requirement:** Select exact model/tool versions by monthly frozen local task-specific bake-off, pin for a campaign, persist exact identity, and route by measured semantic/search/retrieval/code/Lean/referee performance rather than vendor reputation.
- **Inputs/outputs:** Inputs: candidate models/tools and versioned local evaluation. Outputs: signed route registry/run contracts.
- **Invariants:** Generic product labels are not reproducible identities; final truth remains deterministic checkers.
- **Failure behavior:** Version drift creates new contract/cache invalidation/rebenchmark; unavailable model is explicit.
- **Integrations:** Model gateway, selector/controller, evaluation.
- **Acceptance:** Registry/change tests prove pinning, exact provenance, rebenchmark triggers, and task-specific routes.
- **Dependencies:** F-REQ-015, F-REQ-078.
- **Ambiguity/contradiction notes:** Specific model suggestions are candidates, not fixed dependencies.

### F-REQ-196 — Parallelize only independent immutable work

- **Source:** §14.3 lines 2129-2140
- **Category:** Concurrency
- **Requirement:** Parallelize independent interpretations/status queries, distinct programs, independent AND leaves, proof/counterexample twins, retrieval modes, disjoint experiments, Lean branches from immutable goals, and independent verification/replay.
- **Inputs/outputs:** Inputs: dependency/compatibility graph. Outputs: concurrent leases/tasks.
- **Invariants:** Parallel tasks use immutable snapshots and scoped writes.
- **Failure behavior:** Detected dependency/conflict serializes or rejects unsafe concurrency.
- **Integrations:** Scheduler, graph, services.
- **Acceptance:** Concurrency tests cover each class and no shared-state race corrupts events/artifacts.
- **Dependencies:** F-REQ-046, F-REQ-119.
- **Ambiguity/contradiction notes:** Parallelization is conditional on genuine independence, not maximum utilization.

### F-REQ-197 — Serialize or transactionally coordinate critical decisions

- **Source:** §14.3 lines 2142-2149
- **Category:** Concurrency / consistency
- **Requirement:** Serialize/transactionally coordinate interpretation approval/target changes, claim promotion/revocation, schema migrations, final assembly, release certificates, and shared quota/backoff state.
- **Inputs/outputs:** Inputs: concurrent critical operations. Outputs: one ordered/atomic history.
- **Invariants:** Optimistic versions/fencing prevent lost update and split-brain release.
- **Failure behavior:** Conflict retries or aborts; partial state is never visible as committed.
- **Integrations:** Database transactions, event log, scheduler, release.
- **Acceptance:** Deterministic race tests cover all six operation classes.
- **Dependencies:** F-REQ-114, F-REQ-116, F-REQ-119.
- **Ambiguity/contradiction notes:** Final assembly may read concurrent immutable evidence but its commitment is serialized.

### F-REQ-198 — Compatible work stealing and verifier-reserved pool

- **Source:** §14.3 lines 2151-2152
- **Category:** Scheduler / fairness
- **Requirement:** Allow work stealing only among compatible workers; bind leases to problem/interpretation/branch/run contract/budget and reserve verifier workers.
- **Inputs/outputs:** Inputs: queued action and worker capabilities. Outputs: compatible lease or denial.
- **Invariants:** Generation cannot starve truth admission.
- **Failure behavior:** Incompatible worker cannot claim/reuse artifacts; backlog throttles generation.
- **Integrations:** Scheduler, capability registry, verifier pool.
- **Acceptance:** Starvation/deadlock/compatibility tests under load preserve verifier progress.
- **Dependencies:** F-REQ-078, F-REQ-119, F-REQ-170.
- **Ambiguity/contradiction notes:** Reserved pool size is policy-defined and observable.

### F-REQ-199 — Full-scale quality-diversity program archive

- **Source:** §14.4 lines 2153-2170
- **Category:** Full-scale search
- **Requirement:** Maintain the twelve listed method/domain program profiles in a quality-diversity archive, instantiate only compatible/current-bottleneck profiles, allow protected cross-domain exploration, and give each active program a falsifier, budget, and pause/kill criterion.
- **Inputs/outputs:** Inputs: domain/bottleneck/archive. Outputs: scoped active programs and archive updates.
- **Invariants:** No fixed agent census and no active branch without falsifier/budget/state criteria.
- **Failure behavior:** Incompatible/duplicate/missing-contract program is denied or correlated.
- **Integrations:** Governor, archive, controller, falsifier.
- **Acceptance:** Profile coverage/reachability tests and selection traces show actual differentiated behavior.
- **Dependencies:** F-REQ-044, F-REQ-071, F-REQ-173.
- **Ambiguity/contradiction notes:** The archive has profiles, not a requirement to run all twelve simultaneously.

### F-REQ-200 — Full failure-recovery matrix

- **Source:** §14.5 lines 2172-2188
- **Category:** Reliability / truth effects
- **Requirement:** Implement the specified automatic response and truth effect for rate/quota, timeout/crash, malformed model output, source conflict/unavailability, wrong interpretation, false lemma, Lean mismatch, library gap, compute mismatch, evaluator hack, version drift, verification backlog, and stagnation.
- **Inputs/outputs:** Inputs: classified failure event. Outputs: bounded retry/pause/quarantine/revocation/reroute/rebenchmark/escalation and correct truth state.
- **Invariants:** Operational failures have no truth effect unless evidence is incomplete/invalid; semantic/hard failures propagate precisely.
- **Failure behavior:** Unknown/ambiguous failure fails closed and is preserved, never swallowed.
- **Integrations:** All planes and external adapters.
- **Acceptance:** One positive recovery and adversarial negative case exists for every matrix row.
- **Dependencies:** F-REQ-074, F-REQ-075, F-REQ-079, F-REQ-114, F-REQ-118.
- **Ambiguity/contradiction notes:** Transient/permanent classification policy must be explicit and testable.

### F-REQ-201 — Bottleneck-aware scaling and mitigations

- **Source:** §14.6 lines 2190-2201
- **Category:** Performance / control
- **Requirement:** Measure semantic review, formalization, Lean search, retrieval, enumeration, branch explosion, inference, and storage bottlenecks; mitigate with direct-first, risk-weighted formalization, exact caches/snapshots, retrieval, caps, congestion pricing, deduplication, and progress-per-cost routing.
- **Inputs/outputs:** Inputs: event-derived throughput/backlog/cost telemetry. Outputs: throttling/scaling/routing decisions.
- **Invariants:** Worker/model count scales only when verification throughput and evidence warrant it.
- **Failure behavior:** Unbounded loop/token/compute/storage/backlog is prevented by budgets/limits and honest no-result/pause.
- **Integrations:** Observability, controller, storage, services.
- **Acceptance:** Load/smoke tests demonstrate bounded resources, congestion response, and no verifier starvation.
- **Dependencies:** F-REQ-076, F-REQ-078, F-REQ-143.
- **Ambiguity/contradiction notes:** Performance targets are not numerically specified; boundedness and correct control response are.

### F-REQ-202 — Human authority and intervention provenance

- **Source:** §14.7 lines 2203-2215
- **Category:** Human-in-the-loop governance
- **Requirement:** Require humans for genuinely ambiguous intent, specialized/unavailable literature, significance/publication novelty, convincing incompletely formalized central claims, public/OEIS submissions, value/risk settings, and potential major results; record every intervention.
- **Inputs/outputs:** Inputs: escalation/authorization/review. Outputs: authenticated scoped decision and intervention metadata.
- **Invariants:** Routine automation never hides required human work inside an autonomous label.
- **Failure behavior:** Missing required human decision leaves the dimension/action blocked.
- **Integrations:** Intake, retrieval, release, OEIS, policy, evaluation.
- **Acceptance:** Direct automation cannot self-authorize these actions and autonomy certificate counts every intervention.
- **Dependencies:** F-REQ-060, F-REQ-130, F-REQ-133.
- **Ambiguity/contradiction notes:** Local testing can use authenticated fixtures, but real expert judgments cannot be claimed without real reviewers.

### F-REQ-203 — Threat model and mitigations cover all listed critical risks

- **Source:** §15 lines 2217-2238
- **Category:** Security / risk management
- **Requirement:** Implement and test mitigations for wrong formalization, false model admission, circular imports, false novelty, evaluator hacking, correlated consensus, branch explosion, selector bias, contamination/bad benchmarks, unsafe formal trust, provider drift, irreproducible compute, source/licensing gaps, malicious source/code/Lean, memory contamination, communication overstatement, and reviewer bottleneck.
- **Inputs/outputs:** Inputs: threat scenarios and controls. Outputs: reproducible security findings/tests, blocks/revocations, residual-risk records.
- **Invariants:** Residual uncertainty remains explicit and no mitigation name is treated as proof.
- **Failure behavior:** Confirmed exploitable paths fail closed and are fixed locally; external blockers are classified, not hidden.
- **Integrations:** Every subsystem and FABLE security audit.
- **Acceptance:** Adversarial test suite has at least one meaningful attack per locally testable risk and records external limitations.
- **Dependencies:** All security/truth/control requirements.
- **Ambiguity/contradiction notes:** Some risks are research/social rather than fully preventable in code.

### F-REQ-204 — P0 safety precedes P1 truth, P2 search, and P3 learning/scale

- **Source:** §16 lines 2252-2294
- **Category:** Priority / rollout
- **Requirement:** Execute P0 stop-false-promotion/identity before enabling P1 truth/experiment, P2 research search, or P3 calibration/learning/scale; scale only after authenticated outcomes and ablations justify it.
- **Inputs/outputs:** Inputs: milestone evidence and signed feature policy. Outputs: enabled capability set or block.
- **Invariants:** Later functionality cannot reopen unsafe generic promotion or skip safety gates.
- **Failure behavior:** Failed predecessor evidence disables dependent production features.
- **Integrations:** Feature policy, deployment, evaluation.
- **Acceptance:** Configuration/dependency tests prove rollout ordering and rollback.
- **Dependencies:** F-REQ-148, F-REQ-149, F-REQ-166.
- **Ambiguity/contradiction notes:** P0 includes leases while M0 omits them; safest implementation treats lease safety as required before concurrent/distributed actions, not necessarily single-process M0.

### F-REQ-205 — P1 builds truth and experiment plane before deep search

- **Source:** §16 lines 2268-2276
- **Category:** Priority / integration
- **Requirement:** Before deep proof search, integrate append-only revocable graph, Statement IR/interpretations/probes, sandboxed exact compute/replay, pinned Lean target/sentinels/capsules, frozen theorem retrieval/import audit, typed OEIS, and five certificates.
- **Inputs/outputs:** Inputs: completed P0 and problem source. Outputs: evidence-gated local research capabilities.
- **Invariants:** No disconnected collection of classes counts; each service is reachable from orchestration.
- **Failure behavior:** Missing component blocks dependent deep-search/release behavior.
- **Integrations:** All P1 services and M1 loop.
- **Acceptance:** M1 production flow demonstrates each component and failure injection.
- **Dependencies:** F-REQ-165, F-REQ-204.
- **Ambiguity/contradiction notes:** M1 is the practical vertical slice of these P1 capabilities.

### F-REQ-206 — P2 dynamic research search and localized regulation

- **Source:** §16 lines 2278-2284
- **Category:** Priority / search
- **Requirement:** Convert DAG to typed AND/OR dynamic leaves, add consumed fingerprints/dedup/failure/pause/reopen, dispatch differentiated workers, implement posterior allocation with wide priors/protected exploration, and localize regulator repair to failed cones.
- **Inputs/outputs:** Inputs: P1 graph/evidence and budgets. Outputs: adaptive multi-branch search and localized revisions.
- **Invariants:** Fixed whole-proof retry loop is not the sole production path.
- **Failure behavior:** Failed cone does not discard admitted unrelated subgraphs; uncertainty pauses/reopens.
- **Integrations:** Architect, programs, controller, regulator.
- **Acceptance:** Production trace and regression tests prove local repair, branch competition, and future-decision change.
- **Dependencies:** F-REQ-018, F-REQ-162, F-REQ-205.
- **Ambiguity/contradiction notes:** Benefits remain experimental even though implementation is required to test them.

### F-REQ-207 — P3 verified scaling and honest final architectural claim

- **Source:** §16 lines 2286-2302
- **Category:** Priority / learning / reporting
- **Requirement:** Run seven-level equal-cost evaluation, collect authenticated/censored outcomes/cost/reviews, calibrate only after comparable data, add verified-only expert iteration and hard-evaluator evolution, build/measure reusable libraries, and scale workers only when throughput/ablations justify; never report the original integration as measured success without evidence.
- **Inputs/outputs:** Inputs: completed lower stages and evaluation data. Outputs: calibrated policies, verified learning/reuse metrics, evidence-qualified architecture verdict.
- **Invariants:** Amount of generated mathematics/test count/LOC cannot establish success.
- **Failure behavior:** Sparse/unmatched/unverified data leaves advantages unknown and prevents scale/performance claims.
- **Integrations:** Evaluation, learning, libraries, scheduler, audit communication.
- **Acceptance:** Final report separates verified implementation, real-service evidence, mocks/static inspection, external blockers, unresolved defects, and empirical performance.
- **Dependencies:** F-REQ-147, F-REQ-172, F-REQ-204 through F-REQ-206.
- **Ambiguity/contradiction notes:** Complete repository implementation can still have external/empirical limitations; it cannot be called complete if local required behavior is missing.

### F-REQ-208 — Lightweight generation is a cheap baseline with explicit verification cost

- **Source:** §2.1 lines 145-150
- **Category:** Evaluation / baseline
- **Requirement:** Use a lightweight generation/critique/citation pipeline only as a cheap candidate-generation baseline and measure verification cost separately; citation presence and inferred confidence are not verification.
- **Inputs/outputs:** Inputs: matched task/budget and lightweight candidate. Outputs: candidate yield, verification effort, and verified/failure outcomes.
- **Invariants:** Unverified candidates do not count as solutions.
- **Failure behavior:** If only generation is exercised, report candidate-generation behavior, not research-proof performance.
- **Integrations:** Evaluation harness, retrieval audit, referee.
- **Acceptance:** Baseline reporting separates minutes/cost to generate from hours/cost and outcomes to verify, with exact denominators.
- **Dependencies:** F-REQ-021, F-REQ-136.
- **Ambiguity/contradiction notes:** The referenced external implementation is illustrative; repository need not depend on it.

### F-REQ-209 — Task-class routing preserves specified trust boundaries

- **Source:** §14.2 lines 2114-2125
- **Category:** Model/tool routing
- **Requirement:** Route intake reconciliation to two distinct reasoning families plus symbolic parser; broad programs to cost-efficient mixed models; central bottlenecks to strongest locally proven model; literature to retrieval/reranker/auditor; code to sandboxed agents/tools; Lean to formal provers/agents; hosted formal tools only as optional candidates; referees to separate equipped families; final truth to deterministic checkers; novelty/significance to retrieval plus humans.
- **Inputs/outputs:** Inputs: task class and frozen local bake-off. Outputs: capability-scoped route and recorded selection criterion.
- **Invariants:** No model-only substitute for final truth or novelty/significance expert audit.
- **Failure behavior:** Unavailable/ineligible route triggers explicit alternate or blocked status, never broader privilege/fail-open trust.
- **Integrations:** Model/tool gateway, authority policy, controller.
- **Acceptance:** Routing tests cover every table row, trust boundary, version drift, and unavailable provider.
- **Dependencies:** F-REQ-060, F-REQ-195.
- **Ambiguity/contradiction notes:** Candidate products are not fixed; task classes and selection/trust criteria are.

### F-REQ-210 — Ablate interpretation-lattice cost against prevented target errors

- **Source:** §15 lines 2240-2243
- **Category:** Experimental validation
- **Requirement:** Measure whether multiple interpretations prevent enough false-target work to justify added search cost.
- **Inputs/outputs:** Inputs: matched single-target versus lattice runs with ambiguous/unambiguous tasks. Outputs: false-target prevention, cost, and downstream outcome metrics.
- **Invariants:** Lattice benefit is not assumed from implementation.
- **Failure behavior:** Insufficient evidence leaves policy experimental and does not remove fail-closed ambiguity handling.
- **Integrations:** Intake, evaluation.
- **Acceptance:** Preregistered paired ablation reports both prevented errors and multiplicative search cost.
- **Dependencies:** F-REQ-004, F-REQ-137, F-REQ-147.
- **Ambiguity/contradiction notes:** Safety requirement to preserve known ambiguity remains even if broad lattice expansion is costly.

### F-REQ-211 — Ablate cold-pass budgets at 0%, 5%, and 10%

- **Source:** §15 line 2243
- **Category:** Experimental validation
- **Requirement:** Compare zero, five, and ten percent cold-pass allocation for anchoring, query quality, verified progress, and wasted budget.
- **Inputs/outputs:** Inputs: identical tasks/contracts aside from cold fraction. Outputs: matched outcome/cost metrics.
- **Invariants:** Deep retrieval remains mandatory in all conditions except explicitly defined no-literature ablations.
- **Failure behavior:** Without ablation, 5–10% stays an engineering default, not optimized policy.
- **Integrations:** Controller, programs, retrieval, evaluation.
- **Acceptance:** Frozen paired runs exercise all three fractions and preserve information boundaries.
- **Dependencies:** F-REQ-005, F-REQ-137, F-REQ-145.
- **Ambiguity/contradiction notes:** M1 does not explicitly name cold pass, but the full production flow does.

### F-REQ-212 — Validate posterior controller against simple best-first search

- **Source:** §15 line 2244
- **Category:** Experimental validation
- **Requirement:** Compare sparse/nonstationary posterior allocation with a simple best-first baseline so learned values are not assumed superior.
- **Inputs/outputs:** Inputs: matched frontier/outcome streams. Outputs: verified progress/cost, calibration, stability, and branch coverage comparison.
- **Invariants:** Wide priors and protected exploration remain until evidence supports calibration.
- **Failure behavior:** Underperformance or sparse data prevents claiming/adopting learned superiority.
- **Integrations:** Controller, calibration, evaluation.
- **Acceptance:** Causal paired ablation changes only allocation policy and reports uncertainty.
- **Dependencies:** F-REQ-028, F-REQ-137, F-REQ-147.
- **Ambiguity/contradiction notes:** M1 simple best-first/UCB is a natural baseline; M2 implements posterior policy to test.

### F-REQ-213 — Test whether risk-weighted Lean sentinels miss subtle steps

- **Source:** §15 line 2245
- **Category:** Experimental validation
- **Requirement:** Evaluate sentinel prioritization against hidden subtle failures and alternative early/late formalization policies.
- **Inputs/outputs:** Inputs: seeded semantic-risk proof graphs. Outputs: detection recall/time/cost and missed-central-step analysis.
- **Invariants:** Sentinel success is not proof the true subtle step was selected.
- **Failure behavior:** Missed risks remain residual defects and prevent superiority claims.
- **Integrations:** Lean, graph risk model, evaluation.
- **Acceptance:** Injected subtle-step suite measures detection and compares specified ablations.
- **Dependencies:** F-REQ-009, F-REQ-031, F-REQ-145.
- **Ambiguity/contradiction notes:** Risk estimates are initially weak and must remain auditable.

### F-REQ-214 — Credit verified DAG work by downstream unlock, not node count

- **Source:** §15 line 2246
- **Category:** Learning / evaluation anti-gaming
- **Requirement:** Measure whether a verified lemma actually unlocks target dependencies and assign learning/progress credit accordingly rather than by verified-node count.
- **Inputs/outputs:** Inputs: frozen dependency graph and admitted lemmas. Outputs: downstream unlock/target-debt credit.
- **Invariants:** Disconnected/easy verified lemmas receive no target progress credit.
- **Failure behavior:** Graph or weight manipulation invalidates credit cohort.
- **Integrations:** Graph, controller, learning, evaluation.
- **Acceptance:** Adversarial disconnected-node inflation cannot increase progress or future policy reward.
- **Dependencies:** F-REQ-070, F-REQ-141, F-REQ-142.
- **Ambiguity/contradiction notes:** Reusable cross-problem value is a separate component.

### F-REQ-215 — Test cross-problem reuse reward for search distortion

- **Source:** §15 line 2247
- **Category:** Experimental validation
- **Requirement:** Measure whether reuse rewards create real downstream benefit or bias compute away from decisive problem-specific insights.
- **Inputs/outputs:** Inputs: matched allocation with/without reuse reward and cross-problem graph. Outputs: actual reuse, solve/progress displacement, and cost.
- **Invariants:** Predicted reuse is not counted as realized value.
- **Failure behavior:** No demonstrated downstream use prevents claiming reuse benefit and may cap its weight.
- **Integrations:** Selector/controller, formal library, evaluation.
- **Acceptance:** Paired runs track concrete later consumers and opportunity cost.
- **Dependencies:** F-REQ-067, F-REQ-137, F-REQ-207.
- **Ambiguity/contradiction notes:** Formal library construction may still be valuable as its own outcome but must be labeled accordingly.

### F-REQ-216 — Provider diversity is not proof independence

- **Source:** §15 line 2248
- **Category:** Verification / experimental limitation
- **Requirement:** Record different-provider review as one diversity signal while explicitly accounting for shared corpora/training and never treating it as independent mathematical proof.
- **Inputs/outputs:** Inputs: provider/model lineage and reviewer artifacts. Outputs: qualified independence profile.
- **Invariants:** Hard checker/reconstruction obligations remain unchanged.
- **Failure behavior:** Provider-name difference alone cannot satisfy T3/T4/T5 or truth promotion.
- **Integrations:** Model gateway, referee, evidence diversity, release.
- **Acceptance:** Two provider outputs without independent evidence remain correlated search/review testimony.
- **Dependencies:** F-REQ-020, F-REQ-109, F-REQ-122.
- **Ambiguity/contradiction notes:** True training overlap may be unknowable and must remain residual uncertainty.
