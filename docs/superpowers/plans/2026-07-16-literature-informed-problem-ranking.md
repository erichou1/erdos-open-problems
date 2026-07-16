# Literature-Informed Erdős Problem Ranking Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an auditable local-all/live-shortlist ranking pipeline that uses literature opportunity signals weakly while placing every explicitly unpaid eligible Erdős problem ahead of every paid problem in solve-oriented queues.

**Architecture:** Preserve raw first-party prize metadata and classify it with a fail-closed policy module. Refactor local related-work search into one reusable corpus index, add a frozen four-source scholarly cache and deterministic feature extractor, then integrate those artifacts into ranking scores, allocation context, schemas, and queue validation. Keep Bayesian posteriors and proof/novelty gates unchanged; literature and prize affect selection order only.

**Tech Stack:** Python 3.11+, standard library, PyYAML, existing EGMRA scholarly retrievers, `unittest`, `pytest`, JSON Schema draft 2020-12.

## Global Constraints

- `unpaid` means only the explicit case-insensitive source value `no`; any non-empty monetary string is `paid`; missing, non-string, empty, or malformed values are `unknown`.
- Allocation is withheld when any otherwise eligible problem has `prize_status == "unknown"`.
- Prize amount and currency never change a posterior or the order within a prize tier.
- Every solve-oriented product orders all unpaid rows before all paid rows; descriptive products remain prize-neutral.
- Literature features are weak, bounded, auditable ranking signals and never proof, novelty, resolution, or theorem-premise authority.
- Live enrichment is limited to the first 50 unpaid preliminary candidates, at most two deterministic queries per problem, four allowlisted sources, and at most five records per source.
- The selection adjustment is exactly `0.02 * foothold + 0.01 * reuse - 0.02 * machinery_risk`.
- `status_risk >= 0.5` creates a lower status tier before numerical ordering; it does not remove a problem.
- Source failures and rate limits are coverage gaps, not negative evidence and not tractability bonuses.
- Normal builds perform no network access. Only `--refresh-literature` may retrieve live data; `--offline-literature` explicitly forbids retrieval.
- Do not modify proof, Lean, Aristotle, verification, promotion, or source-authoritative status gates.
- Do not overwrite or commit the already modified `triage/normalized/**`, `triage/rankings/**`, campaign, or status-site files. Run integration builds in a temporary output root and stage commits with explicit file lists.

---

## File Structure

- Create `ranking_policy.py`: closed prize classification, priority-tier, and solve-sort helpers.
- Create `ranking_literature.py`: literature policy constants, local/live feature aggregation, deterministic query construction, compatible immutable cache I/O, and coverage summary.
- Modify `sync_problem_catalog.py`: preserve raw prize bytes, classify each record, and emit catalog counts.
- Modify `literature_research.py`: add a reusable `LiteratureIndex` while retaining `research_literature()` compatibility.
- Modify `egmra/retrieval/scholarly.py`: return explicit per-source coverage without breaking the existing list-returning wrapper.
- Modify `erdos_searcher.py`: copy prize metadata into cards, enrich literature, bind policy/artifact hashes into allocation context, apply strict tiered ordering, and expose CLI controls.
- Modify `problem_queue.py`: validate prize metadata, tier boundaries, and per-tier cadence reset.
- Create `schemas/literature-ranking-artifact.schema.json`: closed schema for frozen query artifacts.
- Modify `schemas/ranking-card.schema.json`: require selection-policy and literature audit fields.
- Modify `schemas/problem-card.schema.json`: constrain prize and literature metadata nested in cards.
- Modify `tests/test_problem_catalog.py`, `tests/test_literature_research.py`, `egmra/tests/test_scholarly.py`, `tests/test_erdos_searcher.py`, `tests/test_problem_queue.py`, and `tests/test_artifact_schemas.py`.
- Create `tests/test_ranking_policy.py` and `tests/test_ranking_literature.py` for focused unit coverage.
- Modify `problem_catalog.json` only after the code and tests pass, using the official synchronization command; do not regenerate the shared `triage/` tree.

---

### Task 1: Fail-Closed Prize Metadata

**Files:**
- Create: `ranking_policy.py`
- Create: `tests/test_ranking_policy.py`
- Modify: `sync_problem_catalog.py:111-159`
- Modify: `tests/test_problem_catalog.py`

**Interfaces:**
- Produces: `PRIZE_POLICY_VERSION: str`, `classify_prize(value: object) -> Literal["unpaid", "paid", "unknown"]`, `selection_priority_tier(prize_status: str) -> int`, and catalog fields `prize`, `prize_status`.
- Consumes: raw upstream `problem["prize"]` without normalization.

- [ ] **Step 1: Write prize-policy and catalog tests**

```python
# tests/test_ranking_policy.py
import pytest

from ranking_policy import classify_prize, selection_priority_tier


@pytest.mark.parametrize("value", ["no", "NO", " No "])
def test_only_explicit_no_is_unpaid(value):
    assert classify_prize(value) == "unpaid"


@pytest.mark.parametrize("value", ["$500", "10,000 USD", "€500", "£500"])
def test_monetary_strings_are_paid_without_currency_conversion(value):
    assert classify_prize(value) == "paid"


@pytest.mark.parametrize("value", [None, "", "   ", 500, {}, []])
def test_missing_or_malformed_prize_is_unknown(value):
    assert classify_prize(value) == "unknown"


def test_priority_tier_rejects_unknown():
    assert selection_priority_tier("unpaid") == 0
    assert selection_priority_tier("paid") == 1
    with pytest.raises(ValueError, match="unknown prize metadata"):
        selection_priority_tier("unknown")
```

Append to `tests/test_problem_catalog.py`:

```python
def test_build_catalog_preserves_raw_prize_and_counts_states(self):
    source = [
        {"number": "1", "prize": "no", "status": {"state": "open"}},
        {"number": "2", "prize": "$5000", "status": {"state": "open"}},
        {"number": "3", "status": {"state": "open"}},
        {"number": "4", "prize": "€500", "status": {"state": "proved"}},
    ]
    catalog = build_catalog(source, fetched_at="now", source_url="source")
    assert catalog["problems"]["1"]["prize"] == "no"
    assert catalog["problems"]["1"]["prize_status"] == "unpaid"
    assert catalog["problems"]["2"]["prize"] == "$5000"
    assert catalog["problems"]["2"]["prize_status"] == "paid"
    assert catalog["problems"]["3"]["prize"] is None
    assert catalog["problems"]["3"]["prize_status"] == "unknown"
    assert catalog["counts"]["monetary_prize"] == 2
    assert catalog["counts"]["open_monetary_prize"] == 1
    assert catalog["counts"]["unknown_prize"] == 1
```

- [ ] **Step 2: Run the focused tests and confirm the missing module/fields fail**

Run: `python -m pytest tests/test_ranking_policy.py tests/test_problem_catalog.py -q`

Expected: collection fails with `ModuleNotFoundError: No module named 'ranking_policy'`.

- [ ] **Step 3: Implement the closed prize policy**

```python
# ranking_policy.py
from __future__ import annotations

from typing import Literal

PrizeStatus = Literal["unpaid", "paid", "unknown"]
PRIZE_POLICY_VERSION = "strict-unpaid-first-v1"


def classify_prize(value: object) -> PrizeStatus:
    if not isinstance(value, str) or not value.strip():
        return "unknown"
    if value.strip().casefold() == "no":
        return "unpaid"
    if any(character.isdigit() for character in value):
        return "paid"
    return "unknown"


def selection_priority_tier(prize_status: str) -> int:
    if prize_status == "unpaid":
        return 0
    if prize_status == "paid":
        return 1
    raise ValueError("unknown prize metadata cannot enter allocation")
```

In `sync_problem_catalog.py`, import `classify_prize`, preserve `problem.get("prize")`, add `prize_status`, and calculate the three counts from entries. Do not transform the raw value.

