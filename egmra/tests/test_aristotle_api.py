"""Tests for the Aristotle API client and its hardened archive intake."""

from __future__ import annotations

import io
import tarfile
import zipfile

import pytest

from egmra.lean.aristotle_api import (
    AristotleApiClient,
    AristotleTransportError,
    LocalLeanReplayAttestation,
    LocalReplayResult,
    UnsafeArchiveError,
    UnsafeJobIdError,
    safe_extract_archive,
    seal_local_lean_replay_attestation,
)
from egmra.lean.aristotle_routing import AristotleRequest


def _zip(files, *, symlink=None, extra_entries=0):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        for name, data in files:
            zf.writestr(name, data)
        if symlink is not None:
            link_name, target = symlink
            info = zipfile.ZipInfo(link_name)
            info.external_attr = 0o120777 << 16  # symlink mode bits
            zf.writestr(info, target)
        for i in range(extra_entries):
            zf.writestr(f"pad/{i}.txt", "x")
    return buf.getvalue()


def _tar(files, *, symlink=None, traversal=None):
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w") as tar:
        for name, data in files:
            raw = data.encode()
            info = tarfile.TarInfo(name)
            info.size = len(raw)
            tar.addfile(info, io.BytesIO(raw))
        if symlink is not None:
            link_name, target = symlink
            info = tarfile.TarInfo(link_name)
            info.type = tarfile.SYMTYPE
            info.linkname = target
            tar.addfile(info)
        if traversal is not None:
            raw = b"evil"
            info = tarfile.TarInfo(traversal)
            info.size = len(raw)
            tar.addfile(info, io.BytesIO(raw))
    return buf.getvalue()


# ── safe_extract_archive ────────────────────────────────────────────────────

def test_safe_extract_zip_writes_files_within_quarantine(tmp_path):
    archive = _zip([("Proof.lean", "theorem t : True := trivial"), ("dir/aux.lean", "def a := 1")])
    files, total = safe_extract_archive(archive, tmp_path / "q")
    names = sorted(p.name for p in files)
    assert names == ["Proof.lean", "aux.lean"]
    assert total > 0
    assert all((tmp_path / "q").resolve() in p.resolve().parents for p in files)


def test_safe_extract_rejects_zip_traversal(tmp_path):
    archive = _zip([("../escape.lean", "x")])
    with pytest.raises(UnsafeArchiveError, match="traversal"):
        safe_extract_archive(archive, tmp_path / "q")


def test_safe_extract_rejects_absolute_path(tmp_path):
    archive = _zip([("/etc/evil.lean", "x")])
    with pytest.raises(UnsafeArchiveError, match="absolute"):
        safe_extract_archive(archive, tmp_path / "q")


def test_safe_extract_rejects_zip_symlink(tmp_path):
    archive = _zip([("ok.lean", "x")], symlink=("link", "/etc/passwd"))
    with pytest.raises(UnsafeArchiveError, match="symlink"):
        safe_extract_archive(archive, tmp_path / "q")


def test_safe_extract_rejects_tar_symlink(tmp_path):
    archive = _tar([("ok.lean", "x")], symlink=("link", "/etc/passwd"))
    with pytest.raises(UnsafeArchiveError, match="link"):
        safe_extract_archive(archive, tmp_path / "q")


def test_safe_extract_rejects_tar_traversal(tmp_path):
    archive = _tar([("ok.lean", "x")], traversal="../../escape")
    with pytest.raises(UnsafeArchiveError, match="traversal"):
        safe_extract_archive(archive, tmp_path / "q")


def test_safe_extract_enforces_entry_count(tmp_path):
    archive = _zip([("a.lean", "x")], extra_entries=10)
    with pytest.raises(UnsafeArchiveError, match="too many entries"):
        safe_extract_archive(archive, tmp_path / "q", max_entries=3)


def test_safe_extract_enforces_entry_size(tmp_path):
    archive = _zip([("big.lean", "y" * 100)])
    with pytest.raises(UnsafeArchiveError, match="too large"):
        safe_extract_archive(archive, tmp_path / "q", max_entry_bytes=10)


def test_safe_extract_enforces_total_size(tmp_path):
    archive = _zip([("a.lean", "y" * 40), ("b.lean", "z" * 40)])
    with pytest.raises(UnsafeArchiveError, match="total-size"):
        safe_extract_archive(archive, tmp_path / "q", max_entry_bytes=100, max_total_bytes=50)


def test_safe_extract_rejects_unrecognized_archive(tmp_path):
    with pytest.raises(UnsafeArchiveError, match="unrecognized|corrupt"):
        safe_extract_archive(b"not an archive at all", tmp_path / "q")


# ── AristotleApiClient ──────────────────────────────────────────────────────

