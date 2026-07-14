# EGMRA_IMPLEMENTATION_EVIDENCE.md

**Verdict: INCOMPLETE — BLOCKED ON LIVE ACCEPTANCE.**

> ## Session update (concurrency + quarantine hardening)
> Machine-readable per-scenario status is in `egmra_acceptance_manifest.json`. This session:
> - **Defect 4.2 (fake five-worker concurrency) — FIXED.** `Campaign.drain` hardcoded `worker_ids[0]`; added `Campaign.run_concurrent` (real threads, per-worker leases, monotonic fencing, `heartbeat`, in-process + `fcntl` lock) and wired `egmra campaign` to it. A `threading.Barrier(5)` test proves genuine 5-way overlap; live CLI run showed `max_observed_concurrency=5`, `distinct_workers=5`, no dup/skip. Browser provider is capped to `--workers 1` (Playwright sync is single-threaded; multi-tab async is future work).
> - **Defect 4.8 (quarantine symlink-follow) — FIXED.** `resolve_quarantine_dir` now `lstat`-checks the root and job-dir child WITHOUT following, and `verify_local_replay` rescans for symlinks immediately before replay. Adversarial tests cover symlink destinations inside and outside the root.
> - **Defect 4.3 (shared throttle not wired) — FIXED.** `_browser_throttle()` builds a durable `SharedThrottle` and `_build_runner` passes it to the browser runner in both `run` and `campaign`.
> - Full suite: **939 passed + 44 subtests**, rc=0.
> - **Still not done this session** (verdict remains INCOMPLETE): live retrieval/OEIS wiring (4.4), compute-execution wiring (4.5), `LeanService`-into-`run` + live kernel (4.6), `--event-store postgres` CLI wiring (4.9), durable browser transcript artifacts (4.10). See the manifest's `remaining_defects_not_addressed_this_session`.

> ## Session update (live acceptance + B-items)
> Since the first draft, the following were **live-verified on the operator's machine** and additional code landed:> - **A0/A1 browser end-to-end — VERIFIED live.** `egmra run --provider browser` (authenticated ChatGPT profile) rc=0 → real ChatGPT → `RunnerWorker` parsed **9 claims across 3 branches** → signed event log `integrity: true` (14 events) → honest `BLOCKED_BY_INTERPRETATION`, no fabrication.
> - **A2 PostgreSQL — VERIFIED live (scenario 11).** Throwaway `postgres:16`; `PostgresEventStore.append` (seq 0/1) → `verify_integrity: True` → fresh reconnect reproduces the same merkle head.
> - **A3 Python 3.10 — VERIFIED.** 3.10.20 venv, `pip install -e .[dev]`, full suite rc=0.
> - **B1 Lean replay bridge — DONE (code+tests).** `egmra/lean/replay.py` `LeanReplayVerifier` runs the real pinned kernel (`AttestedKernelRunner`), verifies the signed `CheckerAttestation` is bound to the exact target type + within the axiom whitelist, and seals a `LocalLeanReplayAttestation` bound to the quarantined tree; `bind_local_replay` promotes only then. Live kernel run still needs `elan default stable` + a pinned Mathlib project.
> - **B3 durable campaign — DONE (code+CLI+tests).** `egmra/orchestrator/campaign.py` + `egmra campaign` CLI: HMAC-signed durable state, monotonic fencing tokens, lease expiry reclaim, retain-on-provider-outage, resume with no skip/dup, tamper fails closed (scenarios 7, 8).
> - **B2 Aristotle — DONE (official SDK, code+tests); live needs the built Lean project.** The operator supplied the official docs: Aristotle ships as `aristotlelib` (v2.1.0) and is Lean-native (Lean v4.28.0 + Mathlib v4.28.0). Per the task, I use the **official SDK** (`Project.create_from_directory` → `AgentTask.wait_for_completion` → `project.get_files`) via [egmra/lean/aristotle_sdk.py](egmra/lean/aristotle_sdk.py) `AristotleSdkClient` instead of guessed REST. Key read from env only (never logged); downloaded Lean is quarantined + symlink/escape/bomb-scanned; a vendor `COMPLETE` is never promotable — promotion requires the B1 sealed local replay. `.[aristotle]` extra added; hermetic fake-SDK tests. A pinned Lean project scaffold is at `aristotle_lean_project/` (lean-toolchain + lakefile.toml at v4.28.0). Live submit needs `lake build` of that project + `ARISTOTLE_API_KEY`.
> - Full suite: **934 passed + 44 subtests**, rc=0.

