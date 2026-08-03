# Checkpoint / Resume Adversarial Audit and Remediation

## Scope and verdict

Audited `egmra/orchestrator/checkpoint.py` against specification §10.4
(lines 1654-1680) and independent requirements F-REQ-117, F-REQ-118,
F-REQ-175, F-REQ-176, and the checkpoint portion of F-REQ-187.

Pre-fix verdict: **INCORRECT / TEST-ONLY**. The sole existing checkpoint test
passed, but the checkpoint was a shallow data bag, its hash omitted most state,
and `resume()` did not prove that the checkpoint belonged to the supplied event
history.

Post-fix local-boundary verdict: **PARTIAL**. The in-memory checkpoint and resume
decision are now strict, immutable, authenticated, prefix-bound, and covered by
adversarial tests. Full F-REQ-117/F-REQ-118 remain unverified because no durable
checkpoint serializer/store or production resume loop exists, and lease
reassignment, graph reconstruction, high-trust replay, and actual continuation
are not implemented by this module.

## Findings and remediation

### CHK-001 — Mutable, partially hashed, self-forgeable checkpoint

- **Finding ID:** CHK-001
- **Severity:** HIGH
- **Affected F-REQ IDs:** F-REQ-117, F-REQ-118
- **Specification source:** §10.4 lines 1654-1673
- **Files and line ranges:** pre-fix `egmra/orchestrator/checkpoint.py:20-46`;
  post-fix `egmra/orchestrator/checkpoint.py:52-349`
- **Symbols:** `Checkpoint`, `Checkpoint.checkpoint_hash`,
  `Checkpoint.verify_checkpoint_hash`
- **Expected behavior:** A checkpoint is immutable, every semantic field changes
  its identity, malformed state fails closed, and a caller cannot authorize
  forged state merely by recomputing a public content hash.
- **Observed behavior:** Nested dictionaries remained caller-mutable;
  `checkpoint_hash()` committed only sequence, Merkle root, problem hash, graph
  hash, and closure; controller state, interpretations, budgets, seeds, leases,
  caches, rate-limit state, and schema version were omitted. There was no stored
  seal or authentication.
- **Reproduction command or test:** Initial run of
  `python -m pytest -q egmra/tests/test_adversarial_checkpoint.py` failed
  `test_checkpoint_is_deeply_immutable_and_detached_from_inputs`,
  `test_checkpoint_hash_commits_every_semantic_field`, and
  `test_resume_fails_closed_if_checkpoint_contents_are_corrupted`. A later
  red test, `-k recomputing`, demonstrated that a re-sealed forged budget was
  accepted (`1 failed`).
- **Root cause:** `dataclass(frozen=True)` protected only attribute rebinding;
  nested maps were shallow-copied, and the hand-written hash payload omitted
  most fields. A content digest was treated as authority without a secret.
- **Impact:** A caller could mutate or forge controller/budget/cache state while
  retaining a superficially valid checkpoint, undermining deterministic replay
  and cache safety.
- **Whether existing tests detected it:** No. The prior test asserted only a
  global closure comparison and one cache name.
- **Fix performed:** Added recursive immutable detachment, strict top-level and
  nested schemas, finite numeric checks, SHA-256 validation, a canonical record
  covering every current semantic field, a stored seal, and HMAC-SHA256
  authentication with mandatory `EGMRA_CHECKPOINT_KEY` (minimum 32 bytes).
  Documented the new trust key in `.env.example` and `SETUP_GUIDE.md`.
- **Regression test added:** `test_checkpoint_is_deeply_immutable_and_detached_from_inputs`,
  `test_checkpoint_hash_commits_every_semantic_field`,
  `test_resume_fails_closed_if_checkpoint_contents_are_corrupted`,
  `test_recomputing_a_plain_content_hash_cannot_forge_checkpoint_state`, and
  `test_checkpoint_requires_a_secret_and_rejects_the_wrong_verification_key`.
