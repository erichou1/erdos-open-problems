# Phase 1 normative-requirement inventory — authoritative specification sections 1–9

Scope: only `docs/AUTONOMOUS_MATH_RESEARCH_ARCHITECTURE_2026.md`, lines 1–1418 (through section 9.6). IDs are temporary `S…` identifiers, not final requirement IDs. “Failure” records required fail-closed, downgrade, pause, quarantine, or non-claim behavior; “Acceptance” is the externally observable condition that would demonstrate implementation.

## Sections 1–3: objectives, binding evidence limits, and evaluation constraints

### S1 — Optimize for rigorous research, with explicit evidence semantics

- **Source:** Preamble, lines 1–16. **Category:** implementation / evaluation / acceptance. **Summary:** The system must maximize rigorous, intended, novel, reproducible mathematical progress, treating cost as subordinate; it must label support as established, demonstrated, plausible, or original, and test original proposals. “Lean-verified” means only kernel acceptance of a specified encoding/environment.
- **Inputs → outputs:** Research artifacts and supporting evidence → support label and evidence-profiled result. **Invariants:** Kernel acceptance never implies informal correspondence, novelty, or significance. **Failure:** Unsupported stronger claims are downgraded/rejected. **Integrations:** Evaluation ledger, Lean certificates, release gates. **Acceptance:** Every released claim exposes its support/evidence class and no Lean-only artifact is advertised as intended/novel/significant without separate evidence. **Dependencies:** Five-gate release. **Ambiguity:** “Maximize probability” has no numeric objective here.

### S2 — Maintain five independent release gates

- **Source:** §1, lines 20–35. **Category:** architecture / security / acceptance. **Summary:** The research OS must independently gate statement fidelity, truth, novelty, significance, and reproducibility; no single model, flat debate, or enlarged agent census is an adequate substitute.
- **Inputs → outputs:** Candidate result plus source, proof, literature, significance, and replay evidence → five separate gate decisions. **Invariants:** A positive gate cannot imply another gate. **Failure:** Any unresolved required gate prevents a “solved” promotion and must remain explicitly unresolved. **Integrations:** Intake, truth plane, novelty auditor, referee, artifact replay. **Acceptance:** Gate records are separately inspectable and support mixed statuses such as formally true/novelty unresolved. **Dependencies:** S1. **Ambiguity:** Exact minimum evidence per gate is specified later, especially outside this line range.

### S3 — Use the composite evidence-gated architecture

- **Source:** §1, lines 36–46. **Category:** architecture / integration / security. **Summary:** Implement immutable source plus an interpretation lattice; a short literature-blind falsification pass followed by mandatory theorem-level literature/OEIS/formal-library retrieval; an append-only typed claim graph with dependencies, contradictions, and cascading revocation; nested program/lemma/Lean search; posterior/VOI allocation with protected exploration; early Lean sentinels; replayable executable experiments; an agreement-neutral adversarial referee; and verified-only persistent memory.
- **Inputs → outputs:** Frozen problem source and budget → evidence-gated proof/disproof/partial/no-result artifacts. **Invariants:** Truth status changes only through typed evidence; revocation propagates; persistent learning is verified. **Failure:** Unreplayed, correlated, mutable, or weak evidence cannot promote. **Integrations:** All EGMRA planes and services. **Acceptance:** End-to-end traces exhibit every listed mechanism and independent gate. **Dependencies:** S1–S2. **Ambiguity:** This is a design hypothesis and needs ablation (S28).

### S4 — Close the two urgent provenance defects before promotion uses formal or cross-model evidence

- **Source:** §1 “Assessment,” lines 48–70. **Category:** security / failure / integration. **Summary:** Vendor-reported Aristotle completion without local kernel replay and approved statement fidelity, and cache reuse not bound to actual stage runner/adjudicator provenance, must both be closed before formal evidence or claimed cross-model independence can affect promotion.
- **Inputs → outputs:** Formal sidecars, cached stage artifacts, current/cached runner identity → validated evidence or incompatibility rejection. **Invariants:** Evidence qualifications survive loading; manifest provenance derives from the producing artifact, not current object identity. **Failure:** Missing kernel/fidelity or identity mismatch rejects promotion/cache replay. **Integrations:** Aristotle adapter, evidence loader, cache, adjudication, manifests. **Acceptance:** Regression cases for vendor-only `COMPLETE` and changed-runner cached adjudication fail closed. **Dependencies:** Stage identity and formal certificates. **Ambiguity:** No migration rule for old artifacts is given here.

### S5 — Require local kernel replay and statement-fidelity approval for formal promotion

- **Source:** §1 “Highest-priority decisions,” line 74. **Category:** security / acceptance. **Summary:** Formal promotion requires both local kernel replay and statement-fidelity approval.
- **Inputs → outputs:** Formal candidate, pinned environment, fidelity certificate → promotable formal evidence. **Invariants:** Neither vendor status nor compilation alone suffices. **Failure:** Missing/failed replay or fidelity approval blocks formal promotion. **Integrations:** Lean verifier, target audit, release gate. **Acceptance:** Promotion API cannot accept a certificate lacking either condition. **Dependencies:** S2, S4. **Ambiguity:** Detailed certificate shape appears in §9.

### S6 — Disable promotion until semantic validators and release flags are enforced

- **Source:** §1 “Highest-priority decisions,” line 75. **Category:** security / release engineering. **Summary:** All promotion entry points must remain disabled until every evidence kind has a semantic validator and release flags are centrally enforced.
- **Inputs → outputs:** Evidence kind, validator registry, feature policy → enabled/disabled promotion decision. **Invariants:** No generic caller-controlled `passed` path. **Failure:** Missing validator or disabled flag rejects promotion. **Integrations:** Evidence router, all verifiers/promoters/schedulers. **Acceptance:** Enumerating evidence kinds shows a registered validator and policy check for each. **Dependencies:** S4. **Ambiguity:** Evidence-kind registry is not enumerated here.

### S7 — Bind stage identity completely and reject incompatible cache replay

- **Source:** §1 “Highest-priority decisions,” line 76. **Category:** provenance / security / failure. **Summary:** Every stage contract must bind actual provider/model/runner, adjudicator and literature policy, formal environment, validator version, prompt, tools, and artifacts; incompatible cache replay must be rejected.
- **Inputs → outputs:** Complete runtime/stage fingerprint and cached artifact fingerprint → compatible hit or rejection. **Invariants:** Caller labels do not attest identity. **Failure:** Any behavior-relevant mismatch invalidates reuse. **Integrations:** Run contracts, cache, manifests, adapters. **Acceptance:** Mutating any bound field causes a cache miss/rejection and preserves original provenance. **Dependencies:** S4. **Ambiguity:** “Actual” provider attestation mechanism is unspecified.

### S8 — Preserve and extend conservative repository invariants

- **Source:** §1 “Highest-priority decisions,” line 77. **Category:** integration / regression. **Summary:** Preserve and extend source snapshots, queue behavior, compatible cache machinery, and deterministic rejection while replacing deficient semantics.
- **Inputs → outputs:** Existing provenance/control mechanisms plus new contracts → backward-safe extended mechanisms. **Invariants:** Conservative rejection and compatible-only reuse do not regress. **Failure:** Extensions must not silently loosen existing fail-closed behavior. **Integrations:** Intake, scheduler, cache, gate. **Acceptance:** Legacy invariant regression tests remain valid under the extended schemas. **Dependencies:** S7. **Ambiguity:** Compatibility/migration policy is deferred.

### S9 — Replace mutable proof/manifests with typed graph and append-only events

- **Source:** §1 “Highest-priority decisions,” line 78. **Category:** state / provenance / failure. **Summary:** Mutable whole-proof/manifests must be replaced by a typed claim graph and append-only gate, adjudication, and promotion events.
- **Inputs → outputs:** Claim/evidence/decision proposals → immutable events and derived views. **Invariants:** Authoritative history is append-only; manifests are projections. **Failure:** Conflicting later decisions append superseding events rather than overwrite history. **Integrations:** Claim graph, event store, checkpoint/resume, release. **Acceptance:** Full state can be reconstructed and prior decisions remain inspectable. **Dependencies:** S3. **Ambiguity:** Event schemas are specified later, beyond this audit range.

### S10 — Replace the fixed inner loop with hierarchical search

- **Source:** §1 “Highest-priority decisions,” line 79. **Category:** architecture / search. **Summary:** Replace the fixed scout/synthesis/whole-proof loop with research-program search and AND/OR claim/lemma search.
- **Inputs → outputs:** Locked problem and program proposals → diverse program archive and dynamic proof blueprint. **Invariants:** Multiple mechanisms survive until evidence resolves bottlenecks. **Failure:** A failed whole proof cannot erase viable branches. **Integrations:** Controller, claim graph, formal proof-state search. **Acceptance:** Branch traces expose program and AND/OR levels with local dependencies. **Dependencies:** S3. **Ambiguity:** Algorithm mix is specified in §7.

### S11 — Add executable falsification and high-risk Lean sentinels before agent scaling

- **Source:** §1 “Highest-priority decisions,” line 80. **Category:** implementation / safety / sequencing. **Summary:** Executable falsification and risk-targeted Lean sentinels precede scaling agent count.
- **Inputs → outputs:** Target, boundary cases, risky claims → replayable counterexample/probe artifacts and early formal checks. **Invariants:** More agents do not compensate for absent hard feedback. **Failure:** Deep scaling is withheld when these services are unavailable. **Integrations:** Computation plane, Lean, controller. **Acceptance:** Budget escalation records completed falsification and sentinel work. **Dependencies:** Intake integrity. **Ambiguity:** “Scaling” threshold is unspecified.

### S12 — Build frozen theorem-level packets after a protected cold pass

- **Source:** §1 “Highest-priority decisions,” lines 81–82. **Category:** retrieval / control / evaluation. **Summary:** Build frozen theorem-level literature packets including OEIS and formal declarations; literature search is mandatory before deep proof work, while 5–10% of the initial budget is reserved for a blind scratch/falsification pass.
- **Inputs → outputs:** Problem/interpretations and cold hypotheses → immutable source packet and improved queries. **Invariants:** Cold output is not a publication claim; deep work sees retrieved evidence. **Failure:** Missing packet blocks deep search. **Integrations:** Literature, OEIS, theorem DB, controller. **Acceptance:** Run ledger records the cold fraction, information boundary, packet hash, and retrieval completion. **Dependencies:** S3. **Ambiguity:** Pseudocode later uses exactly 5%, within the 5–10% range.

### S13 — Treat proprietary provers only as candidate workers

- **Source:** §1 “Highest-priority decisions,” line 83. **Category:** trust / security. **Summary:** Aristotle and other proprietary provers may generate candidates but can never be trust roots.
- **Inputs → outputs:** External prover output → quarantined candidate requiring local validation. **Invariants:** Trusted evidence derives from local kernel/certificate checks. **Failure:** Status-only output is rejected as proof evidence. **Integrations:** External-service adapter, sandbox, Lean verifier. **Acceptance:** No trust policy lists a proprietary service as final checker. **Dependencies:** S5. **Ambiguity:** None material.

### S14 — Learn only from authenticated replayable, pipeline-matched outcomes

- **Source:** §1 “Highest-priority decisions,” line 84, and §7.1, lines 803–809. **Category:** learning / security. **Summary:** Persistent learning must use only authenticated, replayable, pipeline-matched outcomes; model consensus is correlated testimony, not independent evidence, and learned value functions are used only after enough such outcomes exist.
- **Inputs → outputs:** Outcome artifacts and provenance → admitted calibration/procedural memory or quarantine. **Invariants:** Consensus cannot elevate truth tier. **Failure:** Unauthenticated/unreplayable outcomes are excluded from learning. **Integrations:** Memory, evaluator, replay service. **Acceptance:** Training/calibration datasets contain evidence and pipeline fingerprints for every row. **Dependencies:** S1, S3. **Ambiguity:** Authentication authority is not defined here.

### S15 — Evaluate against an equal-cost raw frontier-model baseline

- **Source:** §1 “Highest-priority decisions,” line 85. **Category:** evaluation / acceptance. **Summary:** EGMRA evaluation must compare with a raw frontier-model baseline at equal cost, use blind expert review, and replay formal artifacts under versioned environments.
- **Inputs → outputs:** Matched problem set, cost policy, baseline/system outputs → blinded comparative metrics and replay reports. **Invariants:** Architecture gains cannot be attributed to unequal budgets or unblinded grading. **Failure:** Unmatched/unblinded/unversioned comparisons are non-conclusive. **Integrations:** Benchmark harness, cost ledger, expert panel, formal replay. **Acceptance:** Published evaluation exposes matching, blindness, versions, and costs. **Dependencies:** S1. **Ambiguity:** “Equal cost” normalization is not defined in sections 1–9.

### S16 — Do not equate technical correctness with fidelity or significance

- **Source:** §2.1 “Aletheia,” lines 91–97. **Category:** evaluation / release / failure. **Summary:** Correctness review must separately detect vacuous, misread, already-known, or insignificant answers; technical correctness alone cannot satisfy intendedness or significance.
- **Inputs → outputs:** Candidate, locked statement, status/literature, significance rubric → separate classifications. **Invariants:** Correct-but-unresponsive outcomes are not full resolutions. **Failure:** Vacuity/misreading/rediscovery is downgraded and explicitly labeled. **Integrations:** Intent, novelty, significance gates. **Acceptance:** Evaluation confusion matrix includes these false-direction classes. **Dependencies:** S2. **Ambiguity:** Significance rubric is later policy-dependent.

### S17 — Treat same-lineage critics and councils as correlated search controls, not truth oracles

- **Source:** §2.1 “QED,” lines 99–105, and “ProofCouncil/RMA,” lines 151–157. **Category:** trust / evaluation. **Summary:** Selected verifier-positive samples do not establish false-positive bounds; same-lineage judgments are correlated, false negatives must be measured, and critics/councils may control search but cannot certify truth without independent reproduction.
- **Inputs → outputs:** Model reviews/council votes and expert outcomes → correlation-aware evaluation records. **Invariants:** Vote count does not become evidence independence. **Failure:** Unsupported critic acceptance remains unverified; critic rejection is not automatically final. **Integrations:** Referee, evaluation harness, truth gate. **Acceptance:** Reports identify lineage and measure both false positives and false negatives. **Dependencies:** S14. **Ambiguity:** Independence threshold is not quantified.

