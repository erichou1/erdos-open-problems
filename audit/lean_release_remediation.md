# Lean, truth-admission, and release-boundary remediation

Date: 2026-07-13  
Scope: `egmra/lean/*`, `egmra/release/*`, `egmra/comms/*`, the formal-evidence boundary in `egmra/truth/router.py` and `egmra/truth/validators.py`, and their tests.

## Verdict for this scope

The pre-remediation Lean and release claims were materially overstated. Caller-owned booleans, callback return strings, unsigned reviewer records, raw `EvidenceProfile` values, and mutable release metadata could cross boundaries that were described as kernel, truth, or release authority. Those local bypasses are now fail-closed and covered by adversarial tests.

No real Lean build was exercised. Both `lean` and `lake` are installed only as Elan shims; `lean --version` and `lake --version` exit 1 with `no default toolchain configured`. Accordingly, live Lean/Lake/Mathlib behavior remains `BLOCKED-EXTERNAL`, and all subprocess checker positives in tests are structured protocol simulations rather than real kernel executions.

## Findings and remediation

### LR-001 — CRITICAL — caller status counted as kernel verification

- Requirements: F-REQ-090 through F-REQ-101; specification lines 1236-1247, 1304-1311, 1336-1344, 1737-1757.
- Pre-fix behavior: `kernel_result=True`, a lambda returning `True`, or a lambda returning `"kernel_verified"` could be treated as formal success; arbitrary `verification_method` values were not an effective trust boundary.
- Red reproduction: `.venv/bin/python -m pytest -q egmra/tests/test_adversarial_lean_release.py` initially produced failures for caller booleans, callbacks, vendor methods, and incomplete checker output.
- Root cause: an injectable callback result was used as epistemic authority without a pinned executable, structured response, exact source/environment/type binding, or authenticated attestation.
- Fix: `AttestedKernelRunner` pins the executable hash and checker identity, uses a closed JSON protocol, scrubs secrets from the subprocess environment, enforces timeout/error handling, and signs exact request/output bindings. `LeanService` ignores `kernel_result` and non-`AttestedKernelRunner` callbacks. A qualifying certificate requires clean offline replay, network disabled, full import/axiom/immutable-target audits, exact type match, no placeholders/unsafe findings, and the local-kernel method.
- Regression tests: caller boolean, lambda/status, arbitrary method, caller-constructed checker attestation, missing checker response fields, and subprocess secret exposure tests in `test_adversarial_lean_release.py`.
- Residual: the repository has no configured real Lean toolchain or production checker executable.

### LR-002 — HIGH — forgeable `FormalCertificate` and unrelated equivalence proof

- Requirements: F-REQ-090 through F-REQ-101; specification lines 1313-1344.
- Pre-fix behavior: a caller could instantiate `FormalCertificate` with all booleans true and obtain `passed=True`; any such or unrelated certificate plus an arbitrary SHA string could make `compare_statements` return `equivalent`.
- Red reproduction: `pytest ... -k 'caller_constructed_formal or unrelated_certificate'` produced 2 failures before remediation.
- Root cause: structural fields were confused with authenticated proof evidence, and the equivalence certificate was not bound to the exact `A ↔ B` target or proof-term hash.
- Fix: the service signs every trust-relevant formal-certificate field. `FormalCertificate.verify()` authenticates the envelope; `certificate_digest` is stable and tamper-evident. `verify_formal_certificate()` verifies serialized envelopes against independently supplied source, environment, expected type, claim, artifact, and declaration bindings. Equivalence additionally requires the exact relation target hash and the checker-authenticated proof-term hash.
- Regression tests: forged certificate/hardening rejection, unrelated-certificate substitution, positive structured checker certificate, field mutation, exact equivalence relation, and proof-artifact substitution.

### LR-003 — CRITICAL — signed Lean booleans could manufacture T4/T5

