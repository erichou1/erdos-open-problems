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
    assert pi.problem_id.startswith("adhoc-")
    assert pi.status_claims == ()
    assert pi.metadata["input_kind"] == "statement"


def test_inline_problem_identity_is_content_bound_not_global():
    first = from_statement("For all n, n^2 >= 0.")
    repeated = from_statement("For all n, n^2 >= 0.")
    different = from_statement("For all n, n^2 >= 1.")

    assert first.problem_id == repeated.problem_id
    assert first.problem_id != different.problem_id
    assert first.source_id != different.source_id


def test_from_statement_rejects_empty():
    with pytest.raises(SourceResolutionError):
        from_statement("   \n  ")


def test_from_statement_file_reads_and_ids(tmp_path):
    path = tmp_path / "goldbach.txt"
    path.write_text("Every even integer > 2 is a sum of two primes.", encoding="utf-8")
    pi = from_statement_file(path)
    assert pi.display_statement.startswith("Every even integer")
    assert pi.problem_id.startswith("file-goldbach-")
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


def test_monolithic_horizontal_rule_is_an_auditable_statement_boundary(
        tmp_path):
    tex = tmp_path / "corpus.tex"
    tex.write_text(r"""\section{Problem \#1}
\noindent\textbf{Statement:}

Is $A$ true?

\noindent\rule{\linewidth}{0.4pt}

\section{Problem \#2}
\noindent\textbf{Statement:}

Is $B$ true?

\noindent\rule{\linewidth}{0.4pt}
""", encoding="utf-8")
    catalog = tmp_path / "catalog.json"
    catalog.write_text(json.dumps({"problems": {}}), encoding="utf-8")

    first = from_erdos_number(1, corpus_tex_path=tex, catalog_path=catalog)
    second = from_erdos_number(2, corpus_tex_path=tex, catalog_path=catalog)

    assert first.display_statement == "Is $A$ true?"
    assert second.display_statement == "Is $B$ true?"


def test_from_erdos_number_missing_section_raises(corpus):
    tex, catalog = corpus
    with pytest.raises(SourceResolutionError, match="no section"):
        from_erdos_number(999, corpus_tex_path=tex, catalog_path=catalog)


# --- T2 lane: supplemental corpus fallback + machine-status mapping -------------

_SUPPLEMENT_TEX = r"""% corpus_supplement: Erdős problem #742
% source: https://www.erdosproblems.com/latex/742
% fetched_at: 2026-07-14T00:00:00Z
% payload_sha256: 0000000000000000000000000000000000000000000000000000000000000000
% verbatim upstream payload follows — do not edit
\documentclass{article}
\begin{document}
\noindent\textbf{Status:} DECIDABLE

\noindent\textbf{Problem Statement:}

Is the finite quantity $Q(742)$ equal to $5$?

\bigskip
\noindent\small{Source: \url{https://www.erdosproblems.com/742}}
\end{document}
"""


def test_from_erdos_number_falls_back_to_supplement(corpus, tmp_path):
    tex, catalog = corpus
    supplement = tmp_path / "supplement"
    supplement.mkdir()
    (supplement / "problem_742.tex").write_text(_SUPPLEMENT_TEX, encoding="utf-8")
    catalog_doc = json.loads(catalog.read_text(encoding="utf-8"))
    catalog_doc["problems"]["742"] = {
        "problem": 742, "source_state": "decidable",
        "source_problem_url": "https://www.erdosproblems.com/742",
        "source_last_update": "2026-07-01", "tags": ["graph theory"],
    }
    catalog.write_text(json.dumps(catalog_doc), encoding="utf-8")

    pi = from_erdos_number(742, corpus_tex_path=tex, catalog_path=catalog,
                           supplement_dir=supplement)
    assert pi.problem_id == "erdos-742"
    assert pi.display_statement == "Is the finite quantity $Q(742)$ equal to $5$?"
    assert pi.metadata["statement_source"] == "corpus_supplement"
    # Machine-status states are honestly open (upstream: "appear to be open,
    # but ...") — they must not block the campaign as status_uncertain.
    assert pi.status_claims[0].status == "open"


def test_supplement_missing_mentions_fetch_tool(corpus, tmp_path):
    tex, catalog = corpus
    with pytest.raises(SourceResolutionError, match="fetch_corpus_supplement"):
        from_erdos_number(742, corpus_tex_path=tex, catalog_path=catalog,
                          supplement_dir=tmp_path / "empty")


def test_supplement_symlink_rejected(corpus, tmp_path):
    tex, catalog = corpus
    supplement = tmp_path / "supplement"
    supplement.mkdir()
    real = tmp_path / "real.tex"
    real.write_text(_SUPPLEMENT_TEX, encoding="utf-8")
    (supplement / "problem_742.tex").symlink_to(real)
    with pytest.raises(SourceResolutionError):
        from_erdos_number(742, corpus_tex_path=tex, catalog_path=catalog,
                          supplement_dir=supplement)


def test_corpus_snapshot_still_preferred_over_supplement(corpus, tmp_path):
    # A problem present in the snapshot must never silently resolve from a
    # supplement file (snapshot is the pinned source of record).
    tex, catalog = corpus
    supplement = tmp_path / "supplement"
    supplement.mkdir()
    (supplement / "problem_7.tex").write_text(
        _SUPPLEMENT_TEX.replace("742", "7").replace(
            "Is the finite quantity $Q(7)$ equal to $5$?", "WRONG STATEMENT"),
        encoding="utf-8")
    pi = from_erdos_number(7, corpus_tex_path=tex, catalog_path=catalog,
                           supplement_dir=supplement)
    assert pi.metadata["statement_source"] == "corpus_snapshot"
    assert "property $P$" in pi.display_statement


@pytest.mark.parametrize("state", ["decidable", "falsifiable", "verifiable"])
def test_machine_status_states_map_to_open(state, corpus):
    from egmra.corpus.sources import _status_claim_from_entry

    claims = _status_claim_from_entry(5, {"source_state": state})
    assert claims[0].status == "open"


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


@pytest.mark.parametrize("number", [1137, 1139, 361, 468, 598, 911, 943])
def test_bundled_corpus_resolves_sections_ending_at_generated_rule(number):
    pi = from_erdos_number(number)
    assert pi.problem_id == f"erdos-{number}"
    assert pi.display_statement
    assert "\\noindent\\rule" not in pi.display_statement
