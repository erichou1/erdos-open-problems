# Final Comparison Report

“Final” here means the conclusion of this audit/implementation increment, not the completion of the long-term architecture or the solution of an Erdős problem.

## Outcome

The repository moved from a fixed numeric batch over an inconsistent local corpus to an auditable, complete-corpus selection foundation. It also repaired deterministic operational defects that caused honest resource-exhausted outputs and valid review text to be misclassified, lost cache provenance on resume, and equated clean process exit with mathematical completion.

It did not produce a verified novel Erdős resolution. Problem 601 remains `no_progress_within_budget`, with substantial unverified partial analysis and unresolved interpretation/classification gaps.

## Baseline versus merged increment

| Dimension | `fd9c019` baseline | Merged increment | Evidence / limitation |
| --- | --- | --- | --- |
| Open corpus | 597 local vs 616 canonical; 25 missing, 6 extras | 616 canonical = catalog = local; all page/section records validate; catalog pinned to upstream commit `8b46f270…` | Set and theorem-section provenance restored; ambiguous intent still needs audit |
| Selection | Numeric/manual range | 616 cards, separate posteriors/rankings, diversity, protected exploration | Operational, explicitly uncalibrated |
| Pipeline identity | Git/process implicit | Content-derived pipeline fingerprint over behavior-defining files and runtime; schema-v2 reusable contract over statement/source/pipeline/research directive/exact model/full budget/tool/dependencies/runtime, plus execution-specific context | Stable across unrelated Git commits; allocation is withheld when model identity is unrecorded |
| Outcome semantics | Manifest/exit zero treated done | Exact-run verified-only completion; contextual dispositions; evidence-bound append-only revisions, including novelty-evidenced corrections from `verified_novel_resolution` to `independent_rediscovery` or `literature_identification` | Legacy candidates recovered read-only |
| 601 status | `candidate_unclassified` | `resource_exhausted` / `no_progress_within_budget` | Not solved; 27/27 enumerated claims are not verified facts |
| Reviewer schema | Exact role token contradicted prompt | Exact token or exact prompt wrapper only | Still fail closed on other role |
| Candidate schema | Line-anchored fields | One bounded block, layout-independent labels | Duplicate/multiple blocks fail closed |
| Resume | Raw response text only | Schema-v3 full-contract/stage/prompt/response identity, atomic files, compatible context restoration | Legacy/incompatible cache regenerates; full stage event log pending |
| Rate limit | Shared backoff, reset on URL; range started at 180s | Reset after complete response; 15s start; 120s hard cap | Real browser telemetry/canary pending |
| Workers | Numeric shards, no claims | Content-addressed allocation plan whose reusable context includes `allocation_top_k`, plus exact-run-contract atomic claims; actual queue enforces disjoint 4:1 lanes | Lease heartbeat/expiry stress evidence incomplete; flag remains off |
| Verification | Strong deterministic review gate + label-trusted evidence | Gate/intent/negative-disposition certificates replay privacy-scanned closed support for audit; schema/runtime force all events ranking-ineligible because local replay is not authenticated provenance | Production provenance/external/Lean/exact adapters not yet implemented |
| Formal proof | None | Detailed pinned integration specification, flag off | No Lean installed; no formal claims |
| Claim truth | Whole candidate and mutable state | Schemas/specs only | Fact Graph/revocation remains P1 |
| Literature/novelty | None | Research review and architecture/spec | Operational retrieval/novelty agent remains P0 |
| Evaluation | Self-reported completeness board | Explicit baselines/metrics/ablations plan | No performance superiority claim |

## Comparison with `AGENTS.md`

Implemented from the contract:

- searcher as the front door;
- immutable source snapshots and provenance hashes;
- exact first-party theorem-only/original/normalized/intended fields, separate remarks/references, and full raw-page/section provenance;
- status and ambiguity probes;
- deterministic multi-route cards and multipart cards that retain the complete parent source statement while separately hashing each focus question and subproblem contract;
- closed research directives containing all card routes/subproblem targets, bound by reusable run-contract schema v2 and injected into `ProofPipeline` without changing the exact parent statement lock;
- separate probability targets and uncertainty;
- diversified rankings and protected exploration;
- append-only attempt/outcome ledgers;
- exact pipeline/budget-bound audit records; outcome learning remains disabled pending authenticated provenance;
- fail-closed reporting of corpus degradation;
- clearer separation of execution status from truth status.

Still missing from the contract:

- independent interpretation approval for materially ambiguous source statements;
- theorem-level solver packet and novelty audit;
- Fact Graph, graph-wide evidence-tier propagation, dependency slices, and revocation;
- dynamic proof-leaf scheduling/proof-debt accounting;
- executable exact/CAS/SAT/Lean verification;
- formal statement-fidelity testing;
- model registry and capability router;
- calibrated selector and measured adaptive allocation;
- two-key correctness/contribution publication.

## Comparison with leading systems

The project should not imitate closed systems’ scale. Its implementable advantage can be auditability:

- from QED: preserve regulator logic, original-step expansion, structural-first verification, and exact resume;
- from Danus: adopt content-addressed claim dependencies and revocation, but replace LLM-only high-centrality admission;
- from Goedel-Architect/LEAP/LeanMarathon: use a formal blueprint, parallel leaves, successful-node retention, and CI merge gates;
- from AlphaProof Nexus: cache exact elaborated goals, proofs, disproofs, and value/cost, with clean replay;
- from LeanSearch/LeanDojo/Pantograph: theorem retrieval and proof-state interaction;
- from FirstProof: always measure against a raw-model baseline and include costs/failures;
- from Aletheia/Axiom history: never conflate correctness with intent, novelty, or significance;
- from FunSearch/AlphaEvolve: use diversity/evolution only behind hard executable evaluators.

## What is proven by this increment

- The unit/regression behaviors listed in the test suite pass in the configured environment.
- Current canonical/local open membership is equal at 616.
- The ingester fetched, structurally parsed, and revalidated all 616 first-party pages, source records, generated files, and section hashes; it also restored the 25 missing local records and removed six resolved extras.
- The current ranker generates 616 cards and the specified ranking families.
- Stored one-line resource-exhausted candidates are parsed correctly.

## What is not proven

- that any prior candidate proof is correct;
- that the searcher selects solvable problems better than a baseline;
- that its probabilities are calibrated;
- that five live workers are safe under crashes/rate limits;
- that every human/external certificate issuer is semantically trustworthy;
- that Lean integration works;
- that the merged architecture improves verified mathematical output or cost.

## Architectural decision

Preserve the current deterministic promotion gate and regulator. The schema-v2 routing and exact-parent-lock foundation is implemented; make the next engineering milestone telemetry/leases plus independent interpretation approval and theorem-level literature packets—not more proof-generating tabs. Then add claim-level truth and executable evidence behind flags. Only after comparable verified outcomes exist should the project fit a calibrated selector or claim performance gains.
