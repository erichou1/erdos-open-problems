import hashlib
import importlib
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from erdos_ingest import ProvenanceError


class LegacyCandidateCollectionTests(unittest.TestCase):
    prompt_template = "Candidate body:\n{problem}"

    def source(self):
        from legacy_candidate_collection import CandidateSource

        statement = "Canonical statement, not the mutable local TeX."
        return CandidateSource(
            problem_number=601,
            statement=statement,
            source_url="https://www.erdosproblems.com/latex/601",
            source_snapshot_id="20260712-source",
            source_snapshot_sha256="a" * 64,
            statement_sha256=hashlib.sha256(statement.encode("utf-8")).hexdigest(),
        )

    def test_cooldown_values_are_nonnegative_and_hard_capped_at_120_seconds(self):
        from legacy_candidate_collection import AdaptiveCooldown, clamp_cooldown

        self.assertEqual(clamp_cooldown(999), 120.0)
        self.assertEqual(clamp_cooldown(30), 30.0)
        self.assertEqual(clamp_cooldown(-1), 0.0)
        with self.assertRaises(ValueError):
            clamp_cooldown(float("nan"))
        limiter = AdaptiveCooldown(15)
        self.assertEqual(
            [limiter.record_rate_limit() for _ in range(5)],
            [15.0, 30.0, 60.0, 120.0, 120.0],
        )
        limiter.record_success()
        self.assertEqual(limiter.record_rate_limit(), 15.0)

    def test_prompt_begins_with_immutable_source_and_unverified_contract(self):
        from legacy_candidate_collection import (
            build_bound_prompt,
            build_collection_contract,
        )

        source = self.source()
        contract = build_collection_contract(
            source,
            provider="chatgpt",
            category="open",
            prompt_template=self.prompt_template,
        )
        prompt = build_bound_prompt(
            self.prompt_template, source=source, contract=contract
        )

        self.assertTrue(prompt.startswith("IMMUTABLE SOURCE CONTRACT"))
        header, body = prompt.split("\n\n", 1)
        self.assertIn("collection_status: UNVERIFIED_CANDIDATE", header)
        self.assertIn(f"source_snapshot_id: {source.source_snapshot_id}", header)
        self.assertIn(
            f"source_snapshot_sha256: {source.source_snapshot_sha256}", header
        )
        self.assertIn(f"statement_sha256: {source.statement_sha256}", header)
        self.assertIn(
            f"candidate_collection_contract_id: {contract['candidate_collection_contract_id']}",
            header,
        )
        self.assertIn(source.statement, body)
        self.assertNotIn("mutable local TeX", body.replace(source.statement, ""))

    def test_chat_reuse_requires_exact_current_source_and_collection_identity(self):
        from legacy_candidate_collection import (
            build_collection_contract,
            chat_metadata,
            reusable_chat_entry,
        )

        contract = build_collection_contract(
            self.source(),
            provider="deepseek",
            category="open",
            prompt_template=self.prompt_template,
        )
        exact = chat_metadata(contract, "https://chat.deepseek.com/a/chat/s/abc")

        def valid_url(value):
            return "/a/chat/s/" in value

        self.assertTrue(reusable_chat_entry(exact, contract, valid_url=valid_url))
        self.assertFalse(
            reusable_chat_entry(
                {"url": exact["url"], "problem": 601},
                contract,
                valid_url=valid_url,
            )
        )
        for field in (
            "source_snapshot_id",
            "source_snapshot_sha256",
            "statement_sha256",
            "candidate_collection_contract_id",
        ):
            stale = dict(exact)
            stale[field] = "f" * 64
            self.assertFalse(
                reusable_chat_entry(stale, contract, valid_url=valid_url), field
            )

    def test_recorded_chat_metadata_is_explicitly_unverified(self):
        from legacy_candidate_collection import (
            build_collection_contract,
            chat_metadata,
        )

        contract = build_collection_contract(
            self.source(),
            provider="chatgpt",
            category="open",
            prompt_template=self.prompt_template,
        )
        metadata = chat_metadata(contract, "https://chatgpt.com/c/abc")

        self.assertEqual(metadata["collection_status"], "UNVERIFIED_CANDIDATE")
        self.assertEqual(metadata["provider"], "chatgpt")
        self.assertEqual(metadata["problem"], 601)

    def test_collection_identity_changes_when_the_prompt_contract_changes(self):
        from legacy_candidate_collection import build_collection_contract

        common = {
            "provider": "chatgpt",
            "category": "open",
        }
        first = build_collection_contract(
            self.source(), prompt_template="first {problem}", **common
        )
        second = build_collection_contract(
            self.source(), prompt_template="second {problem}", **common
        )

        self.assertNotEqual(
            first["candidate_collection_contract_id"],
            second["candidate_collection_contract_id"],
        )
        self.assertNotEqual(
            first["prompt_template_sha256"], second["prompt_template_sha256"]
        )

    def test_loading_without_a_complete_canonical_snapshot_fails_closed(self):
        from legacy_candidate_collection import load_canonical_candidate_sources

        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ProvenanceError):
                load_canonical_candidate_sources(Path(directory))

    def test_each_collector_builds_its_provider_specific_bound_submission(self):
        import deepseek_submit
        import solve_submit

        source = self.source()
        chatgpt_contract, chatgpt_prompt = solve_submit.prepare_submission(
            source, "open"
        )
        deepseek_contract, deepseek_prompt = deepseek_submit.prepare_submission(
            source, "open"
        )

        self.assertEqual(chatgpt_contract["provider"], "chatgpt")
        self.assertEqual(deepseek_contract["provider"], "deepseek")
        self.assertIn(source.statement, chatgpt_prompt)
        self.assertIn(source.statement, deepseek_prompt)
        self.assertTrue(chatgpt_prompt.startswith("IMMUTABLE SOURCE CONTRACT"))
        self.assertTrue(deepseek_prompt.startswith("IMMUTABLE SOURCE CONTRACT"))

    def test_chatgpt_submission_refuses_missing_snapshot_before_browser_launch(self):
        import solve_submit

        with (
            patch.object(
                solve_submit,
                "load_canonical_candidate_sources",
                side_effect=ProvenanceError("no complete snapshot"),
            ),
            patch.object(solve_submit, "sync_playwright") as playwright,
        ):
            with self.assertRaises(SystemExit) as raised:
                solve_submit.main(["--problem", "601"])

        self.assertIn("complete canonical", str(raised.exception))
        playwright.assert_not_called()

    def test_deepseek_submission_refuses_problem_missing_from_canonical_sources(self):
        import deepseek_submit

        with (
            tempfile.TemporaryDirectory() as directory,
            patch.object(
                deepseek_submit,
                "load_canonical_candidate_sources",
                return_value={},
            ),
            patch.object(
                deepseek_submit.D,
                "DS_PROFILE_DIR",
                Path(directory) / "profile",
            ),
            patch.object(deepseek_submit, "sync_playwright") as playwright,
            patch.object(deepseek_submit.D, "launch_browser") as launch_browser,
            patch.object(deepseek_submit.D, "ensure_logged_in") as ensure_logged_in,
        ):
            with self.assertRaises(SystemExit) as raised:
                deepseek_submit.main(["--problem", "601"])

        self.assertIn("not present", str(raised.exception))
        playwright.assert_called_once_with()
        launch_browser.assert_called_once()
        ensure_logged_in.assert_not_called()

    def test_range_wrapper_delegates_without_replacing_the_global_source_loader(self):
        import erdos_common

        original = erdos_common.get_problem_files
        range_runner = importlib.import_module("run_900_1200")
        self.assertIs(erdos_common.get_problem_files, original)

        with patch.object(range_runner.solve_submit, "main") as delegated:
            range_runner.main(["--limit", "1"])

        args, kwargs = delegated.call_args
        self.assertEqual(args[0], ["--limit", "1"])
        provider = kwargs["problem_file_provider"]
        paths = provider("open")
        self.assertTrue(paths)
        self.assertTrue(
            all("range_900_1200/individual" in str(path) for path in paths)
        )


if __name__ == "__main__":
    unittest.main()