class FakeTransport:
    def __init__(self, *, job_id="job-1", poll_record=None, archive=b"",
                 fail_on=None):
        self._job_id = job_id
        self._poll_record = poll_record or {"status": "complete"}
        self._archive = archive
        self._fail_on = fail_on or set()
        self.submitted = []

    def submit(self, payload):
        if "submit" in self._fail_on:
            raise RuntimeError("boom")
        self.submitted.append(payload)
        return self._job_id

    def poll(self, job_id):
        if "poll" in self._fail_on:
            raise RuntimeError("boom")
        return dict(self._poll_record)

    def download(self, job_id):
        if "download" in self._fail_on:
            raise RuntimeError("boom")
        return self._archive


def _request(*, licensing_ok=True):
    return AristotleRequest(
        locked_target_hash="a" * 64, toolchain_hash="b" * 64,
        bounded_leaf="lemma x", source_packet_hash="c" * 64, licensing_ok=licensing_ok,
    )


def test_submit_enforces_licensing_before_transport(tmp_path):
    transport = FakeTransport()
    client = AristotleApiClient(transport=transport, quarantine_root=tmp_path)
    with pytest.raises(PermissionError):
        client.submit(_request(licensing_ok=False))
    assert transport.submitted == []  # nothing left the host


def test_submit_returns_job_id(tmp_path):
    transport = FakeTransport(job_id="job-42")
    client = AristotleApiClient(transport=transport, quarantine_root=tmp_path)
    assert client.submit(_request()) == "job-42"


def test_poll_normalizes_vendor_complete_without_promotion(tmp_path):
    transport = FakeTransport(poll_record={"status": "SOLVED", "extra": 1})
    client = AristotleApiClient(transport=transport, quarantine_root=tmp_path)
    status = client.poll("job-1")
    assert status.vendor_reports_complete is True
    assert status.failed is False
    assert status.promotable is False  # vendor status is never a promotion
    assert status.detail == {"extra": 1}


def test_poll_detects_failure_status(tmp_path):
    transport = FakeTransport(poll_record={"status": "failed"})
    client = AristotleApiClient(transport=transport, quarantine_root=tmp_path)
    status = client.poll("job-1")
    assert status.failed is True
    assert status.vendor_reports_complete is False


def test_download_quarantines_and_is_not_promotable(tmp_path):
    archive = _zip([("Proof.lean", "theorem t : True := trivial")])
    transport = FakeTransport(archive=archive)
    client = AristotleApiClient(transport=transport, quarantine_root=tmp_path / "quar")
    artifact = client.download("job-9", vendor_status="complete")
    assert artifact.vendor_reports_complete is True
    assert artifact.promotable is False  # arrival never promotes
    assert artifact.quarantine_dir.name == "job-9"
    assert any(p.name == "Proof.lean" for p in artifact.extracted_files)


def _sealed_attestation_for(client, artifact, *, claim_id="goal"):
    """Build a correctly-sealed, artifact-bound attestation (the trusted path)."""
    return seal_local_lean_replay_attestation(LocalLeanReplayAttestation(
        claim_id=claim_id,
        normalized_target_hash="t" * 64,
        source_hash="s" * 64,
        environment_hash="e" * 64,
        lean_version="4.9.0",
        mathlib_commit="deadbeef",
        artifact_hash=client.artifact_hash(artifact),
        checker_id="local-kernel",
        replay_log_hash="l" * 64,
        issued_at="2026-07-13T00:00:00Z",
    ))


def test_bind_local_replay_only_promotes_on_sealed_attestation(tmp_path):
    archive = _zip([("Proof.lean", "theorem t : True := trivial")])
    client = AristotleApiClient(transport=FakeTransport(archive=archive),
                                quarantine_root=tmp_path)
    artifact = client.download("job-1", vendor_status="complete")

    good = _sealed_attestation_for(client, artifact, claim_id="goal")
    passed = client.bind_local_replay(artifact, lambda _dir: good, expected_claim_id="goal")
    assert passed.verified is True and passed.promotable is True


def test_bind_local_replay_rejects_truthy_non_attestation(tmp_path):
    # Adversarial: a caller boolean/string/dict must never manufacture verification.
    archive = _zip([("Proof.lean", "x")])
    client = AristotleApiClient(transport=FakeTransport(archive=archive),
                                quarantine_root=tmp_path)
    artifact = client.download("job-1")
    for truthy in (True, "vendor says COMPLETE", {"status": "ok"}, 1, object()):
        res = client.bind_local_replay(artifact, lambda _dir, v=truthy: v)
        assert res.verified is False and res.promotable is False


