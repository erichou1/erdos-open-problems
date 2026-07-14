"""Production scholarly / theorem-library retrieval (spec §6.4; audit #7).

The packaged Erdős snapshot gives auditable provenance for the *problem corpus*;
this module adds *live scholarly* retrieval so the frozen solver packet can also
carry real, versioned, content-hashed literature (arXiv, Crossref today; the
:class:`ScholarlyRetriever` seam makes Semantic Scholar / MathOverflow / a
citation graph pluggable). Every hit becomes an auditable :class:`TheoremRecord`
with a source URI, a stable version, a content hash, and a verbatim extract.

Trust boundary (unchanged): a retrieved paper seeds hypotheses and search queries
only — it is ``proof_status="unknown"`` and ``independent_verification_status=
"unverified"`` and can NEVER establish proof status (the ImportAuditor enforces
this downstream). Network access is confined to an allowlisted host set behind an
injectable fetcher, so parsing/record construction is fully tested offline and the
live fetch is a thin, documented seam.
"""

from __future__ import annotations

import json
import re
import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import Callable, Protocol
from urllib.parse import urlencode, urlparse

from egmra.provenance.hashing import sha256_hex
from egmra.retrieval.records import TheoremRecord

# Live fetches are confined to these hosts (no user-supplied URLs are ever fetched).
_ALLOWED_HOSTS = frozenset({"export.arxiv.org", "api.crossref.org"})
_ARXIV_NS = "{http://www.w3.org/2005/Atom}"
_MAX_RESULTS = 25
_JATS_TAG = re.compile(r"<[^>]+>")
_WS = re.compile(r"\s+")

Fetcher = Callable[[str], str]


class ScholarlyRetrievalError(RuntimeError):
    """A scholarly source was unavailable or returned unusable data."""


class ScholarlyRetriever(Protocol):
    """Search one scholarly source, returning auditable TheoremRecords."""

    source_id: str

    def search(self, query: str, *, limit: int = 5) -> list[TheoremRecord]:
        ...


def _clip_results(limit: int) -> int:
    return max(1, min(int(limit), _MAX_RESULTS))


def _normalize(text: str) -> str:
    return _WS.sub(" ", (text or "").replace("\n", " ")).strip()


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


@dataclass
class ArxivRetriever:
    """arXiv export API (Atom XML; keyless). Abstract-level, never a proof."""

    fetcher: Fetcher
    source_id: str = "arxiv"

    def search(self, query: str, *, limit: int = 5) -> list[TheoremRecord]:
        url = "http://export.arxiv.org/api/query?" + urlencode({
            "search_query": f"all:{_normalize(query)[:400]}",
            "start": 0, "max_results": _clip_results(limit),
        })
        return parse_arxiv_atom(self.fetcher(url), retrieved_at=_now())


@dataclass
class CrossrefRetriever:
    """Crossref works API (JSON; keyless). Bibliographic metadata, never a proof."""

    fetcher: Fetcher
    source_id: str = "crossref"

    def search(self, query: str, *, limit: int = 5) -> list[TheoremRecord]:
        url = "https://api.crossref.org/works?" + urlencode({
            "query": _normalize(query)[:400], "rows": _clip_results(limit),
        })
        return parse_crossref_json(self.fetcher(url), retrieved_at=_now())


def parse_arxiv_atom(text: str, *, retrieved_at: str = "") -> list[TheoremRecord]:
    """Parse an arXiv Atom feed into auditable TheoremRecords (entities disabled)."""
    if "<!DOCTYPE" in text or "<!ENTITY" in text:
        # Refuse DTDs/entity definitions (billion-laughs / external-entity vectors).
        raise ScholarlyRetrievalError("arXiv response contains a forbidden DTD/entity")
    try:
        root = ET.fromstring(text)
    except ET.ParseError as exc:
        raise ScholarlyRetrievalError(f"arXiv response is not valid XML: {exc}") from exc
    records: list[TheoremRecord] = []
    for entry in root.findall(f"{_ARXIV_NS}entry"):
        id_url = _normalize((entry.findtext(f"{_ARXIV_NS}id") or ""))
        title = _normalize(entry.findtext(f"{_ARXIV_NS}title") or "")
        summary = _normalize(entry.findtext(f"{_ARXIV_NS}summary") or "")
        published = _normalize(entry.findtext(f"{_ARXIV_NS}published") or "")
        if not (id_url and title):
            continue
        arxiv_id = id_url.rsplit("/abs/", 1)[-1] or id_url
        authors = tuple(
            _normalize(name.text or "")
            for name in entry.findall(f"{_ARXIV_NS}author/{_ARXIV_NS}name")
            if _normalize(name.text or "")
        )
        extract = f"{title}\n\n{summary}".strip()
        records.append(TheoremRecord(
            theorem_id=f"arxiv:{arxiv_id}",
            canonical_statement=title,
            conclusion=title,
            source_uri=id_url,
            source_version=published or arxiv_id,
            source_content_hash=sha256_hex(f"{title}\n{summary}"),
            verbatim_theorem_and_hypothesis_extract=extract,
            extraction_method="arxiv_api",
            extraction_confidence=0.5,  # an abstract, not a verbatim theorem statement
            retrieved_at=retrieved_at,
            authors=authors,
            date=published,
            proof_status="unknown",
            independent_verification_status="unverified",
            license="arXiv (see arxiv.org/help/license)",
        ))
    return records


