# Baseline Report

Measurement date: 2026-07-12. Baseline code: `fd9c019`. All mathematical outcome counts below are evidence-tiered; candidate filenames are not counted as solutions.

## Repository baseline

| Measure | Baseline | Interpretation |
| --- | ---: | --- |
| Catalog records | 1,217 | All source states. |
| Catalog state `open` | 616 | Canonical selection target. |
| Local open files | 597 | Corrupt membership: 25 missing and 6 resolved extras. |
| Legacy ChatGPT outputs | 384 | Unverified transcripts. |
| Legacy `candidate-proved` labels | 43 | Model claims only. |
| Gate-verified results | 0 | No final theorem passed the complete gate. |
| Tracked baseline tests | 23 passing | Python 3.14 virtual environment. |
| Test CI jobs | 0 | Only site-data build existed. |

## Verified-pipeline run baseline

| Measure | Value |
| --- | ---: |
| Problem run directories | 13 |
| Manifests | 5 |
| Incomplete/censored runs | 8 |
| Legacy done markers | 5 |
| Stored `candidate_unclassified` | 5 |
| Recovered `resource_exhausted` | 5 |
| Verified proof/disproof | 0 |
| Formal/exact/expert evidence attached | 0 |

The five completed problems were 601, 661, 724, 782, and 849. Each exhausted its configured proof/revision budget. A process completed; the mathematical problem did not.

## Legacy board baseline

| Measure | Value | Caveat |
| --- | ---: | --- |
| Rows | 597 | Derived from corrupt local corpus membership. |
| Outputs | 384 | Not necessarily complete or valid. |
| `unsolved` | 341 | Filename parser category. |
| `candidate-proved` | 43 | Not peer review or gate verification. |
| Completeness ≥60% | 56 | Self-reported by model. |
| Mean completeness | 39.6% | Self-reported; not calibrated. |

These metrics remain useful only as the “legacy direct-attempt” comparator. They must not be combined with verified outcomes.

## Baseline operational behavior

- A manifest caused range workers to skip a problem regardless of gate status.
- A zero child exit caused a `.done` marker regardless of candidate/gate status.
- Rate limits did not consume proof retries, which is correct, but penalties reset too early and one range path effectively started at 180 seconds.
- Cache hits could save substantial model work, but lacked input and context provenance.
- No durable provider-call count, token count, dollar cost, wall-clock stage duration, cache hit, retry reason, or throttling event was recorded.

## Searcher baseline

There was no committed searcher at `fd9c019`. Therefore the required selection baselines have not yet been measured:

- random selection;
- prize-first;
- formalized-first;
- self-rated difficulty;
- static feature ranking;
- cheap-probe ranking;
- adaptive ranking.

The new MVP emits predictions but labels them `uncalibrated_weak_prior_mvp`. It is not legitimate to report Recall@K, Brier score, or calibration error until comparable, verified, context-bound outcomes exist.

## Post-change reproducibility checkpoint

The following are implementation checkpoints, not performance improvements:

| Checkpoint | Current value |
| --- | ---: |
| Canonical/local open set equality | 616 / 616 |
| Missing or unexpected open files | 0 / 0 |
| Normalized problem cards | 616 |
| Ranking families emitted | 10 plus diversified queue |
| Focused/full unit tests after implementation | See current test run; all passing before handoff |
| Verified mathematical results | 0 |

## Metrics required for the next real baseline

Every future run must record:

- problem/source/statement/pipeline/model/toolset/budget hashes;
- wall time and provider/tool call counts per stage;
- cache hits and invalidations;
- rate-limit events and actual cooldown duration;
- claims proposed, admitted, rejected, and revoked;
- time/cost to first verified partial progress;
- final normalized disposition;
- correctness, intended-statement fidelity, novelty, and significance as separate labels;
- expert review time and disagreement;
- Lean build, axiom audit, and replay results where applicable.

Only then can the project compare solve rate, verified-progress rate, false-positive rate, statement drift, cost per verified result, and selection quality.
