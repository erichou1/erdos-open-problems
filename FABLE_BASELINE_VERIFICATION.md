# FABLE Pre-Fix Baseline Verification

## Baseline verdict

The documented legacy CI surface was green, but it did **not** execute the
EGMRA suite. The declared dependency files could not import 16 of 21 EGMRA test
modules because `pytest` was undeclared. After audit-only installation of
pytest, an isolated run reproduced the advertised 241 EGMRA / 420 combined
passing counts, with no skips or warnings. Those tests did not establish the
claimed architecture: all five CLI fixtures exited zero, while two production
outcomes contradicted their own expected or release-blocking state.

This report is the immutable **pre-remediation** baseline. It does not include
later code, dependency, CI, or test additions.

## Isolation and source identity

- Repository: `/Users/eric/workspace/erdos/erdos_problems`
- Audit branch: `audit/egmra-independent-remediation-20260713`
- Initial commit: `4b4ec96f1c81492af02f814c65825a5106e0af60`
- Commit: `2026-07-12T23:34:26-07:00`, `Fail-closed on malformed synthesis JSON instead of killing the whole run`
- Initial working-tree state: 2,357 status entries: 965 modified tracked files and
  1,392 untracked paths. These were pre-existing user changes and were not
  overwritten by baseline execution.
- Full initial status record: `audit/FABLE_INITIAL_GIT_STATUS.txt`.
- Isolated source snapshot: `/tmp/erdos-baseline.t2afE1/src`, copied before
  executing commands and excluding `.git`, `.venv`, `.venev`, Python bytecode,
  and pytest cache.
- Snapshot size: 497,790,976 bytes across 14,662 files.
- Isolated environment: `/tmp/erdos-baseline.t2afE1/venv`.
- Test-generated event/artifact paths were outside the repository.
- Rechecked hashes after the run matched the snapshot: `egmra/cli.py` SHA-256
  `7e173afb49c3ef69c865c672e97b616a5a627480f94c458bdb081de2b8b42723`;
  `requirements.lock` SHA-256
  `2f83369cefe075e217671dcf4f7a4fa487c3cbc5992e053460bd06bb9f4eda7f`.

## Environment

| Item | Baseline observation |
|---|---|
| Date/time zone | 2026-07-13; host zone America/Los_Angeles |
| OS | macOS 26.3, build 25D125; Darwin 25.3.0; arm64 |
| CPU / RAM | 10 logical CPUs / 17,179,869,184 bytes |
| Documented Python | Python 3.10+; CI matrix 3.10 and 3.12 |
| Host `python3` | 3.9.6, below documented minimum |
| Audit Python | `/opt/homebrew/bin/python3.14`, Python 3.14.4 |
| Python 3.10 / 3.12 | Not installed locally; version-parity run unavailable |
| SQLite | 3.51.0 available |
| PostgreSQL | `psql` and `postgres` absent |
| Docker | CLI 29.5.3 present; no baseline project command exercised a container |
| Lean / Lake | elan shims present, but both version probes failed because no default toolchain was configured; elan 4.2.3 |
| Lint/type/security tools | `ruff`, `black`, `mypy`, `pyright`, `bandit`, and `semgrep` absent and not declared/configured |

Inspected metadata: `README.md`, `SETUP_GUIDE.md`, `requirements.txt`,
`requirements.lock`, and both workflow files under `.github/workflows/`.
There was no `pyproject.toml`, `setup.py`, `setup.cfg`, `tox.ini`, `noxfile.py`,
`pytest.ini`, Makefile, Justfile, linter/type configuration, migration framework,
API entry point, or package/console-script declaration.

## Documented install and verification surface

The checked-in CI executed exactly:

```text
python -m pip install -r requirements.lock
python -m unittest discover -s tests -v
python check_corpus_integrity.py
python -m compileall -q -x '(^|/)(\.venv|\.venev|triage)/' .
```

At baseline, `requirements.txt` and `requirements.lock` declared Playwright,
requests, PyYAML, and fpdf2 dependencies, but not pytest. The workflow selected
only `tests/`, so all 241 EGMRA pytest cases were excluded from CI.

## Exact command log and results

Unless otherwise stated, commands ran from
`/tmp/erdos-baseline.t2afE1/src` using the isolated interpreter.

