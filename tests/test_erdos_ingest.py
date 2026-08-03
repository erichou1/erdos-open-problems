import json
import os
import tempfile
import unittest
from pathlib import Path

import erdos_ingest
from erdos_ingest import CATALOG_URL, ingest_corpus
from erdos_common import extract_problem_statement


YAML_SOURCE = b'''- number: "1"
  prize: "$100"
  status:
    state: "open"
    last_update: "2026-07-12"
  formalized:
    state: "no"
  tags: ["number theory"]
- number: "2"
  prize: "no"
  status:
    state: "proved"
    last_update: "2026-07-12"
  tags: ["graph theory"]
'''

PAGE = b'''<html><body>
<div id="content" style="white-space: pre-line;">Is $2^n+1$ prime infinitely often?</div>
<div class="problem-additional-text">A bounded source remark.</div>
<div class="problem-additional-text"><h3>References</h3>[Er26] A reference.</div>
</body></html>'''

YAML_TWO_OPEN = b'''- number: "1"
  prize: "no"
  status:
    state: "open"
    last_update: "2026-07-12"
- number: "3"
  prize: "no"
  status:
    state: "open"
    last_update: "2026-07-12"
'''

PAGE_THREE = b'''<html><body>
<div id="content">Is $a&#60;b$ &amp; $b&#62;c$?</div>
<div class="problem-additional-text">A second remark.</div>
</body></html>'''
TEST_UPSTREAM_COMMIT = "a" * 40


