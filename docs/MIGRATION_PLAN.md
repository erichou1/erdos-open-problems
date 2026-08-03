# Migration Plan

The migration is incremental. Each phase leaves the prior entry points usable, introduces an explicit flag or separate executable, and has a rollback that preserves evidence.

## Release-state flags

Current flags are in [`config/pipeline_features.json`](../config/pipeline_features.json).

| Flag | Default | Meaning | Rollback |
| --- | --- | --- | --- |
| `validated_stage_cache_v3` | on | Reuse only cache-schema-v3 entries bound to stage/prompt/response hashes and the full schema-v2 reusable run contract, including `research_directive_sha256`; restore matching context provenance | Disable the flag to stop reuse. Legacy/incompatible metadata is rejected and the stage regenerates; delete only the affected stage pair if manual cleanup is needed. |
| `tolerant_bounded_result_parser` | on | Parse labeled fields independent of line layout inside one `<result>` block | Revert parser commit; existing raw responses remain intact. |
| `normalized_run_dispositions` | on | Separate verified, budget exhaustion, censorship, and operational failure | Read raw manifests only at the run-normalization boundary; the searcher consumes validated ledger records and evidence persistence receives only the closed projection. Never recreate legacy `ok` markers. |
| `erdos_searcher_mvp` | on | Produce cards/rankings/ledgers | Use manual/numeric assignment; retain snapshots/ledgers. |
| `source_ingestion_snapshots` | on | Fetch through provenance-preserving ingester | Stop ingestion; restore a prior hashed snapshot/generated file. |
| `continuous_scheduler` | off | Ranked multi-worker claims and periodic reranking | Stop workers; run single-problem/range commands. |
| `lean_execution` | off | Execute formal proof search/verification | Route to NL/exact/human review and mark formal evidence unavailable. |
| `fact_graph` | off | Claim-level admission/revocation | Derive read-only graph from existing artifacts; keep legacy state authoritative. |
| `automated_external_evidence` | off | Code-registered kind/issuer/adapter-version implementations may replay typed evidence | External judgment events remain audit-only and ranking-ineligible; no manual or issuer-string override enables learning. |

## Phase 0 — freeze and audit (completed)

- Preserve user runtime changes and inspect actual code/logs/artifacts.
- Record `fd9c019` baseline and run original tests.
- Establish no active workers and zero verified results.
- Identify corpus, parser, role, cache, terminal-state, and backoff root causes.

Rollback: documentation only; no baseline artifact was rewritten.

## Phase 1 — restore trustworthy inputs (completed)

- Add first-party YAML/page ingestion with TLS verification, raw snapshots, hashes, and parse validation.
- Restore the 25 incorrectly deleted source-open records.
- remove six source-resolved files from the open routing directories.
- Add corpus set audit and make degraded state visible.
- Regenerate 616 cards from a complete source set.

Rollback: restore the prior Git tree or reapply any immutable generated snapshot; raw ingestion evidence remains.

## Phase 2 — correct execution semantics (completed)

- Parse one-line bounded result contracts.
- Normalize only the exact reviewer-role wrapper induced by the prompt.
- Add schema-v3 cache metadata, schema-v2 reusable run contracts including `research_directive_sha256`, and atomic writes.
- Restore matching reviewer context on resume and invalidate changed statements, prompts, routing directives, or reusable-contract inputs.
- Reset rate-limit streak only after complete responses; cap adaptive cooldown at 120 seconds.
- Skip only gate-verified results, not any manifest/exit-zero run.
- Recover legacy unclassified resource-exhausted outcomes without mutating run artifacts.

Rollback: stage regeneration and raw-manifest reading remain possible; no candidate text is discarded.

## Phase 3 — searcher MVP (completed, calibration pending)

