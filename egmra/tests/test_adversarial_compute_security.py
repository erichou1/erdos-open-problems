"""Independent adversarial tests for the compute execution boundary.

These tests intentionally exercise production ``ComputeService`` paths.  They do
not replace the executor, mock ``subprocess``, or derive expected security
decisions from implementation helpers.
"""

from __future__ import annotations

import math
import time
import hashlib
import json
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from egmra.compute import (
    ComputeService,
    ContainerSandbox,
    ExperimentSpec,
    SandboxResult,
    SubprocessSandbox,
    TrustedCertificateChecker,
)


SAFE_EXPERIMENT = """
def experiment(inputs):
    n = inputs["n"]
    return {
        "result": all(k * k >= 0 for k in range(n + 1)),
        "coverage": "all integers in 0..n",
        "checked": n + 1,
    }
"""


def _trusted_finite_checker(artifact, certificate) -> bool:
    return certificate == {"output_hash": artifact.output_hash}


def _trusted_checker(*, version: str = "1") -> TrustedCertificateChecker:
    implementation = hashlib.sha256(
        f"egmra-test-finite-checker-{version}".encode("ascii")
    ).hexdigest()
    return TrustedCertificateChecker(
        checker_id="trusted-finite-checker",
        version=version,
        implementation_hash=implementation,
        check=_trusted_finite_checker,
    )


@pytest.mark.parametrize(
    "code",
    [
        "def experiment(inputs):\n    return {'data': open('/etc/passwd').read()}\n",
        "def experiment(inputs):\n    import os\n    return {'data': os.listdir('/')}\n",
        "def experiment(inputs):\n    import _socket\n    return {'socket': bool(_socket.socket())}\n",
        "def experiment(inputs):\n    import subprocess\n    return {'rc': subprocess.run(['/bin/true']).returncode}\n",
        "def experiment(inputs):\n    return {'env': __import__('os').environ.copy()}\n",
    ],
)
def test_restricted_executor_rejects_host_capability_access(code: str) -> None:
    service = ComputeService()
    job_id = service.submit_experiment(ExperimentSpec(purpose="host escape"), code)

    assert service.poll(job_id) == "failed"
    assert "policy" in service.jobs[job_id].error.lower()


def test_default_executor_is_labeled_as_language_restricted_not_a_security_sandbox() -> None:
    service = ComputeService()

    assert service.sandbox.policy == "restricted-python-subprocess"
    assert service.sandbox.security_boundary == "language-restriction"


def test_restricted_executor_still_runs_supported_exact_programs() -> None:
    service = ComputeService()
    spec = ExperimentSpec(
        purpose="finite exact check",
        inputs={"n": 50},
        arithmetic_mode="exact",
        coverage="all integers in 0..n",
    )
    job_id = service.submit_experiment(
        spec, SAFE_EXPERIMENT, claimed_classification="exhaustive_finite_subcase"
    )

    assert service.poll(job_id) == "done"
    assert service.artifact(job_id).output == {
        "checked": 51,
        "coverage": "all integers in 0..n",
        "result": True,
    }


def test_exact_mode_rejects_floating_point_operations() -> None:
    code = "def experiment(inputs):\n    return {'result': 1 / 2 == 0.5, 'coverage': 'one case'}\n"
    service = ComputeService()
    job_id = service.submit_experiment(
        ExperimentSpec(purpose="not exact", arithmetic_mode="exact", coverage="one case"),
        code,
        claimed_classification="exhaustive_finite_subcase",
    )

    assert service.poll(job_id) == "failed"
    assert "exact arithmetic" in service.jobs[job_id].error.lower()


@pytest.mark.parametrize(
    "expression",
    ["2 ** -1", "pow(2, -1)"],
)
def test_exact_mode_rejects_negative_exponents_that_produce_float(expression: str) -> None:
    service = ComputeService()
    code = (
        "def experiment(inputs):\n"
        f"    return {{'result': bool({expression}), 'coverage': 'one case'}}\n"
    )
    job_id = service.submit_experiment(
        ExperimentSpec(purpose="negative exponent", arithmetic_mode="exact", coverage="one case"),
        code,
        claimed_classification="exhaustive_finite_subcase",
    )

    assert service.poll(job_id) == "failed"
    assert "exact arithmetic" in service.jobs[job_id].error.lower()


