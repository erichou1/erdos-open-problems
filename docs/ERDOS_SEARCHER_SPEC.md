# Erdős Searcher and Opportunity Ranking Specification

Implementation: [`erdos_searcher.py`](../erdos_searcher.py), [`erdos_ingest.py`](../erdos_ingest.py), [`problem_queue.py`](../problem_queue.py), and generated [`triage/rankings/current.json`](../triage/rankings/current.json).

## Objective

For an exact pipeline implementation, model portfolio, toolset, and budget, estimate separately the chance of producing:

- a verified intended novel resolution;
- verified partial progress;
- a correct but already known result;
- a statement/interpretation failure;
- a Lean-verified exact target;
- a finite computational resolution;
- reusable formal infrastructure.

The current MVP is a transparent weak-prior system, not a calibrated predictor. Its purpose is to make selection operational now and collect the outcomes needed for later calibration.

## Source ingestion

`erdos_ingest.py` retrieves the first-party metadata YAML over normal TLS and selected `/latex/N` source pages. Each run creates a new immutable directory:

```text
triage/ingestion/<timestamp>-<catalog-hash>/
  raw/problems.yaml
  raw/pages/problem_N.html
  source_records/problem_N.json
  generated/problem_N.tex
  manifest.json
```

The manifest binds URLs, source states, catalog/page/statement/generated hashes, explicit statement/remarks/reference sections, selection policy, errors, and per-destination before/after hashes. Canonical mode resolves the upstream branch to a 40-hex Git commit, fetches the commit-pinned catalog, requires it to be byte-identical to the branch retrieval, and validates the complete open inventory plus every raw page/source record/generated file before selection. Application preflights both mirrored paths with `lstat`, rejects conflicts/symlinks, stages the whole batch, and rolls back a failed replace.

Commands:

```bash
# Snapshot and apply only catalog-open records missing locally
.venv/bin/python erdos_ingest.py --apply

# Snapshot selected source-open records without applying them
.venv/bin/python erdos_ingest.py --numbers 601 724

# Complete solver-grade source snapshot (required by ranking/runs)
.venv/bin/python erdos_ingest.py --canonical
```

## Build flow

```text
complete canonical page/section snapshot + catalog + local inventory + forum snapshots + prior ledgers
→ immutable source inventory snapshot
→ corpus set audit
→ normalized card
→ statement/structure/literature/formal/run probes
→ deterministic route set
→ weak-prior posterior vector
→ cost placeholders
→ separate ranking families + diversified queue + exploration reserve
```

Build command:

```bash
.venv/bin/python erdos_searcher.py build --snapshot-date 2026-07-12 --top-k 25
```

The current canonical snapshot contains all 616 source-open pages and validates all 616 provenance chains. Its catalog is pinned to upstream commit `8b46f270eeef01ac6904f2d8053a4ea1df2c7c0c`; the mutable and commit-pinned catalog bytes share SHA-256 `7108dc960b65c891afd4c9555ef76d6607418b321a786a0457f863d75a7a2605`. A build refuses to rank without this provenance. Local membership also reports complete equality among the canonical, catalog-open, and local-open sets; any mismatch withholds autonomous allocation.

## Card contract

The canonical schema is [`schemas/problem-card.schema.json`](../schemas/problem-card.schema.json). Each card contains:

- problem/snapshot identifiers;
- a content-based fingerprint of behavior-defining local pipeline files plus runtime,
  including uncommitted bytes and stable across unrelated Git commits, together with
  exact model/tool/dependency identities and the complete normalized budget;
- original, whitespace-normalized, and currently intended source statement;
- statement hash and ambiguity markers;
- source state, update, URL, tags, references, formalization metadata;
- structural goal/domain/finite/asymptotic/multipart signals;
- source-forum and early-run probes;
- routes;
- separate posterior objects with approximate intervals;
- relative cost and unknown-cost disclosures;
- canonical snapshot, raw-page, source-record, statement/remarks/reference, local-file, and commit provenance.

“Intended” currently copies the source theorem and is labeled pending theorem-level audit. It must not be reported as human/auditor-approved.

