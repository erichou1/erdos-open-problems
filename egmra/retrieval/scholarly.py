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
_ALLOWED_HOSTS = frozenset({
    "export.arxiv.org", "api.crossref.org",
    "api.semanticscholar.org", "api.stackexchange.com",
})
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


@dataclass
class SemanticScholarRetriever:
    """Semantic Scholar graph API (JSON; keyless/rate-limited). Never a proof."""

    fetcher: Fetcher
    source_id: str = "semanticscholar"

    def search(self, query: str, *, limit: int = 5) -> list[TheoremRecord]:
        url = "https://api.semanticscholar.org/graph/v1/paper/search?" + urlencode({
            "query": _normalize(query)[:400], "limit": _clip_results(limit),
            "fields": "title,abstract,authors,year,url,externalIds",
        })
        return parse_semantic_scholar_json(self.fetcher(url), retrieved_at=_now())


@dataclass
class MathOverflowRetriever:
    """MathOverflow via the StackExchange API (JSON; keyless/low-quota). Never a proof."""

    fetcher: Fetcher
    source_id: str = "mathoverflow"

    def search(self, query: str, *, limit: int = 5) -> list[TheoremRecord]:
        url = "https://api.stackexchange.com/2.3/search/advanced?" + urlencode({
            "order": "desc", "sort": "relevance", "q": _normalize(query)[:400],
            "site": "mathoverflow", "pagesize": _clip_results(limit), "filter": "withbody",
        })
        return parse_mathoverflow_json(self.fetcher(url), retrieved_at=_now())


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


def _loads_object(text: str, source: str) -> dict:
    try:
        document = json.loads(text)
    except (json.JSONDecodeError, ValueError) as exc:
        raise ScholarlyRetrievalError(f"{source} response is not valid JSON: {exc}") from exc
    if not isinstance(document, dict):
        raise ScholarlyRetrievalError(f"{source} response must be a JSON object")
    return document


def parse_semantic_scholar_json(text: str, *, retrieved_at: str = "") -> list[TheoremRecord]:
    """Parse a Semantic Scholar paper-search response into auditable records."""
    document = _loads_object(text, "Semantic Scholar")
    items = document.get("data")
    if not isinstance(items, list):
        raise ScholarlyRetrievalError("Semantic Scholar 'data' is not a list")
    records: list[TheoremRecord] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        paper_id = _normalize(str(item.get("paperId", "")))
        title = _normalize(str(item.get("title", "") or ""))
        if not (paper_id and title):
            continue
        abstract = _normalize(str(item.get("abstract", "") or ""))
        authors = tuple(
            _normalize(str(a.get("name", "")))
            for a in (item.get("authors") or [])
            if isinstance(a, dict) and _normalize(str(a.get("name", "")))
        )
        year = _normalize(str(item.get("year", "") or ""))
        source_uri = _normalize(str(item.get("url", ""))) \
            or f"https://www.semanticscholar.org/paper/{paper_id}"
        extract = f"{title}\n\n{abstract}".strip()
        records.append(TheoremRecord(
            theorem_id=f"s2:{paper_id}",
            canonical_statement=title,
            conclusion=title,
            source_uri=source_uri,
            source_version=year or paper_id,
            source_content_hash=sha256_hex(f"{title}\n{abstract}"),
            verbatim_theorem_and_hypothesis_extract=extract,
            extraction_method="semantic_scholar_api",
            extraction_confidence=0.4,
            retrieved_at=retrieved_at,
            authors=authors,
            date=year,
            proof_status="unknown",
            independent_verification_status="unverified",
            license="see Semantic Scholar terms",
        ))
    return records


