# EGMRA Agent Setup — Executable Runbook

**Audience: an AI coding agent** (Copilot/Claude/etc.) on a fresh macOS/Linux
machine. Follow the phases in order. Run the commands, verify each checkpoint,
and fix failures before moving on. A human is present — you MUST ask them for
the credentials in Phase 0 before anything else.

What you are setting up: EGMRA, a verification-first autonomous math research
pipeline over the Erdős problem catalog. One `egmra campaign` command runs the
whole pipeline: triage-ranked problem draining, browser ChatGPT workers,
multi-round research branches, Aristotle Lean formalization (5 concurrent
proofs), pinned-kernel verification, hostile review, release gates, outcome
ledger, continuous rerank, and durable checkpoints. Campaigns on DIFFERENT
computers coordinate through a shared Neon Postgres database so no two machines
ever work the same problem.

---

## Phase 0 — ASK THE USER (do this first, in one message)

Ask the user for these values. Do NOT guess, reuse examples, or proceed
without them. Never print the received values back, never commit them, and
never run them through shell `echo`.

1. **Aristotle API key** (`arstl_...`) — powers the Lean formalizer.
2. **ChatGPT workspace/project link** — the `https://chatgpt.com/g/g-p-...`
   project URL their account uses (a bare `https://chatgpt.com` also works but
   loses project scoping).
3. **Is this machine JOINING an existing multi-machine campaign?**
   - If YES: ask them to securely copy `egmra.keys.sh` from the primary
     machine into the repo root (it contains the shared signing keys and the
     Neon `EGMRA_POSTGRES_DSN`; identical `EGMRA_CHECKPOINT_KEY` on every
     machine is REQUIRED — the shared campaign state is HMAC-signed and
     mismatched keys fail closed). Then skip the key generation in Phase 2.
   - If NO (standalone): you will generate fresh signing keys in Phase 2, and
     campaigns will use the local file store instead of Postgres.

Sensitive-input rule: if you cannot receive secrets through your chat safely,
have the user paste them directly into `egmra.keys.sh` in an editor and just
tell you when done.

## Phase 1 — prerequisites, clone, dependencies

```bash
# Python >= 3.10 (macOS system python 3.9 is NOT enough)
brew install python@3.14 git || sudo apt-get install -y python3 python3-venv git

git clone https://github.com/erichou1/erdos-open-problems.git erdos_problems
cd erdos_problems
git checkout audit/egmra-independent-remediation-20260713

python3.14 -m venv .venv || python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/pip install -e ".[aristotle]"       # official aristotlelib SDK
.venv/bin/python -m playwright install chromium
```

**Checkpoint:** `.venv/bin/python -c "import egmra, aristotlelib, playwright; print('deps ok')"`

## Phase 2 — keys file (`egmra.keys.sh`, gitignored, mode 600)

Joining machines: the copied file from Phase 0 is complete — just
`chmod 600 egmra.keys.sh` and skip to the checkpoint.

Standalone: create the file. Insert the user's two values from Phase 0 and
generate the signing keys:

```bash
umask 077
{
  printf 'export ARISTOTLE_API_KEY="%s"\n'   "<PASTE-FROM-USER>"
  printf 'export CHATGPT_PROJECT_URL="%s"\n' "<PASTE-FROM-USER>"
  for k in EGMRA_EVENT_KEY EGMRA_POLICY_KEY EGMRA_EVIDENCE_KEY EGMRA_RELEASE_KEY \
           EGMRA_GATE_KEY EGMRA_PROMOTION_KEY EGMRA_LEAN_CHECKER_KEY \
           EGMRA_AUTHORITY_KEY EGMRA_TRUTH_SNAPSHOT_KEY EGMRA_CHECKPOINT_KEY \
           EGMRA_MODEL_ATTESTATION_KEY EGMRA_INTENT_REVIEW_KEY \
           EGMRA_FORMAL_CORRESPONDENCE_KEY EGMRA_LEGACY_REVIEW_KEY \
           EGMRA_LEGACY_EVIDENCE_KEY EGMRA_EXPERT_REVIEW_KEY; do
    printf 'export %s="%s"\n' "$k" "$(.venv/bin/python -c 'import secrets;print(secrets.token_hex(32))')"
  done
} >> egmra.keys.sh
chmod 600 egmra.keys.sh
```

**Checkpoint:** `source egmra.keys.sh && .venv/bin/python -c "import os; assert len(os.environ.get('EGMRA_CHECKPOINT_KEY',''))>=32 and os.environ.get('ARISTOTLE_API_KEY','').strip(); print('keys ok')"`

## Phase 3 — sign the feature policy (required; `egmra` refuses unsigned)

```bash
source egmra.keys.sh
mkdir -p egmra_campaigns
.venv/bin/python -m egmra.cli policy-sign \
  --input policy-template.json \
  --output egmra_campaigns/policy-local.json
```

## Phase 4 — pinned Lean toolchain (kernel verification)

