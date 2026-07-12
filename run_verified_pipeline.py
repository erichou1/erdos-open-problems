#!/usr/bin/env python3
"""Run the full verified pipeline for one problem through ChatGPT browser UI."""

import argparse
import fcntl
import hashlib
import json
import tempfile
import time
from pathlib import Path

import erdos_common as C
from erdos_searcher import (
    canonical_problem_run_inputs,
    find_latest_canonical_snapshot,
    load_canonical_corpus,
    normalized_budget_config,
)
from proof_pipeline import ProofPipeline
from outcome_ledger import record_outcome
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
                 backoff_s: float = 15.0, max_backoff_s: float = 120.0,
                 request_spacing_s: float = 12.0, max_attempts: int = 8):
        self.browser = browser
        self.page = page
        self.timeout_s = timeout_s
        self.max_backoff_s = max(0.0, min(120.0, max_backoff_s))
        self.backoff_s = min(max(0.0, backoff_s), self.max_backoff_s)
        self.rate_limiter = SharedRateLimiter(
            Path(tempfile.gettempdir()) / "erdos_chatgpt_rate_limit.json",
            backoff_s=self.backoff_s,
            max_backoff_s=self.max_backoff_s,
            request_spacing_s=request_spacing_s,
        )
        self.max_attempts = max_attempts
        self.contexts = {}

    def context_id(self, stage: str) -> str:
        return self.contexts.get(stage, "")

    def restore_context(self, stage: str, context_id: str) -> None:
        """Restore durable provenance when ProofPipeline replays a cache entry."""
        self.contexts[stage] = context_id

    def _cool_down(self, stage: str, reason: str) -> None:
        """Apply one shared cooldown across every browser worker."""
        streak, wait_s = self.rate_limiter.record_rate_limit()
        C.dismiss_rate_limit_modal(self.page)
        print(f"{stage}: {reason}; shared rate-limit streak={streak}; "
              f"all workers paused for up to {wait_s:.0f}s", flush=True)

    def run(self, prompt: str, *, stage: str, isolated: bool) -> str:
        if not isolated:
            raise ValueError("verified pipeline stages must use isolated contexts")

        last_error = "unknown"
        attempts_used = 0
        # A rate limit is a provider-side temporary condition, not a failed
        # proof stage. Keep the problem alive until ChatGPT accepts the prompt;
        # only real navigation/generation/response failures consume retries.
        while attempts_used < self.max_attempts:
            self.rate_limiter.wait_for_slot(stage)
            try:
                _ = self.page.url
            except Exception:
                self.page = self.browser.new_page()

            try:
                C.start_new_chat(self.page)

                # A rate-limit alert blocks chat creation — clear it and back off.
                if C.detect_rate_limit(self.page):
                    last_error = "rate-limited before send"
                    self._cool_down(stage, last_error)
                    continue

                start_url = C.current_url(self.page)
                C.send_prompt(self.page, prompt)
                url = C.wait_for_conversation_url(
                    self.page, timeout_s=120, start_url=start_url)

                if not url or url == start_url:
                    if C.detect_rate_limit(self.page):
                        last_error = "rate-limited after send"
                        self._cool_down(stage, last_error)
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
                        self._cool_down(stage, "rate-limited while generating")
                        self.rate_limiter.wait_for_slot(stage)
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

                self.rate_limiter.record_success()
                return response

            except Exception as exc:
                last_error = str(exc)
                print(f"{stage}: error '{exc}'", flush=True)
                try:
                    if C.detect_rate_limit(self.page):
                        last_error = "rate-limited during browser exception"
                        self._cool_down(stage, last_error)
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


