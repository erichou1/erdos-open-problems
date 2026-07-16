# Literature-Informed Erdős Problem Ranking Design

**Date:** 2026-07-16

**Status:** Approved for implementation planning

## Goal

Build one auditable ranking pipeline that uses the first-party Erdős corpus,
surrounding problems, forum discussion, and a bounded live scholarly search to
prefer problems where the production solver has a credible path to verified
progress. Every problem carrying a monetary prize must rank below every
eligible problem explicitly recorded as having no prize in solve-oriented
queues.

The pipeline continues to treat ranking as a search preference. It never
converts prize metadata, popularity, a retrieved abstract, or a forum claim into
proof, novelty, or a calibrated solve probability.

## Current Gap

The repository contains most of the necessary pieces, but they are not joined:

- `sync_problem_catalog.py` currently drops the upstream `prize` field.
- `erdos_searcher.py` therefore cannot distinguish paid and unpaid problems.
- `literature_research.py` finds related local problems only after a target has
  already been selected, and it rebuilds its corpus statistics for each query.
- `egmra/retrieval/scholarly.py` can search arXiv, Crossref, Semantic Scholar,
  and MathOverflow, but the corpus-wide selector does not consume its results.
- `egmra/selection/features.py` defines literature features, while the current
  production queue is still built from `erdos_searcher.py`'s shallow probes.

The result is a queue driven mostly by tied weak priors, statement shape,
formalization availability, reference counts, forum comment counts, and rough
compute cost. It does not yet ask whether the nearby literature supplies a
usable partial-result ladder, indicates dependence on deep unresolved
machinery, or conflicts with the recorded open status.

## Chosen Approach

Use a two-stage, local-all/live-shortlist cascade.

1. Run one deterministic local literature index over every rankable problem.
2. Build a preliminary solve-oriented ranking with the existing posterior,
   cost, uncertainty, and diversity signals.
3. Select the top 50 unpaid candidates for live scholarly enrichment.
4. Search four allowlisted sources, freeze the results into immutable cached
   artifacts, and extract bounded ranking features.
5. Rerank within the unpaid tier using the literature features.
6. Rank paid problems only after the complete unpaid tier, using local
   literature features and any compatible cached live evidence.

This avoids hundreds of live searches for low-priority or paid targets on every
refresh. It also avoids the weaker alternatives:

- A local-only pipeline cannot see recent papers or MathOverflow discussion.
- A live search for every problem is slow, rate-limit prone, and mostly spends
  requests on candidates that cannot reach the active queue.
- A soft prize penalty does not satisfy the required unpaid-first invariant.
- Excluding paid problems entirely loses them as eventual targets and as useful
  sources of reusable infrastructure.

## Ranking Invariants

### Prize policy

The catalog must preserve the raw upstream prize value. Each problem receives
one of three metadata states:

- `unpaid`: the source explicitly records `no`;
- `paid`: the source records any monetary value, in any currency;
- `unknown`: the field is missing or malformed.

No currency conversion or prize-size comparison is performed. Prize values are
historical and sometimes apply only to one direction or version of a problem.

Allocation is withheld if any otherwise eligible problem has `unknown` prize
metadata. This prevents an old catalog that silently omitted prizes from being
treated as unpaid. After complete catalog ingestion, the solve-oriented sort
key begins with `0` for unpaid and `1` for paid. Therefore, no posterior,
literature bonus, uncertainty bonus, or diversity bonus can place a paid target
ahead of an unpaid target.

Prize metadata does not modify any Bayesian posterior. It is a user-selected
allocation policy layered over the weak-prior probabilities.

### Literature trust boundary

Retrieved material is ranking evidence only. It may:

- suggest a nearby theorem, method, reduction, obstruction, or solved case;
- raise rediscovery or status-conflict risk;
- indicate that partial progress may be more accessible than a full solution;
- indicate likely dependence on major unresolved machinery;
- increase the estimated reuse value of a route.

It may not:

- mark a problem solved or disproved;
- establish that a theorem applies;
- establish novelty from a negative search;
- become a premise without the existing import-audit path;
- change a correctness or promotion gate.

Source failure and rate limiting are coverage gaps, not negative literature
results. Missing literature widens uncertainty and is shown in the ranking
record; it does not create a tractability bonus.

## Pipeline Architecture

### 1. Catalog and problem-card metadata

`sync_problem_catalog.build_catalog()` copies an explicit upstream `prize`
value into every record without changing it. An absent field is recorded as
`null` with `prize_status: unknown`; only an explicit source value of `no`
becomes `prize_status: unpaid`. Generated catalog counts include
`monetary_prize`, `open_monetary_prize`, and `unknown_prize` totals.