def parse_mathoverflow_json(text: str, *, retrieved_at: str = "") -> list[TheoremRecord]:
    """Parse a StackExchange (MathOverflow) search response into auditable records.

    A MathOverflow question is a *discussion*, not a theorem: it is recorded as
    unverified provenance that only seeds hypotheses/queries.
    """
    document = _loads_object(text, "MathOverflow")
    items = document.get("items")
    if not isinstance(items, list):
        raise ScholarlyRetrievalError("MathOverflow 'items' is not a list")
    records: list[TheoremRecord] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        question_id = _normalize(str(item.get("question_id", "")))
        title = _normalize(str(item.get("title", "") or ""))
        if not (question_id and title):
            continue
        body = _normalize(_JATS_TAG.sub(" ", str(item.get("body", "") or "")))
        owner = item.get("owner") if isinstance(item.get("owner"), dict) else {}
        author = _normalize(str(owner.get("display_name", "") or ""))
        created = _normalize(str(item.get("creation_date", "") or ""))
        source_uri = _normalize(str(item.get("link", ""))) \
            or f"https://mathoverflow.net/questions/{question_id}"
        extract = f"{title}\n\n{body}".strip()
        records.append(TheoremRecord(
            theorem_id=f"mathoverflow:{question_id}",
            canonical_statement=title,
            conclusion=title,
            source_uri=source_uri,
            source_version=created or question_id,
            source_content_hash=sha256_hex(f"{title}\n{body}"),
            verbatim_theorem_and_hypothesis_extract=extract,
            extraction_method="mathoverflow_api",
            extraction_confidence=0.3,  # a discussion thread, not a theorem statement
            retrieved_at=retrieved_at,
            authors=(author,) if author else (),
            date=created,
            proof_status="unknown",
            independent_verification_status="unverified",
            license="CC BY-SA (StackExchange)",
        ))
    return records


_RETRIEVERS: dict[str, type] = {
    "arxiv": ArxivRetriever,
    "crossref": CrossrefRetriever,
    "semanticscholar": SemanticScholarRetriever,
    "mathoverflow": MathOverflowRetriever,
}

SCHOLARLY_SOURCES = tuple(_RETRIEVERS)


@dataclass(frozen=True)
class ScholarlySearchResult:
    records: tuple[TheoremRecord, ...]
    coverage: dict[str, str]


def search_scholarly_sources(
    query: str, *, fetcher: Fetcher, sources: tuple[str, ...] = SCHOLARLY_SOURCES,
    limit: int = 5,
) -> ScholarlySearchResult:
    """Search the selected scholarly sources and merge auditable TheoremRecords.

    A per-source outage (network / bad payload) is skipped so other sources still
    contribute; the returned records only ever seed hypotheses and queries, never
    proof status. Returns an empty list (an honest empty packet) if no source
    yields a usable, auditable record.
    """
    if not query or not query.strip():
        return ScholarlySearchResult(
            (), {name: "not_queried" for name in sources}
        )
    records: list[TheoremRecord] = []
    coverage: dict[str, str] = {}
    seen: set[str] = set()
    for name in sources:
        retriever_cls = _RETRIEVERS.get(name)
        if retriever_cls is None:
            coverage[name] = "unsupported"
            continue
        try:
            found = retriever_cls(fetcher=fetcher).search(query, limit=limit)
        except ScholarlyRetrievalError:
            coverage[name] = "unavailable"
            continue  # a source outage is not fatal; never a mathematical failure
        coverage[name] = "complete"
        for record in found:
            if record.theorem_id in seen or not record.is_auditable():
                continue
            seen.add(record.theorem_id)
            records.append(record)
    return ScholarlySearchResult(tuple(records), coverage)


def build_scholarly_corpus(
    query: str, *, fetcher: Fetcher, sources: tuple[str, ...] = SCHOLARLY_SOURCES,
    limit: int = 5,
) -> list[TheoremRecord]:
    """Compatibility wrapper returning only auditable records."""
    return list(search_scholarly_sources(
        query, fetcher=fetcher, sources=sources, limit=limit
    ).records)


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
        # The StackExchange (MathOverflow) API always gzips its responses.
        if data[:2] == b"\x1f\x8b":
            import gzip

            try:
                data = gzip.decompress(data)
            except OSError as exc:
                raise ScholarlyRetrievalError(f"could not gunzip response: {exc}") from exc
            if len(data) > self.max_bytes:
                raise ScholarlyRetrievalError("decompressed response exceeded the size cap")
        return data.decode("utf-8", errors="replace")
