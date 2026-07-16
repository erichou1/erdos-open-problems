# Coordinated Literature-Ranking Rollout Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish one compact, integrity-checked literature/prize allocation that coordinated EGMRA restarts and the public website both consume.

**Architecture:** A new `ranking_queue.py` module owns deterministic queue projection and validation. The searcher emits that projection, campaign startup atomically adopts it without touching active or terminal work, and the status publisher renders the same order and fields. The compact projection is committed and pushed; the complete 42 MB audit artifact remains local.

**Tech Stack:** Python 3.12+, pytest, signed EGMRA campaign stores, static HTML/JavaScript, Git, GitHub, Vercel status feed.

## Global Constraints

- Do not mutate the live shared campaign before coordinated restarts.
- Preserve all leased, completed, and failed assignments during adoption.
- Retire only pending or retained assignments absent from the current ranking.
- Reject malformed, non-ready, hash-invalid, incomplete, duplicate, non-contiguous, unknown-prize, or paid-before-unpaid projections.
- The `current` lane must not be overridden by the older `--prefer-solvable` operator default.
- Keep complete ranking artifacts and existing user-owned `triage/` changes out of implementation commits except for the compact queue projection.
- The public site must describe ranking scores as uncalibrated search preferences, never solution probabilities.
- Push the implementation branch only after the full test suite passes.

---

### Task 1: Compact queue projection boundary

**Files:**
- Create: `ranking_queue.py`
- Create: `tests/test_ranking_queue.py`

**Interfaces:**
- Consumes: a complete ranking `dict` with `allocation_queue`, policy versions, source identity, integrity, and `ranking_content_sha256`.
- Produces: `build_queue_projection(ranking: dict) -> dict`, `validate_queue_projection(document: object) -> dict`, `load_queue_projection(path: Path) -> dict`, and `write_queue_projection(path: Path, ranking: dict) -> dict`.

- [ ] **Step 1: Write failing projection tests**

Add fixtures with two unpaid rows followed by one paid row and tests that require deterministic output, canonical SHA-256 verification, contiguous allocation ranks, unique positive problem numbers, complete corpus integrity, known prize states, and the unpaid-before-paid boundary. Include tampering tests for a changed problem number, reordered rows, an unknown prize, and a paid row before an unpaid row.

```python
def test_projection_round_trip_is_hash_bound(tmp_path):
    projection = build_queue_projection(_ranking())
    path = tmp_path / "current_queue.json"
    path.write_text(json.dumps(projection), encoding="utf-8")
    assert load_queue_projection(path) == projection
    projection["allocation_queue"][0]["problem_number"] = 999
    with pytest.raises(QueueProjectionError, match="content hash"):
        validate_queue_projection(projection)


def test_projection_rejects_paid_before_unpaid():
    ranking = _ranking()
    ranking["allocation_queue"] = [
        ranking["allocation_queue"][2], ranking["allocation_queue"][0]
    ]
    ranking["allocation_queue"][0]["allocation_rank"] = 1
    ranking["allocation_queue"][1]["allocation_rank"] = 2
    with pytest.raises(QueueProjectionError, match="unpaid"):
        build_queue_projection(ranking)
```

- [ ] **Step 2: Run the tests and verify RED**

Run: `/tmp/erdos-ranking-venv/bin/python -m pytest tests/test_ranking_queue.py -q`

Expected: collection fails because `ranking_queue` does not exist.

- [ ] **Step 3: Implement projection creation, validation, and atomic writing**

Create constants and the exact public row allowlist:

```python
QUEUE_PROJECTION_SCHEMA_VERSION = 1
QUEUE_PROJECTION_POLICY_VERSION = "queue-projection-v1"
QUEUE_FILENAME = "current_queue.json"
ROW_FIELDS = (
    "problem_id", "problem_number", "allocation_rank", "allocation_lane",
    "prize", "prize_status", "selection_priority_tier",
    "literature_coverage_status", "base_acquisition_score",
    "literature_adjustment", "selection_score", "reason_selected",
)
```

