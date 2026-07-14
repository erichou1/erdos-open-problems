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

> ## Session update (retrieval/OEIS + Postgres CLI wiring — defects 4.4, 4.9)
> - **Defect 4.4 (live retrieval + OEIS not wired into the CLI) — FIXED.** Added [egmra/retrieval/erdos_corpus.py](egmra/retrieval/erdos_corpus.py) `build_erdos_corpus()`, which parses the packaged Erdős TeX snapshot into **auditable `TheoremRecord`s** — each carries `source_uri` (`https://www.erdosproblems.com/N`), a sha256 content hash, and a verbatim statement extract, and is deduped by problem number. The CLI `run`/`campaign` now build the retrieval corpus (`--retrieval corpus|none`) and an `OEISClient` (`--oeis auto|offline|live`) and pass **both** into `research()` via the existing `retrieval_corpus`/`oeis_client` params, so the `RetrievalService` freezes a **provenance-bearing solver packet** for the worker after the blind cold pass and the OEIS integer-sequence stage is reachable. An OEIS/retrieval match seeds conjectures only — it **never** promotes proof status (enforced by the `ImportAuditor` exact-consequence check and the separate novelty query log). Live: `egmra run --erdos 1 --retrieval corpus` reported `retrieval.corpus_records=613`.
> - **Defect 4.9 (`--event-store postgres` not wired) — FIXED.** `PostgresEventStore` ([egmra/m2.py](egmra/m2.py)) is now a full `EventLog` drop-in — reused connection, `events` property, `__len__`, `last_event_id`, `close`, `migrate` — consumed by `research()` through a new additive `event_log=` injection (JSONL stays the default). The CLI adds `--event-store jsonl|postgres` + `--dsn` (DSN from `--dsn` or `EGMRA_POSTGRES_DSN`, **never logged**; only a credential-redacted DSN is printed), the `egmra init-db` / `egmra migrate-db` subcommands (idempotent schema), and `egmra verify-events --event-store postgres`.
> - **Live durability bug found-and-fixed by acceptance.** On a disposable `postgres:16`, the first `verify-events` after a run showed **0 events** even though the run reported success: reusing a **non-autocommit** connection left the initial `COUNT`'s implicit transaction open, so each subsequent `append()`'s `transaction()` became a **savepoint** inside it that was discarded when the reused connection closed. Fixed by switching the reused connection to **autocommit** so every append is a durable top-level `BEGIN`/`COMMIT` and reads never leave a lingering transaction.
> - **Live Postgres acceptance (scenario 11) — VERIFIED.** Disposable `postgres:16` on port **5433** (the operator's own `:5432` untouched): `init-db` created the `events` table (`UNIQUE(run_id,sequence)`); `egmra run --event-store postgres` persisted the research chain (2 rows, seq 0..1); a **fresh process** `egmra verify-events --event-store postgres` reconnected + replayed with `integrity: true` and reproduced the merkle head; the gated live pytest suite proves append/len/events, reconnect+replay-merkle parity, **transaction rollback leaves no partial write**, and out-of-band payload **tamper → `verify_integrity: false`**. Container torn down after.
> - Full suite: **960 passed**, rc=0 (3 live-Postgres tests run when `EGMRA_TEST_POSTGRES_DSN` is set; else they skip → 957 passed, 3 skipped, rc=0).
> - **Still not done** (verdict remains INCOMPLETE): compute-execution wiring (4.5), `LeanService`-into-`run` + live kernel (4.6), `--formalizer` flag (4.7), durable browser transcript artifacts (4.10), distinct-role allocation (4.11); and live scenarios 4 (authenticated browser + built Mathlib kernel) and 5 (live Aristotle key + built Lean project) remain **BLOCKED_EXTERNAL**.

> ## Session update (live Aristotle round-trip + pinned Lean kernel built)
> - **Pinned Lean kernel BUILT + operational.** `aristotle_lean_project` built with Lean v4.28.0 + Mathlib v4.28.0 (`lake build` rc=0, 8027 jobs). Verified it checks a *real* Mathlib theorem (`n + 0 = n ∧ Nat.Prime 7`) and extracts the axiom closure `[propext, Classical.choice, Quot.sound]` (within the whitelist). This lifts the toolchain prerequisite for scenarios 4 and 5.
> - **Live Aristotle round-trip VERIFIED against the real service** (operator-provided key, stored only in the gitignored `egmra.keys.sh`). `submit → poll (queued→in_progress→complete, ~5 min) → download`; Aristotle produced `theorem egmra_live_check : 2 + 2 = 4 := rfl`; the adapter safe-extracted the vendor tar.gz into a hardened quarantine (`promotable=false`), and the produced Lean was **re-checked by the local pinned kernel** (`lake env lean`, rc=0). Scenario 5 is now **PARTIAL** (live round-trip + local kernel verification done; the sealed attestation is the remaining step).
> - **Two real SDK-adapter bugs found-and-fixed by the live run** (the sync test fake had hidden both):
>   - *Async:* the official `aristotlelib` SDK is fully async (every `Project`/`AgentTask` method is a coroutine); `AristotleSdkClient` called them synchronously. Fixed to drive coroutines on a persistent client-owned event loop; added an async-fake regression test.
>   - *Archive fetch:* the real `get_files(destination)` writes a single `tar.gz` blob to a **file** path (not a directory) — the adapter passed a directory and hit `IsADirectoryError`. Fixed to download to a temp file then `safe_extract_archive` into the quarantine under strict traversal/symlink/bomb limits; both fakes updated to emit a real `tar.gz`.
> - **Remaining for a *sealed* result (scenarios 4 & 5).** The `AttestedKernelRunner` attestation needs interface work: `CheckerRequest` carries only hashes (no source path), and there is no canonical elaborated-type-hash Lean helper, so a *sound* production checker (binding `candidate_type_hash == expected_type_hash`) is not yet shippable. Local kernel verification is real; the sealed promotion ceremony is scoped but not done — not faked.
> - Full suite: **961 passed**, rc=0.

> ## Session update (sealed local Lean kernel checker — scenario 5 PASS)
> - **The sealed-attestation gap is closed.** Added `source_root` + `expected_type_source` to `CheckerRequest` (threaded through `LeanReplayTarget`/`LeanReplayVerifier`) and a real pinned checker, [egmra/lean/kernel_checker.py](egmra/lean/kernel_checker.py): it verifies the candidate tree hashes to `source_hash`, rejects `sorry`/`native_decide`, runs the **real Lean kernel** via `lake env lean` on a **definitional obligation** (`example : <expected_type> := @<declaration>`) plus a `#print axioms` audit, and computes `candidate_type_hash` from the exact intended type (no blind echo) so `verify_for`'s `candidate_type_hash == expected_type_hash` is sound. `write_pinned_checker` pins the checker (embedding the EGMRA-capable interpreter, not a bare `/usr/bin/env python3`).
> - **LIVE sealed attestation.** The real kernel sealed a `LocalLeanReplayAttestation` for Aristotle's `egmra_live_check : 2 + 2 = 4 := rfl` (claim `goal`, Lean 4.28.0, Mathlib v4.28.0, bound to the source-tree hash). The full chain — submit → poll → download → safe-extract (`promotable=false`) → **sealed local replay** — is live-verified. **Scenario 5 → PASS.**
> - **CLI reachability.** New `egmra formalize --formalizer local|aristotle --declaration NAME --expected-type "T"` re-checks a candidate (local file or live Aristotle) with the pinned kernel and prints the sealed attestation or an honest rejection; it fails clearly if the project is not built or the checker key is unset.
> - **Tests.** 11 hermetic checker tests (injected fake `lake`): pass path, `sorry`/native/hash-mismatch/kernel-failure/missing-declaration rejections, axiom-whitelist flagging, end-to-end seal through `AttestedKernelRunner` + `verify_for` + `LeanReplayVerifier`, and the soundness property that tampering the expected type breaks the hash binding.
> - **Scenario 4** (browser → Lean) is no longer blocked on the checker; only wiring a browser-produced Lean proof through the formal path remains.

> ## Session update (production wiring — defects 4.11, 4.10, 4.5)
> - **4.11 — distinct per-branch worker roles.** `research()` assigns a method-specific role per mechanism branch (`WORKER_ROLE_BY_FAMILY`: prover / experimentalist / formalizer), records it in each branch's `mechanism_fingerprint` and memory, and drives the worker via `RunnerWorker.for_role()` so the prompt is role-specific. Branches already carried distinct fingerprints, posteriors, and read-slices; role is the added allocation dimension.
> - **4.10 — durable content-addressed model-exchange artifacts + signed events.** New `MODEL_EXCHANGE_RECORDED` action + `_record_model_exchanges()`: given an artifact store (the CLI now builds a `ContentAddressedObjectStore`), `research()` persists each model/browser exchange's provenance (never raw response text) to the content-addressed store and appends a signed event referencing the artifact hash — so the informal reasoning that produced claims is tamper-evident.
> - **4.5 — model-proposed finite experiments executed in the trusted sandbox.** `RunnerWorker` accepts an optional capability-free `experiment(inputs)` and runs it via a shared `_execute_finite_experiment()` in the ComputeService's hardened RestrictedPython/container sandbox; `research()` re-authenticates the artifact + independent replay against the worker's own service. A finite check reaches at most **COMPUTATIONAL_EVIDENCE** (admitted `exact_computation` evidence) and never proves a general claim — the sound boundary is enforced and tested.
> - Tests: `egmra/tests/test_production_wiring.py` (9). Full suite: **981 passed**, rc=0.
> - Remaining: 4.1 (full typed worker-output schema) and 4.6 (emit `formal_candidates` from the worker so the browser→Lean formal-candidate path fires inside `egmra run`; the sealed checker itself is done).

> ## Session update (typed worker schema + formal-candidate path in `egmra run` — 4.1, 4.6)
> - **4.1 — full typed worker-output schema.** `parse_worker_response` now captures `proof_steps`, `assumptions`, `formalization_requests`, and `lean_declaration_candidates` (`{claim_id, declaration_name, source, expected_type}`) alongside the existing fields; incomplete Lean candidates are dropped (never a fabricated formal artifact). `branch_prompt` requests the full schema.
> - **4.6 — formal-candidate path wired into `egmra run`.** `RunnerWorker` converts `lean_declaration_candidates` into `WorkerOutput.formal_candidates`, computing every hash **deterministically** — `expected_type_hash` is the canonical hash the pinned kernel checker recomputes (so `candidate_type_hash == expected_type_hash` is sound), and `project_hash`/`immutable_target_module_hash` are derived, never model-trusted. `egmra run --lean-project <built>` builds a real `LeanService` whose kernel runner is the pinned checker; `LeanService.verify_declaration` writes the candidate into a hardened quarantine and binds `source_root` so the **real Lean kernel** (`lake env lean`) re-checks the declaration. `DeterministicWorker`/existing callers are unaffected (the bridge only activates with a configured `lean_project` + an `AttestedKernelRunner`).
> - **Trust boundary preserved.** A kernel-verified declaration is still **not** admitted as a formal proof of the *informal* claim without an independently signed formal-correspondence review (`egmra run` records `formal_correspondence_required` otherwise) — tested.
> - Tests: 4 more in `egmra/tests/test_production_wiring.py`. Full suite: **985 passed**, rc=0. All enumerated code defects **4.1–4.11 are addressed**; scenario 4's full browser→Lean→`FORMALLY_VERIFIED_CANDIDATE` chain still needs a live authenticated browser emitting valid Lean **and** a signed formal-correspondence review, so the verdict stays **INCOMPLETE**.
>
> ## Session update (formal-correspondence review consumed by `egmra run` — 4.6-correspondence)
> - **`egmra run --formal-correspondence-review [CLAIM_ID=]PATH`** (repeatable; `CLAIM_ID` defaults to `goal`) + `_load_formal_correspondence_reviews()`, mirroring `--intent-review`: it loads signed `FormalCorrespondenceCertificate` JSON artifacts (regular non-symlink file, ≤1 MB, no duplicate JSON keys, no duplicate claim) and hands them to `research()` as the claim-keyed `formal_correspondence_reviews` mapping.
> - **Independence boundary kept.** Signing stays **out-of-band** in the independent review domain (`sign_formal_correspondence_certificate`, already present); the CLI only *consumes*, and the orchestrator *re-verifies* the signature. A signed review must bind the intent certificate, the informal-claim hash, the Lean declaration name, and the elaborated type.
> - **Verified end-to-end through `research()`:** a CLI-loaded signed review discharges the `formal_correspondence_required` blocker and admits the kernel-verified declaration as a **claim-bound `KERNEL_CHECKED`** formal proof of the informal claim (goal `SUPPORTED`, `formal_verification=KERNEL_CHECKED`, correspondence certificate bound). Without it, the axis stays unset (contrast tested).
> - **What this does NOT do:** it does not bypass the **independent adversarial referee** (all 10 required attacks complete + no defects + model-family/replay independence), which remains the real gate to the *public* `FORMALLY_VERIFIED_CANDIDATE` state and which a single mock checker deliberately cannot fake. So the flag closes the formal-correspondence gap but the live scenario 4 still needs a real diverse verification.
> - Tests: 6 in `egmra/tests/test_cli_arbitrary.py` (loader parse/default-claim/symlink/oversize/duplicate + wiring-through/none) + 1 full-chain in `egmra/tests/test_production_wiring.py`. Full suite: **990 passed, 3 skipped**, rc=0. Verdict remains **INCOMPLETE**.
>
> ## Session update (fresh-audit follow-up — lease heartbeat, OEIS array, formal-audit wiring, worker schema)
> - **Branch lease heartbeat (largest end-to-end blocker).** A live browser run made 12 genuine exchanges across 3 branches, then discarded every one as `stale_worker_rejected:<branch>:lease has expired`: the 60 s branch lease had no heartbeat and the fence is checked only *after* the worker returns, so browser reasoning >60 s was rejected as stale. Fix: `loop._lease_heartbeat()` renews the lease every 20 s (< the 60 s grace) on a daemon thread while `work_branch()` runs; if the branch is legitimately superseded the renewal fails closed and the post-return fence check still rejects the stale batch (liveness extended, safety unchanged).
> - **Live OEIS parser.** OEIS now returns a bare top-level JSON array; the client required an object with `results`. `OEISClient._parse_response` now normalizes an array to `{"results": [...]}` (object form preserved), so live + cached paths share one shape.
> - **Referee `formal_audit` + formal-mode wiring.** `formal_audit` tested `informal_only` (so a genuine formal run always failed it). It now passes when the run is informal-only OR the graph holds a valid Lean/ATP proof bound to a formal-correspondence certificate (a real kernel artifact). `egmra run` now sets `informal_only=False` when `--lean-project` is configured.
> - **Typed schema consumed.** `WorkerOutput` gained `proof_steps`/`assumptions`/`formalization_requests`; `RunnerWorker` populates them and `research()` records them in the durable per-branch memory (no longer parsed-then-dropped). Deeper claim-graph semantics remain future work.
> - Tests: 8 more (3 lease-heartbeat + 1 worker-schema in `test_production_wiring.py`, 2 OEIS in `test_oeis.py`, 2 `informal_only` in `test_cli_arbitrary.py`) + formal_audit assertions in the full-chain test. Full suite: **998 passed, 3 skipped**, rc=0.
> - **Still open (honest, verdict INCOMPLETE):** real async multi-tab browser workers; autonomous Aristotle invocation inside `egmra run`/campaigns; production scholarly/theorem-library retrieval; mid-generation rate-limit detection; DB-backed campaign leases; and a LIVE browser→Lean→`FORMALLY_VERIFIED_CANDIDATE` run (the referee still requires a genuine diverse verification — executable countermodel + independent replay — which a single mock/one-model run cannot fake).
>
> ## Session update (async multi-tab browser workers — audit #3)
> - **Genuine multi-tab concurrency.** New `egmra/agents/async_browser.py` drives ONE authenticated Chromium via the **async** Playwright API on a dedicated event-loop thread with a POOL of N pages. `AsyncBrowserEngine` marshals each worker thread's synchronous `BrowserBackend` call onto the shared loop with `asyncio.run_coroutine_threadsafe`, so N tabs make genuine concurrent progress on one account (the `SharedThrottle` still coordinates cooldowns). `TabBackend` binds one page per worker; `build_browser_runner_pool` builds one `BrowserChatGPTRunner` per tab.
> - **Campaign wiring.** `egmra campaign --provider browser --workers N` now builds the engine + pool and gives each worker its own tab; the old `--workers 1` browser cap is removed and the engine is torn down after the run. `egmra run` stays single-problem-sequential (a single problem's branches are researched in order), so multi-tab overlap is a campaign feature (run `--workers` help clarified).
> - **Testing posture.** The per-page DOM ops sit behind the async `AsyncPageDriver` seam; the live `PlaywrightAsyncPageDriver` is a faithful async port of the sync `chatgpt_browser` helpers, verified live (never in CI) — the same posture as the sync backend. Hermetically proven with a fake driver: an `asyncio.Barrier` shows all N tabs run simultaneously on the shared loop, and a 2-worker browser campaign assigns two distinct tab-runners with both workers forced active at once.
> - Tests: +8 (6 in `egmra/tests/test_async_browser.py`, 2 campaign-wiring in `egmra/tests/test_cli_arbitrary.py`). Full suite: **1006 passed, 3 skipped**, rc=0.
> - **Still open (honest, verdict INCOMPLETE):** autonomous Aristotle invocation inside `egmra run`/campaigns; production scholarly/theorem-library retrieval; mid-generation rate-limit detection; DB-backed campaign leases; and a LIVE browser→Lean→`FORMALLY_VERIFIED_CANDIDATE` run.
>
> ## Session update (autonomous Aristotle formalization worker — audit #5)
> - **Aristotle integrated into `egmra run`.** New `egmra/lean/formalizer.py` adds a `Formalizer` seam + `AristotleFormalizer` that turns a **pinned** obligation (declaration name + intended Lean type) into candidate Lean **source** via the Aristotle SDK (submit → fetch → read the quarantined `.lean`). `egmra run --formalizer aristotle` (requires `--lean-project` + `ARISTOTLE_API_KEY`) builds it and hands it to the `RunnerWorker`.
> - **Sound division of labor.** `parse_worker_response` now makes the proof `source` optional (a source-less `lean_declaration_candidate` is a *pinned formalization request*, still requiring `declaration_name` + `expected_type`). When a formalizer is configured, the **vendor produces the proof** while the **obligation stays pinned + deterministically hashed** by us; the produced Lean is UNTRUSTED and re-checked by the pinned kernel on the existing 4.6 path. A vendor `COMPLETE` never promotes on its own, and a formal-correspondence review is still required to prove the informal claim. A formalizer outage is recorded (`formalizer_error`/`formalization_unavailable`), never a mathematical failure.
> - **Testing posture.** The live SDK path is verified live (never in CI), like `egmra formalize`. Hermetically proven with a fake SDK client + fake formalizer: the prompt pins the exact obligation; a source-less candidate is filled by the formalizer (obligation hash still ours); no formalizer → nothing fabricated; an outage is recorded. Campaign wiring is the analogous follow-up.
> - Tests: +10 (4 in `egmra/tests/test_formalizer.py`, 3 worker-integration in `egmra/tests/test_production_wiring.py`, 3 CLI-wiring in `egmra/tests/test_cli_arbitrary.py`). Full suite: **1016 passed, 3 skipped**, rc=0.
> - **Campaign wiring (follow-up).** `egmra campaign --formalizer aristotle` now builds ONE `AristotleFormalizer` per worker (each with its own SDK client/event loop — the client is single-loop and not shared across worker threads) via `_build_worker_formalizers`, plus a shared pinned-kernel `LeanService`; each worker's `RunnerWorker` gets its own formalizer + the pinned Lean env, and every formalizer is closed after the run. +4 tests. Full suite: **1020 passed, 3 skipped**, rc=0.
> - **Still open (honest, verdict INCOMPLETE):** production scholarly/theorem-library retrieval; mid-generation rate-limit detection; DB-backed campaign leases; and a LIVE browser→Lean→`FORMALLY_VERIFIED_CANDIDATE` run.
>
> ## Session update (production scholarly / theorem-library retrieval — audit #7)
> - **Live scholarly retrieval.** New `egmra/retrieval/scholarly.py` adds a `ScholarlyRetriever` seam + live **arXiv** (Atom XML, keyless) and **Crossref** (JSON, keyless) backends behind an injectable `Fetcher`, plus `build_scholarly_corpus()` which merges/dedups auditable `TheoremRecord`s (source URI + stable version + sha256 content hash + verbatim extract). `egmra run --retrieval arxiv|crossref|scholarly` performs LIVE, query-specific retrieval on the problem statement.
> - **Security.** The packaged `UrllibFetcher` is confined to an allowlisted host set (`export.arxiv.org` / `api.crossref.org`), http(s) only, with a timeout + response-size cap; no user-supplied URL is ever fetched. XML parsing refuses DTDs/entities (blocks billion-laughs / external-entity vectors); Crossref JATS tags are stripped.
> - **Trust boundary preserved.** Every record is `proof_status="unknown"` + `independent_verification_status="unverified"` and seeds hypotheses/queries only — it can never establish proof status (the `ImportAuditor` enforces this). A per-source outage is skipped (other sources still contribute); an empty query yields an honest empty packet.
> - **Extensible + honest scope.** The `ScholarlyRetriever` seam makes Semantic Scholar / MathOverflow / a citation graph pluggable follow-ons; campaign-side (per-problem) scholarly retrieval is a follow-up. The live network fetch is verified live (never in CI); parsing/record construction is fully tested with canned payloads.
> - Tests: +9 (8 in `egmra/tests/test_scholarly.py`, 1 CLI in `egmra/tests/test_cli_arbitrary.py`). Full suite: **1029 passed, 3 skipped**, rc=0.
> - **Still open (honest, verdict INCOMPLETE):** additional scholarly backends + campaign-side retrieval; mid-generation rate-limit detection; DB-backed campaign leases; and a LIVE browser→Lean→`FORMALLY_VERIFIED_CANDIDATE` run.
>
> ## Session update (mid-generation rate-limit detection + DB-backed campaign leases)
> - **Mid-generation rate-limit detection.** `BrowserChatGPTRunner` only checked for a throttle *before* submitting; a rate limit that surfaced *during* generation (a modal, or a throttle message returned as the response body) was not detected. `run()` now re-checks `is_rate_limited()` **after** `wait_response` and, on a mid-generation throttle, takes a bounded cooldown via a shared `_pause_once()` budget and retries — the throttle text is never returned as a mathematical answer and is never counted as a malformed-response retry. Pre-submission and mid-generation cooldowns share **one** budget, so a run can never exceed `max_rate_limit_pauses`; exhausting it raises `BrowserProviderUnavailable` (a transient outage the caller retains/resumes), never a math failure.
> - **DB-backed campaign leases.** Campaign state I/O is now behind a pluggable `CampaignStore` seam. `FileCampaignStore` (default) keeps the signed-JSON file + OS advisory lock; new `PostgresCampaignStore` persists the signed state in one row (canonical JSON **text**, never JSONB, so the tamper-evident signature is verified against the exact stored bytes) and uses `pg_advisory_lock` for **cross-process/host** mutual exclusion — leases/checkpoints coordinated across every worker sharing the DB, not just a local file. `egmra campaign --state-store postgres` selects it; the store is closed after the run. Same signing key + `CampaignError` fail-closed contract for both backends.
> - **Testing posture.** Mid-generation throttle handling is fully hermetic (fake backends: detect+retry, persistent→provider-unavailable, shared-budget). The campaign store seam is exercised end-to-end by an in-memory store (lifecycle + resume + tamper); the Postgres SQL is verified live (gated on `EGMRA_TEST_POSTGRES_DSN`).
> - Tests: +11 (3 mid-generation in `test_browser_runner.py`, 8 in `test_campaign_store.py` incl. 1 live-gated). Full suite: **1040 passed, 4 skipped**, rc=0.
> - **Only remaining audit item (honest, verdict INCOMPLETE):** a LIVE browser→Lean→`FORMALLY_VERIFIED_CANDIDATE` run — the independent adversarial referee still gates on a genuine diverse verification (executable countermodel + independent replay) that a single mock/one-model run cannot fake. Pluggable follow-ons: more scholarly backends + campaign-side scholarly retrieval.
>
> ## Session update (scenario-4 capability proof + scholarly follow-ons)
> - **Scenario 4 — capability hermetically demonstrated (no faking).** The FULL chain now reaches the public `FORMALLY_VERIFIED_CANDIDATE` state with a **genuinely-passing** adversarial referee: a real executable countermodel search (from the contract predicate) + a real independent computation replay (executed in the compute sandbox) + a kernel-checked formal candidate + a signed formal-correspondence review. All ten required attacks pass with **no faked result** (`test_full_verification_reaches_formally_verified_candidate`), gates reach T4/I2/F2. This proves the referee gate is satisfiable by **genuine work**, not a mock/one-model run. The ONLY remaining piece is a LIVE run — a real authenticated browser emitting valid Lean + the real `lake env lean` kernel (a fake attested checker stands in for the kernel in the hermetic test, exactly as in every formal test).
> - **Scholarly follow-ons.** Extended the `ScholarlyRetriever` seam with **Semantic Scholar** (graph API) and **MathOverflow** (StackExchange API; the live `UrllibFetcher` now gunzips StackExchange's always-gzipped responses). `--retrieval` (run + campaign) gained `semanticscholar`/`mathoverflow`, and `scholarly` now merges all four sources (dedup + per-source-outage skip). **Campaign-side** scholarly retrieval is now query-specific **per problem** (rebuilt in `run_one`). Both new records are `proof_status=unknown`/unverified (seed hypotheses only); MathOverflow HTML is tag-stripped; the host allowlist adds `api.semanticscholar.org`/`api.stackexchange.com`. Citation-graph retrieval remains a pluggable follow-on.
> - Tests: +6 (1 scenario-4 e2e in `test_production_wiring.py`, 4 backend/merge in `test_scholarly.py`, 1 campaign scholarly in `test_cli_arbitrary.py`). Full suite: **1046 passed, 4 skipped**, rc=0.
> - **Only remaining audit item (honest, verdict INCOMPLETE):** a LIVE browser→Lean→`FORMALLY_VERIFIED_CANDIDATE` run (real browser + real Lean kernel); plus citation-graph retrieval as a pluggable follow-on.
>
> ## Session update (live scenario-4 scaffolding — `run --predicate` + `sign-review` CLI)
> - **The arbitrary/browser path gets an executable countermodel.** Previously only the *fixture* path supplied a probe predicate, so on a real `egmra run --erdos/--statement` the `counterexample_search` probe stayed non-executable and the referee's `countermodel_search` attack (which requires an executable search that **passed**) could never pass live. New `egmra run --predicate '<expr over n>'` compiles an operator predicate and feeds it to the intake probes, so the arbitrary/browser path now has a genuine executable countermodel search.
> - **The predicate is not arbitrary code.** New `egmra/intake/predicate.py` parses the expression to an AST and rejects anything outside a numeric-expression whitelist — no imports, attribute access, subscripting, lambdas, f-strings, or non-builtin calls — which structurally closes the `().__class__…` sandbox escapes; it compiles once and evaluates with an **empty `__builtins__`** plus a fixed set of pure numeric helpers (`abs/min/max/pow/int/bool/len/sum/all/any/range/divmod`). A malformed/unsafe predicate is rejected *before* the run starts (rc 2), never mid-run.
> - **`sign-review` produces the signed review artifacts a live run consumes.** New `egmra sign-review intent` and `egmra sign-review correspondence` sign the intent/formal-correspondence certificates with the review keys (via the existing `sign_intent_certificate` / `sign_formal_correspondence_certificate`). `intent` resolves the problem exactly as `research()` does and binds the source-bytes / interpretation / informal-claim hashes; `correspondence` reads the signed intent artifact for its certificate id + informal-claim hash and binds the Lean declaration name + `elaborated_type_hash(expected_type)`. Both write **mode-0600** files that refuse to overwrite (mirroring `policy-sign`).
> - **Honest by construction.** `sign-review` records a genuine key-holder's verdict and asserts the reviewer's methods/independence — it does **not** manufacture independence. An operator holding all keys is a self-review, and every `sign-review` invocation says so in its output note. It signs; it does not review.
> - **Testing posture.** Fully hermetic. The predicate compiler is unit-tested (numeric eval, comprehension-scope binding, unsafe-construct + oversize rejection); `run --predicate` wiring is tested (good run rc 0, unsafe predicate rc 2); `sign-review` artifacts are shown to verify, bind, be 0600, and refuse overwrite. An **end-to-end** test drives artifacts produced ONLY through the `sign-review` CLI (with CLI-computed hashes) + a `--predicate`-compiled countermodel through `research()` to a claim-bound **kernel-checked** formal proof (goal `SUPPORTED`).
> - Tests: +25 in `egmra/tests/test_sign_review_cli.py`. Full suite: **1071 passed, 4 skipped**, rc=0.
> - **Only remaining audit item (honest, verdict INCOMPLETE):** the LIVE scenario-4 run is now purely operational — point the (now-complete) scaffolding at a live authenticated browser emitting valid Lean + a built `--lean-project` (real `lake env lean`) and let the genuine adversarial referee observe the passing verification. Pluggable follow-on: citation-graph retrieval.






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
| 11 | PostgreSQL replay reproduces state + head | DONE (live) | `--event-store postgres` live on disposable `postgres:16`: append/reconnect/replay/rollback/tamper; merkle head reproduced |
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
4. **PostgreSQL (scenario 11):** DONE — `--event-store postgres` + `init-db`/`migrate-db`
   are wired and live-verified on a disposable `postgres:16` (append/reconnect/replay/
   rollback/tamper). `pip install -e .[postgres]`; DSN via `EGMRA_POSTGRES_DSN`.
5. **Live OEIS network fetch (§G):** retrieval-with-provenance and the OEIS client are
   wired into the CLI (offline path live-verified); only a live `oeis.org` network fetch
   (`--oeis live`, needs egress) was not exercised this session.
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
- `egmra/cli.py` — `--provider/--role/--workers`, provider builder, provider-unavailable retain, real doctor probes; `--event-store jsonl|postgres` + `--dsn`, `init-db`/`migrate-db`, `--retrieval`/`--oeis` wiring, `verify-events --event-store postgres`.
- `egmra/m2.py` — `PostgresEventStore` full `EventLog` drop-in (reused **autocommit** connection, `events`/`__len__`/`last_event_id`/`close`/`migrate`) via shared `seal_event`.
- `egmra/orchestrator/loop.py` — additive `event_log=` injection into `research()` (JSONL default; Postgres when supplied).
- `egmra/retrieval/erdos_corpus.py` (new) — `build_erdos_corpus()` builds auditable `TheoremRecord`s (source URI, content hash, verbatim extract) from the packaged corpus.
- `egmra/truth/events.py` — extracted shared `seal_event`.
- `egmra/corpus/sources.py` — packaged corpus lookup.
- `egmra/data/*` (new) — packaged corpus snapshot.
- `pyproject.toml` — package-data, `.[dev]`/`.[all]`/`.[postgres]` deps.
- Tests: `test_runner_worker.py`, `test_throttle.py`, `test_m2_postgres_conformance.py` (10 no-server + 3 live gated), `test_erdos_corpus.py` (new); expanded `test_result_states.py`, `test_aristotle_api.py`, `test_cli.py` (retrieval/OEIS + Postgres CLI wiring).
