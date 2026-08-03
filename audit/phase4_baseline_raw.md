# Phase 4 pre-fix baseline — raw independent verification

## Result summary

The documented legacy CI surface is green, but it does **not** execute the EGMRA test suite. The checkout's declared dependencies cannot import 16 of the 21 EGMRA test modules because `pytest` is undeclared; after installing `pytest` only in a temporary environment, `unittest` still discovers zero EGMRA tests because they are pytest-style functions. An audit-only pytest run collected and passed 420 items (179 legacy plus 241 EGMRA), with no skips or warnings, but direct execution of every bundled EGMRA CLI fixture exposed two production-path inconsistencies that the green suite does not cover:

1. `fx-true-even-sum` is declared `verified` but returns `honest_triage_report` with `proof_complete: true` and exit 0.
2. `fx-true-square` has a `release_blocked` problem contract because its two parsers disagree, yet the CLI emits a signed release certificate and labels the result `verified_finite_or_conditional_result` with intent gate `I0`.

This is a raw pre-fix baseline, not a final implementation verdict. `FABLE_BASELINE_VERIFICATION.md` was not used as evidence.

## Isolation and source identity

- Repository: `/Users/eric/workspace/erdos/erdos_problems`
- Branch observed: `audit/egmra-independent-remediation-20260713`
- `HEAD`: `4b4ec96f1c81492af02f814c65825a5106e0af60`
- Commit date/title: `2026-07-12T23:34:26-07:00`, `Fail-closed on malformed synthesis JSON instead of killing the whole run`
- Pre-work status: 2,357 entries: 965 modified and 1,392 untracked. These were pre-existing and were not altered by baseline execution.
- Stable test snapshot: `/tmp/erdos-baseline.t2afE1/src`, copied before executing commands, excluding `.git`, `.venv`, `.venev`, Python bytecode, and pytest cache. Snapshot size was 497,790,976 bytes across 14,662 files.
- Temporary environment: `/tmp/erdos-baseline.t2afE1/venv`; all test-generated events and artifacts were outside the repository.
- Key source/requirements hashes were rechecked after execution and still matched the snapshot (`egmra/cli.py` SHA-256 `7e173afb49c3ef69c865c672e97b616a5a627480f94c458bdb081de2b8b42723`; `requirements.lock` `2f83369cefe075e217671dcf4f7a4fa487c3cbc5992e053460bd06bb9f4eda7f`).
- The only repository file written by this baseline worker is this report.

## Environment and documented setup

Host observations:

| Item | Observation |
| --- | --- |
| OS | macOS 26.3, build 25D125, Darwin 25.3.0, arm64 |
| CPU / RAM | 10 logical CPUs / 17,179,869,184 bytes |
| Documented Python | `README.md` / `SETUP_GUIDE.md`: Python 3.10+; CI matrix 3.10 and 3.12 |
| Host `python3` | 3.9.6; below the documented minimum |
| Audit Python | `/opt/homebrew/bin/python3.14`, 3.14.4 |
| Python 3.10 / 3.12 | not found locally; CI-version parity was not available |
| SQLite | 3.51.0 found |
| PostgreSQL | `psql` and `postgres` not found |
| Docker | CLI 29.5.3 found; no project command exercised a container |
| Lean / Lake | elan shims found, but both version probes fail because no default toolchain is configured; elan 4.2.3 |
| Lint/type/security tools | `ruff`, `black`, `mypy`, `pyright`, `bandit`, and `semgrep` not installed or declared/configured |

Project metadata inspected: `README.md`, `SETUP_GUIDE.md`, `requirements.txt`, `requirements.lock`, and both files under `.github/workflows/`. No `pyproject.toml`, `setup.py`, `setup.cfg`, `tox.ini`, `noxfile.py`, `pytest.ini`, `Makefile`, `Justfile`, linter configuration, or package entry-point metadata exists.

The documented CI verification commands are exactly:

```text
python -m pip install -r requirements.lock
python -m unittest discover -s tests -v
python check_corpus_integrity.py
python -m compileall -q -x '(^|/)(\.venv|\.venev|triage)/' .
```

`requirements.txt` and `requirements.lock` contain runtime packages for Playwright, requests, PyYAML, and fpdf2, but neither declares pytest.

## Exact command results

Commands below ran from `/tmp/erdos-baseline.t2afE1/src` with the temporary interpreter unless stated otherwise.