- Requirements: F-REQ-003, F-REQ-013, F-REQ-014, F-REQ-048, F-REQ-090 through F-REQ-101; specification lines 1236-1245 and 1737-1757.
- Pre-fix behavior: an evidence HMAC over `generator_identity.findings.kernel_verified=true` authenticated the assertion but did not verify Lean semantics; with a correspondence ID, those booleans could promote a claim.
- Red reproduction: `test_signed_lean_booleans_with_real_correspondence_but_no_envelope_cannot_promote` initially changed the claim to `SUPPORTED`.
- Root cause: `validate_lean_proof` validated self-reported fields instead of consuming formal verifier authority.
- Fix: the router derives claim hash from the live graph, expected type/declaration from the authenticated correspondence certificate, and source/environment/artifacts from the immutable Evidence record, then calls `verify_formal_certificate`. The certificate digest must itself be a content-addressed Evidence artifact. `validate_lean_proof` ignores status booleans; T5 derives only from the signed independent-checker identity.
- Regression tests: absent-envelope rejection, signed-booleans rejection, forged correspondence rejection, and positive authenticated envelope admission.

### LR-004 — CRITICAL — raw profile and stale truth state could authorize release

- Requirements: F-REQ-003, F-REQ-013, F-REQ-014, F-REQ-105, F-REQ-110, F-REQ-129 through F-REQ-134; specification lines 1737-1815.
- Pre-fix behavior: `run_five_gates(profile=...)` accepted a caller-owned profile; gates were not bound to the authoritative event-log head; cached approvals could survive later truth changes.
- Red reproduction: raw-profile and post-approval event tests failed before the snapshot integration.
- Root cause: release consumed a mutable materialized object rather than a replay-derived truth-plane attestation.
- Fix: gates require a signed `TruthSnapshot` plus the current `EventLog`, bind the claim, canonical hash, run ID, event count, head event, and Merkle root, and attest those fields. Any appended, removed, reordered, or corrupted event invalidates gate verification, promotion authorization, certificate verification, and rendering immediately.
- Regression tests: raw profile rejection and `test_new_truth_event_immediately_invalidates_gate_authorization_and_release`.

### LR-005 — HIGH — release signing/render bypasses and weak key fallback

- Requirements: F-REQ-013, F-REQ-014, F-REQ-105, F-REQ-110, F-REQ-129 through F-REQ-134; specification lines 1746-1815.
- Pre-fix behavior: release signing had a fallback key, could occur before promotion, accepted stale state, and direct/human render paths did not uniformly prove the same gate/promotion/signature chain.
- Root cause: release objects were descriptive records rather than a mandatory authorization chain.
- Fix: gate, promotion, and release keys must each be at least 32 bytes and mutually distinct. Promotion decisions are signed, policy-bound, subject-bound, short-lived authorizations. Certificate signing requires a fresh gate and authorization. Verification and every render entry point revalidate the current event log, authorization, certificate HMAC, freshness, and mandatory schema.
- Regression tests: missing/weak keys, sign-before-promotion, unsigned/forged direct render, stale timestamp, gate mutation, auth reuse, certificate mutation, stale render, and placeholder mandatory fields.

### LR-006 — HIGH — claim, interpretation, I2, and F2 substitution

- Requirements: F-REQ-022, F-REQ-051, F-REQ-064, F-REQ-105, F-REQ-110; specification lines 1240-1241, 1750-1757, 1773-1794.
- Pre-fix behavior: a valid gate for one claim could authorize another result claim; a signed subject could name an unrelated active interpretation; raw reviewer strings were sufficient for I2/F2.
- Root cause: gate attestations omitted semantic bindings and intent/correspondence records lacked independent authentication.
- Fix: gates bind truth claim ID/hash and accepted source, interpretation, informal claim, intent certificate, correspondence certificate, and elaborated type. Release signing requires exact equality. I2 requires a separately signed intent review; F2 requires a separately signed formal-correspondence review under `EGMRA_FORMAL_CORRESPONDENCE_KEY`. Raw labels yield at most I1/F1.
- Regression tests: claim substitution, active-interpretation substitution, stale parent intent, reused intent binding, raw formal reviewer labels, and signature mutation.

### LR-007 — HIGH — unresolved axes rendered as verified result

- Requirements: F-REQ-105, F-REQ-110, F-REQ-129 through F-REQ-134; specification lines 1737-1757.
- Pre-fix behavior: a T4 result with I0/N0/S0/R0 could receive verified-sounding output.
- Fix: positive vocabulary is unavailable until intent, current status, significance, and replay obligations are discharged; otherwise the only label is `honest_no_result`. Formal resolution needs T5+I2+F2; scoped and informal releases have explicit lower-tier policies.
- Regression test: `test_unresolved_axes_never_render_verified_sounding_result`.