## Routing

Deterministic routes are additive:

| Evidence | Route |
| --- | --- |
| Material ambiguity | `statement_audit`, `human_clarification` |
| Source formalization state exactly yes | `formal_search` |
| Explicit construction goal | `exact_construction_search`, `construction_verification` |
| Explicit multiple questions | subproblem cards that retain the complete exact parent source statement and parent statement hash, plus a separately hashed focus question and combined subproblem contract; `subproblem_decomposition`, `shared_infrastructure_search` |
| Finite exact-search affordance | `exact_computation`, `counterexample_search` |
| Forum solution/counterexample signal | `literature_search` |
| No material ambiguity | `natural_language_research` |

The current formal probe correctly distinguishes `{state: "no"}` from `{state: "yes"}`; dictionary truthiness is not used.

Every card route and every subproblem target is serialized into a closed research
directive. Reusable run-contract schema v2 binds the directive's SHA-256. The
supported verified-run entry points pass the directive to `ProofPipeline`, which
injects it into the research stages as search guidance only; the complete exact
parent statement remains the locked proof target.

## Probability model

The model version is `heuristic-competing-risks-v2`. It begins from deliberately weak Beta priors and applies small, inspectable multi-signal changes for formal/exact affordance, multipart burden, ambiguity, literature evidence, construction, mathematical value, and reuse. Bare/private attempt directories never enter cards, cost, uncertainty, or posterior calculations. The aggregation path can consume only schema-valid, exact-context, learning-eligible records, and this release deliberately permits none until provenance is authenticated.

Approximate 95% intervals use a normal approximation to the Beta mean. They are uncertainty indicators, not validated Bayesian credible intervals. The output label `uncalibrated_weak_prior_mvp` is mandatory until a sufficient contextual outcome cohort exists.

Censored, operational, awaiting-evidence, and negative runs do not alter mathematical success/failure pseudo-counts in this release. Closed raw-input projections can replay budget-exhausted, fundamentally flawed, or wrong-interpretation classifications for audit, but local hashes and caller-controlled files are not authenticated production provenance. Consequently every ledger record is forced to `learning_eligible=false`, including deterministic and manually appended negatives. Positive external judgments are also audit-only because this release registers no feature-flagged production adapter. Records may still form allowed append-only correction transitions without changing the ranking model.

## Ranking families

The build publishes:

1. highest probability of verified novel solution;
2. highest probability of verified partial progress;
3. highest probability of Lean verification;
4. best finite-computation targets;
5. most likely stale literature records;
6. highest-value uncertain problems;
7. highest mathematical-value targets;
8. highest reusable formal-infrastructure value;
9. highest expected corpus-wide unlock;
10. protected exploration;
11. a diversified attack queue.

Mathematical value, formal reuse, and corpus-wide unlock use distinct multi-signal weak priors; they remain uncalibrated proxies and must not be presented as measured value models. Their ranking sequences are regression-tested against accidental aliases.

Ranking-card schema: [`schemas/ranking-card.schema.json`](../schemas/ranking-card.schema.json).

## Protected exploration

At least one-fifth of `top_k` (minimum one) is reserved outside the exploitation set for low-attempt, high-uncertainty problems. The diversified exploitation lane gives a decreasing bonus to underrepresented domains. The actual `allocation_queue` deterministically interleaves four exploitation records then one protected record; the worker consumes this artifact rather than rebuilding a posterior sort.

## Attempt and outcome ledgers

Append commands:

```bash
.venv/bin/python erdos_searcher.py record-attempt --record attempt.json
.venv/bin/python erdos_searcher.py record-outcome --record outcome.json
```

Records are append-only JSONL under closed ledger schema v3 and require matching problem ID/number, canonical snapshot/statement hashes, reusable contract ID, unique execution-specific context ID, exact bounded model/pipeline/toolset/full-budget identities, bounded gate/candidate dispositions, status, and `learning_eligible=false`. Both schema and runtime reject `true` until an authenticated provenance adapter is implemented. Reusable run-contract schema v2 also binds `research_directive_sha256`, so different route/subproblem packets are not interchangeable reuse contexts. Each stored event has a content hash, monotone sequence, and explicit superseded-event link, so external promotion and novelty reclassification retain their history. The loader uses only the latest valid event in each continuous chain.

