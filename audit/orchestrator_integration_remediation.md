# Orchestrator, Intake, CLI, and Integration Remediation

Date: 2026-07-13  
Scope owner: `/root/orchestrator_integration_remediation`  
Audit posture: all pre-existing completion labels and tests were treated as untrusted.

## Executive result

The pre-fix orchestration was a collection of plausible objects, but several of
the security- and truth-critical objects were not consumed by the production
loop. In particular, workers could choose goal text, the loop self-approved its
own interpretation, worker-provided evidence metadata was trusted too far,
formal certificates stopped at a diagnostic report, source bytes/status were
not replayable from the event log, and the CLI could count a self-contained
fixture path as verified without an externally reviewed intent artifact.

The remediated local path now fails closed at those boundaries. Source bytes and
status are event-sourced; direct-first search, mechanism diversity, budget,
leases, capabilities, verified debt, computation replay, evidence routing,
formal certificate envelopes, referee checks, and current-log release
attestations are consumed in the production call path. A result cannot be
returned with a release certificate unless its goal is currently `SUPPORTED`
and both gates and certificate verify against the exact current event-log head.

This does **not** establish complete-spec implementation. Material external and
architectural limitations remain at the end of this report.

## Findings, reproductions, and remediation

### ORCH-001 — HIGH — production loop bypassed runner/search/control state

- **Pre-fix behavior:** model-runner output, mechanism fingerprints,
  quality-diversity bins, branch budgets, AND/OR structure, and verified debt
  could exist without determining branch execution. The claimed closed-loop
  search was therefore not demonstrated.
- **Reproduction:** production-path tests recorded worker calls and observed no
  enforced direct-first ordering, no consumed runner outputs, no unique
  fingerprint/QD state, and no independently computed debt delta.
- **Fix:** `egmra/orchestrator/loop.py` now consumes the cold-pass runner result,
  freezes its queries into the packet, uses `ProblemSelector`, instantiates
  mechanism-distinct `ResearchProgram` objects, registers graph `Branch`
  entities with fingerprints and QD bins, builds real GOAL/OR/AND/LEAF nodes,
  forces `direct_structural` first, charges a hard `BudgetLedger`, and updates
  posterior state from independently computed verified-debt reduction.
- **Regression:** `test_runner_cold_pass_and_budget_are_consumed_by_production_flow`
  and `test_non_positive_budget_is_rejected_before_worker_execution`.

### ORCH-002 — CRITICAL — stale or overprivileged workers could affect truth

- **Pre-fix behavior:** lease/capability classes were not a demonstrated
  production boundary. A worker result could be processed after lease expiry or
  without a packet/branch-scoped immutable view.
- **Reproduction:** a worker deliberately expired and transferred its own lease,
  then returned a forged claim/evidence batch.
- **Fix:** production execution now acquires a lease, passes its fencing token,
  rechecks the token immediately after the worker returns and before inspecting
  output, rejects the whole stale batch, and uses signed, resource-scoped
  authority tokens plus deeply immutable blackboard slices. Claim, computation,
  OEIS, and formal proposals traverse the blackboard authority boundary.
- **Regression:** `test_stale_fencing_token_rejects_worker_output_before_evidence_admission`.

### ORCH-003 — CRITICAL — worker-selected goal substitution and forged evidence

- **Pre-fix behavior:** a worker proposal could supply goal prose/formula and
  evidence fields that looked authoritative. Shape validation was not semantic
  authentication.
- **Reproduction:** adversarial workers proposed `True` as the locked goal,
  asserted successful exact computation without a service artifact, or omitted
  the immutable `ExperimentSpec.claim_ids` binding.
- **Fix:** the goal claim is always reconstructed from the selected locked
  interpretation. Generic worker evidence remains quarantined. Exact-computation
  evidence is reconstructed server-side only from a trusted `ComputeService`
  job/artifact, exact claim binding, qualifying classification, literal true
  output, matching content hashes, and a measured independent-environment
  replay. The resulting `Evidence` receives complete provenance and an evidence
  HMAC before `EvidenceRouter` admission.
- **Regressions:**
  `test_untrusted_worker_cannot_forge_computation_evidence`,
  `test_computation_without_locked_claim_binding_is_quarantined`,
  `test_false_computation_cannot_support_or_release_a_claim`, and
  `test_computation_replay_report_reaches_reproducibility_gate`.

### ORCH-004 — CRITICAL — orchestrator self-issued I2 intent approval

- **Pre-fix behavior:** a single-node lattice was automatically marked approved;
  the same production function then created an `IntentCertificate` with
  `reviewer_ids=["intake_authority"]`. No independent input or authentication was
  required. Raw strings therefore created I2 and unlocked evidence/release.
- **Reproduction:** call `research()` with a single unambiguous statement and no
  review service/artifact; the graph previously contained an approved intent
  certificate issued by the governor path.