```python
raw_prize = problem.get("prize")
entry = {
    # existing fields remain unchanged
    "prize": raw_prize,
    "prize_status": classify_prize(raw_prize),
}

# inside catalog["counts"]
"monetary_prize": sum(item["prize_status"] == "paid" for item in entries.values()),
"open_monetary_prize": sum(
    item["prize_status"] == "paid" and not item["source_reports_resolved"]
    for item in entries.values()
),
"unknown_prize": sum(item["prize_status"] == "unknown" for item in entries.values()),
```

- [ ] **Step 4: Run focused tests**

Run: `python -m pytest tests/test_ranking_policy.py tests/test_problem_catalog.py -q`

Expected: all tests pass.

- [ ] **Step 5: Commit the prize ingestion unit**

```bash
git add ranking_policy.py sync_problem_catalog.py tests/test_ranking_policy.py tests/test_problem_catalog.py
git commit -m "feat: preserve prize metadata for ranking"
```

### Task 2: Reusable Local Literature Index

**Files:**
- Modify: `literature_research.py:130-290`
- Modify: `tests/test_literature_research.py`

**Interfaces:**
- Produces: `LiteratureIndex(root: Path)`, `LiteratureIndex.research(problem_number: int, *, max_related: int = 6, max_results_each: int = 3, max_refs: int = 15, min_cosine: float = 0.05) -> LiteratureContext`, `LiteratureIndex.source_hashes(problem_number: int) -> tuple[str, ...]`, and the existing compatibility wrapper `research_literature(root, problem_number, *, max_related=6, max_results_each=3, max_refs=15, min_cosine=0.05) -> LiteratureContext`.
- Consumes: `problem_catalog.json` plus `individual/problem_<n>.tex` from a corpus root.

- [ ] **Step 1: Add tests proving one load serves multiple queries and hashes are stable**

```python
def test_index_loads_corpus_once_and_serves_multiple_queries(monkeypatch):
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        make_corpus(root)
        calls = 0
        original = L._corpus_texts

        def counted(path):
            nonlocal calls
            calls += 1
            return original(path)

        monkeypatch.setattr(L, "_corpus_texts", counted)
        index = L.LiteratureIndex(root)
        first = index.research(1)
        second = index.research(2)
        assert calls == 1
        assert first.related
        assert second.related


def test_index_records_stable_local_source_hashes():
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        make_corpus(root)
        first = L.LiteratureIndex(root)
        second = L.LiteratureIndex(root)
        assert first.source_hashes(1) == second.source_hashes(1)
        assert all(len(value) == 64 for value in first.source_hashes(1))
```

- [ ] **Step 2: Run the new tests and confirm `LiteratureIndex` is absent**

Run: `python -m pytest tests/test_literature_research.py -q`

Expected: failures report `AttributeError: module 'literature_research' has no attribute 'LiteratureIndex'`.

- [ ] **Step 3: Refactor corpus loading into an immutable index**

Add a private frozen `_IndexedProblem` record holding number, raw text, display text, tags, citations, tokens, TF-IDF vector, and source SHA-256. Move the existing document-frequency and similarity preparation from `research_literature()` into `LiteratureIndex.__init__`, and move only target-specific scoring/rendering into `research()`.

```python
@dataclass(frozen=True)
class _IndexedProblem:
    number: int
    raw_tex: str
    text: str
    tags: frozenset[str]
    citations: frozenset[str]
    vector: dict[str, float]
    source_sha256: str


class LiteratureIndex:
    def __init__(self, root: Path):
        self.root = Path(root)
        texts = _corpus_texts(self.root)
        tags = _load_tags(self.root)
        token_map = {number: tokens(display_text(tex)) for number, tex in texts.items()}
        document_frequency = Counter(
            word for document_tokens in token_map.values() for word in set(document_tokens)
        )
        document_count = max(1, len(texts))
        self._problems = {
            number: _IndexedProblem(
                number=number,
                raw_tex=tex,
                text=display_text(tex),
                tags=frozenset(tags.get(number, set())),
                citations=frozenset(citations(tex)),
                vector=_tfidf(token_map[number], document_frequency, document_count),
                source_sha256=hashlib.sha256(tex.encode("utf-8")).hexdigest(),
            )
            for number, tex in texts.items()
        }

    def source_hashes(self, problem_number: int) -> tuple[str, ...]:
        target = self._problems.get(problem_number)
        if target is None:
            return ()
        context = self.research(problem_number)
        numbers = [problem_number, *(item.number for item in context.related)]
        return tuple(self._problems[number].source_sha256 for number in numbers)

    def research(
        self, problem_number: int, *, max_related: int = 6,
        max_results_each: int = 3, max_refs: int = 15,
        min_cosine: float = 0.05,
    ) -> LiteratureContext:
        target = self._problems.get(problem_number)
        if target is None:
            return LiteratureContext(problem_number, (), (), "", "")
        scored: list[RelatedProblem] = []
        for number, candidate in self._problems.items():
            if number == problem_number:
                continue
            shared_tags = set(target.tags & candidate.tags)
            shared_citations = set(target.citations & candidate.citations)
            cosine = _cosine(target.vector, candidate.vector)
            score = (
                0.40 * _jaccard(set(target.tags), set(candidate.tags))
                + 0.35 * _jaccard(set(target.citations), set(candidate.citations))
                + 0.25 * cosine
            )
            if score <= 0 or not (
                shared_tags or shared_citations or cosine >= min_cosine
            ):
                continue
            scored.append(RelatedProblem(
                number=number,
                score=round(score, 3),
                shared_tags=tuple(sorted(shared_tags)),
                shared_citations=tuple(sorted(shared_citations)),
                statement=_statement_snippet(candidate.raw_tex),
                results=_result_sentences(candidate.raw_tex, max_results_each),
            ))
        scored.sort(key=lambda item: (-item.score, item.number))
        related = scored[:max_related]
        references = tuple(sorted(
            set().union(*(self._problems[item.number].citations for item in related))
            or set(target.citations)
        ))[:max_refs]
        rendered = _render(problem_number, related, references)
        digest = hashlib.sha256(rendered.encode("utf-8")).hexdigest() if rendered else ""
        return LiteratureContext(
            problem_number, tuple(related), references, rendered, digest
        )


def research_literature(
    root: Path, problem_number: int, *, max_related: int = 6,
    max_results_each: int = 3, max_refs: int = 15,
    min_cosine: float = 0.05,
) -> LiteratureContext:
    return LiteratureIndex(root).research(
        problem_number, max_related=max_related,
        max_results_each=max_results_each, max_refs=max_refs,
        min_cosine=min_cosine,
    )
```

- [ ] **Step 4: Run local literature tests**

Run: `python -m pytest tests/test_literature_research.py -q`

Expected: all tests pass, including existing relevance and untrusted-rendering tests.

- [ ] **Step 5: Commit the reusable index**

```bash
git add literature_research.py tests/test_literature_research.py
git commit -m "refactor: index local literature once"
```

### Task 3: Scholarly Retrieval Coverage

**Files:**
- Modify: `egmra/retrieval/scholarly.py:324-360`
- Modify: `egmra/tests/test_scholarly.py`

**Interfaces:**
- Produces: `ScholarlySearchResult(records: tuple[TheoremRecord, ...], coverage: dict[str, str])` and `search_scholarly_sources(query: str, *, fetcher: Fetcher, sources: tuple[str, ...] = SCHOLARLY_SOURCES, limit: int = 5) -> ScholarlySearchResult`.
- Preserves: `build_scholarly_corpus(query: str, *, fetcher: Fetcher, sources: tuple[str, ...] = SCHOLARLY_SOURCES, limit: int = 5) -> list[TheoremRecord]` as a compatibility wrapper.

- [ ] **Step 1: Add tests for complete and partial coverage**

