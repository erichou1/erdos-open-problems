# FABLE Final Post-Remediation Verification

## Verdict

**PARTIAL IMPLEMENTATION**

The repository is materially safer and better integrated than the audit-start
state, and every final local test passed. That result is not complete
specification conformance. The independent matrix contains 216 requirements;
only 13 satisfy the audit's full `VERIFIED` standard. The remaining final
statuses are 126 `PARTIAL`, 25 `BLOCKED-EXTERNAL`, 22 `UNVERIFIED`, 18
`TEST-ONLY`, 9 `UNREACHABLE`, and 3 `OMITTED`. Several of those limitations are
non-external, so the repository cannot honestly receive a complete verdict.

This document records the fresh final commands and distinguishes executable
local evidence from mocks, static inspection, missing infrastructure, and
absent production surfaces. Test counts are evidence about the named paths,
not a substitute for requirement traceability.

## Repository identity and preservation

| Item | Final observation |
|---|---|
| Repository | `/Users/eric/workspace/erdos/erdos_problems` |
| Audit branch | `audit/egmra-independent-remediation-20260713` |
| Initial commit | `4b4ec96f1c81492af02f814c65825a5106e0af60` |
| Final `HEAD` | `4b4ec96f1c81492af02f814c65825a5106e0af60` |
| Initial working tree | 2,357 expanded (`-uall`) paths: 965 modified tracked files and 1,392 untracked paths; the default collapsed porcelain record reports 16 untracked directory entries |
| Initial status record | `audit/FABLE_INITIAL_GIT_STATUS.txt` |
| Clean verification environment | `/tmp/fable-postfix-20260713/venv` |
| Independent requirements | 216 contiguous IDs, `F-REQ-001` through `F-REQ-216` |

The pre-existing dirty overlay was preserved. The audit used a dedicated branch
and isolated virtual environments, did not reset or delete unrelated work, and
did not create a sweeping commit over user-owned changes. `HEAD` therefore
remains the audit-start commit while the working tree contains the preserved
overlay plus remediation and audit artifacts. The authoritative specification
was not edited by this audit; its final SHA-256 was
`a736acd0488ea400ab27c3f3c7cd12307dd73a1edd4c5e7f5804a7f91b6e7340`
(2,302 lines, 160,880 bytes).

## Environment

| Item | Observation |
|---|---|
| Date / time zone | 2026-07-13 / America/Los_Angeles |
| Host | macOS 26.3 build 25D125; Darwin 25.3.0; arm64 |
| Verification Python | `/opt/homebrew/bin/python3.14`, Python 3.14.4 |
| Verification pip | pip 26.0.1 |
| Python 3.10 / 3.12 | Not installed locally; parity runs unavailable |
| Docker | Client/server 29.5.3; Docker Desktop 4.78; Linux server reachable |
| Lean / Lake | Elan 4.2.3 shims present; no configured default toolchain |
| PostgreSQL | `psql` and `postgres` absent |
| Aristotle | CLI absent |
| External credentials | No Aristotle, OpenAI, Anthropic, Gemini, database/Postgres, or OEIS credential was present |

Audit-only tools installed after dependency verification were pytest 9.1.1,
Ruff 0.15.21, mypy 2.3.0, pip-audit 2.10.1, and Bandit 1.9.4. They are not
misrepresented as runtime dependencies.

## Clean installation and packaging

Commands ran from the repository root. The two dependency manifests were
tested in separate fresh virtual environments.

| Exact command | Exit | Result |
|---|---:|---|
| `/opt/homebrew/bin/python3.14 -m venv /tmp/fable-postfix-20260713/venv` | 0 | Fresh Python 3.14.4 environment created. |
| `/tmp/fable-postfix-20260713/venv/bin/python -m pip install --disable-pip-version-check -r requirements.lock` | 0 | Locked dependencies installed. |
| `/tmp/fable-postfix-20260713/venv/bin/python -m pip check` | 0 | `No broken requirements found.` |
| `/opt/homebrew/bin/python3.14 -m venv /tmp/fable-postfix-20260713/requirements-venv` | 0 | Separate manifest-check environment created. |
| `/tmp/fable-postfix-20260713/requirements-venv/bin/python -m pip install --disable-pip-version-check -r requirements.txt` | 0 | Unlocked requirements installed. |
| `/tmp/fable-postfix-20260713/requirements-venv/bin/python -m pip check` | 0 | `No broken requirements found.` |
| `/tmp/fable-postfix-20260713/venv/bin/python -m pip install -e .` | 1 | Packaging unavailable: there is no `pyproject.toml` or `setup.py`. |