```bash
curl -sSf https://elan.lean-lang.org/elan-init.sh | sh -s -- -y   # if lake missing
cd aristotle_lean_project && lake exe cache get && lake build && cd ..
```

Slow (~6.8 GB cache; minutes to hours). Run it in the background and continue
with Phase 5 meanwhile.

**Checkpoint:** `cd aristotle_lean_project && lake env lean --version && cd ..`

## Phase 5 — ChatGPT browser login (headed, one-time, human at keyboard)

Headless is blocked by Cloudflare — the profile MUST be created headed, by the
human:

```bash
source egmra.keys.sh
.venv/bin/python - << 'EOF'
from playwright.sync_api import sync_playwright
from pathlib import Path
with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(
        str(Path.cwd() / ".chatgpt_profile"), headless=False)
    page = ctx.new_page(); page.goto("https://chatgpt.com")
    input("Have the USER log in to ChatGPT in that window, then press Enter here...")
    ctx.close()
EOF
```

Tell the user to log in (including any 2FA), then continue. Each machine needs
its OWN ChatGPT account/profile — two machines sharing one account share one
rate limit and defeat the purpose.

## Phase 6 — verify before launching

```bash
source egmra.keys.sh
# 1. Full test suite (expect ~1300+ passed, exit 0):
.venv/bin/python -m pytest egmra/tests tests -p no:cacheprovider -q
# 2. Aristotle live round-trip (proves the key; takes a few minutes):
.venv/bin/python -m egmra.cli formalize --formalizer aristotle \
  --prompt "Prove that for all natural numbers n, n*n + n + 1 >= 1." \
  --lean-project aristotle_lean_project
# 3. If joining a shared campaign — Postgres reachability:
.venv/bin/python -c "
import os, psycopg; psycopg.connect(os.environ['EGMRA_POSTGRES_DSN']).close(); print('neon ok')"
```

Do not launch until #1 passes and #2 reports a sealed/kernel result.

## Phase 7 — launch the campaign (5 workers, full pipeline)

```bash
source egmra.keys.sh
HOST=$(hostname -s)
mkdir -p egmra_outcomes
nohup .venv/bin/python -m egmra.cli campaign \
  --campaign-id shared-current-v1 \
  --state-store postgres \
  --triage triage --triage-lane current --max-problems 25 \
  --provider browser --workers 5 --worker-rounds 4 --budget 100 \
  --policy egmra_campaigns/policy-local.json \
  --formalizer aristotle --lean-project aristotle_lean_project --lean-repair-rounds 2 \
  --hostile-review 2 --retrieval corpus --oeis offline --explore-blocked \
  --checkpoint-dir egmra_campaigns/ckpts-shared \
  --auto-rerank --refresh-ranking-after \
  --outcome-ledger "egmra_outcomes/shared-${HOST}.jsonl" \
  > "/tmp/egmra_campaign_${HOST}.log" 2>&1 &
echo "campaign PID $!"
```

- Joining machines MUST use the **same `--campaign-id`** — that (plus the
  shared keys) is what prevents two computers working the same problem. The
  shared state lives in Neon (`campaign_state` table; read-only status view
  `problem_status`).
- Standalone machines: drop `--state-store postgres`.
- `--workers 5` = 5 browser tabs + 5 per-worker Aristotle formalizers (the
  vendor's 5-concurrent-proof account budget is enforced process-wide).
  Honest note: one ChatGPT account throttle-serializes text generation, so 5
  tabs mainly help by overlapping generation with Lean/formalizer/review work.

## Phase 8 — monitor

```bash
tail -f /tmp/egmra_campaign_$(hostname -s).log        # live progress
wc -l egmra_outcomes/shared-$(hostname -s).jsonl      # recorded outcomes
ls egmra_campaigns/ckpts-shared/*/exchanges | wc -l   # cached exchanges
# Cross-machine status (shared campaigns): SELECT * FROM problem_status;
```

Troubleshooting quick refs:
- `PolicyError: feature policy is unsigned` → Phase 3 not done or keys not sourced.
- `Could not find ChatGPT input box` → profile not logged in or running headless → redo Phase 5.
- Browser rate-limit alerts → self-recovering (bounded pauses); persistent = account throttled, lower `--workers`.
- Campaign crash → relaunch the same command; leases resume, the exchange cache
  replays paid rounds, dossiers carry learning; a NEW `--campaign-id` starts fresh
  coordination (old one keeps its state).
- `campaign state already exists for a different campaign` → your `--campaign-id`
  or triage problem set differs from the shared one; align both with the primary machine.

## Hard rules for the agent

- NEVER commit `egmra.keys.sh`, `.env`, `.chatgpt_profile/`, or any credential.
- NEVER mark a problem solved/released yourself — only the pipeline's gates do that.
- A vendor "COMPLETE" or a model's claim is never a proof; only the pinned local
  kernel seal counts, and the pipeline enforces that without your help.
