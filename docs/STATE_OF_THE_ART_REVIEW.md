# State of the Art in Autonomous Mathematical Research

Research cutoff: 2026-07-12. Most 2026 systems below are preprints. “Released proof artifact,” “expert-reviewed result,” “kernel-checked theorem,” and “reproducible generation system” are different evidence levels.

## What the field has and has not established

No public system currently closes all four gates needed by this project:

1. mathematical correctness;
2. fidelity to the intended informal problem;
3. novelty relative to prior literature;
4. mathematical significance.

Formal systems can give unusually strong evidence for the exact formal expression but cannot by themselves establish that it is the intended theorem or a novel contribution. Natural-language systems can work closer to research practice but still show wrong-interpretation, citation, and verifier-consensus failures. Closed systems may release impressive individual artifacts without making their generation process reproducible.

## Natural-language long-horizon systems

### Aletheia

[Aletheia](https://arxiv.org/abs/2602.10177) uses nested generator, verifier, and reviser work with search/tool access around a Gemini Deep Think model. The public evidence includes papers and selected artifacts, not the agent code, weights, complete trajectories, or a reproducible API. Its verifier is an independent natural-language context plus expert grading, not a formal kernel.

The separate [Erdős sweep](https://arxiv.org/abs/2601.22401) is especially relevant. It attempted roughly 700 then-open problems for one week, generated 212 candidates, and obtained definitive grading for 200. Sixty-three were technically correct in some sense, but only thirteen represented meaningful progress; wrong-intent and vacuous answers were major failure modes. The current documented result is two full resolutions (#652 and #1051) and two partial solutions (#654 and #1040), plus rediscoveries or literature matches. The earlier shorthand “five novel Erdős solutions” is not a safe current claim.

Reusable lesson: aggressive search and revise/check loops can produce real progress, but answer validity must be split into correctness, intent, novelty, and importance. Citation existence is insufficient; theorem hypotheses and applicability need auditing.

### QED

[QED](https://arxiv.org/abs/2604.24021) and its [public repository](https://github.com/proofQED/QED) provide the clearest reproducible natural-language control loop among the reviewed systems: literature survey, proof generation, structural verification, detailed checking, citation tags, expansion of original steps, optional lemma-DAG decomposition, a regulator choosing proof revision versus plan revision versus rewrite, and exact-stage resume artifacts.

The paper reports five original works from eighteen expert-proposed projects. Its verifier accepted 17 of 214 candidates in the reported GPT-5.5 runs, and experts accepted all 17. That is an observed zero false-positive count among accepted candidates, not a general false-positive bound; false negatives are unmeasured, the project set is small, and verifier/generator model lineage is not broadly independent. Reported successful-run costs range roughly from $50 to $1,000.

Reusable lesson: preserve structural-before-local verification, immutable-statement checks, expansion of original contributions, failure memory, and regulator decisions. Pin paper-era prompts/models because the repository defaults can drift.

### Danus

[Danus](https://arxiv.org/abs/2607.06447) and its [Apache-licensed repository](https://github.com/frenzymath/Danus) supply the most relevant open claim-memory design: a coordinator, parallel workers, role-gated claim submission, a fresh verifier, a content-addressed dependency DAG, explicit dependency edges, negative memory, and cascading revocation. Its own [security documentation](https://github.com/frenzymath/Danus/blob/main/docs/security-and-trust.md) correctly says its accepted facts are LLM-verified, not formally verified.

Reported case studies include a run with thousands of accepted facts and dependencies over several days. Human audit still found a rational-versus-integral target error, an incomplete manuscript proof, and a bad literature definition that forced revocation of 23 dependent facts. The mechanism is highly relevant; the admission verifier is the weak link.

Reusable lesson: adopt dependency-aware facts and revocation, but label evidence tiers and require executable or independent evidence for high-centrality facts.

### AI Co-Mathematician

The [AI Co-Mathematician](https://arxiv.org/abs/2605.06651) uses an interactive top-level coordinator, user-approved intent, asynchronous workstreams, specialist agents, a shared persistent filesystem, messages, durable failed-hypothesis records, literature/code/cloud tools, and a living research artifact. The system is closed and used uncapped inference compute in reported studies.

Its historically reported FrontierMath Tier 4 v1 score was 23/48 (48%). The corrected [FrontierMath v2](https://epoch.ai/benchmarks/frontiermath-tier-4) changed many items and currently reports a materially different score; v1 and v2 are not directly comparable. The paper explicitly identifies reviewer-pleasing consensus, nontermination, and rigor illusion.

Reusable lesson: retain human intent approval, asynchronous bounded workstreams, persistent dead ends, uncertainty, and a continuously auditable paper—but keep a raw-model baseline because orchestration complexity is not automatically beneficial.

### FirstProof batch 2

[FirstProof batch 2](https://arxiv.org/abs/2606.18119), its [full code/log release](https://github.com/1stproof/batch-2), and the [evaluation report](https://1stproof.org/assets/docs/report.pdf) provide the strongest controlled comparison reviewed here: fresh containers, one-shot 24-hour runs, complete logs, and double-blind expert review on ten unpublished human-solved research problems.

At least one entrant passed seven of ten. ProofCouncil passed six, UCLA Moonshot five, a raw ChatGPT 5.5 Pro baseline five, and Princeton Momus one. The two strongest elaborate harnesses cost roughly 27–41 times the raw baseline while improving by at most one accepted problem in this small sample. Citation errors remained common, and Momus reported corrupted runs from timeouts/races.

Reusable lesson: every architecture claim needs a raw-model/cost baseline, failure-complete logs, and ablations. More agents are not evidence of better mathematics.

## Formal proof systems and agents

### AlphaProof and AlphaGeometry2

The [AlphaProof Nature paper](https://www.nature.com/articles/s41586-025-09833-y) describes AlphaZero-style policy/value search in Lean, large-scale autoformalized training, self-play, and target-specific reinforcement learning. At IMO 2024, experts manually formalized non-geometry problems; AlphaProof solved three and AlphaGeometry2 solved one, contributing to 28/42. The main training cost was reported at roughly 80,000 TPU-days; inference and target-specific training budgets varied by orders of magnitude. Public releases contain papers, pseudocode, corrected [miniF2F](https://github.com/google-deepmind/miniF2F), [formal IMO artifacts](https://github.com/google-deepmind/formal-imo), and proofs—not the decisive weights/training system.

[AlphaGeometry2](https://www.jmlr.org/papers/v26/25-1654.html) combines Gemini-generated constructions, an expanded geometry language, a symbolic DDAR engine, and parallel search trees sharing derived facts. It reports 42/50 geometry problems. Its [public repository](https://github.com/google-deepmind/alphageometry2) explicitly releases DDAR and examples, some with manually supplied auxiliary points, not the complete Gemini/SKEST system.

Reusable lesson: a hard symbolic checker, shared verified facts, and enormous search can be powerful. Cost and manual formalization make the full approach unsuitable as the default Erdős pipeline.

### AlphaProof Nexus

[AlphaProof Nexus](https://arxiv.org/abs/2605.22763) couples stateful Gemini Lean editing, optional AlphaProof queries, evolutionary sketch sharing, and a goal cache keyed by exact Lean context/target. It reports 9/353 Formal Conjectures and 44/492 autoformalized OEIS conjectures, with costs of a few hundred dollars per problem. The [results repository](https://github.com/google-deepmind/alphaproof-nexus-results) contains outputs and reports, not the engine/weights. Failures include single-`sorry` sketches and hallucinated literature lemmas.

Reusable lesson: cache exact elaborated goals, proofs, formal disproofs, tactic segments, and values; replay all hits under the current kernel. Evolve proof programs/blueprints, not unrestricted persuasive prose.

### AxiomProver and AXLE

[Axiom Math](https://axiommath.ai/) describes AxiomProver as an autonomous multi-agent theorem prover. Its model, orchestration, memory, search policy, and training are closed. Public [Putnam 2025 artifacts](https://github.com/AxiomMath/Putnam2025) cover all twelve problems in Lean: eight were solved in the official window and four afterward. The artifacts support kernel replay and axiom/sorry audits; they do not reproduce generation.

[AXLE](https://arxiv.org/abs/2606.26442) and its [SDK/docs](https://github.com/AxiomMath/axiom-lean-engine) expose a hosted Lean engine with verification, extraction, repair, simplification, disproof, and normalization tools across versions. AXLE is tooling, not AxiomProver. Its documentation warns that adversarial metaprogramming can exploit a trusted environment; untrusted final proofs should also be checked with SafeVerify, Comparator, `lean4checker`, or a clean pinned local toolchain. Compilation is not semantic-intent validation.

Reusable lesson: expose Lean as a service to agents, but preserve a clean independent final replay and a separate statement-fidelity gate.

### DeepSeek-Prover-V2

[DeepSeek-Prover-V2](https://arxiv.org/abs/2504.21801) and its [official repository/weights](https://github.com/deepseek-ai/DeepSeek-Prover-V2) use an informal proof to propose recursive Lean `have` subgoals, a smaller prover to close them, compiler-verified cold-start data, and verifier-rewarded training. The 671B model reports 82.4% miniF2F pass@32 and 88.9% with very large sampling, plus 49/658 PutnamBench with expanded search. The complete training pipeline/data are not public. A [ProofGate audit](https://openreview.net/forum?id=uMTF54muYL) found released miniF2F proofs kernel-faithful but also illustrates that statement alignment is a separate problem.

Reusable lesson: recursive subgoal decomposition and compiler feedback are credible mechanisms. Do not compare pass@k without matching sample, token, timeout, and toolchain budgets.

### Goedel-Prover-V2 and Goedel-Architect

[Goedel-Prover-V2](https://arxiv.org/abs/2508.03613) and its [public code/weights](https://github.com/Goedel-LM/Goedel-Prover-V2) add scaffolded synthetic tasks, two-round Lean-feedback correction, and checkpoint averaging. Reported miniF2F results reach 90.4% with correction and larger values at high pass@k; PutnamBench results also rise with large sampling. Independent artifact audit noted that a public miniF2F file contained input statements with `sorry`, so benchmark claims still require rerun.

The very recent [Goedel-Architect](https://arxiv.org/abs/2606.06468) generates a formal dependency blueprint, proves leaves in parallel, formally negates suspected false nodes, and refines failed regions while retaining successful ones. Its reported results and low aggregate Putnam costs are striking but fresh and not independently audited; “pass@1” includes many global refinements and tool calls.

Reusable lesson: the blueprint/AND-OR graph, formal falsification of nodes, parallel leaves, and selective refinement fit this project better than monolithic proof regeneration.

### OProver, Seed-Prover, LEAP, and LeanMarathon

[OProver](https://arxiv.org/abs/2605.17283), its [Apache pipeline](https://github.com/multimodal-art-projection/OProver), weights, and OProofs data form the strongest apparently open 2026 snapshot: retrieval, Lean feedback, repair, SFT, and RL use a shared multi-round interface; OProofs reports 1.77M statements and 6.86M compiler-verified proofs. The 32B model reports 93.3% miniF2F pass@32 and lower research-benchmark rates. It is new and lacks a full independent rerun; training-data provenance/contamination need audit.

[Seed-Prover](https://github.com/ByteDance-Seed/Seed-Prover) combines whole-proof generation, lemma refinement, compiler feedback, summaries, and progressively heavier search. Released Lean proofs are checkable, but the prover code, weights, and training data are not; heavy runs can last hours or days.

[LEAP](https://arxiv.org/abs/2606.03303) uses an AND-OR DAG, direct attempts, reviewed lemma decomposition, memoization, backtracking, and anticipatory lemmas. Its public repository contains benchmarks/solutions, not a fully reproducible Gemini system. Reported individual problems can require tens to thousands of calls.

[LeanMarathon](https://arxiv.org/abs/2606.05400) is most valuable for governance: contract-scoped roles share a Lean blueprint as formal skeleton, prose graph, and system of record; target review precedes proof work; isolated worktrees merge through CI and two-way dependency/prose parity. Its [harness and artifacts](https://github.com/YuanheZ/LeanMarathon) are public. Evidence is limited to three expensive runs, but the workflow is directly implementable.

Reusable lesson: use open models/tooling for an affordable baseline, and borrow blueprint governance, isolation, and CI even when the strongest prover is closed.

## Retrieval, caching, and formalization fidelity

[LeanSearch v2](https://arxiv.org/abs/2605.13137) combines Mathlib informalization, dense retrieval/reranking, and sketch–retrieve–reflect; its [code/data](https://github.com/frenzymath/LeanSearch-v2) are public. [LeanDojo](https://arxiv.org/abs/2306.15626) provides extracted proof states, tactics, accessible premises, and dependency-aware negatives. [Pantograph](https://arxiv.org/abs/2410.16429) exposes explicit goal selection, multiple goals, sketches, and tree search.

The [live proof-state snapshot paper](https://arxiv.org/abs/2605.25556) reports large speedups by elaborating once and branching tactics from a live state, but the patched implementation was not public at the cutoff. Safe cache identity should include Lean version, Mathlib commit, imports, options, elaborated local context, exact target expression, and trusted-axiom policy. Textual goal strings are not enough.

Autoformalization evidence strongly rejects “compiles means faithful.” [Beyond Compilation](https://arxiv.org/abs/2606.31002) reports a large gap between compilation and consensus faithfulness on graduate mathematics. A [perturbation audit](https://arxiv.org/abs/2606.14867) found seven autoformalizers unstable under meaning-preserving rewrites and often unresponsive to local semantic edits. Required defenses are multiple formalization candidates, formal equivalence where possible, backtranslation as evidence rather than proof, global paraphrase invariance, local mutation covariance, vacuity/counterexample probes, independent target review, and a frozen theorem hash before proof search.

[TheoremGraph](https://arxiv.org/abs/2606.25363) offers millions of informal candidate edges, hundreds of thousands of typed Lean declarations, and cross-formality matches. Informal/cross-formality edges are probabilistic discovery aids; only elaborator/kernel edges belong in the correctness plane.

## Evolutionary and population search

[MaxProof](https://arxiv.org/abs/2606.13473) uses proof, verifier, and critique-conditioned repair experts plus population search, pessimistic multi-verification, patch/rewrite offspring, and tournament selection. Its natural-language outputs are not formal proofs, and the paper documents verifier reward hacking. [FunSearch](https://www.nature.com/articles/s41586-023-06924-6) and [AlphaEvolve](https://arxiv.org/abs/2506.13131) evolve executable programs under objective evaluators and island/diversity mechanisms; their core language models/distributed infrastructure are not fully open.

Reusable lesson: evolve lemma decompositions, constructions, proof programs, and counterexample generators only when the evaluator is hard, replayable, and multi-objective. Fitness should keep correctness, statement fidelity, novelty, reuse, and cost separate.

## Conclusions required for this project

### Strongest proven mechanisms

- hard kernel or exact-checker verification for the exact encoded target;
- immutable statement/target review before expensive proof search;
- compiler feedback, recursive subgoals, and dependency blueprints;
- independent structural review before local proof review;
- persistent negative memory and exact-stage resume;
- claim dependency graphs with cascading revocation;
- diverse candidates plus pessimistic selection;
- controlled expert evaluation and raw-model/cost baselines.

### Promising but unproven mechanisms

- long-lived live Lean proof states and content-addressed goal/value caches at research scale;
- evolutionary sharing of formal sketches across open research problems;
- calibrated problem-selection bandits from verified outcomes;
- large informal/formal theorem graphs for research retrieval;
- LLM Fact Graphs when high-centrality admission is backed by executable evidence.

### Mechanisms that appear overhyped

- agent count or orchestration depth as a performance metric;
- self-reported confidence/completeness;
- same-family verifier consensus as correctness;
- Lean compilation as proof of informal intent, novelty, or significance;
- pass@k comparisons without equal budgets;
- polished success artifacts without failed traces, costs, and versions.

### Reproducible systems

QED’s orchestration, Danus’s public harness, LeanDojo, Pantograph, LeanSearch v2, DeepSeek-Prover-V2 checkpoints, Goedel-Prover-V2 code/weights, OProver’s released pipeline/weights/data, AlphaGeometry1/DDAR, and LeanMarathon’s governance harness are substantially inspectable. Reproduction strength varies, and claimed benchmark numbers still require rerun.

### Closed or proprietary systems

Aletheia, AI Co-Mathematician, AxiomProver, AlphaProof, the complete AlphaProof Nexus engine, AlphaGeometry2’s Gemini/SKEST components, Seed-Prover’s generator, LEAP’s complete Gemini system, MaxProof orchestration, and AlphaEvolve’s production engine are closed or only partially released.

### Ideas relevant to this project

Statement-fidelity gates, theorem-level retrieval, dependency blueprints, exact goal caches, compiler/exact feedback, claim admission tiers, cascading revocation, protected exploration, normalized outcome ledgers, and separate correctness/intent/novelty/significance reports.

### Ideas already present in this project

Fresh contexts, four search perspectives, statement hashes, a validated dependency DAG, adversarial reviewer roles, a regulator, persisted raw artifacts, a fail-closed deterministic gate, and adaptive shared rate limiting.

### Ideas already present in `AGENTS.md`

Truth/search/control/communication planes, exact statement locking, theorem-level retrieval, Fact Graphs, revocation, Lean as an evidence fabric, executable construction search, diverse programs, separate outcome probabilities, append-only ledgers, calibrated allocation, and auditable publishing.

### Genuinely new integration opportunities

1. Bind the searcher’s exact pipeline fingerprint and budget directly to claim-level outcome learning.
2. Combine QED’s regulator with a Goedel-Architect/LeanMarathon formal blueprint so it repairs only failed dependency regions.
3. Admit Danus-style facts through evidence tiers, with mechanically verified high-centrality facts and automatic revocation closure.
4. Use AlphaProof Nexus-style exact Lean goal hashes plus clean kernel replay, while recording formal disproofs and costs.
5. Evaluate statement formalization with paraphrase invariance and local mutation covariance before freezing the target.
6. Treat cross-problem formal infrastructure as its own searcher reward rather than counting only final theorem solves.
7. Maintain a raw-model baseline and automatically compute orchestration gain per dollar and per expert-review hour.