- **Post-fix verification:** All 14 checkpoint adversarial tests and all 38
  checkpoint/orchestrator/acceptance tests pass in the final focused run.
- **Residual limitation:** There is no durable serializer or external checkpoint
  anchor, key identifier, or key-rotation protocol. HMAC authenticity assumes
  the checkpoint service keeps its key outside untrusted workers.
- **Confidence:** HIGH for the tested local boundary; LOW for real restart
  durability because no persisted checkpoint path exists.

### CHK-002 — Resume accepted a checkpoint from another valid event log

- **Finding ID:** CHK-002
- **Severity:** HIGH
- **Affected F-REQ IDs:** F-REQ-116, F-REQ-117, F-REQ-118
- **Specification source:** §10.4 lines 1656-1673
- **Files and line ranges:** pre-fix `egmra/orchestrator/checkpoint.py:78-96`;
  post-fix `egmra/orchestrator/checkpoint.py:362-402,431-508`
- **Symbols:** `take_checkpoint`, `_prefix_matches`, `resume`
- **Expected behavior:** Resume verifies the checkpoint's exact run, sequence,
  last event, and Merkle root against the corresponding prefix, while accepting
  a valid append-only tail.
- **Observed behavior:** `resume()` checked only that the supplied current log
  was internally valid. Any other valid log was accepted; checkpoint sequence
  and Merkle root were not compared at all.
- **Reproduction command or test:** The initial adversarial run failed
  `test_resume_rejects_checkpoint_from_another_valid_log`; two different valid
  logs with the same run label produced `ResumeReport(ok=True)`.
- **Root cause:** Current-head integrity and checkpoint-to-history binding were
  conflated.
- **Impact:** State from one history could be resumed against another, permitting
  stale or unrelated controller/cache state to influence work.
- **Whether existing tests detected it:** No.
- **Fix performed:** Checkpoints now bind `run_id`, `last_sequence`,
  `last_event_id`, and prefix Merkle root. Resume validates current log integrity
  and recomputes the exact historical prefix. A tail appended after checkpoint
  creation remains valid.
- **Regression test added:**
  `test_resume_rejects_checkpoint_from_another_valid_log`,
  `test_resume_accepts_the_exact_prefix_with_a_valid_appended_tail`,
  `test_resume_rejects_a_resealed_but_inconsistent_sequence_and_merkle`, and
  `test_resume_fails_closed_on_event_log_corruption`.
- **Post-fix verification:** The cross-log, inconsistent-prefix, corrupt-log,
  and appended-tail cases all pass.
- **Residual limitation:** Two byte-identical histories with the same run ID are
  intentionally the same content-addressed logical prefix; no physical storage
  identity is recorded. Snapshot graph contents are not reconstructed or
  compared to `graph_view_hash` by this module.
- **Confidence:** HIGH.

### CHK-003 — Cache invalidation was global and identity-free

- **Finding ID:** CHK-003
- **Severity:** HIGH
- **Affected F-REQ IDs:** F-REQ-117, F-REQ-118, F-REQ-175, F-REQ-176, F-REQ-187
- **Specification source:** §10.4 lines 1664-1679; §13.6 lines 2061-2062 and 2073
- **Files and line ranges:** pre-fix `egmra/orchestrator/checkpoint.py:85-88`;
  post-fix `egmra/orchestrator/checkpoint.py:167-221,415-428,489-499`
- **Symbols:** `_validate_stage_caches`,
  `_validate_current_stage_fingerprints`, `resume`
- **Expected behavior:** Each cache is bound to artifact, replay policy, and
  actual stage compatibility identity; only proven-compatible entries survive.
- **Observed behavior:** Cache values were arbitrary (`"cache1"`). If one global
  closure string changed, every cache was invalidated; if it did not, every cache
  was reused. Runner/adjudicator/model/policy identity was not consumed.
- **Reproduction command or test:** Initial adversarial run failed
  `test_resume_supports_precise_per_stage_cache_invalidation` because `resume`
  had no per-stage input, and failed
  `test_missing_stage_identity_invalidates_cache_even_when_global_closure_matches`.
