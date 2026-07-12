# Setup Guide

How to set up and run the Erdős solver pipeline on your own machine.

## 1. Requirements

- Python 3.10+
- A ChatGPT account (and optionally a DeepSeek account)

## 2. Install

```bash
git clone https://github.com/erichou1/erdos-open-problems.git
cd erdos-open-problems

# (recommended) create a virtual environment
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# install Python dependencies
pip install -r requirements.txt

# install the Chromium browser used by Playwright
playwright install chromium
```

## 3. Configure your ChatGPT Project URL

The pipeline opens new chats inside a ChatGPT Project. The URL is read from a
local `.env` file (which is never committed).

```bash
cp .env.example .env
```

Then edit `.env` and set your own project URL:

```
CHATGPT_PROJECT_URL=https://chatgpt.com/g/g-p-<your-project-id>/project
```

To find it: open your project in ChatGPT and copy the URL from the address bar.
If you leave it unset, chats are created at plain `https://chatgpt.com`.

## 4. Log in (one time)

This opens a real browser window so you can sign in. Your session is saved in a
local profile folder (git-ignored), so you only do this once.

```bash
python3 solve_submit.py --login
python3 deepseek_submit.py --login      # optional, for DeepSeek
```

## 5. (Optional) Fetch the problem set

The problems are already included in the repository. To re-download them:

```bash
python3 fetch_erdos.py
python3 fetch_categories.py
```

## 6. Run the pipeline

Submission is fail-closed on a complete canonical source snapshot. The
repository includes the audited snapshot; to refresh it, resolve and verify a
new commit-pinned upstream catalog plus every source page with:

```bash
python3 erdos_ingest.py --canonical
```

Submit a batch of problems (opens one chat per problem and sends the prompt):

```bash
python3 solve_submit.py --reverse --start 0 --limit 50
python3 deepseek_submit.py --reverse --start 0 --limit 50 --delay 60
```

Then collect answers and label each saved file with a candidate outcome and completeness:

```bash
python3 solve_rename.py --watch --interval 60
python3 deepseek_rename.py --watch --interval 45
```

Solutions are written to:

- `solutions/<category>/` (ChatGPT)
- `solutions_deepseek/<category>/` (DeepSeek)

A second, human-named copy of every answer is also written to an `outputs/`
folder, named by verdict and completeness score:

- `outputs/chatgpt/<category>/Erdős #N [candidate-proved] 88%.md`
- `outputs/deepseek/<category>/Erdős #N [resource-exhausted] 0%.md`

These labels are not verified solutions. The multi-context workflow in
`proof_pipeline.py` must pass `verification.evaluate_gate` before a result can
be recorded as `verified_proved` or `verified_disproved`. The gate requires a
hashed formal-proof, exact-computation, or expert-review artifact in addition to
unanimous independent model review:

```bash
python3 run_verified_pipeline.py --problem 137 --print-statement-sha \
  --model-id <exact-model-id>
cp verification-evidence.example.json verification-evidence.json
python3 run_verified_pipeline.py --problem 137 --model-id <exact-model-id>
# Review the saved candidate, then fill in its hashes, verifier, outcome,
# and local artifact path.
python3 promote_verified_run.py \
  --run-dir proof_runs/problem_137/<run-id> \
  --evidence-json verification-evidence.json --publish
```

The legacy collectors use canonical theorem text only and label their private
chat metadata `UNVERIFIED_CANDIDATE`; an old URL-only entry is resubmitted
because it cannot prove which statement was sent. Provider throttles wait and
retry adaptively without consuming a mathematical attempt, with a hard
120-second maximum for backoff, request spacing, and legacy round delays.

## 7. Resuming after the computer is closed

Progress is saved to disk continuously, so you can close the computer (or stop a
script) at any time and pick up where you left off:

- Submitted chats and their exact source/prompt contracts are recorded in the
  private chat maps as they happen.
- Each answer is written to disk the moment it is collected.

Just re-run the same commands. Already-submitted problems and already-saved
answers are skipped automatically, and the `outputs/` copies are rebuilt from
the saved solutions if they are missing. The `--watch` collectors also
re-open the browser by themselves if the window is closed.

## 8. Privacy

These files stay local and are git-ignored:

- `.env` — your project URL
- `.chatgpt_profile/`, `.deepseek_profile/` — browser sessions / cookies
- `.chatgpt_chat_map.json`, `.deepseek_chat_map.json` — conversation IDs
- `*.log`

See `SETUP_GUIDE.pdf` for a printable copy of this guide.