| Exact command | Exit | Passed / failed / skipped / other result |
|---|---:|---|
| `python3.14 -m venv /tmp/erdos-baseline.t2afE1/venv` | 0 | Created Python 3.14.4 environment; pip 26.0.1. |
| `python -m pip install --disable-pip-version-check -r requirements.lock` | 0 | Installed all 14 locked packages at exact pins. |
| `python -m pip check` | 0 | `No broken requirements found.` |
| `python -m unittest discover -s tests -v` | 0 | 179 passed in 0.832s; 0 failures, errors, or skips. |
| `python check_corpus_integrity.py` | 0 | `complete`: 616 canonical, 616 catalog, 616 local, 616 rankable; no missing or unexpected IDs. |
| `python -m compileall -q -x '(^\|/)(\.venv\|\.venev\|triage)/' .` | 0 | No diagnostics. |
| `python -m unittest discover -s egmra/tests -v` before pytest install | 1 | 16 `_FailedTest` import errors, all `ModuleNotFoundError: No module named 'pytest'`; no real EGMRA test executed. |
| `python -m pip install --disable-pip-version-check pytest` | 0 | Audit-only pytest 9.1.1 installed; baseline repository manifests unchanged. |
| `python -m unittest discover -s egmra/tests -v` after pytest install | 5 | `Ran 0 tests`; `NO TESTS RAN` because tests are pytest-style functions. |
| `python -m pytest --collect-only -q` | 0 | 420 collected items: 241 EGMRA plus 179 legacy. |
| `python -m pytest -q -ra egmra/tests` | 0 | 241 passed in 0.67s; no skip/xfail/deselection/warning category. |
| `python -m pytest -q -ra` | 0 | 420 passed plus 18 successful subtests in 1.96s. |
| `python -m pytest -q -W error` | 0 | 420 passed plus 18 successful subtests in 1.98s; no warnings. |
| `python -m pytest -q -ra egmra/tests/test_acceptance.py` | 0 | 18 passed in 0.13s. |
| `python -m pytest -q -ra egmra/tests/test_eval.py` | 0 | 11 passed in 0.10s. |
| `python -m pytest -q -ra egmra/tests/test_cli.py` | 0 | 8 passed in 0.11s. |
| `python -m pytest -q -ra egmra/tests/test_m0_safety.py` | 0 | 9 passed in 0.07s. |
| `python -m pytest -q -ra egmra/tests/test_m2_scale.py` | 0 | 4 passed in 0.02s. |

The 18 successful subtests are not additional collected test items; the pytest
collection denominator remained 420.

## Collection exclusions, skips, markers, and warnings

- Static test files: 23 under `tests/`; 21 under `egmra/tests/`.
- Static function count and pytest collection agreed: 179 legacy + 241 EGMRA =
  420 collected cases.
- Searches found no `pytest.mark`, `pytest.skip`, `pytest.importorskip`,
  `unittest.skip`, `skipIf`, `skipUnless`, `pytestmark`, marker declarations, or
  configured `addopts` in either test tree/project metadata.
- Full `pytest -ra` reported no skipped, xfailed, xpassed, deselected, or warning
  categories.
- The documented CI command excluded all 241 EGMRA tests by its selected start
  directory.
- Pointing unittest at `egmra/tests` was not an alternative: it produced 16
  dependency import errors before pytest installation and collected zero
  EGMRA functions after installation.

Therefore:

- **179** was the actual legacy-only documented CI surface;
- **241** was the undeclared pytest-only EGMRA surface; and
- **420** was the audit-only union.

## CLI, API, database, benchmark, and example smoke results

All baseline CLI commands used
`EGMRA_EVENTS_DIR=/tmp/erdos-baseline.t2afE1/cli-runs`.

| Command | Exit | Observation |
|---|---:|---|
| `python -m egmra.cli --help` | 0 | Exposed `run`, `policy-show`, `verify-events`, `fixtures`. |
| `python -m egmra.cli fixtures` | 0 | Listed five bundled fixtures. |
| `python -m egmra.cli policy-show` | 0 | Printed unsigned-default policy; promotion/formal promotion/Lean/external routing disabled. |
| `python -m egmra.cli run --fixture <id>` for each listed fixture | 0 for all five | See outcome table below. |
| `python -m egmra.cli verify-events --events <fixture-log>` for each run | 0 for all five | Each log reported `integrity: true`; this did not validate omitted graph bodies. |