def test_false_output_cannot_retain_exhaustive_classification() -> None:
    service = ComputeService()
    spec = ExperimentSpec(
        purpose="false exhaustive result", arithmetic_mode="exact", coverage="all cases"
    )
    job_id = service.submit_experiment(
        spec,
        "def experiment(inputs):\n    return {'result': False, 'coverage': 'all cases'}\n",
        claimed_classification="exhaustive_finite_subcase",
    )

    artifact = service.artifact(job_id)
    assert artifact.output["result"] is False
    assert artifact.effective_classification() == "heuristic_numerical"


def test_untrusted_output_cannot_supply_its_own_exhaustive_coverage() -> None:
    service = ComputeService()
    job_id = service.submit_experiment(
        ExperimentSpec(purpose="self-reported coverage", arithmetic_mode="exact"),
        "def experiment(inputs):\n    return {'result': True, 'coverage': 'trust me: all cases'}\n",
        claimed_classification="exhaustive_finite_subcase",
    )

    artifact = service.artifact(job_id)
    assert artifact.output["coverage"] == "trust me: all cases"
    assert artifact.coverage == ""
    assert artifact.effective_classification() == "heuristic_numerical"


def test_non_json_output_is_rejected_instead_of_stringified() -> None:
    service = ComputeService()
    job_id = service.submit_experiment(
        ExperimentSpec(purpose="unsafe serialization"),
        "def experiment(inputs):\n    return {'values': {1, 2, 3}}\n",
    )

    assert service.poll(job_id) == "failed"
    assert "json" in service.jobs[job_id].error.lower()


def test_output_schema_is_enforced_before_artifact_creation() -> None:
    service = ComputeService()
    spec = ExperimentSpec(
        purpose="schema mismatch",
        output_schema={
            "type": "object",
            "required": ["result"],
            "properties": {"result": {"type": "boolean"}},
            "additionalProperties": False,
        },
    )
    job_id = service.submit_experiment(
        spec, "def experiment(inputs):\n    return {'result': 'yes', 'extra': 1}\n"
    )

    assert service.poll(job_id) == "failed"
    assert "schema" in service.jobs[job_id].error.lower()


@pytest.mark.parametrize(
    "schema",
    [
        {"unknownKeyword": True},
        {"type": "capability"},
        {"type": "object", "required": "result"},
        {"type": "array", "minItems": -1},
        {"type": "string", "maxLength": "unbounded"},
        {"enum": "not-an-array"},
    ],
)
def test_malformed_output_schema_is_rejected_at_submission_boundary(schema: dict) -> None:
    with pytest.raises(ValueError, match="output_schema"):
        ExperimentSpec(purpose="bad schema", output_schema=schema)


def test_default_output_limit_fails_closed() -> None:
    service = ComputeService()
    job_id = service.submit_experiment(
        ExperimentSpec(purpose="oversized output"),
        "def experiment(inputs):\n    return {'blob': 'x' * 1100000}\n",
    )

    assert service.poll(job_id) == "failed"
    assert "output limit" in service.jobs[job_id].error.lower()


def test_default_stdout_limit_fails_closed_without_buffering_unbounded_data() -> None:
    service = ComputeService()
    job_id = service.submit_experiment(
        ExperimentSpec(purpose="oversized stdout"),
        "def experiment(inputs):\n    print('x' * 1100000)\n    return {'result': True}\n",
    )

    assert service.poll(job_id) == "failed"
    assert "output limit" in service.jobs[job_id].error.lower()