`projection_content_sha256` hashes canonical JSON after removing only
`projection_content_sha256`. `validate_queue_projection` returns a normalized
deep copy and raises `QueueProjectionError`. `write_queue_projection` writes a
temporary sibling, fsyncs it, and replaces the target atomically.

The projection top level contains:

```python
{
    "schema_version": QUEUE_PROJECTION_SCHEMA_VERSION,
    "projection_policy_version": QUEUE_PROJECTION_POLICY_VERSION,
    "allocation_status": ranking["allocation_status"],
    "allocation_context_id": ranking["allocation_context_id"],
    "ranking_content_sha256": ranking["ranking_content_sha256"],
    "source_snapshot_id": ranking["source_snapshot_id"],
    "source_snapshot_sha256": ranking["source_snapshot_sha256"],
    "prize_policy_version": ranking["prize_policy_version"],
    "literature_policy_version": ranking["literature_policy_version"],
    "literature_model_version": ranking["literature_model_version"],
    "literature_coverage": ranking["literature_coverage"],
    "corpus_integrity": ranking["corpus_integrity"],
    "attempt_exclusions": ranking["attempt_exclusions"],
    "allocation_queue": projected_rows,
}
```

- [ ] **Step 4: Run projection tests and verify GREEN**

Run: `/tmp/erdos-ranking-venv/bin/python -m pytest tests/test_ranking_queue.py -q`

Expected: all projection tests pass.

- [ ] **Step 5: Commit the projection boundary**

```bash
git add ranking_queue.py tests/test_ranking_queue.py
git commit -m "feat: publish compact ranked queue projection"
```

---

### Task 2: Searcher emission and EGMRA projection consumption

**Files:**
- Modify: `erdos_searcher.py`
- Modify: `egmra/orchestrator/triage_source.py`
- Modify: `tests/test_erdos_searcher.py`
- Modify: `egmra/tests/test_triage_source.py`

**Interfaces:**
- Consumes: Task 1 `write_queue_projection` and `load_queue_projection`.
- Produces: every ready searcher build writes `rankings/current_queue.json`; `triage_ranked_problem_ids(triage_dir: Path, *, lane: str = "current", limit: int | None = None) -> list[str]` reads that projection.

- [ ] **Step 1: Write failing searcher and triage-reader tests**

Add a searcher assertion that the output projection exists and matches the
complete ranking hash. Update triage-source tests to write a valid compact
projection and assert the `current` lane uses it even when a conflicting
`current.json` exists.

```python
queue = load_queue_projection(output / "rankings" / "current_queue.json")
assert queue["ranking_content_sha256"] == ranking["ranking_content_sha256"]
assert [row["problem_number"] for row in queue["allocation_queue"]] == [
    row["problem_number"] for row in ranking["allocation_queue"]
]
```

- [ ] **Step 2: Run focused tests and verify RED**

Run: `/tmp/erdos-ranking-venv/bin/python -m pytest tests/test_erdos_searcher.py egmra/tests/test_triage_source.py -q`

Expected: projection-emission and projection-precedence assertions fail.

- [ ] **Step 3: Emit the projection only after the complete ranking hash exists**

Import `write_queue_projection` in `erdos_searcher.py`. After writing and
validating the immutable complete-ranking paths, call:

```python
write_queue_projection(
    output_root / "rankings" / QUEUE_FILENAME,
    rankings,
)
```

This ensures a withheld or failed build cannot replace the last ready queue.

- [ ] **Step 4: Make the EGMRA current lane require the compact projection**

In `triage_source.py`, use `load_queue_projection` for `current_queue.json`.
Non-current lanes continue reading their existing documents; their exclusions
come from the compact projection. Do not fall back to `current.json` for the
`current` lane, so missing rollout data fails closed.

- [ ] **Step 5: Run focused tests and verify GREEN**

Run: `/tmp/erdos-ranking-venv/bin/python -m pytest tests/test_ranking_queue.py tests/test_erdos_searcher.py egmra/tests/test_triage_source.py -q`

