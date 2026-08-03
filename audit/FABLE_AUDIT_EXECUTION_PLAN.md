# FABLE Independent Audit and Remediation Execution Plan

> The user-provided thirteen-phase brief is the governing specification for this audit. This file records execution order and contamination controls; it does not replace `AUTONOMOUS_MATH_RESEARCH_ARCHITECTURE_2026.md`.

## Goal

Independently determine whether the claimed EGMRA implementation faithfully implements the complete architecture, remediate every repository-local defect with test-first evidence, and issue a final verdict that distinguishes verified local behavior from mocked, static-only, and externally blocked behavior.

## Isolation and preservation

- Initial commit: `4b4ec96f1c81492af02f814c65825a5106e0af60`.
- Audit branch: `audit/egmra-independent-remediation-20260713`.
- The claimed implementation is an uncommitted overlay on `main`, so a clean worktree from `HEAD` would omit it. The overlay was moved intact to the audit branch without changing file contents.
- The exact pre-audit working-tree snapshot is in `audit/FABLE_INITIAL_GIT_STATUS.txt`.
- Existing proof-pipeline, proof-run, triage, and generated-data changes are user-owned and out of remediation scope unless a verified EGMRA defect requires an overlapping edit.

## Execution order

1. Read all 2,302 specification lines before opening any previous ledger, plan, decisions, report, implementation, or test.
2. Create `FABLE_INDEPENDENT_REQUIREMENTS.md` with independent F-REQ identifiers, exact line provenance, semantics, failure behavior, integrations, acceptance conditions, dependencies, and ambiguity notes.
3. Compare prior claims and create discrepancy, code-inventory, and baseline-verification reports.
4. Build a requirement-by-requirement traceability matrix and independently assess test quality and reachability.
5. Audit truth, search, control, communication, intake, retrieval, OEIS, sandbox, Lean, authorities, T0-T5 verification, release, learning, orchestration, evaluation, and external integrations.
6. For each confirmed defect, record a finding, reproduce it, establish root cause, add a failing test, implement the smallest complete correction, verify the reproduction no longer succeeds, and search for equivalent defects.
7. Reproduce M1 and inject failure at every stage; independently execute all eighteen section 13.6 acceptance criteria with negative cases.
8. Run a fresh full suite, security/adversarial tests, restart/concurrency tests, entry-point smoke tests, external capability probes, and a final independent code review.
9. Finalize all ten required deliverables and report quantitative pre-fix/post-fix statuses without upgrading unavailable external behavior.

## Non-negotiable evidence rules

- No requirement is `VERIFIED` from names, comments, mocks, static inspection alone, or a passing test written around the same implementation.
- Runtime reachability, required integration, positive and negative behavior, and failure semantics are mandatory for `VERIFIED`.
- External levels are reported separately: interface, configuration, mock, local integration, real service, failure/recovery, and production readiness.
- No production fix is written before its regression test has failed for the expected reason.
- No completion or pass claim is made without fresh command output and exit status.
