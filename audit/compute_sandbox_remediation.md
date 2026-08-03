# Compute/Sandbox Independent Audit and Remediation Evidence

Date: 2026-07-13  
Scope: `egmra/compute/*`, `egmra/tests/test_compute.py`, and the independent
`egmra/tests/test_adversarial_compute_security.py` suite.  This note is
subsystem evidence for the parent FABLE audit; it does not claim that the full
architecture is complete.

## Normative mapping

The principal requirements are F-REQ-010, F-REQ-160, F-REQ-168, F-REQ-184,
F-REQ-194, and F-REQ-203.  Their authoritative anchors include specification
§6.8 lines 733-765 (immutable compute jobs, replay, checked classification and
certificates), §13.3 line 2028 (M1 sandboxed exact Python), §13.4 line 2041
(containerized mathematical backends), §13.6 line 2070 (independent-container
replay), §14.1 line 2104 (isolated compute with network off), and §15 lines
2217-2238 (malicious code and irreproducible-compute threats).

## Initial red evidence

Direct production-path probes before remediation established that:

- a submitted program read `/etc/passwd`;
- `import _socket; _socket.socket()` succeeded;
- a caller could change only `environment_label` and obtain a different replay
  identity;
- `ContainerSandbox.run()` only raised `RuntimeError`;
- `{"result": false}` retained `exhaustive_finite_subcase`;
- a restarted `ComputeService` loaded zero jobs/artifacts;
- an arbitrary lambda passed to `verify_certificate` self-approved a forged
  certificate; and
- a passed certificate reverted to heuristic state after restart.

The first adversarial batch produced `27 failed, 1 passed`.  After the main
remediation, a separate verifier-bypass red run was:

```text
.venv/bin/python -m pytest -q egmra/tests/test_adversarial_compute_security.py \
  -k 'caller_supplied_certificate_checker or checked_certificate_state_survives_restart'
2 failed, 54 deselected
```

The failures showed `CertificateReport(... passed=True)` for the caller lambda
and `heuristic_numerical` after restart where `certificate_checked_lemma` was
required.

## Findings and fixes

### CS-001 — CRITICAL — Host capability access behind a false sandbox label

- **Affected requirements:** F-REQ-010, F-REQ-160, F-REQ-194, F-REQ-203.
- **Expected:** malicious M1 jobs cannot access host files, processes, network,
  credentials, or inherited environment; unsupported isolation fails closed.
- **Observed/root cause:** the old subprocess wrapper executed unrestricted
  Python on the host while describing itself as a sandbox.
- **Impact:** arbitrary code execution with repository-user authority and
  credential/file disclosure.
- **Existing tests:** did not exercise raw `_socket`, file reads, process spawn,
  environment access, or production-path policy bypass.
- **Fix:** `RestrictedPythonExecutor` now accepts a small AST-validated,
  capability-free Python subset; exposes only an allowlisted builtin set; uses
  an isolated child, scrubbed environment, closed descriptors, separate
  globals, and no imports/attributes/private runtime names.  It is honestly
  labeled `language-restriction`, not an OS sandbox.  Container policy never
  falls back to it.
- **Regression:** parametrized host-file, `os`, `_socket`, `subprocess`, and
  environment attacks in `test_restricted_executor_rejects_host_capability_access`.
- **Post-fix:** all attacks fail with `policy_violation`; supported finite exact
  programs still run.
- **Residual:** this local executor is defense in depth, not a kernel boundary;
  hostile arbitrary Python requires the OCI backend.
- **Confidence:** high.

### CS-002 — HIGH — No working OCI execution boundary

- **Affected requirements:** F-REQ-160, F-REQ-168, F-REQ-184, F-REQ-194.
- **Observed/root cause:** `ContainerSandbox` was a raising placeholder.
- **Fix:** implemented a real Docker/Podman path with local-image-only lookup,
  immutable image-ID execution, no network, read-only root, all capabilities
  dropped, `no-new-privileges`, non-root UID/GID, bounded CPU/memory/PIDs/files,
  `noexec,nosuid,nodev` tmpfs, read-only job mount, bounded output mount,
  scrubbed environment, process/container cleanup, and explicit entrypoint
  override.  Runtime/image absence returns typed `sandbox_unavailable`; there is
  no unsandboxed fallback.
- **Regression:** unavailable-runtime and live locally-present-image negative
  path tests, including a base-image ENTRYPOINT interception check.
- **Post-fix:** Docker server 29.5.3 and local image
  `postgres:17-alpine@sha256:dc17045ccfd343b49600570ea734b9c4991cf1c3f3302e67df51e3b402dd55c4`
  exercised the real OCI/runc path.  The test confirms its entrypoint cannot
  reinterpret the job command.
