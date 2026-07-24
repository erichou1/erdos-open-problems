"""Exchange-level durability: replay identical model exchanges across attempts.

The signed branch checkpoints proved too coarse for live browser runs: a
branch is a 30-60 minute unit of deep-think exchanges, and a run that dies
mid-branch (timeout, throttle, crash) left NOTHING to resume — every retry
re-bought every exchange.  This wrapper makes the individual model exchange
the durable unit.

Correctness comes from the key, not from trust: a cached reply is returned
ONLY for a byte-identical prompt (keyed by its SHA-256).  Round-2 prompts
embed the round-1 ledger, so a replayed chain stays valid exactly as far as
the reconstruction is identical and goes live at the first divergence —
stale or foreign progress can never leak into a changed context.

Honesty invariants:

* replaying is returning the SAME model output for the IDENTICAL prompt; the
  recorded model identity (attested or not) is preserved verbatim — a replay
  never upgrades attestation;
* nothing here touches truth: replayed output re-enters the same parsing,
  admission, and verification pipeline as a live reply;
* fail-open to LIVE, never to fabrication: a missing, malformed, oversized,
  or symlinked cache entry is treated as a miss and the real runner is asked.
"""

from __future__ import annotations

import json
import os
import re
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from egmra.agents.runner import RunnerResponse
from egmra.provenance.hashing import sha256_hex
from egmra.provenance.stage_identity import AttestedModelIdentity

_MAX_ENTRY_BYTES = 4_000_000
_SCHEMA_VERSION = 1
_STAGE_SAFE = re.compile(r"[^A-Za-z0-9_.-]+")


@dataclass
class CachedRunner:
    """Wrap any ``ModelRunner`` with a durable per-prompt exchange cache.

    ``salt`` partitions the cache: an empty salt (default) keys purely on the
    prompt — crash retries replay byte-identical exchanges free. A non-empty
    salt (e.g. the count of previously RECORDED outcomes for the problem)
    yields fresh, independent samples on retries after a completed-but-failed
    attempt — pass@k semantics — while never invalidating existing entries.
    """

    runner: Any
    cache_dir: Path
    salt: str = ""
    hits: int = field(default=0, init=False)
    misses: int = field(default=0, init=False)

    @property
    def runner_id(self) -> str:
        return getattr(self.runner, "runner_id", "cached")

    def __getattr__(self, name: str) -> Any:
        # Delegate everything else (records/transcripts/close/...) so the
        # wrapper is transparent to provenance recording and teardown.
        return getattr(object.__getattribute__(self, "runner"), name)

    def _entry_path(self, stage: str, prompt_hash: str) -> Path:
        safe_stage = _STAGE_SAFE.sub("_", stage)[:80] or "stage"
        return Path(self.cache_dir) / f"{safe_stage}.{prompt_hash}.json"

    def _load(self, path: Path, cache_key: str) -> RunnerResponse | None:
        try:
            if path.is_symlink() or not path.is_file():
                return None
            if path.stat().st_size > _MAX_ENTRY_BYTES:
                return None
            record = json.loads(path.read_text(encoding="utf-8"))
            if (
                not isinstance(record, dict)
                or record.get("schema_version") != _SCHEMA_VERSION
                # Pre-salt entries carry no cache_key; their key IS the prompt
                # hash, so the fallback keeps existing caches replayable.
                or record.get("cache_key", record.get("prompt_hash")) != cache_key
                or not isinstance(record.get("text"), str)
                or not record["text"].strip()
            ):
                return None
            identity = record.get("model")
            if not isinstance(identity, dict):
                return None
            return RunnerResponse(
                text=record["text"],
                model=AttestedModelIdentity(**identity),
                context_id=str(record.get("context_id", "")),
                prompt_hash=str(record.get("prompt_hash", cache_key)),
                # Optional for backward compatibility with schema-v1 entries
                # written before conversation URLs were propagated.
                conversation_url=str(record.get("conversation_url", "")),
            )
        except (OSError, ValueError, TypeError, json.JSONDecodeError):
            return None

    def _store(self, stage: str, response: RunnerResponse, cache_key: str) -> None:
        try:
            if not response.text.strip():
                return                      # never cache an empty exchange
            model = response.model
            record = {
                "schema_version": _SCHEMA_VERSION,
                "stage": stage,
                "cache_key": cache_key,
                "prompt_hash": response.prompt_hash,
                "response_hash": sha256_hex(response.text),
                "text": response.text,
                "context_id": response.context_id,
                "conversation_url": response.conversation_url,
                "model": {
                    "provider": model.provider,
                    "model": model.model,
                    "version": model.version,
                    "build_id": model.build_id,
                    "ui_surface": model.ui_surface,
                    "account_class": model.account_class,
                    "attestation": model.attestation,
                },
            }
            payload = json.dumps(record, ensure_ascii=False)
            if len(payload.encode("utf-8")) > _MAX_ENTRY_BYTES:
                return
            directory = Path(self.cache_dir)
            directory.mkdir(parents=True, exist_ok=True)
            fd, tmp_name = tempfile.mkstemp(dir=directory, suffix=".tmp")
            try:
                with os.fdopen(fd, "w", encoding="utf-8") as handle:
                    handle.write(payload)
                os.chmod(tmp_name, 0o600)
                os.replace(tmp_name, self._entry_path(stage, cache_key))
            except BaseException:
                try:
                    os.unlink(tmp_name)
                except OSError:
                    pass
                raise
        except OSError:
            # Cache persistence is an ops aid; a write failure never affects
            # the live response (and never becomes a mathematical verdict).
            return

    def run(self, prompt: str, *, stage: str) -> RunnerResponse:
        cache_key = (
            sha256_hex(f"{self.salt}\n{prompt}") if self.salt else sha256_hex(prompt)
        )
        cached = self._load(self._entry_path(stage, cache_key), cache_key)
        if cached is not None:
            self.hits += 1
            return cached
        self.misses += 1
        response = self.runner.run(prompt, stage=stage)
        self._store(stage, response, cache_key)
        return response