```python
def test_search_reports_each_source_coverage(canned_fetcher):
    result = search_scholarly_sources("Ramsey graph", fetcher=canned_fetcher, limit=5)
    assert set(result.coverage) == set(SCHOLARLY_SOURCES)
    assert set(result.coverage.values()) == {"complete"}
    assert result.records


def test_source_outage_is_coverage_gap_not_empty_negative(monkeypatch, canned_fetcher):
    class BrokenRetriever:
        def __init__(self, *, fetcher):
            pass

        def search(self, query, limit):
            raise ScholarlyRetrievalError("rate limited")

    monkeypatch.setitem(_RETRIEVERS, "arxiv", BrokenRetriever)
    result = search_scholarly_sources("Ramsey graph", fetcher=canned_fetcher, limit=5)
    assert result.coverage["arxiv"] == "unavailable"
    assert any(value == "complete" for key, value in result.coverage.items() if key != "arxiv")
    assert build_scholarly_corpus("Ramsey graph", fetcher=canned_fetcher, limit=5) == list(result.records)
```

- [ ] **Step 2: Run scholarly tests and confirm the new API fails**

Run: `python -m pytest egmra/tests/test_scholarly.py -q`

Expected: import or name failure for `search_scholarly_sources`.

- [ ] **Step 3: Implement explicit per-source coverage**

```python
@dataclass(frozen=True)
class ScholarlySearchResult:
    records: tuple[TheoremRecord, ...]
    coverage: dict[str, str]


def search_scholarly_sources(
    query: str,
    *,
    fetcher: Fetcher,
    sources: tuple[str, ...] = SCHOLARLY_SOURCES,
    limit: int = 5,
) -> ScholarlySearchResult:
    if not query or not query.strip():
        return ScholarlySearchResult((), {name: "not_queried" for name in sources})
    records: list[TheoremRecord] = []
    coverage: dict[str, str] = {}
    seen: set[str] = set()
    for name in sources:
        retriever_cls = _RETRIEVERS.get(name)
        if retriever_cls is None:
            coverage[name] = "unsupported"
            continue
        try:
            found = retriever_cls(fetcher=fetcher).search(query, limit=limit)
        except ScholarlyRetrievalError:
            coverage[name] = "unavailable"
            continue
        coverage[name] = "complete"
        for record in found:
            if record.theorem_id not in seen and record.is_auditable():
                seen.add(record.theorem_id)
                records.append(record)
    return ScholarlySearchResult(tuple(records), coverage)


def build_scholarly_corpus(query: str, *, fetcher: Fetcher,
                            sources: tuple[str, ...] = SCHOLARLY_SOURCES,
                            limit: int = 5) -> list[TheoremRecord]:
    return list(search_scholarly_sources(
        query, fetcher=fetcher, sources=sources, limit=limit
    ).records)
```

- [ ] **Step 4: Run scholarly tests**

Run: `python -m pytest egmra/tests/test_scholarly.py -q`

Expected: all tests pass with no network access.

- [ ] **Step 5: Commit coverage reporting**

```bash
git add egmra/retrieval/scholarly.py egmra/tests/test_scholarly.py
git commit -m "feat: report scholarly source coverage"
```

### Task 4: Frozen Literature Artifacts and Opportunity Features

**Files:**
- Create: `ranking_literature.py`
- Create: `tests/test_ranking_literature.py`
- Create: `schemas/literature-ranking-artifact.schema.json`
- Modify: `tests/test_artifact_schemas.py`

**Interfaces:**
- Consumes: `LiteratureIndex`, a problem card, source snapshot identifiers, and optional injected `Fetcher`.
- Produces: `LITERATURE_POLICY_VERSION`, `LITERATURE_MODEL_VERSION`, `LiteratureEnrichment`, `build_queries(card: dict, local_context: LiteratureContext) -> tuple[LiteratureQuery, ...]`, `build_local_enrichments(cards: list[dict], local_index: LiteratureIndex) -> dict[int, LiteratureEnrichment]`, `select_live_shortlist(preliminary_cards: list[dict]) -> tuple[int, ...]`, `enrich_live_shortlist(cards_by_number: dict[int, dict], enrichments: dict[int, LiteratureEnrichment], *, shortlist_problem_numbers: tuple[int, ...], cache_root: Path, source_snapshot_id: str, refresh: bool, offline: bool, fetcher: Fetcher | None = None) -> dict[int, LiteratureEnrichment]`, `literature_adjustment(features: dict[str, float]) -> float`, immutable cache artifacts, and aggregate coverage statistics.

- [ ] **Step 1: Write deterministic query, feature, cache, and failure tests**

```python
def test_queries_are_deterministic_and_capped_at_two(sample_card, local_context):
    first = build_queries(sample_card, local_context)
    second = build_queries(sample_card, local_context)
    assert first == second
    assert 1 <= len(first) <= 2
    assert all(query.query_hash == sha256_text(query.text) for query in first)


def test_adjustment_uses_exact_bounded_weights():
    features = {"foothold": 0.75, "reuse": 0.5, "machinery_risk": 0.25, "status_risk": 0.0}
    assert literature_adjustment(features) == pytest.approx(0.015)


def test_partial_result_snippet_can_raise_foothold(sample_card, local_index):
    result = local_features(sample_card, local_index.research(sample_card["problem_number"]))
    assert result["foothold"] > 0
    assert result["components"]["partial_result_snippets"]


def test_unknown_source_coverage_never_creates_a_bonus(sample_card, local_index):
    enrichment = build_local_enrichments([sample_card], local_index)[
        sample_card["problem_number"]
    ]
    assert enrichment.coverage_status == "local_only"
    assert enrichment.live_artifact_hashes == ()
    assert enrichment.features["foothold"] == enrichment.local_features["foothold"]


def test_cache_reuse_requires_exact_statement_source_query_and_policy(tmp_path, sample_card, local_index, canned_fetcher):
    local = build_local_enrichments([sample_card], local_index)
    cards = {sample_card["problem_number"]: sample_card}
    first = enrich_live_shortlist(
        cards, local, shortlist_problem_numbers=(sample_card["problem_number"],),
        cache_root=tmp_path,
        source_snapshot_id="snapshot-a", refresh=True, offline=False,
        fetcher=canned_fetcher,
    )[sample_card["problem_number"]]
    second = enrich_live_shortlist(
        cards, local, shortlist_problem_numbers=(sample_card["problem_number"],),
        cache_root=tmp_path,
        source_snapshot_id="snapshot-a", refresh=False, offline=True,
    )[sample_card["problem_number"]]
    changed = {**sample_card, "statement": {**sample_card["statement"], "statement_sha256": "f" * 64}}
    invalidated = enrich_live_shortlist(
        {changed["problem_number"]: changed}, local,
        shortlist_problem_numbers=(changed["problem_number"],), cache_root=tmp_path,
        source_snapshot_id="snapshot-a", refresh=False, offline=True,
    )[sample_card["problem_number"]]
    assert second.live_artifact_hashes == first.live_artifact_hashes
    assert invalidated.live_artifact_hashes == ()


def test_live_shortlist_is_first_fifty_unpaid_and_caps_queries(
    tmp_path, monkeypatch, local_index,
):
    cards = [
        {
            "problem_number": number,
            "metadata": {"prize": "no", "prize_status": "unpaid", "tags": ["graphs"], "ai_wiki": {}},
            "statement": {"normalized": f"graph problem {number}", "statement_sha256": f"{number:064x}"},
        }
        for number in range(1, 56)
    ] + [
        {
            "problem_number": number,
            "metadata": {"prize": "$500", "prize_status": "paid", "tags": ["graphs"], "ai_wiki": {}},
            "statement": {"normalized": f"paid graph problem {number}", "statement_sha256": f"{number:064x}"},
        }
        for number in range(56, 61)
    ]
    local = build_local_enrichments(cards, local_index)
    shortlist = select_live_shortlist(cards)
    calls = []

    def fake_search(query, *, fetcher, sources=SCHOLARLY_SOURCES, limit=5):
        calls.append(query)
        return ScholarlySearchResult((), {name: "complete" for name in sources})

    monkeypatch.setattr("ranking_literature.search_scholarly_sources", fake_search)
    enrich_live_shortlist(
        {card["problem_number"]: card for card in cards}, local,
        shortlist_problem_numbers=shortlist, cache_root=tmp_path,
        source_snapshot_id="snapshot-a", refresh=True, offline=False,
        fetcher=object(),
    )
    assert shortlist == tuple(range(1, 51))
    assert len(calls) <= 100
```

