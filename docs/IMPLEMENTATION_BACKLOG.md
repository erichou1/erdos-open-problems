# Prioritized Implementation Backlog

Each item is independently testable. “Done” means code, regression test, documentation, and rollback evidence—not merely a design note.

## P0 — integrity and trustworthy execution

| ID | Deliverable | Status | Acceptance test |
| --- | --- | --- | --- |
| P0.1 | Canonical corpus ingestion/snapshot/set gate | Done in this audit | Canonical/catalog/local sets are all 616; raw page/section chains validate; catalog bytes are pinned to upstream commit `8b46f270…`. |
| P0.2 | Bounded single-line result parsing | Done | Real 601 candidate recovers `resource_exhausted`; duplicate/multiple result blocks fail closed. |
| P0.3 | Prompt-compatible reviewer role parsing | Done | Exact allowed wrapper passes; any different role fails. |
| P0.4 | Stage-cache metadata v3 / reusable run contract v2 | Done | Changed prompt or response hash invalidates; the embedded run contract binds statement/source/pipeline/model/tool/budget/dependency/runtime plus `research_directive_sha256`; cache restores only the matching original context. |
| P0.5 | Verified-only completion semantics | Done | Rejected/resource-exhausted manifest and stale marker do not skip; only a verified manifest with the exact current run contract does. |
| P0.6 | Adaptive limiter correctness | Done at unit level | 15s initial, exponential, hard 120s cap, reset only after complete response. |
| P0.7 | Durable run event log | Next | Every stage/provider/cache/retry/throttle/outcome event append-only, atomic, versioned, and replayable. |
| P0.8 | Worker leases/campaigns | Next | Five-worker crash test has zero duplicate active problems; stale leases recover; pipeline upgrades revisit eligible failures. |
| P0.9 | Model/tool/cost telemetry | Next | Every run records exact model disclosure, tool versions, calls/tokens/wall time/cost; missing identity blocks calibrated learning. |
| P0.10 | Structured output repair | Next | Malformed planner/regulator/reviewer gets bounded format-only repair without spending mathematical revision; failure remains typed. |
| P0.11 | Statement contract v2 | Next | Raw/theorem/normalized/intended layers and hashes; seeded quantifier/domain drift rejected. |
| P0.12 | Theorem-level retrieval/novelty packet | Next | Every imported theorem has exact statement/hypotheses/source/hash/applicability; solver cannot browse after packet freeze. |
| P0.13 | CI and dependency floor | In progress | Unit suite and corpus gate run on supported Python versions; browser/tool versions pinned. |
| P0.14 | Evidence-bound outcome revisions | Audit replay done; authenticated adapters pending | Gate/intent/negative-disposition evidence replays a closed privacy-scanned raw-input projection and exact required support; negative status is recomputed by the shared classifier. Local replay is not provenance, so schema/runtime force all events audit-only. The flock-serialized transaction spans all certificates through ledger fsync, failed workflows leave no newly created evidence files, and correction chains remain append-only. |
| P0.15 | Immutable allocation contract | Done at unit level, release flag off | Context—including `allocation_top_k`—ranking/allocation hashes, 4:1 lane cadence, exact run-contract claims, and reordered/tampered or top-k-mismatched artifacts fail closed. |
| P0.16 | Run-contract-v2 research routing | Done at unit level | The reusable contract binds `research_directive_sha256`; all supported verified-run entry points inject routes/subproblem targets into `ProofPipeline` while the exact parent statement remains locked; subproblem cards retain the full parent statement and separately hash the focus question and combined contract. |

## P1 — claim truth and executable evidence

| ID | Deliverable | Acceptance test |
| --- | --- | --- |
| P1.1 | Append-only Fact Graph events and derived view | Rebuild produces identical graph; content hashes/dependencies/evidence tiers stable. |
| P1.2 | Cascading revocation | Seeded false central fact revokes complete dependent closure and invalidates caches/publication. |
| P1.3 | Counterexample twins | Improves seeded false-claim detection/first-error localization under equal review budget. |
| P1.4 | Proof-debt scheduler | Reduces central unchecked debt/time to first verified progress versus centrality/FIFO baseline. |
| P1.5 | Exact-computation adapter | Clean replay validates program/domain/coverage/certificate; tampering fails. |
| P1.6 | Pinned Lean project + clean replay | Valid fixture passes, `sorry`/unsafe axiom/misaligned target fixtures fail in fresh CI. |
| P1.7 | Formalization mutation covariance | Seeded local semantic edits detected materially better than backtranslation-only baseline. |
| P1.8 | Independent novelty gate | Correctness cannot publish “novel solved” without separately signed literature/contribution decision. |
| P1.9 | Public evidence-tier board | Legacy candidate labels clearly archival; verified novel, partial, independent rediscovery, literature identification, blocked, and censored outcomes remain separate. |

## P2 — calibrated selection and scalable research

| ID | Deliverable | Acceptance test |
| --- | --- | --- |
| P2.1 | Contextual outcome dataset | ≥100 comparable expert/evidence-graded attempts with censorship/costs and temporal holdout. |
| P2.2 | Calibrated opportunity model v2 | Improves held-out Brier/log loss and Recall@K over static MVP without diversity loss. |
| P2.3 | Successive halving/contextual bandit | Higher verified yield per total compute+review cost than fixed allocation; exploration retained. |
| P2.4 | Cross-problem infrastructure graph | Predicted unlock correlates with actual imports/reuse; no credit without replayed reuse. |
| P2.5 | Capability-change revisit | Higher useful revisit yield than fixed retry intervals with lower wasted cost. |
| P2.6 | Verification-congestion pricing | Reduces unreviewed backlog/age without lowering verified high-value yield. |
| P2.7 | Executable population search | Equal-budget ablation shows gain; frozen target and evaluator-adversarial tests pass. |

## Release checklist

- Full test suite green on supported Python matrix.
- Corpus audit complete.
- No unreviewed secret/profile/context URL staged.
- Generated artifacts have source and pipeline hashes.
- Feature flags match actual runtime behavior.
- Rollback exercised for changed subsystem.
- No performance or mathematical correctness claim without evaluation/evidence.
