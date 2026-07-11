#!/usr/bin/env python3
"""Run the full verified pipeline for one problem through ChatGPT browser UI."""

import argparse
import hashlib
import json
import time
from pathlib import Path

import erdos_common as C
from proof_pipeline import ProofPipeline
from research_state import make_statement_lock
from verification import candidate_contract, VerificationEvidence


def load_evidence(path: Path | None) -> tuple[VerificationEvidence, ...]:
    if path is None:
        return ()
    records = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(records, list):
        raise ValueError("evidence JSON must be a list")
    evidence = []
    for record in records:
        artifact = Path(record["artifact_path"]).expanduser().resolve()
        artifact_sha = hashlib.sha256(artifact.read_bytes()).hexdigest()
        evidence.append(VerificationEvidence(
            kind=str(record["kind"]),
            verifier=str(record["verifier"]),
            outcome=str(record["outcome"]),
            statement_sha256=str(record["statement_sha256"]),
            candidate_sha256=str(record["candidate_sha256"]),
            artifact_sha256=artifact_sha,
            passed=record.get("passed") is True,
        ))
    return tuple(evidence)


def publish_verified_result(result, category: str, base_dir: Path) -> Path:
    if result.gate.status not in {"verified_proved", "verified_disproved"}:
        raise ValueError("only a gate-approved result can be published")
    status = result.gate.status.replace("_", "-")
    candidate = (result.artifact_dir / "candidate.md").read_text(encoding="utf-8")
    completeness = candidate_contract(candidate).completeness_score
    body = (
        f"# Erdős Problem #{result.problem_number} [{status}] {completeness}%\n\n"
        f"Verification manifest SHA-256: "
        f"{hashlib.sha256((result.artifact_dir / 'manifest.json').read_bytes()).hexdigest()}\n\n"
        f"## Verified candidate\n\n{candidate}\n"
    )
    output_dir = base_dir / "outputs" / "chatgpt" / category
    output_dir.mkdir(parents=True, exist_ok=True)
    for stale in output_dir.glob(f"Erdős #{result.problem_number} *.md"):
        if "[verified-" in stale.name:
            stale.unlink()
    output = output_dir / (
        f"Erdős #{result.problem_number} [{status}] {completeness}%.md"
    )
    output.write_text(body, encoding="utf-8")
    return output