- **Residual:** no compatible pinned Python/Sage image was locally available;
  pulling `python:3.12-alpine` blocked in the Docker credential helper and was
  interrupted.  Successful independent-container replay is therefore
  **BLOCKED-EXTERNAL**, not verified.  General Sage/CAS/SAT/SMT/ILP containers
  remain outside this implementation.
- **Confidence:** high for fail-closed local behavior; low for an unexercised
  successful compatible-image run.

### CS-003 — HIGH — Forged replay independence and mutable executor identity

- **Affected requirements:** F-REQ-010, F-REQ-160, F-REQ-184.
- **Observed/root cause:** caller text supplied the environment identity;
  arbitrary executor objects could self-attest.
- **Fix:** environment hashes are derived from the resolved executable,
  implementation/version/platform/resource probe, executable SHA-256, runner
  version, isolation kind, and (for OCI) inspected immutable image ID.  Caller
  labels are ignored.  Only the two audited concrete executor types are
  admitted, their configuration is immutable, and service executor
  configuration cannot be swapped after initialization.
- **Regression:** caller-label forgery, fake executor, relative/non-Python
  executable, mutable executor, and mutable service-configuration tests.
- **Post-fix:** same-environment replay is explicitly non-independent; replay
  through `/usr/bin/python3` reproduced the output with a distinct measured
  environment and `independent_environment=True`.
- **Residual:** a distinct Python toolchain is not the independent container
  required by F-REQ-184.
- **Confidence:** high.

### CS-004 — HIGH — Jobs/artifacts were not durable or integrity checked

- **Affected requirements:** F-REQ-010, F-REQ-160, F-REQ-203.
- **Observed/root cause:** process-local dictionaries were presented as a
  replayable artifact service; restart lost code, spec, output, and job state.
- **Fix:** successful jobs are atomically persisted as content-addressed bundles
  with exact spec/code/output/metadata/stdout, per-file hashes, strict JSON,
  bounded regular-file reads, staging/fsync/rename publication, startup replay,
  and identity revalidation.  Artifact identity binds spec, code, output, and
  measured environment.  Storage publication occurs before an in-memory job is
  marked done.
- **Regression:** restart replay, output corruption, rehashed environment
  forgery, symlinked bundle file, unsafe staging symlink, root replacement, and
  persistence-failure publication tests.
- **Post-fix:** jobs and output hashes survive a fresh service instance;
  corruption/root substitution fails closed.
- **Residual:** local-admin deletion causes loss/downgrade, not forged success;
  this M1 filesystem store is not the M2 object store.
- **Confidence:** high for tested single-host behavior.

### CS-005 — HIGH — Exact/evidence classification trusted untrusted output

- **Affected requirements:** F-REQ-010, F-REQ-160, F-REQ-203.
- **Observed/root cause:** false output could retain exhaustive status and output
  could self-declare its own coverage.
- **Fix:** coverage comes only from immutable `ExperimentSpec`; exhaustive and
  finite-reduction classifications require non-empty submitted coverage and
  literal `result is True`; otherwise the artifact downgrades to heuristic.
  Nested spec and artifact data are immutable snapshots.
- **Regression:** false-result, self-reported coverage, and post-hash mutation
  tests, plus the dependent truth-plane false-computation test.
- **Post-fix:** false output cannot retain exact exhaustive evidence or promote a
  claim.
- **Residual:** a scope/claim-specific verifier must still establish that the
  submitted program and coverage statement mean what they claim; orchestration
  and truth-plane admission remain separate trust boundaries.
- **Confidence:** high.

### CS-006 — HIGH — Resource, serialization, and schema controls failed open

- **Affected requirements:** F-REQ-010, F-REQ-160, F-REQ-194, F-REQ-203.
- **Observed/root cause:** weak/unvalidated limits, permissive serialization,
  and no semantic output-schema enforcement allowed resource abuse and fake
  shaped evidence.
- **Fix:** construction-time bounds for CPU, memory, wall time, processes,
  output/log sizes, seed, entrypoint, arithmetic, network, and sandbox policy;
  strict JSON with non-finite/unsupported values rejected; bounded stdout,
  stderr, and output; deterministic timeout/process-group cleanup; schema-subset
  definition and runtime semantic validation.  Exact mode rejects float
  literals, `/`, unchecked `**`, and negative/non-integer `pow` exponents.
- **Regression:** CPU, memory, wall-time, output/log, malformed schema, schema
  mismatch, non-JSON, negative exponent, invalid policy/resource, and cleanup
  tests.