The confirmed local defects (epistemic-invariant and security violations,
packaging, provider wiring, doctor readiness, event-store protocol conformance)
are repaired with reproduced-then-fixed regression tests. The end-to-end
acceptance scenarios that require external infrastructure (authenticated ChatGPT
browser profile, Lean/Mathlib toolchain, Aristotle credentials, a PostgreSQL
server, live OEIS/retrieval) cannot be executed in this environment and are kept
explicitly incomplete below.

FABLE_TRACEABILITY_MATRIX.md verdicts were **not** edited. This document is
self-reported and left for independent re-audit.

## Environment + top-line commands

- Dev interpreter available locally: CPython 3.14.4 (no local 3.10/3.11/3.12; CI
  matrix covers 3.10 & 3.12).
- Full suite (editable install, dev venv):
  `python -m pytest egmra/tests tests` → **911 passed, 44 subtests passed**, exit 0.
- Clean `.[dev]` install (fresh venv): complete suite **collects with 0 errors**
  and runs exit 0 (`pip install -e .[dev]` then `pytest egmra/tests tests`).
- Clean **wheel** outside the checkout (`cwd=/tmp`, wheel-only venv):
  `egmra --help` (rc 0), `egmra doctor` (rc 0),
  `egmra --config cfg.json run --erdos 312 --provider deterministic --policy policy.json`
  → `result_state = BLOCKED_BY_INTERPRETATION`, `proof_complete=false`, exit 0.

## Confirmed defects — reproduced, then repaired

| # | Defect | Fix (production call path) | Regression test(s) | Status |
|---|--------|----------------------------|--------------------|--------|
| 1 | CLI used `DeterministicWorker` for arbitrary problems | `egmra/cli.py` `_run_arbitrary` now builds `RunnerWorker` over a selected provider | `test_cli_arbitrary.py::test_run_does_not_touch_fixture_loader` | FIXED |
| 2 | No real adapters injected by the CLI | `--provider browser\|deterministic` in `cli._build_runner`; browser → `BrowserChatGPTRunner`/`PlaywrightChatGPTBackend` | `test_cli_arbitrary.py::test_run_browser_provider_without_profile_fails_cleanly` | FIXED (browser live path BLOCKED) |
| 3 | Model responses not converted to `WorkerOutput` | `egmra/orchestrator/runner_worker.py` `RunnerWorker` parses a strict schema → claims/lemmas/falsifiers/queries/sequences; never emits proof evidence | `test_runner_worker.py` (8 tests) | FIXED |
| 4 | Browser/Aristotle referenced only by tests | Both now on the production `run` path (browser via `--provider`, Aristotle via `AristotleApiClient` + local replay) | `test_runner_worker.py`, `test_aristotle_api.py` | FIXED (live BLOCKED) |
| 5 | `result_states` checked external/formal before interpretation; no release artifact required | `classify_result` now returns `BLOCKED_BY_INTERPRETATION` first; external states require `_valid_release` (promoted, claim+contract-hash bound, signature verifies); formal requires `_valid_formal_certificate` (T4/T5+F2+cert id) | `test_result_states.py` adversarial suite (12 new) | FIXED |
| 6 | `bind_local_replay` accepted any truthy object | Requires a sealed, artifact-bound `LocalLeanReplayAttestation` (HMAC under `EGMRA_LEAN_CHECKER_KEY`); bool/str/dict rejected | `test_aristotle_api.py::test_bind_local_replay_rejects_truthy_non_attestation` (+4) | FIXED |
| 7 | Unsanitized job IDs escaped quarantine | `validate_job_id` strict regex + `_resolve_quarantine_dir` proves containment + refuses symlink dest; HTTP URL-encodes ids, `allow_redirects=False` | `test_aristotle_api.py::test_download_rejects_traversal_job_id` (+2) | FIXED |
| 8 | Wheel omitted corpus/policy, depended on `erdos_common` | Corpus shipped as package data (`egmra/data/*`); browser glue vendored (`egmra/agents/chatgpt_browser.py`); no repo-root import at runtime | Clean-wheel run from `/tmp` (above) | FIXED |
| 9 | Clean `.[dev]` couldn't collect the suite | `.[dev]` now includes `requests`, `PyYAML`, `playwright`, `fpdf2` | Clean `.[dev]` collect (0 errors, above) | FIXED |
| 10 | 3.10 advertised but `enum.StrEnum` (3.11+) used | `result_states` imports the repo's 3.10-safe `StrEnum` shim | Suite runs; CI matrix 3.10 | FIXED |
| 11 | Per-instance throttle, checked only before request | `egmra/agents/throttle.py` `SharedThrottle` (file+flock, cross-worker, Retry-After, 120 s clamp) wired into `BrowserChatGPTRunner`; checked before/at each pause | `test_throttle.py` (5 tests) | FIXED |
| 12 | Responses extracted before generation began | `chatgpt_browser.wait_for_generation_start` gates `PlaywrightChatGPTBackend.wait_response` | code path (browser live BLOCKED) | FIXED (logic) |
| 13 | Exhausted retries raised without retain/resume | `BrowserProviderUnavailable` → CLI exit 4 `provider_unavailable`, retains the durable event log; never a math verdict | `test_cli_arbitrary.py::test_provider_unavailable_is_retained_not_a_math_failure` | FIXED (single-run); campaign resume BLOCKED |
| 14 | `PostgresEventStore` incomplete protocol | Implements `append`/`verify_integrity`/`merkle_root` via real psycopg reusing shared `seal_event` (parity by construction); DSN redacted; `UNIQUE(run_id,sequence)` | `test_m2_postgres_conformance.py` (6 tests) | PROTOCOL FIXED; live replay BLOCKED |
| 15 | Retrieval only in-memory; arbitrary runs supply none | Empty retrieval is never presented as completed review — honest state stays OPEN/BLOCKED/PARTIAL | `test_cli_arbitrary.py` open-state tests | PARTIAL; live retrieval BLOCKED |
| 16 | `doctor` reported Lean ready on launcher presence | `_probe_executable` runs `--version`; `_lean_toolchain_report` requires operational lake+lean AND a configured project | `test_cli_arbitrary.py::test_doctor_distinguishes_launcher_from_operational_lean` | FIXED |
| 17 | No clean-package / live e2e demonstrated | Clean wheel + clean `.[dev]` verified above; live e2e still BLOCKED | see commands above | PARTIAL |