### S18 — Do not infer architecture quality from closed, uncontrolled, uncapped, or one-off results

- **Source:** §2.1, lines 107–117, 125–143, and 165–171; §2.2, lines 173–181; and §3 comparison table, lines 272–299. **Category:** evaluation / reporting. **Summary:** Closed-system, uncontrolled, human-selected, uncapped/extreme/high-compute, provider-reported, benchmark-drifted, or one-off successes establish capability context at most; they cannot support reproducibility, practical-default, solve-probability, or architecture claims. Comparator limitations—including manual targets, varying underlying models, dependence on a hard evaluator/skeleton, and a low thoroughly-checked denominator—remain explicit. Missing architecture must not be guessed, and verifier-backed discoveries may still need self-contained proof/significance audit.
- **Inputs → outputs:** External result claims and disclosed protocol → appropriately scoped evidence statement. **Invariants:** Claims do not exceed disclosed controls/artifacts. **Failure:** Overclaiming is rejected/downgraded. **Integrations:** Literature map, evaluation report. **Acceptance:** Every comparator claim states closure, budget, review, drift, and replay limitations. **Dependencies:** S1. **Ambiguity:** “Enough disclosure” is not formalized.

### S19 — Strengthen fact-graph admission for central claims and support revocation

- **Source:** §2.1 “Danus,” lines 119–123. **Category:** truth state / failure. **Summary:** A fact graph must survive domain mismatches and bad imported definitions through evidence-typed admission and downstream revocation; LLM-only admission is too weak for high-centrality facts.
- **Inputs → outputs:** Proposed/imported claim, dependencies, validating evidence → admitted tier or rejection; refutation → affected closure. **Invariants:** Centrality does not relax evidence requirements. **Failure:** Invalid source facts revoke all dependent claims. **Integrations:** Import auditor, claim graph, controller. **Acceptance:** Injected bad-definition and wrong-domain cases trigger complete dependency closure invalidation. **Dependencies:** S3. **Ambiguity:** Exact centrality threshold is later policy.

### S20 — Use lightweight generation as a cheap baseline, never as final verification

- **Source:** §2.1 “lightweight pipeline,” lines 145–149. **Category:** evaluation / architecture. **Summary:** Citation-bearing lightweight generation may serve as a cheap candidate baseline and inform a verification-cost model, but citation presence does not establish theorem applicability and the wrapper is not the final architecture or formal verification.
- **Inputs → outputs:** Generated candidate/citations and checking cost → baseline candidate plus audited applicability/cost record. **Invariants:** Citations are leads until exact hypotheses are checked. **Failure:** Unchecked candidates remain unverified. **Integrations:** Baseline harness, import auditor, cost model. **Acceptance:** Baseline and verification time/cost are reported separately. **Dependencies:** S15. **Ambiguity:** None material.

### S21 — Require semantic target audit plus clean pinned independent replay for formal artifacts

- **Source:** §2.2 “Aristotle” and “AXLE,” lines 183–197. **Category:** formal security / acceptance. **Summary:** Vendor completion or formal artifact acceptance proves only the encoded theorem; research-level formal evidence requires local build, semantic target audit, clean pinned replay, and an independent checker for untrusted generated metaprogramming.
- **Inputs → outputs:** Formal target/source, environment, generated artifact → correspondence certificate and independently replayed formal certificate. **Invariants:** Manual target dependency remains explicit. **Failure:** Missing audit/replay/checker blocks release. **Integrations:** Lean service, sandbox, target-fidelity gate. **Acceptance:** Released formal artifact builds in pinned clean context and passes distinct checker with approved correspondence. **Dependencies:** S5, S13. **Ambiguity:** “Independent checker” may share Lean’s logical kernel; trust paths must be disclosed.

### S22 — Score formal evolution by target-relative verified-debt reduction

- **Source:** §2.2 “AlphaProof Nexus,” lines 191–195. **Category:** search / security / evaluation. **Summary:** Formal/evolutionary fitness must measure target-relative verified-debt reduction, not plausibility or elegance, so moving all difficulty into a `sorry`-shaped helper or hallucinated literature lemma earns no credit.
- **Inputs → outputs:** Before/after formal obligation graph → debt delta and branch fitness. **Invariants:** New helper obligations and import/correspondence debt count. **Failure:** Restating/hiding the target yields zero or negative credit. **Integrations:** Formal blueprint, claim graph, controller. **Acceptance:** Adversarial helper-restatement tests cannot improve fitness. **Dependencies:** S10. **Ambiguity:** Full debt formula appears in §7.3.

### S23 — Make formal-system comparisons matched, versioned, and contamination-audited

- **Source:** §2.2 “open formal agents,” lines 199–212. **Category:** evaluation / provenance. **Summary:** Formal comparisons must state exact benchmark commit, pass@k, token/tool budget, and Mathlib version; very large/unequal pass@k and synthetic mutations require matched-budget reruns and contamination audits. Retrieval remains a proposal source, never proof.
- **Inputs → outputs:** System runs, benchmark/toolchain fingerprints, retrieval candidates → reproducible comparison and audited evidence. **Invariants:** Different budgets/versions are not collapsed into one score. **Failure:** Missing protocol metadata makes comparison non-controlled; retrieved premises require elaboration/proof. **Integrations:** Benchmark harness, theorem retrieval, replay. **Acceptance:** Comparison records contain every required field and contamination assessment. **Dependencies:** S15. **Ambiguity:** Contamination audit method is unspecified.

### S24 — Implement a translation firewall for autoformalization

- **Source:** §2.3, lines 214–226. **Category:** semantic security / evaluation. **Summary:** Autoformalization is a semantic bottleneck; use multiple candidate translations, independent backtranslation, counterexample/vacuity tests, global paraphrase invariance, local mutation covariance, formal equivalence when feasible, and an independently approved target hash before proof promotion. The firewall is an original proposal requiring ablation.
- **Inputs → outputs:** Informal statement/paraphrases/mutations → candidate formal targets, test reports, approved hash. **Invariants:** Compilation rate is not semantic accuracy. **Failure:** Unresolved correspondence blocks intended-target promotion. **Integrations:** Intake, Lean target package, falsifier, evaluation. **Acceptance:** Firewall test corpus includes meaning-preserving and meaning-changing variants and reports ablation impact. **Dependencies:** S5. **Ambiguity:** Approval authority and pass thresholds are unspecified.

### S25 — Restrict evolutionary promotion to hard-evaluator domains

- **Source:** §2.4, lines 228–240. **Category:** search / security / acceptance. **Summary:** Evolve constructions, algorithms, decompositions, counterexample generators, or formal proof programs only when fitness is exact/certificate-backed, an independent checker exists, novelty and complexity are separate objectives, mechanism diversity is preserved, and winners are replayed outside search; never evolve unrestricted prose proofs under an LLM judge for promotion.
- **Inputs → outputs:** Executable candidates, evaluator/checker, population → independently replayed winner plus separate objective scores. **Invariants:** Hard evaluation and diversity are mandatory. **Failure:** Missing checker/certificate/replay restricts output to speculative search, not promotion. **Integrations:** Evolution islands, computation, novelty. **Acceptance:** Promotion validator checks all five preconditions. **Dependencies:** S3. **Ambiguity:** “Exact” includes certificate-backed evaluators but trusted checker scope must be declared.

### S26 — Route suitable leaves to symbolic solvers with semantic preservation and checked closure

- **Source:** §2.5, lines 242–253. **Category:** integration / formal security. **Summary:** Mature ATP/SAT/SMT/proof systems should solve supported leaves; exported obligations must preserve semantics, and success must be reconstructed in Lean or attached as a checked proof/model/certificate. A solver status label is insufficient.
- **Inputs → outputs:** Source claim, translated obligation, premises → proof/model/certificate and checked reconstruction. **Invariants:** Translation obligations remain linked to the source claim. **Failure:** Status-only or mistranslated results remain solver testimony. **Integrations:** Lean, Isabelle/Rocq/HOL/Metamath, E/Vampire, SAT/SMT. **Acceptance:** Every accepted solver result has checked closure and translation audit. **Dependencies:** S21. **Ambiguity:** Certificate support differs by solver.

### S27 — Apply benchmark-specific provenance and separate pipeline-stage evaluation

- **Source:** §2.6, lines 255–270. **Category:** evaluation / provenance. **Summary:** Use corrected formalization benchmarks where available; do not treat training corpora as gold research tests; record factored-answer policy, pass@k/tool budget, benchmark commits/versions, formal statement versus submitted-solution provenance, and benchmark corrections. Verifier-backed “solves” may need proof/significance audit; historical solved Erdős problems behind dated snapshots are the internal retrospective test, while currently unsolved problems are deployment, not labeled benchmarks. No single accuracy may collapse parsing, retrieval, novelty, proof, and formalization.
- **Inputs → outputs:** Versioned benchmark corpus and stage outputs → stage-specific metrics and provenance. **Invariants:** Benchmark drift and semantic simplifications remain visible. **Failure:** Mixed-version/single-score claims are invalidated. **Integrations:** Evaluation suite, formal replay, expert audit. **Acceptance:** Reports expose per-stage metrics and exact corpus lineage. **Dependencies:** S15, S24. **Ambiguity:** Section 12, outside scope, defines final metric suite.

### S28 — Treat EGMRA as unmeasured until controlled ablations support it

- **Source:** §3 “Architecture alternatives,” lines 300–315, and §5.3, lines 466–481. **Category:** evaluation / governance. **Summary:** The hybrid is a preferred design hypothesis, not a measured winner; performance claims must be earned through ablations separating search-uncertainty mechanisms from truth-uncertainty mechanisms. Support status must remain attached to each choice: kernel validation is established only within the encoding; several loops/retrieval/blueprints are demonstrated; the cold pass, interpretation lattice, risk sentinels, epistemic compiler, posterior allocation, and novelty firewall remain plausible/original where so labeled.
- **Inputs → outputs:** EGMRA and component-disabled variants → controlled outcome, cost, rigor, and failure-detection comparisons. **Invariants:** Target qualities labeled “target” or “unmeasured” cannot be reported as achieved. **Failure:** No-ablation results remain hypotheses. **Integrations:** Evaluation harness and feature policy. **Acceptance:** Each original integration has a controlled ablation with matched conditions. **Dependencies:** S15. **Ambiguity:** Required ablations reside in §12, outside this extraction.

## Section 4: binding audit conclusions and migration requirements

### S29 — Audit implementation and aspirational specification as different objects

- **Source:** §4.1, lines 317–330. **Category:** audit / evaluation / acceptance. **Summary:** The live implementation and ambitious target specification must be assessed separately; passing software tests establishes consistency, not theorem performance, and identity-incomplete rejected manifests/resource-exhaustion text are not authenticated solutions or normalized outcomes.
- **Inputs → outputs:** Code/test results, specs, manifests, raw text → separately scoped audit findings and authenticated outcome labels. **Invariants:** Aspirational features are not credited as implemented; raw candidate prose cannot normalize operational status. **Failure:** Identity-incomplete artifacts remain rejected/unclassified. **Integrations:** Audit, manifest schema, outcome writer. **Acceptance:** Capability claims link to executable evidence, and no legacy manifest is counted as a solve. **Dependencies:** S1. **Ambiguity:** Snapshot counts are time-specific, not permanent acceptance values.

### S30 — Retain source provenance but replace semantic intake

- **Source:** §4.2 source-intake row, line 336. **Category:** implementation / semantic security. **Summary:** Keep commit-pinned corpus/raw/section hashes and fail-closed extraction, but add Statement IR, two independent parses, reconciliation, semantic mutation tests, and explicit interpretations instead of regex semantics or copying raw text as intent.
- **Inputs → outputs:** Pinned source and context → typed, tested ProblemContract and interpretation lattice. **Invariants:** Byte-level lock remains. **Failure:** Unresolved ambiguity is explicit and blocks intended release. **Integrations:** Intake, falsifier, target audit. **Acceptance:** Dual parsing and mutation tests run on every promotable target. **Dependencies:** S24. **Ambiguity:** Parser independence standard is detailed in §6.1.

### S31 — Replace selector pseudo-probabilities with calibrated competing-risk acquisition

- **Source:** §4.2 selector row, line 337. **Category:** control / evaluation. **Summary:** Retain queue provenance/protected exploration while replacing hand-tuned pseudo-probabilities with standardized probes, competing-risk posteriors, censored outcomes, value of information, reuse, OEIS/library coverage, and actual telemetry.
- **Inputs → outputs:** Features, probes, authenticated/censored outcomes and costs → uncertainty-aware acquisition/allocation. **Invariants:** Timeout/rate limit is not math failure. **Failure:** Insufficient data yields wide intervals/weak priors, not false precision. **Integrations:** Queue, telemetry, retrieval, computation/formal coverage. **Acceptance:** Selector reports calibrated outcome intervals and protected allocation. **Dependencies:** S14. **Ambiguity:** Model family is implementation-selectable.

### S32 — Merge local recall into frozen theorem-level retrieval

- **Source:** §4.2 related-work row, line 338. **Category:** retrieval / novelty / integration. **Summary:** Retain hashed local related-work recall as stage zero, but merge it into theorem-level retrieval with exact hypotheses, external papers, citation graph, Mathlib, OEIS, immutable source spans, and applicability checks.
- **Inputs → outputs:** Local snippets plus external/formal sources → frozen audited theorem records. **Invariants:** Local untrusted snippets never satisfy novelty or theorem applicability. **Failure:** Unaudited records remain query leads. **Integrations:** Literature, theorem DB, OEIS, novelty auditor. **Acceptance:** Solver packet hashes full theorem records and scope checks. **Dependencies:** S12. **Ambiguity:** Access constraints must be represented later.