- **Post-fix:** violations are typed failed results and never create artifacts.
- **Residual:** macOS memory enforcement uses parent RSS monitoring because the
  audited Python rejects `RLIMIT_AS`; it is not as strong as an OCI/kernel
  memory cgroup.  Network allowlists are unsupported and fail closed.
- **Confidence:** high for tested bounds, medium for polling granularity.

### CS-007 — HIGH — Caller-controlled certificate verifier and restart loss

- **Affected requirements:** F-REQ-010, F-REQ-160, F-REQ-168, F-REQ-203.
- **Observed/root cause:** `verify_certificate` accepted an arbitrary callable,
  allowing generator self-approval, and only mutated an in-memory artifact.
- **Fix:** the method now accepts only `checker_id` and a JSON certificate.
  Checkers enter through an immutable `TrustedCertificateChecker` deployment
  registry containing stable ID, version, and implementation SHA-256.  Registry
  keys and immutable spec checker/kind must agree.  A content-addressed
  certificate record persists the certificate hash, result, kind, and checker
  attestation.  Startup requires the attested checker, reruns it against the raw
  artifact, rejects result/identity drift, and only then restores checked state.
  Raw artifact bundles are forbidden from containing pre-forged checked state.
- **Regression:** caller-lambda self-approval, restart restoration, attestation
  drift, and registry/identity mutation tests.
- **Post-fix:** the two-test red reproduction is now green; direct checker
  injection raises `TypeError`, missing registry returns a failed report, and a
  valid configured certificate remains checked after restart.
- **Residual:** the explicit implementation hash is a deployment attestation;
  signing/governance of that deployment registry belongs to the global policy
  plane.  Checker implementations must be deterministic and treat certificate
  payloads as non-secret persisted evidence.
- **Confidence:** high.

### CS-008 — MEDIUM — Persistence publication and metadata identity races

- **Affected requirements:** F-REQ-010, F-REQ-160, F-REQ-203.
- **Observed/root cause:** an artifact could be published in memory before a
  failed durable write, and the measured environment was initially outside the
  artifact ID.
- **Fix:** persist-before-publish ordering, failed job disposition on storage
  errors, measured-environment binding in the content identity, immutable store
  root identity, and staging/symlink rejection.
- **Regression:** rehashed environment forgery and post-start root-swap tests.
- **Post-fix:** neither reproduction can leave a successful artifact.
- **Residual:** the path implementation is hardened against tested substitutions
  but does not use a complete `openat(2)`/directory-FD transaction for every
  operation; a hostile local process with concurrent filesystem-write authority
  remains outside the M1 threat boundary.
- **Confidence:** high for reproductions, medium for untested nanosecond TOCTOU.

## Final verification evidence

```text
.venv/bin/python -m py_compile \
  egmra/compute/__init__.py egmra/compute/artifact.py \
  egmra/compute/sandbox.py egmra/compute/service.py egmra/compute/spec.py \
  egmra/tests/test_adversarial_compute_security.py egmra/tests/test_compute.py
exit 0

.venv/bin/python -m pytest -q \
  egmra/tests/test_adversarial_compute_security.py egmra/tests/test_compute.py
67 passed in 3.97s

.venv/bin/python -m pytest -q \
  egmra/tests/test_acceptance.py::test_acc11_exact_computation_replays \
  egmra/tests/test_adversarial_truth_security.py::test_unsigned_self_reported_computation_cannot_promote_claim \
  egmra/tests/test_adversarial_truth_security.py::test_false_computation_output_cannot_claim_exhaustive_success \
  egmra/tests/test_orchestrator.py::test_end_to_end_finite_claim_reaches_verified_result
4 passed in 0.47s

docker info --format '{{.ServerVersion}}'
29.5.3

docker image inspect --format '{{.Id}}' postgres:17-alpine
sha256:dc17045ccfd343b49600570ea734b9c4991cf1c3f3302e67df51e3b402dd55c4
```

The focused collection contains 58 adversarial compute/security cases and nine
legacy compute tests (67 total).  Search for TODO/FIXME/XXX/NotImplementedError
in the changed compute scope found no implementation placeholder; matches were
ordinary boolean returns and narrow exception handlers.

## Honest subsystem verdict

The M1 restricted exact-computation path is substantially repaired, reachable,
durable, fail-closed, and integrated with the tested truth/orchestrator path.
It must not be described as a complete full-scale compute lab.  F-REQ-184
remains **BLOCKED-EXTERNAL** because successful replay in a compatible
independent container was not exercised, and F-REQ-168 remains **PARTIAL**
because containerized Sage/CAS/SAT/SMT/ILP/graph backends were not implemented
or live-tested.  The local restricted executor is deliberately and accurately
not represented as an OS security sandbox.
