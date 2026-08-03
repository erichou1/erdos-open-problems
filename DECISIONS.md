# EGMRA Implementation Decisions

Records interpretations of ambiguity and resolutions of contradictions in
`docs/AUTONOMOUS_MATH_RESEARCH_ARCHITECTURE_2026.md`, per the task's "no silent
omissions" rule.

## D-001 — New `egmra/` package vs rewriting existing files
The spec (§4.1) explicitly distinguishes the "live implementation" (fixed loop)
from the target architecture, and §13 says to *reuse* specific existing modules
while *replacing* the fixed loop. **Decision:** build the new architecture as a
cohesive `egmra/` package and *reuse* `run_contract.py`, `verification.py`,
`lean_verify.py`, `feature_flags.py`, `erdos_ingest.py`, and `erdos_searcher.py`
where the spec says "retain"; apply M0 *repairs* in place to the existing files
they name (`aristotle_verifier.py`). This preserves the 179-test baseline.

## D-002 — "Two independent parses ... different model families"
No model credentials are guaranteed available. §6.1 permits "one deterministic
grammar/parser plus a separately implemented semantic model." **Decision:** the
default Statement IR uses two *independently implemented deterministic* parsers
(a grammar/regex parser and a structurally different heuristic parser). A
`ModelParser` adapter exists for real model families and is used when a runner is
configured; the two-parse reconciliation contract is identical either way. Tests
use the deterministic parsers.

## D-003 — Signed feature policy
§4.2/§16 require "one signed feature policy." A cryptographic signature needs a
key. **Decision:** the policy is content-addressed (SHA-256 over canonical JSON)
and carries an HMAC signature using a key from `EGMRA_POLICY_KEY` when present;
without a key it uses a deterministic local dev key and marks
`signature_trust="local-dev"`. Enforcement (record + check the policy hash at
every entry point) works regardless. Production signing command is documented.

## D-004 — Real external services vs local tests
OEIS HTTP, Lean/Mathlib `lake build`, frontier-model providers, Aristotle CLI,
Postgres, and OCI containers require credentials/infrastructure not available in
this environment. **Decision (per task rule):** implement the real integration
interface + configuration + validation + local/mock tests, and document the exact
command to validate with real credentials. The live external call is not claimed
tested; the interface and local behavior are.

## D-005 — Event store backend
§13.3 (M1) says "SQLite plus append-only JSONL events"; §13.4 (M2) says Postgres.
**Decision:** the authoritative store is append-only JSONL (portable, replayable);
a SQLite index is built for queries. A `PostgresEventStore` interface is provided
for M2 with the same contract; the default backend is JSONL+SQLite. Later/more
specific requirement (M2 Postgres) is provided as an interface, not the default,
because M1 must run without a database server.

## D-006 — verifiedDebt weights "frozen for an evaluation run"
§7.3/§12.3 require the debt definition and weights be frozen per eval run.
**Decision:** `egmra/search/verified_debt.py` loads weights from an immutable,
content-addressed `DebtPolicy`; the policy hash is recorded on every debt
computation so a changed policy is detectable and cannot silently affect scores.

## D-007 — "Adversarial referee ... different model family"
Independence cannot be guaranteed without multiple providers. **Decision:** the
referee records generator/checker/replay/human diversity as *separate evidenced
fields* (§11.1). When only one model family is configured, the referee marks
`model_family_independence=false` and the release auditor treats high-value
informal claims as not meeting T3's "two genuinely independent" requirement.
Correctness of the release gate does not depend on having two providers.

## D-008 — Sandbox without containers
§6.8/§13.3 require sandboxed exact computation; real OCI isolation needs Docker.
**Decision:** the default `SubprocessSandbox` runs jobs in a separate Python
process with no network (import guard + env scrub), RO input snapshot, bounded
CPU/RAM/wall (resource limits on POSIX), and captured outputs. A
`ContainerSandbox` interface exists for M2/production (documented command). Exact
arithmetic uses `fractions.Fraction`/`decimal`/`sympy` when available; float
results are always classified as heuristic and never prove an exact statement.

## D-009 — Contradiction: "literature mandatory before proof" vs "cold pass first"
§1/§5.2 resolve this explicitly: a 5–10% *blind* cold pass runs first, then a
*mandatory* frozen literature packet before deep proof work. **Decision:** the
orchestrator enforces this order and the loop test asserts cold-pass events
precede packet-freeze events which precede deep-branch events. No contradiction
remains once the two-pass protocol (§4.3 item 4) is implemented.

