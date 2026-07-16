"""Auditable literature opportunity signals for the Erdős problem ranker.

The records produced here affect selection order only.  They never establish
proof, novelty, theorem applicability, or source-authoritative resolution.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from egmra.retrieval.scholarly import (
    Fetcher,
    SCHOLARLY_SOURCES,
    UrllibFetcher,
    search_scholarly_sources,
)
from literature_research import LiteratureContext, LiteratureIndex


LITERATURE_POLICY_VERSION = "literature-ranking-v1"
LITERATURE_MODEL_VERSION = "literature-opportunity-v1"
LIVE_SHORTLIST_LIMIT = 50
LIVE_QUERY_LIMIT = 2
LIVE_RESULTS_PER_SOURCE = 5

PARTIAL_RESULT_RE = re.compile(
    r"\b(partial|special case|weaker|upper bound|lower bound|conditional|assuming)\b",
    re.IGNORECASE,
)
REUSE_RE = re.compile(
    r"\b(method|lemma|reduction|construction|formalization|algorithm)\b",
    re.IGNORECASE,
)
MACHINERY_RE = re.compile(
    r"\b(Riemann hypothesis|abc conjecture|Schanuel(?:'s)? conjecture|"
    r"Elliott-Halberstam conjecture|Bateman-Horn conjecture|"
    r"Generalized Riemann hypothesis)\b",
    re.IGNORECASE,
)
STATUS_RE = re.compile(
    r"\b(full solution|solved|settled|proof of (?:the|Erd(?:o|ő)s) problem|disproved)\b",
    re.IGNORECASE,
)
NEGATION_RE = re.compile(
    r"\b(no|not|unknown|unresolved|open|conjectured|claimed)\b",
    re.IGNORECASE,
)


def _canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class LiteratureQuery:
    text: str
    query_hash: str


@dataclass(frozen=True)
class LiteratureEnrichment:
    coverage_status: str
    local_artifact_hash: str
    live_artifact_hashes: tuple[str, ...]
    local_features: dict
    features: dict
    coverage_gaps: tuple[str, ...]
    supporting_snippets: tuple[dict, ...]
    queries: tuple[LiteratureQuery, ...]
    cache_reused_artifacts: int = 0
    live_requests: int = 0

    def to_dict(self) -> dict:
        return {
            "coverage_status": self.coverage_status,
            "local_artifact_hash": self.local_artifact_hash,
            "live_artifact_hashes": list(self.live_artifact_hashes),
            "local_features": self.local_features,
            "features": self.features,
            "coverage_gaps": list(self.coverage_gaps),
            "supporting_snippets": list(self.supporting_snippets),
            "queries": [
                {"text": query.text, "query_hash": query.query_hash}
                for query in self.queries
            ],
            "cache_reused_artifacts": self.cache_reused_artifacts,
            "live_requests": self.live_requests,
        }


def _sentences(values: Iterable[str]) -> list[str]:
    sentences: list[str] = []
    seen: set[str] = set()
    for value in values:
        for sentence in re.split(r"(?<=[.?!])\s+|[\r\n]+", str(value)):
            normalized = re.sub(r"\s+", " ", sentence).strip()
            if normalized and normalized not in seen:
                seen.add(normalized)
                sentences.append(normalized[:500])
    return sentences


def _matched_snippets(
    snippets: list[str], pattern: re.Pattern, label: str,
) -> list[dict]:
    matches: list[dict] = []
    for snippet in snippets:
        match = pattern.search(snippet)
        if match is None:
            continue
        prefix = snippet[max(0, match.start() - 40):match.start()]
        if NEGATION_RE.search(prefix):
            continue
        matches.append({"signal": label, "snippet": snippet})
        if len(matches) >= 5:
            break
    return matches


def _capped(count: int, cap: int) -> float:
    return round(min(1.0, count / cap), 6)


def aggregate_features(
    snippets: list[str], *, related_count: int, distinct_citations: int,
    ai_wiki: dict,
) -> dict:
    partial = _matched_snippets(snippets, PARTIAL_RESULT_RE, "partial_result")
    reuse = _matched_snippets(snippets, REUSE_RE, "reusable_method")
    machinery = _matched_snippets(snippets, MACHINERY_RE, "deep_machinery")
    status = _matched_snippets(snippets, STATUS_RE, "status_conflict")
    status_count = (
        len(status)
        + int(bool(ai_wiki.get("primary_full")))
        + int(bool(ai_wiki.get("secondary_full")))
    )
    return {
        "foothold": _capped(len(partial) + min(2, related_count), 6),
        "reuse": _capped(len(reuse) + min(2, distinct_citations), 6),
        "machinery_risk": _capped(len(machinery), 3),
        "status_risk": _capped(status_count, 2),
        "components": {
            "partial_result_snippets": partial,
            "reuse_snippets": reuse,
            "machinery_snippets": machinery,
            "status_snippets": status,
            "related_problem_count": related_count,
            "distinct_citation_count": distinct_citations,
            "ai_wiki_primary_full": bool(ai_wiki.get("primary_full")),
            "ai_wiki_secondary_full": bool(ai_wiki.get("secondary_full")),
        },
    }


def literature_adjustment(features: dict[str, float]) -> float:
    return round(
        0.02 * float(features["foothold"])
        + 0.01 * float(features["reuse"])
        - 0.02 * float(features["machinery_risk"]),
        6,
    )


def literature_status_tier(features: dict[str, float]) -> int:
    return int(float(features["status_risk"]) >= 0.5)


def _local_snippets(card: dict, context: LiteratureContext) -> list[str]:
    sections = card.get("metadata", {}).get("source_sections", {})
    values = [str(sections.get("remarks", ""))]
    for related in context.related:
        values.extend(related.results)
    return _sentences(values)


def build_queries(
    card: dict, local_context: LiteratureContext,
) -> tuple[LiteratureQuery, ...]:
    number = int(card["problem_number"])
    statement = re.sub(r"\s+", " ", card["statement"]["normalized"]).strip()
    tags = " ".join(str(tag) for tag in card.get("metadata", {}).get("tags", []))
    exact = f'Erdos problem {number} "{statement[:240]}" {tags}'.strip()
    query_texts = [exact]
    related_terms: list[str] = []
    for related in local_context.related[:3]:
        related_terms.extend(related.results[:1])
        related_terms.extend(related.shared_citations)
    if related_terms:
        surrounding = re.sub(r"\s+", " ", " ".join(related_terms)).strip()[:360]
        if surrounding and surrounding != exact:
            query_texts.append(surrounding)
    return tuple(
        LiteratureQuery(text=text, query_hash=sha256_text(text))
        for text in query_texts[:LIVE_QUERY_LIMIT]
    )


def build_local_enrichments(
    cards: list[dict], local_index: LiteratureIndex,
) -> dict[int, LiteratureEnrichment]:
    enrichments: dict[int, LiteratureEnrichment] = {}
    for card in cards:
        number = int(card["problem_number"])
        context = local_index.research(number)
        snippets = _local_snippets(card, context)
        features = aggregate_features(
            snippets,
            related_count=len(context.related),
            distinct_citations=len(context.references),
            ai_wiki=dict(card.get("metadata", {}).get("ai_wiki") or {}),
        )
        local_payload = {
            "literature_policy_version": LITERATURE_POLICY_VERSION,
            "literature_model_version": LITERATURE_MODEL_VERSION,
            "problem_number": number,
            "statement_sha256": card["statement"]["statement_sha256"],
            "context_sha256": context.sha256,
            "source_hashes": list(local_index.source_hashes(number)),
            "features": features,
            "supporting_snippets": snippets,
        }
        local_hash = sha256_text(_canonical_json(local_payload))
        supporting = tuple(
            feature
            for key in (
                "partial_result_snippets", "reuse_snippets",
                "machinery_snippets", "status_snippets",
            )
            for feature in features["components"][key]
        )
        enrichments[number] = LiteratureEnrichment(
            coverage_status="local_only",
            local_artifact_hash=local_hash,
            live_artifact_hashes=(),
            local_features=features,
            features=features,
            coverage_gaps=(),
            supporting_snippets=supporting,
            queries=build_queries(card, context),
        )
    return enrichments


def select_live_shortlist(preliminary_cards: list[dict]) -> tuple[int, ...]:
    return tuple(
        int(card["problem_number"])
        for card in preliminary_cards
        if card.get("metadata", {}).get("prize_status") == "unpaid"
    )[:LIVE_SHORTLIST_LIMIT]


def artifact_path(
    cache_root: Path, source_snapshot_id: str, problem_number: int,
    query_hash: str,
) -> Path:
    return (
        Path(cache_root) / source_snapshot_id / str(problem_number)
        / f"{query_hash}.json"
    )


def artifact_content_sha256(payload: dict) -> str:
    immutable = {
        key: value for key, value in payload.items()
        if key != "artifact_content_sha256"
    }
    return sha256_text(_canonical_json(immutable))


def compatible_artifact(
    payload: dict, *, problem_number: int, statement_sha256: str,
    source_snapshot_id: str, query_hash: str,
) -> bool:
    return (
        payload.get("schema_version") == 1
        and payload.get("literature_policy_version") == LITERATURE_POLICY_VERSION
        and payload.get("problem_number") == problem_number
        and payload.get("statement_sha256") == statement_sha256
        and payload.get("source_snapshot_id") == source_snapshot_id
        and payload.get("query_hash") == query_hash
        and payload.get("artifact_content_sha256") == artifact_content_sha256(payload)
    )


def _load_artifact(path: Path, **compatibility: object) -> dict | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if compatible_artifact(payload, **compatibility) else None


def _write_immutable_artifact(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    serialized = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    try:
        with path.open("x", encoding="utf-8") as handle:
            handle.write(serialized)
    except FileExistsError:
        try:
            existing = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise RuntimeError("immutable literature artifact conflict") from error
        if existing != payload:
            raise RuntimeError("immutable literature artifact conflict")


def _artifact_for_query(
    card: dict, query: LiteratureQuery, *, cache_root: Path,
    source_snapshot_id: str, refresh: bool, offline: bool,
    fetcher: Fetcher | None,
) -> tuple[dict | None, bool, int]:
    number = int(card["problem_number"])
    path = artifact_path(cache_root, source_snapshot_id, number, query.query_hash)
    compatibility = {
        "problem_number": number,
        "statement_sha256": card["statement"]["statement_sha256"],
        "source_snapshot_id": source_snapshot_id,
        "query_hash": query.query_hash,
    }
    cached = _load_artifact(path, **compatibility)
    if cached is not None:
        return cached, True, 0
    if offline or not refresh:
        return None, False, 0
    result = search_scholarly_sources(
        query.text,
        fetcher=fetcher or UrllibFetcher(),
        sources=SCHOLARLY_SOURCES,
        limit=LIVE_RESULTS_PER_SOURCE,
    )
    records = [record.to_dict() for record in result.records]
    live_snippets = _sentences(
        str(record["verbatim_theorem_and_hypothesis_extract"])
        for record in records
    )
    live_features = aggregate_features(
        live_snippets, related_count=0, distinct_citations=0, ai_wiki={}
    )
    supporting = [
        item
        for key in (
            "partial_result_snippets", "reuse_snippets",
            "machinery_snippets", "status_snippets",
        )
        for item in live_features["components"][key]
    ]
    payload = {
        "schema_version": 1,
        "literature_policy_version": LITERATURE_POLICY_VERSION,
        "literature_model_version": LITERATURE_MODEL_VERSION,
        "problem_number": number,
        "statement_sha256": card["statement"]["statement_sha256"],
        "source_snapshot_id": source_snapshot_id,
        "query": query.text,
        "query_hash": query.query_hash,
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "source_coverage": result.coverage,
        "records": records,
        "deduplication_identities": [record["theorem_id"] for record in records],
        "features": live_features,
        "supporting_snippets": supporting,
    }
    payload["artifact_content_sha256"] = artifact_content_sha256(payload)
    _write_immutable_artifact(path, payload)
    return payload, False, 1


def enrich_live_shortlist(
    cards_by_number: dict[int, dict],
    enrichments: dict[int, LiteratureEnrichment], *,
    shortlist_problem_numbers: tuple[int, ...], cache_root: Path,
    source_snapshot_id: str, refresh: bool, offline: bool,
    fetcher: Fetcher | None = None,
) -> dict[int, LiteratureEnrichment]:
    if refresh and offline:
        raise ValueError("refresh and offline literature modes are mutually exclusive")
    if len(shortlist_problem_numbers) > LIVE_SHORTLIST_LIMIT:
        raise ValueError("live literature shortlist exceeds policy limit")
    shortlist = set(shortlist_problem_numbers)
    output = dict(enrichments)
    for number, card in cards_by_number.items():
        base = enrichments[number]
        queries = base.queries
        live_artifacts: list[dict] = []
        reused = 0
        requests = 0
        for query in queries:
            allow_refresh = (
                number in shortlist
                and card.get("metadata", {}).get("prize_status") == "unpaid"
            )
            artifact, was_reused, request_count = _artifact_for_query(
                card, query, cache_root=cache_root,
                source_snapshot_id=source_snapshot_id,
                refresh=refresh and allow_refresh, offline=offline,
                fetcher=fetcher,
            )
            if artifact is not None:
                live_artifacts.append(artifact)
                reused += int(was_reused)
                requests += request_count
        if not live_artifacts:
            continue
        live_records: list[dict] = []
        seen_record_ids: set[str] = set()
        for artifact in live_artifacts:
            for record in artifact.get("records", []):
                identity = str(record.get("theorem_id", ""))
                if not identity or identity in seen_record_ids:
                    continue
                seen_record_ids.add(identity)
                live_records.append(record)
        live_snippets = [
            str(record["verbatim_theorem_and_hypothesis_extract"])
            for record in live_records
        ]
        local_components = base.local_features["components"]
        combined_features = aggregate_features(
            _sentences(
                [item["snippet"] for item in base.supporting_snippets]
                + live_snippets
            ),
            related_count=int(local_components["related_problem_count"]),
            distinct_citations=int(local_components["distinct_citation_count"]),
            ai_wiki={
                "primary_full": local_components["ai_wiki_primary_full"],
                "secondary_full": local_components["ai_wiki_secondary_full"],
            },
        )
        gaps = sorted({
            f"{source}:{status}"
            for artifact in live_artifacts
            for source, status in artifact.get("source_coverage", {}).items()
            if status != "complete"
        })
        status = "partial" if gaps else "live_complete"
        supporting = tuple(
            item
            for key in (
                "partial_result_snippets", "reuse_snippets",
                "machinery_snippets", "status_snippets",
            )
            for item in combined_features["components"][key]
        )
        output[number] = LiteratureEnrichment(
            coverage_status=status,
            local_artifact_hash=base.local_artifact_hash,
            live_artifact_hashes=tuple(
                artifact["artifact_content_sha256"] for artifact in live_artifacts
            ),
            local_features=base.local_features,
            features=combined_features,
            coverage_gaps=tuple(gaps),
            supporting_snippets=supporting,
            queries=base.queries,
            cache_reused_artifacts=reused,
            live_requests=requests,
        )
    return output


def literature_snapshot_sha256(
    enrichments: dict[int, LiteratureEnrichment],
    shortlist_problem_numbers: tuple[int, ...],
) -> str:
    payload = {
        "literature_policy_version": LITERATURE_POLICY_VERSION,
        "literature_model_version": LITERATURE_MODEL_VERSION,
        "live_shortlist_limit": LIVE_SHORTLIST_LIMIT,
        "weights": {"foothold": 0.02, "reuse": 0.01, "machinery_risk": -0.02},
        "shortlist_problem_numbers": list(shortlist_problem_numbers),
        "problems": {
            str(number): {
                "local_artifact_hash": value.local_artifact_hash,
                "live_artifact_hashes": list(value.live_artifact_hashes),
                "coverage_status": value.coverage_status,
                "features": value.features,
            }
            for number, value in sorted(enrichments.items())
        },
    }
    return sha256_text(_canonical_json(payload))


def literature_coverage_summary(
    enrichments: dict[int, LiteratureEnrichment],
) -> dict:
    statuses: dict[str, int] = {}
    for enrichment in enrichments.values():
        statuses[enrichment.coverage_status] = (
            statuses.get(enrichment.coverage_status, 0) + 1
        )
    return {
        "status_counts": dict(sorted(statuses.items())),
        "cache_reused_artifacts": sum(
            item.cache_reused_artifacts for item in enrichments.values()
        ),
        "live_requests": sum(item.live_requests for item in enrichments.values()),
        "source_failure_count": sum(
            len(item.coverage_gaps) for item in enrichments.values()
        ),
    }
