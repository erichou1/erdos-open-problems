import json
from pathlib import Path

import pytest

from literature_research import LiteratureIndex
from ranking_literature import (
    LIVE_SHORTLIST_LIMIT,
    artifact_content_sha256,
    build_local_enrichments,
    build_queries,
    enrich_live_shortlist,
    literature_adjustment,
    select_live_shortlist,
)


def _tex(body: str) -> str:
    return "\\documentclass{article}\n\\begin{document}\n" + body + "\n\\end{document}\n"


def make_index(root: Path) -> LiteratureIndex:
    individual = root / "individual"
    individual.mkdir(parents=True)
    (individual / "problem_1.tex").write_text(_tex(
        "Determine a graph bound. A special case is proved by a reusable reduction \\cite{A}."
    ))
    (individual / "problem_2.tex").write_text(_tex(
        "A related graph theorem gives an upper bound by the same method \\cite{A}."
    ))
    (root / "problem_catalog.json").write_text(json.dumps({
        "problems": {
            "1": {"tags": ["graphs"]},
            "2": {"tags": ["graphs"]},
        }
    }))
    return LiteratureIndex(root)


def make_card(number: int = 1, *, prize_status: str = "unpaid") -> dict:
    return {
        "problem_number": number,
        "statement": {
            "normalized": f"Determine the graph bound in problem {number}",
            "statement_sha256": f"{number:064x}",
        },
        "metadata": {
            "prize": "no" if prize_status == "unpaid" else "$500",
            "prize_status": prize_status,
            "tags": ["graphs"],
            "ai_wiki": {},
            "source_sections": {"remarks": "A partial special case is known.", "references": "A"},
        },
        "probe_summary": {
            "literature": {"comment_count": 2, "matched_claim_snippets": []}
        },
    }


def empty_fetcher(url: str) -> str:
    if "export.arxiv.org" in url:
        return '<feed xmlns="http://www.w3.org/2005/Atom"></feed>'
    if "api.crossref.org" in url:
        return '{"message":{"items":[]}}'
    if "api.semanticscholar.org" in url:
        return '{"data":[]}'
    if "api.stackexchange.com" in url:
        return '{"items":[]}'
    raise AssertionError(url)


def duplicate_fetcher(url: str) -> str:
    if "export.arxiv.org" in url:
        return """<feed xmlns="http://www.w3.org/2005/Atom"><entry>
        <id>http://arxiv.org/abs/2401.00001v1</id>
        <published>2024-01-01T00:00:00Z</published>
        <title>A partial graph bound</title>
        <summary>We prove a special case and an upper bound.</summary>
        <author><name>Ada</name></author></entry></feed>"""
    return empty_fetcher(url)


def test_queries_are_deterministic_and_capped_at_two(tmp_path):
    index = make_index(tmp_path)
    card = make_card()
    context = index.research(1)
    first = build_queries(card, context)
    second = build_queries(card, context)
    assert first == second
    assert 1 <= len(first) <= 2
    assert all(len(query.query_hash) == 64 for query in first)


def test_adjustment_uses_exact_bounded_weights():
    features = {
        "foothold": 0.75,
        "reuse": 0.5,
        "machinery_risk": 0.25,
        "status_risk": 0.0,
    }
    assert literature_adjustment(features) == pytest.approx(0.015)


def test_local_partial_result_and_method_are_auditable_features(tmp_path):
    index = make_index(tmp_path)
    enrichment = build_local_enrichments([make_card()], index)[1]
    assert enrichment.features["foothold"] > 0
    assert enrichment.features["reuse"] > 0
    assert enrichment.features["components"]["partial_result_snippets"]
    assert enrichment.local_artifact_hash
    assert enrichment.coverage_status == "local_only"


def test_live_shortlist_is_first_fifty_unpaid():
    cards = [make_card(number, prize_status="paid") for number in range(100, 105)]
    cards += [make_card(number) for number in range(1, 56)]
    shortlist = select_live_shortlist(cards)
    assert shortlist == tuple(range(1, LIVE_SHORTLIST_LIMIT + 1))


def test_cache_reuse_requires_exact_statement_source_query_and_policy(tmp_path):
    corpus = tmp_path / "corpus"
    index = make_index(corpus)
    card = make_card()
    local = build_local_enrichments([card], index)
    cache = tmp_path / "cache"
    first = enrich_live_shortlist(
        {1: card}, local, shortlist_problem_numbers=(1,), cache_root=cache,
        source_snapshot_id="snapshot-a", refresh=True, offline=False,
        fetcher=empty_fetcher,
    )[1]
    second = enrich_live_shortlist(
        {1: card}, local, shortlist_problem_numbers=(1,), cache_root=cache,
        source_snapshot_id="snapshot-a", refresh=False, offline=True,
    )[1]
    changed = {
        **card,
        "statement": {**card["statement"], "statement_sha256": "f" * 64},
    }
    invalidated = enrich_live_shortlist(
        {1: changed}, local, shortlist_problem_numbers=(1,), cache_root=cache,
        source_snapshot_id="snapshot-a", refresh=False, offline=True,
    )[1]
    assert first.live_artifact_hashes
    assert len(first.live_artifact_hashes) == len(build_queries(card, index.research(1))) == 2
    assert second.live_artifact_hashes == first.live_artifact_hashes
    assert invalidated.live_artifact_hashes == ()
    for path in cache.rglob("*.json"):
        payload = json.loads(path.read_text())
        assert payload["artifact_content_sha256"] == artifact_content_sha256(payload)


def test_source_failure_is_a_coverage_gap_not_a_bonus(tmp_path):
    corpus = tmp_path / "corpus"
    index = make_index(corpus)
    card = make_card()
    local = build_local_enrichments([card], index)

    result = enrich_live_shortlist(
        {1: card}, local, shortlist_problem_numbers=(1,),
        cache_root=tmp_path / "cache", source_snapshot_id="snapshot-a",
        refresh=False, offline=True,
    )[1]
    assert result.features == local[1].features
    assert result.coverage_status == "local_only"
    assert result.live_artifact_hashes == ()


def test_duplicate_paper_across_queries_counts_once(tmp_path):
    corpus = tmp_path / "corpus"
    index = make_index(corpus)
    card = make_card()
    result = enrich_live_shortlist(
        {1: card}, build_local_enrichments([card], index),
        shortlist_problem_numbers=(1,), cache_root=tmp_path / "cache",
        source_snapshot_id="snapshot-a", refresh=True, offline=False,
        fetcher=duplicate_fetcher,
    )[1]
    live_matches = [
        item for item in result.features["components"]["partial_result_snippets"]
        if item["snippet"] == "A partial graph bound"
    ]
    partial_snippets = [
        item["snippet"]
        for item in result.features["components"]["partial_result_snippets"]
    ]
    assert len(partial_snippets) == len(set(partial_snippets))
    assert len(live_matches) == 1