The editable-install failure is a real residual limitation. Importing and
running from the repository works, but this is not an installable Python
package and exposes no packaged console script.

## Compilation, lint, type, dependency, and security checks

| Exact command | Exit | Result |
|---|---:|---|
| `/tmp/fable-postfix-20260713/venv/bin/python -m compileall -q -x '(^\|/)(\.venv\|\.venev\|triage\|proof_runs)/' .` | 0 | No compilation diagnostics. |
| `/tmp/fable-postfix-20260713/venv/bin/ruff check egmra tests *.py` | 0 | `All checks passed!` |
| `/tmp/fable-postfix-20260713/venv/bin/ruff format --check egmra tests *.py` | 1 | 206 files would be reformatted; 15 already formatted. |
| `/tmp/fable-postfix-20260713/venv/bin/mypy --check-untyped-defs --ignore-missing-imports --exclude '(^egmra/tests/\|^tests/)' --show-error-codes egmra *.py` | 0 | `Success: no issues found in 153 source files.` |
| `/tmp/fable-postfix-20260713/venv/bin/mypy --follow-imports=skip --exclude '^egmra/tests/' --show-error-codes --pretty egmra` | 0 | `Success: no issues found in 116 source files.` |
| `/tmp/fable-postfix-20260713/venv/bin/pip-audit -r requirements.lock` | 0 | `No known vulnerabilities found.` |
| `/tmp/fable-postfix-20260713/venv/bin/bandit -q -r -ll -x egmra/tests,tests egmra *.py` | 0 | No medium- or high-severity finding. |
| `/tmp/fable-postfix-20260713/venv/bin/bandit -r -l -iii -x egmra/tests,tests -f json -q egmra *.py` | 1 | 53 LOW, 0 MEDIUM, 0 HIGH; all 53 high-confidence; 28,876 LOC; 0 `nosec`; 0 skipped checks. |
| `git diff --check` | 0 | No whitespace-error diagnostic. |

The formatting check did **not** pass. A repository-wide mechanical reformat was
not applied over the large pre-existing dirty tree, and the project has no
checked-in formatter configuration defining an authoritative style. This is
recorded as a limitation rather than hidden or converted to success.

The 53 Bandit findings are retained rather than suppressed: B110 (24 cleanup or
failure-path `try/except/pass` sites), B603 (11 subprocess invocations), B404
(6 subprocess imports), B311 (5 non-cryptographic randomness uses), B101 (4
asserts), B112 (2 `try/except/continue` sites), and B607 (1 partial executable
path). The medium/high scan is clean, but the low findings still require
deployment-context review.

## Final test executions

The final full executions used `-ra` and converted every warning into an error.
No skipped, xfailed, xpassed, deselected, or warning category was reported.
The `subtests passed` number is not added to the pytest collection denominator.

