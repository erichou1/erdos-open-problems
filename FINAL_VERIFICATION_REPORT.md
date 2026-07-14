# EGMRA Final Verification Report

Implementation of `docs/AUTONOMOUS_MATH_RESEARCH_ARCHITECTURE_2026.md`
(Evidence-Gated Mathematical Research Architecture).

Date: 2026-07-13 · Python 3.14.4 (`.venv`) · macOS.

---

## 1. Requirement totals

| Status | Count |
|---|---:|
| Total requirements (`IMPLEMENTATION_LEDGER.md`) | **120** |
| `VERIFIED` (code exists AND a test was written and observed to pass) | **120** |
| `PLANNED` | 0 |
| `IN_PROGRESS` | 0 |
| `BLOCKED` | 0 |
| `NOT_APPLICABLE` | 0 |

No requirement remains `PLANNED`, `PARTIAL`, `TODO`, `UNREVIEWED`, or `IN_PROGRESS`.
Ledger integrity: 0 duplicate requirement IDs.

Every top-level specification section (1, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15,
16) is represented in the ledger. Sections 2 (literature map) and 3 (comparison
tables) are prose/data; their actionable content is encoded in
`egmra/design_status.py` (design-status provenance) and `egmra/risks.py`.

## 2. What was built

A new, cohesive, tested `egmra/` package (**92 source modules**, **22 packages**,
**~10.8k LOC**) implementing the four planes and three nested searches, plus M0
safety patches to the existing pipeline.

| Plane / subsystem | Modules | Key behaviors |
|---|---|---|
| provenance | hashing, stage_identity, rules | canonical hashing, Merkle root, per-stage identity + cache incompatibility, provenance rules |
| policy | signed `FeaturePolicy` + `PolicyEnforcer` | HMAC-signed policy, non-overridable release features, per-entry-point checks |
| truth | entities, events, graph, validators, router, revocation, blackboard, views | append-only HMAC-chained event log, epistemic claim graph, type-specific evidence validators, SCC-aware revocation, least-privilege blackboard, SQLite/manifest views |
| intake (A) | statement_ir, interpretation, probes, contract | dual-parse Statement IR + reconciliation, interpretation lattice, paraphrase-invariance / mutation-covariance / executable counterexample probes, `ProblemContract` |
| corpus | status | dated status claims, conflict → `status_uncertain` |
| retrieval (D) | records, packet, service, premises, source_priority | `TheoremRecord`, frozen versioned `SourcePacket`, TF-IDF retriever, import auditor, separate novelty log, premise retrieval, claim-specific source matrix |
| oeis (C) | transforms, client, matching | 20 typed transforms (exact arithmetic), read-only cached client (submission refused), held-out match verification |
| compute (H) | spec, artifact, sandbox, service, backends | sandboxed (network-off) jobs, 6-way checked classification, replay, SAT/SMT/CAS interfaces + RUP unsat reconstruction, exact arithmetic |
| lean (I) | service, target_package, sentinels, coverage, blueprint, proof_state, sync, hardening, missing_library, aristotle_routing | Lean service API + `FormalCertificate` + `GoalCapsule`, L0–L5 staged workflow, risk-weighted RFC, PUCT + diagnostics routing, quarantine + independent-checker hardening, Aristotle routing/sandbox policy |
| search (G) | mechanism, verified_debt, blueprint, dedup, failure, bands, controller, programs, algorithms | mechanism fingerprints + MAP-Elites archive, frozen target-relative debt, AND/OR blueprint, 6-stage dedup, failure certificates, compute bands, additive-utility posterior controller, 12 program families, algorithm routing |
| agents (E) | authorities, profiles, prompts, runner | 7 durable authorities, method-profile diversity (≥2 axes), role prompts, attested model identity |
| verification (J) | referee, attacks, standards, aggregation | independent referee (obligations not score), 10 attacks + taint, T0–T5 + I/F/N/S/R/autonomy, pessimistic aggregation |
| release | gates, certificate, compiler, policy | five independent gates, signed `ReleaseCertificate` (never a confidence %), proof compiler from admitted claims only, kernel+intent+correspondence promotion policy |
| selection (B) | features, posterior, acquisition | 9 feature families, competing-risk posterior with censoring, `A_p` acquisition + Thompson + protected exploration |
| learning (K) | memory, calibration, expert_iteration | 6 never-conflated memory stores, Brier/ECE/false-promotion calibration, verified-only expert iteration |
| control | leases, throttle, parallel, recovery, congestion | leases/heartbeats, 120s-capped provider backoff (pause ≠ fail), parallel/serialize policy + reserved verifier pool, 13-row recovery table, congestion pricing |
| orchestrator | roles, checkpoint, loop | runtime roles, checkpoint/resume, `research()` 17-step loop |
| comms | human, render | intervention log + autonomy metadata, five-gate rendering with confidence-% guard |
| eval | levels, protocol, metrics, progress, ablations, stats, datasets | 7 levels + A/B/C tracks, 4-baseline protocol + time capsules, metrics + frozen RFC, durable-object progress gate, 13 ablations, pass@k guard, executable fixtures + pinned-benchmark manifests |
| meta | services, topology, models/registry, design_status, risks, config, cli, m0, m2 | 8 service contracts, 10-layer topology, local-bake-off model registry, design-status table, 24-risk register, layered config + secrets handling, CLI, M0 safety layer, M2 scale layer |

M0 patches to **existing** files (baseline preserved):
- `aristotle_verifier.py`: `verify_run` forces `require_kernel=True` on any promote/publish
  path — a vendor-only `COMPLETE` can never yield `passed=true` toward the gate.
- `promote_verified_run.py`: the promotion entry point enforces the signed feature
  policy (default policy disables promotion; `--policy` supplies a signed one).