| Command | Exit | Exact result |
| --- | ---: | --- |
| `python3.14 -m venv /tmp/erdos-baseline.t2afE1/venv` | 0 | Python 3.14.4; pip 26.0.1 |
| `python -m pip install --disable-pip-version-check -r requirements.lock` | 0 | All 14 locked packages installed at their exact pins |
| `python -m pip check` | 0 | `No broken requirements found.` |
| `python -m unittest discover -s tests -v` | 0 | 179 tests passed in 0.832s; 0 skipped/errors/failures |
| `python check_corpus_integrity.py` | 0 | status `complete`; 616 canonical, 616 catalog, 616 local, 616 rankable; no missing/unexpected IDs |
| `python -m compileall -q -x '(^|/)(\.venv|\.venev|triage)/' .` | 0 | no diagnostics |
| `python -m unittest discover -s egmra/tests -v` before installing pytest | 1 | 16 `_FailedTest` import errors, each `ModuleNotFoundError: No module named 'pytest'`; no real EGMRA tests executed |
| `python -m pip install --disable-pip-version-check pytest` | 0 | audit-only pytest 9.1.1 installed; not added to repository manifests |
| `python -m unittest discover -s egmra/tests -v` after installing pytest | 5 | `Ran 0 tests`; `NO TESTS RAN` |
| `python -m pytest --collect-only -q` | 0 | 420 items collected: 241 EGMRA plus 179 legacy |
| `python -m pytest -q -ra egmra/tests` | 0 | 241 passed in 0.67s |
| `python -m pytest -q -ra` | 0 | 420 passed plus 18 successful subtests in 1.96s |
| `python -m pytest -q -W error` | 0 | 420 passed plus 18 successful subtests in 1.98s; no warning was emitted |
| `python -m pytest -q -ra egmra/tests/test_acceptance.py` | 0 | 18 passed in 0.13s |
| `python -m pytest -q -ra egmra/tests/test_eval.py` | 0 | 11 passed in 0.10s |
| `python -m pytest -q -ra egmra/tests/test_cli.py` | 0 | 8 passed in 0.11s |
| `python -m pytest -q -ra egmra/tests/test_m0_safety.py` | 0 | 9 passed in 0.07s |
| `python -m pytest -q -ra egmra/tests/test_m2_scale.py` | 0 | 4 passed in 0.02s |

The 18 pytest subtests are not additional collected test items; the collection denominator remains 420.

## Collection, skips, gates, and excluded totals

- Test files: 23 under `tests/`, 21 under `egmra/tests/`.
- Static function count and pytest collection agree: 179 legacy plus 241 EGMRA equals 420.
- Searches found no `pytest.mark`, `pytest.skip`, `pytest.importorskip`, `unittest.skip`, `skipIf`, `skipUnless`, `pytestmark`, or configured marker/addopts declarations in either test tree or project metadata.
- Full `pytest -ra` reported no skipped, xfailed, xpassed, deselected, or warning categories.
- The documented GitHub Actions command `unittest discover -s tests` excludes all 241 EGMRA tests by start-directory selection.
- Pointing that same runner at `egmra/tests` is not a substitute: before audit-only pytest installation it raises 16 import errors; afterward it collects zero tests because EGMRA tests are plain pytest functions.
- Therefore a total of 179 is the legacy-only CI surface, 241 is the EGMRA-only pytest surface, and 420 is their union. Any claim using one of the first two totals excludes the other surface.

## CLI and executable-example results

All CLI runs used `EGMRA_EVENTS_DIR=/tmp/erdos-baseline.t2afE1/cli-runs`; no repository run record was written.

| Command | Exit | Result |
| --- | ---: | --- |
| `python -m egmra.cli --help` | 0 | exposes `run`, `policy-show`, `verify-events`, `fixtures` |
| `python -m egmra.cli fixtures` | 0 | lists five bundled fixtures |
| `python -m egmra.cli policy-show` | 0 | unsigned-default policy; promotion/formal promotion/Lean/external routing disabled |

Each listed fixture was then run with `python -m egmra.cli run --fixture <id>`, followed by `python -m egmra.cli verify-events --events /tmp/erdos-baseline.t2afE1/cli-runs/<id>.jsonl`:

| Fixture | Declared expected | Runtime outcome | `proof_complete` | Events | Signed release object | Run / integrity exits |
| --- | --- | --- | ---: | ---: | --- | --- |
| `fx-true-square` | verified | `verified_finite_or_conditional_result` | true | 5 | yes, intent `I0` | 0 / 0 |
| `fx-false-prime` | honest triage | `honest_triage_report` | false | 3 | no | 0 / 0 |
| `fx-true-even-sum` | verified | `honest_triage_report` | true | 5 | no | 0 / 0 |
| `fx-false-all-even` | honest triage | `honest_triage_report` | false | 3 | no | 0 / 0 |
| `fx-ambiguous` | honest triage | `honest_triage_report` | false | 3 | no | 0 / 0 |