### S33 — Dynamically dispatch mechanism-distinct workers and attest model identity

- **Source:** §4.2 scouts row, line 339. **Category:** multi-agent / provenance. **Summary:** Replace a fixed same-runner scout census with dynamically dispatched workers differentiated by tool/information/mechanism; attest exact provider/model/runner identity.
- **Inputs → outputs:** Branch need, method/tool portfolio, identity attestations → distinct worker leases and structured proposals. **Invariants:** Role names alone do not create independence. **Failure:** Same context/model work is marked correlated and cannot claim diversity. **Integrations:** Controller, run contracts, model router. **Acceptance:** Each branch records actual identity and at least the required mechanism/tool boundary. **Dependencies:** S7. **Ambiguity:** Provider attestation availability varies.

### S34 — Extend synthesis into a typed AND/OR blueprint

- **Source:** §4.2 synthesis-DAG row, line 340. **Category:** search / state / failure. **Summary:** Replace one-LLM JSON DAG and single-goal fallback with typed AND/OR claims, dynamic leaves, proof-debt accounting, evidence/revocation, and dependency-local repair.
- **Inputs → outputs:** Program proposals and admitted claims → validated formal blueprint. **Invariants:** Malformed planner output cannot silently collapse semantics. **Failure:** Invalid blueprint proposals are rejected or repaired without inventing a fallback proof plan. **Integrations:** Claim graph, controller, Lean. **Acceptance:** AND/OR validation covers cycles, edges, tiers, revocation, and dynamic leaves. **Dependencies:** S10, S22. **Ambiguity:** Exact blueprint schema is later.

### S35 — Demote whole-proof construction to admitted-claim compilation

- **Source:** §4.2 constructor row, line 341. **Category:** proof assembly / security. **Summary:** A whole-proof constructor may compile only admitted claims; retain multiple blueprints until bottlenecks close rather than prematurely collapsing uncertainty or repeating entire proofs.
- **Inputs → outputs:** Admitted claim graph and viable blueprints → proof candidate with dependency links. **Invariants:** Unverified claims do not silently become premises. **Failure:** Missing admitted dependency leaves explicit proof debt and prevents complete proof claim. **Integrations:** Claim graph, proof compiler, release. **Acceptance:** Every logically active sentence resolves to admitted evidence or explicit debt. **Dependencies:** S34. **Ambiguity:** Informal assembly tiers are later.

### S36 — Use reviews as tool-backed checks, not evidence by consensus

- **Source:** §4.2 reviewers row, line 342. **Category:** verification / trust. **Summary:** Retain adversarial roles as checks, but add executable falsification, source audit, formal replay, and a different-family referee; same-family sequential unanimity is correlated and cannot itself promote.
- **Inputs → outputs:** Candidate/source/artifacts → defect proposals, replays, and independent referee report. **Invariants:** Review votes do not create truth tier. **Failure:** Unsupported approval remains non-evidence; defects route to affected claims. **Integrations:** Falsifier, import auditor, Lean, referee. **Acceptance:** Verification traces include tools and lineage separation. **Dependencies:** S17. **Ambiguity:** Different-family availability may require explicit residual correlation.

### S37 — Localize regulator repair and allocate by posterior value

- **Source:** §4.2 regulator row, line 343. **Category:** control / failure recovery. **Summary:** Preserve the proof-failure versus plan-failure distinction, but repair only the failed dependency cone, archive branches, allocate posterior-based budget, and support explicit reopen rules rather than two fixed whole-proof revisions.
- **Inputs → outputs:** Failure certificate, dependency graph, cost/value posterior → local repair/pause/reopen action. **Invariants:** Unaffected verified work survives. **Failure:** Exhausted budget pauses rather than declares mathematical failure. **Integrations:** Controller, graph, archive. **Acceptance:** A leaf failure changes only its dependency closure and records rationale. **Dependencies:** S34. **Ambiguity:** Review count and thresholds are policy defaults.

### S38 — Replace mutable `ResearchState` with an event-sourced epistemic graph

- **Source:** §4.2 `ResearchState` row, line 344. **Category:** state / provenance. **Summary:** Represent claim tiers, contradictions, costs, provenance, attempts, failures, and revocation in append-only graph events; JSON may remain only as a derived view.
- **Inputs → outputs:** Structured claim/evidence/control events → reconstructable graph and projections. **Invariants:** Final theorem is not the only verified node; negative evidence persists. **Failure:** Corrupt/inconsistent views are regenerated from events rather than accepted as authority. **Integrations:** Event store, claim validators, checkpoints. **Acceptance:** Replay reconstructs identical graph/tier/revocation state. **Dependencies:** S9. **Ambiguity:** Schema appears in §10 outside scope.

### S39 — Close stage-cache behavior and actor identity

- **Source:** §4.2 cache row, line 345. **Category:** provenance / security / resume. **Summary:** Retain content-addressed caching but bind actual stage runner/model/provider/context and adjudicator, literature/formal/evidence policies, import/behavior closure, exact Lean context, and replay policy; add live proof-state cache only with complete keys.
- **Inputs → outputs:** Producing-stage fingerprint and candidate reuse context → compatible cache artifact or rejection. **Invariants:** Resume never invents cross-model independence. **Failure:** Missing/mismatched identity or behavior closure causes cache miss/recompute. **Integrations:** Run contracts, module fingerprints, Lean GoalCapsule. **Acceptance:** Identity/policy/module mutations invalidate cache deterministically. **Dependencies:** S7. **Ambiguity:** Import-closure computation mechanism is unspecified.

### S40 — Add leases and provider-aware throttling without math-failure conversion

- **Source:** §4.2 queue/rate-limiter row, line 346. **Category:** reliability / failure / integration. **Summary:** Preserve atomic claims and retry-budget protection for detected rate limits; add leases/heartbeats, `Retry-After`, jitter, provider quotas, legacy-claim migration, stale-artifact handling, and parallel execution. Rate limits pause and never terminate a mathematical branch.
- **Inputs → outputs:** Queue claim, provider response, lease/heartbeat → renewed/paused/retried/reclaimed task. **Invariants:** Rate-limit waits do not consume mathematical retries; cooldown cap remains 120 seconds. **Failure:** Stale leases are safely reclaimed; general failures are normalized separately. **Integrations:** Scheduler, provider state, event log. **Acceptance:** Fault-injection demonstrates no double claim and no math failure from throttling. **Dependencies:** S8. **Ambiguity:** Legacy migration rules are not specified.

### S41 — Add a sandboxed replayable computational-evidence service

- **Source:** §4.2 computation row, line 347. **Category:** computation / security / acceptance. **Summary:** Replace caller-controlled path/`passed` evidence with sandboxed immutable jobs, exact arithmetic and coverage specification, independent replay, typed classifications, and certificate validation.
- **Inputs → outputs:** Immutable experiment specification → artifact, replay report, classification/checker report. **Invariants:** Labels are validator-derived, not caller-trusted. **Failure:** Arbitrary path or unvalidated `passed=true` cannot satisfy evidence. **Integrations:** Computation plane, artifact store, evidence router. **Acceptance:** Tampered or unreplayable artifacts are rejected; exact evidence has coverage/checker records. **Dependencies:** S25. **Ambiguity:** Supported tools vary by deployment.

### S42 — Redesign Lean/Aristotle as kernel-checked, fidelity-audited evidence

- **Source:** §4.2 Lean/Aristotle row, line 348. **Category:** formal security / integration. **Summary:** Keep Aristotle only as candidate worker; require local kernel validation, target audit, pinned project, exhaustive source/placeholder/axiom/import scan, early central lemmas, and typed evidence. `lake build` alone is inadequate because `sorry` may pass.
- **Inputs → outputs:** Formal candidate/source tree/locked target → audited formal certificate or rejection. **Invariants:** Vendor `COMPLETE` and unreviewed correspondence never pass. **Failure:** Placeholders, unapproved axioms/imports, replay failure, or fidelity failure block promotion. **Integrations:** Lean service, Aristotle, target gate. **Acceptance:** Full-tree scans and local clean replay are mandatory promotion steps. **Dependencies:** S5, S21. **Ambiguity:** Exhaustive scan scope is made concrete in §9.

### S43 — Replace generic promotion evidence with five typed certificates

- **Source:** §4.2 promotion-gate row, line 349. **Category:** release / security / acceptance. **Summary:** Preserve deterministic hash binding, explicit rejection reasons, role/gap/import checks, but replace caller-controlled external `passed` labels and same-runner unanimity with semantic validators and separate truth, intent, novelty, significance, and replay certificates.
- **Inputs → outputs:** Candidate plus typed formal/computational/expert evidence → five independent signed decisions. **Invariants:** Correctness cannot collapse contribution axes. **Failure:** Invalid/generic evidence rejects deterministically with reasons. **Integrations:** Evidence router, release auditor, event log. **Acceptance:** Each evidence type has a semantic validator and each gate is independently queryable. **Dependencies:** S2, S6. **Ambiguity:** Signature authority is not defined in sections 1–9.

### S44 — Enforce one signed feature policy at every entry point

- **Source:** §4.2 release-flags row, line 350. **Category:** release engineering / security. **Summary:** Every verifier, promoter, scheduler, and cache must record and enforce the same signed feature/run policy; experimental Lean/external-evidence flags cannot be bypassed through standalone or overridden entry points.
- **Inputs → outputs:** Signed policy and requested operation → permitted operation with policy provenance or rejection. **Invariants:** No entry-point-specific flag interpretation. **Failure:** Disabled/missing/incompatible policy fails closed. **Integrations:** Scheduler, verification scripts, proof pipeline, cache, promotion API. **Acceptance:** Cross-entry-point tests show identical decisions and policy hash. **Dependencies:** S6. **Ambiguity:** Signing/key management is unspecified.

### S45 — Make manifests derived views with explicit decision precedence

- **Source:** §4.2 manifest/adjudication row, line 351. **Category:** provenance / state / failure. **Summary:** Stop overwriting authoritative manifests; append immutable gate/adjudication/promotion events and define explicit precedence, including formal-versus-referee conflicts and cache provenance.
- **Inputs → outputs:** Decision events → derived current manifest and full history. **Invariants:** No in-place loss of prior state. **Failure:** Conflicts remain visible and resolve only through declared precedence/supersession events. **Integrations:** Event store, adjudicator, release. **Acceptance:** Reprojection is deterministic and preserves every prior decision. **Dependencies:** S9, S38. **Ambiguity:** The precedence table is not present in sections 1–9.

### S46 — Keep learning quarantined until verified telemetry exists

- **Source:** §4.2 learning row, line 352. **Category:** learning / provenance / evaluation. **Summary:** Retain quarantine; add structured attempt/failure telemetry, calibrated cohorts, censoring, and verified-only persistent learning. Separate temporary problem memory from replayable long-term memory.
- **Inputs → outputs:** Authenticated attempts/outcomes/costs/failure classes → calibration and reusable verified memory. **Invariants:** Empty or untrusted learning sets do not self-bootstrap authority. **Failure:** Missing writer/provenance/replay keeps records quarantined. **Integrations:** Attempt writer, evaluator, memory, selector. **Acceptance:** Cohorts can be reproduced by pipeline fingerprint and censorship status. **Dependencies:** S14. **Ambiguity:** Minimum cohort size is unspecified.

### S47 — Add OEIS as a structured service, not a prose agent

- **Source:** §4.2 OEIS row, line 353. **Category:** integration / provenance. **Summary:** Route retained upstream OEIS data through a deterministic structured service with local transforms, caching, provenance, and independent checking of any claim derived from a match.
- **Inputs → outputs:** Exact sequence/construction and transform budget → versioned ranked matches and source links. **Invariants:** OEIS suggestions never self-promote. **Failure:** No/ambiguous match yields a report, not novelty or truth. **Integrations:** Intake, experiments, literature, claim graph. **Acceptance:** Sequence-producing runs invoke the service and store transform/content hashes. **Dependencies:** S32. **Ambiguity:** Full trigger and API appear in §6.3/§8.

### S48 — Instantiate specialists conditionally, not as standing role theater

- **Source:** §4.3, lines 355–361. **Category:** multi-agent architecture / efficiency. **Summary:** Consolidate twenty-two nominal roles into seven durable services/authorities; instantiate a specialist only when a branch needs a distinct tool, prior, or information boundary.
- **Inputs → outputs:** Branch requirements and service capabilities → conditional worker dispatch. **Invariants:** Agent count is not a diversity metric. **Failure:** Redundant roles are not allocated as independent work. **Integrations:** Governor, authority registry, scheduler. **Acceptance:** Every worker lease records the branch-specific differentiator and durable authority. **Dependencies:** S33. **Ambiguity:** Seven authorities are defined in §6.5.

### S49 — Allocate branches by posterior utility and information value, not multiplication

- **Source:** §4.3, line 362. **Category:** control / evaluation. **Summary:** Replace brittle multiplicative priority factors with posterior expected utility plus value of information under explicit safety constraints.
- **Inputs → outputs:** Outcome/cost posteriors, information value, constraints → branch/action priority. **Invariants:** A subjective near-zero factor cannot automatically veto high-risk/high-reward work. **Failure:** Uncalibrated values retain uncertainty rather than compound into false precision. **Integrations:** Selector/controller. **Acceptance:** Scoring implementation matches the additive posterior formulations in §7. **Dependencies:** S31. **Ambiguity:** Weights remain policy/calibration choices.

### S50 — Let ambiguous interpretations coexist while blocking intended-problem publication

- **Source:** §4.3, line 363. **Category:** semantic control / failure. **Summary:** A statement adversary blocks publication against unresolved intent but need not halt all exploration; separable ambiguous readings remain distinct interpretation-lattice nodes and may receive cheap resolving tests.
- **Inputs → outputs:** Ambiguous parses and probe results → separate branches or reconciled interpretation. **Invariants:** Evidence never crosses interpretations without an explicit relation. **Failure:** Unresolved intent blocks intended-problem release, not exploratory computation. **Integrations:** Intake, controller, release. **Acceptance:** Multiple readings have unique IDs and independent claim closures. **Dependencies:** S24, S30. **Ambiguity:** “Cheap” test budget is policy-defined.