`erdos_searcher.build_card()` copies the raw value into `metadata.prize` and
adds `metadata.prize_status`. Ranking rows expose both fields and include the
paid policy in `largest_risks` when applicable.

The source snapshot, problem card, ranking content hash, and allocation context
therefore bind the exact prize bytes used for ordering.

### 2. Corpus-wide local literature index

Refactor `literature_research.py` around a reusable `LiteratureIndex`. The index
loads and tokenizes the corpus once, then answers every per-problem query using
the existing tag Jaccard, shared-citation, and TF-IDF relevance signals.
`research_literature()` remains as a compatibility wrapper.

For each problem, the index emits a closed `LocalLiteratureFeatures` record:

- related problem IDs and relevance scores;
- shared tags and citation keys;
- extracted result-bearing sentences from canonical remarks;
- count of related results and distinct citations;
- partial-result ladder signals such as explicit weaker cases, bounds, or
  conditional results;
- deep-machinery signals such as explicit equivalence to, implication from, or
  conditional dependence on a named major conjecture;
- forum comment count and exact matched claim/partial-progress snippets;
- AI-wiki full/partial rediscovery-risk metadata already in the catalog;
- hashes of every local source used.

Keyword-derived features are capped weak signals. Their matched sentences are
stored so a reviewer can see why they fired. A negated or ambiguous sentence
cannot silently become a high-confidence classification.

### 3. Preliminary ranking and live shortlist

The preliminary ranking uses the current posterior, compute cost, protected
exploration, and domain diversity. Local literature features contribute only
bounded acquisition adjustments and status-risk tiers.

The live shortlist contains the first 50 unpaid candidates from that
preliminary allocation order. The limit is a versioned policy constant and is
recorded in the allocation context. Paid problems never consume live shortlist
slots. A paid problem may reuse a compatible cached packet from an earlier
explicit research run, but cache presence cannot change its outer priority
tier.

### 4. Frozen live scholarly enrichment

For each shortlisted problem, create at most two deterministic queries:

1. an exact-object query derived from the normalized statement, tags, and the
   Erdős problem number;
2. a surrounding-work query derived from the strongest local related results,
   citation keys, and method terms.

Each query searches arXiv, Crossref, Semantic Scholar, and MathOverflow through
the existing allowlisted retrievers, with at most five results per source.
Duplicate papers are collapsed by canonical arXiv ID, DOI, Semantic Scholar ID,
or MathOverflow question ID.

Artifacts are stored under:

`triage/literature/ranking/<source_snapshot_id>/<problem_number>/<query_hash>.json`

Each immutable artifact records:

- schema and literature-policy versions;
- problem, statement, source-snapshot, and query hashes;
- query text and retrieval time;
- retriever/source versions and per-source coverage;
- exact returned records with source URI, version, content hash, title,
  abstract/extract, authors, and date;
- deduplication identities;
- feature values and exact supporting snippets;
- artifact content hash.

Normal reranks reuse only an exact compatible artifact. `--refresh-literature`
performs live retrieval. `--offline-literature` forbids network access and uses
compatible cached artifacts plus the local index. An incompatible cache is
ignored rather than partially reused.

### 5. Literature opportunity features

Live and local evidence produce four normalized, auditable values in `[0, 1]`:

- `foothold`: density of nearby proved results, explicit partial cases, useful
  reductions, and independently checkable finite/formal subtargets;
- `reuse`: likelihood that a route or formal component transfers to other
  corpus problems;
- `machinery_risk`: explicit dependence on major unresolved conjectures or
  machinery far outside the available toolset;
- `status_risk`: source conflicts, full-solution claims, or strong
  already-known/rediscovery signals.

The exact component counts and caps are emitted beside the normalized values.
The first version uses transparent fixed weights and the model identifier
`literature-opportunity-v1`. Fixed weights are weak priors until enough exact
context outcome records exist to fit them. No vendor reputation, prize amount,
or raw hit count is a solvability oracle.

Within each prize tier, solve-oriented acquisition uses:

`base acquisition + 0.02 * foothold + 0.01 * reuse - 0.02 * machinery_risk`

`status_risk >= 0.5` creates a lower literature-status tier before numerical
sorting, so likely rediscoveries do not occupy novel-solution slots. It does not
remove them from the literature-cleanup ranking.

The small bounded coefficients keep literature from overwhelming the current
weak posterior. They are recorded in every ranking snapshot and can later be
replaced only by a versioned, evaluated calibration.

### 6. Queue construction

The following solve-oriented products apply the strict prize tier and
literature-aware order:

- `direct_solve_probability`;
- `diversified_attack_queue`;
- `allocation_queue`;
- `highest_probability_verified_novel_solution`;
- `highest_probability_verified_partial_progress`;
- `highest_probability_lean_verification`;
- `best_finite_computation_targets`;
- `tractable_frontier`;
- `highest_value_uncertain_problems`;
- `protected_exploration`.

Descriptive products remain prize-neutral because they answer different
questions:

- `most_likely_stale_literature_records`;
- `highest_mathematical_value_targets`;
- `highest_reusable_formal_infrastructure_value`;
- `highest_expected_corpus_wide_unlock`.

The final allocation is constructed in two complete phases. Exploitation and
protected exploration are interleaved for unpaid problems first. The same lane
cadence then restarts for paid problems. `problem_queue.py` validates the tier
boundary, the reset cadence, contiguous ranks, and per-row prize metadata.

### 7. Ranking-card auditability

Every solve-oriented ranking row adds:

- `prize` and `prize_status`;
- `selection_priority_tier`;
- `literature_policy_version`;
- `literature_coverage_status`;
- local and live literature artifact hashes;
- `literature_features` with component counts and normalized values;
- `base_acquisition_score`, `literature_adjustment`, and final
  `selection_score`;
- exact positive signals, risks, and coverage gaps.

The top-level ranking snapshot adds the live shortlist, literature coverage
summary, cache reuse counts, source failure counts, and every policy version.
The ranking content hash covers these fields.

## Failure Behavior

- Missing prize metadata withholds allocation and requests a catalog refresh.
- A malformed local corpus record is excluded from its literature feature
  calculation and reported as a coverage gap.
- One scholarly-source outage yields partial coverage; other sources continue.
- All scholarly sources unavailable yields `local_only` coverage, not an empty
  negative search.
- Rate limits preserve the last compatible cache and report staleness; they do
  not penalize the mathematical target.
- A validly hashed but incompatible literature artifact is not reused.
- A status conflict routes the problem toward literature cleanup and lowers its
  novel-solve priority, but only source-authoritative resolution or the existing
  attempt-exclusion process removes it.
- Existing censored outcomes remain operational observations and never become
  mathematical failures.

## Testing Strategy

Implementation follows test-driven development.

1. Catalog tests prove raw prizes in multiple currencies survive ingestion, an
   explicit source `no` becomes unpaid, and a missing field remains unknown.
2. Card tests prove missing prize metadata withholds allocation rather than
   silently treating a problem as unpaid.
3. Local-index tests prove one corpus build serves multiple problem queries and
   produces stable hashes and supporting snippets.
4. Scholarly tests use injected canned responses for all four sources; CI never
   depends on live network access.
5. Cache tests prove exact reuse, invalidation on statement/source/query/policy
   change, immutability, and honest partial coverage.
6. Ranking tests construct a paid high-score target and an unpaid low-score
   target and prove the unpaid target comes first in every solve-oriented lane.
7. Allocation tests prove all unpaid rows precede all paid rows, lane cadence
   restarts at the tier boundary, and ranks remain contiguous.
8. Literature tests prove partial-result footholds can reorder two unpaid
   targets, machinery risk can lower an unpaid target, source failure cannot
   create a bonus, and status-risk records move to the lower status tier.
9. Regression tests prove descriptive mathematical-value and literature-cleanup
   rankings remain prize-neutral.
10. The focused suite is followed by the complete repository test suite and a
    real cached ranking build. A live refresh is a separate explicit smoke test
    because external source availability is not a CI invariant.

## Out of Scope

- Treating prize size as a calibrated hardness estimate.
- Currency conversion.
- Downloading or automatically trusting full paper proofs.
- Letting an LLM assign unaudited literature scores.
- Replacing source-status or novelty gates with search results.
- Training a learned selector before sufficient exact-context outcomes exist.
- Changing the proof, Lean, Aristotle, or promotion gates.

## Research Basis

The design follows three relevant ideas from the reviewed literature:

- The official Erdős database treats prize as first-party metadata, while
  individual problem pages show that rewards can apply to particular directions
  or formulations. This supports preserving the raw field and using only a
  coarse user-selected policy tier.
- Algorithm-selection systems such as SATzilla use cheap instance features and
  empirical performance rather than a single surface heuristic:
  <https://arxiv.org/abs/1111.2249>.
- Risk-aware algorithm selection treats time-limited runs as censored data rather
  than failures, as in Run2Survive:
  <https://proceedings.mlr.press/v129/tornede20a.html>.

The existing protected-exploration lane is therefore retained, and future
weight changes must be justified by exact-context outcomes rather than by prize,
popularity, or source count alone.
