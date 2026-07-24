"""Tests for the Erdős retrieval-corpus builder (task 4.4)."""

from __future__ import annotations

import pytest

from egmra.corpus.sources import default_catalog_path, default_corpus_tex_path
from egmra.retrieval.erdos_corpus import build_erdos_corpus

_SECTION_TEMPLATE = (
    "\\section{{Problem \\#{n}}}\n\n"
    "\\noindent \\textbf{{Problem Statement:}}\n"
    "{statement}\n\n"
    "\\bigskip\n"
    "\\noindent \\small{{Source: https://www.erdosproblems.com/{n}}}\n\n"
)


def _write_corpus(path, sections):
    body = "".join(
        _SECTION_TEMPLATE.format(n=n, statement=s) for n, s in sections
    )
    path.write_text(body, encoding="utf-8")
    return path


def test_builds_auditable_records_with_real_provenance(tmp_path):
    tex = _write_corpus(tmp_path / "corpus.tex", [
        (7, "For every prime p there exists a larger prime q."),
        (42, "Every even integer greater than two is a sum of two primes."),
    ])
    records = build_erdos_corpus(tex)
    assert [r.theorem_id for r in records] == ["erdos-7", "erdos-42"]
    first = records[0]
    assert first.source_uri == "https://www.erdosproblems.com/7"
    assert first.canonical_statement.startswith("For every prime p")
    assert first.verbatim_theorem_and_hypothesis_extract == first.canonical_statement
    assert len(first.source_content_hash) == 64
    assert first.is_auditable()


def test_deduplicates_repeated_problem_numbers(tmp_path):
    tex = _write_corpus(tmp_path / "corpus.tex", [
        (7, "First occurrence of problem seven."),
        (7, "Duplicate occurrence that must be dropped."),
        (8, "Problem eight statement."),
    ])
    records = build_erdos_corpus(tex)
    ids = [r.theorem_id for r in records]
    assert ids == ["erdos-7", "erdos-8"]
    assert records[0].canonical_statement.startswith("First occurrence")


def test_limit_bounds_the_number_of_records(tmp_path):
    tex = _write_corpus(tmp_path / "corpus.tex", [
        (1, "One."), (2, "Two."), (3, "Three."),
    ])
    assert len(build_erdos_corpus(tex, limit=2)) == 2


def test_catalog_metadata_enriches_records(tmp_path):
    import json

    tex = _write_corpus(tmp_path / "corpus.tex", [(9, "Statement nine.")])
    catalog = tmp_path / "catalog.json"
    catalog.write_text(json.dumps({"problems": {"9": {
        "source_problem_url": "https://www.erdosproblems.com/9",
        "source_state": "open",
        "source_last_update": "2026-01-01",
        "tags": ["number-theory"],
    }}}), encoding="utf-8")
    record = build_erdos_corpus(tex, catalog)[0]
    assert record.proof_status == "open"
    assert record.source_version == "2026-01-01"
    assert "number-theory" in record.authors


def test_rejects_symlinked_corpus(tmp_path):
    real = _write_corpus(tmp_path / "corpus.tex", [(1, "One.")])
    link = tmp_path / "link.tex"
    link.symlink_to(real)
    with pytest.raises(ValueError):
        build_erdos_corpus(link)


def test_unique_ids_have_no_duplicate_for_retrieval_service(tmp_path):
    # The retrieval service rejects duplicate theorem ids; the builder must never
    # emit them even if the corpus repeats a number.
    tex = _write_corpus(tmp_path / "corpus.tex", [(5, "Five."), (5, "Five again.")])
    ids = [r.theorem_id for r in build_erdos_corpus(tex)]
    assert len(ids) == len(set(ids))


def test_packaged_corpus_builds_many_auditable_records():
    records = build_erdos_corpus(default_corpus_tex_path(), default_catalog_path())
    assert len(records) > 100
    ids = [r.theorem_id for r in records]
    assert len(ids) == len(set(ids))
    assert all(r.is_auditable() for r in records)
