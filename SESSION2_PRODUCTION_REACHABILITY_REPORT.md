# EGMRA Session-2 Production-Reachability Report

**Status: Implementation complete for the locally exercisable scope. Final
production verification remains BLOCKED-EXTERNAL** on the toolchains/credentials
listed in §4. This report does not claim the whole system is "complete": several
production requirements depend on external services that are not reachable in this
environment, and those paths are implemented + locally exercised but **not**
live-verified here.

All verdicts below are **self-reported and pending independent re-audit**. This
report intentionally does **not** rewrite any verdict cell in
`FABLE_TRACEABILITY_MATRIX.md`; changing an auditor's grade is the auditor's job.

- Test baseline at start of session: **786 passed + 44 subtests**.
- Test suite after this session: **864 passed + 44 subtests** (`python -m pytest
  egmra/tests tests`), exit 0. Net **+78 tests**, no regressions.
- Branch: `audit/egmra-independent-remediation-20260713`. **Not pushed** (no
  operator authorization to push).

---

## 1. What became production-reachable this session

### 1.1 Packaging + installable console command (D-012)
- New `pyproject.toml`: setuptools backend, dynamic version from
  `egmra.__version__`, `requires-python>=3.10` (matches the CI matrix of 3.10 &
  3.12), `[project.scripts] egmra = "egmra.cli:main"`. Core deps are empty
  (stdlib-only core); live adapters are opt-in extras `browser` / `fetch` / `pdf`
  / `dev` / `all`.
- Verify:
  ```bash
  python -m pip install -e .[dev]
  egmra --help
  egmra fixtures
  ```

### 1.2 Arbitrary-problem entry point (D-012)
- `egmra run` now drives the **real** research loop on an arbitrary problem and
  **never calls the fixture loader** on that path:
  - `--erdos N` — resolves the exact statement from the bundled corpus snapshot
    (`all_open_problems.tex` + `problem_catalog.json`) via
    `egmra/corpus/sources.py` (+ vendored exact extractor
    `egmra/corpus/tex_extract.py`, so the installed package is self-contained).
  - `--statement TEXT` / `--statement-file PATH` — arbitrary statements; file
    reads reject symlinks, non-regular files, and oversized payloads.
- `--fixture ID` is retained only as an explicit regression selector.
- Verify (needs a signed policy + the trust keys; see §3):
  ```bash
  egmra --config cfg.json run --erdos 312 --policy signed-policy.json
  egmra --config cfg.json run --statement "Every group of prime order is cyclic." \
        --policy signed-policy.json
  ```

### 1.3 Honest result-state taxonomy (`egmra/orchestrator/result_states.py`)
- `classify_result()` maps a completed run onto ten non-overlapping public states:
  `BLOCKED_BY_INTERPRETATION, OPEN_NO_PROGRESS, PARTIAL_PROGRESS,
  CONDITIONAL_RESULT, COMPUTATIONAL_EVIDENCE, CANDIDATE_PROOF, CANDIDATE_DISPROOF,
  FORMALLY_VERIFIED_CANDIDATE, EXTERNALLY_VALIDATED_SOLUTION,
  EXTERNALLY_VALIDATED_DISPROOF`.
- The classifier **never upgrades**: a locally released/assembled proof is a
  *candidate* (never "externally validated"), and a finite/scoped computation is
  `COMPUTATIONAL_EVIDENCE` (never a general proof). Only **executed** integrity
  probes count, so an inapplicable probe cannot masquerade as an ambiguity.
- Observed on real inputs:
  | Input | Public state |
  |---|---|
  | `fx-true-square` (finite exact check) | `COMPUTATIONAL_EVIDENCE` |
  | `fx-false-prime` (counterexample probe fires) | `CANDIDATE_DISPROOF` |
  | Erdős #312 / #1 (independent parsers disagree on dense LaTeX) | `BLOCKED_BY_INTERPRETATION` |
  | Parser-agreed unsolved statement | `OPEN_NO_PROGRESS` |

### 1.4 Operator diagnostics
- `egmra doctor` — readiness report: Python version, optional deps, executables
  (via PATH lookup only), signing-key presence (**booleans only, never values**),
  policy loadability, corpus presence, and a `ready_for` summary. Verify:
  `egmra doctor`.
- `egmra status` — inventories persisted runs in the events directory with event
  counts and integrity. Verify: `egmra status`.

### 1.5 Browser ChatGPT model runner — primary informal provider (D-013)
- `egmra/agents/browser_runner.py`: `BrowserChatGPTRunner` implements the
  `ModelRunner` protocol over an injectable `BrowserBackend`. Responses carry an
  **unattested** identity (`attested=False`) and can never be independent-model
  evidence. Fresh isolated conversation per call; records model label, conversation
  URL, account class, timestamp, prompt/response hashes, runner version. Rate
  limiting pauses with backoff **clamped to ≤120s** and never fails the math
  problem; persistent throttle raises `BrowserProviderUnavailable` (transient).