def test_cpu_limit_is_enforced_and_classified() -> None:
    code = "def experiment(inputs):\n    n = 0\n    while True:\n        n += 1\n"
    result = SubprocessSandbox().run(
        ExperimentSpec(purpose="cpu bound", cpu_seconds=1, wall_seconds=5), code
    )

    assert not result.ok
    assert result.failure_kind == "cpu_limit"
    assert "cpu limit" in result.stderr.lower()


def test_wall_clock_timeout_terminates_execution() -> None:
    code = "def experiment(inputs):\n    n = 0\n    while True:\n        n += 1\n"
    started = time.monotonic()
    result = SubprocessSandbox().run(
        ExperimentSpec(purpose="wall bound", cpu_seconds=10, wall_seconds=0.05), code
    )

    assert not result.ok and result.timed_out
    assert result.failure_kind == "timeout"
    assert time.monotonic() - started < 2


def test_memory_limit_terminates_allocation() -> None:
    result = SubprocessSandbox().run(
        ExperimentSpec(purpose="memory bound", memory_bytes=8 * 1024 * 1024, wall_seconds=5),
        "def experiment(inputs):\n    return {'blob': 'x' * 100000000}\n",
    )

    assert not result.ok
    assert result.failure_kind == "memory_limit"
    assert "memory limit" in result.stderr.lower()


@pytest.mark.parametrize(
    "overrides",
    [
        {"cpu_seconds": 0},
        {"memory_bytes": -1},
        {"wall_seconds": 0},
        {"wall_seconds": math.inf},
        {"max_processes": 0},
        {"seed": -1},
        {"seed": 2**32},
        {"seed": "0"},
        {"entry_point": "../../escape"},
        {"sandbox_policy": "unknown"},
    ],
)
def test_invalid_resource_and_execution_policy_is_rejected(overrides: dict) -> None:
    with pytest.raises(ValueError):
        ExperimentSpec(purpose="invalid policy", **overrides)


@pytest.mark.parametrize(
    "overrides",
    [
        {"network": "allowlist"},
        {"sandbox_policy": "container"},
        {"max_processes": 2},
    ],
)
def test_restricted_executor_rejects_policies_it_cannot_enforce(overrides: dict) -> None:
    spec = ExperimentSpec(purpose="unsupported restricted policy", **overrides)
    result = SubprocessSandbox().run(spec, "def experiment(inputs):\n    return {'result': True}\n")

    assert not result.ok
    assert "policy" in result.stderr.lower()


def test_caller_environment_label_cannot_forge_independent_replay() -> None:
    service = ComputeService()
    job_id = service.submit_experiment(
        ExperimentSpec(purpose="replay identity", inputs={"n": 2}), SAFE_EXPERIMENT
    )
    artifact = service.artifact(job_id)

    first = service.replay(artifact.artifact_id, environment_label="claimed-independent-A")
    second = service.replay(artifact.artifact_id, environment_label="claimed-independent-B")

    assert first.replayed and first.output_hash_matches
    assert first.environment_hash == second.environment_hash
    assert first.environment_hash == artifact.environment_hash
    assert first.original_environment_hash == artifact.environment_hash
    assert not first.independent_environment


def test_replay_can_use_a_distinct_validated_python_toolchain() -> None:
    alternate_python = Path("/usr/bin/python3")
    assert alternate_python.is_file(), "audited macOS environment lacks its system Python"
    service = ComputeService()
    job_id = service.submit_experiment(
        ExperimentSpec(purpose="toolchain-diverse replay", inputs={"n": 2}), SAFE_EXPERIMENT
    )
    artifact = service.artifact(job_id)

    report = service.replay(
        artifact.artifact_id,
        sandbox=SubprocessSandbox(python_executable=alternate_python),
    )

    assert report.replayed and report.output_hash_matches
    assert report.environment_hash != artifact.environment_hash
    assert report.original_environment_hash == artifact.environment_hash
    assert report.independent_environment


@pytest.mark.parametrize("executable", ["python3", "/bin/sh"])
def test_replay_executor_rejects_unverified_or_relative_interpreters(executable: str) -> None:
    with pytest.raises(ValueError, match="Python executable"):
        SubprocessSandbox(python_executable=executable)