| Exact command | Exit | Result |
|---|---:|---|
| `/tmp/fable-postfix-20260713/venv/bin/python -m pytest -q -ra -W error egmra/tests` | 0 | **555 passed** in 11.34s; 0 failures/errors/skips/warnings. |
| `/tmp/fable-postfix-20260713/venv/bin/python -m pytest -q -ra -W error` | 0 | **786 passed plus 44 subtests passed** in 13.19s; 0 failures/errors/skips/warnings. |
| `/tmp/fable-postfix-20260713/venv/bin/python -m unittest discover -s tests -v` | 0 | **231 passed** in 1.414s; 0 failures/errors/skips. |
| `/tmp/fable-postfix-20260713/venv/bin/python -m pytest -q -ra -W error egmra/tests/test_acceptance.py` | 0 | **18 passed**; see the semantic qualification below. |
| `/tmp/fable-postfix-20260713/venv/bin/python -m pytest -q -ra -W error egmra/tests/test_adversarial_*.py egmra/tests/test_*security.py egmra/tests/test_m0_safety.py egmra/tests/test_release.py tests/test_ingestion_network_security.py tests/test_legacy_trust_boundaries.py tests/test_searcher_safety.py` | 0 | **349 passed plus 25 subtests passed** in 6.98s. |
| `/tmp/fable-postfix-20260713/venv/bin/python -m pytest -q -ra -W error egmra/tests/test_eval.py egmra/tests/test_adversarial_eval.py` | 0 | **31 passed**; local schemas/interpreter only, no benchmark campaign. |
| `/tmp/fable-postfix-20260713/venv/bin/python -m pytest -q -ra -W error egmra/tests/test_m2_scale.py egmra/tests/test_adversarial_m2.py` | 0 | **18 passed**; configuration/object boundaries, not a live M2 deployment. |

Additional focused batches, which overlap and therefore must not be summed,
passed as follows:

- compute/security: 67;
- truth/security/snapshots: 42;
- Lean/release/truth/communications: 132;
- authorities/agents/truth: 32;
- search: 32; retrieval: 16; OEIS: 24 after the final HTTP hardening;
- verification: 19; learning: 15; control: 19; selection: 19;
- orchestrator/intake/CLI/evaluation: 71;
- checkpoint/orchestrator/acceptance: 38;
- CLI certificate/result binding: 23;
- ingestion/network boundary: 52; and
- current legacy/CLI consolidation: 121 plus 13 subtests.

Relative to the immutable baseline, collection rose from 420 cases plus 18
subtests to 786 cases plus 44 subtests: **366 net additional collected tests**.
The final split is 555 EGMRA and 231 legacy cases, versus 241 and 179 at
baseline.

## Section 13.6 acceptance criteria

All 18 functions named for §13.6 pass. That is not equivalent to all 18 full
criteria being verified. Applying the matrix rule—faithful semantics,
production reachability, required integration, positive and negative tests,
runtime behavior, and required failure behavior—only four criteria are fully
`VERIFIED`:

| Requirement | Criterion | Final status |
|---|---|---|
| F-REQ-180 | 7/18: ambiguity creates multiple interpretations and blocks release | VERIFIED |
| F-REQ-181 | 8/18: a false central lemma revokes all dependents | VERIFIED |
| F-REQ-186 | 13/18: vendor-only `COMPLETE` cannot count as formal verification | VERIFIED |
| F-REQ-189 | 16/18: OEIS remains heuristic and cannot promote truth | VERIFIED |

The other 14 are `PARTIAL`, `UNREACHABLE`, `TEST-ONLY`, `UNVERIFIED`, or
`BLOCKED-EXTERNAL`; their exact dispositions and runtime evidence are in
`FABLE_TRACEABILITY_MATRIX.md`. Therefore “18 tests passed” must not be reported
as “all 18 acceptance criteria are satisfied.”

## Corpus, import, CLI, and entry-point smoke tests

| Command / path | Exit | Result |
|---|---:|---|
| `/tmp/fable-postfix-20260713/venv/bin/python check_corpus_integrity.py` | 0 | `complete`: 616 canonical source records, 616 catalog records, 616 local LaTeX files, 616 rankable intersection; no missing or unexpected IDs. |
| Production EGMRA import sweep using `importlib.import_module` over every non-test, non-`__init__` `egmra/**/*.py` module | 0 | 95 modules imported. This proves importability, not production reachability. |
| `/tmp/fable-postfix-20260713/venv/bin/python -m egmra.cli --help` | 0 | `run`, `policy-sign`, `policy-show`, `verify-events`, and `fixtures` exposed. |
| `/tmp/fable-postfix-20260713/venv/bin/python -m egmra.cli fixtures` | 0 | Bundled local fixtures listed. |
| `env -u EGMRA_POLICY_KEY /tmp/fable-postfix-20260713/venv/bin/python -m egmra.cli policy-show` | 2 | Default/unsigned policy failed closed. |