- [ ] **Step 2: Run tests and confirm the module is absent**

Run: `python -m pytest tests/test_ranking_literature.py tests/test_artifact_schemas.py -q`

Expected: collection fails with `ModuleNotFoundError: No module named 'ranking_literature'`.

- [ ] **Step 3: Implement the policy constants, query records, feature caps, and exact score**

```python
LITERATURE_POLICY_VERSION = "literature-ranking-v1"
LITERATURE_MODEL_VERSION = "literature-opportunity-v1"
LIVE_SHORTLIST_LIMIT = 50
LIVE_QUERY_LIMIT = 2
LIVE_RESULTS_PER_SOURCE = 5


@dataclass(frozen=True)
class LiteratureQuery:
    text: str
    query_hash: str


@dataclass(frozen=True)
class LiteratureEnrichment:
    coverage_status: str
    local_artifact_hash: str
    live_artifact_hashes: tuple[str, ...]
    local_features: dict
    features: dict
    coverage_gaps: tuple[str, ...]


def literature_adjustment(features: dict[str, float]) -> float:
    return round(
        0.02 * features["foothold"]
        + 0.01 * features["reuse"]
        - 0.02 * features["machinery_risk"],
        6,
    )


def literature_status_tier(features: dict[str, float]) -> int:
    return int(features["status_risk"] >= 0.5)


def select_live_shortlist(preliminary_cards: list[dict]) -> tuple[int, ...]:
    return tuple(
        card["problem_number"]
        for card in preliminary_cards
        if card["metadata"]["prize_status"] == "unpaid"
    )[:LIVE_SHORTLIST_LIMIT]
```

Use these closed first-version patterns; every match stores the exact sentence and signal label:

```python
PARTIAL_RESULT_RE = re.compile(
    r"\b(partial|special case|weaker|upper bound|lower bound|conditional|assuming)\b",
    re.IGNORECASE,
)
REUSE_RE = re.compile(
    r"\b(method|lemma|reduction|construction|formalization|algorithm)\b",
    re.IGNORECASE,
)
MACHINERY_RE = re.compile(
    r"\b(Riemann hypothesis|abc conjecture|Schanuel(?:'s)? conjecture|"
    r"Elliott-Halberstam conjecture|Bateman-Horn conjecture|"
    r"Generalized Riemann hypothesis)\b",
    re.IGNORECASE,
)
STATUS_RE = re.compile(
    r"\b(full solution|solved|settled|proof of (?:the|Erd(?:o|\u0151)s) problem|disproved)\b",
    re.IGNORECASE,
)


def _capped(count: int, cap: int) -> float:
    return round(min(1.0, count / cap), 6)


def aggregate_features(snippets: list[str], *, related_count: int,
                       distinct_citations: int, ai_wiki: dict) -> dict:
    partial = matched_snippets(snippets, PARTIAL_RESULT_RE, "partial_result")
    reuse = matched_snippets(snippets, REUSE_RE, "reusable_method")
    machinery = matched_snippets(snippets, MACHINERY_RE, "deep_machinery")
    status = matched_snippets(snippets, STATUS_RE, "status_conflict")
    status_count = len(status) + int(bool(ai_wiki.get("primary_full"))) \
        + int(bool(ai_wiki.get("secondary_full")))
    return {
        "foothold": _capped(len(partial) + min(2, related_count), 6),
        "reuse": _capped(len(reuse) + min(2, distinct_citations), 6),
        "machinery_risk": _capped(len(machinery), 3),
        "status_risk": _capped(status_count, 2),
        "components": {
            "partial_result_snippets": partial,
            "reuse_snippets": reuse,
            "machinery_snippets": machinery,
            "status_snippets": status,
            "related_problem_count": related_count,
            "distinct_citation_count": distinct_citations,
            "ai_wiki_primary_full": bool(ai_wiki.get("primary_full")),
            "ai_wiki_secondary_full": bool(ai_wiki.get("secondary_full")),
        },
    }
```

`matched_snippets` returns at most five `{"signal": label, "snippet": sentence}` objects in input order. Match sentence-level text only; do not infer beyond the displayed string.

- [ ] **Step 4: Implement compatible immutable artifacts and orchestration**

Artifact path and compatibility must be exact:

```python
def artifact_path(cache_root: Path, source_snapshot_id: str,
                  problem_number: int, query_hash: str) -> Path:
    return (Path(cache_root) / source_snapshot_id / str(problem_number)
            / f"{query_hash}.json")


def artifact_content_sha256(payload: dict) -> str:
    immutable = {key: value for key, value in payload.items() if key != "artifact_content_sha256"}
    return hashlib.sha256(json.dumps(
        immutable, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")).hexdigest()


def compatible_artifact(payload: dict, *, problem_number: int,
                        statement_sha256: str, source_snapshot_id: str,
                        query_hash: str) -> bool:
    return (
        payload.get("schema_version") == 1
        and payload.get("literature_policy_version") == LITERATURE_POLICY_VERSION
        and payload.get("problem_number") == problem_number
        and payload.get("statement_sha256") == statement_sha256
        and payload.get("source_snapshot_id") == source_snapshot_id
        and payload.get("query_hash") == query_hash
        and payload.get("artifact_content_sha256") == artifact_content_sha256(payload)
    )
```

`build_local_enrichments` calculates local features for every card without reading or writing the live cache. `enrich_live_shortlist` rejects more than `LIVE_SHORTLIST_LIMIT` numbers and may call `search_scholarly_sources` only when `refresh is True`, `offline is False`, the card is explicitly unpaid, and the number is in `shortlist_problem_numbers`. Existing compatible cache packets may be loaded for the supplied shortlist without network access. If both `refresh` and `offline` are true, raise `ValueError("refresh and offline literature modes are mutually exclusive")`.

When writing a new artifact, use exclusive creation (`open("x")`). If the path already exists, read and verify exact byte-equivalent immutable content; raise `RuntimeError("immutable literature artifact conflict")` on mismatch.

- [ ] **Step 5: Add the closed literature artifact schema**