- Create normalized cards, deterministic routes, cheap probes, separate weak-prior outputs, intervals, diversified rankings, exploration reserve, and append-only ledgers.
- Use a content-derived pipeline fingerprint over behavior-defining files and runtime; keep it stable across unrelated Git commits.
- Generate closed directives from all card routes and subproblem targets, bind the directive hash in reusable run-contract schema v2, and inject it into `ProofPipeline` as search guidance while preserving the exact parent truth target.
- Retain the full parent source statement on multipart cards and separately hash each focus question and subproblem contract.
- Include `allocation_top_k` in reusable allocation context; add content-addressed plans and exact-run-contract atomic claims.
- Replay deterministic gate/intent/negative-disposition evidence against a privacy-scanned closed run projection and exact required content-addressed support for audit. Force every event to `learning_eligible=false` until a secret-backed signature, external verifier, or equivalent authenticated production adapter is registered and replayed.
- Add an opt-in continuous worker.

Exit criterion reached for operational MVP: complete corpus cards/rankings exist. Calibration criterion not reached: verified contextual outcome cohort is insufficient.

Rollback: disable ranked allocation and run manual/numeric assignments. Never delete ledger history.

## Phase 4 — telemetry and leases (next P0)

- Add append-only run/stage events with process/worker/campaign ID, prompt/model/tool versions, timings, token/call/cost counts, cache decisions, retry/throttle reasons, and outcome.
- Add lease expiry, heartbeat, safe takeover, and pipeline-upgrade revisit semantics.
- Stress-test five workers and simulated crashes.
- Import existing runs into ledgers with historical version/budget labels.

Gate to enable `continuous_scheduler`: zero duplicate claims in stress tests, bounded stale takeover, all cooldowns ≤120 seconds, and no loss of incomplete cache artifacts.

Rollback: stop workers and clear only expired claim files; retain events.

## Phase 5 — interpretation approval and literature packet (next P0; parent/focus routing foundation completed)

- Extend the existing raw/theorem-only/normalized/provenance fields and exact parent/focus locks with approved intended branches, definitions, and commentary boundaries.
- Add ambiguity branches and human/independent approval.
- Build theorem-level solver packets with exact statement/hypotheses, citations, source hashes, and applicability notes.
- Implement an independent novelty-audit workflow plus a code-registered replay adapter; the current artifact may retain schema-conforming review events for audit but deliberately excludes them from learning.
- Add stale-record routing.

Gate: seeded quantifier/domain/source-drift tests fail closed; solver packet replay is deterministic.

Rollback: retain old statement lock as one layer; block promotion if new fidelity gate unavailable.

## Phase 6 — Fact Graph (P1)

- Append claim events rather than overwrite one state file.
- Store content-addressed claims, dependencies, evidence tier, centrality, proof debt, provenance, and status.
- Add counterfactual twins and first-error localization.
- Implement cascading revocation and shadow-revocation tests.

Gate: seeded false central facts are rejected or revoke their complete dependent closure; no final gate reads a revoked fact.

Rollback: rebuild derived graph from append-only events; keep final legacy gate authoritative until ablation passes.

## Phase 7 — executable evidence and Lean (P1)

- Pin Lean/Mathlib and add clean replay CI.
- Implement statement-fidelity mutation tests.
- Add typed formal and exact-computation adapters.
- Connect only high-risk leaves first.
- Audit axioms, imports, `sorry`, metaprograms, target correspondence, and replay.

Gate: deliberately invalid/misaligned proofs are rejected; clean certificates reproduce from scratch.

Rollback: turn flags off, revoke facts whose only evidence is unavailable, retain artifacts as untrusted candidates.

## Phase 8 — calibrated allocation and experimental search (P2)

- Fit a versioned opportunity model after adequate verified outcomes.
- Evaluate contextual bandits/successive halving against deterministic MVP.
- Add population/evolution only for executable constructions/formal blueprints.
- Add verification-congestion pricing and capability-change revisit.

Gate: pre-registered held-out improvement in selection and cost without worse false-positive, intent-drift, or domain-diversity metrics.

Rollback: restore deterministic ranker and protected exploration.

## Phase 9 — communication migration (P1/P2)

- Replace “candidate-proved” public language with evidence-tiered dispositions.
- Publish correctness, intent, novelty, significance, costs, versions, and failed attempts separately.
- Require two-key publication for solved/novel claims.

Rollback: publish nothing rather than downgrade a verified label; legacy board remains clearly labeled archival.
