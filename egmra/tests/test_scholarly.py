"""Tests for production scholarly retrieval (arXiv + Crossref, audit #7).

Live network I/O is confined to the injectable fetcher (verified live, never in
CI); here canned API payloads exercise parsing, provenance, the trust boundary
(retrieved papers are never a proof), dedup/outage handling, and the fetcher's
host allowlist.
"""

from __future__ import annotations

import pytest

from egmra.retrieval.scholarly import (
    ScholarlyRetrievalError,
    UrllibFetcher,
    build_scholarly_corpus,
    parse_arxiv_atom,
    parse_crossref_json,
)

_ARXIV_XML = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <id>http://arxiv.org/abs/2401.00001v1</id>
    <published>2024-01-01T00:00:00Z</published>
    <title>On prime gaps</title>
    <summary>We study gaps between consecutive primes.</summary>
    <author><name>Ada Lovelace</name></author>
  </entry>
</feed>"""

_CROSSREF_JSON = (
    '{"message": {"items": [{"DOI": "10.1000/xyz", '
    '"title": ["A theorem on primes"], '
    '"abstract": "<jats:p>We prove a bound.</jats:p>", '
    '"author": [{"given": "Carl", "family": "Gauss"}], '
    '"URL": "https://doi.org/10.1000/xyz", '
    '"issued": {"date-parts": [[2020, 5]]}}]}}'
)


def test_parse_arxiv_atom_yields_auditable_unproven_records():
    records = parse_arxiv_atom(_ARXIV_XML, retrieved_at="2026-07-14T00:00:00Z")
    assert len(records) == 1
    record = records[0]
    assert record.theorem_id == "arxiv:2401.00001v1"
    assert record.source_uri == "http://arxiv.org/abs/2401.00001v1"
    assert record.canonical_statement == "On prime gaps"
    assert "consecutive primes" in record.verbatim_theorem_and_hypothesis_extract
    assert record.authors == ("Ada Lovelace",)
    assert record.is_auditable()
    # Trust boundary: a paper is never a proof.
    assert record.proof_status == "unknown"
    assert record.independent_verification_status == "unverified"


def test_parse_arxiv_atom_rejects_dtd_entities():
    with pytest.raises(ScholarlyRetrievalError):
        parse_arxiv_atom('<!DOCTYPE feed [<!ENTITY x "y">]><feed/>')


def test_parse_crossref_json_strips_jats_and_is_auditable():
    records = parse_crossref_json(_CROSSREF_JSON)
    assert len(records) == 1
    record = records[0]
    assert record.theorem_id == "doi:10.1000/xyz"
    assert record.source_uri == "https://doi.org/10.1000/xyz"
    assert record.source_version == "2020-5"
    assert record.authors == ("Carl Gauss",)
    assert "We prove a bound." in record.verbatim_theorem_and_hypothesis_extract
    assert "<jats:p>" not in record.verbatim_theorem_and_hypothesis_extract
    assert record.is_auditable() and record.proof_status == "unknown"


def test_parse_crossref_json_rejects_non_json():
    with pytest.raises(ScholarlyRetrievalError):
        parse_crossref_json("not json")


def test_build_scholarly_corpus_merges_sources_and_dedups():
    def fetcher(url: str) -> str:
        if "export.arxiv.org" in url:
            return _ARXIV_XML
        if "api.crossref.org" in url:
            return _CROSSREF_JSON
        raise AssertionError(f"unexpected url: {url}")

    records = build_scholarly_corpus("prime gaps", fetcher=fetcher, limit=5)
    assert {r.theorem_id for r in records} == {"arxiv:2401.00001v1", "doi:10.1000/xyz"}
    assert all(r.is_auditable() and r.proof_status == "unknown" for r in records)


def test_build_scholarly_corpus_skips_a_source_outage():
    def flaky(url: str) -> str:
        if "arxiv" in url:
            raise ScholarlyRetrievalError("arxiv down")
        return _CROSSREF_JSON

    records = build_scholarly_corpus("q", fetcher=flaky, sources=("arxiv", "crossref"))
    assert [r.theorem_id for r in records] == ["doi:10.1000/xyz"]  # crossref still contributes


def test_build_scholarly_corpus_empty_query_returns_empty():
    assert build_scholarly_corpus("   ", fetcher=lambda url: _ARXIV_XML) == []


def test_urllib_fetcher_refuses_non_allowlisted_urls():
    fetcher = UrllibFetcher()
    with pytest.raises(ScholarlyRetrievalError):
        fetcher("https://evil.example.com/x")  # host not allowlisted
    with pytest.raises(ScholarlyRetrievalError):
        fetcher("file:///etc/passwd")  # scheme not allowed