## D-010 — Scope realism
The spec is a complete research operating system. **Decision:** implement all
technically actionable requirements as real, tested code. Sections that are pure
prose guidance (literature map §2, comparison tables §3) are encoded as
machine-readable data (`design_status.py`) where they carry an actionable
contract (design-status provenance), and otherwise summarized in the ledger as
NOT_APPLICABLE-to-code with justification (they inform, not command, the build).

## D-011 — Promotion entry point enforces a signed policy (M0)
Spec §16 P0.1 requires the signed feature policy be checked at *every* promotion
entry point. **Decision:** `promote_verified_run.promote` now enforces the signed
feature policy; with no explicit enforcer it loads the default egmra policy (which
disables promotion), so promotion is off unless a signed policy enables it. The CLI
gains a `--policy` flag. The one existing promotion test
(`test_external_evidence_promotes_existing_run_and_publishes`) was updated to pass a
signed promotion-enabled policy. This is the intended M0 behavior change, not a
regression; the 179-test baseline otherwise remains unchanged.

## D-012 — Packaging + arbitrary-problem entry point (production reachability)
The system must be installable and must research *arbitrary* problems, not only
bundled fixtures. **Decision:** add `pyproject.toml` (setuptools, dynamic version
from `egmra.__version__`, `requires-python>=3.10` to match the CI matrix) exposing
the `egmra` console script (`egmra.cli:main`). The core package is stdlib-only, so
`pip install -e .` yields a fully importable, fully testable system with no external
services; live adapters are opt-in extras (`.[browser]`, `.[fetch]`, `.[dev]`,
`.[all]`). The primary `egmra run` path drives the real research loop on
`--erdos N | --statement | --statement-file` and never calls the fixture loader;
`--fixture` remains available only as an explicit regression selector. `--erdos N`
resolves the exact statement from the bundled corpus snapshot via a vendored copy
of the exact extraction regexes (`egmra/corpus/tex_extract.py`) so the installed
package is self-contained (it does not import the repository's loose top-level
scripts). New `egmra doctor` reports readiness (deps, executables, key presence as
booleans only — never values, policy, corpus); `egmra status` inventories runs.

## D-013 — Browser ChatGPT is the primary informal-reasoning provider (unattested)
Per the operator contract, the primary informal provider is a human-authenticated
ChatGPT browser session, and a browser UI cannot cryptographically attest an
immutable model/version. **Decision:** `egmra/agents/browser_runner.py` implements
the `ModelRunner` protocol over an injectable `BrowserBackend` (the live
`PlaywrightChatGPTBackend` wraps `erdos_common`). Every response carries an
**unattested** `AttestedModelIdentity` (`attested=False`) and can never count as
independent-model evidence. Each `run` uses a fresh isolated conversation and
records the UI model label, conversation URL, account class, timestamp,
prompt/response hashes, and runner version. Rate limiting **pauses** (cooldown
clamped to `<=120s`) and retries — it never terminates the run or marks the
mathematical problem failed; persistent throttling raises
`BrowserProviderUnavailable`, a transient-outage signal for the caller to
pause/resume, not a mathematical verdict. The control logic is fully tested against
a fake backend; the live path needs an authenticated Chromium profile
(`python3 solve_submit.py --login`) and the `browser` extra.

## D-014 — Aristotle API client is allowed but never a trust root
Per the operator contract, the Aristotle API may be used, but it must never be a
trust root (spec §9.6). **Decision:** `egmra/lean/aristotle_api.py` implements a
real `AristotleApiClient` over an injectable `AristotleTransport` (the live
`HttpAristotleTransport` reads `ARISTOTLE_API_KEY` from the environment only and
requires an `https://` base URL). `submit` enforces the licensing/confidentiality
gate before any source packet leaves the host; `poll` normalizes vendor status but
a vendor `COMPLETE`/`solved` **always** carries `promotable=False`; `download`
extracts the returned Lean into a per-job quarantine directory with a hardened
extractor that rejects absolute paths, `..` traversal, symlinks/hardlinks/special
files, oversized entries, and archive/zip bombs; `bind_local_replay` delegates the
only trust decision to a caller-supplied local verifier (the pinned kernel path),
treating any verifier error as a rejection. The existing CLI wrapper
(`aristotle_verifier.py`) is retained as a fallback. The transport/quarantine/replay
control flow is fully tested against a fake transport; the live path needs API
credentials and a real Lean/Mathlib re-check.