- **Root cause:** The checkpoint stored no typed cache compatibility contract and
  resume had only a single global equality predicate.
- **Impact:** The old implementation either reused unsafe stale work or discarded
  unrelated compatible work; it could not prove acceptance criteria 2, 3, or 14.
- **Whether existing tests detected it:** No; the old test repeated the same
  global boolean implemented by production code.
- **Fix performed:** Stage cache records now have an exact four-field schema:
  artifact hash, compatibility fingerprint, replay-policy hash, and durable-stage
  number. Resume requires current per-stage fingerprints; missing or mismatched
  identity invalidates that stage deterministically, while a matching unaffected
  stage remains reusable.
- **Regression test added:**
  `test_resume_supports_precise_per_stage_cache_invalidation` and
  `test_missing_stage_identity_invalidates_cache_even_when_global_closure_matches`;
  the prior orchestrator fixture was upgraded to real digests and an explicit
  current stage identity.
- **Post-fix verification:** The two-stage mutation invalidates only `formal`,
  and missing current identity invalidates `scout` even under equal global
  closure.
- **Residual limitation:** This module compares fingerprints but does not attest
  that the upstream fingerprint was produced from an actual `StageIdentity` or
  execute the invalidated stage. Acceptance criterion 14's final-manifest
  independence property is outside this module and remains unproved here.
- **Confidence:** HIGH for deterministic comparison; MEDIUM for end-to-end cache
  provenance because the production loop does not call this API.

### CHK-004 — Malformed checkpoint and forged censoring metadata were accepted

- **Finding ID:** CHK-004
- **Severity:** MEDIUM
- **Affected F-REQ IDs:** F-REQ-049, F-REQ-117, F-REQ-118, F-REQ-182
- **Specification source:** §10.4 lines 1656-1679
- **Files and line ranges:** pre-fix `egmra/orchestrator/checkpoint.py:56-96`;
  post-fix `egmra/orchestrator/checkpoint.py:63-221,405-428,470-481`
- **Symbols:** validation helpers, `take_checkpoint`, `resume`
- **Expected behavior:** Unknown schemas, malformed digests, booleans masquerading
  as numbers, non-finite budgets, duplicate/blank calls, unknown cache fields,
  and invented interrupted-call IDs fail closed.
- **Observed behavior:** All shapes and values were accepted. Any caller-provided
  tuple became `censored_calls`, even if the call was never recorded in flight.
- **Reproduction command or test:** Initial adversarial run failed schema and
  interrupted-call tests. A second red cycle, `pytest ... -k unrecorded`, failed
  because a well-formed but unknown call ID was accepted (`1 failed`).
- **Root cause:** No input schema or checkpoint-bound in-flight call registry.
- **Impact:** Corrupt state could enter hashes and arbitrary work could be labeled
  operationally censored to avoid mathematical failure accounting.
- **Whether existing tests detected it:** No.
- **Fix performed:** Added strict schema/type/digest/numeric validation,
  duplicate rejection, immutable `in_flight_calls`, and a subset check requiring
  every censored ID to have been recorded in the authenticated checkpoint.
- **Regression test added:**
  `test_take_checkpoint_rejects_malformed_schema_and_digests`,
  `test_interrupted_calls_must_be_unique_nonempty_identifiers`, and
  `test_resume_cannot_mark_an_unrecorded_call_as_censored`.
- **Post-fix verification:** All malformed and forged cases reject; the related
  orchestrator test records `scout_call` before successfully censoring it.
- **Residual limitation:** There is no durable provider-call journal. Calls begun
  after the last checkpoint cannot be authenticated as interrupted from this
  checkpoint alone.
- **Confidence:** HIGH.

## Test-quality assessment

The original single test could still pass if checkpoint hashing ignored almost
all fields, nested state was mutable, sequence/Merkle were never checked, any
valid log was accepted, caller censoring was forged, and cache reuse depended
only on one global string. All of those defects existed simultaneously.