- `tests/test_proof_pipeline.py`: the one promotion test now supplies a signed
  promotion-enabled policy (documented in DECISIONS.md D-011 below).

## 3. Tests & commands run

```
.venv/bin/python -m pytest egmra/tests/ tests/ -q      # full combined suite
.venv/bin/python -m compileall -q egmra                # all modules compile (exit 0)
.venv/bin/python -m pytest tests/ -q                   # existing baseline (unchanged)
```

### Results

| Suite | Result |
|---|---|
| `egmra/tests/` (21 files, 241 test functions) | **241 passed** |
| existing `tests/` (baseline) | **179 passed, 18 subtests** |
| **combined** | **420 passed, 18 subtests, 0 failed** |
| `compileall egmra` | exit 0 (all 92 modules compile) |
| `get_errors` (package + patched files) | no errors |
| stub scan (<6-line modules) | none |
| `TODO`/`FIXME`/`NotImplementedError` in source | none |

The M1 end-to-end vertical slice runs genuinely: a finite true statement flows
`intake → probes → cold pass → frozen packet → sandboxed exact computation →
replay → evidence router → SUPPORTED (T2) → proof compiler → five gates`, while a
false statement yields an `honest_triage_report` and promotion stays blocked by the
default feature policy. All 18 §13.6 acceptance criteria pass
(`egmra/tests/test_acceptance.py`).

## 4. Blocked requirements

None. Every requirement's implementation (interface + configuration + validation +
local/mock test) is complete and tested.

## 5. Known limitations & remaining manual validation

Per the task's external-dependency rule, integrations requiring credentials or
infrastructure are implemented as **real interfaces with configuration, validation,
and local/mock tests**; the *live external call* is not executed in this
environment. These are not unmet requirements — the requirement was the interface +
local test — but the live calls remain manually validatable:

| Integration | Interface + local test | Command to validate live (needs credentials/infra) |
|---|---|---|
| Real Lean kernel (`lake build`) | `egmra/lean/service.py` (injected `kernel_runner`), reuses `lean_verify.py`; `lean_kernel_check/` project | install Lean/Elan + Mathlib, then run `verify_project` against a pinned project (`lake exe cache get && lake build`) |
| Frontier model providers | `egmra/agents/runner.py` `AttestedRunner` (raises without a configured call); `DeterministicRunner` for tests | set `OPENAI_API_KEY`/`ANTHROPIC_API_KEY`/`GEMINI_API_KEY`, provide a `call` returning `(text, model, version, build_id)` |
| Aristotle CLI | `egmra/lean/aristotle_routing.py` + existing `aristotle_verifier.py` | `pip install aristotlelib`, `ARISTOTLE_API_KEY=…`, run `verify_run(..., promote_result=True)` (kernel replay forced) |
| OEIS HTTP | `egmra/oeis/client.py` (injected fetcher; offline default; mock-tested) | run with `OEISClient(offline=False)` + network; respects rate limits + AI-submission-forbidden policy |
| Postgres event store | `egmra/m2.py` `PostgresEventStore` (documents DDL, refuses to fake) | `psql "$DSN" -c "<schema_ddl>"`; JSONL `EventLog` satisfies the same contract for CI |
| OCI container sandbox | `egmra/compute/sandbox.py` `ContainerSandbox` (documents `docker run`, refuses to fake) | `docker run --network=none --read-only … python -I /job/job.py`; `SubprocessSandbox` (network-off) used for CI |
| SAT/SMT/CAS solvers | `egmra/compute/backends.py` protocols + stdlib exact arithmetic + RUP checker | install cvc5/z3/PySAT/Sage and wire a backend implementing the `SolverResult` contract |

Additional intrinsic limitations (from the spec itself, §15): semantic equivalence
can be hard; absence of prior art cannot be proved; frontier model families may
share training data (so provider diversity is recorded but not treated as proof
independence). The deterministic parsers used for the Statement IR are genuine but
weaker than model-family parsers (DECISIONS.md D-002); disagreement correctly
produces ambiguity nodes that block release rather than a wrong silent choice.

## 6. Evidence supporting the completion claim

1. `IMPLEMENTATION_LEDGER.md` — 120 requirements, each with source section,
   component, dependencies, `VERIFIED` status, and the exact test file that
   exercises it.
2. `IMPLEMENTATION_PLAN.md` — repository structure and milestones (M0/M1/M2) mapped
   to requirement IDs.
3. `DECISIONS.md` — recorded interpretations (D-001…D-011) for every ambiguity /
   contradiction resolved during implementation.
4. Reproducible test run: `420 passed, 18 subtests` on the combined suite; the
   existing 179-test baseline is unchanged.
5. Clean static checks: `compileall` exit 0, no `get_errors`, no stubs, no TODOs.
6. The 18 §13.6 acceptance tests encode the specification's own pass/fail criteria
   and all pass.

## DECISIONS addendum

- **D-011 — promotion entry point now enforces a signed policy.** M0 makes
  `promote_verified_run.promote` require a signed feature policy that enables
  promotion (default policy disables it). The single existing promotion test was
  updated to pass such a policy. This is the intended M0 behavior change
  ("enforce at every promotion entry point"), not a regression.

## Conclusion

The repository contains a working, tested implementation of the complete EGMRA
system described in the specification: the truth/search/control/communication
planes, the three nested searches, the five release gates, the M0 safety and
provenance repairs, the M1 end-to-end vertical slice, and the M2 scale interfaces.
All 120 extracted requirements are `VERIFIED` by 241 EGMRA tests (420 combined,
0 failures), and the specification's own 18 acceptance criteria pass. External
live calls that require credentials/infrastructure are implemented as real
interfaces with local/mock tests and exact documented validation commands, and are
explicitly not claimed to have been exercised live.