| Fixture | Declared expected | Runtime outcome | `proof_complete` | Events | Signed release object | Run / integrity exits |
|---|---|---|---:|---:|---|---|
| `fx-true-square` | verified | `verified_finite_or_conditional_result` | true | 5 | yes, intent `I0` | 0 / 0 |
| `fx-false-prime` | honest triage | `honest_triage_report` | false | 3 | no | 0 / 0 |
| `fx-true-even-sum` | verified | `honest_triage_report` | true | 5 | no | 0 / 0 |
| `fx-false-all-even` | honest triage | `honest_triage_report` | false | 3 | no | 0 / 0 |
| `fx-ambiguous` | honest triage | `honest_triage_report` | false | 3 | no | 0 / 0 |

No API server or migration command existed, so API/database migration smoke was
**unavailable**, not passed. PostgreSQL client/server were absent and
`PostgresEventStore.connect()` was intentionally nonfunctional. External
benchmark manifests existed, but no benchmark runner or datasets were present;
only the five local elementary fixtures ran.

## Reproduced defects missed by the green suite

### B-001 — Expected-verified fixture triaged while claiming proof complete

Reproduction:

```text
EGMRA_EVENTS_DIR=/tmp/erdos-baseline.t2afE1/cli-runs \
  /tmp/erdos-baseline.t2afE1/venv/bin/python -m egmra.cli run \
  --fixture fx-true-even-sum
```

Observed: exit 0; `outcome: honest_triage_report`; `proof_complete: true`; five
integrity-valid events; no release object. The fixture's manifest expected
`verified`. The parser invented/fell back to binder `x` with no domain, causing
the dimensional/type probe to fail even though finite computation and candidate
compiler state said complete. Existing fixture tests ran only two of five
fixtures and never compared every expected outcome.

### B-002 — Intake release block was bypassed by the release path

Reproduction: run `fx-true-square`, then independently build its
`ProblemContract`.

Observed: the two parsers disagreed on binder names and conclusion; the contract
had `release_blocked = true`. Nevertheless the CLI returned
`verified_finite_or_conditional_result`, emitted a signed release object, and
reported intent `I0`. The loop used `release_blocked` only to withhold automatic
intent approval; certificate creation and the outcome label did not require the
block to be false. Acceptance 7 tested only lattice construction, never the
release boundary.

### Additional audit repros established after baseline collection

Read-only/pre-fix reproductions also showed that:

- unsigned policy could be accepted and enforced;
- a valid-prefix event-log truncation was not detected and concurrent writers
  could share sequence zero;
- self-reported/forged exact-computation metadata could promote a claim;
- caller Lean booleans, arbitrary proof text, or unrelated certificate labels
  could create formal/equivalence status;
- same-host “sandboxed” jobs could read `/etc/passwd` and import `_socket`;
- release gates trusted caller profiles/booleans and public fallback keys;
- caller `hardened=True` could raise a result to T5;
- selection/search/control/learning state was either disconnected or accepted
  untrusted labels/records.

These are documented in `FABLE_LEDGER_DISCREPANCIES.md`,
`FABLE_TEST_QUALITY_REPORT.md`, and the remediation/security reports.

## What was unavailable or deliberately not claimed

- Python 3.10 and 3.12 parity: interpreters absent locally.
- Real Lean kernel/Mathlib: no configured elan toolchain or pinned project; tests
  used injected success functions.
- PostgreSQL: client/server absent; adapter did not connect.
- OCI computation: Docker CLI existed, but the baseline implementation always
  raised for the container backend and no project command invoked it.
- Frontier model providers and Aristotle CLI: no credentials/live calls; tests
  used deterministic/injected callables.
- Live OEIS: tests used a fake fetcher; CLI did not invoke the client.
- Live theorem/citation retrieval: only caller-supplied local corpus.
- Playwright browser/UI: Python package installed, but browser/login not
  installed or exercised.
- External benchmark datasets and historical time capsules: manifests only.
- API, service daemons, package installation, migrations: no such metadata or
  commands.
- Formatting, linting, type checking, static-security scanning: no declared
  tools or configuration; none was installed ad hoc and represented as a
  project check.

## Baseline conclusion

The baseline supports the raw claims “179 documented legacy tests pass,” “241
audit-only EGMRA tests pass,” and “420 pass in their union.” It does not support
complete M0/M1/M2, production reachability, real external integration, or the 18
acceptance behaviors. The two CLI contradictions and later adversarial
reproductions demonstrate that test count alone materially overstated
correctness.