def parse_crossref_json(text: str, *, retrieved_at: str = "") -> list[TheoremRecord]:
    """Parse a Crossref works response into auditable TheoremRecords."""
    try:
        document = json.loads(text)
    except (json.JSONDecodeError, ValueError) as exc:
        raise ScholarlyRetrievalError(f"Crossref response is not valid JSON: {exc}") from exc
    items = (((document or {}).get("message") or {}).get("items")) or []
    if not isinstance(items, list):
        raise ScholarlyRetrievalError("Crossref message.items is not a list")
    records: list[TheoremRecord] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        doi = _normalize(str(item.get("DOI", "")))
        titles = item.get("title") if isinstance(item.get("title"), list) else []
        title = _normalize(str(titles[0])) if titles else ""
        if not (doi and title):
            continue
        raw_abstract = str(item.get("abstract", "") or "")
        abstract = _normalize(_JATS_TAG.sub(" ", raw_abstract))
        authors = tuple(
            _normalize(f"{a.get('given', '')} {a.get('family', '')}")
            for a in (item.get("author") or [])
            if isinstance(a, dict) and _normalize(f"{a.get('given', '')} {a.get('family', '')}")
        )
        issued = item.get("issued") if isinstance(item.get("issued"), dict) else {}
        parts = issued.get("date-parts") if isinstance(issued, dict) else None
        date = "-".join(str(p) for p in parts[0]) if isinstance(parts, list) and parts \
            and isinstance(parts[0], list) else ""
        source_uri = _normalize(str(item.get("URL", ""))) or f"https://doi.org/{doi}"
        extract = f"{title}\n\n{abstract}".strip()
        records.append(TheoremRecord(
            theorem_id=f"doi:{doi}",
            canonical_statement=title,
            conclusion=title,
            source_uri=source_uri,
            source_version=date or doi,
            source_content_hash=sha256_hex(f"{title}\n{raw_abstract}"),
            verbatim_theorem_and_hypothesis_extract=extract,
            extraction_method="crossref_api",
            extraction_confidence=0.4,  # bibliographic metadata, not a theorem extract
            retrieved_at=retrieved_at,
            authors=authors,
            date=date,
            proof_status="unknown",
            independent_verification_status="unverified",
            license=_normalize(str(item.get("license", ""))) or "see publisher",
        ))
    return records


_RETRIEVERS: dict[str, type] = {
    "arxiv": ArxivRetriever,
    "crossref": CrossrefRetriever,
}

SCHOLARLY_SOURCES = tuple(_RETRIEVERS)


def build_scholarly_corpus(
    query: str, *, fetcher: Fetcher, sources: tuple[str, ...] = SCHOLARLY_SOURCES,
    limit: int = 5,
) -> list[TheoremRecord]:
    """Search the selected scholarly sources and merge auditable TheoremRecords.

    A per-source outage (network / bad payload) is skipped so other sources still
    contribute; the returned records only ever seed hypotheses and queries, never
    proof status. Returns an empty list (an honest empty packet) if no source
    yields a usable, auditable record.
    """
    if not query or not query.strip():
        return []
    records: list[TheoremRecord] = []
    seen: set[str] = set()
    for name in sources:
        retriever_cls = _RETRIEVERS.get(name)
        if retriever_cls is None:
            continue
        try:
            found = retriever_cls(fetcher=fetcher).search(query, limit=limit)
        except ScholarlyRetrievalError:
            continue  # a source outage is not fatal; never a mathematical failure
        for record in found:
            if record.theorem_id in seen or not record.is_auditable():
                continue
            seen.add(record.theorem_id)
            records.append(record)
    return records


class UrllibFetcher:  # pragma: no cover - performs live network I/O
    """A minimal live fetcher confined to the scholarly host allowlist.

    Never fetches a user-supplied URL: only URLs this module builds against
    ``export.arxiv.org`` / ``api.crossref.org`` are permitted. Enforces http(s)
    only, an allowlisted host, a timeout, and a response-size cap.
    """

    def __init__(self, *, timeout_s: float = 15.0, max_bytes: int = 4_000_000,
                 user_agent: str = "egmra-retrieval/1 (mailto:noreply@egmra.local)") -> None:
        self.timeout_s = float(timeout_s)
        self.max_bytes = int(max_bytes)
        self.user_agent = user_agent

    def __call__(self, url: str) -> str:
        import urllib.request

        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"} or parsed.hostname not in _ALLOWED_HOSTS:
            raise ScholarlyRetrievalError(f"refusing to fetch non-allowlisted URL: {url}")
        request = urllib.request.Request(url, headers={"User-Agent": self.user_agent})
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_s) as response:  # noqa: S310
                data = response.read(self.max_bytes + 1)
        except OSError as exc:
            raise ScholarlyRetrievalError(f"scholarly fetch failed: {exc}") from exc
        if len(data) > self.max_bytes:
            raise ScholarlyRetrievalError("scholarly response exceeded the size cap")
        return data.decode("utf-8", errors="replace")