### S51 — Use a controlled two-pass literature protocol

- **Source:** §4.3, line 364. **Category:** retrieval / control / provenance. **Summary:** Replace an absolute online/offline split with blind scratch first, frozen solver packet second, and provenance-preserving targeted retrieval re-entry only when an exact gap appears.
- **Inputs → outputs:** Locked target, cold hypotheses, identified gap → versioned packets and branch updates. **Invariants:** Information boundaries and packet versions remain recorded. **Failure:** Unlogged ad hoc literature injection is rejected. **Integrations:** Controller, retrieval, packet store. **Acceptance:** Every worker input names its packet version; re-entry names the missing theorem/query. **Dependencies:** S12. **Ambiguity:** Exact cold fraction is 5–10% earlier.

### S52 — Formalize selectively by risk and centrality

- **Source:** §4.3, line 365. **Category:** formalization / resource allocation. **Summary:** Early formalization targets the problem statement, definitions, boundary cases, and claims with high centrality, semantic risk, or downstream consequence; low-risk glue may wait.
- **Inputs → outputs:** Claim graph with risk/centrality/cost → formalization queue. **Invariants:** Queue priority is not truth status. **Failure:** Deferred glue retains explicit formalization debt. **Integrations:** Claim graph, Lean, controller. **Acceptance:** Every early target has recorded selection factors; deferred claims remain labeled. **Dependencies:** S11. **Ambiguity:** Threshold/weights appear in §9.5 but are tunable.

### S53 — Do not admit high-centrality facts through a stateless LLM verifier

- **Source:** §4.3, line 366. **Category:** truth / security. **Summary:** High-centrality fact admission depends on evidence type; model review may route work but cannot manufacture a truth tier.
- **Inputs → outputs:** Central claim proposal and typed evidence → admitted tier or non-admission. **Invariants:** LLM confidence/vote is never a mechanical truth upgrade. **Failure:** Insufficient evidence leaves the claim weak/quarantined. **Integrations:** Evidence router, claim graph, referee. **Acceptance:** Admission policy denies model-only evidence for protected tiers. **Dependencies:** S19. **Ambiguity:** Tier-specific validator matrix is later.

### S54 — Keep truth, correspondence, novelty, and significance orthogonal

- **Source:** §4.3, line 367. **Category:** release / evaluation. **Summary:** No consensus score or Lean build may collapse mathematical truth, intended correspondence, novelty, and significance; reproducibility is likewise a separate gate under §1.
- **Inputs → outputs:** Per-axis evidence → per-axis verdicts. **Invariants:** Positive formal truth does not infer contribution status. **Failure:** Any combined scalar promotion path is invalid. **Integrations:** Five-gate release, manifests. **Acceptance:** Data model prevents one verdict from populating another. **Dependencies:** S2. **Ambiguity:** Line 367 names four axes while §1 adds replay as the fifth; they are complementary, not contradictory.

### S55 — Preserve the enumerated extension invariants

- **Source:** §4.4, lines 369–383. **Category:** regression / reliability / security. **Summary:** Preserve commit-pinned snapshots/section hashes, exact parent-statement lock, complete content-addressed compatible caches, append-only attempt/gate/adjudication/promotion ledgers, deterministic protected-exploration queues, atomic leased claims with migration/stale handling, non-consuming rate-limit waits capped at 120 seconds, deterministic rejection with generic evidence disabled, and proof-versus-plan failure distinction.
- **Inputs → outputs:** Extended implementation → invariant-preserving state/control behavior. **Invariants:** All listed properties. **Failure:** Any violated invariant blocks release of the extension. **Integrations:** Intake, cache, event store, queue, gate, regulator. **Acceptance:** Dedicated regression/fault tests cover each bullet. **Dependencies:** S8, S40. **Ambiguity:** “Append-only ledger machinery” may require migration from mutable current artifacts.

## Section 5: system organization and required end-to-end flow

### S56 — Separate four planes and three nested searches

- **Source:** §5.1, lines 385–400. **Category:** architecture / integration. **Summary:** Implement truth, search, control, and communication planes, and distinct research-program, AND/OR claim/lemma, and exact formal proof-state search levels.
- **Inputs → outputs:** Research events and user steering → plane-specific state/actions with controlled interfaces. **Invariants:** Control cannot set truth; communication does not become evidence. **Failure:** Cross-plane privilege violations are rejected. **Integrations:** All services. **Acceptance:** Service boundaries and event schemas map each operation to one plane/search level. **Dependencies:** S3. **Ambiguity:** Deployment/process isolation level is unspecified.

### S57 — Use least-privilege blackboard access and truth-plane-only status changes

- **Source:** §5.1 diagram and following text, lines 402–444. **Category:** security / state / integration. **Summary:** Agents read only the claim-graph/source-packet slice they need and write structured proposals; only truth-plane validators change epistemic status. Revocation feeds search; released outcomes alone feed persistent memory and later acquisition.
- **Inputs → outputs:** Scoped branch capsule and proposals → validated claim events, control feedback, release/memory records. **Invariants:** Shared state is not an unrestricted transcript. **Failure:** Unauthorized reads/writes or direct status changes are denied. **Integrations:** Access control, claim graph, controller, memory. **Acceptance:** Capability tests show workers cannot mutate truth tiers or access withheld packets. **Dependencies:** S56. **Ambiguity:** Authentication/ACL technology is unspecified.

### S58 — Freeze, parse, branch interpretations, probe, and audit status before search

- **Source:** §5.2 steps 1–5, lines 446–452. **Category:** workflow / intake / failure. **Summary:** Record exact source bytes/locations/status metadata/licenses/hashes; dual-parse a Statement IR; retain distinct interpretations; run type, boundary, exact-enumeration, symmetry/metamorphic, and counterexample probes; then audit current status across exact wording, objects, citations, OEIS, and formal libraries into `known/open/false/misquoted/ambiguous/status-uncertain` with provenance.
- **Inputs → outputs:** Source → frozen ProblemContract, lattice, probes, status classification. **Invariants:** Status and intent are evidence-backed claims. **Failure:** Conflicts become explicit uncertainty, not assumed openness. **Integrations:** Intake, falsifier, retrieval. **Acceptance:** Deep-run record contains every artifact/classification. **Dependencies:** S30. **Ambiguity:** Source coverage depends on access.

### S59 — Run cold search, freeze solver evidence, then score acquisition

- **Source:** §5.2 steps 6–8, lines 453–455. **Category:** workflow / retrieval / control. **Summary:** Spend 5–10% on literature-blind scratch/falsification whose output is only hypotheses/queries; build a frozen packet of exact theorem records, hypotheses, applicability checks, formal declarations, negative results and provenance; then score with uncertain outcomes, verification cost, status freshness, formal/computational affordances, reuse, and protected exploration.
- **Inputs → outputs:** Contract/interpretations/cold hypotheses/status → packet and acquisition decision. **Invariants:** Cold output cannot publish. **Failure:** Non-acquired problems produce honest triage, not false failure. **Integrations:** Programs, retrieval, selector. **Acceptance:** Packet/acquisition events are immutable and rationale-bearing. **Dependencies:** S12, S31. **Ambiguity:** Exact score is §7.

### S60 — Generate mechanism-distinct programs and dynamic AND/OR leaves

- **Source:** §5.2 steps 9–11, lines 456–458. **Category:** search / multi-agent. **Summary:** Dispatch only mechanism-distinct programs, each declaring falsifiers and bottlenecks; try direct proof first, then alternative sufficient lemma sets with prerequisites/centrality/risk/formal targets; attack disjoint leaves under explicit tools, budgets, and information boundaries, returning only structured claim/source/experiment/formal proposals.
- **Inputs → outputs:** Packet and problem graph → program archive, blueprint, branch results. **Invariants:** Branch distinction and least privilege persist. **Failure:** Failed direct search triggers justified decomposition, not arbitrary helper creation. **Integrations:** Governor, workers, claim graph, Lean/computation. **Acceptance:** Every leaf has a branch capsule and typed output. **Dependencies:** S33–S35. **Ambiguity:** Mechanism-distance threshold is §6.5 policy.

### S61 — Validate claims, cascade revocation, formalize risk early, and allocate adaptively

- **Source:** §5.2 steps 12–14, lines 459–461. **Category:** truth / failure / control. **Summary:** Evidence-type validators assign tiers; refuted claims revoke their dependency closure; weak claims may guide search but never silently become premises. Freeze Lean targets and prove boundary/high-risk/high-centrality claims early. Allocate using posterior utility, information gain, unlock/reuse/diversity/cost/duplication/semantic risk; rate limits only pause.
- **Inputs → outputs:** Branch artifacts and graph → admission/rejection/revocation/formal/controller events. **Invariants:** Tiers propagate downstream. **Failure:** Refutation reopens affected work; rate limits are operational censoring. **Integrations:** Evidence router, graph, Lean, controller. **Acceptance:** Injected refutation causes deterministic closure and reallocation. **Dependencies:** S40, S52–S53. **Ambiguity:** Validator matrix is later.

### S62 — Assemble only admitted proof material and issue five separate release verdicts

- **Source:** §5.2 steps 15–16, lines 462–463. **Category:** proof assembly / verification / release. **Summary:** Compile informal proof from admitted claims, formalize its dependency cone where feasible, run independent hostile verification, and decide truth, target correspondence, novelty, significance, and replay separately; mixed/partial status must be expressible without “solved.”
- **Inputs → outputs:** Admitted graph/blueprint/artifacts → candidate, referee report, five certificates, scoped result label. **Invariants:** No gate substitution. **Failure:** Unclosed gates yield qualified partial/unresolved status. **Integrations:** Proof compiler, Lean, referee, release. **Acceptance:** Renderer accurately expresses mixed verdicts. **Dependencies:** S35, S43. **Ambiguity:** “Where feasible” allows rigorous informal tiers defined later.

### S63 — Distill only replayed verified learning

- **Source:** §5.2 step 17, line 464. **Category:** learning / security. **Summary:** Persist proof patterns, tactics, calibrated outcomes, and failure classes only after replay under the current toolchain; keep speculative problem memory quarantined.
- **Inputs → outputs:** Gate certificates, replay reports, graph → persistent patterns or local quarantine. **Invariants:** Toolchain drift triggers revalidation. **Failure:** Missing/current replay denies persistent admission. **Integrations:** Replay, memory, selector/archive. **Acceptance:** Every persistent entry points to authenticated result and current-environment replay. **Dependencies:** S14, S46. **Ambiguity:** Retention/expiry policy is unspecified.

## Section 6: detailed module contracts

### S64 — Parse immutable intake into the complete typed Statement IR

- **Source:** §6.1 inputs/schema, lines 485–510. **Category:** data model / provenance. **Summary:** Consume immutable first-party bytes/metadata, prior versions, surrounding definitions/notation, and separately marked status claims; emit a `Problem` IR containing source IDs/hashes/spans, scoped typed binders, definitions, hypotheses, conclusion, requested outcome, parameter regime, edge cases, ambiguity nodes, and typed stronger/weaker/equivalent/special-case variants.
- **Inputs → outputs:** Enumerated intake records → typed Problem IR. **Invariants:** Every semantic element links to source spans; status labels remain claims. **Failure:** Missing/unparseable required structure is explicit, not guessed. **Integrations:** Source store, interpretation lattice. **Acceptance:** Schema validation and source-link completeness pass. **Dependencies:** S30. **Ambiguity:** Formula/type representation is unspecified.

### S65 — Run independent parsing and semantic covariance probes

- **Source:** §6.1 processing steps 2–6, lines 512–516. **Category:** semantic validation / failure. **Summary:** Obtain two parses from different model families or deterministic parser plus independently implemented semantic model; same-model prompt variants are correlated. Reconcile only exact/semantically justified matches, backtranslate every candidate, enforce meaning-preserving paraphrase invariance and meaning-changing mutation covariance, generate finite/boundary/type/dimension probes, and search smallest meaningful domains for counterexamples.
- **Inputs → outputs:** IR candidates and transformed statements → reconciliation/test/counterexample reports. **Invariants:** Claimed independence is architectural, not prompt-level. **Failure:** Failed covariance or counterexample creates ambiguity/refutation. **Integrations:** Falsifier, Lean, parser registry. **Acceptance:** Reports retain both parses and every transformation result. **Dependencies:** S24. **Ambiguity:** “Semantically justified” review mechanism is unspecified.

### S66 — Preserve unresolved interpretations and emit complete intake outputs

- **Source:** §6.1 step 7 and outputs, lines 517–525. **Category:** failure / acceptance / data model. **Summary:** Every unresolved ambiguity becomes an interpretation node; node-specific exploration may continue, but release against the intended problem is blocked. Emit exact-hashed `ProblemContract`, interpretation lattice, probe artifacts, status-audit request, fidelity risk, and unresolved decisions.
- **Inputs → outputs:** Reconciliation/probe results → full intake package. **Invariants:** Ambiguities are never silently normalized away. **Failure:** Unresolved intent blocks intended-target certificate. **Integrations:** Controller, status retrieval, release. **Acceptance:** All listed outputs exist and hashes bind the source. **Dependencies:** S64–S65. **Ambiguity:** Risk-score calibration is unspecified.

### S67 — Cover all specified selector feature families

- **Source:** §6.2 feature families, lines 529–543. **Category:** control / evaluation / data. **Summary:** The calibrated selector must include status, statement, literature, formal, computational, mathematical, operational, reuse, and locally measured model/tool-fit features, including conflicts/freshness, ambiguity, theorem density, Mathlib debt, certificate affordance, censoring/cost, and cross-problem reuse; it is not a difficulty oracle or vendor-reputation score.
- **Inputs → outputs:** Versioned feature observations → selector feature vector with provenance/uncertainty. **Invariants:** Locally observed fit supersedes vendor reputation. **Failure:** Missing features are represented as unknown, not favorable defaults. **Integrations:** Retrieval, Lean, computation, telemetry. **Acceptance:** Feature schema contains each family and source timestamps. **Dependencies:** S31. **Ambiguity:** Some mathematical features are subjective and require calibration.