def test_replay_rejects_caller_supplied_forged_executor_attestation() -> None:
    service = ComputeService()
    job_id = service.submit_experiment(
        ExperimentSpec(purpose="forged executor", inputs={"n": 2}), SAFE_EXPERIMENT
    )
    artifact = service.artifact(job_id)

    class ForgedExecutor:
        def run(self, spec, code):
            return SandboxResult(
                True,
                artifact.output,
                0,
                "",
                "",
                environment_hash="forged-different-environment",
            )

    with pytest.raises(ValueError, match="trusted executor"):
        service.replay(artifact.artifact_id, sandbox=ForgedExecutor())


def test_validated_executor_configuration_cannot_be_mutated_after_attestation() -> None:
    restricted = SubprocessSandbox()
    container = ContainerSandbox("postgres:17-alpine")

    with pytest.raises(AttributeError):
        restricted.python_executable = "/bin/sh"
    with pytest.raises(TypeError):
        restricted.python_identity["version"] = [0, 0, 0]
    with pytest.raises(AttributeError):
        container.runtime = "/tmp/forged-runtime"
    with pytest.raises(AttributeError):
        container.image = "attacker/image:latest"


def test_persisted_job_can_be_loaded_and_replayed_after_restart(tmp_path: Path) -> None:
    service = ComputeService(store_dir=tmp_path)
    job_id = service.submit_experiment(
        ExperimentSpec(purpose="durable replay", inputs={"n": 3}), SAFE_EXPERIMENT
    )
    artifact_id = service.artifact(job_id).artifact_id

    restarted = ComputeService(store_dir=tmp_path)
    report = restarted.replay(artifact_id)

    assert restarted.poll(job_id) == "done"
    assert report.replayed and report.output_hash_matches


def test_persistence_detects_output_corruption_instead_of_silently_ignoring_it(
    tmp_path: Path,
) -> None:
    service = ComputeService(store_dir=tmp_path)
    job_id = service.submit_experiment(
        ExperimentSpec(purpose="corruption check", inputs={"n": 3}), SAFE_EXPERIMENT
    )
    artifact = service.artifact(job_id)
    (tmp_path / artifact.artifact_id / "output.json").write_text(
        '{"result":false}', encoding="utf-8"
    )

    with pytest.raises(ValueError, match="integrity"):
        ComputeService(store_dir=tmp_path)


def test_content_identity_binds_measured_environment_even_if_manifest_is_rehashed(
    tmp_path: Path,
) -> None:
    service = ComputeService(store_dir=tmp_path)
    job_id = service.submit_experiment(
        ExperimentSpec(purpose="environment binding", inputs={"n": 3}), SAFE_EXPERIMENT
    )
    artifact = service.artifact(job_id)
    directory = tmp_path / artifact.artifact_id
    artifact_path = directory / "artifact.json"
    manifest_path = directory / "manifest.json"

    metadata = json.loads(artifact_path.read_text(encoding="utf-8"))
    metadata["environment_hash"] = "0" * 64
    forged_metadata = json.dumps(
        metadata, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    )
    artifact_path.write_text(forged_metadata, encoding="utf-8")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["files"]["artifact.json"] = hashlib.sha256(
        forged_metadata.encode("utf-8")
    ).hexdigest()
    manifest_path.write_text(
        json.dumps(manifest, sort_keys=True, separators=(",", ":"), ensure_ascii=False),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="integrity"):
        ComputeService(store_dir=tmp_path)


def test_persistence_rejects_symlinked_bundle_files(tmp_path: Path) -> None:
    service = ComputeService(store_dir=tmp_path / "store")
    job_id = service.submit_experiment(
        ExperimentSpec(purpose="symlink check", inputs={"n": 3}), SAFE_EXPERIMENT
    )
    artifact = service.artifact(job_id)
    outside = tmp_path / "outside.json"
    outside.write_text('{"result":true}', encoding="utf-8")
    output_path = tmp_path / "store" / artifact.artifact_id / "output.json"
    output_path.unlink()
    output_path.symlink_to(outside)

    with pytest.raises(ValueError, match="integrity"):
        ComputeService(store_dir=tmp_path / "store")
    assert outside.read_text(encoding="utf-8") == '{"result":true}'


