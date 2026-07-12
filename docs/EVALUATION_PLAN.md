# Evaluation Plan

## Rule

No architecture is called better until it beats specified baselines on held-out, evidence-graded outcomes under comparable budgets. Zero verified results means the current work can claim correctness of infrastructure tests, not improved mathematical performance.

## Evaluation units

The atomic unit is:

```text
(problem snapshot, intended-statement hash, pipeline fingerprint,
 model portfolio, toolset versions, compute/review budget, execution ID)
```

Changing any component creates a new unit. Repeated executions are clustered by problem for uncertainty estimates; they are not treated as independent problems.

## Outcome labels

Primary mutually exclusive terminal labels:

- verified intended novel resolution;
- verified intended partial progress;
- independent rediscovery;
- literature identification;
- wrong interpretation;
- statement defect;
- formalization mismatch;
- fundamentally flawed candidate;
- no progress within specified budget;
- censored attempt;
- operational failure;
- awaiting external evidence.

Correctness, intent fidelity, novelty, and significance also receive separate ordinal/binary judgments.

## Required selection baselines

1. Uniform random among eligible problems.
2. Prize-first.
3. Formalized-first.
4. Problem-age/popularity heuristic (diagnostic, not endorsed).
5. One model self-rated difficulty/solve chance.
6. Static statement/catalog features only.
7. Current deterministic cheap-probe weak-prior ranker.
8. Full adaptive/contextual ranker when available.

Every selector receives the same total research and review budget. Protected exploration is reported separately.

## Required research-harness baselines

1. Legacy direct single-model prompt at a fixed budget.
2. Original four-scout/review pipeline at `fd9c019` behavior.
3. Merged pipeline without Lean.
4. Merged pipeline without literature retrieval.
5. Merged pipeline without counterexample twin.
6. Merged pipeline without shared claim memory.
7. Merged pipeline without regulator/local replanning.
8. Merged pipeline without opportunity selection (random assignment).
9. Merged full configuration.

Where feasible, include an open formal baseline (for example OProver/DeepSeek/Goedel with a pinned local Lean stack) on formally stated leaves, not as a direct substitute for informal research.

## Metrics

### Mathematical outcome

- verified novel resolution rate;
- verified partial-progress rate;
- correctness false-positive rate after expert audit;
- wrong-interpretation rate;
- formalization-mismatch rate;
- false-novelty rate;
- first material error position/localization accuracy;
- revoked-fact and downstream-revocation counts.

### Selection

- Recall@K of problems yielding verified progress;
- precision/yield@K;
- selection loss versus oracle hindsight;
- domain coverage and entropy;
- protected-exploration yield;
- revisit yield after capability changes.

### Probability quality

- Brier score and log loss for each separate target;
- calibration slope/intercept;
- expected calibration error with uncertainty intervals;
- reliability plots;
- interval coverage;
- performance on new pipeline versions and temporal source snapshots.

Censored/unattempted units are excluded from naive binary loss. Use survival/censoring-aware analyses or report bounds.

### Efficiency

- wall time, model calls, tokens, dollars, and tool calls;
- cost and time to first verified central lemma;
- cost per verified partial/full result;
- expert-review minutes per accepted/rejected candidate;
- verifier queue age/congestion;
- cache hit, invalidation, and replay rates;
- duplicate worker effort;
- rate-limit events and cooldown distribution;
- formal import/build/replay time.

### Reuse

- cross-problem imports of formal definitions/lemmas/checkers;
- realized versus predicted corpus unlock;
- proof-debt reduction per unit cost;
- successful cache replays across compatible problems/toolchains.

## Dataset construction

- Freeze source and forum/literature snapshots before selection.
- Stratify by domain, problem type, ambiguity, source formalization, age, and prior attempts.
- Maintain a temporal holdout of future runs and a problem-level holdout to prevent leakage.
- Keep all source-open problems eligible; do not discard hard domains based on early failure.
- Build a native failure benchmark from old runs with expert first-error and repair-class labels.
- Seed known statement mutations, false lemmas, malformed schemas, cache mismatches, and malicious/unsafe formal artifacts.

## Budget tiers

Use fixed published tiers, for example:

| Tier | Purpose | Bound |
| --- | --- | --- |
| P0 | Deterministic/source probe | No frontier-model call or one bounded diagnostic call |
| P1 | Cheap research | Fixed calls/tokens/wall time; no heavy formal search |
| P2 | Standard full run | Current four-scout + revisions + reviews budget |
| P3 | Heavy selected run | Pre-approved formal/evolutionary compute and expert review |

Exact numeric limits must be filled from measured telemetry before experiments. “Until solved” is not a budget.

## Statistical policy

- Pre-register selection cohort, metrics, budget, exclusion/censoring rules, and stopping rule.
- Report problem-clustered bootstrap confidence intervals.
- For paired harness comparisons, use identical problem snapshots and matched budgets; report paired outcome differences and cost ratios.
- Correct for repeated ablation comparisons or label them exploratory.
- Publish all runs, including operational failures and rejected outputs.
- Do not tune on the final temporal holdout.

## Ablation sequence

1. Parser/cache/run-semantics reliability only: operational failure rate.
2. Searcher versus selection baselines: Recall@K/yield/cost.
3. Statement contract: wrong-interpretation and false-promotion rate.
4. Retrieval packet: citation/hypothesis errors and verified yield.
5. Fact Graph/revocation: false-fact containment and proof debt.
6. Counterexample twin: seeded false-claim detection.
7. Lean/exact adapters: false-positive reduction versus cost.
8. Adaptive scheduler: verified yield, diversity, and selection regret.
9. Population/evolution: incremental gain under equal evaluator/cost budget.

## Stop conditions

Pause or roll back a component if it:

- increases false solved/novel claims;
- increases wrong interpretations or formalization mismatch;
- loses artifacts or provenance;
- creates duplicate worker execution above 1%;
- violates the 120-second configured cooldown cap;
- worsens verified yield per total review cost without a predeclared benefit;
- cannot reproduce certificates from a clean environment.

## Reporting template

Every evaluation release includes source snapshot IDs, Git commit and local pipeline fingerprint, model/tool versions, prompts/config, budgets, normalized dispositions, evidence certificates, expert forms, costs, exclusions, analysis code, and negative/operational results. Private raw outputs remain in a controlled runtime store; only privacy-scanned/redacted release-safe projections or explicitly approved public artifacts are published.