### S68 — Model competing outcomes with calibrated, censoring-aware posteriors

- **Source:** §6.2 outcome posterior, lines 545–560. **Category:** evaluation / control / failure. **Summary:** Separately model full novel resolution, rediscovery/status identification, disproof, verified partial, reusable infrastructure, status correction, no progress, and invalid/false promotion, including generation/retrieval/computation/formalization/verification/expert-review costs. Use hierarchical Bayesian or calibrated ensembles with domain priors, credible intervals, survival/censoring likelihoods; timeouts/rate limits are censored, and early data uses weak priors/wide intervals.
- **Inputs → outputs:** Authenticated outcomes/costs/censor reasons → per-outcome/cost posterior. **Invariants:** Outcomes do not collapse into solve/no-solve. **Failure:** Operational censoring never records math failure. **Integrations:** Telemetry, selector, evaluation. **Acceptance:** Posterior API exposes intervals and censor handling. **Dependencies:** S14. **Ambiguity:** Calibration method is selectable.

### S69 — Enforce selector exclusion, probe, exploration, and list-separation behavior

- **Source:** §6.2 selection behavior, lines 562–568. **Category:** control / fairness / failure. **Summary:** Hard-exclude only malformed, unauthorized, or provably duplicate tasks; run a standard cheap probe before deep search; reserve 15–25% for domain/low-attempt/high-uncertainty exploration; publish separate rankings for full solve, useful partial, formalization, finite computation, and reuse; never infer solvability from prize/popularity/formal statement alone.
- **Inputs → outputs:** Posterior/features/policy → exclusions, probes, lane allocations, distinct ranked lists. **Invariants:** Low score is not impossibility. **Failure:** Hard exclusions carry an explicit enumerated reason. **Integrations:** Queue, probe service, portfolio. **Acceptance:** Allocation ledger meets protected fraction and list schemas remain separate. **Dependencies:** S67–S68. **Ambiguity:** 15–25% is an initial policy range.

### S70 — Invoke OEIS deterministically on the specified triggers

- **Source:** §6.3, lines 572–576. **Category:** integration / control. **Summary:** Implement OEIS as deterministic service plus source-auditing worker, invoked for experiment-generated integer sequences; extremal counts, recurrences, coefficients, partitions, graph invariants, finite extrema; or Erdős OEIS links/“possible” markers—not as a free-form proof agent.
- **Inputs → outputs:** Triggering problem/experiment and exact sequence metadata → OEIS request and audited result. **Invariants:** Service output remains source/numerical evidence. **Failure:** Unavailable/failed OEIS does not become novelty evidence. **Integrations:** Experiments, intake, literature. **Acceptance:** Trigger tests deterministically enqueue the service. **Dependencies:** S47. **Ambiguity:** Trigger NLP detection may need explicit schemas.

### S71 — Query four linked retrieval indexes with the complete query bundle

- **Source:** §6.4 indexes/query bundle, lines 578–595. **Category:** retrieval / integration. **Summary:** Search linked bibliographic, mathematical, formal, and experimental indexes using exact normalized statement/distinctive text, object/type/parameter signature, equivalents/duals/special cases, techniques/obstructions, author/citation neighborhoods, formal goal/premises, and OEIS references.
- **Inputs → outputs:** ProblemContract/interpretation/formal goal → logged multi-index query bundle and candidates. **Invariants:** Query diversity and formulation variants are preserved. **Failure:** Missing index/access becomes explicit coverage limitation. **Integrations:** Literature graph, theorem DB, OEIS, code/dataset indexes. **Acceptance:** Query log records every applicable bundle component and corpus version. **Dependencies:** S32. **Ambiguity:** Coverage minimum is not specified.

### S72 — Store complete `TheoremRecord`s and rank without treating popularity as truth

- **Source:** §6.4 theorem records/ranking, lines 597–618. **Category:** data / provenance / retrieval. **Summary:** Each theorem record includes canonical statement, exact hypotheses/conclusion/notation, versioned URI/hash/span/time/verbatim extract, extraction method/version/confidence, authors/date/publication/corrections, formal declarations, applicability conditions/checks, citations, independent verification, and license/access. Rank by semantic/formula match, compatibility, authority/freshness/corroboration/formal linkage/citation proximity/query diversity, never citation count as truth.
- **Inputs → outputs:** Retrieved source material → versioned ranked records. **Invariants:** Verbatim hypotheses and corrections remain available. **Failure:** Incomplete/low-confidence extraction stays unaudited. **Integrations:** Source store, OCR/parser, formal library, license policy. **Acceptance:** Schema completeness and deterministic ranking-feature audit pass. **Dependencies:** S71. **Ambiguity:** Ranking weights are unspecified.

### S73 — Separate recall from import audit and novelty review

- **Source:** §6.4, lines 620–625. **Category:** separation of duties / security. **Summary:** A high-recall retriever may propose uncertain matches; a separate import auditor checks exact source, hypotheses, scope, version, and logical consequence. Only audited imports become usable facts. Novelty review uses a separate query log and has no incentive to support the proof.
- **Inputs → outputs:** Candidate theorem matches → audited import/rejection and independent novelty coverage. **Invariants:** Retrieval score cannot upgrade truth; proof support and novelty incentives remain separate. **Failure:** Audit failure leaves a lead, not a premise. **Integrations:** Claim graph, source auditor, novelty gate. **Acceptance:** Usable import nodes include auditor/verdict and exact applicability checks. **Dependencies:** S72. **Ambiguity:** Auditor independence may be organizational or model/tool based.

### S74 — Implement seven durable authorities with enforced boundaries and required outputs

- **Source:** §6.5 authority table, lines 627–639. **Category:** architecture / least privilege / integration. **Summary:** Provide governor (budget decisions, no truth mutation), intake/retrieval (target/status/packet, no proof injection), scoped program workers, initially withheld computational falsifier, formalization authority (no novelty decision), agreement-neutral adversarial referee, and release auditor (five certificates, no same-pass repair generation), each emitting the specified structured outputs.
- **Inputs → outputs:** Authority-specific scoped inputs → branch decisions/contracts/proposals/artifacts/reports/certificates. **Invariants:** Objective and information boundaries are enforced. **Failure:** Boundary-violating output is rejected and logged. **Integrations:** Scheduler, ACLs, all planes. **Acceptance:** Capability tests and output-schema tests pass for all seven. **Dependencies:** S48, S57. **Ambiguity:** Human authority interaction is not fully specified.

### S75 — Count diversity only when workers differ in at least two dimensions

- **Source:** §6.5 diversity, lines 641–653. **Category:** multi-agent evaluation / control. **Summary:** Independent method credit requires difference in at least two of method/prohibitions, tools, source packet/withheld information, objective, model lineage, representation, or counterfactual assumption. Same-model identical-context chats are one correlated method.
- **Inputs → outputs:** Worker configurations → diversity/correlation labels and portfolio bins. **Invariants:** Prompt wording alone does not create independence. **Failure:** Insufficiently distinct workers merge for diversity accounting. **Integrations:** Dispatcher, mechanism archive, evaluator. **Acceptance:** Diversity validator computes qualifying dimensions and rejects duplicate independence claims. **Dependencies:** S33. **Ambiguity:** “Model family/training lineage” attestation may be unavailable.

### S76 — Enforce governor and program-worker action contracts

- **Source:** §6.5 compact roles, lines 655–675. **Category:** control / failure / output contract. **Summary:** Governor maximizes verified progress from contracts/graph/posteriors/costs/leases and may open/pause/reopen/merge/route/request human help, but cannot alter evidence, treat timeout as math failure, publish, or use confidence as truth. A worker pursues only its declared mechanism/target/assumptions and returns normalized claims, dependencies, proof/experiment, strongest falsifier, bottleneck, cost; it cannot use uncited imports, strengthen assumptions, or label evidence, and failure yields a minimal reusable certificate.
- **Inputs → outputs:** Scoped branch capsule → authorized control event or structured result. **Invariants:** Control and truth privileges remain distinct. **Failure:** Contract violation rejects result; mechanism failure produces certificate. **Integrations:** Controller, claim graph, cost ledger. **Acceptance:** Schema/policy tests cover every required/forbidden action. **Dependencies:** S74. **Ambiguity:** Human-decision escalation SLA is unspecified.

### S77 — Require reproducible, classified computational-falsifier output

- **Source:** §6.5 computational-falsifier role, lines 677–684. **Category:** computation / failure / provenance. **Summary:** Actively test target/key lemmas in smallest, boundary, alternate, random, and adversarial cases; every result includes code, exact inputs/environment/seed/arithmetic/coverage/output hash and explicitly distinguishes evidence, finite proof, or counterexample.
- **Inputs → outputs:** Claim/branch and search domain → immutable computational artifact with classification. **Invariants:** Reproduction metadata is mandatory for positive and negative results. **Failure:** Missing fields prevent evidence admission. **Integrations:** Experiment service, artifact store, evidence router. **Acceptance:** Required metadata validates and replay reproduces hash. **Dependencies:** S41. **Ambiguity:** “Smallest meaningful” domain is claim-specific.

### S78 — Enforce formalization-authority semantic and proof-state discipline

- **Source:** §6.5 formalization role, lines 686–694. **Category:** formal security / workflow. **Summary:** Audit the target first; keep source-to-Lean links and semantic invariants; operate on exact proof states with premise retrieval, smallest justified helpers, continuous compilation, and complete axiom/import/placeholder reporting. Vendor status/build success never establishes informal correspondence.
- **Inputs → outputs:** Approved interpretation, sources, Lean goals → declarations, proof states, build/axiom/correspondence reports. **Invariants:** Wrong-theorem proof is failure. **Failure:** Semantic mismatch or hidden trust mechanism blocks admission. **Integrations:** Lean service, theorem retrieval, target gate. **Acceptance:** Every declaration has source link and clean reports. **Dependencies:** S42. **Ambiguity:** “Smallest” helper is judged via debt/risk policy.

### S79 — Require hostile reconstruction and five independent release verdicts

- **Source:** §6.5 referee/release roles, lines 696–712. **Category:** verification / release / failure. **Summary:** Referee independently reconstructs from locked statement, graph, raw sources, and artifacts, searching quantifier/domain errors, circularity, assumptions/imports, counterexamples, computation mismatch, and formal/informal divergence, returning first invalid dependency and all affected conclusions. Release auditor separately returns target, truth, novelty, significance, and reproducibility verdicts; `unknown` is allowed and no verdict substitutes for another.
- **Inputs → outputs:** Candidate/evidence → defect graph/recalculation/profile and five verdicts. **Invariants:** Referee is not collaborator; release pass does not repair. **Failure:** Defect revokes affected closure; unknown remains explicit. **Integrations:** Graph, replay, release. **Acceptance:** Checklist/reconstruction artifacts and per-gate verdicts exist. **Dependencies:** S43, S74. **Ambiguity:** “First invalid dependency” does not excuse omitting other discovered defects.

### S80 — Preserve evidence tiers through all downstream uses

- **Source:** §6.6, lines 714–718. **Category:** state / security. **Summary:** Shared state is append-only graph plus materialized views; weak claims may guide search, but every downstream use retains the source tier and no model summary upgrades evidence.
- **Inputs → outputs:** Claim/event dependencies → tier-preserving derived claims/views. **Invariants:** Evidence monotonicity requires validator events, not prose transformation. **Failure:** Tier laundering invalidates the downstream node. **Integrations:** Graph, summarizers, proof compiler. **Acceptance:** Provenance traversal returns original tiers for every premise. **Dependencies:** S38. **Ambiguity:** Full graph schema is §10 outside scope.

### S81 — Match search algorithms to topology and restrict weak methods

- **Source:** §6.7, lines 720–731, and §7.1, lines 803–809. **Category:** search architecture / trust. **Summary:** Use contextual Thompson/UCB across programs/tools, quality-diversity best-first/MAP-Elites at mechanism level, AO*/best-first on AND/OR blueprints, PUCT/MCTS plus beam/best-first for Lean states, evolutionary islands only for executable candidates, and debate only to propose defects/experiments/revisions—not truth. Algorithm choice must respect topology: best-first risks collapse, beam drops branches, MCTS suits locally feedback-rich Lean rather than sparse long semantic programs, and evolution requires executable fitness.
- **Inputs → outputs:** Level-specific state and evidence → algorithm-specific next actions. **Invariants:** Search heuristic never becomes evidence. **Failure:** Unsupported evolution/debate results remain proposals. **Integrations:** Controller, archives, claim graph, Lean, computation. **Acceptance:** Routing tests select only allowed algorithm/domain combinations. **Dependencies:** S25, S49. **Ambiguity:** Exact algorithm choice within a level is adaptive.

### S82 — Expose immutable computation jobs with a complete experiment specification

- **Source:** §6.8 API/spec, lines 733–754. **Category:** service interface / reproducibility / security. **Summary:** Implement submit/poll/artifact/replay/verify-certificate operations. `ExperimentSpec` binds claim/branch purpose, repository commit/entry point, exact inputs/domain/coverage, all tool versions, arithmetic/precision/error bounds, seed/resources, output schema/checker, and network/sandbox policy.
- **Inputs → outputs:** Immutable `ExperimentSpec` → job ID, artifact, independent ReplayReport, CertificateReport. **Invariants:** Jobs/specifications are content-bound. **Failure:** Incomplete/changed spec rejects execution or evidence reuse. **Integrations:** Sandbox, artifact store, checkers, claim graph. **Acceptance:** API round-trip and replay produce stable hashes with enforced resource/network policy. **Dependencies:** S41. **Ambiguity:** Poll/status state machine is unspecified.

### S83 — Validate exactly one computational evidence class and hard-check exactness