- The live backend `PlaywrightChatGPTBackend` wraps `erdos_common`.

### 1.6 Aristotle API client — allowed, never a trust root (D-014)
- `egmra/lean/aristotle_api.py`: `AristotleApiClient` over an injectable
  `AristotleTransport`. `submit` enforces the licensing gate before any packet
  leaves the host; a vendor `COMPLETE`/`solved` status **always** carries
  `promotable=False`; `download` extracts returned Lean into a per-job quarantine
  with a hardened extractor (rejects absolute paths, `..` traversal,
  symlinks/hardlinks/special files, oversized entries, and archive bombs);
  `bind_local_replay` gives the only trust decision to a caller-supplied local
  verifier. The existing `aristotle_verifier.py` CLI wrapper is retained as a
  fallback.

---

## 2. Local test evidence

```bash
python -m pytest egmra/tests tests            # 864 passed, 44 subtests, exit 0
python -m pytest egmra/tests/test_result_states.py \
                egmra/tests/test_corpus_sources.py \
                egmra/tests/test_cli_arbitrary.py \
                egmra/tests/test_browser_runner.py \
                egmra/tests/test_aristotle_api.py
```

New test modules: `test_result_states.py` (all 10 states), `test_corpus_sources.py`
(erdos/statement/file + traversal/symlink/oversize rejection),
`test_cli_arbitrary.py` (arbitrary run / doctor / status, no-secret-leak),
`test_browser_runner.py` (isolation, ≤120s cooldown, malformed retry, provider
outage), `test_aristotle_api.py` (submit/poll/download/quarantine + hardened
archive intake + "vendor COMPLETE never promotes").

---

## 3. Minimal local activation (no external services)

```bash
python -m pip install -e .[dev]
# process-local trust keys (see egmra/tests/conftest.py for the full set)
export EGMRA_EVENT_KEY=... EGMRA_EVIDENCE_KEY=... EGMRA_GATE_KEY=... \
       EGMRA_TRUTH_SNAPSHOT_KEY=... EGMRA_AUTHORITY_KEY=... EGMRA_POLICY_KEY=... # etc.
printf '{"flags":{"claim_graph":true,"literature_retrieval":true,"computation_service":true,"promotion":false}}' > tmpl.json
egmra policy-sign --input tmpl.json --output signed-policy.json
printf '{"events_dir":"runs"}' > cfg.json
egmra --config cfg.json run --erdos 312 --policy signed-policy.json
egmra doctor
```

---

## 4. BLOCKED-EXTERNAL — final production verification not performed here

Each item below is implemented as a real interface with local/fake tests and a
documented activation path; the **live** path is not claimed verified in this
environment.

1. **Lean / Mathlib formal verification** (`egmra/lean/service.py`, `harden.py`).
   Activate: install `elan`/`lean`, build a pinned Mathlib project (`lake build`),
   set `lean_lake_path` in config, and supply a real `AttestedKernelRunner`.
   Verify: run the L0–L5 pipeline and confirm a `FormalCertificate` verifies under
   the pinned checker. (`egmra doctor` reports the `lake`/`lean` binaries but not
   an end-to-end proof.)
2. **Aristotle API** (`egmra/lean/aristotle_api.py`). Activate:
   `export ARISTOTLE_API_KEY=...`; use
   `HttpAristotleTransport(base_url="https://<host>")` with `AristotleApiClient`.
   Verify: `submit → poll → download`, then `bind_local_replay` with the pinned
   Lean kernel verifier; confirm a vendor `COMPLETE` yields no promotion until the
   local replay passes.
3. **Browser ChatGPT** (`egmra/agents/browser_runner.py`). Activate:
   `pip install -e .[browser] && playwright install chromium`; create an
   authenticated profile (`python3 solve_submit.py --login`); build
   `PlaywrightChatGPTBackend().start()` and pass
   `runner=BrowserChatGPTRunner(backend=...)` to `research(...)`. Verify: a live
   `run` records a conversation URL with `attested=False`.
4. **PostgreSQL event store** (D-005). Activate: provision Postgres and configure
   the `PostgresEventStore` backend. Verify: replay parity with the JSONL log.
5. **Docker/OCI compute sandbox** (D-008). Activate: provide a compatible OCI
   runtime. Verify: exact-computation replay in an independent container.
6. **Live OEIS / literature retrieval** (D-004). Activate: set `oeis_offline=false`
   and provide network egress. Verify: a live OEIS lookup and a real retrieval
   corpus.

---

## 5. Operator notes
- **Not pushed to GitHub.** No push/PR was performed; awaiting explicit operator
  authorization.
- The worktree contains pre-existing modifications from the prior audit and a
  problem-312 run; those were left untouched.