- **Fix:** automatic approval and self-issuance were removed. `research()` now
  accepts only an explicit `intent_review`. I2 requires an HMAC-authenticated
  certificate bound to the exact source-byte hash, a stable immutable-semantic
  interpretation hash, and canonical informal-claim hash, with all five review
  methods, identified non-generator reviewer, conflict disclosure, and stated
  independence from intake/generation. Missing or forged review keeps evidence
  unadmitted and release unavailable. `release.intent_gate` independently checks
  the durable signature, so direct callers cannot obtain I2 from reviewer names.
- **Regressions:** `egmra/tests/test_intent_review_security.py` and
  `test_research_cannot_self_issue_semantic_intent_approval`.

### ORCH-005 — HIGH — source freeze was not replayable

- **Pre-fix behavior:** the `Problem` event contained only an original byte hash;
  exact bytes, source identifier, Statement-IR hash, and dated status assertions
  were absent. A restarted graph had `source_versions == []`.
- **Captured RED:**

  ```text
  frozen_source = replayed.problems["budgeted"].source_versions[0]
  E IndexError: list index out of range
  ```

- **Fix:** `ProblemContract` stores base64 exact bytes and binds `source_id` in
  the contract hash. `PROBLEM_FROZEN` now contains the byte content/hash,
  source identifier, Statement-IR hash, and serialized dated status claims.
- **Regression:** the runner/budget production-path test reopens a fresh
  `EpistemicGraph(EventLog(...))`, decodes the bytes, and verifies status source.

### ORCH-006 — HIGH — formal verification stopped before truth evidence

- **Pre-fix behavior:** the loop called Lean and appended a report, but a passing
  formal result was never converted into truth-plane `Evidence`; the formal
  service was disconnected from epistemic state.
- **Fix:** the loop now supplies graph-derived claim bindings and immutable
  artifact hashes to `LeanService.verify_declaration`. A passing authenticated
  `FormalCertificate` is accepted only alongside a separately signed, exact
  formal-correspondence review. The production `Evidence` carries the full
  certificate envelope, source hash, environment, certificate digest and all
  proof/source artifacts, intent/correspondence IDs, verifier identity, replay
  command, and evidence HMAC; it is then admitted through `EvidenceRouter`.
  Static scans, lambdas, caller-owned `COMPLETE` strings, missing correspondence,
  or mismatched bindings never promote truth.
- **Regressions:**
  `test_formal_candidate_reaches_lean_but_static_or_mock_result_cannot_promote`
  and `test_authenticated_formal_envelope_is_carried_into_truth_evidence`.

### ORCH-007 — CRITICAL — release freshness and bypass resistance were incomplete

- **Pre-fix behavior:** components could report a gate profile or cached success
  without proving it remained bound to the current log head. Learning and render
  paths also needed to consume authenticated truth rather than mutable status.
- **Fix:** release eligibility explicitly requires the current goal be
  `SUPPORTED`, nonblocked intake/status, a complete assembly, and a clean referee.
  Gates consume a signed `TruthSnapshot` from the event log. Promotion and
  release-certificate signing receive the current `EventLog`. Immediately before
  `research()` returns, it re-verifies goal status, fresh gate attestation, and
  certificate against the exact current head; failure clears the certificate.
  Render also verifies the certificate against the current log, so any later
  event invalidates cached release. Verified semantic learning receives the same
  snapshot/log/gates instead of trusting labels.
- **Regressions:**
  `test_promoted_scoped_result_has_current_verifiable_release_certificate`,
  `test_unresolved_interpretation_blocks_certificate_even_with_support`,
  `test_independent_referee_defect_blocks_release`, and
  `test_missing_referee_attacks_fail_closed`.

### ORCH-008 — HIGH — OEIS, referee, and learning paths were semantically weak

- **Pre-fix behavior:** generated sequences, attack results, and memory objects
  could be present without a safe production effect; missing checks risked
  optimistic success.
- **Fix:** generated sequences become authorized next-experiment proposals and
  reach only the injected read-only OEIS client; results remain heuristic and
  never become mathematical evidence. Missing OEIS is explicit. Cold/branch
  outputs enter problem-local quarantine only. Cross-problem semantic memory is
  admitted only after current T2+/I2/R2 authenticated gates. The default attack
  evaluator executes concrete checks and missing required attacks fail closed.
- **Regressions:**
  `test_generated_sequence_reaches_read_only_oeis_without_becoming_truth`,
  `test_cold_and_branch_learning_is_quarantined_problem_local`, and referee tests.

### CLI-001 — HIGH — fixture evaluation could exaggerate verification

- **Pre-fix behavior:** the fixture worker rewrote `_isprime(n)` to `True`; CLI
  expectation logic could trust labels/objects rather than current gate
  attestation; policy signing had unsafe fallback/overwrite edges.