### LR-008 — MEDIUM — L0 target package weakened 2–3 to 1–3 and froze before probes

- Requirements: F-REQ-090 family; specification lines 1251-1259.
- Red reproduction: a one-candidate package was accepted and an unreviewed target froze.
- Fix: exactly 2–3 unique candidates are required. Freeze requires an approved interpretation, nonempty backtranslations, recorded example/anti-example tests, and passing paraphrase/mutation probes.
- Regression test: `test_l0_rejects_one_candidate_and_requires_semantic_probe_results_before_freeze`.

### LR-009 — MEDIUM — L2 decomposition bypassed direct attempt

- Requirements: specification lines 1273-1277.
- Red reproduction: callers added holes without attempting the target.
- Fix: `add_hole` enforces direct-first and rejects duplicate/self-dependent holes in addition to target restatements.
- Regression test: `test_l2_holes_cannot_bypass_direct_target_attempt`.

### LR-010 — MEDIUM — frozen RFC weights were mutable

- Requirements: specification risk-weighted formal coverage policy and frozen-blueprint invariant.
- Red reproduction: changing all weights after freeze with the same claim IDs was accepted.
- Fix: scoring recomputes and compares the frozen weight hash; duplicate claim IDs are rejected.
- Regression test: `test_frozen_rfc_rejects_post_freeze_weight_manipulation`.

### LR-011 — MEDIUM — ambiguous L4 grounding accepted

- Requirements: specification lines 1294-1302.
- Red reproduction: one load-bearing sentence could simultaneously claim a Lean declaration and audited-source grounding.
- Fix: a `SyncLink` must have exactly one grounding, not merely at least one.
- Regression test: `test_sync_link_rejects_ambiguous_multiple_groundings`.

## Verification evidence

- Initial adversarial Lean/release run: 9 failed, 2 passed (before the first trust-boundary fixes).
- Forged formal certificate/equivalence red run: 2 failed, 25 deselected.
- Claim substitution red run: 1 failed, 29 deselected.
- Active interpretation substitution red run: 1 failed, 30 deselected.
- L0/L2/RFC/L4 red run: 4 failed, 32 deselected.
- Signed Lean booleans red run: 1 failed, 21 deselected.
- Focused post-fix run: 132 passed across acceptance, Lean, release, communication, truth, and adversarial suites.
- Full EGMRA run after all dependent fixtures were corrected: `.venv/bin/python -m pytest -q egmra/tests` exited 0 with **510 passed in 9.16s**, no failures and no skips reported.
- Compilation: `.venv/bin/python -m compileall -q egmra/lean egmra/release egmra/comms egmra/truth egmra/intake` exited 0.
- External Lean check: `lean --version` and `lake --version` both exited 1 because Elan has no configured default toolchain.

## Residual limitations

- Real Lean, Lake, Mathlib, clean-checkout replay, and independent checker binaries were not exercised. Formal positive tests use a pinned local executable with a monkeypatched structured response and prove protocol/binding behavior only.
- `elaborate` is deliberately labeled `static_source_scan` with `trusted_elaboration=False`; it is not a Lean elaborator.
- The specified live `searchPremises` and `tryActions` Lean backends are not implemented or exercised against LeanDojo/Pantograph/other services. The portfolio constants and routing helpers are not equivalent to those integrations.
- Aristotle routing remains a policy/request description; no live Aristotle service or returned-Lean quarantine build was exercised in this audit.
- HMAC keys model separate service authorities, but the repository test/runtime process can hold several keys in one environment. Real separation of duties requires deployment-level key isolation.
- L5 archive validation now binds source-tree and theorem hashes, but the required human-readable graph-linked proof artifact is not represented, and no production archive/rebuild pipeline was exercised with real artifacts.

These limitations prohibit a `VERIFIED COMPLETE` verdict for the complete Lean subsystem. The locally testable trust and release paths are substantially stronger and fail closed, but external formal verification remains unverified.