Create the schema with this closed top level; `$defs.record` requires the serialized `TheoremRecord` audit fields `theorem_id`, `canonical_statement`, `conclusion`, `source_uri`, `source_version`, `source_content_hash`, `verbatim_theorem_and_hypothesis_extract`, `extraction_method`, `extraction_confidence`, `retrieved_at`, `authors`, `date`, `proof_status`, `independent_verification_status`, and `license`.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://example.invalid/erdos/literature-ranking-artifact.schema.json",
  "title": "Erdos Literature Ranking Artifact",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "schema_version", "literature_policy_version", "literature_model_version",
    "problem_number", "statement_sha256", "source_snapshot_id", "query",
    "query_hash", "retrieved_at", "source_coverage", "records",
    "deduplication_identities", "features", "supporting_snippets",
    "artifact_content_sha256"
  ],
  "properties": {
    "schema_version": {"const": 1},
    "literature_policy_version": {"const": "literature-ranking-v1"},
    "literature_model_version": {"const": "literature-opportunity-v1"},
    "problem_number": {"type": "integer", "minimum": 1},
    "statement_sha256": {"$ref": "#/$defs/hash"},
    "source_snapshot_id": {"type": "string", "minLength": 1},
    "query": {"type": "string", "minLength": 1},
    "query_hash": {"$ref": "#/$defs/hash"},
    "retrieved_at": {"type": "string", "format": "date-time"},
    "source_coverage": {
      "type": "object", "additionalProperties": false,
      "required": ["arxiv", "crossref", "semanticscholar", "mathoverflow"],
      "properties": {
        "arxiv": {"$ref": "#/$defs/coverage"},
        "crossref": {"$ref": "#/$defs/coverage"},
        "semanticscholar": {"$ref": "#/$defs/coverage"},
        "mathoverflow": {"$ref": "#/$defs/coverage"}
      }
    },
    "records": {"type": "array", "items": {"$ref": "#/$defs/record"}},
    "deduplication_identities": {"type": "array", "items": {"type": "string"}},
    "features": {"$ref": "#/$defs/features"},
    "supporting_snippets": {"type": "array", "items": {"$ref": "#/$defs/snippet"}},
    "artifact_content_sha256": {"$ref": "#/$defs/hash"}
  },
  "$defs": {
    "hash": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
    "coverage": {"enum": ["complete", "unavailable", "unsupported", "not_queried"]},
    "features": {
      "type": "object",
      "required": ["foothold", "reuse", "machinery_risk", "status_risk", "components"],
      "properties": {
        "foothold": {"type": "number", "minimum": 0, "maximum": 1},
        "reuse": {"type": "number", "minimum": 0, "maximum": 1},
        "machinery_risk": {"type": "number", "minimum": 0, "maximum": 1},
        "status_risk": {"type": "number", "minimum": 0, "maximum": 1},
        "components": {"type": "object"}
      }
    },
    "snippet": {
      "type": "object", "required": ["signal", "snippet"],
      "properties": {"signal": {"type": "string"}, "snippet": {"type": "string"}}
    },
    "record": {
      "type": "object",
      "required": [
        "theorem_id", "canonical_statement", "conclusion", "source_uri",
        "source_version", "source_content_hash",
        "verbatim_theorem_and_hypothesis_extract", "extraction_method",
        "extraction_confidence", "retrieved_at", "authors", "date",
        "proof_status", "independent_verification_status", "license"
      ],
      "properties": {
        "theorem_id": {"type": "string"}, "canonical_statement": {"type": "string"},
        "conclusion": {"type": "string"}, "source_uri": {"type": "string"},
        "source_version": {"type": "string"}, "source_content_hash": {"$ref": "#/$defs/hash"},
        "verbatim_theorem_and_hypothesis_extract": {"type": "string"},
        "extraction_method": {"type": "string"},
        "extraction_confidence": {"type": "number", "minimum": 0, "maximum": 1},
        "retrieved_at": {"type": "string"},
        "authors": {"type": "array", "items": {"type": "string"}},
        "date": {"type": ["string", "null"]}, "proof_status": {"type": "string"},
        "independent_verification_status": {"type": "string"},
        "license": {"type": ["string", "null"]}
      }
    }
  }
}
```

Add `literature-ranking-artifact.schema.json` to the `names` tuple in `tests/test_artifact_schemas.py`.

- [ ] **Step 6: Run feature/cache/schema tests**

Run: `python -m pytest tests/test_ranking_literature.py tests/test_artifact_schemas.py egmra/tests/test_scholarly.py tests/test_literature_research.py -q`

Expected: all tests pass and canned fetchers are the only retrieval mechanism.

- [ ] **Step 7: Commit the literature ranking unit**

```bash
git add ranking_literature.py tests/test_ranking_literature.py schemas/literature-ranking-artifact.schema.json tests/test_artifact_schemas.py
git commit -m "feat: add auditable literature ranking artifacts"
```

### Task 5: Bind Literature and Prize Policy into Problem Cards and Builds

**Files:**
- Modify: `erdos_searcher.py:135-151,382-408,1040-1125,2430-2780,3043-3070`
- Modify: `tests/test_erdos_searcher.py`

**Interfaces:**
- Consumes: `classify_prize`, `PRIZE_POLICY_VERSION`, `LiteratureIndex`, `enrich_cards`, and optional scholarly `Fetcher`.
- Produces: the existing `build_searcher` interface extended with keyword-only `refresh_literature: bool = False`, `offline_literature: bool = False`, and `scholarly_fetcher: Fetcher | None = None`; card metadata and allocation context bind prize/literature policy and artifact hashes.

- [ ] **Step 1: Add card, allocation-withholding, shortlist, cache-only, and CLI tests**

First update `make_repo()` so records 1, 2, and 3 each contain `"prize": "no"` and `"prize_status": "unpaid"`; this keeps every existing build test on a complete catalog.

```python
def test_card_copies_raw_prize_and_status(self):
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        self.make_repo(root)
        catalog_path = root / "problem_catalog.json"
        catalog = json.loads(catalog_path.read_text())
        catalog["problems"]["1"].update({"prize": "$5000", "prize_status": "paid"})
        catalog_path.write_text(json.dumps(catalog))
        build_searcher(
            root, root / "triage", snapshot_date="2026-07-12", top_k=5,
            model_portfolio="model-a", offline_literature=True,
        )
        card = json.loads(
            (root / "triage" / "normalized" / "problem_cards" / "1.json").read_text()
        )
        self.assertEqual(card["metadata"]["prize"], "$5000")
        self.assertEqual(card["metadata"]["prize_status"], "paid")


def test_unknown_eligible_prize_withholds_allocation(self):
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        self.make_repo(root)
        catalog_path = root / "problem_catalog.json"
        catalog = json.loads(catalog_path.read_text())
        catalog["problems"]["1"].update({"prize": None, "prize_status": "unknown"})
        catalog_path.write_text(json.dumps(catalog))
        ranking = build_searcher(
            root, root / "triage", snapshot_date="2026-07-12", top_k=5,
            model_portfolio="model-a", offline_literature=True,
        )
        self.assertEqual(ranking["unknown_prize_problem_numbers"], [1])
        self.assertEqual(ranking["allocation_status"], "withheld_unknown_prize_metadata")
        self.assertEqual(ranking["allocation_queue"], [])


def test_normal_build_never_constructs_live_fetcher(self):
    with tempfile.TemporaryDirectory() as directory, mock.patch(
        "ranking_literature.UrllibFetcher",
        side_effect=AssertionError("network attempted"),
    ):
        root = Path(directory)
        self.make_repo(root)
        ranking = build_searcher(
            root, root / "triage", snapshot_date="2026-07-12", top_k=5,
            model_portfolio="model-a", refresh_literature=False,
            offline_literature=False,
        )
        self.assertEqual(ranking["literature_coverage"]["live_requests"], 0)
```

The 55-unpaid/5-paid shortlist test added in Task 4 exercises the cap directly without creating 60 canonical ingestion snapshots.

- [ ] **Step 2: Run focused searcher tests and confirm new arguments/fields fail**

Run: `python -m pytest tests/test_erdos_searcher.py -q`

Expected: failures identify absent `prize_status`, `offline_literature`, and literature summary fields.

- [ ] **Step 3: Copy metadata and enrich cards before allocation context creation**

Add to `build_card.metadata`:

```python
"prize": entry.get("prize"),
"prize_status": entry.get("prize_status", classify_prize(entry.get("prize"))),
"ai_wiki": dict(entry.get("ai_wiki") or {}),
```

In `build_searcher`, build cards first and add corpus-unlock posteriors. Create one `LiteratureIndex(root / "open")`, call `build_local_enrichments(cards, index)`, attach those local records under `card["probe_summary"]["literature_ranking"]`, and calculate the preliminary solve order. Pass that ordered list to `select_live_shortlist`, then call `enrich_live_shortlist` with cache root `output_root / "literature" / "ranking"`; replace the local records with the returned combined audit records before writing cards. Recompute the final solve rankings only after live/cache enrichment.

Move `make_allocation_context` after enrichment and extend it with exact fields:

```python
def make_allocation_context(
    *, root: Path, snapshot_id: str, source_snapshot_sha256: str,
    source_snapshot_id: str, canonical_open_source_records: int,
    pipeline_version: str, model_portfolio: str, budget: str,
    budget_config: dict | BudgetConfig, allocation_top_k: int,
    prize_policy_version: str, literature_policy_version: str,
    literature_model_version: str, literature_snapshot_sha256: str,
    live_shortlist_limit: int,
) -> tuple[dict, str | None]:
    context = {
        # existing exact context fields
        "prize_policy_version": prize_policy_version,
        "literature_policy_version": literature_policy_version,
        "literature_model_version": literature_model_version,
        "literature_snapshot_sha256": literature_snapshot_sha256,
        "literature_live_shortlist_limit": int(live_shortlist_limit),
    }