def test_bind_local_replay_rejects_forged_seal(tmp_path):
    archive = _zip([("Proof.lean", "x")])
    client = AristotleApiClient(transport=FakeTransport(archive=archive),
                                quarantine_root=tmp_path)
    artifact = client.download("job-1")
    forged = LocalLeanReplayAttestation(
        claim_id="goal", normalized_target_hash="t" * 64, source_hash="s" * 64,
        environment_hash="e" * 64, lean_version="4.9.0", mathlib_commit="c",
        artifact_hash=client.artifact_hash(artifact), checker_id="x",
        replay_log_hash="l" * 64, issued_at="2026-07-13T00:00:00Z",
        signature="0" * 64,  # not a valid HMAC
    )
    res = client.bind_local_replay(artifact, lambda _dir: forged)
    assert res.verified is False


def test_bind_local_replay_rejects_attestation_for_other_artifact(tmp_path):
    archive = _zip([("Proof.lean", "x")])
    client = AristotleApiClient(transport=FakeTransport(archive=archive),
                                quarantine_root=tmp_path)
    artifact = client.download("job-1")
    # A sealed attestation whose artifact_hash names a *different* artifact.
    mismatched = seal_local_lean_replay_attestation(LocalLeanReplayAttestation(
        claim_id="goal", normalized_target_hash="t" * 64, source_hash="s" * 64,
        environment_hash="e" * 64, lean_version="4.9.0", mathlib_commit="c",
        artifact_hash="f" * 64, checker_id="x", replay_log_hash="l" * 64,
        issued_at="2026-07-13T00:00:00Z",
    ))
    res = client.bind_local_replay(artifact, lambda _dir: mismatched)
    assert res.verified is False and "not bound" in res.detail


def test_bind_local_replay_rejects_wrong_claim_id(tmp_path):
    archive = _zip([("Proof.lean", "x")])
    client = AristotleApiClient(transport=FakeTransport(archive=archive),
                                quarantine_root=tmp_path)
    artifact = client.download("job-1")
    att = _sealed_attestation_for(client, artifact, claim_id="some-other-claim")
    res = client.bind_local_replay(artifact, lambda _dir: att, expected_claim_id="goal")
    assert res.verified is False


def test_bind_local_replay_treats_verifier_error_as_rejection(tmp_path):
    archive = _zip([("Proof.lean", "x")])
    client = AristotleApiClient(transport=FakeTransport(archive=archive),
                                quarantine_root=tmp_path)
    artifact = client.download("job-1")

    def _explode(_dir):
        raise RuntimeError("kernel unavailable")

    result = client.bind_local_replay(artifact, _explode)
    assert isinstance(result, LocalReplayResult)
    assert result.verified is False and result.promotable is False
    assert "raised" in result.detail


# ── job-id sanitization / quarantine escape (defect 7) ──────────────────────

def test_download_rejects_traversal_job_id(tmp_path):
    client = AristotleApiClient(transport=FakeTransport(archive=_zip([("a.lean", "x")])),
                                quarantine_root=tmp_path / "root")
    with pytest.raises(UnsafeJobIdError):
        client.download("../../../../tmp/egmra_escape")


@pytest.mark.parametrize("bad", ["../evil", "a/b", "/abs", "..", ".hidden", "a" * 200, ""])
def test_download_rejects_unsafe_job_ids(bad, tmp_path):
    client = AristotleApiClient(transport=FakeTransport(archive=_zip([("a.lean", "x")])),
                                quarantine_root=tmp_path / "root")
    with pytest.raises(UnsafeJobIdError):
        client.download(bad)


def test_download_stays_within_quarantine_root(tmp_path):
    root = (tmp_path / "root")
    client = AristotleApiClient(transport=FakeTransport(archive=_zip([("a.lean", "x")])),
                                quarantine_root=root)
    artifact = client.download("job-77")
    assert root.resolve() in artifact.quarantine_dir.resolve().parents


def test_submit_validates_returned_job_id(tmp_path):
    client = AristotleApiClient(transport=FakeTransport(job_id="../escape"),
                                quarantine_root=tmp_path)
    with pytest.raises(UnsafeJobIdError):
        client.submit(_request())


def test_vendor_complete_alone_never_promotes(tmp_path):
    # End-to-end: even a 'solved' vendor status yields no promotion without replay.
    archive = _zip([("Proof.lean", "theorem t : True := trivial")])
    transport = FakeTransport(poll_record={"status": "solved"}, archive=archive)
    client = AristotleApiClient(transport=transport, quarantine_root=tmp_path)
    status = client.poll("job-1")
    artifact = client.download("job-1", vendor_status=status.raw_status)
    assert status.vendor_reports_complete and not status.promotable
    assert artifact.vendor_reports_complete and not artifact.promotable


def test_transport_errors_are_normalized(tmp_path):
    client = AristotleApiClient(transport=FakeTransport(fail_on={"poll"}),
                                quarantine_root=tmp_path)
    with pytest.raises(AristotleTransportError):
        client.poll("job-1")