There is no API server, migration framework, database setup command, packaged
entry point, benchmark runner, or service deployment command. API smoke,
migration smoke, full benchmark smoke, and daemon/topology startup are therefore
**unavailable**, not passed.

## Local M1-style CLI slice

The CLI smoke used `/tmp/fable-postfix-20260713/cli/config.json`, a signed
`/tmp/fable-postfix-20260713/cli/policy.json`, a signed intent-review input, and
independent audit keys of at least 32 bytes. Secret values are intentionally not
printed in this report; the command shape and all non-secret arguments are:

```text
env EGMRA_*_KEY='<redacted audit keys>' \
  /tmp/fable-postfix-20260713/venv/bin/python -m egmra.cli \
  --config /tmp/fable-postfix-20260713/cli/config.json run \
  --fixture fx-true-square \
  --policy /tmp/fable-postfix-20260713/cli/policy.json \
  --intent-review /tmp/fable-postfix-20260713/cli/intent-review.json

env EGMRA_*_KEY='<redacted audit keys>' \
  /tmp/fable-postfix-20260713/venv/bin/python -m egmra.cli \
  --config /tmp/fable-postfix-20260713/cli/config.json run \
  --fixture fx-false-prime \
  --policy /tmp/fable-postfix-20260713/cli/policy.json

env EGMRA_EVENT_KEY='<redacted audit key>' \
  /tmp/fable-postfix-20260713/venv/bin/python -m egmra.cli verify-events \
  --events /tmp/fable-postfix-20260713/cli/events/fx-true-square.jsonl \
  --run-id fx-true-square
```

Observed true-claim flow:

- exit 0 with disposition `verified_finite_or_conditional_result`;
- exact source and selected interpretation were persisted;
- the 10-event log contains `PROBLEM_FROZEN`, `INTERPRETATION_ADDED`,
  `INTENT_CERTIFICATE_ISSUED`, three `BRANCH_OPENED` events,
  `CLAIM_PROPOSED`, `CLAIM_INTENT_BOUND`, `EVIDENCE_ATTACHED`, and
  `CLAIM_PROMOTED`;
- replay reconstructed claim `goal` as `SUPPORTED` with evidence `ev_goal`;
- the five-gate result and current subject-bound release certificate were
  present; event verification returned `integrity: true`; and
- the event log/head and signed policy were mode 0600. The signed review input
  was mode 0644 and contains no secret key material.

Observed false-claim flow:

- exit 0 with disposition `honest_triage_report`;
- six events stopped after interpretation, branch creation, and unknown claim;
- there was no evidence attachment, promotion, gate approval, or release
  certificate; and
- replay retained the claim as `UNKNOWN`.

The CLI/event/certificate tests inject missing or forged policy, interpretation,
intent, computation, event-run, gate, promotion, stale-head, result-binding, and
release failures and require fail-closed behavior. This is a meaningful local
slice, but it is **not** the complete §13.3 M1 flow: `runner_attested` remained
false, formal checks were zero, no persisted Lean artifact was kernel-compiled,
the exact computation used the restricted local executor rather than a
successful compatible OCI image, and the semantic reviewer/referee were not
independent live services.

## External integration ladder