## Non-negotiable epistemic invariants — where enforced

- Ambiguous/malformed/parser-disputed target can never be proved/validated →
  `result_states.classify_result` step 1 (`test_blocked_interpretation_dominates_*`).
- Evidence about a different statement cannot prove the original → `_valid_release`
  binds `result_claim_hash`/`problem_contract_hash` (`test_release_for_strengthened_statement_is_rejected`).
- No positive terminal without required artifacts → `_valid_release` /
  `_valid_formal_certificate` (`test_external_profile_without_release_is_not_validated`).
- Vendor "complete" is never verification → `AristotleArtifact.promotable=False`,
  `poll` never promotes (`test_vendor_complete_alone_never_promotes`).
- Caller truthiness cannot manufacture formal status → sealed
  `LocalLeanReplayAttestation` (`test_bind_local_replay_rejects_truthy_non_attestation`).
- Computational evidence ≠ proof → `COMPUTATIONAL_EVIDENCE` distinct from
  `CANDIDATE_PROOF` (`test_computational_evidence_for_finite_exact_support`).
- Rate limiting pauses/retries/retains, never fails the problem →
  `SharedThrottle` + `BrowserProviderUnavailable`→exit 4 retain.

## End-to-end acceptance scenarios

| # | Scenario | Status | Evidence / blocker |
|---|----------|--------|--------------------|
| 1 | False statement → reproducible counterexample, CANDIDATE_DISPROOF | LOCAL (fixture) | `fx-false-prime` + `test_candidate_disproof_on_executed_counterexample`; arbitrary free-text has no executable predicate |
| 2 | Ambiguous → BLOCKED_BY_INTERPRETATION even with formal/external evidence | DONE | `test_blocked_interpretation_dominates_formal_evidence`/`_external_evidence` |
| 3 | Finite experiment → COMPUTATIONAL_EVIDENCE (not a general proof) | DONE | `fx-true-square` → `COMPUTATIONAL_EVIDENCE` |
| 4 | Known theorem via browser + worker + skeptical review + Lean replay | BLOCKED | needs browser profile + Lean/Mathlib; `RunnerWorker`+referee tested with deterministic runner |
| 5 | Aristotle candidate untrusted until local Lean replay | DONE (logic) | `test_bind_local_replay_only_promotes_on_sealed_attestation`; live Lean BLOCKED |
| 6 | Rate-limited worker waits/checkpoints/resumes | LOGIC | `test_throttle.py`, provider-unavailable retain; live browser BLOCKED |
| 7 | Kill/restart resumes without skip/dup | BLOCKED | durable campaign resume needs the store; single-run event log persists |
| 8 | Five workers, no index lost | PARTIAL | `--workers 1-5` validated; full durable pool BLOCKED |
| 9 | Clean wheel runs an Erdős input outside checkout | DONE | `run --erdos 312 --provider deterministic` from `/tmp` |
| 10 | Malformed/malicious Aristotle artifact rejected | DONE | `test_aristotle_api.py` traversal/symlink/bomb/size tests |
| 11 | PostgreSQL replay reproduces state + head | BLOCKED | no server; protocol conformance + sealing parity tested |
| 12 | doctor distinguishes installed vs operational | DONE | `test_doctor_distinguishes_launcher_from_operational_lean` |
| 13 | Open problem → OPEN_NO_PROGRESS / PARTIAL_PROGRESS | DONE | `egmra run --statement …` → OPEN_NO_PROGRESS |

