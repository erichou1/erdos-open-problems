"""Materialized derived views: SQLite index + deterministic manifest (spec §10.3).

Derived views are disposable projections of the authoritative event log. The
manifest is a *materialized view*, not a mutable record that history overwrites
(spec §4.2, §16 P0.7).
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

from egmra.provenance.hashing import content_id
from egmra.truth.graph import EpistemicGraph


def materialize_sqlite(graph: EpistemicGraph, db_path: str | Path) -> Path:
    """Rebuild a SQLite index of claims / evidence / relations / branches.

    The index is fully derived from the graph (itself derived from events), so it
    can be dropped and rebuilt at any time.
    """
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        cur.executescript(
            """
            DROP TABLE IF EXISTS claims;
            DROP TABLE IF EXISTS evidence;
            DROP TABLE IF EXISTS relations;
            DROP TABLE IF EXISTS branches;
            DROP TABLE IF EXISTS dependencies;
            CREATE TABLE claims(
                claim_id TEXT PRIMARY KEY, interpretation_id TEXT,
                truth_status TEXT, lifecycle_status TEXT, scope TEXT,
                centrality REAL, semantic_risk REAL, status_version INTEGER);
            CREATE TABLE evidence(
                evidence_id TEXT PRIMARY KEY, kind TEXT, valid INTEGER,
                replay_result TEXT);
            CREATE TABLE relations(
                edge_id TEXT PRIMARY KEY, relation_type TEXT,
                source_id TEXT, target_id TEXT, lifecycle_status TEXT);
            CREATE TABLE branches(
                branch_id TEXT PRIMARY KEY, status TEXT, interpretation_id TEXT);
            CREATE TABLE dependencies(claim_id TEXT, depends_on TEXT);
            """
        )
        cur.executemany(
            "INSERT INTO claims VALUES (?,?,?,?,?,?,?,?)",
            [
                (c.claim_id, c.interpretation_id, str(c.truth_status),
                 str(c.lifecycle_status), c.scope, c.centrality, c.semantic_risk,
                 c.status_version)
                for c in graph.claims.values()
            ],
        )
        cur.executemany(
            "INSERT INTO evidence VALUES (?,?,?,?)",
            [(e.evidence_id, str(e.kind), int(e.valid), e.replay_result)
             for e in graph.evidence.values()],
        )
        cur.executemany(
            "INSERT INTO relations VALUES (?,?,?,?,?)",
            [(r.edge_id, str(r.relation_type), r.source_id, r.target_id,
              str(r.lifecycle_status)) for r in graph.relations.values()],
        )
        cur.executemany(
            "INSERT INTO branches VALUES (?,?,?)",
            [(b.branch_id, b.status, b.interpretation_id) for b in graph.branches.values()],
        )
        cur.executemany(
            "INSERT INTO dependencies VALUES (?,?)",
            [(c.claim_id, dep) for c in graph.claims.values() for dep in c.dependencies],
        )
        conn.commit()
    finally:
        conn.close()
    return db_path


def manifest_projection(graph: EpistemicGraph, *, problem_id: str = "") -> dict[str, Any]:
    """A deterministic manifest derived from the event log (never overwritten)."""
    claims = graph.claims
    manifest = {
        "projection_type": "egmra-manifest-v1",
        "problem_id": problem_id,
        "event_count": len(graph.log),
        "merkle_root": graph.log.merkle_root(),
        "claim_count": len(claims),
        "supported_claims": sorted(
            cid for cid, c in claims.items() if str(c.truth_status) == "SUPPORTED"
        ),
        "refuted_claims": sorted(
            cid for cid, c in claims.items() if str(c.truth_status) == "REFUTED"
        ),
        "conflicted_claims": sorted(
            cid for cid, c in claims.items() if str(c.truth_status) == "CONFLICTED"
        ),
        "actions_in_order": graph.log.actions_in_order(),
    }
    manifest["projection_hash"] = content_id(manifest)
    return manifest