- **Source:** §6.8 classification, lines 756–765. **Category:** evidence validation / failure. **Summary:** Every artifact is validator-classified as exactly one of heuristic/numerical evidence, exact-validation-pending counterexample, exact counterexample, exhaustive finite-subcase proof, certificate-checked lemma, or complete proof via justified finite reduction. Floating point proves exact claims only with validated interval/error arguments; CAS is replayed/certified; SAT/SMT `unsat` needs reconstruction/checked trace where available.
- **Inputs → outputs:** Artifact/spec/checker → exclusive class and admission tier. **Invariants:** Self-classification is not trusted. **Failure:** Ambiguous class or missing exactness support downgrades/rejects. **Integrations:** Evidence router, CAS/SAT/SMT checkers. **Acceptance:** Negative tests prevent numeric/status-only exact promotion. **Dependencies:** S82. **Ambiguity:** “Where available” leaves solver testimony tier for unsupported proof traces.

### S84 — Start Lean during intake, not after proof drafting

- **Source:** §6.9, lines 767–769. **Category:** formalization / workflow. **Summary:** Lean is an active evidence plane beginning during intake, with staged target/sentinel/proof-state work; it is not a post-hoc formatting step.
- **Inputs → outputs:** Intake interpretation and early claims → target candidates, sentinels, diagnostics. **Invariants:** Formal feedback may revise the blueprint and prose. **Failure:** A post-hoc-only formal path cannot satisfy the architecture. **Integrations:** Intake, controller, graph. **Acceptance:** Run trace shows Lean target work before deep assembly. **Dependencies:** S11, S52. **Ambiguity:** Formal coverage may remain selective.

### S85 — Separate verification organization, resources, and success metrics from generation

- **Source:** §6.10, lines 771–773. **Category:** separation of duties / verification. **Summary:** Verification has its own models, tools, caches, and success metric; a positive result is a set of discharged obligations, not scalar confidence.
- **Inputs → outputs:** Candidate and obligation checklist → per-obligation evidence/verdict. **Invariants:** Generator cannot self-certify. **Failure:** Undischarged obligations remain visible and block the corresponding tier. **Integrations:** Referee, evidence router, release. **Acceptance:** Separate identities/caches and obligation-level reports are auditable. **Dependencies:** S17, S79. **Ambiguity:** Organizational independence strength is unspecified.

### S86 — Separate memory stores and revalidate on drift

- **Source:** §6.11, lines 775–786. **Category:** learning / provenance / security. **Summary:** Keep distinct problem-local weak/quarantined memory, mechanically verified semantic memory with exact dependencies, audited external imports whose applicability is rechecked, procedural memory, negative memory with reopen conditions, and calibration memory. Never conflate stores; train/evaluate in frozen periods with exact pipeline fingerprints and evaluators different from trained models; source/toolchain corrections trigger revalidation/applicability review.
- **Inputs → outputs:** Typed outcomes/imports/patterns/failures → store-specific entries and revalidation events. **Invariants:** Audited external theorem is not locally verified fact. **Failure:** Drift or missing provenance suspends reuse. **Integrations:** Claim graph, training, evaluator, source/toolchain registry. **Acceptance:** Type system/access rules prevent cross-store promotion and drift tests trigger review. **Dependencies:** S14, S63. **Ambiguity:** Expiry policy is unspecified.

### S87 — Enforce minimal service contracts and solver-translation obligations

- **Source:** §6.12, lines 788–801. **Category:** integration / interface / security. **Summary:** Literature, theorem DB, OEIS, computation, Lean, ATP/SMT/SAT, claim graph, and controller services must accept/return the listed minimal provenance-bearing requests/responses. ATP/solver `proved`/`unsat` without checked trace/reconstruction remains testimony, and source-to-solver semantic translation obligations must be discharged before promotion.
- **Inputs → outputs:** Service-specific request → versioned source packet, premise candidates, OEIS matches, replay artifact, Lean results, checked solver proof/model, graph admission, or lease/rationale. **Invariants:** Responses do not exceed their trust semantics. **Failure:** Missing provenance/check/translation blocks promotion. **Integrations:** All services. **Acceptance:** Contract/schema tests plus mistranslation test fail closed. **Dependencies:** S26, S72, S82. **Ambiguity:** “Minimal trusted response” may still require later release checks.

## Section 7: mathematical search and compute allocation

### S88 — Maintain competing outcome and full-cost posteriors and use the acquisition formula

- **Source:** §7.2, lines 811–837. **Category:** control / evaluation / implementation. **Summary:** For each problem maintain separate posteriors for novel full result, refutation, verified partial, status fix, reusable infrastructure, rediscovery, no progress, and invalid result, plus total generation/retrieval/computation/formalization/verification/expert-review cost. Project policy—not the model—sets outcome values. Acquisition combines expected value, protected-lane uncertainty, expected information gain, reuse, portfolio diversity, status freshness, cost exponent, and ambiguity/staleness/library-gap penalties as specified.
- **Inputs → outputs:** Features/posteriors/policy values/cost → acquisition score/distribution. **Invariants:** Value policy is external to models. **Failure:** Missing/uncertain data propagates uncertainty. **Integrations:** Selector, telemetry, policy. **Acceptance:** Formula-level tests reproduce all terms/signs and cost range `α∈[0.7,1]`. **Dependencies:** S68. **Ambiguity:** Weights/penalty definitions require calibration.

### S89 — Use posterior sampling, protected exploration, and separate hard constraints

- **Source:** §7.2, lines 839–848. **Category:** control / safety / evaluation. **Summary:** Apply the standard-deviation bonus only in protected exploration; use Thompson sampling in exploitation rather than posterior means forever; reserve 15–25% exploration and report point estimates plus intervals. Unsupported source access, malformed statements, incompatible licenses, or unacceptable false-promotion risk block allocation as hard constraints; low score never means mathematical impossibility.
- **Inputs → outputs:** Posteriors, lane, hard-policy checks → sampled allocation or explicit block. **Invariants:** Safety constraints are not traded off against score. **Failure:** Hard-constraint violation fails closed with reason. **Integrations:** Scheduler, license/access policy, intake. **Acceptance:** Lane tests enforce bonus scope/fraction and block rules. **Dependencies:** S69, S88. **Ambiguity:** “Unacceptable” risk threshold is policy-defined.

### S90 — Score branch actions additively and select under global constraints

- **Source:** §7.3 branch/action score, lines 850–879. **Category:** search control / evaluation. **Summary:** Branch/action utility sums outcome value, information gain, centrality-weighted unlock, cross-problem reuse, mechanism diversity, and falsification value, minus expected cost, duplication, and semantic risk; select by posterior sampling/UCB under global budget/concurrency. Do not multiply subjective factors.
- **Inputs → outputs:** Branch/action features and posteriors → utility sample and selected action/lease. **Invariants:** Semantic risk and duplication remain explicit penalties; falsification is positively valued. **Failure:** Missing calibration yields uncertain utility, not silent zero veto. **Integrations:** Controller, graph centrality, archive, cost model. **Acceptance:** Scoring tests cover each term and disallow multiplicative legacy formula. **Dependencies:** S49. **Ambiguity:** Weight calibration is unspecified.

### S91 — Key Lean transpositions exactly and freeze target-relative verified-debt accounting

- **Source:** §7.3 Lean scoring/debt, lines 881–892. **Category:** formal search / cache security / evaluation. **Summary:** Lean child selection uses PUCT prior/value/visit terms plus verified-debt reduction and cost. Exact state transpositions bind Lean/Mathlib versions, imports/options, elaborated local context, exact target, and trust policy. Verified debt covers every reachable open helper plus semantic/import debt; target-restating helpers earn zero/negative credit. Debt definition/weights are frozen for an evaluation run.
- **Inputs → outputs:** Exact GoalCapsule/actions/debt graph → PUCT score/cache hit/debt delta. **Invariants:** Pretty text is not identity; difficulty cannot be hidden in helpers. **Failure:** Key mismatch prevents reuse; added obligations reduce credit. **Integrations:** Lean service, blueprint, cache. **Acceptance:** Restatement and context-mutation tests behave as required. **Dependencies:** S22, S39. **Ambiguity:** PUCT constants are tunable.

### S92 — Fingerprint mechanisms, preserve quality diversity, and crossover only verified subgraphs

- **Source:** §7.4, lines 894–921. **Category:** search / diversity / security. **Summary:** Every top-level program declares target interpretation, reformulation, method, central lemma, new objects/invariants, required external theorems, computation, falsifiers, and formal route. Archive by method/result/domain/finite-literature dimensions and permit direct, contrapositive, representation, explicit variant, decomposition, counterexample-twin, retrieval, computational, or formal branches; crossover only verified subgraphs.
- **Inputs → outputs:** Program proposal → mechanism fingerprint, archive bin, allowed branch. **Invariants:** Variant relations and external dependencies are explicit; weak subgraphs do not contaminate crossover. **Failure:** Incomplete/duplicate fingerprint is rejected or penalized. **Integrations:** Program archive, claim graph, controller. **Acceptance:** Schema tests and unverified-crossover rejection pass. **Dependencies:** S60, S75. **Ambiguity:** Bin granularity is policy-defined.

### S93 — Deduplicate in a staged cascade without merging materially different obligations

- **Source:** §7.5, lines 923–934. **Category:** search efficiency / provenance. **Summary:** Detect duplicates via exact target/assumption/formal-context hash, normalized formula/dependency-cone isomorphism, premise/mechanism MinHash/Jaccard, plan embedding, behavior on tests/countermodels, and human/model comparison only at the borderline. Merge exact duplicates’ evidence/cost histories; penalize but retain near-duplicates whose assumptions, falsifiers, or obligations differ.
- **Inputs → outputs:** Branch pair/history → exact merge, near-duplicate penalty, or distinct status. **Invariants:** No semantic information is lost by approximate merging. **Failure:** Borderline cases remain separate pending comparison. **Integrations:** Archive, graph, cost ledger. **Acceptance:** Test pairs exercise every cascade stage and preserve materially distinct branches. **Dependencies:** S92. **Ambiguity:** Similarity thresholds require calibration.

### S94 — Compress failures structurally and distinguish censoring from mathematical death

- **Source:** §7.6, lines 936–952. **Category:** failure handling / learning / control. **Summary:** A failed branch records branch/fingerprint, exact obligation, first invalid claim/missing premise, evidence/counterexample, attempted actions/cost, learning, scope, reopen condition, and related branches. “Model could not finish” is not a mathematical certificate; resource exhaustion is censored. Kill only for valid counterexample, logical impossibility, dominated identical state, or policy constraint; otherwise pause.
- **Inputs → outputs:** Failed attempt/operational outcome → structured failure certificate plus kill/pause/censor event. **Invariants:** Operational limits do not falsify mathematics. **Failure:** Missing valid kill reason forces pause. **Integrations:** Controller, negative memory, calibration. **Acceptance:** Timeout/resource tests record censoring and reopen metadata. **Dependencies:** S37, S68. **Ambiguity:** Logical-impossibility evidence standard must use claim validators.

### S95 — Apply conjunctive pause rules, narrow termination, and explicit reopen triggers

- **Source:** §7.7, lines 954–970. **Category:** control / failure recovery. **Summary:** Pause only after all four conditions persist for `K` controller reviews: marginal value below cost, no verified-debt/information gain, repeated known signatures, and no exploration obligation. Terminate only if falsified, strictly subsumed by stronger verified branch, semantically invalid, or prohibited. Reopen on admitted dependency, interpretation-changing counterexample, relevant literature/OEIS, capability change, material posterior change, or human ambiguity resolution.
- **Inputs → outputs:** Review history/graph/posteriors/policy events → continue/pause/terminate/reopen. **Invariants:** Stop reasons are enumerated and evented. **Failure:** Insufficient pause predicates keep branch eligible; non-terminal exhaustion pauses. **Integrations:** Controller, graph, retrieval/tool registry, human steering. **Acceptance:** State-machine tests cover every predicate/trigger. **Dependencies:** S94. **Ambiguity:** `K` is configurable and unspecified.

### S96 — Use progressive evidence-gated compute bands and reserve capacity

- **Source:** §7.8, lines 972–987. **Category:** control / evaluation / capacity. **Summary:** Treat percentages/counts as initial defaults requiring ablation. Progress from integrity, cheap probes, 4–8 distinct programs, dynamic lemma/compute/Lean work, deep campaign, to release only when each listed evidence condition is met. Scale compute because evidence warrants it and reserve 10–20% for surprises, independent verification, and recovery.
- **Inputs → outputs:** Band evidence and budget → next-band promotion or hold. **Invariants:** Busy capacity is not an expansion reason; verification capacity remains protected. **Failure:** Missing expansion condition holds/pauses at current band. **Integrations:** Controller, evaluator, verification queue. **Acceptance:** Band transition events cite the specified evidence; reserve remains within range. **Dependencies:** S11, S28. **Ambiguity:** Defaults conflict only superficially with the distinct 15–25% problem-exploration reserve; they fund different purposes.

### S97 — Implement the evented main research loop and honest non-acquisition outcome

- **Source:** §7.9, lines 989–1055. **Category:** end-to-end integration / resume / acceptance. **Summary:** Execute freeze/interpret/probe/status, 5% cold pass, frozen packet, acquisition (return honest triage if declined), graph/archive/verified-store/blueprint/controller setup, budgeted leased parallel action selection, artifact freezing, evidence validation/event append, revocation/reopen, blueprint/archive/verified-memory/posterior updates, stagnation retrieval/counterfactual/formal-risk protocol, event snapshots, admitted-graph compilation, independent referee, five gates, authenticated distillation, and rendered result.
- **Inputs → outputs:** Source/global budget → replayable result or honest triage. **Invariants:** Only authenticated patterns reach verified store; every loop mutation is evented. **Failure:** Refutation propagates; stagnation changes strategy; no acquisition is not failure. **Integrations:** Entire EGMRA. **Acceptance:** End-to-end trace contains each ordered stage and resumes from snapshots deterministically. **Dependencies:** S56–S96. **Ambiguity:** Pseudocode’s 5% is one permitted point in S12’s 5–10% range.

