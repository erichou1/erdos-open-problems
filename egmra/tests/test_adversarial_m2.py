"""Security and honesty checks for the local scale-layer substitutes."""


import pytest

from egmra.m2 import ContentAddressedObjectStore, M2Assembly, PostgresEventStore
from egmra.truth.events import EventLog


@pytest.mark.parametrize("digest", ["../secret", "0" * 63, "A" * 64, "/tmp/escape"])
def test_object_store_rejects_path_like_or_invalid_digests(tmp_path, digest):
    store = ContentAddressedObjectStore(tmp_path / "objects")
    with pytest.raises(ValueError, match="SHA-256"):
        store.get(digest)
    with pytest.raises(ValueError, match="SHA-256"):
        store.exists(digest)


def test_object_store_detects_corruption_and_symlink_substitution(tmp_path):
    store = ContentAddressedObjectStore(tmp_path / "objects")
    digest = store.put(b"trusted")
    path = tmp_path / "objects" / digest[:2] / digest
    path.write_bytes(b"forged")
    with pytest.raises(ValueError, match="integrity"):
        store.get(digest)

    path.unlink()
    target = tmp_path / "outside"
    target.write_bytes(b"trusted")
    path.symlink_to(target)
    with pytest.raises(ValueError, match="regular non-symlink"):
        store.get(digest)


def test_object_store_rejects_symlinked_prefix_directory(tmp_path):
    store = ContentAddressedObjectStore(tmp_path / "objects")
    data = b"trusted"
    from egmra.provenance.hashing import sha256_bytes
    digest = sha256_bytes(data)
    outside = tmp_path / "outside-prefix"
    outside.mkdir()
    (outside / digest).write_bytes(data)
    (tmp_path / "objects" / digest[:2]).symlink_to(outside, target_is_directory=True)
    with pytest.raises(ValueError, match="prefix"):
        store.get(digest)


def test_object_store_is_atomic_bounded_and_private(tmp_path):
    store = ContentAddressedObjectStore(tmp_path / "objects", max_object_bytes=16)
    digest = store.put(b"small")
    path = tmp_path / "objects" / digest[:2] / digest
    assert path.stat().st_mode & 0o777 == 0o600
    with pytest.raises(ValueError, match="too large"):
        store.put(b"x" * 17)
    with pytest.raises(TypeError):
        store.put("not-bytes")


def test_object_store_rejects_root_replacement_after_initialization(tmp_path):
    root = tmp_path / "objects"
    store = ContentAddressedObjectStore(root)
    old = tmp_path / "old"
    root.rename(old)
    root.mkdir()
    with pytest.raises(ValueError, match="root changed"):
        store.put(b"x")


@pytest.mark.parametrize(
    "dsn",
    ["", "sqlite:///tmp/x", "postgres://", "postgresql://host-without-db"],
)
def test_postgres_adapter_rejects_malformed_configuration(dsn):
    with pytest.raises(ValueError, match="Postgres DSN"):
        PostgresEventStore(dsn)


def test_postgres_failure_never_echoes_credentials():
    pg = PostgresEventStore("postgresql://user:top-secret@localhost/egmra")
    with pytest.raises(RuntimeError) as caught:
        pg.connect()
    assert "top-secret" not in str(caught.value)


def test_m2_assembly_rejects_invalid_capacity_and_host_sandbox_default(tmp_path):
    log = EventLog(tmp_path / "events.jsonl")
    store = ContentAddressedObjectStore(tmp_path / "objects")
    with pytest.raises(ValueError):
        M2Assembly(log, store, concurrent_programs=0)
    assembly = M2Assembly(log, store)
    assert assembly.m2_ready() is False
    assert assembly.sandbox is None
