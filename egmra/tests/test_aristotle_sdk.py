"""Tests for the official Aristotle SDK adapter (task B2) with a fake SDK."""

from __future__ import annotations

import hmac
from types import SimpleNamespace

import pytest

from egmra.lean.aristotle_sdk import AristotleSdkClient, AristotleSubmission
from egmra.lean.aristotle_api import AristotleClientError, UnsafeArchiveError, UnsafeJobIdError
from egmra.lean.replay import LeanReplayTarget, LeanReplayVerifier
from egmra.lean.service import CheckerAttestation, CheckerRequest, LeanEnvironment, _checker_key
from egmra.provenance.hashing import canonical_json, sha256_bytes, sha256_hex

_ENV = {"ARISTOTLE_API_KEY": "aristotle-test-key-not-a-real-secret"}


class _FakeTask:
    def __init__(self, task_id="task-1", status="COMPLETE"):
        self.agent_task_id = task_id
        self.status = SimpleNamespace(name=status)
        self.percent_complete = 100
        self.waited = False

    def refresh(self):
        pass

    def wait_for_completion(self, num_events: int = 3):
        self.waited = True


class _FakeProject:
    def __init__(self, project_id="proj-1", task=None, files=(("Proof.lean", "theorem t : True := trivial"),),
                 symlink=None):
        self.project_id = project_id
        self._task = task or _FakeTask()
        self._files = files
        self._symlink = symlink

    def get_tasks(self, limit=10, **kw):
        return [self._task], None

    def get_files(self, destination):
        from pathlib import Path

        dest = Path(destination)
        dest.mkdir(parents=True, exist_ok=True)
        for name, body in self._files:
            (dest / name).write_text(body, encoding="utf-8")
        if self._symlink is not None:
            (dest / self._symlink).symlink_to("/etc/passwd")


class _FakeSdk:
    def __init__(self, project):
        self._project = project
        self.api_key = None
        outer = self

        class Project:
            @staticmethod
            def create_from_directory(prompt, project_dir, *a, **k):
                outer._project.prompt = prompt
                return outer._project

            @staticmethod
            def from_id(object_id):
                return outer._project

        class AgentTask:
            @staticmethod
            def from_id(object_id):
                return outer._project._task

        self.Project = Project
        self.AgentTask = AgentTask

    def set_api_key(self, key):
        self.api_key = key
        return key


def _client(tmp_path, *, project=None, project_dir="lean_project"):
    (tmp_path / project_dir).mkdir(exist_ok=True)
    return AristotleSdkClient(
        quarantine_root=tmp_path / "quar",
        project_dir=tmp_path / project_dir,
        sdk=_FakeSdk(project or _FakeProject()),
        env=_ENV,
    )


def test_requires_api_key(tmp_path):
    (tmp_path / "lean_project").mkdir()
    with pytest.raises(AristotleClientError):
        AristotleSdkClient(quarantine_root=tmp_path / "q", project_dir=tmp_path / "lean_project",
                           sdk=_FakeSdk(_FakeProject()), env={})


def test_submit_sets_key_and_returns_safe_ids(tmp_path):
    client = _client(tmp_path)
    sub = client.submit("Prove that there are infinitely many primes.")
    assert isinstance(sub, AristotleSubmission)
    assert sub.project_id == "proj-1" and sub.agent_task_id == "task-1"
    assert client.sdk.api_key == _ENV["ARISTOTLE_API_KEY"]


def test_submit_rejects_unsafe_project_id(tmp_path):
    client = _client(tmp_path, project=_FakeProject(project_id="../escape"))
    with pytest.raises(UnsafeJobIdError):
        client.submit("prove something")


def test_poll_maps_complete_but_never_promotes(tmp_path):
    client = _client(tmp_path)
    sub = client.submit("q")
    status = client.poll(sub)
    assert status.vendor_reports_complete is True
    assert status.failed is False
    assert status.promotable is False


def test_poll_maps_failure(tmp_path):
    client = _client(tmp_path, project=_FakeProject(task=_FakeTask(status="OUT_OF_BUDGET")))
    sub = client.submit("q")
    status = client.poll(sub)
    assert status.failed is True and status.vendor_reports_complete is False


def test_fetch_quarantines_and_is_not_promotable(tmp_path):
    client = _client(tmp_path)
    sub = client.submit("q")
    artifact = client.fetch(sub)
    assert artifact.promotable is False
    assert any(p.name == "Proof.lean" for p in artifact.extracted_files)
    assert client.quarantine_root.resolve() in artifact.quarantine_dir.resolve().parents


def test_fetch_rejects_symlink_in_downloaded_tree(tmp_path):
    client = _client(tmp_path, project=_FakeProject(symlink="evil-link"))
    sub = client.submit("q")
    with pytest.raises(UnsafeArchiveError):
        client.fetch(sub)


# ── promotion requires a real local Lean replay (never the vendor) ──────────

def _valid_attestation(request: CheckerRequest) -> CheckerAttestation:
    key = _checker_key(None)
    att = CheckerAttestation(
        environment_id=request.environment_id, source_hash=request.source_hash,
        declaration_name=request.declaration_name, expected_type_hash=request.expected_type_hash,
        candidate_type_hash=request.expected_type_hash,
        candidate_declaration_hash=sha256_hex("cd"), proof_term_hash=sha256_hex("pt"),
        immutable_target_module_hash=request.immutable_target_module_hash,
        trust_policy_hash=request.trust_policy_hash, source_tree_hash=sha256_hex("st"),
        imports_hash=sha256_hex("im"), checker_id="local-kernel", checker_version="1",
        checker_trust_base="lean4-kernel", checker_binary_hash=sha256_hex("bin"),
        checker_log_hash=sha256_hex("log"), transitive_axioms=("propext",),
        placeholder_findings=(), unsafe_findings=(), imports_audited=True,
        axiom_closure_verified=True, immutable_target_isolated=True, clean_replay=True,
        network_disabled=True, kernel_verified=True, production=True,
        issued_at="2026-07-13T00:00:00Z", key_fingerprint=sha256_bytes(key),
    )
    sig = hmac.new(key, canonical_json(att.signed_record()).encode("utf-8"), "sha256").hexdigest()
    return CheckerAttestation(**(att.__dict__ | {"signature": sig}))


class _Checker:
    def run(self, request):
        return _valid_attestation(request)


def test_vendor_complete_alone_does_not_promote_only_local_replay_does(tmp_path):
    client = _client(tmp_path)
    sub = client.submit("q")
    artifact = client.fetch(sub)
    # Vendor said COMPLETE, but the artifact is not promotable on arrival.
    assert artifact.vendor_reports_complete and not artifact.promotable

    env = LeanEnvironment(lean_version="4.28.0", mathlib_commit="v4.28.0",
                          project_hash=sha256_hex("proj"))
    target = LeanReplayTarget(
        claim_id="goal", declaration_name="egmra_target",
        normalized_target_hash=sha256_hex("nt"), expected_type_hash=sha256_hex("et"),
        immutable_target_module_hash=sha256_hex("mod"), trust_policy_hash=sha256_hex("tp"),
    )
    result = client.bind_local_replay(
        artifact, LeanReplayVerifier(checker=_Checker(), environment=env, target=target),
        expected_claim_id="goal")
    assert result.verified is True and result.promotable is True