## Remaining gaps — exact prerequisites to lift BLOCKED ON LIVE ACCEPTANCE

1. **Browser ChatGPT (scenarios 4, 6, 7, 8 live):** an authenticated Chromium
   profile. `pip install -e .[browser] && playwright install chromium`; set
   `CHATGPT_PROFILE_DIR` and log in once; run `egmra run --statement … --provider browser`.
2. **Lean/Mathlib (scenarios 4, 5, 11 formal):** install `elan`/`lean`, build a
   pinned Mathlib project, point `lean_lake_path` at it, and supply an
   `AttestedKernelRunner` producing a sealed `LocalLeanReplayAttestation`.
3. **Aristotle (scenario 5 live):** `ARISTOTLE_API_KEY` + base URL; then
   `HttpAristotleTransport` → `AristotleApiClient` submit/poll/download →
   `bind_local_replay` with the Lean kernel verifier.
4. **PostgreSQL (scenario 11):** a reachable server + `pip install -e .[postgres]`;
   `PostgresEventStore(dsn).connect()` initializes the schema; then replay parity.
5. **Live OEIS / retrieval (§G):** set `oeis_offline=false` + network egress.
6. **Durable 5-worker campaign + kill/restart resume (scenarios 7, 8):** the
   campaign orchestrator over the durable store (checkpoint/resume) is not wired
   into a single `run`; the per-run event log is durable but campaign resume needs
   the store.
7. **Python 3.10 acceptance:** only 3.14 is available locally; CI covers 3.10.

## Files changed this session

- `egmra/orchestrator/result_states.py` — interpretation-first precedence; artifact-gated terminal states; 3.10-safe StrEnum.
- `egmra/lean/aristotle_api.py` — job-id validation, quarantine containment, sealed `LocalLeanReplayAttestation`, URL-encoded/redirect-safe HTTP.
- `egmra/orchestrator/runner_worker.py` (new) — `RunnerWorker`, strict schema parser, `StructuredDemoRunner`.
- `egmra/agents/chatgpt_browser.py` (new) — vendored, self-contained browser glue.
- `egmra/agents/throttle.py` (new) — `SharedThrottle` cross-worker coordinator.
- `egmra/agents/browser_runner.py` — shared throttle, generation-start gate, packaged glue.
- `egmra/cli.py` — `--provider/--role/--workers`, provider builder, provider-unavailable retain, real doctor probes.
- `egmra/m2.py` — `PostgresEventStore` full protocol via shared `seal_event`.
- `egmra/truth/events.py` — extracted shared `seal_event`.
- `egmra/corpus/sources.py` — packaged corpus lookup.
- `egmra/data/*` (new) — packaged corpus snapshot.
- `pyproject.toml` — package-data, `.[dev]`/`.[all]`/`.[postgres]` deps.
- Tests: `test_runner_worker.py`, `test_throttle.py`, `test_m2_postgres_conformance.py` (new); expanded `test_result_states.py`, `test_aristotle_api.py`, `test_cli_arbitrary.py`.
