"""Read-only, integrity-checked OEIS client (spec §8.2)."""

from __future__ import annotations

import json
import math
import os
import re
import tempfile
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from types import MappingProxyType
from typing import Any, Callable, Mapping
from urllib.parse import urljoin, urlencode, urlsplit

from egmra.provenance.hashing import canonical_json, sha256_hex

OEIS_JSON_ENDPOINT = "https://oeis.org/search"
OEIS_AI_SUBMISSION_FORBIDDEN = (
    "OEIS forbids AI-generated submissions/editorial responses; EGMRA may only "
    "read. A permitted submission requires an identified, responsible human author."
)
_A_NUMBER = re.compile(r"^A[0-9]{6}$")
_MAX_HTTP_REDIRECTS = 5
_MAX_HTTP_RESPONSE_BYTES = 4 * 1024 * 1024
_REDIRECT_STATUS_CODES = frozenset({301, 302, 303, 307, 308})
_OEIS_HOSTS = frozenset({"oeis.org", "www.oeis.org"})


class OEISPolicyError(RuntimeError):
    pass


class OEISUnavailable(RuntimeError):
    pass


Fetcher = Callable[[str], str]


def _freeze(value: Any) -> Any:
    if isinstance(value, dict):
        return MappingProxyType({key: _freeze(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(_freeze(item) for item in value)
    return value


@dataclass(frozen=True)
class OEISResponse:
    query: str
    raw: Mapping[str, Any]
    retrieved_at: str
    content_hash: str
    from_cache: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "raw", _freeze(dict(self.raw)))

    def entries(self) -> list[dict]:
        return json.loads(canonical_json(list(self.raw.get("results") or ())))


@dataclass
class OEISClient:
    fetcher: Fetcher | None = None
    cache_dir: Path | None = None
    offline: bool = True
    min_interval_s: float = 1.0
    _last_request: float = field(default=0.0, init=False)
    _mem_cache: dict[str, tuple[OEISResponse, str]] = field(default_factory=dict, init=False)
    _lock: threading.Lock = field(default_factory=threading.Lock, init=False, repr=False)

    def __post_init__(self) -> None:
        if not math.isfinite(self.min_interval_s) or self.min_interval_s < 0:
            raise ValueError("min_interval_s must be finite and non-negative")
        if self.cache_dir is not None:
            self.cache_dir = Path(self.cache_dir)
            if self.cache_dir.exists() and self.cache_dir.is_symlink():
                raise OEISUnavailable("OEIS cache directory may not be a symlink")

    def submit(self, *_args, **_kwargs) -> None:
        raise OEISPolicyError(OEIS_AI_SUBMISSION_FORBIDDEN)

    def _cache_key(self, query: str) -> str:
        return sha256_hex(query)

    def _cache_path(self, query: str) -> Path | None:
        if self.cache_dir is None:
            return None
        return self.cache_dir / f"{self._cache_key(query)}.json"

    @staticmethod
    def _parse_response(text: str) -> dict[str, Any]:
        try:
            raw = json.loads(text, object_pairs_hook=_reject_duplicate_keys)
        except (json.JSONDecodeError, ValueError) as exc:
            raise OEISUnavailable(f"OEIS response is not valid JSON: {exc}") from exc
        # Live OEIS may return either the classic ``{"results": [...]}`` object or a
        # bare top-level array of result objects; normalize the array form so the
        # rest of the client sees a single consistent shape.
        if isinstance(raw, list):
            raw = {"results": raw}
        if not isinstance(raw, dict):
            raise OEISUnavailable("OEIS JSON response must be an object or array")
        results = raw.get("results")
        if results is not None and not isinstance(results, list):
            raise OEISUnavailable("OEIS JSON results must be an array or null")
        if isinstance(results, list) and any(not isinstance(item, dict) for item in results):
            raise OEISUnavailable("OEIS JSON result entries must be objects")
        return raw

    def _load_cache(self, query: str) -> OEISResponse | None:
        if query in self._mem_cache:
            hit, text = self._mem_cache[query]
            if sha256_hex(text) != hit.content_hash:
                raise OEISUnavailable("OEIS memory-cache integrity check failed")
            return OEISResponse(hit.query, hit.raw, hit.retrieved_at, hit.content_hash, True)
        path = self._cache_path(query)
        if path and path.exists():
            if path.is_symlink():
                raise OEISUnavailable("OEIS cache entry is an unsafe symlink")
            try:
                doc = json.loads(path.read_text(encoding="utf-8"),
                                 object_pairs_hook=_reject_duplicate_keys)
                if set(doc) != {"query", "response_text", "retrieved_at", "content_hash"}:
                    raise ValueError("unexpected cache schema")
                if doc["query"] != query:
                    raise ValueError("cache query binding mismatch")
                text = doc["response_text"]
                if sha256_hex(text) != doc["content_hash"]:
                    raise ValueError("content hash mismatch")
                raw = self._parse_response(text)
                return OEISResponse(
                    query, raw, doc["retrieved_at"], doc["content_hash"], True
                )
            except (OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
                raise OEISUnavailable(f"OEIS cache integrity check failed: {exc}") from exc
        return None

    def _store_cache(self, resp: OEISResponse, response_text: str) -> None:
        self._mem_cache[resp.query] = (resp, response_text)
        path = self._cache_path(resp.query)
        if path is None:
            return
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.parent.is_symlink() or (path.exists() and path.is_symlink()):
            raise OEISUnavailable("refusing unsafe OEIS cache symlink")
        document = json.dumps({
            "query": resp.query,
            "response_text": response_text,
            "retrieved_at": resp.retrieved_at,
            "content_hash": resp.content_hash,
        }, ensure_ascii=False, sort_keys=True)
        fd, temp_name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
        try:
            os.fchmod(fd, 0o600)
            with os.fdopen(fd, "w", encoding="utf-8") as stream:
                stream.write(document)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temp_name, path)
        finally:
            if os.path.exists(temp_name):
                os.unlink(temp_name)

    def _throttle(self) -> None:
        with self._lock:
            elapsed = time.monotonic() - self._last_request
            if elapsed < self.min_interval_s:
                time.sleep(self.min_interval_s - elapsed)
            self._last_request = time.monotonic()

    def query_terms(self, terms: list[int], *, use_cache: bool = True) -> OEISResponse:
        if not terms or len(terms) > 100 or any(type(term) is not int for term in terms):
            raise ValueError("OEIS terms must be 1-100 exact integers")
        query = urlencode({"q": ",".join(str(term) for term in terms), "fmt": "json"})
        return self._query(query, use_cache=use_cache)

    def query_anumber(self, a_number: str, *, use_cache: bool = True) -> OEISResponse:
        if not isinstance(a_number, str) or not _A_NUMBER.fullmatch(a_number):
            raise ValueError("OEIS A-number must have the form A followed by six digits")
        query = urlencode({"q": f"id:{a_number}", "fmt": "json"})
        return self._query(query, use_cache=use_cache)

    def _query(self, query: str, *, use_cache: bool) -> OEISResponse:
        if use_cache:
            cached = self._load_cache(query)
            if cached is not None:
                return cached
        fetcher = self.fetcher
        if fetcher is None:
            if self.offline:
                raise OEISUnavailable(
                    "OEIS network access is disabled and no cache entry exists; "
                    "inject a fetcher or run with offline=False and network access"
                )
            fetcher = _requests_fetcher
        self._throttle()
        url = f"{OEIS_JSON_ENDPOINT}?{query}"
        try:
            text = fetcher(url)
        except Exception as exc:
            raise OEISUnavailable(f"OEIS request failed: {exc}") from exc
        if not isinstance(text, str):
            raise OEISUnavailable("OEIS fetcher returned non-text content")
        raw = self._parse_response(text)
        resp = OEISResponse(
            query=query, raw=raw, retrieved_at=_now(), content_hash=sha256_hex(text),
        )
        self._store_cache(resp, text)
        return resp


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key {key!r}")
        result[key] = value
    return result


def _require_oeis_https_url(url: str) -> None:
    try:
        parsed = urlsplit(url)
    except (TypeError, ValueError) as exc:
        raise OEISUnavailable("OEIS URL is malformed") from exc
    if (
        parsed.scheme.lower() != "https"
        or parsed.hostname not in _OEIS_HOSTS
        or parsed.username is not None
        or parsed.password is not None
    ):
        raise OEISUnavailable(
            "OEIS URL must use HTTPS on the canonical OEIS host without credentials"
        )


def _requests_fetcher(url: str) -> str:  # pragma: no cover - live network
    import requests

    _require_oeis_https_url(url)
    current_url = url
    for redirect_count in range(_MAX_HTTP_REDIRECTS + 1):
        response = requests.get(
            current_url,
            timeout=30,
            headers={"User-Agent": "egmra-research/0.1"},
            stream=True,
            allow_redirects=False,
        )
        try:
            final_url = getattr(response, "url", None)
            if not isinstance(final_url, str):
                raise OEISUnavailable("OEIS final response URL is unavailable")
            _require_oeis_https_url(final_url)
            if response.status_code in _REDIRECT_STATUS_CODES:
                if redirect_count >= _MAX_HTTP_REDIRECTS:
                    raise OEISUnavailable("OEIS redirect limit exceeded")
                location = response.headers.get("Location")
                if not isinstance(location, str) or not location.strip():
                    raise OEISUnavailable("OEIS redirect target is unavailable")
                next_url = urljoin(current_url, location)
                _require_oeis_https_url(next_url)
                current_url = next_url
                continue

            response.raise_for_status()
            content_length = response.headers.get("Content-Length")
            if content_length is not None:
                try:
                    announced_size = int(content_length)
                except (TypeError, ValueError):
                    announced_size = None
                if announced_size is not None and (
                    announced_size < 0
                    or announced_size > _MAX_HTTP_RESPONSE_BYTES
                ):
                    raise OEISUnavailable("OEIS response exceeds size limit")

            payload = bytearray()
            for chunk in response.iter_content(
                chunk_size=min(64 * 1024, _MAX_HTTP_RESPONSE_BYTES + 1)
            ):
                if not chunk:
                    continue
                if not isinstance(chunk, (bytes, bytearray)):
                    raise OEISUnavailable("OEIS response yielded non-byte content")
                payload.extend(chunk)
                if len(payload) > _MAX_HTTP_RESPONSE_BYTES:
                    raise OEISUnavailable("OEIS response exceeds size limit")
            try:
                return bytes(payload).decode("utf-8")
            except UnicodeDecodeError as exc:
                raise OEISUnavailable("OEIS response is not valid UTF-8") from exc
        finally:
            response.close()
    raise OEISUnavailable("OEIS redirect limit exceeded")


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