### S98 — Reserve verification, route by local evidence, cap concentration, and normalize rate limits

- **Source:** §7.10, lines 1057–1064. **Category:** resource control / reliability / evaluation. **Summary:** Reserve verification before opening many proof branches; route cheap models to breadth, stronger ones to bottlenecks, formal/open models to Lean, deterministic tools to arithmetic/enumeration; benchmark routing locally and re-estimate after versions change. A branch exceeding configured budget share needs a governor event citing debt reduction/information value. Costs include expert time/formal debt. Rate limits use provider state, `Retry-After`, jittered exponential backoff capped at 120 seconds per attempt, pausing leases without consuming math retry.
- **Inputs → outputs:** Capacity/model/tool metrics/provider signals → route, lease, cost, pause/retry events. **Invariants:** Verification backlog and provider throttling cannot masquerade as math outcomes. **Failure:** Missing concentration rationale prevents more allocation. **Integrations:** Scheduler, model registry, cost ledger, provider adapters. **Acceptance:** Capacity/fault/version tests satisfy each safeguard. **Dependencies:** S40, S96. **Ambiguity:** Configured branch fraction is unspecified.

## Section 8: OEIS and external-database integration

### S99 — Pin corpus snapshots and treat status as versioned evidence

- **Source:** §8.1, lines 1066–1079. **Category:** provenance / retrieval / failure. **Summary:** Pin an upstream Erdős snapshot rather than a drifting page; store YAML, website, original sources, later papers, and expert commentary as separate evidence. “Open” has source/review date; status-change date differs from solution date. Every deep run refreshes status or uses a recent signed snapshot; conflicts become `status_uncertain` plus literature task, not automatic campaigns.
- **Inputs → outputs:** Corpus/source snapshots and status observations → versioned status record/conflict task. **Invariants:** Snapshot counts are not timeless. **Failure:** Stale/conflicting status blocks assumed-open deep work. **Integrations:** Intake, literature, selector, signing policy. **Acceptance:** Deep-run contract has snapshot hash/freshness and conflict behavior. **Dependencies:** S58. **Ambiguity:** “Recent” is not quantified.

### S100 — Search broadly and independently for novelty/status

- **Source:** §8.1, line 1080. **Category:** novelty / retrieval / acceptance. **Summary:** MathOverflow, papers, author pages, formal libraries, and databases are discovery sources, none singly proves openness/novelty; novelty audit must search backward/forward citations, synonyms, equivalents, and original references.
- **Inputs → outputs:** Candidate claim/problem record → query log, coverage gaps, novelty/status verdict. **Invariants:** Absence in one source is never novelty evidence. **Failure:** Incomplete coverage yields unresolved novelty/status. **Integrations:** Literature service, release gate. **Acceptance:** Novelty certificate links all required search dimensions and dates. **Dependencies:** S73, S99. **Ambiguity:** Exhaustiveness threshold is not specified.

### S101 — Cache OEIS provenance and enforce rate/use/submission policy

- **Source:** §8.2, lines 1082–1085. **Category:** integration / legal-policy / security. **Summary:** Cache OEIS responses with retrieval time/content hash, respect usage/rate limits and OEIS AI policy; research use is allowed, but the system must not generate Pink Box/editorial replies or bulk submissions. Any permitted submission needs an identified human who understands, verifies, and accepts responsibility for all mathematical and bibliographic content/correspondence.
- **Inputs → outputs:** OEIS query/response and optional submission intent → cached result or policy denial/human-governed submission. **Invariants:** Autonomous editorial/submission activity is prohibited. **Failure:** Rate/policy violation pauses/rejects; no accountable human blocks submission. **Integrations:** OEIS adapter, identity/policy, rate limiter. **Acceptance:** Policy tests deny prohibited modes and cache immutable provenance. **Dependencies:** S47. **Ambiguity:** Human identity verification mechanism is unspecified.

### S102 — Validate typed OEIS requests and transforms locally and fail visibly

- **Source:** §8.2 request/transforms, lines 1086–1112. **Category:** interface / data integrity / failure. **Summary:** Requests bind query/problem/claim IDs, exact string terms/value type/index/offset/construction, term-generator hash, allowed transforms, and query cap. Generate/deduplicate transforms locally; store exact transform path. Registry entries declare domains, parameters, preconditions, and inverse where relevant; exact-ratio zero denominators, Dirichlet invertibility, complement baseline, nonzero normalization scale, and subsequence index maps are enforced. Undefined transforms fail visibly.
- **Inputs → outputs:** Validated sequence/request → deduplicated remote queries and traceable transform paths. **Invariants:** No lost offset/sign/normalization/subsequence semantics. **Failure:** Preconditions/unknown transform reject rather than emit query. **Integrations:** Experiment artifact, OEIS client. **Acceptance:** Schema and edge-case tests cover listed transform failures/max queries. **Dependencies:** S70, S101. **Ambiguity:** Transform list may be extensible only through typed registry.

### S103 — Return provenance-rich OEIS match and rate-limit records

- **Source:** §8.2 response, lines 1114–1140. **Category:** service output / provenance. **Summary:** OEIS responses must expose ranked A-number matches with score, exact transform, offset, exact prefix overlap, descriptive/formula/recurrence/generating-function/program/cross-reference/reference/keyword fields, entry version, retrieval time/content hash, plus no-match transforms and rate-limit state.
- **Inputs → outputs:** OEIS API/cache data → normalized response schema. **Invariants:** Every match is version/hash/transform traceable. **Failure:** Partial/malformed responses are not admitted as complete match records. **Integrations:** OEIS client, source store, literature. **Acceptance:** Contract validation proves all required fields or explicit absence states. **Dependencies:** S102. **Ambiguity:** External field availability may require nullable-but-explicit representation.

### S104 — Rank, hold out, audit, and never treat OEIS matching as proof or novelty

- **Source:** §8.3, lines 1142–1165. **Category:** evaluation / evidence / failure. **Summary:** Rank by prefix length/rarity, independent extra-term agreement, offset, construction/object semantics, formula/recurrence, linked sources, transform complexity, and collision risk. When feasible compute at least 5–10 exact terms (more for common prefixes), query variants, hold out and recompute extra terms, test formulas/recurrences, retrieve sources, create only `NUMERICAL_EVIDENCE` conjectural nodes, and independently prove/import-audit any used formula. Match is never proof; no match is never novelty.
- **Inputs → outputs:** Exact terms/matches → ranked conjectures, held-out tests, source tasks. **Invariants:** Held-out evidence was not sent in query. **Failure:** Formula mismatch/refuted terms reject match use; short prefixes retain collision risk. **Integrations:** Computation, claim graph, retrieval/auditor. **Acceptance:** Workflow logs query/holdout separation and tier. **Dependencies:** S77, S102–S103. **Ambiguity:** “When feasible” needs recorded infeasibility.

### S105 — Freeze versioned literature packets and make re-entry explicit

- **Source:** §8.4, lines 1167–1197. **Category:** interface / provenance / retrieval. **Summary:** `LiteratureQuery` binds ProblemContract hash, interpretation, statements/formulas/objects/techniques/equivalents, optional authors/sources/cutoff, and citation/formal-library expansion. `SourcePacket` contains packet ID, complete query log, theorem records, negative coverage, conflicts, snapshot/corpus versions/hash and is immutable. Targeted re-entry creates a linked new version naming the exact gap.
- **Inputs → outputs:** LiteratureQuery → immutable versioned SourcePacket. **Invariants:** Old packets never mutate; worker information provenance is reconstructable. **Failure:** Unlogged re-entry or hash/version mismatch rejects reuse. **Integrations:** Retrieval, packet store, controller. **Acceptance:** Packet hash verifies and version graph names each re-entry reason. **Dependencies:** S51, S71–S73. **Ambiguity:** Negative-search coverage schema is unspecified.

### S106 — Return exact premise provenance and require elaboration plus informal-link audit

- **Source:** §8.5, lines 1199–1215. **Category:** formal retrieval / semantic security. **Summary:** Retrieve premises using natural claim, Lean goal/context/imports/Mathlib commit/max count and dense/lexical/type/dependency/sketch modes. Every candidate includes exact declaration/type/imports/file/commit/dependencies/scores and current-context compilation. Worker use requires elaboration; a separate source auditor ensures informal paper results were not strengthened during formal linkage.
- **Inputs → outputs:** Typed/informal retrieval request → provenance-complete PremiseCandidate list and audit status. **Invariants:** Retrieval and formal compilation do not establish informal scope. **Failure:** Non-elaborating or strengthened candidate cannot be used. **Integrations:** Lean, theorem DB, import auditor. **Acceptance:** Accepted premise records show successful current-context elaboration and source audit where linked. **Dependencies:** S73, S78. **Ambiguity:** Sketch-reflect mode is not defined here.

### S107 — Select evidence by claim type and keep snippets/summaries as leads

- **Source:** §8.6, lines 1217–1230. **Category:** evidence policy / novelty / provenance. **Summary:** Historical wording uses exact original bytes/version history; current truth uses latest corrected version/errata plus independent proof; encoded truth uses pinned formal artifact/axiom report and independent check; intended interpretation uses context/definitions/revisions/expert review; open status uses fresh multi-source search; novelty uses original/later literature, citation directions, synonyms/equivalents, and expert review. Respect each caveat. Search snippets/model summaries are leads; curated records are versioned claims, not underlying theorems.
- **Inputs → outputs:** Claim type and candidate sources → evidence-priority plan/verdict. **Invariants:** No universal paper/formal/database ordering. **Failure:** Wrong source class or ignored erratum/caveat blocks conclusion. **Integrations:** Intake, retrieval, Lean, novelty/status gates. **Acceptance:** Auditor chooses/records the matrix row and corroboration. **Dependencies:** S99–S100. **Ambiguity:** Expert-review independence standard is not defined here.

## Section 9: Lean and external formal-verification workflow

### S108 — Complete all immediate Lean-production repairs before enabling evidence

- **Source:** §9.1, lines 1234–1245. **Category:** formal security / release engineering / provenance. **Summary:** Before production Lean evidence: make `require_kernel=true` non-overridable for promotion; reject `aristotle_reported`; preserve/validate verification method, intent/correspondence cert IDs, provider model/build/request IDs, toolchain/import/axiom/replay hashes; require approved intent and formal-correspondence certificates; pin Lean/Lake/Mathlib/Aristotle client/dependencies and mark unattested mutable server model non-reproducible; put standalone scripts under the same feature/run contract; fingerprint complete behavior/import closure including literature/adjudication/formal/evidence adapters; and clean offline rebuild plus placeholder/`sorry`/unsafe-axiom scan.
- **Inputs → outputs:** Formal evidence/config/runtime → enabled validated evidence or production-disabled rejection. **Invariants:** All eight preconditions are conjunctive for enabling/promotion as applicable. **Failure:** Any absent repair fails closed. **Integrations:** Lean/Aristotle, schema, feature policy, cache, build scanner. **Acceptance:** A production-readiness checklist/test proves every item and non-overridability. **Dependencies:** S42, S44. **Ambiguity:** “Unsafe axiom” whitelist is §9.3 policy.

### S109 — Never use Aristotle as the trusted checker

- **Source:** §9.1, line 1247. **Category:** trust / security. **Summary:** Aristotle may generate formalization/proof candidates only; it is never the trusted checker.
- **Inputs → outputs:** Aristotle result → quarantined Lean candidate. **Invariants:** Trust is rooted in local kernel/independent path. **Failure:** Vendor-only success is rejected as proof evidence. **Integrations:** External adapter, sandbox, Lean verify. **Acceptance:** Trust-policy graph has no Aristotle terminal verifier edge. **Dependencies:** S13, S108. **Ambiguity:** None.

### S110 — Build and freeze the L0 semantic target package

- **Source:** §9.2 L0, lines 1249–1259. **Category:** formal intake / semantic validation. **Summary:** From an approved interpretation create 2–3 Lean statement candidates, explicitly define objects/reuse Mathlib only when semantically correct, backtranslate, test examples/anti-examples, prove candidate equivalence where feasible, run paraphrase-invariance and mutation-covariance tests, and freeze the approved declaration hash.
- **Inputs → outputs:** Approved interpretation/source context → tested candidate targets and locked declaration. **Invariants:** Reuse is semantic, not name-based. **Failure:** Failed tests/equivalence keep candidates unresolved; no hash approval. **Integrations:** Intake firewall, Mathlib, compareStatements. **Acceptance:** Target package contains all tests/backtranslations and frozen hash. **Dependencies:** S24, S66. **Ambiguity:** Equivalence is optional when infeasible but non-equivalence remains explicit.

### S111 — Formalize L1 risk sentinels early

- **Source:** §9.2 L1, lines 1261–1271. **Category:** formalization / failure detection. **Summary:** Early sentinels cover type/domain sanity, boundary/degenerate cases, monotonicity/symmetry/invariance assumptions, finite cases driving conjectures, and the central lemma with highest calibrated centrality/semantic-risk/false-branch-cost combination, exposing hidden regularity/finiteness/choice/decidability/nonzero assumptions before proof entrenchment.
- **Inputs → outputs:** Target package/claim risks → Lean sentinel declarations and diagnostics. **Invariants:** High-risk semantic assumptions are tested before deep proof. **Failure:** Sentinel failure revises/refutes target/blueprint instead of being ignored. **Integrations:** Controller, claim graph, Lean. **Acceptance:** Risk ranking selects the central sentinel and results precede proof assembly. **Dependencies:** S52, S110. **Ambiguity:** Calibration formula differs from broader §9.5 queue only in included factors; implementations should document mapping.

### S112 — Keep `sorry` only in quarantined L2 blueprints and reject debt-hiding helpers