Deterministic gate, intent, and negative-disposition certificates are replayed on every read against a content-addressed closed projection of raw classifier/run-identity inputs and the exact support required for that evidence kind: candidate bytes, schema-v2 run contract, canonical snapshot manifest, source record, and statement. The projection excludes the derived ledger status, full gate object, reviews, paths, and context URLs. Negative replay invokes the same classifier used at the raw-manifest boundary and requires its recomputed status, gate status, and candidate outcome to equal the certificate and ledger. This establishes consistency, not provenance: a self-issued, classifier-consistent disposition certificate may be retained for audit but cannot authorize learning. Support is privacy-scanned before persistence and again on read; one flock-serialized evidence transaction covers all certificate registrations and the ledger fsync, rolling back only files created by a failed workflow. Missing, deleted, tampered, private, secret-bearing, or mismatched support withholds the event rather than turning it into a negative. All outcome learning remains disabled until a secret-backed signature, external verifier, or equivalent authenticated production capability is implemented and replayed.

External human novelty/partial-review labels are different: this release has no production-registered replay adapter, and `automated_external_evidence` is off. Such status events may be retained for audit with `learning_eligible=false`, but they cannot change any pseudo-count, posterior, cost estimate, or ranking. The code registry is keyed by evidence kind, issuer, and adapter version and is empty; an issuer string or manual override cannot enable learning. `verified_novel_resolution`, `independent_rediscovery`, `literature_identification`, and qualified-human partial progress therefore remain audit-only until a feature-flagged deterministic adapter is implemented and replayed. Exact duplicate events are idempotent; only allowlisted superseding transitions are accepted, and secret/conversation URL content is rejected. Schema: [`schemas/ledger-record.schema.json`](../schemas/ledger-record.schema.json).

## Scheduler

`problem_queue.py` validates and consumes the immutable content-addressed artifact `rankings/contexts/<allocation-context>/<ranking-content-sha256>.json`. The reusable allocation context includes `allocation_top_k`, so a cached allocation built for a different requested top-k is not reused. The queue recomputes the context and ranking-content hashes and the combined allocation ID, checks disjoint lanes, exact per-problem run contracts, ranks, and the four-to-one cadence, then retains the validated plan in memory to remove a read/claim time-of-check race. Claims live under `.claims/<allocation-id>/` and bind the exact problem run contract. `run_continuous.py` rejects a changed statement/run contract before execution and records only the disposition of that exact manifest.

It is disabled in [`config/pipeline_features.json`](../config/pipeline_features.json) pending:

- lease expiry and process-owner heartbeat;
- campaign IDs so an upgraded pipeline can revisit prior failures;
- crash-safe claim takeover tests;
- model identity and cost telemetry;
- a five-worker duplicate-work stress test.

An operator may run a bounded experiment only with the explicit
`run_continuous.py --enable-experimental` override. `--new-campaign` additionally
releases prior unverified claims and is safe only before any workers start.

## Rollback

The searcher does not replace bounded manual assignment. To roll back allocation, stop `run_continuous.py` and run `run_verified_pipeline.py --problem N --model-id <exact-id>` or `run_sol2_batch.py --problems ... --model-id <exact-id>`. All verified-pipeline entry points still require the complete canonical source snapshot and exact run contract. Raw snapshots and ledgers remain read-only evidence. Disabling the selector must never delete cards, outcomes, or source snapshots.

## Acceptance criteria for calibrated v2

- at least 100 comparable completed attempts spanning multiple domains, with censorship explicit;
- independently verified outcome labels;
- Brier score, log loss, calibration slope/intercept, expected calibration error, and interval coverage;
- Recall@K and selection loss against random, prize-first, formalized-first, self-rating, and static-feature baselines;
- no hidden use of future source status or literature labels;
- versioned model artifact and reproducible feature extraction;
- protected exploration retained unless an ablation justifies change.
