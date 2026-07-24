# EGMRA Verification Evidence

**Audit date:** 2026-07-14  
**Repository:** `/Users/eric/workspace/erdos/erdos_problems`  
**Evidence rule:** outputs below were observed in fresh commands during this audit. Secret values are represented as `<32-byte-audit-key>` and the Aristotle API value is never shown.

## 1. Specification and code inspection

Normative sources read completely:

```text
/Users/eric/.codex/attachments/26df0b00-b0f8-4e21-87d2-0519b472ffc5/pasted-text.txt  (1,108 lines)
docs/AUTONOMOUS_MATH_RESEARCH_ARCHITECTURE_2026.md                         (2,302 lines)
DECISIONS.md
```

Major code areas inspected included every package under `egmra/` and specifically intake, status, selection, retrieval, OEIS, agents, search, truth, compute, Lean/Aristotle, release, memory/learning, orchestration/campaign/checkpoint, provenance/event stores, CLI/config, prompts, schemas, and all EGMRA tests. Previous reports and ledgers were not accepted as evidence.

## 2. Baseline and final test suites

Baseline before remediation:

```bash
.venv/bin/python -m pytest -q -rs egmra/tests tests
```

```text
1071 passed, 4 skipped, 44 subtests passed
```

The four skips were live PostgreSQL tests gated on `EGMRA_TEST_POSTGRES_DSN`; they were subsequently enabled rather than silently accepted.

PostgreSQL service and previously skipped tests:

```bash
docker run --rm -d --name egmra-audit-postgres \
  -e POSTGRES_PASSWORD=egmra_audit -e POSTGRES_DB=egmra_audit \
  -p 55432:5432 postgres:16
export EGMRA_TEST_POSTGRES_DSN='postgresql://postgres:egmra_audit@127.0.0.1:55432/egmra_audit'
.venv/bin/python -m pytest -q -rs \
  egmra/tests/test_campaign_store.py egmra/tests/test_m2_postgres_conformance.py
```

```text
22 passed
```

Final collection and complete suite, with PostgreSQL enabled:

```bash
export EGMRA_TEST_POSTGRES_DSN='postgresql://postgres:egmra_audit@127.0.0.1:55432/egmra_audit'
.venv/bin/python -m pytest --collect-only egmra/tests tests
.venv/bin/python -m pytest -q -rs egmra/tests tests
```

```text
1173 tests collected
........................................................................ [ 96%]
.........................................                                [100%]
exit status 0
```

The quiet configuration suppresses the ordinary numeric summary when no skips/failures exist; collection count and process exit were checked separately.

Focused failure-injection/regression command:

```bash
.venv/bin/python -m pytest -vv \
 egmra/tests/test_production_wiring.py::test_execute_finite_experiment_reports_sandbox_failure_detail \
 egmra/tests/test_sign_review_cli.py::test_sign_review_intent_can_bind_a_regression_fixture \
 egmra/tests/test_adversarial_orchestrator.py::test_circular_claim_proposal_batch_is_rejected_without_crashing_run \
 egmra/tests/test_adversarial_orchestrator.py::test_worker_crash_is_recorded_and_other_branches_remain_schedulable \
 egmra/tests/test_adversarial_orchestrator.py::test_malformed_evidence_and_formal_artifacts_are_quarantined \
 egmra/tests/test_adversarial_orchestrator.py::test_formal_verifier_failure_is_recorded_without_aborting_research \
 egmra/tests/test_adversarial_orchestrator.py::test_promoted_scoped_result_has_current_verifiable_release_certificate
```

```text
collected 7 items
... 7 named tests PASSED ...
7 passed in 0.68s
```

The wider suite also exercises invalid JSON, repair retries, duplicate events, stale/revoked evidence, forged signatures, malformed certificates, corrupted JSONL/PostgreSQL state, interrupted leases, exhausted budgets, retrieval failures, archive traversal/symlinks/bombs, Lean failure, and provider throttling. The final addition, `test_referee_attack_semantics.py`, contributed twelve tests showing that an attested correspondence-bound kernel replay can discharge formal-only computation/reconstruction attacks while every informal, unattested, failed, mixed-bad-replay, or incomplete-compilation variant remains fail-closed.

## 3. Corrected finite-computation proof boundary

Policy and intent artifacts were signed with independent test-domain keys, then the real fixture path was run:

