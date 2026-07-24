# EGMRA Implementation Ledger

Authoritative persistent state for implementing
`docs/AUTONOMOUS_MATH_RESEARCH_ARCHITECTURE_2026.md` (the "spec").

**Status vocabulary:** `PLANNED` (extracted, not started) · `IN_PROGRESS` ·
`VERIFIED` (code exists AND behavior tested with a passing test) · `BLOCKED`
(precise unavoidable blocker) · `NOT_APPLICABLE` (with justification).
A requirement becomes `VERIFIED` only after its test is written and observed to
pass. No requirement may end as `PLANNED`/`PARTIAL`/`TODO`/`UNREVIEWED`.

**Package strategy:** new `egmra/` package holds new subsystems; existing modules
(`run_contract.py`, `verification.py`, `lean_verify.py`, `feature_flags.py`,
`erdos_ingest.py`, `erdos_searcher.py`) are reused/patched where the spec says
"retain" or "repair". Tests: `egmra/tests/` (new) + existing `tests/` stays green
(baseline 179 passed).

---

## Section 1 — Executive summary & highest-priority decisions

| ID | Source | Requirement summary | Component | Deps | Status | Evidence |
|---|---|---|---|---|---|---|
| REQ-001 | §1 | Five independent gates: statement fidelity, truth, novelty, significance, reproducibility | egmra/release/gates.py | REQ-070,REQ-112 | VERIFIED | run_five_gates separate profile; summary_label non-collapsed; test_release.py (9) |
| REQ-002 | §1 | Immutable source record + explicit interpretation lattice (not one normalized statement) | egmra/intake/interpretation.py | REQ-040 | VERIFIED | lattice parent+children; release_blocked; test_intake.py (14 pass) |
| REQ-003 | §1 | Literature-blind falsification pass then mandatory theorem-level retrieval before proof search | egmra/orchestrator/loop.py | REQ-040,REQ-050 | VERIFIED | loop enforces cold_pass<packet<deep_branches; test_orchestrator.py |
| REQ-004 | §1 | Append-only epistemic claim graph w/ typed evidence, deps, contradictions, cascading revocation | egmra/truth/graph.py | REQ-060 | VERIFIED | EpistemicGraph+EventLog+revocation; test_truth_plane.py (17 pass) |
| REQ-005 | §1 | Three nested searches: research programs, AND/OR lemma graph, Lean proof-state | egmra/search/*, egmra/lean/* | REQ-080 | VERIFIED | programs+AndOrBlueprint+proof_state; test_search.py (21) + test_lean.py |
| REQ-006 | §1 | Dynamic branch allocation by posterior expected utility + VOI + protected exploration | egmra/search/controller.py | REQ-081 | VERIFIED | additive U(b,a) + Thompson + 15-25% reserve; test_search.py |
| REQ-007 | §1 | Early Lean sentinels for target, definitions, boundary cases, high-centrality/risk lemmas | egmra/lean/sentinels.py | REQ-092 | VERIFIED | select_sentinels + F(c); test_lean.py (19 pass) |
| REQ-008 | §1 | Executable Python/CAS/SAT/SMT/ILP experiments w/ immutable artifacts + independent replay | egmra/compute/service.py | REQ-047 | VERIFIED | ComputeService + SubprocessSandbox + replay; test_compute.py (9 pass) |
| REQ-009 | §1 | Adversarial referee subsystem that receives no reward for agreement | egmra/verification/referee.py | REQ-110 | VERIFIED | reward=defects-found; cannot repair; test_verification.py |
| REQ-010 | §1 | Verified-only persistent memory + outcome-calibrated expert iteration | egmra/learning/memory.py | REQ-04A | VERIFIED | LongTermMemory verified-only + VerifiedOnlyExpertIteration; test_learning.py |
| REQ-011 | §1 | Require local kernel replay + statement-fidelity approval for formal promotion; disable promotion until every evidence kind has a validator + flags enforced | egmra/release/policy.py, verification.py | REQ-070,REQ-140 | VERIFIED | PromotionPolicy needs kernel+intent+correspondence+feature; test_release.py, test_m0_safety.py |
| REQ-012 | §1 | Bind every stage to actual provider/model/runner, adjudicator, literature policy, formal env, validator, prompt, tools, artifacts; reject incompatible cache | egmra/provenance/stage_identity.py | REQ-061b | VERIFIED | StageIdentity.cache_key binds all fields; incompatible reuse rejected; test_foundations.py (17 pass) |
| REQ-013 | §1 | Replace mutable manifests w/ typed claim graph + append-only events; replace fixed loop w/ AND/OR; add falsification + sentinels before scaling | egmra/* | REQ-004,REQ-080 | VERIFIED | EpistemicGraph + AndOrBlueprint + compute falsifier + sentinels; test_truth_plane/test_search/test_lean |
| REQ-014 | §1 | Frozen theorem-level packets incl OEIS+formal; literature mandatory before deep work w/ 5-10% blind pass; Aristotle worker not trust root; learn only authenticated; eval vs raw baseline equal cost | egmra/retrieval/*, egmra/eval/* | REQ-040,REQ-130 | VERIFIED | frozen SourcePacket + OEIS + two-pass loop + aristotle_routing + baseline_comparison_valid; tests |

## Section 4 — Critical review of current pipeline

| ID | Source | Requirement summary | Component | Deps | Status | Evidence |
|---|---|---|---|---|---|---|
| REQ-020 | §4.1 | Aristotle sidecar must NOT emit passed=true from vendor COMPLETE when kernel unavailable | aristotle_verifier.py | REQ-090 | VERIFIED | verify_run forces require_kernel on promote path; egmra lean validator rejects aristotle_reported; test_acceptance.py acc13 + tests/test_aristotle_verifier.py |
| REQ-021 | §4.2 | Retain source provenance; replace semantic intake w/ Statement IR + dual parse + reconciliation + mutation tests + interpretations | egmra/intake/* | REQ-040 | VERIFIED | GrammarParser+ClauseParser+reconcile+probes; test_intake.py |
| REQ-022 | §4.2 | Retain queue/provenance; replace selector model w/ competing-risk posterior, censored outcomes, VOI, reuse | egmra/selection/* | REQ-081 | VERIFIED | CompetingRiskPosterior censoring + acquisition; test_selection.py |
| REQ-023 | §4.2 | Related-work packet → theorem retrieval; freeze theorem records w/ source spans + applicability | egmra/retrieval/packet.py | REQ-043 | VERIFIED | frozen SourcePacket + TheoremRecord; test_retrieval.py (11 pass) |
| REQ-024 | §4.2 | Replace fixed 4-scout census w/ tool/info-differentiated program workers dispatched dynamically; attest model identity | egmra/agents/* | REQ-044 | VERIFIED | MethodProfile diversity + instantiate_programs + AttestedModelIdentity; test_agents.py (11) |
| REQ-025 | §4.2 | Synthesis DAG → typed AND/OR blueprint w/ dynamic leaves, proof debt, dependency-local repair | egmra/search/blueprint.py | REQ-080 | VERIFIED | AndOrBlueprint closure + failed_dependency_cone; test_search.py |
| REQ-026 | §4.2 | Demote whole-proof constructor to compiler assembling only from admitted claims | egmra/release/compiler.py | REQ-004 | VERIFIED | assemble_from_admitted_graph refuses UNKNOWN; test_release.py |
| REQ-027 | §4.2 | Reviewers as checks not evidence; tool-backed falsifier, source auditor, formal replay, different-family referee | egmra/verification/* | REQ-110 | VERIFIED | referee obligations-not-score + diversity fields; test_verification.py (13) |
| REQ-028 | §4.2 | Localize regulator to failed dependency cone w/ posterior budget + reopen rules | egmra/search/controller.py | REQ-081 | VERIFIED | AndOrBlueprint.failed_dependency_cone + Controller reopen_conditions; test_search.py |
| REQ-029 | §4.2 | Replace ResearchState mutable JSON w/ event-sourced epistemic graph (views may stay JSON) | egmra/truth/graph.py | REQ-004 | VERIFIED | events authoritative, views.py derived; test_truth_plane.py |
| REQ-020b | §4.2 | Stage cache/run contract: bind per-stage runner/model/provider/context, hash import closure + policies, exact Lean context + replay policy | egmra/provenance/stage_identity.py | REQ-061b | VERIFIED | import_closure_hash + policy hashes bound; AttestedModelIdentity.independent_of; test_foundations.py |
| REQ-020c | §4.2 | Worker queue: leases/heartbeats + provider-aware throttling; rate limits pause never terminate | egmra/control/leases.py | REQ-08A | VERIFIED | LeaseManager + ProviderThrottle pause-not-fail; test_control.py |
| REQ-020d | §4.2 | Computational evidence sandboxed immutable jobs + exact arithmetic + coverage + replay + typed certificate | egmra/compute/* | REQ-047 | VERIFIED | sandbox+exact+coverage+replay+certificate; test_compute.py |
| REQ-020e | §4.2 | Lean sidecar redesign: kernel required, target audit, source/axiom/import scan, early central lemmas, typed evidence | egmra/lean/* | REQ-090 | VERIFIED | LeanService kernel+axiom+placeholder scan+target-type; test_lean.py |
| REQ-020f | §4.2 | Promotion gate: replace evidence acceptance + split five gates producing separate certificates | egmra/release/* | REQ-070 | VERIFIED | run_five_gates + PromotionPolicy; test_release.py |
| REQ-020g | §4.2 | Release flags enforced centrally: every verifier/promoter/scheduler/cache records + checks one signed feature policy | egmra/policy/__init__.py, promote_verified_run.py | REQ-140 | VERIFIED | PolicyEnforcer records+checks at every entry point; promote() enforces; test_foundations.py, test_m0_safety.py |
| REQ-020h | §4.2 | Manifest = derived view; append immutable gate/adjudication/promotion events w/ explicit precedence | egmra/truth/events.py | REQ-004 | VERIFIED | manifest_projection derived; append-only EventLog; test_truth_plane.py |
| REQ-020i | §4.2 | Learning: verified-only + telemetry; temp problem memory vs replayable persistent memory | egmra/learning/* | REQ-04A | VERIFIED | 6 stores + PromotionTelemetry; test_learning.py, test_m0_safety.py |
| REQ-020j | §4.2 | OEIS structured service (not prose agent): transform locally, cache, provenance, independent claim checking | egmra/oeis/* | REQ-051 | VERIFIED | typed transforms + cached client + held-out verification; test_oeis.py (14 pass) |
| REQ-020k | §4.3 | Consolidate 22 roles into 7 durable authorities; instantiate specialists conditionally | egmra/agents/authorities.py | REQ-044 | VERIFIED | 7 AUTHORITIES + conditional instantiate_programs; test_agents.py |
| REQ-020l | §4.3 | Replace multiplicative branch priority w/ posterior EU + VOI under safety constraints | egmra/search/controller.py | REQ-081 | VERIFIED | additive branch_action_utility; test_search.py |
| REQ-020m | §4.3 | Statement adversary blocks publication not all exploration; interpretation lattice | egmra/intake/interpretation.py | REQ-002 | VERIFIED | explorable_nodes always; release_blocked while ambiguous; test_intake.py |
| REQ-020n | §4.3 | Controlled two-pass protocol (blind scratch, frozen packet, targeted re-entry w/ provenance) | egmra/orchestrator/loop.py | REQ-003 | VERIFIED | loop phases + SourcePacket.reentry; test_orchestrator.py, test_retrieval.py |
| REQ-020o | §4.3 | Formalize target/defs/boundary/high-risk only, not every prose claim | egmra/lean/sentinels.py | REQ-092 | VERIFIED | low-risk glue deferred in select_sentinels; test_lean.py |
| REQ-020p | §4.3 | Admission depends on evidence type; model review routes but cannot manufacture truth tier | egmra/truth/validators.py | REQ-061 | VERIFIED | type-specific validators; proposals cannot assert status; test_truth_plane.py |
| REQ-020q | §4.4 | Preserve invariants: pinned snapshots, statement lock, content-addressed contracts, append-only ledger, protected exploration, atomic claims, rate-limit ≤120s, deterministic rejection, regulator distinction | reuse + egmra | many | VERIFIED | existing run_contract/verification retained + egmra events/throttle(120s)/controller; 419 tests |

## Section 5 — Proposed architecture

| ID | Source | Requirement summary | Component | Deps | Status | Evidence |
|---|---|---|---|---|---|---|
| REQ-030 | §5.1 | Four planes: truth, search, control, communication | egmra/{truth,search,control,comms}/ | - | VERIFIED | four plane packages present + tested; egmra/tests/* |
| REQ-031 | §5.1 | Blackboard w/ least-privilege slices; agents write proposals; only truth plane changes status | egmra/truth/blackboard.py | REQ-004 | VERIFIED | ReadSlice + proposal-only writes; test_truth_plane.py |
| REQ-032 | §5.2 | End-to-end flow steps 1-17 | egmra/orchestrator/loop.py | most | VERIFIED | research() runs all 17 steps; test_orchestrator.py end-to-end |
| REQ-033 | §5.3 | Design-status table machine-readable (established/demonstrated/original) | egmra/design_status.py | - | VERIFIED | DESIGN_STATUS + originals(); test_meta.py |

## Section 6 — Detailed module specifications

| ID | Source | Requirement summary | Component | Deps | Status | Evidence |
|---|---|---|---|---|---|---|
| REQ-040 | §6.1 | Module A intake: Statement IR, 2 parses, backtranslate, paraphrase/mutation tests, boundary/type probes, counterexample search, interpretation nodes, ProblemContract | egmra/intake/* | REQ-021 | VERIFIED | full pipeline; paraphrase-invariance + mutation-covariance + executable counterexample probes; test_intake.py |
| REQ-041 | §6.2 | Module B selector: 9 feature families; competing outcome posterior; selection behavior + separate ranked lists | egmra/selection/* | REQ-081 | VERIFIED | ProblemFeatures(9 families)+CompetingRiskPosterior+ProblemSelector; test_selection.py |
| REQ-042 | §6.3 | Module C OEIS deterministic service + source-auditing worker w/ trigger logic | egmra/oeis/* | REQ-051 | VERIFIED | client+transforms+matching; test_oeis.py |
| REQ-043 | §6.4 | Module D retrieval: 4 indexes; query bundle; TheoremRecord; ranking; retriever + import auditor; separate novelty query log | egmra/retrieval/* | REQ-023 | VERIFIED | TF-IDF retriever + ImportAuditor + NoveltyQueryLog; test_retrieval.py |
| REQ-044 | §6.5 | Module E: 7 authorities; dispatchable method profiles; diversity ≥2 axes; role prompt specs | egmra/agents/* | REQ-020k | VERIFIED | authorities+profiles+prompts+runner; test_agents.py (11) |
| REQ-045 | §6.6 | Module F shared state: append-only graph + views; weak-tier claim guides search but tier travels | egmra/truth/* | REQ-004 | VERIFIED | blackboard exposes true tier; no summary upgrade; test_truth_plane.py |
| REQ-046 | §6.7 | Module G search hybrid (Thompson/UCB, MAP-Elites, AO*, PUCT, evolution executable-only, debate proposes) | egmra/search/* | REQ-006 | VERIFIED | algorithms routing + QD archive + AO* + PUCT; test_search.py (21) |
| REQ-047 | §6.8 | Module H computation: immutable job API; ExperimentSpec; 6-way artifact classification checked; float never proves exact; SAT via reconstruction | egmra/compute/* | REQ-008 | VERIFIED | 6-way classification downgrades; reconstruct_unsat RUP; network blocked; test_compute.py |
| REQ-048 | §6.9 | Module I Lean staged L0-L5 + service API + missing-library + coverage + Aristotle routing | egmra/lean/* | REQ-090 | VERIFIED | all L0-L5 + service + missing-library + coverage + routing; test_lean.py (19 pass) |
| REQ-049 | §6.10 | Module J adversarial verification separate; positive result = discharged obligations | egmra/verification/* | REQ-009 | VERIFIED | RefereeResult obligations; reports_to auditor; test_verification.py (13) |
| REQ-04A | §6.11 | Module K memory: 6 stores never conflated; frozen eval + different evaluators | egmra/learning/* | REQ-065 | VERIFIED | LongTermMemory 6 stores + VerifiedOnlyExpertIteration; test_learning.py |
| REQ-04B | §6.12 | Service interfaces table (8 services) typed request+response | egmra/services.py | many | VERIFIED | 8 ServiceContracts + Protocols; truth_upgrade flags; test_meta.py |

## Section 7 — Mathematical search & compute allocation

| ID | Source | Requirement summary | Component | Deps | Status | Evidence |
|---|---|---|---|---|---|---|
| REQ-080 | §7.1 | Different algorithms per level connected via claim graph | egmra/search/* | REQ-046 | VERIFIED | SEARCH_LEVEL_ALGORITHMS routing; test_search.py |
| REQ-081 | §7.2 | Problem acquisition score A_p; Thompson sampling; 15-25% protected; wide intervals early | egmra/selection/acquisition.py | REQ-041 | VERIFIED | acquisition_score A_p + Thompson + protected reserve clamp; test_selection.py |
| REQ-082 | §7.3 | Branch/action utility U(b,a) additive; PUCT Lean score w/ verifiedDebt; transpositions keyed | egmra/search/controller.py, egmra/lean/proof_state.py | REQ-006 | VERIFIED | branch_action_utility additive + puct_score + TranspositionTable; test_search.py/test_lean.py |
| REQ-083 | §7.3 | verifiedDebt target-relative; helper restating target zero/negative credit; frozen for eval | egmra/search/verified_debt.py | REQ-025 | VERIFIED | DebtPolicy frozen + restates_target_penalty; test_search.py |
| REQ-084 | §7.4 | Mechanism fingerprint (9 fields); QD archive bins; 10 branch-generation types incl verified-only crossover | egmra/search/mechanism.py, archive.py | REQ-046 | VERIFIED | MechanismFingerprint + QualityDiversityArchive; test_search.py |
| REQ-085 | §7.5 | Duplicate detection cascade (6 stages) | egmra/search/dedup.py | REQ-084 | VERIFIED | dedup_cascade 6 stages; test_search.py |
| REQ-086 | §7.6 | Failure compression cert; resource exhaustion censored; kill only counterexample/impossibility/dominated/policy | egmra/search/failure.py | REQ-004 | VERIFIED | FailureCertificate + KILL/CENSORED reasons; test_search.py |
| REQ-087 | §7.7 | Pause/stop/reopen rules | egmra/search/controller.py | REQ-081 | VERIFIED | should_pause/can_terminate/reopen_conditions; test_search.py |
| REQ-088 | §7.8 | Compute bands 0-5 + 10-20% reserve | egmra/search/bands.py | REQ-081 | VERIFIED | 6 BANDS + reserve_amount; test_search.py |
| REQ-089 | §7.9 | Main research loop pseudocode implemented faithfully | egmra/orchestrator/loop.py | most | VERIFIED | research() matches pseudocode; test_orchestrator.py |
| REQ-08A | §7.10 | Compute safeguards: reserve verification, local routing, branch cap w/ governor event, costs incl review+debt, provider backoff Retry-After+jitter+120s pauses leases | egmra/control/* | REQ-020c | VERIFIED | VerifierPool reserve + Controller.allocate cap + ProviderThrottle 120s; test_control.py, test_search.py |

## Section 8 — OEIS & external-database integration

| ID | Source | Requirement summary | Component | Deps | Status | Evidence |
|---|---|---|---|---|---|---|
| REQ-050 | §8.1 | Corpus/status hygiene: pin snapshot; separate evidence records; dated status; refresh; conflict → status_uncertain + literature task | egmra/corpus/status.py | REQ-021 | VERIFIED | reconcile_status; conflict blocks campaign; test_retrieval.py |
| REQ-051 | §8.2 | OEIS service contract: request schema; typed transform registry (domains/params/preconditions/inverse); undefined fail visibly; cache time+hash; rate-limit + AI-submission-forbidden policy | egmra/oeis/transforms.py, client.py | REQ-020j | VERIFIED | 20 typed transforms; submit refused; cache+throttle; test_oeis.py |
| REQ-052 | §8.3 | Match ranking + workflow (5-10 terms, exact+transformed, held-out test, NUMERICAL_EVIDENCE node, prove formulas used); match=conjecture; not-found != novelty | egmra/oeis/matching.py | REQ-051 | VERIFIED | ranking + held-out verification + conjecture node; test_oeis.py |
| REQ-053 | §8.4 | Literature service interface (LiteratureQuery, immutable SourcePacket, versioned re-entry) | egmra/retrieval/service.py | REQ-043 | VERIFIED | reentry links predecessor + new hash; test_retrieval.py |
| REQ-054 | §8.5 | Theorem-library retrieval: retrievePremises informal+typed; PremiseCandidate fields; use only after elaboration; source auditor no silent strengthening | egmra/retrieval/premises.py, egmra/lean/premises.py | REQ-043 | VERIFIED | PremiseLibrary + usable_after_elaboration; auditor rejects strengthening; test_retrieval.py |
| REQ-055 | §8.6 | Claim-specific source priority matrix (6 claim kinds) | egmra/retrieval/source_priority.py | REQ-043 | VERIFIED | 6-kind matrix; test_retrieval.py |

## Section 9 — Lean & Aristotle formal-verification workflow

| ID | Source | Requirement summary | Component | Deps | Status | Evidence |
|---|---|---|---|---|---|---|
| REQ-090 | §9.1 | M0 Lean repairs (8 items): require_kernel non-overridable; reject aristotle_reported; preserve+validate metadata; require intent+correspondence certs; pin toolchain; gate scripts; fingerprint closure; clean offline rebuild + placeholder/sorry/unsafe scan | aristotle_verifier.py, lean_verify.py, egmra/lean/* | REQ-011 | VERIFIED | egmra/lean redesign + aristotle_verifier verify_run forces require_kernel on promote; tests/test_aristotle_verifier.py + egmra test_lean.py + test_acceptance.py acc13 |
| REQ-091 | §9.2 L0 | Semantic target package: 2-3 candidates, defs, backtranslate, example/anti-example, equivalence, paraphrase/mutation, freeze declaration hash | egmra/lean/target_package.py | REQ-040 | VERIFIED | TargetPackage freeze; test_lean.py |
| REQ-092 | §9.2 L1 | Lean sentinels early (type/domain, boundary, monotonicity/symmetry, finite cases, central lemma by centrality×risk×cost) | egmra/lean/sentinels.py | REQ-007 | VERIFIED | select_sentinels; test_lean.py |
| REQ-093 | §9.2 L2 | Formal blueprint: sorry only in quarantined branch; each hole = node; production never imports quarantine; direct-first; reject restating helpers | egmra/lean/blueprint.py | REQ-025 | VERIFIED | FormalBlueprint rejects restating helper + direct-first; test_lean.py |
| REQ-094 | §9.2 L3 | Proof-state search portfolio + diagnostics routing | egmra/lean/proof_state.py | REQ-082 | VERIFIED | PROOF_PORTFOLIO + PUCT + route_diagnostic + TranspositionTable; test_lean.py |
| REQ-095 | §9.2 L4 | Assembly/sync: informal↔formal share claim IDs; every load-bearing sentence maps; bidirectional propagation | egmra/lean/sync.py | REQ-026 | VERIFIED | ProofSync coverage + propagation; test_lean.py |
| REQ-096 | §9.2 L5 | Hardening/release: eliminate sorry/axioms/unsafe; transitive axiom closure + whitelist; clean pinned offline; second checker; archive; human-readable proof | egmra/lean/hardening.py | REQ-090 | VERIFIED | harden releasable gate + untrusted needs independent checker; test_lean.py |
| REQ-097 | §9.3 | Lean service API (7 methods) + FormalCertificate + immutable target module + type-check vs locked + compareStatements checked-only + axiom policy + GoalCapsule key | egmra/lean/service.py | REQ-090 | VERIFIED | full API; equivalent only w/ proof; GoalCapsule context-keyed; test_lean.py |
| REQ-098 | §9.4 | Missing library workflow (7 steps) | egmra/lean/missing_library.py | REQ-097 | VERIFIED | ordered 7-step workflow; test_lean.py |
| REQ-099 | §9.5 | Risk-weighted formal coverage F(c) + expensive-claim policy (never label full "formally verified") | egmra/lean/coverage.py | REQ-092 | VERIFIED | RFC frozen blueprint + ExpensiveClaimPolicy; test_lean.py |
| REQ-09A | §9.6 | Aristotle routing + sandbox policy | egmra/lean/aristotle_routing.py | REQ-090 | VERIFIED | licensing gate + non-reproducible-if-unattested + quarantine pipeline; test_lean.py |

## Section 10 — Shared-state & provenance

| ID | Source | Requirement summary | Component | Deps | Status | Evidence |
|---|---|---|---|---|---|---|
| REQ-060 | §10.1 | Core graph entities (Problem, Interpretation, Claim full schema, Branch, Evidence, IntentCertificate, FormalCorrespondenceCertificate) + typed relations as first-class claims | egmra/truth/entities.py | REQ-004 | VERIFIED | all entities + Relation w/ evidence_profile; test_truth_plane.py |
| REQ-061 | §10.2 | Admission & revocation: proposals UNKNOWN empty; validator obligations; passed=true invalid; CONFLICTED; invalidate_evidence vs refute_claim; SCC transactional | egmra/truth/{validators,revocation}.py | REQ-060 | VERIFIED | Tarjan SCC; invalidate vs refute; CONFLICTED on hard-vs-hard; test_truth_plane.py |
| REQ-061b | §10.2 | Evidence router dispatch by 6 kinds (source/computation/informal/lean/counterexample/expert) w/ kind-specific obligations | egmra/truth/router.py | REQ-061 | VERIFIED | EvidenceRouter dispatch + revalidate; test_truth_plane.py |
| REQ-062 | §10.3 | Append-only audit log event schema (17 fields incl signature); dashboards disposable; event log + artifacts authoritative | egmra/truth/events.py | REQ-004 | VERIFIED | Event schema + HMAC sig + hash chain + tamper detection; test_truth_plane.py |
| REQ-063 | §10.4 | Checkpoint & resume (checkpoint contents + resume procedure 8 steps) | egmra/orchestrator/checkpoint.py | REQ-062 | VERIFIED | take_checkpoint + resume (chain verify, closure compare, invalidate, censored); test_orchestrator.py |
| REQ-064 | §10.5 | Provenance rules (6 rule kinds; hidden reasoning not provenance) | egmra/provenance/rules.py | REQ-062 | VERIFIED | check_provenance 5 kinds + hidden_reasoning_is_provenance=False; test_foundations.py |
| REQ-065 | §10.6 | Temp vs persistent memory table (7 memory kinds) | egmra/learning/memory.py | REQ-04A | VERIFIED | MEMORY_TABLE 7 kinds; test_learning.py |

## Section 11 — Adversarial verification protocol

| ID | Source | Requirement summary | Component | Deps | Status | Evidence |
|---|---|---|---|---|---|---|
| REQ-110 | §11.1 | Organizational independence (no shared scratchpad, fresh + diff family, rewarded for defects, cannot repair same pass, reports to auditor); diversity fields separate | egmra/verification/referee.py | REQ-009 | VERIFIED | DiversityProfile fields + reports_to auditor + repair raises; test_verification.py |
| REQ-111 | §11.2 | 10 required attacks + taint-aware graph | egmra/verification/attacks.py | REQ-110 | VERIFIED | REQUIRED_ATTACKS(10) + propagate_taint; test_verification.py |
| REQ-112 | §11.3 | Verification standards T0-T5 + orthogonal dims (I/F/N/S/R/autonomy); never collapse | egmra/verification/standards.py | REQ-070 | VERIFIED | truth_level T0-T5 + dims; lean_verified only T4+; test_verification.py |
| REQ-113 | §11.4 | Pessimistic aggregation; single central defect blocks; conflict flow; correlated consensus raises priority not tier | egmra/verification/aggregation.py | REQ-112 | VERIFIED | aggregate pessimistic + fresh adjudicator + priority-not-tier; test_verification.py |
| REQ-114 | §11.5 | Final ReleaseCertificate schema + signature; never collapsed to confidence % | egmra/release/certificate.py | REQ-112 | VERIFIED | ReleaseCertificate sign/verify/render profile; test_release.py |

## Section 12 — Evaluation plan

| ID | Source | Requirement summary | Component | Deps | Status | Evidence |
|---|---|---|---|---|---|---|
| REQ-130 | §12.1 | Seven difficulty levels + tracks A/B/C; training corpora not gold; benchmark versions in provenance | egmra/eval/levels.py | - | VERIFIED | 7 LEVELS + TRACKS + scores_accuracy; test_eval.py |
| REQ-131 | §12.2 | Protocol: freeze everything; dedup; ≥4 baselines; equalize cost or Pareto; preserve outcomes; formal by replay + informal by blind experts; separate novelty graders; calibration first; causal ablations; Level 6 time-capsule; Level 7 no accuracy | egmra/eval/protocol.py | REQ-130 | VERIFIED | FrozenEvalConfig+REQUIRED_BASELINES+CausalAblationSpec+TimeCapsule; test_eval.py |
| REQ-132 | §12.3 | Metrics: outcomes, progress, RFC (frozen blueprint+weights), search quality, efficiency, calibration | egmra/eval/metrics.py | REQ-131 | VERIFIED | metric dataclasses + rfc frozen blueprint; test_eval.py |
| REQ-133 | §12.4 | Progress vs verbose: progress only if durable object; tokens/agents/consensus zero | egmra/eval/progress.py | REQ-132 | VERIFIED | ProgressLedger durable-object gate; manuscript<counterexample; test_eval.py |
| REQ-134 | §12.5 | 13 required ablations + pre-registered metrics + stop conditions | egmra/eval/ablations.py | REQ-131 | VERIFIED | 13 REQUIRED_ABLATIONS + AblationRegistry; test_eval.py |
| REQ-135 | §12.6 | Statistical policy (denominators/intervals/censored; paired; no pass@1 vs pass@k; dev/eval separate; version benchmarks; blind ≥2 experts; preprints=hypotheses) | egmra/eval/stats.py | REQ-132 | VERIFIED | compare_pass_at_k guard + ReportedResult + dev_eval_separated; test_eval.py |

## Section 13 — Minimal viable implementation (M0/M1/M2 + acceptance)

| ID | Source | Requirement summary | Component | Deps | Status | Evidence |
|---|---|---|---|---|---|---|
| REQ-140 | §13.2 | 8 M0 safety/provenance patches | egmra/m0.py, egmra/policy, patched aristotle_verifier+promote_verified_run | REQ-020g | VERIFIED | PromotionGuard+evidence_precedence+legacy quarantine+telemetry; aristotle require_kernel; promote enforces policy; test_m0_safety.py + 179 baseline green |
| REQ-141 | §13.3 | M1 end-to-end vertical slice | egmra/* | REQ-140 | VERIFIED | research() finite-claim -> compute -> SUPPORTED -> proof -> gates; test_orchestrator.py, test_eval.py |
| REQ-142 | §13.4 | M2 scalable MVP (interfaces + local backends) | egmra/m2.py + planes | REQ-141 | VERIFIED | EventStore contract + ContentAddressedObjectStore + PostgresEventStore iface + M2Assembly; test_m2_scale.py |
| REQ-143 | §13.5 | Runtime role layout (4 concurrent roles; services) | egmra/orchestrator/roles.py | REQ-141 | VERIFIED | RoleLayout 4 roles + 5 services; test_orchestrator.py |
| REQ-144 | §13.6 | 18 acceptance tests (spec lists 18) | egmra/tests/test_acceptance.py | REQ-141 | VERIFIED | all 18 §13.6 acceptance tests pass; test_acceptance.py |
| REQ-145 | §13.7 | Evaluation set (fixtures/manifests) | egmra/eval/datasets.py | REQ-130 | VERIFIED | EVAL_SET_COMPOSITION + executable FIXTURE_PROBLEMS + PINNED_BENCHMARKS; test_eval.py |

## Section 14 — Full-scale implementation

| ID | Source | Requirement summary | Component | Deps | Status | Evidence |
|---|---|---|---|---|---|---|
| REQ-160 | §14.1 | Service topology registry (10 layers) + health | egmra/topology.py | many | VERIFIED | TOPOLOGY_LAYERS(10) + ServiceTopology; test_meta.py |
| REQ-161 | §14.2 | Model assignments via local bake-off then pin; never vendor benchmark; persist exact identity | egmra/models/registry.py | REQ-012 | VERIFIED | ModelRegistry.pin_best refuses unattested; test_meta.py |
| REQ-162 | §14.3 | Parallelization policy (parallelize independent; serialize approval/promotion/schema/assembly/release/quota; compatible work stealing; reserved verifier pool) | egmra/control/parallel.py | REQ-020c | VERIFIED | can_parallelize/must_serialize + VerifierPool reserve; test_control.py |
| REQ-163 | §14.4 | QD archive of 12 research-program families; governor instantiates compatible; each has falsifier/budget/kill | egmra/search/programs.py | REQ-084 | VERIFIED | 12 METHOD_FAMILIES + instantiate_programs + QualityDiversityArchive; test_search.py |
| REQ-164 | §14.5 | Failure recovery table (13 rows) | egmra/control/recovery.py | REQ-08A | VERIFIED | RECOVERY_TABLE 13 rows + truth_effect; test_control.py |
| REQ-165 | §14.6 | Compute bottleneck mitigations (8) | egmra/control/congestion.py | REQ-08A | VERIFIED | congestion pricing + CongestionController (scheduling not truth); test_control.py |
| REQ-166 | §14.7 | Human role: record every intervention; humans required for 7 responsibilities | egmra/comms/human.py | REQ-062 | VERIFIED | InterventionLog + HUMAN_RESPONSIBILITIES(7); test_meta.py |

## Section 15 — Risks

| ID | Source | Requirement summary | Component | Deps | Status | Evidence |
|---|---|---|---|---|---|---|
| REQ-170 | §15 | Risk register (17 general + 7 innovation) w/ actionable mitigation links | egmra/risks.py + DECISIONS.md | many | VERIFIED | 24 risks w/ mitigation_component links; test_meta.py |

## Section 16 — Prioritized recommendations (roadmap)

| ID | Source | Requirement summary | Component | Deps | Status | Evidence |
|---|---|---|---|---|---|---|
| REQ-180 | §16 P0 | Stop false promotion + complete execution identity (11 items) — superset of M0 | see REQ-140,012,090 | REQ-140 | VERIFIED | covered by REQ-140/012/090/020h/061/062; test_m0_safety.py + test_acceptance.py |
| REQ-181 | §16 P1 | Build truth + experiment planes (7 items) | see REQ-004,040,047,090,043,050,070 | REQ-141 | VERIFIED | all component reqs VERIFIED; egmra/tests/* |
| REQ-182 | §16 P2 | Replace fixed loop w/ research search (5 items) | see REQ-025,084,024,081,028 | REQ-141 | VERIFIED | all component reqs VERIFIED; test_search.py/test_agents.py |
| REQ-183 | §16 P3 | Calibrate/learn/scale (7 items) | see REQ-131,04A,081,134,142 | REQ-142 | VERIFIED | eval harness + learning + acquisition + ablations + M2; egmra/tests/* |

---

## Implementation order (dependency-sorted)

1. Foundations: `egmra/provenance/hashing.py`, `egmra/policy/feature_policy.py` (REQ-020g/140), `egmra/provenance/stage_identity.py` (REQ-012/020b)
2. Truth plane: entities (REQ-060) → events (REQ-062) → graph/store (REQ-004/029) → validators+router (REQ-061/061b) → revocation SCC (REQ-061) → blackboard (REQ-031)
3. Intake: Statement IR (REQ-040) → interpretation lattice (REQ-002/020m) → integrity probes → ProblemContract
4. Corpus/status hygiene (REQ-050)
5. Retrieval: TheoremRecord + packet (REQ-023/043/053) → premises (REQ-054) → source priority (REQ-055) → auditor
6. OEIS: transforms (REQ-051) → client → matching (REQ-052)
7. Compute: ExperimentSpec + sandbox + artifact + replay + certificate (REQ-008/047)
8. Lean: service API (REQ-097) → target package L0 (REQ-091) → sentinels L1 (REQ-092) → blueprint L2 (REQ-093) → proof-state L3 (REQ-094) → sync L4 (REQ-095) → hardening L5 (REQ-096) → missing-library (REQ-098) → coverage (REQ-099) → aristotle routing (REQ-09A) + patch aristotle_verifier (REQ-020/090)
9. Search/control: mechanism (REQ-084) → verified_debt (REQ-083) → blueprint (REQ-025) → dedup (REQ-085) → failure (REQ-086) → bands (REQ-088) → controller (REQ-006/081/082/087) → programs (REQ-163) → algorithms (REQ-046/080)
10. Agents: authorities + method profiles + prompts + diversity (REQ-044/024/020k)
11. Verification: referee (REQ-110) → attacks (REQ-111) → standards (REQ-112) → aggregation (REQ-113)
12. Release: gates (REQ-001/070) → certificate (REQ-114) → compiler (REQ-026) → policy (REQ-011)
13. Selection: posterior (REQ-041) → acquisition (REQ-081) → protected exploration (REQ-022)
14. Learning/memory: 6 stores (REQ-04A/065/010)
15. Control extras: leases (REQ-020c) → parallel (REQ-162) → recovery (REQ-164) → congestion (REQ-165)
16. Orchestration: roles (REQ-143) → loop (REQ-032/089) → checkpoint (REQ-063)
17. Comms/meta: human (REQ-166), design_status (REQ-033), services (REQ-04B), topology (REQ-160), models (REQ-161), risks (REQ-170)
18. Eval: levels (REQ-130) → protocol (REQ-131) → metrics (REQ-132) → progress (REQ-133) → ablations (REQ-134) → stats (REQ-135) → datasets (REQ-145)
19. M0 patches to existing files + acceptance tests (REQ-140/144) + M1/M2 integration (REQ-141/142)
20. Final: get_errors, full test run, FINAL_VERIFICATION_REPORT.md

## Notes / blockers
- External-credential integrations (real OEIS HTTP, real Lean/Mathlib build, real
  provider model calls, Aristotle CLI, Postgres/containers) get real interface +
  config + validation + local/mock tests + documented real-cred command. The live
  external call is NOT claimed VERIFIED; interface+local test IS.