def test_crash_cleanup_never_follows_an_attacker_staging_symlink(tmp_path: Path) -> None:
    store = tmp_path / "store"
    store.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    sentinel = outside / "sentinel"
    sentinel.write_text("preserve", encoding="utf-8")
    (store / ".tmp-attacker").symlink_to(outside, target_is_directory=True)

    with pytest.raises(ValueError, match="integrity"):
        ComputeService(store_dir=store)
    assert sentinel.read_text(encoding="utf-8") == "preserve"


def test_persistence_rejects_store_root_swapped_to_symlink_after_startup(tmp_path: Path) -> None:
    store = tmp_path / "store"
    service = ComputeService(store_dir=store)
    original = tmp_path / "original-store"
    store.rename(original)
    attacker_target = tmp_path / "attacker-target"
    attacker_target.mkdir()
    store.symlink_to(attacker_target, target_is_directory=True)

    with pytest.raises(ValueError, match="integrity"):
        service.submit_experiment(
            ExperimentSpec(purpose="root swap", inputs={"n": 2}), SAFE_EXPERIMENT
        )
    assert list(attacker_target.iterdir()) == []
    assert service.artifacts == {}
    assert all(job.status == "failed" for job in service.jobs.values())


def test_experiment_spec_snapshots_mutable_inputs() -> None:
    caller_inputs = {"n": 3, "nested": {"values": [1, 2]}}
    spec = ExperimentSpec(purpose="immutable spec", inputs=caller_inputs)
    original_hash = spec.spec_hash()

    caller_inputs["n"] = 99
    caller_inputs["nested"]["values"].append(3)

    assert spec.inputs["n"] == 3
    assert list(spec.inputs["nested"]["values"]) == [1, 2]
    assert spec.spec_hash() == original_hash


def test_computational_artifact_is_immutable_after_hashing() -> None:
    service = ComputeService()
    job_id = service.submit_experiment(
        ExperimentSpec(purpose="immutable artifact", inputs={"n": 2}, coverage="0..n"),
        SAFE_EXPERIMENT,
        claimed_classification="exhaustive_finite_subcase",
    )
    artifact = service.artifact(job_id)
    original_hash = artifact.output_hash

    with pytest.raises(TypeError):
        artifact.output["result"] = False
    with pytest.raises(FrozenInstanceError):
        artifact.claimed_classification = "exact_counterexample"
    assert artifact.output_hash == original_hash
    assert artifact.output["result"] is True


def test_caller_supplied_certificate_checker_cannot_self_approve() -> None:
    service = ComputeService()
    spec = ExperimentSpec(
        purpose="certificate authority",
        inputs={"n": 2},
        certificate_kind="finite-witness-v1",
        checker_id="trusted-finite-checker",
    )
    job_id = service.submit_experiment(
        spec,
        SAFE_EXPERIMENT,
        claimed_classification="certificate_checked_lemma",
    )
    artifact = service.artifact(job_id)

    with pytest.raises(TypeError):
        service.verify_certificate(
            artifact.artifact_id,
            lambda _artifact, _certificate: True,
            checker_id="trusted-finite-checker",
            certificate={"forged": True},
        )
    report = service.verify_certificate(
        artifact.artifact_id,
        checker_id="trusted-finite-checker",
        certificate={"forged": True},
    )

    assert not report.passed
    assert service.artifact(job_id).effective_classification() == "heuristic_numerical"