class ErdosIngestTests(unittest.TestCase):
    def test_ingestion_schema_closes_v2_records_and_requires_exact_mirror_pair(self):
        schema_path = Path(__file__).resolve().parents[1] / "schemas" / "ingestion-manifest.schema.json"
        schema = json.loads(schema_path.read_text())
        self.assertEqual(schema["properties"]["schema_version"], {"const": 2})
        record_schema = schema["properties"]["records"]["items"]
        self.assertFalse(record_schema["additionalProperties"])
        destinations = record_schema["properties"]["applied_destinations"]
        self.assertEqual(destinations["minItems"], 2)
        self.assertEqual(destinations["maxItems"], 2)

    def test_reference_word_inside_remark_does_not_reclassify_it_as_bibliography(self):
        page = b'''<html><body>
<div id="content">A theorem?</div>
<div class="problem-additional-text">References in this remark are informal.</div>
<div class="problem-additional-text"><h3>References</h3>[X1] Formal.</div>
</body></html>'''
        statement, remarks, references = erdos_ingest.extract_source_page(page)
        self.assertEqual(statement, "A theorem?")
        self.assertEqual(remarks, "References in this remark are informal.")
        self.assertEqual(references, "[X1] Formal.")

    def test_structural_html_parser_preserves_tail_after_nested_div(self):
        page = b'''<html><body>
<div id="content">first<div>nested</div>tail</div>
<div class="problem-additional-text">before<div>inside</div>after</div>
</body></html>'''
        statement, remarks, references = erdos_ingest.extract_source_page(page)
        self.assertEqual(statement, "first\nnested\ntail")
        self.assertEqual(remarks, "before\ninside\nafter")
        self.assertEqual(references, "")

    def test_structural_html_parser_rejects_duplicate_content_regions(self):
        page = b'''<html><body>
<div id="content">first theorem</div>
<div id="content">second theorem</div>
</body></html>'''
        with self.assertRaises(erdos_ingest.SourceExtractionError):
            erdos_ingest.extract_source_page(page)

    def test_rendered_tex_sections_round_trip_without_crossing_source_footer(self):
        entry = {
            "number": "1",
            "prize": "no",
            "status": {"last_update": "2026-07-12"},
            "tags": ["number theory"],
        }
        tex = erdos_ingest.render_tex(
            entry,
            "Exact theorem?",
            "A source remark.",
            "[X1] A source reference.",
        )
        self.assertEqual(
            erdos_ingest.extract_tex_sections(tex),
            {
                "statement": "Exact theorem?",
                "remarks": "A source remark.",
                "references": "[X1] A source reference.",
            },
        )

    def test_ingestion_snapshots_first_party_bytes_and_applies_only_open_source(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "open" / "individual").mkdir(parents=True)
            (root / "individual").mkdir()
            output = root / "triage"
            fetched = []

            def fetch(url: str) -> bytes:
                fetched.append(url)
                if url == CATALOG_URL:
                    return YAML_SOURCE
                if url.endswith("/latex/1"):
                    return PAGE
                raise AssertionError(f"unexpected URL: {url}")

            result = ingest_corpus(
                root,
                output,
                fetch_bytes=fetch,
                apply=True,
                missing_only=True,
                snapshot_time="2026-07-12T12:00:00Z",
                delay_s=0,
            )

            self.assertEqual(result["selected_open_problems"], [1])
            self.assertEqual(len(fetched), 2)
            snapshot = output / "ingestion" / result["snapshot_id"]
            self.assertEqual((snapshot / "raw" / "problems.yaml").read_bytes(), YAML_SOURCE)
            self.assertEqual((snapshot / "raw" / "pages" / "problem_1.html").read_bytes(), PAGE)
            self.assertTrue((snapshot / "generated" / "problem_1.tex").exists())
            self.assertTrue((root / "open" / "individual" / "problem_1.tex").exists())
            self.assertTrue((root / "individual" / "problem_1.tex").exists())
            self.assertEqual(
                (root / "open" / "individual" / "problem_1.tex").stat().st_mode & 0o777,
                0o644,
            )
            self.assertEqual(
                (root / "individual" / "problem_1.tex").stat().st_mode & 0o777,
                0o644,
            )
            self.assertFalse((root / "open" / "individual" / "problem_2.tex").exists())
            manifest = json.loads((snapshot / "manifest.json").read_text())
            self.assertEqual(manifest["records"][0]["source_state"], "open")
            self.assertRegex(manifest["records"][0]["raw_html_sha256"], r"^[0-9a-f]{64}$")
            destinations = manifest["records"][0]["applied_destinations"]
            self.assertEqual(len(destinations), 2)
            for destination in destinations:
                self.assertIsNone(destination["before_sha256"])
                self.assertRegex(destination["after_sha256"], r"^[0-9a-f]{64}$")

            with self.assertRaises(FileExistsError):
                ingest_corpus(
                    root,
                    output,
                    fetch_bytes=fetch,
                    apply=False,
                    snapshot_time="2026-07-12T12:00:00Z",
                    delay_s=0,
                )

    def test_canonical_mode_snapshots_every_open_page_with_validated_section_provenance(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output = root / "triage"

            def fetch(url: str) -> bytes:
                if url == CATALOG_URL:
                    return YAML_TWO_OPEN
                if url.endswith("/latex/1"):
                    return PAGE
                if url.endswith("/latex/3"):
                    return PAGE_THREE
                raise AssertionError(f"unexpected URL: {url}")

            result = ingest_corpus(
                root,
                output,
                fetch_bytes=fetch,
                canonical=True,
                upstream_commit=TEST_UPSTREAM_COMMIT,
                commit_catalog_bytes=YAML_TWO_OPEN,
                snapshot_time="2026-07-12T12:00:01Z",
                delay_s=0,
            )

            self.assertTrue(result["canonical"])
            self.assertFalse(result["missing_only"])
            self.assertTrue(result["corpus_complete"])
            self.assertEqual(result["upstream_commit"], TEST_UPSTREAM_COMMIT)
            self.assertIn(TEST_UPSTREAM_COMMIT, result["commit_pinned_catalog_url"])
            self.assertEqual(
                result["commit_pinned_catalog_sha256"], result["catalog_sha256"]
            )
            self.assertEqual(result["selected_open_problems"], [1, 3])
            snapshot = output / "ingestion" / result["snapshot_id"]
            for record in result["records"]:
                self.assertRegex(record["source_record_sha256"], r"^[0-9a-f]{64}$")
                self.assertEqual(
                    sorted(record["section_sha256"]),
                    ["references", "remarks", "statement"],
                )
                self.assertTrue((snapshot / record["source_record_path"]).is_file())

            source = erdos_ingest.load_canonical_problem_source(snapshot, 3)
            self.assertEqual(source["statement"], "Is $a<b$ & $b>c$?")
            self.assertEqual(source["remarks"], "A second remark.")
            self.assertEqual(source["references"], "")

            catalog_path = snapshot / "raw" / "problems.yaml"
            catalog_path.write_bytes(b"tampered catalog")
            with self.assertRaises(erdos_ingest.ProvenanceError):
                erdos_ingest.load_canonical_problem_source(snapshot, 3)
            catalog_path.write_bytes(YAML_TWO_OPEN)

            manifest_path = snapshot / "manifest.json"
            complete_manifest = json.loads(manifest_path.read_text())
            truncated_manifest = dict(complete_manifest)
            truncated_manifest["catalog_open_records"] = 1
            truncated_manifest["selected_open_problems"] = [1]
            truncated_manifest["records"] = [complete_manifest["records"][0]]
            manifest_path.write_text(json.dumps(truncated_manifest))
            with self.assertRaises(erdos_ingest.ProvenanceError):
                erdos_ingest.load_canonical_problem_source(snapshot, 1)
            manifest_path.write_text(json.dumps(complete_manifest))

            other_source_path = snapshot / result["records"][0]["source_record_path"]
            other_source_bytes = other_source_path.read_bytes()
            other_source_path.unlink()
            with self.assertRaises(erdos_ingest.ProvenanceError):
                erdos_ingest.load_canonical_problem_source(snapshot, 3)
            other_source_path.write_bytes(other_source_bytes)

            (snapshot / result["records"][1]["source_record_path"]).unlink()
            with self.assertRaises(erdos_ingest.ProvenanceError):
                erdos_ingest.load_canonical_problem_source(snapshot, 3)

    def test_latest_canonical_snapshot_selector_ignores_newer_incomplete_snapshot(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output = root / "triage"

            def fetch(url: str) -> bytes:
                if url == CATALOG_URL:
                    return YAML_SOURCE
                if url.endswith("/latex/1"):
                    return PAGE
                raise AssertionError(f"unexpected URL: {url}")

            first = ingest_corpus(
                root,
                output,
                fetch_bytes=fetch,
                canonical=True,
                upstream_commit=TEST_UPSTREAM_COMMIT,
                commit_catalog_bytes=YAML_SOURCE,
                snapshot_time="2026-07-12T12:00:00Z",
                delay_s=0,
            )
            newer = ingest_corpus(
                root,
                output,
                fetch_bytes=fetch,
                canonical=True,
                upstream_commit=TEST_UPSTREAM_COMMIT,
                commit_catalog_bytes=YAML_SOURCE,
                snapshot_time="2026-07-12T12:00:01Z",
                delay_s=0,
            )
            newer_path = output / "ingestion" / newer["snapshot_id"]
            newer_record = newer["records"][0]
            (newer_path / newer_record["source_record_path"]).unlink()

            self.assertEqual(
                erdos_ingest.find_latest_canonical_snapshot(output),
                output / "ingestion" / first["snapshot_id"],
            )

            first_path = output / "ingestion" / first["snapshot_id"]
            first_manifest = json.loads((first_path / "manifest.json").read_text())
            first_manifest["canonical"] = False
            (first_path / "manifest.json").write_text(json.dumps(first_manifest))
            with self.assertRaises(erdos_ingest.ProvenanceError):
                erdos_ingest.find_latest_canonical_snapshot(output)

    def test_apply_waits_for_all_source_validation_and_writes_nothing_on_parse_error(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output = root / "triage"

            def fetch(url: str) -> bytes:
                if url == CATALOG_URL:
                    return YAML_TWO_OPEN
                if url.endswith("/latex/1"):
                    return PAGE
                if url.endswith("/latex/3"):
                    return b"<html><body>missing canonical content</body></html>"
                raise AssertionError(f"unexpected URL: {url}")

            result = ingest_corpus(
                root,
                output,
                fetch_bytes=fetch,
                apply=True,
                canonical=True,
                upstream_commit=TEST_UPSTREAM_COMMIT,
                commit_catalog_bytes=YAML_TWO_OPEN,
                snapshot_time="2026-07-12T12:00:02Z",
                delay_s=0,
            )

            self.assertFalse(result["corpus_complete"])
            self.assertEqual(result["application"]["status"], "skipped_source_errors")
            self.assertFalse((root / "open" / "individual" / "problem_1.tex").exists())
            self.assertFalse((root / "individual" / "problem_1.tex").exists())

    def test_canonical_ingestion_rejects_unpinned_or_different_commit_catalog(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output = root / "triage"

            def fetch(url: str) -> bytes:
                if url == CATALOG_URL:
                    return YAML_SOURCE
                if url.endswith("/latex/1"):
                    return PAGE
                raise AssertionError(f"unexpected URL: {url}")

            with self.assertRaises(erdos_ingest.ProvenanceError):
                ingest_corpus(
                    root, output, fetch_bytes=fetch, canonical=True,
                    upstream_commit=TEST_UPSTREAM_COMMIT,
                    commit_catalog_bytes=YAML_TWO_OPEN,
                    snapshot_time="2026-07-12T12:00:03Z", delay_s=0,
                )

    def test_legacy_canonical_snapshot_can_be_sealed_once_then_validates(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output = root / "triage"

            def fetch(url: str) -> bytes:
                if url == CATALOG_URL:
                    return YAML_SOURCE
                if url.endswith("/latex/1"):
                    return PAGE
                raise AssertionError(f"unexpected URL: {url}")

            result = ingest_corpus(
                root, output, fetch_bytes=fetch, canonical=True,
                upstream_commit=TEST_UPSTREAM_COMMIT,
                commit_catalog_bytes=YAML_SOURCE,
                snapshot_time="2026-07-12T12:00:04Z", delay_s=0,
            )
            snapshot = output / "ingestion" / result["snapshot_id"]
            manifest_path = snapshot / "manifest.json"
            legacy = json.loads(manifest_path.read_text())
            for field in (
                "upstream_repository_url", "upstream_commit",
                "commit_pinned_catalog_url", "commit_pinned_catalog_sha256",
            ):
                legacy.pop(field)
            manifest_path.write_text(json.dumps(legacy))
            with self.assertRaises(erdos_ingest.ProvenanceError):
                erdos_ingest.load_canonical_corpus(snapshot)

            sealed = erdos_ingest.seal_canonical_snapshot_upstream_provenance(
                snapshot,
                upstream_commit=TEST_UPSTREAM_COMMIT,
                commit_catalog_bytes=YAML_SOURCE,
            )
            self.assertEqual(sealed["upstream_commit"], TEST_UPSTREAM_COMMIT)
            self.assertEqual(set(erdos_ingest.load_canonical_corpus(snapshot)), {1})
            with self.assertRaises(erdos_ingest.ProvenanceError):
                erdos_ingest.seal_canonical_snapshot_upstream_provenance(
                    snapshot,
                    upstream_commit="b" * 40,
                    commit_catalog_bytes=YAML_SOURCE,
                )

    def test_safe_apply_rejects_symlinks_and_conflicting_pair_contents(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            open_path = root / "open" / "individual" / "problem_1.tex"
            mirror_path = root / "individual" / "problem_1.tex"
            open_path.parent.mkdir(parents=True)
            mirror_path.parent.mkdir(parents=True)
            target = root / "outside.tex"
            target.write_text("outside", encoding="utf-8")
            open_path.symlink_to(target)
            mirror_path.write_text("old", encoding="utf-8")

            with self.assertRaises(erdos_ingest.UnsafeDestinationError):
                erdos_ingest.safe_apply_tex_pair(root, "problem_1.tex", b"new")
            self.assertEqual(target.read_text(), "outside")
            self.assertEqual(mirror_path.read_text(), "old")

            open_path.unlink()
            open_path.write_text("old-a", encoding="utf-8")
            mirror_path.write_text("old-b", encoding="utf-8")
            with self.assertRaises(erdos_ingest.UnsafeDestinationError):
                erdos_ingest.safe_apply_tex_pair(root, "problem_1.tex", b"new")
            self.assertEqual(open_path.read_text(), "old-a")
            self.assertEqual(mirror_path.read_text(), "old-b")

    def test_safe_apply_rolls_back_first_destination_when_second_replace_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            open_path = root / "open" / "individual" / "problem_1.tex"
            mirror_path = root / "individual" / "problem_1.tex"
            open_path.parent.mkdir(parents=True)
            mirror_path.parent.mkdir(parents=True)
            open_path.write_bytes(b"old")
            mirror_path.write_bytes(b"old")
            calls = 0

            def fail_second_replace(source, destination):
                nonlocal calls
                calls += 1
                if calls == 2:
                    raise OSError("injected second replace failure")
                os.replace(source, destination)

            with self.assertRaises(erdos_ingest.ApplyTransactionError):
                erdos_ingest.safe_apply_tex_pair(
                    root,
                    "problem_1.tex",
                    b"new",
                    replace_file=fail_second_replace,
                )
            self.assertEqual(open_path.read_bytes(), b"old")
            self.assertEqual(mirror_path.read_bytes(), b"old")
            self.assertEqual(open_path.stat().st_mode & 0o777, 0o644)
            self.assertEqual(mirror_path.stat().st_mode & 0o777, 0o644)

    def test_safe_apply_honors_a_falsey_replacement_callable(self):
        class FalseyReplace:
            def __init__(self):
                self.calls = []

            def __bool__(self):
                return False

            def __call__(self, source, destination):
                self.calls.append((source, destination))
                os.replace(source, destination)

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "open" / "individual").mkdir(parents=True)
            (root / "individual").mkdir()
            replace = FalseyReplace()

            erdos_ingest.safe_apply_tex_pair(
                root, "problem_1.tex", b"new", replace_file=replace,
            )

            self.assertEqual(len(replace.calls), 2)
            self.assertEqual(
                (root / "open" / "individual" / "problem_1.tex").read_bytes(),
                b"new",
            )
            self.assertEqual(
                (root / "individual" / "problem_1.tex").read_bytes(), b"new",
            )


class LegacyStatementExtractionTests(unittest.TestCase):
    ROOT = Path(__file__).resolve().parents[1]

    def test_real_legacy_problem_1_excludes_remarks_and_references(self):
        statement = extract_problem_statement(
            self.ROOT / "open" / "individual" / "problem_1.tex"
        )
        self.assertEqual(
            statement,
            "If $A\\subseteq \\{1,\\ldots,N\\}$ with $\\lvert A\\rvert=n$ is "
            "such that the subset sums $\\sum_{a\\in S}a$ are distinct for all "
            "$S\\subseteq A$ then\\[N \\gg 2^{n}.\\]",
        )

    def test_real_legacy_problem_301_stops_before_unheaded_commentary(self):
        statement = extract_problem_statement(
            self.ROOT / "open" / "individual" / "problem_301.tex"
        )
        self.assertEqual(
            statement,
            "Let $f(N)$ be the size of the largest $A\\subseteq \\{1,\\ldots,N\\}$ "
            "such that there are no solutions to\\[\\frac{1}{a}= \\frac{1}{b_1}+"
            "\\cdots+\\frac{1}{b_k}\\]with distinct $a,b_1,\\ldots,b_k\\in A$? "
            "Estimate $f(N)$. In particular, is it true that "
            "$f(N)=(\\tfrac{1}{2}+o(1))N$?",
        )

    def test_real_legacy_problem_839_decodes_html_entities_in_theorem(self):
        statement = extract_problem_statement(
            self.ROOT / "open" / "individual" / "problem_839.tex"
        )
        self.assertEqual(
            statement,
            "Let $1\\leq a_1<a_2<\\cdots$ be a sequence of integers such that no "
            "$a_i$ is the sum of consecutive $a_j$ for $j<i$. Is it true that"
            "\\[\\limsup \\frac{a_n}{n}=\\infty?\\]Or even\\[\\lim "
            "\\frac{1}{\\log x}\\sum_{a_n<x}\\frac{1}{a_n}=0?\\]",
        )


if __name__ == "__main__":
    unittest.main()