| Integration | Interface / config validation | Mocked or local protocol tests | Real exercise | Failure/recovery exercise | Production readiness |
|---|---|---|---|---|---|
| Lean / Lake / Mathlib | Yes | Yes | **No**: `lean --version` and `lake --version` exited 1; no default toolchain | Missing/malformed/vendor-only paths fail closed | No |
| Model providers | Yes | Yes, with injected transports/attestations | **No credentials or live call** | Malformed/identity/config paths locally tested | No |
| Aristotle CLI | Yes | Fake CLI plus filesystem/archive quarantine tests | **No executable or credential** | Timeout, malformed archive, symlink, secret-env, and vendor-only paths tested | No |
| OEIS HTTP | Yes | Local transforms/cache and mocked HTTPS/TLS/redirect/size tests | **No live OEIS request** | Mocked malformed JSON, redirect-downgrade, oversize, cache-corruption, and offline paths tested | No |
| Literature/theorem retrieval | Local interface and immutable packets | Yes | **No live four-index service** | Local malformed/provenance/injection boundaries tested | No |
| PostgreSQL | DSN/schema interface and fail-closed readiness | Yes | **No client/server** | Invalid/unavailable DSN paths tested | No |
| Docker / OCI | `ContainerSandbox` and OCI readiness | Yes | Docker 29.5.3 reached a real runc negative path using local `postgres:17-alpine`; it exited 127 because the image has no Python | Unavailable image, forced entrypoint, timeout/cleanup, and no-fallback paths tested | No successful compatible math job; not ready |
| Upstream corpus ingestion | Central HTTPS-only bounded transport | 52 mocked/local tests | **No live upstream fetch in final verification** | Scheme, redirect downgrade, TLS-default, oversize, and cleanup paths tested; credential rejection is statically enforced but lacks its own regression | Partial; DNS/IP SSRF pinning and live recovery absent |
| Public API / release service | No API surface | N/A | No | No | No |

No live service success is claimed. In particular, an interface plus a mock is
not reported as a working integration.

## Final repository searches

The following source search returned no match (ripgrep exit 1 means “no
matches,” not a command failure):

```text
rg -n --glob '!.venv/**' --glob '!.venev/**' --glob '!triage/**' \
  --glob '!proof_runs/**' --glob '!FABLE_*.md' \
  '(TODO|FIXME|XXX|NotImplementedError|pytest\.skip|pytest\.mark\.skip|unittest\.skip)' \
  egmra tests *.py
```

An AST scan over production EGMRA and root modules found zero functions or
methods whose sole body is `pass`. A textual pass-line scan still found 53
lines, principally exception marker classes and cleanup/error handlers; Bandit
independently reports the material low-severity catch/pass sites above. A broad
exception scan found 92 `except Exception`/`BaseException` sites across EGMRA
and root production modules. These are not silently reclassified as safe merely
because tests pass; unexpected-exception propagation was specifically fixed for
OEIS transform enumeration, while remaining legacy cleanup/retry sites retain
review debt.

Static import success does not prove reachability. The final matrix still marks
9 requirements `UNREACHABLE`, 18 `TEST-ONLY`, and 3 `OMITTED`, and the code
inventory records disconnected descriptors, retired legacy publication, and
external facades. The repository also has no complete generated inventory of
future/direct release entry points and no deployment document for key rotation,
HSM isolation, or all required service environment variables.

## Warnings, skips, unavailable work, and residual limitations

- Test failures/errors: 0 in the final full run.
- Test skips/xfails/xpasses/deselections: 0 reported.
- Runtime warnings: 0; warnings were errors.
- Formatting: failed (`206 would be reformatted`).
- Package installation: failed because package metadata is absent.
- Python 3.10/3.12 parity: unavailable.
- API, migration, service-daemon, and full benchmark commands: absent.
- Real Lean/Lake/Mathlib, providers, Aristotle, OEIS, theorem/citation
  retrieval, PostgreSQL, and successful compatible OCI computation: not run.
- Event log plus local head can be rolled back together without an external
  monotonic witness.
- Search/controller/checkpoint/learning state is not one durable,
  crash-consistent distributed closed loop.
- No PostgreSQL transaction/partition/recovery or multi-host lease campaign ran.
- Local restricted exact execution is a capability-limited interpreter, not an
  OS isolation boundary.
- No organizationally independent referee/provider or human intent service ran.
- No blind benchmark, paired equal-cost baseline, time-capsule, ablation, or
  statistically controlled deployment evaluation ran.
- Storage/token/retention quotas, DNS/IP SSRF enforcement, key isolation and
  rotation, and exhaustive alternate-entry reachability remain incomplete.

## Final conclusion

The final repository passes a substantially stronger 786-case local suite and
closes the confirmed local reproductions on their tested paths. It does not
implement or demonstrate the complete authoritative architecture. Passing
tests coexist with 203 requirements that are not fully `VERIFIED`, including
many non-external architectural gaps. The correct final disposition is
**PARTIAL IMPLEMENTATION**, not “verified complete” and not “verified with only
external limitations.”