def test_checked_certificate_state_survives_restart(tmp_path: Path) -> None:
    checker = _trusted_checker()
    registry = {checker.checker_id: checker}
    service = ComputeService(store_dir=tmp_path, certificate_checkers=registry)
    spec = ExperimentSpec(
        purpose="durable certificate",
        inputs={"n": 2},
        certificate_kind="finite-witness-v1",
        checker_id="trusted-finite-checker",
    )
    job_id = service.submit_experiment(
        spec,
        SAFE_EXPERIMENT,
        claimed_classification="certificate_checked_lemma",
    )
    artifact = service.artifact(job_id)
    report = service.verify_certificate(
        artifact.artifact_id,
        checker_id="trusted-finite-checker",
        certificate={"output_hash": artifact.output_hash},
    )
    assert report.passed

    restarted = ComputeService(store_dir=tmp_path, certificate_checkers=registry)

    assert restarted.artifact(job_id).effective_classification() == "certificate_checked_lemma"
    assert len(list(tmp_path.glob("cert_art_*.json"))) == 1


def test_persisted_certificate_rejects_checker_attestation_drift(tmp_path: Path) -> None:
    checker = _trusted_checker(version="1")
    service = ComputeService(
        store_dir=tmp_path, certificate_checkers={checker.checker_id: checker}
    )
    spec = ExperimentSpec(
        purpose="checker drift",
        inputs={"n": 2},
        certificate_kind="finite-witness-v1",
        checker_id=checker.checker_id,
    )
    job_id = service.submit_experiment(
        spec, SAFE_EXPERIMENT, claimed_classification="certificate_checked_lemma"
    )
    artifact = service.artifact(job_id)
    assert service.verify_certificate(
        artifact.artifact_id,
        checker_id=checker.checker_id,
        certificate={"output_hash": artifact.output_hash},
    ).passed

    changed_checker = _trusted_checker(version="2")
    with pytest.raises(ValueError, match="attestation"):
        ComputeService(
            store_dir=tmp_path,
            certificate_checkers={changed_checker.checker_id: changed_checker},
        )


def test_checker_registry_and_identity_are_immutable() -> None:
    checker = _trusted_checker()
    caller_registry = {checker.checker_id: checker}
    service = ComputeService(certificate_checkers=caller_registry)

    caller_registry.clear()
    with pytest.raises(TypeError):
        service.certificate_checkers["attacker"] = checker
    with pytest.raises(AttributeError):
        service.certificate_checkers = {}
    with pytest.raises(AttributeError):
        service.sandbox = SubprocessSandbox()
    with pytest.raises(FrozenInstanceError):
        checker.version = "forged"
    assert service.certificate_checkers[checker.checker_id] is checker


def test_unavailable_oci_runtime_is_reported_without_unsandboxed_fallback() -> None:
    executor = ContainerSandbox("egmra/python:pinned", runtime="definitely-missing-runtime")
    try:
        result = executor.run(
            ExperimentSpec(purpose="oci unavailable", sandbox_policy="container"),
            "def experiment(inputs):\n    return {'result': True}\n",
        )
    except Exception as exc:  # pragma: no cover - the assertion is the point of this test
        pytest.fail(f"OCI unavailability must be a typed failed result, not {type(exc).__name__}")

    assert not result.ok
    assert result.failure_kind == "sandbox_unavailable"
    assert result.isolation == "oci-container"


def test_live_oci_path_overrides_an_image_entrypoint_when_locally_available() -> None:
    """Exercise Docker when the audited environment's local image is present.

    Absence remains an honest unavailable result; when present, a base image's
    entrypoint must never intercept or reinterpret the restricted runner command.
    """

    result = ContainerSandbox("postgres:17-alpine").run(
        ExperimentSpec(purpose="OCI entrypoint audit", sandbox_policy="container", wall_seconds=10),
        "def experiment(inputs):\n    return {'result': True}\n",
    )

    if result.failure_kind == "sandbox_unavailable":
        assert not result.ok and "unavailable" in result.stderr.lower()
        return
    assert not result.ok  # this audited base image intentionally has no Python
    assert "docker-entrypoint.sh" not in result.stderr
    assert "python3" in result.stderr
