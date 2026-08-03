# Pipeline Integration Matrix

Legend: **present** = implemented before this audit; **added** = implemented in this audit; **planned** = specified but not implemented; **reject** = intentionally not adopted.

| Capability | Baseline project | `AGENTS.md` contract | External evidence | Merged decision | Status / owner |
| --- | --- | --- | --- | --- | --- |
| Immutable raw corpus snapshots | No | Required | Reproducible evaluations preserve inputs | First-party YAML/HTML bytes, hashes, append-only ingestion snapshots | **Added**: `erdos_ingest.py` |
| Corpus membership gate | No; set corrupt | Required provenance | Benchmark validity requires frozen sets | Exact catalog-`open`/local equality | **Added**: 616/616 |
| Opportunity ranking | No | Non-negotiable | No reviewed system solves selection completely | Transparent weak priors, separate targets, uncertainty, diverse/exploration lists | **Added**, uncalibrated |
| Exact pipeline/budget conditioning | No | Required | Evaluation comparability requires equal contexts | Local source fingerprint + budget-bound ledger updates | **Added** |
| Protected exploration | No | Required | Bandit/diversity literature; population systems | Reserve low-attempt/high-uncertainty slice | **Added**, simple deterministic policy |
| Statement hash | Trimmed text | Multi-layer contract | QED, LeanMarathon, formal fidelity audits | Keep hash; add raw/theorem/normalized/intended layers and mutation audit | Hash **present**; full contract **planned** |
| Fresh search contexts | Four scouts | Diverse search programs | QED, Aletheia | Preserve; record exact model and cost | **Present**, telemetry planned |
| Subgoal DAG | Basic dependency validation | Truth/search graph separation | Goedel-Architect, LEAP, LeanMarathon | Extend to AND/OR formal blueprint with claim evidence and revocation | Basic **present**; extension **planned** |
| Regulator | Proof/plan/rewrite | Adaptive control | QED | Preserve; localize to failed dependency cone | **Present**, localization planned |
| Candidate schema | Strict line-based block | Structured evidence | QED output controls | Bounded tolerant field parser, duplicate fields fail closed | **Added** |
| Reviewer roles | Exact token | Independent adversaries | QED, Aletheia | Preserve strict semantic role while accepting prompt-generated wrapper | **Added** |
| Stage resume | Raw text cache | Auditable durable state | QED resume, live Lean caching | Schema-v3 full run-contract key, prompt/response hashes, atomic write, context restoration | **Added** cache v3 |
| Batch terminal state | Exit zero / manifest | Contextual outcome taxonomy | FirstProof operational failures | Verified-only completion; normalized dispositions | **Added** |
| Adaptive throttling | Shared exponential backoff | Persistent execution | Browser/provider reality | No proof retry consumed; 15s start, 120s cap, reset after full response | **Added** |
| Atomic worker claims | No | Control plane | Distributed harness failures | Shared claims and ranked queue | **Added**, lease/campaign semantics planned |
| Claim-level Fact Graph | No | Required | Danus | Content-addressed claims, typed evidence, dependency slices, cascade revocation | **Planned**; Danus admission weakness rejected |
| Theorem-level retrieval | No | Required | LeanSearch v2, TheoremGraph | Frozen solver packets with exact declarations/hypotheses/provenance | **Planned** |
| Novelty audit | No | Required | Aletheia/Axiom novelty corrections | Independent literature plane; correctness and novelty separate | **Planned** |
| Lean execution | None | Active evidence fabric | Axiom, AlphaProof, DeepSeek, Goedel, LeanMarathon | Start with high-risk central leaves and exact certificates | **Planned**, flag off; no Lean installed |
| Formal statement fidelity | None | Required | Compile/faithfulness gap studies | Multi-candidate formalization, equivalence, paraphrase/local-mutation tests, frozen target | **Planned** |
| Exact computation | Label-trusted evidence | Executable discovery | FunSearch/AlphaEvolve | Sandboxed generator + independent replay/certificate | **Planned** |
| Evidence semantics | Hash + declared `passed` | Typed replayable evidence | AXLE trust caveat | Privacy-scanned closed support plus deterministic gate/intent/negative-disposition audit replay now; authenticated adapter contract next | **Partial**; every event is ranking-ineligible until provenance is authenticated |
| Population search | Four fixed scouts | Program populations | MaxProof, FunSearch, AlphaEvolve | Use only behind hard evaluators; maintain diversity archive | **Planned experimental** |
| Human intent approval | None | Ambiguity disposition | AI Co-Mathematician | Require approval for material branches before “intended” claim | **Planned** |
| Raw-model baseline | Legacy output exists | Required evaluation | FirstProof batch 2 | Pin direct model budget and compare orchestration gain/cost | **Planned evaluation** |
| Public reporting | Legacy candidate board | Separate communication plane | FirstProof transparency | Publish outcome/evidence tiers, not “candidate-proved” as solved | **Planned migration** |

## Preserve, modify, reject

### Preserve

- deterministic fail-closed promotion;
- immutable statement hash as one layer;
- role-separated fresh conversations;
- four diverse search perspectives;
- dependency-cycle validation;
- regulator distinction between proof and plan failure;
- raw artifacts and explicit gate reasons.

### Modify

- move from whole-proof-only truth to claim-level evidence;
- convert mutable state into append-only events plus derived views;
- bind all caches/outcomes to exact local implementation and budgets;
- execute evidence instead of trusting labels;
- let selection consume only verified contextual outcomes;
- add statement-fidelity and novelty gates outside the proof generator.

### Reject

- “more agents” as an objective;
- self-confidence/completeness as correctness evidence;
- same-family consensus as a formal verifier;
- source popularity/prize/formalization alone as ranking;
- Lean compilation as intent/novelty/significance;
- proprietary architecture guesses;
- one failed or censored run as permanent problem difficulty.