The new suite independently mutates every current semantic field, bypasses
`frozen=True` with `object.__setattr__`, recomputes a public content hash, signs a
deliberately inconsistent prefix to ensure the log proof is independent of the
signature, corrupts the event file, substitutes another valid log, appends a
valid tail, supplies malformed values, changes one of two stage identities, and
omits current identity entirely.

## Verification evidence

Environment: Python 3.14.4; Darwin 25.3.0 arm64.

Baseline weak-test command:

```text
/tmp/erdos-baseline.t2afE1/venv/bin/python -m pytest -q \
  egmra/tests/test_orchestrator.py -k checkpoint
exit 0: 1 passed, 5 deselected
```

Initial adversarial red run:

```text
/tmp/erdos-baseline.t2afE1/venv/bin/python -m pytest -q \
  egmra/tests/test_adversarial_checkpoint.py
exit 1: 8 failed, 1 passed
```

Additional TDD red runs:

```text
... pytest -q egmra/tests/test_adversarial_checkpoint.py -k unrecorded
exit 1: 1 failed, 11 deselected

... pytest -q egmra/tests/test_adversarial_checkpoint.py -k recomputing
exit 1: 1 failed, 12 deselected
```

Final compilation:

```text
/tmp/erdos-baseline.t2afE1/venv/bin/python -m compileall -q \
  egmra/orchestrator/checkpoint.py \
  egmra/tests/test_adversarial_checkpoint.py \
  egmra/tests/test_orchestrator.py egmra/tests/conftest.py
exit 0
```

Final focused and dependent verification:

```text
/tmp/erdos-baseline.t2afE1/venv/bin/python -m pytest -q \
  egmra/tests/test_adversarial_checkpoint.py \
  egmra/tests/test_orchestrator.py egmra/tests/test_acceptance.py
exit 0: 38 passed in 1.01s; 0 failed; 0 skipped; 0 deselected
```

## Residual specification gaps

These are material and must remain visible in the repository-wide verdict:

1. **No durable checkpoint artifact.** There is no canonical `to_dict`/strict
   `from_dict`, atomic file/database persistence, restart read path, corruption
   recovery, or checkpoint retention policy. The implementation is still an
   authenticated in-memory value.
2. **No production reachability.** At audit time, `take_checkpoint()` and
   `resume()` are imported by the package and exercised by tests, but the main
   `research()` loop does not invoke them. A process crash therefore cannot
   resume production work through this code.
3. **Incomplete checkpoint content.** The object still lacks explicit source
   hashes, program archive/AND-OR blueprint, full materialized graph snapshot,
   model/prompt/tool/environment/dependency/service version records, quota
   provenance, and full lease/heartbeat/fencing records. Opaque closure/cache
   fingerprints do not make those components independently auditable.
4. **No state reconstruction or transaction.** `resume()` does not rebuild the
   graph from events, compare rebuilt state to `graph_view_hash`, atomically
   snapshot event/controller/lease/provider state, or restore RNG/controller
   objects.
5. **No lease recovery.** Active leases are only IDs. The module does not recheck
   expiry, transfer ownership with the durable `LeaseManager`, or reject a stale
   worker as part of resume.
6. **No high-trust replay or continuation.** Formal/computation artifacts are not
   replayed after environment drift, no highest compatible durable stage is
   selected/launched, and no resumed worker effect is demonstrated.
7. **No end-to-end cache attestation.** Cache compatibility depends on supplied
   SHA-256 fingerprints. This module does not independently derive them from
   provider/model/runner/retrieval/validator objects or prove final manifest
   independence.
8. **No authenticated post-checkpoint call journal.** Censoring is exact for calls
   recorded at checkpoint time only. Work started later needs a durable call-start
   event before it can be classified after a crash.

Accordingly, these changes materially repair the local trust boundary but do not
make checkpoint/restart requirements VERIFIED or the complete implementation
production-ready.