Expected: all focused tests pass.

- [ ] **Step 6: Commit searcher/consumer integration**

```bash
git add erdos_searcher.py egmra/orchestrator/triage_source.py tests/test_erdos_searcher.py egmra/tests/test_triage_source.py
git commit -m "feat: distribute one compact EGMRA ranking"
```

---

### Task 3: Atomic campaign adoption on coordinated restart

**Files:**
- Modify: `egmra/orchestrator/campaign.py`
- Modify: `egmra/cli.py`
- Modify: `egmra/tests/test_campaign_store.py`
- Modify: `egmra/tests/test_cli.py`

**Interfaces:**
- Consumes: ordered problem IDs returned by the validated compact projection.
- Produces: `Campaign.adopt_ranked_order(campaign_id: str, problem_ids: list[str]) -> list[str]`.

- [ ] **Step 1: Write failing adoption lifecycle tests**

Create an in-memory campaign with ranked problems 1, 2, 3 and stale problem 9.
Lease problem 1 and complete problem 2. Adopt the order `[3, 4, 1, 2]` and
assert:

```python
assert adopted == ["erdos-3", "erdos-4", "erdos-1", "erdos-2", "erdos-9"]
assert status["workers"]["erdos-1"]["status"] == "leased"
assert status["workers"]["erdos-2"]["status"] == "done"
assert status["workers"]["erdos-9"]["status"] == "retired"
assert campaign.lease("w1", now=2).problem_id == "erdos-3"
```

Add a test that a stale leased problem remains leased and a test that duplicate
ranked IDs fail before mutation. Add a CLI test proving triage startup invokes
adoption rather than growth-only initialization.

- [ ] **Step 2: Run campaign tests and verify RED**

Run: `/tmp/erdos-ranking-venv/bin/python -m pytest egmra/tests/test_campaign_store.py egmra/tests/test_cli.py -q`

Expected: `adopt_ranked_order` is absent and the CLI assertion fails.

- [ ] **Step 3: Implement one-transaction adoption**

Add `retired` to the terminal status set and assignment status documentation.
Within one `_locked()` block, `adopt_ranked_order`:

```python
ranked = list(problem_ids)
existing = self._read()
assignments = self._decode(existing)
for problem_id in ranked:
    assignments.setdefault(problem_id, Assignment(problem_id=problem_id))
for problem_id, assignment in assignments.items():
    if problem_id not in ranked and assignment.status in {"pending", "retained"}:
        assignment.status = "retired"
        assignment.worker_id = ""
        assignment.lease_expires_at = 0.0
        assignment.result_state = "retired_not_in_current_ranking"
historical = [pid for pid in existing["order"] if pid not in set(ranked)]
order = ranked + historical
self._write(self._encode(
    campaign_id, order, assignments,
    int(existing["fencing_counter"]), existing.get("machines"),
))
return order
```

For a new campaign, create exactly the ranked assignments. Reject campaign-ID
mismatch and duplicate IDs using the existing `CampaignError` contract.

- [ ] **Step 4: Wire coordinated adoption into triage startup**

In `egmra/cli.py`, call `campaign.adopt_ranked_order` when `--triage` is used;
keep `initialize` for explicit numeric ranges. Outcome-driven reranking remains
unchanged and receives the projection order as its stable input list.

- [ ] **Step 5: Run campaign/CLI tests and verify GREEN**

Run: `/tmp/erdos-ranking-venv/bin/python -m pytest egmra/tests/test_campaign_store.py egmra/tests/test_cli.py egmra/tests/test_rerank.py -q`

Expected: all tests pass.

- [ ] **Step 6: Commit coordinated adoption**

```bash
git add egmra/orchestrator/campaign.py egmra/cli.py egmra/tests/test_campaign_store.py egmra/tests/test_cli.py
git commit -m "feat: adopt ranked queue on coordinated restart"
```

---

### Task 4: Prevent the operator from overriding the current allocation

