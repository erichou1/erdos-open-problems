# Coordinated Literature-Ranking Rollout Design

**Date:** 2026-07-16  
**Status:** Approved for implementation planning

## Objective

Distribute one compact, auditable projection of the current literature- and
prize-aware allocation to every EGMRA worker and the public status site. A
coordinated worker restart adopts the new order without interrupting work that
was already leased. After restart, each worker leases the highest-ranked
available problem. The existing status daemon continues publishing worker
progress approximately once per minute.

## Current Constraints

- The complete `triage/rankings/current.json` artifact is approximately 42 MB
  because it contains every ranking family and complete audit metadata.
- The active `shared-current-v1` campaign was initialized before the new
  ranking and does not reread `current.json` while running.
- `--auto-rerank` adjusts pending work from recorded outcomes; it does not
  reload the corpus ranking.
- `--prefer-solvable` replaces the allocation order with the older
  formal/exact-computation formula.
- The website ranking page independently applies that older formula and
  therefore does not display the new allocation.
- Other worker machines receive only committed Git data, so a local generated
  ranking is not a reliable distribution mechanism.

## Architecture

### 1. Compact queue projection

Every successful ready ranking build emits
`triage/rankings/current_queue.json`. This artifact contains only the data
needed to distribute and explain the allocation:

- schema and projection-policy versions;
- allocation status and allocation-context identifier;
- source snapshot and complete-ranking content hashes;
- prize and literature policy versions;
- corpus-integrity summary;
- ordered allocation rows containing problem number, allocation rank, prize
  status, selection tier, literature coverage, base acquisition score,
  literature adjustment, final selection score, and selection reason;
- a canonical content hash covering the projection.

The projection is deterministically derived from the complete ranking. It is
small enough to commit and pull on every worker, but it does not replace the
complete local ranking artifact for auditing or the exact-hash legacy queue.

The projection validator recomputes its content hash, requires contiguous
ranks, rejects duplicate or malformed problem numbers, requires a ready and
complete source context, and verifies that every unpaid row precedes every
paid row. An invalid projection fails closed.

### 2. Coordinated campaign adoption

For the `current` triage lane, EGMRA reads the validated compact projection.
On process startup, the campaign atomically adopts the projection:

1. Preserve every existing assignment and its attempts, result, fencing token,
   lease, and terminal status.
2. Add any newly ranked problem as pending.
3. Mark an assignment missing from the new ranking as retired only when its
   status is pending or retained. A leased, completed, or failed assignment is
   never rewritten.
4. Store the ranked problems in projection order, followed by preserved
   historical assignments that are no longer ranked.
5. Lease skips retired assignments, so the next post-restart lease is the
   highest-ranked available current problem.

This adoption happens only during coordinated startup. No live process polls
or mutates its queue in the middle of a run. Existing leased work can finish
before the coordinated restart, as requested.

The operator command no longer appends `--prefer-solvable` for the `current`
lane. Explicit use on another single-objective lane remains supported. Outcome
driven `--auto-rerank` remains enabled and uses the adopted allocation as its
stable base order.

### 3. Public website ranking

`status_site/build_data.py` loads and validates the same compact queue. The
public `ranking` array follows allocation rank and joins current campaign
status/progress when available. A ranked problem not yet present in campaign
state still appears with queued/no-run progress and public statement metadata.
Historical campaign-only problems do not appear in the current ranking table.

The ranking page displays:

- allocation rank and problem number;
- current progress;
- unpaid or paid tier;
- literature coverage;
- base acquisition score;
- literature adjustment;
- final selection score.

The explanatory copy states that scores are transparent, uncalibrated search
preferences, not solution probabilities. It also states that paid problems are
deferred until eligible unpaid problems are exhausted.

The existing `status_site/live_refresh.py` remains the publication mechanism.
It rebuilds credential-free site data and force-with-lease updates only the
dedicated `status-live` branch. The main implementation branch is pushed
normally after tests pass.

## Data Flow

1. `erdos_searcher.py` builds and validates the complete ranking.
2. The searcher writes the compact, self-hashed queue projection atomically.
3. The implementation branch commits that projection with the consumer code.
4. Each machine pulls the same commit.
5. A coordinated restart validates the projection and adopts its order in the
   shared Postgres campaign.
6. Workers atomically lease the highest-ranked available problem.
7. Worker heartbeats and outcomes enter the existing shared state.
8. The status daemon joins that state to the compact ranking and publishes the
   website snapshot every minute.

## Failure Handling

- Missing, oversized, malformed, non-ready, or hash-invalid projections are
  refused before campaign mutation.
- Unknown prize status or a paid-before-unpaid boundary is refused.
- Campaign adoption is one locked store transaction; partial adoption cannot
  be observed.
- Active leases and terminal assignments are immutable during adoption.
- A site projection error prevents publication and leaves the last valid
  `status-live` snapshot available.
- A Git push failure leaves local commits intact and is reported; it never
  changes campaign state.

## Testing and Verification

- Unit tests for deterministic projection creation, content-hash verification,
  tier boundaries, contiguous ranks, duplicate rejection, and tampering.
- Campaign-store tests proving adoption preserves leased and terminal work,
  retires only stale pending work, adds new ranked work, and leases the highest
  available ranked problem next.
- CLI/operator tests proving `current` uses the projection and is not
  overridden by `--prefer-solvable` defaults.
- Website builder and frontend tests proving displayed order and fields match
  the compact projection.
- Integration test using the real generated projection and current shared
  ranking.
- Full repository test suite before push.
- After push, verify the remote branch commit and the live website snapshot.

## Rollout Boundary

Codex will implement, test, commit, push the active branch, update the local
status-site publication, and verify the remote artifacts. The user will perform
the coordinated restarts on the other worker machines. No live shared-campaign
reorder is performed before those restarts.