class ChatGPTBrowserRunner:
    """Fresh-chat adapter for ProofPipeline's isolated model calls."""

    def __init__(self, browser, page, *, timeout_s: float,
                 backoff_s: float = 180.0, max_backoff_s: float = 1800.0,
                 max_attempts: int = 8):
        self.browser = browser
        self.page = page
        self.timeout_s = timeout_s
        self.backoff_s = backoff_s
        self.max_backoff_s = max(backoff_s, max_backoff_s)
        self.max_attempts = max_attempts
        self.contexts = {}

    def context_id(self, stage: str) -> str:
        return self.contexts.get(stage, "")

    def _cool_down(self, stage: str, reason: str, streak: int) -> None:
        """Dismiss a rate-limit alert and wait with capped exponential backoff."""
        wait_s = min(self.backoff_s * (2 ** max(0, streak - 1)),
                     self.max_backoff_s)
        C.dismiss_rate_limit_modal(self.page)
        print(f"{stage}: {reason}; consecutive rate limits={streak}; "
              f"waiting {wait_s:.0f}s before retrying (does not use a retry)",
              flush=True)
        time.sleep(wait_s)

    def run(self, prompt: str, *, stage: str, isolated: bool) -> str:
        if not isolated:
            raise ValueError("verified pipeline stages must use isolated contexts")

        last_error = "unknown"
        attempts_used = 0
        rate_limit_streak = 0
        # A rate limit is a provider-side temporary condition, not a failed
        # proof stage. Keep the problem alive until ChatGPT accepts the prompt;
        # only real navigation/generation/response failures consume retries.
        while attempts_used < self.max_attempts:
            try:
                _ = self.page.url
            except Exception:
                self.page = self.browser.new_page()

            try:
                C.start_new_chat(self.page)

                # A rate-limit alert blocks chat creation — clear it and back off.
                if C.detect_rate_limit(self.page):
                    rate_limit_streak += 1
                    last_error = "rate-limited before send"
                    self._cool_down(stage, last_error, rate_limit_streak)
                    continue
                rate_limit_streak = 0

                start_url = C.current_url(self.page)
                C.send_prompt(self.page, prompt)
                url = C.wait_for_conversation_url(
                    self.page, timeout_s=120, start_url=start_url)

                if not url or url == start_url:
                    if C.detect_rate_limit(self.page):
                        rate_limit_streak += 1
                        last_error = "rate-limited after send"
                        self._cool_down(stage, last_error, rate_limit_streak)
                        continue
                    attempts_used += 1
                    last_error = "no conversation URL"
                    print(f"{stage}: no conversation URL (attempt {attempts_used}); retrying",
                          flush=True)
                    time.sleep(15)
                    continue

                self.contexts[stage] = url
                print(f"{stage}: waiting for response at {url}", flush=True)
                time.sleep(5)

                deadline = time.time() + self.timeout_s
                while time.time() < deadline and C.is_generating(self.page):
                    # A throttle can pop up mid-generation; keep the UI clear.
                    if C.detect_rate_limit(self.page):
                        C.dismiss_rate_limit_modal(self.page)
                    time.sleep(5)

                if C.is_generating(self.page):
                    attempts_used += 1
                    last_error = f"generation exceeded {self.timeout_s:.0f}s"
                    print(f"{stage}: {last_error} (attempt {attempts_used}); backing off",
                          flush=True)
                    time.sleep(self.backoff_s)
                    continue

                time.sleep(2)
                response = C.extract_response(self.page)
                if not response or len(response.strip()) < 100:
                    attempts_used += 1
                    last_error = "empty/incomplete response"
                    print(f"{stage}: {last_error} (attempt {attempts_used}); retrying",
                          flush=True)
                    time.sleep(15)
                    continue

                return response

            except Exception as exc:
                last_error = str(exc)
                print(f"{stage}: error '{exc}'", flush=True)
                try:
                    if C.detect_rate_limit(self.page):
                        rate_limit_streak += 1
                        last_error = "rate-limited during browser exception"
                        self._cool_down(stage, last_error, rate_limit_streak)
                        continue
                except Exception:
                    pass
                attempts_used += 1
                print(f"{stage}: retrying after browser error "
                      f"(attempt {attempts_used})", flush=True)
                time.sleep(15)

        raise RuntimeError(
            f"{stage}: failed after {self.max_attempts} non-rate-limit attempts "
            f"({last_error})")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--problem", type=int, required=True)
    parser.add_argument("--category", default="open")
    parser.add_argument("--artifacts", type=Path, default=Path("proof_runs"))
    parser.add_argument("--stage-timeout", type=float, default=1800)
    parser.add_argument("--backoff", type=float, default=180.0,
                        help="Initial seconds to wait after a rate-limit alert")
    parser.add_argument("--max-backoff", type=float, default=1800.0,
                        help="Maximum adaptive rate-limit backoff in seconds")
    parser.add_argument("--max-revisions", type=int, default=2)
    parser.add_argument("--print-statement-sha", action="store_true")
    parser.add_argument("--headless", action="store_true")
    args = parser.parse_args()

    problem_file = C.REPO_DIR / args.category / "individual" / f"problem_{args.problem}.tex"
    if not problem_file.exists():
        raise SystemExit(f"problem file not found: {problem_file}")
    statement = C.extract_problem_statement(problem_file)
    if args.print_statement_sha:
        print(make_statement_lock(statement).sha256)
        return

    C.PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    with C.sync_playwright() as playwright:
        browser = C.launch_browser(playwright, headless=args.headless)
        page = browser.pages[0] if browser.pages else browser.new_page()
        C.ensure_logged_in(page)
        runner = ChatGPTBrowserRunner(
            browser, page, timeout_s=args.stage_timeout,
            backoff_s=args.backoff,
            max_backoff_s=args.max_backoff,
        )
        result = ProofPipeline(
            runner,
            args.artifacts,
            max_revisions=args.max_revisions,
        ).solve(args.problem, statement)
        browser.close()

    print(f"candidate: {result.candidate_outcome}")
    print(f"gate: {result.gate.status}")
    for reason in result.gate.reasons:
        print(f"- {reason}")
    print(f"artifacts: {result.artifact_dir}")
    print("External evidence is applied afterward with promote_verified_run.py.")


if __name__ == "__main__":
    main()