**Files:**
- Modify: `operator_console.py`
- Modify: `egmra/tests/test_operator_console.py`
- Modify: `START_PIPELINE.md`
- Modify: `AGENT_SETUP.md`

**Interfaces:**
- Consumes: operator config with `triage_lane` and legacy `prefer_solvable`.
- Produces: current-lane launch commands that preserve allocation order.

- [ ] **Step 1: Write a failing command-construction test**

```python
config = _load_config(tmp_path)
config["triage_lane"] = "current"
config["prefer_solvable"] = True
assert "--prefer-solvable" not in build_campaign_command(config, tmp_path)
config["triage_lane"] = "tractable_frontier"
assert "--prefer-solvable" in build_campaign_command(config, tmp_path)
```

- [ ] **Step 2: Run the operator test and verify RED**

Run: `/tmp/erdos-ranking-venv/bin/python -m pytest egmra/tests/test_operator_console.py -q`

Expected: the current-lane assertion fails.

- [ ] **Step 3: Preserve current allocation order in generated commands**

Change command construction to:

```python
if config.get("prefer_solvable", True) and config.get("triage_lane") != "current":
    command.append("--prefer-solvable")
```

Set the new default `prefer_solvable` to `False`. Update both launch documents
to remove `--prefer-solvable` from the `current` example and explain that the
current queue already includes exploitation, exploration, literature, and
prize policy.

- [ ] **Step 4: Run operator tests and verify GREEN**

Run: `/tmp/erdos-ranking-venv/bin/python -m pytest egmra/tests/test_operator_console.py -q`

Expected: all tests pass.

- [ ] **Step 5: Commit operator behavior**

```bash
git add operator_console.py egmra/tests/test_operator_console.py START_PIPELINE.md AGENT_SETUP.md
git commit -m "fix: preserve current allocation on worker restart"
```

---

### Task 5: Render the shared allocation on the public website

**Files:**
- Modify: `status_site/build_data.py`
- Modify: `status_site/ranking.js`
- Modify: `status_site/ranking.html`
- Modify: `status_site/styles.css`
- Modify: `egmra/tests/test_status_site_live_refresh.py`
- Create: `egmra/tests/test_status_site_ranking.py`

**Interfaces:**
- Consumes: Task 1 `load_queue_projection` and current campaign/public card data.
- Produces: `data.json["ranking"]` in exact allocation order and ranking UI fields matching the compact projection.

- [ ] **Step 1: Write failing status-data and static-client tests**

Test the pure `build_public_ranking(queue: dict, problems: list[dict[str, Any]], root: Path = ROOT) -> list[dict[str, Any]]` helper. Require that queue order `[8, 3, 5]` is preserved, campaign progress joins by
problem number, a missing campaign problem receives queued progress, and a
campaign-only stale problem is omitted. Static tests require the page copy to
mention unpaid-first policy and JavaScript to render `prize_status`,
`literature_coverage_status`, `base_acquisition_score`,
`literature_adjustment`, and `selection_score`.

```python
ranking = build_public_ranking(queue, campaign_problems, root=tmp_path)
assert [row["number"] for row in ranking] == [8, 3, 5]
assert ranking[0]["progress"] == campaign_problems_by_number[8]["progress"]
assert ranking[1]["progress"]["stage"] == "Queued"
assert all(row["number"] != 99 for row in ranking)
```

- [ ] **Step 2: Run website tests and verify RED**

Run: `/tmp/erdos-ranking-venv/bin/python -m pytest egmra/tests/test_status_site_ranking.py egmra/tests/test_status_site_live_refresh.py -q`

Expected: helper import and new-field assertions fail.

- [ ] **Step 3: Implement the ranking join**

Load `triage/rankings/current_queue.json` through `load_queue_projection`.
Build a `problem_number -> campaign problem` map, iterate only the projection
rows, and emit:

```python
{
    "problem_id": row["problem_id"],
    "number": row["problem_number"],
    "allocation_rank": row["allocation_rank"],
    "statement": public_statement,
    "status": campaign_problem.get("status", "pending"),
    "worker": campaign_problem.get("worker"),
    "progress": campaign_problem.get("progress", queued_progress),
    "prize": row["prize"],
    "prize_status": row["prize_status"],
    "literature_coverage_status": row["literature_coverage_status"],
    "base_acquisition_score": row["base_acquisition_score"],
    "literature_adjustment": row["literature_adjustment"],
    "selection_score": row["selection_score"],
    "reason_selected": row["reason_selected"],
}
```

Replace the old tractability `ranking_method` with the projection policy and
the unpaid-first, literature-adjusted explanation.

- [ ] **Step 4: Update ranking markup and client rendering**

Use columns Rank, Problem, Progress, Prize tier, Literature, Base score,
Literature adjustment, and Final score. Render signed adjustments with a
leading `+` for positive values. Keep the existing search, refresh, keyboard,
and MathJax behavior.

- [ ] **Step 5: Run website tests and verify GREEN**

Run: `/tmp/erdos-ranking-venv/bin/python -m pytest egmra/tests/test_status_site_ranking.py egmra/tests/test_status_site_live_refresh.py -q`

Expected: all website tests pass.

- [ ] **Step 6: Commit website integration**

```bash
git add status_site/build_data.py status_site/ranking.js status_site/ranking.html status_site/styles.css egmra/tests/test_status_site_live_refresh.py egmra/tests/test_status_site_ranking.py
git commit -m "feat: show live literature ranking on status site"
```

---

### Task 6: Generate, verify, commit, push, and publish

**Files:**
- Generate and commit: `triage/rankings/current_queue.json`
- Preserve without staging: all other pre-existing/generated `triage/` changes.

**Interfaces:**
- Consumes: the current ready complete ranking and all implementation from Tasks 1-5.
- Produces: a pushed implementation branch, a compact shared queue, and a verified live website snapshot.

- [ ] **Step 1: Regenerate the current queue from the complete ranking**

Run a short Python command that loads `triage/rankings/current.json`, calls
`write_queue_projection`, reloads it through `load_queue_projection`, and
prints row count, first paid rank, top 20 problem numbers, and projection hash.

Expected: 588 rows, first paid rank 535, and no validation error.

- [ ] **Step 2: Run real consumer integration checks**

Verify:

```python
ids = triage_ranked_problem_ids(Path("triage"), lane="current", limit=20)
assert ids == [f"erdos-{row['problem_number']}" for row in queue["allocation_queue"][:20]]
```

Build a credential-free site snapshot to a temporary path and assert its first
20 ranking numbers equal the projection's first 20.

- [ ] **Step 3: Run the full test suite**

Run: `/tmp/erdos-ranking-venv/bin/python -m pytest -q`

Expected: exit code 0 with only documented skips.

- [ ] **Step 4: Commit only the compact generated projection**

```bash
git add triage/rankings/current_queue.json
git commit -m "data: publish current literature-aware queue"
```

Inspect `git status --short` and confirm unrelated/generated user changes are
still unstaged.

- [ ] **Step 5: Push the active branch**

```bash
git push origin audit/egmra-independent-remediation-20260713
```

Expected: the remote branch advances to local `HEAD` without force.

- [ ] **Step 6: Publish and verify the live status snapshot**

Run the status refresher once using its existing private environment loader:

```bash
/tmp/erdos-ranking-venv/bin/python status_site/live_refresh.py --once
```

If the daemon lock correctly refuses a second publisher, wait for the running
daemon's next one-minute cycle instead. Fetch the remote `status-live`
`data.json` and assert its ranking top 20 equals the compact projection, its
ranking method names the literature/prize allocation, and its generation time
is current. Confirm `https://egmra-status.vercel.app/ranking.html` returns HTTP
200 and references the updated client asset version.

- [ ] **Step 7: Final repository and remote verification**

Confirm local `HEAD` equals the remote implementation ref, the compact queue
hash validates, no live campaign mutation occurred, and the active local
worker process remains untouched for the user's coordinated restart.