```bash
export EGMRA_POLICY_KEY='<32-byte-audit-key>'
export EGMRA_INTENT_REVIEW_KEY='<32-byte-audit-key>'
.venv/bin/egmra policy-sign \
  --input /private/tmp/egmra-audit-20260714/policy-promotion-template.json \
  --output /private/tmp/egmra-audit-20260714/policy-promotion-v3.json
.venv/bin/egmra sign-review intent --fixture fx-true-square \
  --reviewer-id audit-independent-reviewer \
  --output /private/tmp/egmra-audit-20260714/fixture-intent-v3.json
.venv/bin/egmra run --fixture fx-true-square --provider deterministic --budget 100 \
  --policy /private/tmp/egmra-audit-20260714/policy-promotion-v3.json \
  --intent-review /private/tmp/egmra-audit-20260714/fixture-intent-v3.json \
  --retrieval none --oeis offline
```

Key output after remediation:

```json
{
  "problem_id": "fx-true-square",
  "outcome": "verified_finite_or_conditional_result",
  "proof_complete": false,
  "candidate_assembly_complete": true,
  "result_state": "COMPUTATIONAL_EVIDENCE",
  "gate_profile": {"truth":"T2","intent":"I2","formal_correspondence":"N/A","reproducibility":"R2"},
  "failures": []
}
```

Before the fix, the identical T2 result rendered `proof_complete: true`. The current output is the required finite-evidence boundary.

Independent event-chain verification:

```bash
export EGMRA_EVENT_KEY='<32-byte-audit-key>'
.venv/bin/egmra verify-events \
  --events egmra_runs/fx-true-square.1784026912628654000-217-ae68bd80.jsonl \
  --run-id fx-true-square.1784026912628654000-217-ae68bd80
```

```json
{"events":10,"merkle_root":"a77cb5e9576dad12a60e91511326064a990f6085146b6bcd93a489980821ab18","integrity":true}
```

## 4. Representative task traces

### 4.1 Trivial theorem

```bash
egmra run --statement 'Prove that for all natural numbers n, n = n.' \
  --predicate 'n == n' --provider deterministic --budget 20 \
  --policy policy-promotion-v3.json --retrieval none --oeis offline
```

```json
{"problem_id":"adhoc-b47fd50463c0dae5","outcome":"honest_triage_report","proof_complete":false,"result_state":"OPEN_NO_PROGRESS","event_count":9,"failures":["intent_review_unavailable"]}
```

This is honest but demonstrates that the deterministic path is a fixture/test provider, not a proof discoverer.

### 4.2 False statement

```bash
egmra run --statement 'Prove that for all natural numbers n, n < 3.' \
  --predicate 'n < 3' --provider deterministic --retrieval none --oeis offline
```

```json
{
  "proof_complete": false,
  "result_state": "CANDIDATE_DISPROOF",
  "rationale": "counterexample probe 'counterexample_search' failed: counterexample found at n=3"
}
```

This run failed before remediation because the conclusion was incorrectly parsed as a domain restriction.

### 4.3 Underspecified statement

A statement referring to an unnamed sequence and contradictory growth/boundedness wording produced:

```json
{"outcome":"honest_triage_report","proof_complete":false,"result_state":"BLOCKED_BY_INTERPRETATION","event_count":2}
```

No deep branch was allowed to manufacture a target.

### 4.4 Open-problem-style task

```bash
egmra run --erdos 601 --provider deterministic --retrieval corpus --oeis offline
```

```json
{"problem_id":"erdos-601","outcome":"honest_triage_report","proof_complete":false,"result_state":"BLOCKED_BY_INTERPRETATION","event_count":2}
```

The packaged corpus produced 613 source records in the retrieval probe, but problem #601 did not advance to mathematical exploration because its interpretations disagreed.

### 4.5 Standard known theorem / finite computation

The `fx-true-square` trace in section 3 ran a real restricted exact computation plus independent replay. It achieved T2/R2 and correctly stopped at `COMPUTATIONAL_EVIDENCE`; it did not pretend that bounded enumeration proved the universal theorem.

An additional signed `fx-true-even-sum` run stopped at `BLOCKED_BY_INTERPRETATION` with `intent_review_rejected`, demonstrating the unresolved inability of review to select an interpretation after parser disagreement.

## 5. Primary browser ChatGPT run

The first browser run produced useful-looking JSON, but rendered Markdown removed backslashes inside JSON string source, yielding invalid JSON such as nested unescaped quotes in `inputs.get("limit", 1000)`. This established a transport defect rather than simple model noncompliance.

After changing the protocol to one fenced JSON object plus base64 Python/Lean fields, the fresh run was:

```bash
egmra run --provider browser \
  --statement 'Prove that for all natural numbers n, n = n.' \
  --predicate 'n == n' --retrieval none --oeis offline --budget 6 \
  --policy /private/tmp/egmra-audit-20260714/policy-browser-v2.json
```

Observed:

```json
{
  "problem_id": "adhoc-b47fd50463c0dae5",
  "outcome": "honest_triage_report",
  "proof_complete": false,
  "event_count": 19,
  "result_state": {
    "state": "OPEN_NO_PROGRESS",
    "rationale": "the interpretation was fixed and the problem attempted, but no supporting evidence was produced"
  },
  "budget": {"total":6.0,"spent":4.575,"remaining":1.425}
}
```

Runtime facts:

- six model exchanges were recorded across cold/deep stages;
- no malformed or unparseable model-output failure occurred after the transport fix;
- the model proposed claims, experiments, queries, and sequences;
- three experiments failed under the restricted executor and two offline OEIS queries missed cache;
- no supported subclaim, informal-review evidence, or formal certificate existed;
- the result therefore remained `OPEN_NO_PROGRESS`.

The computation diagnostics and prompt were subsequently improved so future runs identify the exact failure and avoid unsupported method syntax.

## 6. Lean and Aristotle

Pinned local project build:

```bash
cd aristotle_lean_project
lake --version
lean --version
lake build
```

```text
Lake version 5.0.0-src (Lean version 4.28.0)
Lean (version 4.28.0 ...)
Build completed successfully (8027 jobs).
```

Real local kernel replay:

```bash
export EGMRA_LEAN_CHECKER_KEY='<32-byte-audit-key>'
egmra formalize --formalizer local \
  --lean-file aristotle_lean_project/AristotleProject.lean \
  --declaration egmra_project_builds --expected-type True \
  --lean-project aristotle_lean_project --mathlib-commit v4.28.0
```

```json
{
  "formalizer":"local",
  "declaration":"egmra_project_builds",
  "expected_type":"True",
  "sealed":true,
  "promotable_local_replay":true,
  "checker_id":"egmra-local-lean-kernel"
}
```

Live Aristotle probe (credential value loaded from the parent `.env`, never printed):

```bash
egmra formalize --formalizer aristotle --prompt 'Prove True' \
  --declaration egmra_project_builds --expected-type True \
  --lean-project aristotle_lean_project --mathlib-commit v4.28.0
```

```json
{"error":"RuntimeError","detail":"Aristotle API request failed (401): Invalid API key"}
```

Exit status was 2 and stderr contained no traceback after remediation. No claim of live Aristotle functionality is made.

## 7. Live retrieval and OEIS

Fresh network probes returned:

```text
OEIS Fibonacci query: 10 entries; fresh response; 64-character content hash
arXiv:             2 auditable records
Crossref:          2 auditable records
Semantic Scholar: direct request failed HTTP 429
MathOverflow:      1 auditable record
```

The scholarly aggregate returned the successful sources but did not expose the Semantic Scholar failure. This is recorded as unresolved gap U-10 rather than as a successful all-source retrieval.

No OEIS match or literature record was treated as proof.

## 8. Five-worker, PostgreSQL-backed campaign

```bash
export EGMRA_POSTGRES_DSN='postgresql://postgres:egmra_audit@127.0.0.1:55432/egmra_audit'
egmra campaign --erdos-range 601-605 \
  --campaign-id audit-five-worker-final-20260714 \
  --state-store postgres --event-store postgres \
  --workers 5 --provider deterministic --budget 3 \
  --policy /private/tmp/egmra-audit-20260714/policy-promotion-v3.json \
  --retrieval corpus --oeis offline
```

```json
{
  "total":5,
  "by_status":{"done":4,"failed":1},
  "complete":true,
  "workers":{
    "erdos-601":{"worker_id":"w0","status":"done","attempts":1,"result_state":"BLOCKED_BY_INTERPRETATION"},
    "erdos-602":{"worker_id":"w1","status":"done","attempts":1,"result_state":"BLOCKED_BY_INTERPRETATION"},
    "erdos-603":{"worker_id":"w2","status":"done","attempts":1,"result_state":"BLOCKED_BY_INTERPRETATION"},
    "erdos-604":{"worker_id":"w3","status":"done","attempts":1,"result_state":"BLOCKED_BY_INTERPRETATION"},
    "erdos-605":{"worker_id":"w4","status":"failed","attempts":1,"result_state":"SourceResolutionError: Erdős problem #605 has no section in the local corpus snapshot"}
  },
  "concurrency":{"max_observed_concurrency":5,"distinct_workers":5,"total_runs":5}
}
```

Resume/status command:

```bash
egmra campaign --campaign-id audit-five-worker-final-20260714 \
  --state-store postgres --event-store postgres --status
```

It returned the same terminal assignments without duplicating successful work. This verifies durable problem-level resume, cross-campaign event namespacing, true five-worker overlap, and single-attempt handling for the typed permanent source error. Stage-level resume remains absent.

## 9. Ranked production-browser launch

The retired `run_continuous.py` was not used: it correctly refuses by default because it drives the legacy `ProofPipeline`. The supported ranked path was launched directly:

```bash
egmra campaign --triage triage --triage-lane current --max-problems 5 \
  --campaign-id egmra-current-browser-20260714 \
  --state egmra_campaigns/current-browser-20260714.json \
  --outcome-ledger egmra_outcomes/current-browser-20260714.jsonl \
  --provider browser --workers 5 --worker-rounds 2 --budget 50 \
  --policy /private/tmp/egmra-audit-20260714/policy-promotion-v3.json \
  --retrieval corpus --oeis offline
```

The current lane selected #312, #1104, #153, #197, and #77, and all five statements resolved. The first launch exposed a live-only integration defect: every async tab checked for the React composer immediately after `domcontentloaded`, failed with `Could not find ChatGPT input box`, and the campaign consumed 25 ordinary retries. After adding a bounded visible-composer wait, a fresh `egmra-current-browser-v2-20260714` launch reached:

```json
{
  "by_status":{"leased":5},
  "complete":false,
  "workers":{
    "erdos-312":{"worker_id":"w0","status":"leased","attempts":1},
    "erdos-1104":{"worker_id":"w1","status":"leased","attempts":1},
    "erdos-153":{"worker_id":"w2","status":"leased","attempts":1},
    "erdos-197":{"worker_id":"w3","status":"leased","attempts":1},
    "erdos-77":{"worker_id":"w4","status":"leased","attempts":1}
  }
}
```

This confirms that ranked selection now reaches the single EGMRA pipeline and five browser tabs survive startup. It is launch/progress evidence, not proof-completion evidence.

The latest status captured during the audit had completed three first attempts—#1104 and #77 as `BLOCKED_BY_INTERPRETATION`, #197 as `OPEN_NO_PROGRESS`—while #312 and #153 remained leased on first attempts with three branch-open events each. No problem had retried and no release was claimed.

The requested T2 lane was checked before launch. A mechanical pass over all 43 ranked IDs found 0 resolvable and 43 `SourceResolutionError` results because the resolver uses the open-only corpus snapshot. This includes #742, #848, #19, #475, and #506. The complete lane-coverage failure is recorded as gap U-25; none was silently skipped or described as a mathematical failure.

## 10. Security and failure behavior covered

| Required injection | Evidence |
|---|---|
| Invalid/malformed JSON | Runner parser/repair tests and first live browser failure |
| Hallucinated/invalid citations | source record/import-auditor adversarial tests; not yet integrated with branch prose |
| Circular dependencies | focused cycle test passed; run continues |
| Stale evidence | result-state and certificate freshness tests fail closed |
| Verifier disagreement/failure | attack and Lean failure tests block promotion without aborting |
| Revoked claims | revocation cascade and stale release tests |
| Worker crash | focused branch crash-isolation test passed |
| Duplicate events | JSONL/PostgreSQL idempotency tests |
| Interrupted run/expired lease | campaign fencing/recovery tests; only whole-attempt resume |
| Corrupted state | HMAC, symlink, malformed/collision persistence tests |
| Retrieval failure | client error tests; scholarly aggregate suppression remains a defect |
| Formalization failure | malformed candidate and verifier-exception focused tests |
| Exhausted budgets | budget/controller tests; honest incomplete result |
| False-proof prevention | T2 renderer regression, gate/release/correspondence adversarial suites |

## 11. Evidence artifacts

Audit runtime outputs were retained outside the repository at:

```text
/private/tmp/egmra-audit-20260714/
```

Notable files include `browser-v2.json`, `browser-v2-events/`, `fixture-run-v3.json`, `formalize-local.json`, `campaign-five-worker.json`, `campaign-resume-status.json`, `failure-injection-final.txt`, and `full-suite-final.txt`. These are transient machine-local artifacts; authoritative repository deliverables are the three Markdown reports and the code/tests.

## 12. Completion claim supported by this evidence

The codebase now has stronger false-proof boundaries and more robust, observable component behavior. The evidence does **not** support “implemented and working end to end.” It supports the audit verdict:

**NOT RELIABLY FUNCTIONAL**