```

The literature snapshot hash is the canonical hash of policy versions, per-card local hashes, compatible live artifact hashes, coverage states, shortlist problem numbers, and fixed weights. Assign the resulting `allocation_context_id` to cards only after this hash exists.

- [ ] **Step 4: Implement fail-closed allocation readiness and top-level audit summary**

```python
unknown_prize_numbers = sorted(
    card["problem_number"] for card in eligible
    if card["metadata"]["prize_status"] == "unknown"
)
allocation_ready = (
    not unknown_prize_numbers
    and allocation_context_id is not None
    and all(card.get("run_contract_id") for card in eligible)
    and integrity["status"] == "complete"
)
allocation_status = (
    "withheld_unknown_prize_metadata" if unknown_prize_numbers
    else "ready" if allocation_ready
    else "withheld_until_complete_exact_recorded_context"
)
```

Add top-level fields `prize_policy_version`, `literature_policy_version`, `literature_model_version`, `unknown_prize_problem_numbers`, `literature_live_shortlist`, `literature_coverage`, and `literature_snapshot_sha256`. These fields must be present before `ranking_content_sha256` is calculated.

- [ ] **Step 5: Add mutually exclusive CLI controls**

```python
literature_mode = parser.add_mutually_exclusive_group()
literature_mode.add_argument("--refresh-literature", action="store_true")
literature_mode.add_argument("--offline-literature", action="store_true")
```

Pass both booleans into `build_searcher`. The default mode loads compatible cache but does not construct `UrllibFetcher`; refresh constructs it only if no injected fetcher was supplied.

- [ ] **Step 6: Include all ranking-defining files in the pipeline fingerprint**

Add `ranking_policy.py`, `ranking_literature.py`, `literature_research.py`, `egmra/retrieval/scholarly.py`, `schemas/problem-card.schema.json`, `schemas/ranking-card.schema.json`, and `schemas/literature-ranking-artifact.schema.json` to `PIPELINE_FINGERPRINT_FILES`.

- [ ] **Step 7: Run focused tests**

Run: `python -m pytest tests/test_erdos_searcher.py tests/test_searcher_safety.py tests/test_ranking_literature.py -q`

Expected: all tests pass with no live network calls.

- [ ] **Step 8: Commit build integration**

```bash
git add erdos_searcher.py tests/test_erdos_searcher.py
git commit -m "feat: bind literature evidence into ranking builds"
```

### Task 6: Strict Unpaid-First Solve Rankings

**Files:**
- Modify: `ranking_policy.py`
- Modify: `erdos_searcher.py:1288-1490,2550-2700`
- Modify: `tests/test_ranking_policy.py`
- Modify: `tests/test_erdos_searcher.py`

**Interfaces:**
- Produces: `solve_sort_key(card, *, base_score: float)`, `selection_fields(card, *, base_score: float)`, `build_ranking_products(cards: list[dict], *, top_k: int, allocation_ready: bool) -> dict`, literature-aware ranking rows, and two-phase `interleave_allocation`.
- Consumes: prize status and `probe_summary.literature_ranking.features` from Task 5.

- [ ] **Step 1: Add regression tests across every solve-oriented and descriptive lane**

Add `copy` to the imports in `tests/test_erdos_searcher.py`, import `build_ranking_products`, and add this helper to `ErdosSearcherTests`:

```python
def policy_cards(self, root: Path, specifications: list[dict]) -> list[dict]:
    self.make_repo(root)
    build_searcher(
        root, root / "triage", snapshot_date="2026-07-12", top_k=5,
        model_portfolio="model-a", offline_literature=True,
    )
    base = json.loads(
        (root / "triage" / "normalized" / "problem_cards" / "1.json").read_text()
    )
    cards = []
    for specification in specifications:
        card = copy.deepcopy(base)
        number = specification["number"]
        card["problem_number"] = number
        card["problem_id"] = f"erdos-{number}"
        card["metadata"]["prize"] = specification["prize"]
        card["metadata"]["prize_status"] = specification["prize_status"]
        for posterior in card["posterior"].values():
            if isinstance(posterior, dict) and "probability" in posterior:
                posterior["probability"] = specification.get("probability", 0.2)
        features = card["probe_summary"]["literature_ranking"]["features"]
        features.update(specification.get("features", {}))
        cards.append(card)
    return cards
```

Then add these tests:

```python
SOLVE_ORIENTED = (
    "direct_solve_probability", "diversified_attack_queue", "allocation_queue",
    "highest_probability_verified_novel_solution",
    "highest_probability_verified_partial_progress",
    "highest_probability_lean_verification", "best_finite_computation_targets",
    "tractable_frontier", "highest_value_uncertain_problems", "protected_exploration",
)


def test_paid_high_score_never_precedes_unpaid_low_score(self):
    with tempfile.TemporaryDirectory() as directory:
        cards = self.policy_cards(Path(directory), [
            {"number": 1, "prize": "no", "prize_status": "unpaid", "probability": 0.01},
            {"number": 2, "prize": "no", "prize_status": "unpaid", "probability": 0.02},
            {"number": 3, "prize": "no", "prize_status": "unpaid", "probability": 0.03},
            {"number": 4, "prize": "$500", "prize_status": "paid", "probability": 0.97},
            {"number": 5, "prize": "$5000", "prize_status": "paid", "probability": 0.98},
            {"number": 6, "prize": "10000 USD", "prize_status": "paid", "probability": 0.99},
        ])
        ranking = build_ranking_products(cards, top_k=6, allocation_ready=True)
        for lane in SOLVE_ORIENTED:
            statuses = [row["prize_status"] for row in ranking[lane]]
            self.assertEqual(
                statuses, sorted(statuses, key={"unpaid": 0, "paid": 1}.__getitem__),
                lane,
            )


def test_literature_foothold_reorders_two_unpaid_cards(self):
    with tempfile.TemporaryDirectory() as directory:
        cards = self.policy_cards(Path(directory), [
            {"number": 1, "prize": "no", "prize_status": "unpaid", "probability": 0.2,
             "features": {"foothold": 0.0}},
            {"number": 2, "prize": "no", "prize_status": "unpaid", "probability": 0.2,
             "features": {"foothold": 1.0}},
        ])
        ranking = build_ranking_products(cards, top_k=2, allocation_ready=True)
        self.assertEqual(
            [row["problem_number"] for row in ranking["direct_solve_probability"]],
            [2, 1],
        )


def test_status_risk_precedes_numeric_score_within_unpaid_tier(self):
    with tempfile.TemporaryDirectory() as directory:
        cards = self.policy_cards(Path(directory), [
            {"number": 1, "prize": "no", "prize_status": "unpaid", "probability": 0.99,
             "features": {"status_risk": 0.6}},
            {"number": 2, "prize": "no", "prize_status": "unpaid", "probability": 0.01,
             "features": {"status_risk": 0.0}},
        ])
        ranking = build_ranking_products(cards, top_k=2, allocation_ready=True)
        self.assertEqual(ranking["direct_solve_probability"][0]["problem_number"], 2)


def test_descriptive_products_are_prize_neutral(self):
    with tempfile.TemporaryDirectory() as directory:
        cards = self.policy_cards(Path(directory), [
            {"number": 1, "prize": "no", "prize_status": "unpaid", "probability": 0.01},
            {"number": 2, "prize": "$500", "prize_status": "paid", "probability": 0.99},
        ])
        ranking = build_ranking_products(cards, top_k=2, allocation_ready=True)
        self.assertEqual(ranking["highest_mathematical_value_targets"][0]["prize_status"], "paid")
        self.assertEqual(ranking["most_likely_stale_literature_records"][0]["prize_status"], "paid")