class SharedRateLimiter:
    """Cross-process request gate for the single shared ChatGPT quota."""

    def __init__(self, path: Path, *, backoff_s: float,
                 max_backoff_s: float, request_spacing_s: float):
        self.path = path
        self.max_backoff_s = max(0.0, min(120.0, max_backoff_s))
        self.backoff_s = min(max(0.0, backoff_s), self.max_backoff_s)
        self.request_spacing_s = max(0.0, min(120.0, request_spacing_s))
        self.path.touch(exist_ok=True)

    def _update(self, action):
        with self.path.open("r+", encoding="utf-8") as handle:
            fcntl.flock(handle, fcntl.LOCK_EX)
            try:
                try:
                    state = json.load(handle)
                except (json.JSONDecodeError, ValueError):
                    state = {}
                result = action(state)
                handle.seek(0)
                handle.truncate()
                json.dump(state, handle)
                handle.flush()
                return result
            finally:
                fcntl.flock(handle, fcntl.LOCK_UN)

    def wait_for_slot(self, stage: str) -> None:
        """Serialize sends and honor a cooldown imposed by any worker."""
        while True:
            now = time.time()

            def reserve(state):
                ceiling = now + 120.0
                state["cooldown_until"] = min(
                    float(state.get("cooldown_until", 0)), ceiling
                )
                state["next_request_at"] = min(
                    float(state.get("next_request_at", 0)), ceiling
                )
                ready_at = max(state["cooldown_until"], state["next_request_at"])
                if ready_at <= now:
                    state["next_request_at"] = now + self.request_spacing_s
                    return 0.0
                return ready_at - now

            delay = self._update(reserve)
            if delay <= 0:
                return
            print(f"{stage}: waiting {delay:.0f}s for the shared ChatGPT quota",
                  flush=True)
            time.sleep(delay)

    def record_rate_limit(self) -> tuple[int, float]:
        now = time.time()

        def penalize(state):
            streak = int(state.get("rate_limit_streak", 0)) + 1
            wait_s = min(self.backoff_s * (2 ** max(0, streak - 1)),
                         self.max_backoff_s)
            state["rate_limit_streak"] = streak
            ceiling = now + 120.0
            existing_cooldown = min(
                float(state.get("cooldown_until", 0)), ceiling
            )
            existing_request = min(
                float(state.get("next_request_at", 0)), ceiling
            )
            state["cooldown_until"] = max(existing_cooldown, now + wait_s)
            state["next_request_at"] = max(
                existing_request, state["cooldown_until"]
            )
            return streak, wait_s

        return self._update(penalize)

    def record_success(self) -> None:
        def clear_penalty(state):
            state["rate_limit_streak"] = 0
            # Another worker may have recorded a newer 429 while this request
            # was in flight. Never erase shared future cooldown/spacing state.

        self._update(clear_penalty)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--problem", type=int, required=True)
    parser.add_argument("--category", default="open")
    parser.add_argument("--artifacts", type=Path, default=Path("proof_runs"))
    parser.add_argument("--triage", type=Path, default=Path("triage"))
    parser.add_argument("--stage-timeout", type=float, default=1800)
    parser.add_argument("--backoff", type=float, default=15.0,
                        help="Initial seconds to wait after a rate-limit alert")
    parser.add_argument("--max-backoff", type=float, default=120.0,
                        help="Maximum adaptive rate-limit backoff in seconds")
    parser.add_argument("--request-spacing", type=float, default=12.0,
                        help="Minimum seconds between any two worker requests")
    parser.add_argument("--max-revisions", type=int, default=2)
    parser.add_argument("--max-attempts", type=int, default=8)
    parser.add_argument(
        "--model-id", required=True,
        help="Exact ChatGPT UI model/version disclosure stored in the manifest",
    )
    parser.add_argument("--print-statement-sha", action="store_true")
    parser.add_argument("--headless", action="store_true")
    args = parser.parse_args()

    triage_dir = args.triage if args.triage.is_absolute() else C.REPO_DIR / args.triage
    if args.print_statement_sha:
        snapshot = find_latest_canonical_snapshot(triage_dir)
        sources = load_canonical_corpus(snapshot)
        if args.problem not in sources:
            raise SystemExit(f"problem {args.problem} is not source-open")
        print(make_statement_lock(sources[args.problem]["statement"]).sha256)
        return
    if "unrecorded" in args.model_id.lower() or not args.model_id.strip():
        parser.error("--model-id must be the exact recorded UI model identity")
    budget_config = normalized_budget_config(
        max_revisions=args.max_revisions,
        stage_timeout_s=args.stage_timeout,
        initial_backoff_s=args.backoff,
        max_backoff_s=args.max_backoff,
        request_spacing_s=args.request_spacing,
        max_attempts=args.max_attempts,
        browser_headless=args.headless,
    )
    try:
        run_inputs = canonical_problem_run_inputs(
            C.REPO_DIR,
            triage_dir,
            args.problem,
            model_portfolio=args.model_id,
            budget_config=budget_config,
        )
    except Exception as error:
        raise SystemExit(f"exact canonical run context unavailable: {error}") from error
    statement = run_inputs["statement"]
    C.PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    with C.sync_playwright() as playwright:
        browser = C.launch_browser(playwright, headless=args.headless)
        page = browser.pages[0] if browser.pages else browser.new_page()
        C.ensure_logged_in(page)
        runner = ChatGPTBrowserRunner(
            browser, page, timeout_s=budget_config["stage_timeout_s"],
            backoff_s=budget_config["initial_backoff_s"],
            max_backoff_s=budget_config["max_backoff_s"],
            request_spacing_s=budget_config["request_spacing_s"],
            max_attempts=budget_config["max_attempts"],
        )
        result = ProofPipeline(
            runner,
            args.artifacts,
            max_revisions=args.max_revisions,
            pipeline_version=run_inputs["pipeline_version"],
            model_portfolio=args.model_id,
            execution_config=run_inputs["execution_config"],
            source_snapshot_id=run_inputs["source_snapshot_id"],
            source_snapshot_sha256=run_inputs["source_snapshot_sha256"],
            toolset=run_inputs["toolset"],
            dependencies=run_inputs["dependencies"],
            runtime=run_inputs["runtime"],
        ).solve(
            args.problem, statement,
            research_directive=run_inputs["research_directive"],
        )
        record_outcome(
            triage_dir, args.problem, result.artifact_dir / "manifest.json",
        )
        browser.close()

    print(f"candidate: {result.candidate_outcome}")
    print(f"gate: {result.gate.status}")
    for reason in result.gate.reasons:
        print(f"- {reason}")
    print(f"artifacts: {result.artifact_dir}")
    print("External evidence is applied afterward with promote_verified_run.py.")


if __name__ == "__main__":
    main()
