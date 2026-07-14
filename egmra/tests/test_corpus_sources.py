"""Tests for arbitrary-problem source resolution."""

from __future__ import annotations

import json

import pytest

from egmra.corpus import sources
from egmra.corpus.sources import (
    ProblemInput,
    SourceResolutionError,
    from_erdos_number,
    from_statement,
    from_statement_file,
)

_CORPUS_TEX = r"""\documentclass{article}
\begin{document}
%% ============================================================
\section{Problem \#7}
\label{prob:7}

\noindent\textbf{Statement:}

Does every sufficiently large integer have property $P$?

\bigskip
\noindent\textbf{Remarks:}
Some remark that is not the statement.
%% ============================================================
\section{Problem \#42}
\label{prob:42}

\noindent\textbf{Statement:}

Prove that $f(n) \gg n$ for all $n$.

\end{document}
"""

_CATALOG = {
    "problems": {
        "7": {
            "problem": 7, "source_state": "open",
            "source_problem_url": "https://www.erdosproblems.com/7",
            "source_last_update": "2025-01-01", "tags": ["number theory"],
            "formalized": {"state": "no"},
        },
        "42": {"problem": 42, "source_state": "solved",
               "source_problem_url": "https://www.erdosproblems.com/42",
               "source_last_update": "2024-06-01", "tags": []},
    }
}


@pytest.fixture()
def corpus(tmp_path):
    tex = tmp_path / "corpus.tex"
    tex.write_text(_CORPUS_TEX, encoding="utf-8")
    catalog = tmp_path / "catalog.json"
    catalog.write_text(json.dumps(_CATALOG), encoding="utf-8")
    return tex, catalog


def test_from_statement_freezes_bytes():
    pi = from_statement("For all n, n^2 >= 0.")
    assert isinstance(pi, ProblemInput)
    assert pi.source_bytes == b"For all n, n^2 >= 0."
    assert pi.problem_id == "adhoc-problem"
    assert pi.status_claims == ()
    assert pi.metadata["input_kind"] == "statement"


def test_from_statement_rejects_empty():
    with pytest.raises(SourceResolutionError):
        from_statement("   \n  ")


def test_from_statement_file_reads_and_ids(tmp_path):
    path = tmp_path / "goldbach.txt"
    path.write_text("Every even integer > 2 is a sum of two primes.", encoding="utf-8")
    pi = from_statement_file(path)
    assert pi.display_statement.startswith("Every even integer")
    assert pi.problem_id == "file-goldbach"
    assert pi.source_id.startswith("file://")


def test_from_statement_file_rejects_symlink(tmp_path):
    target = tmp_path / "real.txt"
    target.write_text("statement", encoding="utf-8")
    link = tmp_path / "link.txt"
    link.symlink_to(target)
    with pytest.raises(SourceResolutionError):
        from_statement_file(link)


def test_from_statement_file_rejects_oversized(tmp_path, monkeypatch):
    path = tmp_path / "big.txt"
    path.write_text("x" * 50, encoding="utf-8")
    monkeypatch.setattr(sources, "_MAX_STATEMENT_BYTES", 10)
    with pytest.raises(SourceResolutionError):
        from_statement_file(path)


def test_from_erdos_number_extracts_exact_statement(corpus):
    tex, catalog = corpus
    pi = from_erdos_number(7, corpus_tex_path=tex, catalog_path=catalog)
    assert pi.problem_id == "erdos-7"
    assert pi.display_statement == "Does every sufficiently large integer have property $P$?"
    assert pi.source_id == "https://www.erdosproblems.com/7"
    assert pi.metadata["tags"] == ["number theory"]
    assert len(pi.status_claims) == 1
    claim = pi.status_claims[0]
    assert claim.status == "open"
    assert claim.review_date == "2025-01-01"
    assert claim.source == "https://www.erdosproblems.com/7"


def test_from_erdos_number_maps_solved_to_known(corpus):
    tex, catalog = corpus
    pi = from_erdos_number(42, corpus_tex_path=tex, catalog_path=catalog)
    assert pi.status_claims[0].status == "known"
    assert pi.display_statement == r"Prove that $f(n) \gg n$ for all $n$."


def test_from_erdos_number_boundary_does_not_confuse_prefixes(corpus):
    # Problem #7 must not match \#42, and vice versa.
    tex, catalog = corpus
    seven = from_erdos_number(7, corpus_tex_path=tex, catalog_path=catalog)
    assert "property $P$" in seven.display_statement
    assert "f(n)" not in seven.display_statement


def test_from_erdos_number_missing_section_raises(corpus):
    tex, catalog = corpus
    with pytest.raises(SourceResolutionError, match="no section"):
        from_erdos_number(999, corpus_tex_path=tex, catalog_path=catalog)


@pytest.mark.parametrize("bad", [0, -3, True])
def test_from_erdos_number_rejects_non_positive(bad, corpus):
    tex, catalog = corpus
    with pytest.raises(SourceResolutionError):
        from_erdos_number(bad, corpus_tex_path=tex, catalog_path=catalog)


def test_from_erdos_number_without_catalog_still_extracts(corpus, tmp_path):
    tex, _ = corpus
    missing = tmp_path / "does-not-exist.json"
    pi = from_erdos_number(7, corpus_tex_path=tex, catalog_path=missing)
    assert pi.display_statement.startswith("Does every")
    assert pi.status_claims == ()  # no catalog -> no dated status claim


def test_bundled_corpus_defaults_resolve_a_real_problem():
    # The repository snapshot ships all_open_problems.tex + problem_catalog.json.
    pi = from_erdos_number(312)
    assert pi.problem_id == "erdos-312"
    assert pi.display_statement
    assert pi.status_claims and pi.status_claims[0].status == "open"