```

- [ ] **Step 2: Run the ranking tests and verify paid rows currently leak upward**

Run: `python -m pytest tests/test_ranking_policy.py tests/test_erdos_searcher.py -q`

Expected: new solve-lane tests fail because current keys omit prize and literature tiers.

- [ ] **Step 3: Centralize transparent solve selection scores**

```python
def selection_fields(card: dict, *, base_score: float) -> dict:
    audit = card["probe_summary"]["literature_ranking"]
    adjustment = literature_adjustment(audit["features"])
    return {
        "selection_priority_tier": selection_priority_tier(card["metadata"]["prize_status"]),
        "literature_status_tier": literature_status_tier(audit["features"]),
        "base_acquisition_score": round(base_score, 6),
        "literature_adjustment": adjustment,
        "selection_score": round(base_score + adjustment, 6),
    }


def solve_sort_key(card: dict, *, base_score: float) -> tuple[int, int, float, int]:
    fields = selection_fields(card, base_score=base_score)
    return (
        fields["selection_priority_tier"],
        fields["literature_status_tier"],
        -fields["selection_score"],
        card["problem_number"],
    )
```

Use this key in direct, diversified winner selection, protected exploration, tractable frontier, high-value uncertain, and `posterior_ranking(cards, posterior_key, limit, reason, solve_oriented=True)`. For descriptive calls pass `solve_oriented=False` and retain the existing posterior/problem-number order.

Extract the current ranking-product dictionary construction from `build_searcher` into `build_ranking_products`. Give `ranking_record` a keyword-only `base_acquisition_score: float | None = None`; when omitted, use the selected posterior probability. Diversified rows pass their exact posterior/cost/uncertainty/diversity acquisition value; exploration rows pass their deterministic uncertainty-per-cost score. `build_searcher` merges the returned products with its top-level snapshot metadata.

- [ ] **Step 4: Emit complete literature/prize audit fields in every ranking row**

Extend `ranking_record` with:

```python
"prize": card["metadata"]["prize"],
"prize_status": card["metadata"]["prize_status"],
"selection_priority_tier": fields["selection_priority_tier"],
"literature_policy_version": LITERATURE_POLICY_VERSION,
"literature_coverage_status": literature_audit["coverage_status"],
"local_literature_artifact_hash": literature_audit["local_artifact_hash"],
"live_literature_artifact_hashes": literature_audit["live_artifact_hashes"],
"literature_features": literature_audit["features"],
"base_acquisition_score": fields["base_acquisition_score"],
"literature_adjustment": fields["literature_adjustment"],
"selection_score": fields["selection_score"],
"literature_coverage_gaps": literature_audit["coverage_gaps"],
```

Append a paid-policy explanation to `largest_risks` for paid records. Append supporting foothold/reuse snippets to `strongest_positive_signals`, and machinery/status snippets to `largest_risks`; cap each display list deterministically while full evidence remains in artifacts.

- [ ] **Step 5: Interleave allocation separately by prize tier**

```python
def _interleave_one_tier(exploitation: list[dict], exploration: list[dict],
                         *, exploit_per_explore: int) -> list[dict]:
    combined: list[dict] = []
    exploit_index = 0
    explore_index = 0
    while exploit_index < len(exploitation) or explore_index < len(exploration):
        for _ in range(exploit_per_explore):
            if exploit_index >= len(exploitation):
                break
            combined.append({
                **exploitation[exploit_index], "allocation_lane": "exploitation"
            })
            exploit_index += 1
        if explore_index < len(exploration):
            combined.append({
                **exploration[explore_index],
                "allocation_lane": "protected_exploration",
            })
            explore_index += 1
        if exploit_index >= len(exploitation) and explore_index < len(exploration):
            combined.extend(
                {**record, "allocation_lane": "protected_exploration"}
                for record in exploration[explore_index:]
            )
            break
    return combined


def interleave_allocation(exploitation: list[dict], exploration: list[dict],
                          *, exploit_per_explore: int = 4) -> list[dict]:
    combined: list[dict] = []
    for prize_status in ("unpaid", "paid"):
        tier_exploit = [row for row in exploitation if row["prize_status"] == prize_status]
        tier_explore = [row for row in exploration if row["prize_status"] == prize_status]
        combined.extend(_interleave_one_tier(
            tier_exploit, tier_explore, exploit_per_explore=exploit_per_explore
        ))
    for rank, record in enumerate(combined, 1):
        record["lane_rank"] = record["rank"]
        record["rank"] = rank
        record["allocation_rank"] = rank
    return combined
```

- [ ] **Step 6: Run ranking tests**

Run: `python -m pytest tests/test_ranking_policy.py tests/test_erdos_searcher.py -q`

Expected: all solve-oriented invariant, literature reorder, status tier, and descriptive-neutrality tests pass.

- [ ] **Step 7: Commit tiered ranking behavior**

```bash
git add ranking_policy.py erdos_searcher.py tests/test_ranking_policy.py tests/test_erdos_searcher.py
git commit -m "feat: rank unpaid problems before paid targets"
```

### Task 7: Validate Queue Boundaries and Artifact Schemas

**Files:**
- Modify: `problem_queue.py`
- Modify: `tests/test_problem_queue.py`
- Modify: `schemas/problem-card.schema.json`
- Modify: `schemas/ranking-card.schema.json`
- Modify: `tests/test_artifact_schemas.py`

**Interfaces:**
- Consumes: ranking rows from Task 6 and policy fields in allocation context.
- Produces: `_validate_allocation_prize_tiers(allocation: list[dict]) -> None`, `_validate_tiered_lane_cadence(allocation: list[dict], *, exploit_per_explore: int = 4) -> None`, and fail-closed `load_allocation_plan` validation for complete prize metadata, a single unpaid-to-paid boundary, contiguous ranks, and a restarted 4:1 cadence per tier.

- [ ] **Step 1: Extend queue fixtures and add invalid-boundary/cadence tests**

Add `prize`, `prize_status`, and `selection_priority_tier` to every `row()` returned by `make_ranking`, defaulting its existing rows to unpaid. Add `prize_policy_version`, `literature_policy_version`, `literature_model_version`, `literature_snapshot_sha256`, and `literature_live_shortlist_limit` to its allocation context before calculating `context_id`. Import `_validate_allocation_prize_tiers` and `_validate_tiered_lane_cadence` from `problem_queue`.

```python
def test_queue_rejects_paid_row_before_unpaid_row(self):
    rows = [
        {"problem_number": 1, "prize_status": "paid", "selection_priority_tier": 1},
        {"problem_number": 2, "prize_status": "unpaid", "selection_priority_tier": 0},
    ]
    with self.assertRaisesRegex(RuntimeError, "paid allocation row precedes unpaid row"):
        _validate_allocation_prize_tiers(rows)


def test_queue_rejects_unknown_prize_status(self):
    rows = [
        {"problem_number": 1, "prize_status": "unknown", "selection_priority_tier": 0}
    ]
    with self.assertRaisesRegex(RuntimeError, "unknown prize metadata"):
        _validate_allocation_prize_tiers(rows)


def test_queue_accepts_cadence_reset_at_paid_boundary(self):
    rows = []
    rank = 1
    for prize_status, tier in (("unpaid", 0), ("paid", 1)):
        for lane in (
            "exploitation", "exploitation", "exploitation", "exploitation",
            "protected_exploration",
        ):
            rows.append({
                "problem_number": rank, "rank": rank, "allocation_rank": rank,
                "allocation_lane": lane, "prize_status": prize_status,
                "selection_priority_tier": tier,
            })
            rank += 1
    _validate_allocation_prize_tiers(rows)
    _validate_tiered_lane_cadence(rows, exploit_per_explore=4)
```

- [ ] **Step 2: Run queue tests and confirm new invalid artifacts are accepted or fixtures fail**

Run: `python -m pytest tests/test_problem_queue.py -q`

Expected: new tests fail before the queue validator understands prize tiers.

- [ ] **Step 3: Validate tier boundary then validate cadence independently per tier**

```python
def _validate_allocation_prize_tiers(allocation: list[dict]) -> None:
    statuses = [row.get("prize_status") for row in allocation]
    if any(status not in {"unpaid", "paid"} for status in statuses):
        raise RuntimeError("allocation contains unknown prize metadata")
    if statuses != sorted(statuses, key={"unpaid": 0, "paid": 1}.__getitem__):
        raise RuntimeError("paid allocation row precedes unpaid row")
    for row in allocation:
        expected_tier = 0 if row["prize_status"] == "unpaid" else 1
        if row.get("selection_priority_tier") != expected_tier:
            raise RuntimeError("allocation selection priority tier mismatch")