- **Source:** §9.2 L2, lines 1273–1277. **Category:** formal development / security / search. **Summary:** Proof blueprints may use `sorry` only in a quarantined development branch never imported by production evidence; every hole is a graph node with source claim, exact goal, expected premises, semantic invariants, and dependencies. Try target directly first; after failure create only smallest justified helpers and reject target restatements/difficulty sinks.
- **Inputs → outputs:** Locked target/graph → quarantined declaration blueprint and hole nodes. **Invariants:** Production import closure excludes development branch. **Failure:** Placeholder leakage or debt-hiding helper rejects evidence/fitness. **Integrations:** Claim graph, Lean cache, verified-debt controller. **Acceptance:** Import scan proves isolation; every hole schema is complete. **Dependencies:** S22, S91. **Ambiguity:** Direct-search budget is unspecified.

### S113 — Use the L3 proof-state portfolio and diagnostic-specific repair

- **Source:** §9.2 L3, lines 1279–1292. **Category:** formal search / integration / failure recovery. **Summary:** Portfolio whole-proof compiler agents, premise-retrieval/best-first tactics, multi-goal trees, specialized generation/repair models, optional Aristotle candidates, standard/domain tactics, supported ATP/SMT/SAT exports with Lean reconstruction/certificates, and formal-negation/counterexample search. Search tactic segments and auxiliary lemmas, and route syntax, missing premise, false target, library gap, and decomposition failure to distinct repair policies.
- **Inputs → outputs:** GoalCapsule/action budget → action results, proof terms, diagnostics, repaired blueprint/counterexample. **Invariants:** External solver closure remains checked; Aristotle is optional/untrusted. **Failure:** Diagnosis routes locally rather than whole-proof retry; false target can refute. **Integrations:** Lean service, theorem DB, external solvers, controller. **Acceptance:** Routing tests cover all diagnostic classes and portfolio paths. **Dependencies:** S81, S109, S112. **Ambiguity:** Portfolio composition may vary with availability.

### S114 — Synchronize informal and formal dependency cones through shared claim IDs

- **Source:** §9.2 L4, lines 1294–1302. **Category:** integration / semantic consistency / failure. **Summary:** Every logically active informal sentence points to a Lean declaration, rigorous informal claim with explicit formalization debt, or audited source theorem. Formal and prose artifacts share claim IDs; formal counterexamples/hypothesis changes invalidate prose dependencies, and informal clarification invalidates affected formal statements until correspondence is reapproved.
- **Inputs → outputs:** Informal/formal edits and evidence → synchronized graph plus invalidation/reapproval events. **Invariants:** No orphan logical step; changes propagate both ways. **Failure:** Stale dependent cone is revoked and cannot release. **Integrations:** Claim graph, proof document, Lean, correspondence gate. **Acceptance:** Bidirectional mutation tests invalidate exact affected nodes and require reapproval. **Dependencies:** S35, S80. **Ambiguity:** “Does real logical work” needs reviewer/tool enforcement.

### S115 — Harden L5 release artifacts under clean, independently checked conditions

- **Source:** §9.2 L5, lines 1304–1311. **Category:** formal security / reproducibility / release. **Summary:** Eliminate `sorry`, `admit`, placeholders, generated axioms, and unauthorized `unsafe`; minimize imports; compute transitive axiom closure and enforce explicit whitelist for every theorem; build clean pinned checkout offline; require a second checker/trust path for untrusted generated Lean; archive source, manifest, toolchain, build log, environment/container and theorem hashes; produce graph-linked human-readable proof.
- **Inputs → outputs:** Candidate project/target/policy → hardened FormalCertificate and release bundle. **Invariants:** Network-disabled clean replay and complete trust closure. **Failure:** Any forbidden mechanism, unapproved axiom, replay/check failure, or archive gap blocks formal release. **Integrations:** Build sandbox, checker, artifact store, proof renderer. **Acceptance:** Release bundle independently reconstructs and verifies. **Dependencies:** S108, S114. **Ambiguity:** Import minimization is optimization; trust checks are mandatory.

### S116 — Implement the Lean service API and complete `FormalCertificate`

- **Source:** §9.3 API/certificate, lines 1313–1347. **Category:** service interface / provenance / formal security. **Summary:** Provide environment creation, elaboration, goal-state, premise search, action trials, declaration verification, and statement comparison with the specified environment/goal/budget/hash flags. Verification requires clean replay, placeholder rejection, axiom policy, and independent checker. Certificate stores expected elaborated type, declaration/proof-term, immutable target module, full source/import tree, transitive axioms/whitelist, placeholder/unsafe findings, trust policy, checker and independent-checker identities/versions/log hashes.
- **Inputs → outputs:** Pinned environment and immutable target/candidate hashes → diagnostics/actions/FormalCertificate. **Invariants:** API calls bind EnvironmentId and immutable content. **Failure:** Any required check/field failure prevents certificate issuance. **Integrations:** Mathlib project, theorem retrieval, checkers, artifact store. **Acceptance:** Contract tests validate all operations/fields and clean replay flags. **Dependencies:** S115. **Ambiguity:** API transport/implementation is unspecified.

### S117 — Isolate the target and compare elaborated expected types, not names

- **Source:** §9.3 certificate semantics, line 1347. **Category:** formal security / anti-tampering. **Summary:** Store the approved target in a separate immutable module; candidate code cannot redefine its imports, namespaces, options, macros, or declaration. Verification compares candidate theorem’s elaborated type with the locked expected expression rather than declaration name.
- **Inputs → outputs:** Immutable target module/expected type and candidate → equality/mismatch verdict. **Invariants:** Candidate cannot control target semantics or elaboration context. **Failure:** Any target-context mutation/type mismatch rejects. **Integrations:** Lean environment builder, hash store. **Acceptance:** Adversarial namespace/macro/option/name collision tests fail. **Dependencies:** S110, S116. **Ambiguity:** Definitional versus propositional equality policy should be explicit.

### S118 — Reserve formal equivalence for checked implication artifacts

- **Source:** §9.3, line 1349. **Category:** semantic evidence / acceptance. **Summary:** `compareStatements` may output `equivalent` only with checked `A ↔ B` or both implication proofs; model/backtranslation judgment can output only `plausibly_corresponding`.
- **Inputs → outputs:** Declarations/relation and proof artifacts → equivalent or plausible/unresolved status. **Invariants:** Natural-language plausibility never becomes formal equivalence. **Failure:** Missing proof artifacts downgrades result. **Integrations:** Lean service, interpretation reconciliation. **Acceptance:** API refuses formal-equivalent enum without proof hashes. **Dependencies:** S110, S116. **Ambiguity:** Other relations (stronger/weaker) should analogously return checked implication evidence, though only equivalence is explicit.

### S119 — Enforce an explicit release axiom/native-computation policy

- **Source:** §9.3, line 1351. **Category:** trust policy / security. **Summary:** Release policy explicitly lists permitted axioms (example classical whitelist: `propext`, `Quot.sound`, `Classical.choice`), rejects `sorryAx` and unapproved user axioms, and stores transitive closure. Kernel-bypassing native mechanisms such as `native_decide` are forbidden or treated as external computation with separately checked certificate.
- **Inputs → outputs:** Transitive axiom/native-mechanism report and policy → whitelist decision/evidence route. **Invariants:** Hidden axioms/native execution cannot masquerade as kernel proof. **Failure:** Unapproved use blocks formal release or routes to external evidence tier. **Integrations:** Lean scanner, computation verifier. **Acceptance:** Tests catch transitive custom axioms and `native_decide`. **Dependencies:** S115–S116. **Ambiguity:** Example whitelist is project-specific, not universally mandated exactly.

### S120 — Key `GoalCapsule` by full elaborated context and trust policy

- **Source:** §9.3, lines 1353–1360. **Category:** cache / formal provenance. **Summary:** A goal identity binds Lean version, Mathlib commit, project/import/options hash, elaborated local context, exact target expression, and trust policy; pretty-printed text is insufficient.
- **Inputs → outputs:** Elaborated environment/goal → canonical GoalCapsule key. **Invariants:** Behavior/trust-relevant context is part of identity. **Failure:** Any key-field change causes cache miss. **Integrations:** Lean proof-state cache, premise search, action trials. **Acceptance:** Alpha-equivalent/context-different and pretty-identical/trust-different tests do not collide. **Dependencies:** S39, S91. **Ambiguity:** Canonicalization of elaborated expressions is unspecified.

### S121 — Turn missing library facts into independently tested reusable infrastructure

- **Source:** §9.4, lines 1362–1374. **Category:** formalization / retrieval / reuse / governance. **Summary:** When Mathlib lacks a theorem, verify absence across equivalent names/types, import-audit the informal result, create a local namespaced statement with source/assumptions/claim ID, decompose into reusable library-quality lemmas, prove/test independently of final target, score corpus-wide reuse, and upstream only after human review and licensing checks.
- **Inputs → outputs:** Missing-premise diagnosis/source theorem → local verified library package/reuse score and optionally reviewed upstream contribution. **Invariants:** Final-target dependence does not substitute for independent testing. **Failure:** Found existing theorem redirects retrieval; failed audit/proof/license blocks use/upstreaming. **Integrations:** Mathlib search, import auditor, Lean CI, license/human review. **Acceptance:** Package has source, tests, independent build and governance approvals. **Dependencies:** S106, S113. **Ambiguity:** “Truly absent” search completeness is heuristic.

### S122 — Prioritize formal coverage by risk-weighted benefit per cost, never as truth

- **Source:** §9.5 formula, lines 1376–1393. **Category:** resource control / evaluation. **Summary:** Formalization priority is `(centrality + semantic risk + dispute probability + downstream loss + reuse, each weighted) / expected formalization cost`; it is a queue priority, not truth score.
- **Inputs → outputs:** Claim graph/risk/dispute/reuse/cost estimates → formalization priority. **Invariants:** Unformalized or low-priority does not mean false; high-priority does not mean true. **Failure:** Missing estimates retain uncertainty and explicit debt. **Integrations:** Controller, Lean queue, telemetry. **Acceptance:** Score implementation includes all terms and is stored separately from evidence tier. **Dependencies:** S52, S111. **Ambiguity:** Weights/calibration are unspecified.

### S123 — Publish expensive-to-formalize results with honest evidence profiles only

- **Source:** §9.5, lines 1395–1403. **Category:** release / acceptance / failure. **Summary:** For convincing but prohibitively expensive claims, retain exact assumptions and `SINGLE`/`DOUBLE_INDEPENDENT` informal-review reports, formally verify surrounding sentinels/high-risk reductions, seek independent expert review or second proof, and publish remaining debt; never call the full result formally verified. A novel resolution may be “rigorous informal proof” after two genuinely independent rigorous reviews, but the system must never imply stronger evidence.
- **Inputs → outputs:** Informal proof, cost rationale, sentinel/formal/reviewer evidence → accurately scoped release profile. **Invariants:** Evidence label never exceeds support. **Failure:** Missing independence/debt disclosure blocks rigorous-informal/full claims. **Integrations:** Review service, Lean sentinels, release renderer. **Acceptance:** Output explicitly lists review count/independence, formal coverage, and debt. **Dependencies:** S2, S115, S122. **Ambiguity:** “Prohibitively expensive” and “genuinely independent” require policy definitions.

### S124 — Constrain hosted prover inputs and record reproducibility/provenance honestly

- **Source:** §9.6 input/provenance policy, lines 1405–1415. **Category:** external integration / privacy / provenance / security. **Summary:** Send external services only the locked formal target, exact toolchain/project, bounded leaf where possible, provenance-bearing theorem packets, and request full source artifacts rather than status. Before sending, enforce license, confidentiality, and data-residency policy. Record provider request/model/build IDs, timestamp, raw I/O, and client version; unattested mutable server revisions are marked non-reproducible.
- **Inputs → outputs:** Policy-approved locked goal/package → external request and immutable provenance record/candidate source. **Invariants:** Client version never pretends to pin server model. **Failure:** Policy violation blocks transmission; status-only response cannot prove. **Integrations:** External adapter, DLP/license policy, artifact store. **Acceptance:** Request audit shows locked hashes, approvals, raw I/O and reproducibility flag. **Dependencies:** S105, S109. **Ambiguity:** Provider confidentiality constraints may limit raw-output retention and must be reconciled before use.

### S125 — Quarantine returned Lean in a disposable least-privilege sandbox and independently audit it

- **Source:** §9.6 returned-code policy, line 1417. **Category:** security / formal acceptance / failure. **Summary:** Treat returned Lean as executable metaprogram/tactic code: quarantine it; build only in a disposable unprivileged sandbox with no network/credentials, read-only source/dependency mounts, bounded CPU/RAM/time/processes, and captured outputs—never on host. Then source-scan, audit axioms/imports, review correspondence, check isolated target type, and independently check before admission. Provider diversity does not create verifier diversity when trust base is shared.
- **Inputs → outputs:** External Lean source → sandbox logs and independently audited FormalCertificate or rejection. **Invariants:** Host and credentials are never exposed; search-provider identity is separate from verifier trust. **Failure:** Sandbox/policy/audit/check failure rejects and preserves quarantine. **Integrations:** Sandbox, source scanner, Lean target module, correspondence and independent checker. **Acceptance:** Escape/resource/network tests fail safely and admission requires every post-build audit. **Dependencies:** S109, S115–S119, S124. **Ambiguity:** Independent checker may diversify implementation while retaining the same Lean logic; trust report must say so.

## Coverage and extraction notes

- Total temporary requirements: **125** (`S1`–`S125`).
- Background sections 1–4 are included wherever an empirical limitation becomes a binding negative claim, evaluation rule, trust constraint, migration decision, or invariant. Pure literature description without a design/evaluation implication is intentionally not converted into a requirement.
- Repeated mandates are retained when they impose a distinct acceptance surface (for example, executive priority, current-repository repair, service schema, and release hardening). Dependencies identify intentional overlap.
- Percentages and branch counts described as initial defaults remain requirements to implement as defaults **and** requirements to ablate before treating them as settled policy (§7.8, lines 972–987).
- Sections 1–9 leave several policy parameters intentionally open: gate evidence thresholds, signer/key governance, model-lineage attestation, similarity thresholds, posterior weights, `K`, freshness, and expert independence. Implementations must not silently hard-code those choices as specification facts.