- **Fix:** the fixture executes a real deterministic primality predicate. Verified
  expectations require a freshly attested gate profile against the graph log.
  Expectation mismatch has exit code 3. `run` requires an externally signed
  `--intent-review` artifact for verified fixtures. `policy-sign` has no fallback
  key, rejects duplicate JSON keys, uses exclusive no-follow creation at mode
  0600, refuses overwrite/symlink, and never prints the secret. Configuration
  rejects all local trust keys in files.
- **Regressions:** 17 CLI/config tests, including false-prime, missing key,
  unattested gate, symlink, overwrite, and absent intent review cases.

### INTAKE-001 — HIGH — parser semantics and malformed input were underchecked

- **Pre-fix behavior:** parsers could invent a binder, treat arbitrary single
  letters as quantified variables, truncate clauses at commas, or collapse
  domain/definition distinctions. Empty input could proceed too far.
- **Fix:** quantified binders/domains are extracted rather than invented;
  semantic keys preserve domains, scopes, definitions and parameter regimes;
  malformed/empty input and untyped quantified domains fail closed. Subsequent
  root-owned hardening also froze Statement IR, required parser-family/raw-byte
  bindings, represented nested quantifiers/constraints/definitions, marked probe
  execution, and made unexecuted probes release-blocking.
- **Regressions:** 18 intake tests plus malformed-input orchestration coverage.

## Verification evidence

Focused post-fix command:

```bash
.venv/bin/python -m pytest -q \
  egmra/tests/test_intake.py \
  egmra/tests/test_intent_review_security.py \
  egmra/tests/test_orchestrator.py \
  egmra/tests/test_adversarial_orchestrator.py \
  egmra/tests/test_cli.py \
  egmra/tests/test_eval.py
```

Fresh final result: **71 passed in 6.83s**, zero failures/skips.

The new independent adversarial orchestration file contains 17 production-path
tests; the intent-authentication file adds 2 direct gate/signature tests.

The last full EGMRA run from this subtask produced **510 passed, 13 failed in
10.04s**. All 13 failures were isolated to newly introduced
`egmra/tests/test_adversarial_m2.py` checks for object-store/DSN/M2 assembly
hardening and were handed to the root/security workstream. They were not hidden,
skipped, or modified by this subtask.

Additional checks:

- `.venv/bin/python -m compileall -q egmra`: exit 0.
- `git diff --check -- .env.example README.md SETUP_GUIDE.md egmra audit/orchestrator_integration_remediation.md`:
  exit 0.
- Ruff is not installed in the audit environment (`No module named ruff`).

## Residual limitations and honest classification

1. **HIGH — formal-correspondence reviewer disclosure:** the production
   orchestration now requires at least one reviewer ID before admitting formal
   evidence, and HMAC signature/bindings are checked. However, the shared
   correspondence signer/gate still needs root-owned hardening to require
   complete independence/conflict disclosures for every F2 direct call. This was
   reported to root and must not be represented as closed until fixed/tested.
2. **Local symmetric-key trust boundary:** intent and correspondence HMACs prove
   integrity/authentication relative to locally provisioned verifier secrets, but
   local M1 does not provide hardware/process isolation of those verifier keys
   from all trusted host code. Worker/model sandboxes do not receive them.
3. **No live external verification in this subtask:** OEIS HTTP, a real pinned
   Lean/lake checker, Postgres, Docker, provider models, and Aristotle were not
   exercised. The positive formal integration test uses the production
   structured checker protocol with a deterministic fake subprocess response;
   it proves envelope plumbing, not live Lean correctness.
4. **Persistence gaps:** default leases and verified semantic memory are
   process-local unless explicitly injected with durable backing. Checkpoint and
   resume objects exist but are not integrated per iteration into the live
   `research()` loop. There is no demonstrated SQLite materialized view here.
5. **Closed-loop gaps:** verified learning is authenticated but does not yet
   durably alter later problem selection/program priors. The runner is serial,
   not a demonstrated distributed parallel scheduler.
6. **Source metadata limits:** the API persists exact bytes/hash, `source_id`, IR
   hash and supplied dated status claims, but cannot invent unavailable URL,
   upstream commit, retrieval timestamp, or license metadata.
7. **External-status limitation:** supplied status claims are reconciled and
   persisted; this subtask did not perform a live independent status audit.
8. **Sandbox limitation:** exact compute evidence is independently replayed and
   locally restricted, but true OS/container isolation remains dependent on the
   separate sandbox/Docker workstream and available infrastructure.

## Verdict for this scope

The remediated local integration path is materially stronger and its focused
tests pass, but the complete specification is **not verified complete** by this
work. The correct aggregate classification must retain external blocks and the
nonexternal residuals above rather than infer completeness from test count.