def _validate_tiered_lane_cadence(
    allocation: list[dict], *, exploit_per_explore: int = 4,
) -> None:
    for prize_status in ("unpaid", "paid"):
        tier_rows = [
            row for row in allocation if row["prize_status"] == prize_status
        ]
        _validate_lane_cadence(
            tier_rows, exploit_per_explore=exploit_per_explore
        )


_validate_allocation_prize_tiers(allocation)
_validate_tiered_lane_cadence(allocation, exploit_per_explore=4)
```

Extract the existing global cadence check into `_validate_lane_cadence`; preserve its overlap, lane-rank, union, and contiguous-rank checks.

- [ ] **Step 4: Tighten problem-card and ranking-card schemas**

In `problem-card.schema.json`, replace unconstrained metadata with required `prize`, `prize_status`, and `ai_wiki` properties while allowing existing metadata keys. Require `probe_summary.literature_ranking` with coverage, artifact hashes, features, and gaps.

In `ranking-card.schema.json`, add the Task 6 audit fields to `required`, constrain `prize_status` to `unpaid|paid`, constrain `selection_priority_tier` to `0|1`, feature values to `[0,1]`, and artifact hashes to 64 lowercase hex characters. Add `additionalProperties: false` only if every current optional ranking field is first represented in `properties`; otherwise keep the current extensible top level and enforce the newly required fields.

- [ ] **Step 5: Run queue and schema suites**

Run: `python -m pytest tests/test_problem_queue.py tests/test_artifact_schemas.py tests/test_erdos_searcher.py -q`

Expected: all tests pass and malformed tier boundaries fail closed.

- [ ] **Step 6: Commit queue/schema validation**

```bash
git add problem_queue.py tests/test_problem_queue.py schemas/problem-card.schema.json schemas/ranking-card.schema.json tests/test_artifact_schemas.py
git commit -m "feat: validate prize-tier allocation artifacts"
```

### Task 8: Refresh Official Catalog and Verify the Pipeline Without Touching Shared Triage

**Files:**
- Modify: `problem_catalog.json`
- Verify only: all files changed in Tasks 1-7

**Interfaces:**
- Consumes: official Erdős YAML and the existing complete canonical snapshot under `triage/ingestion/` or `triage/snapshots/`.
- Produces: refreshed first-party catalog and a temporary cached/offline ranking proving the unpaid-first invariant.

- [ ] **Step 1: Run all focused tests from the implementation**

Run:

```bash
python -m pytest \
  tests/test_ranking_policy.py \
  tests/test_problem_catalog.py \
  tests/test_literature_research.py \
  tests/test_ranking_literature.py \
  egmra/tests/test_scholarly.py \
  tests/test_erdos_searcher.py \
  tests/test_problem_queue.py \
  tests/test_artifact_schemas.py -q
```

Expected: all focused tests pass.

- [ ] **Step 2: Run the complete repository test suite**

Run: `python -m pytest -q`

Expected: all tests pass. If a failure is in one of the pre-existing dirty campaign/status-site files, record its exact test and traceback, verify it also fails with only those user changes present, and do not alter or revert those files.

- [ ] **Step 3: Refresh the catalog from official first-party data**

Run: `python sync_problem_catalog.py --output problem_catalog.json`

Expected: command prints a successful catalog write; `problem_catalog.json` contains `prize` and `prize_status` for every problem and `counts.unknown_prize == 0` for the current official dataset. If upstream currently contains an unknown prize, leave it unknown and expect allocation to be withheld.

- [ ] **Step 4: Commit only the catalog refresh**

```bash
git add problem_catalog.json
git commit -m "data: refresh erdos prize metadata"
```

- [ ] **Step 5: Build into a temporary output root in offline/cache-only mode**

Find the latest complete canonical snapshot without changing the shared tree:

```bash
CANONICAL=$(find triage/ingestion -name manifest.json -type f -print 2>/dev/null \
  | xargs -n1 dirname | sort | tail -1)
TMP_TRIAGE=$(mktemp -d /tmp/erdos-ranking-XXXXXX)
python erdos_searcher.py build \
  --root . \
  --output "$TMP_TRIAGE" \
  --snapshot-date 2026-07-16 \
  --top-k 75 \
  --offline-literature
```

If the CLI cannot discover the canonical snapshot from a temporary output root, invoke `build_searcher` from a short read-only Python command with `canonical_snapshot=Path("$CANONICAL")`. Do not copy results into `triage/`.

Expected: the build completes, reports zero unknown eligible prize records, and performs no network requests. Live coverage may be `local_only` because no compatible cache exists in the temporary root.

- [ ] **Step 6: Prove the invariant from the temporary ranking artifact**

Run:

```bash
python - "$TMP_TRIAGE/rankings/current.json" <<'PY'
import json
import sys

ranking = json.load(open(sys.argv[1], encoding="utf-8"))
solve_lanes = (
    "direct_solve_probability", "diversified_attack_queue", "allocation_queue",
    "highest_probability_verified_novel_solution",
    "highest_probability_verified_partial_progress",
    "highest_probability_lean_verification", "best_finite_computation_targets",
    "tractable_frontier", "highest_value_uncertain_problems", "protected_exploration",
)
order = {"unpaid": 0, "paid": 1}
for lane in solve_lanes:
    statuses = [row["prize_status"] for row in ranking[lane]]
    assert statuses == sorted(statuses, key=order.__getitem__), lane
assert not ranking["unknown_prize_problem_numbers"]
print({lane: [row["problem_number"] for row in ranking[lane][:5]] for lane in solve_lanes})
PY
```

Expected: the script prints the leading problem numbers and exits 0.

- [ ] **Step 7: Run an explicit live-refresh smoke test only when credentials/network policy permit**

Run against a fresh temporary output root with a supplied canonical snapshot:

```bash
python erdos_searcher.py build \
  --root . \
  --output "$TMP_TRIAGE" \
  --snapshot-date 2026-07-16 \
  --top-k 5 \
  --refresh-literature
```

Expected: no more than 10 deterministic queries are issued, artifacts appear only under `$TMP_TRIAGE/literature/ranking/<source_snapshot_id>/`, and outages are reported as partial/local-only coverage without changing mathematical posteriors. This smoke test is not a release gate because external availability is unstable.

- [ ] **Step 8: Inspect final scope and record verification evidence**

Run:

```bash
git status --short
git diff --stat HEAD~8..HEAD
git log --oneline -9
```

Expected: implementation commits contain only the files named in this plan plus `problem_catalog.json`; the pre-existing dirty campaign, status-site, and shared `triage/` changes remain unstaged and untouched.

---

## Self-Review Checklist

- Prize preservation, three-state classification, raw-value auditability, unknown fail-closed behavior, and catalog counts are covered by Tasks 1 and 5.
- One reusable local index, supporting snippets, source hashes, and compatibility wrapper are covered by Task 2.
- All four sources, five-result cap, outage coverage, two-query cap, top-50 unpaid shortlist, immutable exact cache, and offline/refresh modes are covered by Tasks 3-5.
- Exact feature names, `[0,1]` bounds, exact fixed weights, status tier, and coverage-gap semantics are covered by Tasks 4 and 6.
- All ten solve-oriented products and all four prize-neutral descriptive products have explicit regression coverage in Task 6.
- Allocation phase reset and consumer-side validation are covered by Task 7.
- Ranking rows, top-level snapshot, policy hashes, schemas, and pipeline fingerprint binding are covered by Tasks 4-7.
- Focused tests, full tests, official catalog refresh, temporary real build, invariant inspection, optional live smoke, and dirty-worktree protection are covered by Task 8.
- No task changes proof, Lean, Aristotle, verification, promotion, or source-authoritative status gates.
