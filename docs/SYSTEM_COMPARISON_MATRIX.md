# System Comparison Matrix

Cutoff: 2026-07-12. “Formal” means a proof assistant or exact symbolic checker checks an encoded target; it does not imply informal-statement fidelity or novelty.

| System | Public generation stack | Search/control | Durable memory | Verification | Evidence strength | Principal limitation | Best transferable mechanism |
| --- | --- | --- | --- | --- | --- | --- | --- |
| This project at `fd9c019` | Yes | 4 scouts → DAG → constructor → 7 reviews → regulator | Mutable run JSON + raw cache | LLM reviews + declared external artifact | Local tests; 0 verified math results | No executable verifier, retrieval, or selector | Fail-closed gate and role separation |
| This project, in-flight MVP | Yes | Corpus ranker + opt-in queue + existing proof loop | Source snapshots, cards, ledgers, cache metadata | Privacy-scanned gate/intent/disposition audit replay; authenticated adapters pending | 616/616 corpus; tests | All outcomes are audit-only; probabilities uncalibrated; scheduler experimental | Exact-context audit records with learning gated on authenticated provenance |
| Aletheia | No | Generator/verifier/reviser + search | Undisclosed | Independent NL verifier + experts | Expert-reviewed selected results | Closed; intent/citation failures | Intensive revise/check loop |
| Aletheia Erdős sweep | No | Broad one-week sweep | Partial artifacts | NL grading + experts | 2 full + 2 partial current meaningful record | 137/200 graded candidates fundamentally flawed | Separate meaningful progress from technical correctness |
| QED | Orchestration yes | Literature → proof → structural/local checks → regulate | Exact-stage artifacts/failure memory | NL verifier + experts | 17/17 verifier-accepted also expert-accepted in sample | No false-negative estimate; same-family verifier | Regulator and original-step expansion |
| Danus | Yes | Coordinator + 3–9 workers + fact submission | Content-addressed dependency DAG | Fresh LLM verifier + manuscript/human review | Six case studies | LLM facts are not formal; deep error amplification | Cascading revocation |
| AI Co-Mathematician | No | Interactive asynchronous workstreams | Shared filesystem, messages, failed hypotheses | Persistent NL reviewers + humans | Blind benchmark + case studies | Closed and uncapped compute | Intent approval and living research artifact |
| FirstProof batch 2 | Harnesses/logs yes | Four heterogeneous entrants | Entrant-specific | Double-blind experts | Best controlled research comparison | Only 10 problems | Raw-model/cost baseline |
| AxiomProver | No | Undisclosed multi-agent prover | Undisclosed | Lean kernel + human correspondence audit | Public Lean research/Putnam artifacts | Generation not reproducible | Formal artifacts with axiom audit |
| AXLE | Client/API yes | Stateless Lean tools | Request-level | Lean environment; strict tools available | Tool agreement studies | Hosted backend; metaprogram trust caveat | Isolated multi-version Lean service |
| AlphaProof | No | RL policy/value tree search + target RL | Search tree | Lean kernel | Nature paper + artifacts | Extreme compute and manual formalization | Hard evaluator + search |
| AlphaProof Nexus | Results only | Gemini edit loops + AlphaProof + evolution | Exact-goal cache | Lean kernel | Released proofs/reports | Engine/weights closed; high per-problem budget | Cache proof/disproof/value by exact goal |
| DeepSeek-Prover-V2 | Code/weights partly | Recursive subgoals + sampling | Generated trajectories | Lean kernel | Released weights; proof audit | Full training stack/data unavailable | Informal-to-`have` decomposition |
| Goedel-Prover-V2 | Code/weights | Scaffolded synthesis + two-round repair | Prompt/trajectory | Lean kernel | Public code/weights, author benchmarks | Released proof artifact gap noted by audit | Feedback repair + model diversity |
| Goedel-Architect | Paper | Formal blueprint + parallel leaves + refinements | Successful nodes retained | Lean kernel/formal negation | Very fresh author report | “Pass@1” hides many calls; no independent audit | Selective DAG refinement |
| OProver | Code/weights/data | Retrieval + Lean feedback + repair | Multi-round trajectories | Lean kernel | Broad open snapshot | New; contamination and rerun pending | Unified retrieval/repair interface |
| Seed-Prover | Proofs only | Whole proof + lemma refine + heavy search | Summaries | Lean kernel | Recheckable proofs | Generator/training closed; heavy budgets | Progressive search tiers |
| LEAP | Benchmarks/results | AND-OR DAG + backtracking/reuse | Memoized lemmas | Lean kernel | Reported ablation/results | Full system not released | Anticipatory lemmas and AND-OR graph |
| LeanMarathon | Harness/artifacts | Blueprint-governed parallel worktrees | Lean blueprint/system of record | Lean CI + target review | Three public expensive runs | Small run count; high cost | Contract scopes and merge gates |
| MaxProof | Model weights, not system | Population patch/rewrite + tournament | Population archive | Generative verifiers | Author benchmarks | Natural language; reward hacking | Diversity archive with pessimistic selection |
| LeanSearch v2 | Yes | Retrieve/rerank/reflect | Index | Downstream Lean | Public code/data and retrieval eval | Retrieval is evidence, not proof | Theorem-level retrieval packet |
| LeanDojo | Yes | Proof-state/tactic interface | Extracted dataset | Lean kernel | Mature public infrastructure | Historical benchmark/toolchain | Accessible-premise extraction |
| Pantograph | Yes | Explicit multi-goal/tree interface | Caller-managed | Lean kernel | Public tool | Not a persistent search system by itself | Goal-addressable interaction |
| TheoremGraph | Data/API | Graph retrieval | Large typed/probabilistic graph | Typed edges vs probabilistic links | Public paper/resource | Informal edges are not truth | Separate discovery graph from proof graph |
| AlphaGeometry2 | DDAR subset | Gemini construction + shared symbolic trees | Shared derived facts | Symbolic DDAR | JMLR paper | Full model/SKEST closed; narrow geometry DSL | Shared checked facts |
| FunSearch / AlphaEvolve | Partial | Islanded executable evolution | Program populations | Objective evaluator | Published mathematical results | Models/infrastructure closed; skeleton/evaluator needed | Multi-objective executable search |

## Decision summary

The project should preserve its fail-closed final gate and regulator, add QED-style source/original-step controls, Danus-style revocation with stronger admission, Goedel/LEAP/LeanMarathon blueprints, LeanSearch/LeanDojo/Pantograph retrieval and interaction, and AlphaEvolve-style diversity only where an executable evaluator exists. It should not imitate proprietary scale claims, count agents as progress, or replace expert novelty review with model consensus.