All five event logs independently reported `"integrity": true`. Exit status therefore does not expose the `fx-true-even-sum` expectation mismatch.

## Reproduced uncovered defects

### B-001 — A declared verified fixture triages while claiming a complete proof

Reproduction:

```text
EGMRA_EVENTS_DIR=/tmp/erdos-baseline.t2afE1/cli-runs \
  /tmp/erdos-baseline.t2afE1/venv/bin/python -m egmra.cli run \
  --fixture fx-true-even-sum
```

Observed: exit 0, `outcome: honest_triage_report`, `proof_complete: true`, five valid events, no release object. The fixture is declared `expected_outcome="verified"` in `egmra/eval/datasets.py`.

Root-cause evidence: its statement is `Prove that for all n, 2*n is even.` The grammar parser creates fallback binder `x` with an unspecified domain and records no parameter regime. The `dimensional_type` integrity probe consequently fails with `binders without a domain and no regime: ['x']`. `_outcome_label()` then returns honest triage even though the exact finite computation admitted the goal and the compiler marked it complete.

Coverage gap: `test_fixture_predicates_execute` checks only `fx-true-square` and `fx-false-prime`, then merely asserts that at least five fixtures exist. `test_fixtures_run_through_the_research_loop` hard-codes those same two fixtures rather than comparing every `FixtureProblem.expected_outcome`. The CLI test likewise runs only the same true/false pair.

### B-002 — Intake release block is not enforced at the production release path

Reproduction: run the `fx-true-square` CLI command above and independently build its `ProblemContract`.

Observed contract evidence:

- `contract.release_blocked` is true.
- The two parsers disagree on `binder_names` (`['x']` versus `['n']`) and `conclusion_norm` (the complete theorem versus the truncated clause `prove that for all natural numbers n`).
- Despite that block, the CLI returns `verified_finite_or_conditional_result`, emits a signed release object, and reports intent gate `I0` with the parser disagreements only in `unresolved_risks`.

Root-cause evidence in `egmra/orchestrator/loop.py`: the local `release_blocked` value is used only to withhold automatic intent-certificate approval. Certificate creation is later guarded by `profile is not None and not referee_result.blocks_release`, which omits `release_blocked`; `_outcome_label()` also receives only `probe_failed`, referee state, and gates. Thus a parser-ambiguity block can reach certificate creation and a verified-sounding outcome as long as no integrity probe fails.

Coverage gap: acceptance test 7 checks only that the intake lattice sets `release_blocked`; it never executes `research()` or the CLI and never asserts absence of a release certificate/outcome at the production boundary.

## What was and was not exercised

Exercised locally: dependency installation, dependency consistency, documented unit/regression suite, EGMRA pytest suite, all 18 named acceptance test functions, corpus equality, compilation, warnings-as-errors, evaluation/CLI/M0/M2 test modules, all five credential-free CLI fixtures, JSONL event persistence, and integrity verification.

Not exercised or not available:

- Python 3.10 and 3.12 CI parity (interpreters unavailable locally); Python 3.14.4 was used.
- Live ChatGPT/DeepSeek submission or collection, browser login, paid model calls, external evidence promotion, and canonical corpus refresh; these are mutating, authenticated, paid, or network-dependent workflows.
- Playwright Chromium installation/UI automation; the Python package was installed, but browser download/login was intentionally not performed.
- A real Lean kernel/Mathlib build; no default elan toolchain or pinned Lean project is present. EGMRA Lean tests use injected `kernel_runner` lambdas, so passing tests are not kernel evidence.
- A real PostgreSQL database; client/server are unavailable, and `PostgresEventStore.connect()` intentionally raises rather than connecting. The four M2 tests verify local interfaces/static behavior only.
- OCI/container execution; although a Docker CLI is present, `ContainerSandbox.run()` intentionally raises and no project command exercises it. Passing sandbox tests use the subprocess backend.
- External benchmark datasets in `PINNED_BENCHMARKS`; they are manifests/placeholders and no benchmark runner or bundled datasets exist.
- API-server or migration commands; no API application, migration framework, or configured command was found.
- Repository-defined formatting, lint, type-check, static-security, or standalone benchmark commands; none exists in the inspected metadata, so no ad hoc tool was installed and presented as a project check.

Passing local tests must therefore be read as deterministic local-component evidence, not proof of real-provider, kernel, database, container, benchmark, or production readiness.
