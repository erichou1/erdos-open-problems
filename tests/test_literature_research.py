import json
import tempfile
import unittest
from unittest import mock
from pathlib import Path

import literature_research as L


def _tex(body: str) -> str:
    return (
        "\\documentclass{article}\n\\begin{document}\n\\maketitle\n"
        "\\noindent\\textbf{Status:} OPEN\n\n" + body + "\n\\end{document}\n"
    )


def make_corpus(root: Path) -> None:
    individual = root / "individual"
    individual.mkdir(parents=True)
    (individual / "problem_1.tex").write_text(_tex(
        "Determine the chromatic number of a graph $G$. Is $\\chi(G)\\leq k$? "
        "This is related to Ramsey theory \\cite{A} and \\cite{B}."), encoding="utf-8")
    (individual / "problem_2.tex").write_text(_tex(
        "Estimate the chromatic number of a graph. Alon \\cite{A} proved "
        "$\\chi(G)\\geq k$. This bounds graph colouring."), encoding="utf-8")
    (individual / "problem_3.tex").write_text(_tex(
        "A graph colouring question about independent sets and the chromatic "
        "number of sparse graphs."), encoding="utf-8")
    (individual / "problem_4.tex").write_text(_tex(
        "Compute a measure integral in real analysis \\cite{Z}."), encoding="utf-8")
    (root / "problem_catalog.json").write_text(json.dumps({
        "problems": {
            "1": {"tags": ["combinatorics", "graphs"]},
            "2": {"tags": ["combinatorics", "graphs"]},
            "3": {"tags": ["graphs"]},
            "4": {"tags": ["analysis"]},
        }
    }), encoding="utf-8")


class LiteratureResearchTests(unittest.TestCase):
    def test_index_loads_corpus_once_and_serves_multiple_queries(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            make_corpus(root)
            original = L._corpus_texts
            calls = 0

            def counted(path):
                nonlocal calls
                calls += 1
                return original(path)

            with mock.patch.object(L, "_corpus_texts", side_effect=counted):
                index = L.LiteratureIndex(root)
                first = index.research(1)
                second = index.research(2)
            self.assertEqual(calls, 1)
            self.assertTrue(first.related)
            self.assertTrue(second.related)

    def test_index_records_stable_local_source_hashes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            make_corpus(root)
            first = L.LiteratureIndex(root)
            second = L.LiteratureIndex(root)
            self.assertEqual(first.source_hashes(1), second.source_hashes(1))
            self.assertTrue(first.source_hashes(1))
            self.assertTrue(all(len(value) == 64 for value in first.source_hashes(1)))

    def test_index_uses_open_corpus_when_root_has_no_individual_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            make_corpus(root / "open")
            (root / "problem_catalog.json").write_text(
                (root / "open" / "problem_catalog.json").read_text()
            )
            (root / "open" / "problem_catalog.json").unlink()
            context = L.LiteratureIndex(root).research(1)
            self.assertTrue(context.related)

    def test_finds_related_and_excludes_unrelated(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            make_corpus(root)
            ctx = L.research_literature(root, 1)
            numbers = [r.number for r in ctx.related]
            self.assertIn(2, numbers)   # shared tags + shared cite A + terms
            self.assertIn(3, numbers)   # shared tag + terms
            self.assertNotIn(4, numbers)  # analysis, no overlap
            self.assertNotIn(1, numbers)  # never itself

    def test_extracts_references_and_results(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            make_corpus(root)
            ctx = L.research_literature(root, 1)
            self.assertIn("A", ctx.references)
            related_2 = next(r for r in ctx.related if r.number == 2)
            self.assertTrue(any("Alon" in s for s in related_2.results))

    def test_rendered_is_marked_untrusted(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            make_corpus(root)
            ctx = L.research_literature(root, 1)
            self.assertIn("UNTRUSTED", ctx.rendered)
            self.assertIn("#2", ctx.rendered)
            record = ctx.grounding_record()
            self.assertTrue(record["enabled"])
            self.assertTrue(record["rediscovery_eligible"])
            self.assertEqual(record["source"], "local_corpus")
            self.assertIn(2, record["related_problems"])

    def test_missing_problem_yields_empty_context(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            make_corpus(root)
            ctx = L.research_literature(root, 999)
            self.assertTrue(ctx.is_empty())
            self.assertEqual(ctx.rendered, "")
            self.assertFalse(ctx.grounding_record()["enabled"])

    def test_citation_parsing(self):
        self.assertEqual(L.citations("x \\cite{A, B} y \\cite{C}"), {"A", "B", "C"})


if __name__ == "__main__":
    unittest.main()
