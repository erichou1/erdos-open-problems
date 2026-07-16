# Starting the EGMRA Pipeline

Exact steps to start (or resume) the research pipeline on a machine that has
already completed one-time setup ([AGENT_SETUP.md](AGENT_SETUP.md)). Starting
is always a **resume**: shared campaign state, checkpoints, the exchange
cache, and dossiers carry all prior work forward — nothing is re-paid.

---

## Option A — the operator app (recommended)

1. Open **EGMRA Operator** (`~/Applications/EGMRA Operator.app` on macOS,
   Desktop/Start-Menu shortcut on Windows, application menu on Linux), or run
   the fallback in the checkout:

   ```bash
   .venv/bin/python -u operator_console.py        # opens http://127.0.0.1:8765/
   ```

2. Check the status cards. Every one of these must be ready before starting:

   | Card | Must show |
   | --- | --- |
   | Pipeline | Stopped |
   | Version | current |
   | Shared state | Driver + configuration ready |
   | Keys | Verified + provider configured |
   | ChatGPT | Profile present (login is human-verified) |
   | Lean + policy | Build + REPL + signature ready |

3. If **Version** says an update is available, click **Update + restart**
   (it stops cooperatively, fast-forwards, and resumes) — done, skip step 4.
4. Otherwise click **Run / resume pipeline** once.

The app refuses to start when prerequisites are missing, a campaign is
already running, or the same ChatGPT profile is in use — those refusals are
correct; fix the reported item instead of forcing.

## Option B — manual terminal launch

From the repository root (`erdos_problems/`):

```bash
# 1. Load private configuration into THIS shell only (never printed/committed)
set -a && . ./egmra.keys.sh && [[ -f .env ]] && . ./.env; set +a

# 2. Per-machine provider limits
export CHATGPT_PROFILE_DIR="$PWD/.chatgpt_profile"
export EGMRA_ARISTOTLE_MAX_CONCURRENT=3   # sum across machines sharing one key must be <= 5

# 3. Refuse a double start (one campaign per checkout / browser profile)
pgrep -f 'egmra.cli campaign' && { echo 'already running'; false; }

# 4. Launch (full literature/prize-ranked corpus, survives logout)
rm -f .egmra_operator/stop-request.json
nohup .venv/bin/python -u -m egmra.cli campaign \
  --campaign-id shared-current-v1 \
  --state-store postgres \
  --triage triage --triage-lane current --max-problems 0 \
  --derive-missing-intents \
  --provider browser --workers 3 --worker-rounds 4 --budget 100.0 \
  --reviews-dir reviews --targets-dir targets \
  --lemma-library egmra_lemma_library.jsonl \
  --formalizer aristotle --lean-project aristotle_lean_project \
  --lean-repair-rounds 2 \
  --lean-dev-repl "lake env $HOME/workspace/erdos/repl/.lake/build/bin/repl" \
  --hostile-review 2 --retrieval corpus --oeis offline --explore-blocked \
  --checkpoint-dir egmra_campaigns/ckpts-shared \
  --stop-file .egmra_operator/stop-request.json \
  --auto-rerank \
  --outcome-ledger "egmra_outcomes/shared-$(hostname -s).jsonl" \
  --policy egmra_campaigns/policy-promotion-v3-local.json \
  >> "/tmp/egmra_campaign_$(hostname -s).log" 2>&1 &
echo "campaign PID $!"
```

Adjust only these per machine:

- `--lean-dev-repl` — absolute path to this machine's built warm REPL
  (sibling `repl/` checkout, tag `v4.28.0`).
- `EGMRA_ARISTOTLE_MAX_CONCURRENT` — this machine's share of the 5-slot
  Aristotle account quota.
- `--workers` — 1–5 browser tabs (3 is the tested default for one account).

Never change on a joining machine: `--campaign-id`, `--triage-lane`,
`--state-store postgres`. A larger `--max-problems`/ranked set extends the
shared campaign in place; problems are never dropped.

## What startup does automatically

- **Resumes** the shared campaign; leases from dead processes expire (~15 min)
  and are reclaimed with fencing protection.
- **Requeues** every problem that failed only because the provider was down
  (`infrastructure_budget_exhausted`) — printed to stderr at launch.
- **Derives** an offline machine-signed intent certificate for any ranked
  problem missing one (marked provenance; lifts only interpretation
  ambiguity, never probes, reviews, or release gates).
- **Adopts** the compact current allocation on coordinated startup; leased and
  terminal work is preserved, stale pending work is retired, and the next
  lease follows the highest available literature/prize-aware rank.

## Verify it is running (about 2 minutes)

```bash
# process alive, workers leased
pgrep -f 'egmra.cli campaign'
tail -5 "/tmp/egmra_campaign_$(hostname -s).log"

# heartbeat fresh (< 60 s) and leases held by THIS pid
set -a && . ./egmra.keys.sh; set +a
.venv/bin/python - <<'PY'
import os, time
from egmra.orchestrator.campaign import Campaign, PostgresCampaignStore
c = Campaign('unused.json', worker_ids=('check:w0',),
             store=PostgresCampaignStore(os.environ['EGMRA_POSTGRES_DSN'],
                                         name='shared-current-v1'))
try:
    s = c.status(); now = time.time()
    print('by_status:', s['by_status'])
    for meta in s.get('machines', {}).values():
        print('machine pid', meta.get('process_id'),
              'heartbeat_age_s', round(now - meta.get('heartbeat_at', 0), 1))
finally:
    c.close()
PY
```

Then confirm <https://egmra-status.vercel.app> shows this computer as
**active** with a current version (the snapshot can lag ~1–2 minutes).

## Stopping

- **Operator app → Stop cleanly** (preferred), or manually:

  ```bash
  printf '{"requested_at": %s}\n' "$(date +%s)" > .egmra_operator/stop-request.json
  ```

  Workers finish their current problems, take no new leases, then exit.
  Never `kill -9`; a plain `kill <pid>` (SIGTERM) is the last resort and may
  cut an in-flight attempt (the lease expires and work replays from cache).

## Quick failure references

| Symptom | Meaning / action |
| --- | --- |
| `feature policy is unsigned` | Keys not loaded, or wrong shared `egmra.keys.sh`. |
| `campaign state already exists for a different campaign` | Wrong `--campaign-id`; align with the primary machine. |
| `Could not find ChatGPT input box` | Profile logged out or headless — use the app's **Open ChatGPT login**. |
| `Technical note: provider_unavailable` | One transient browser outage; auto-retried with backoff. No action. |
| `Lease stale — waiting to reassign` | A dead process held the lease; a free worker reclaims it automatically. |
| Aristotle `Connection to server was interrupted` | Transient; the fetch retries automatically (bounded). |
| Heartbeat frozen but log fresh | Laptop slept and dropped the DB link (pre-`cafa74a` builds only) — update and restart. |
| 0 completions for hours | Normal: hard problems take multi-hour multi-round attempts. Check exchange-cache writes under `egmra_campaigns/ckpts-shared/*/exchanges/` for live progress. |

Keep the machine on power with sleep disabled for unattended runs — sleep
pauses all local compute even though the database connection now recovers.
