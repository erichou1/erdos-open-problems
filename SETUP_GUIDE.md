# Setup Guide

How to set up and run the Erdős solver pipeline on your own machine.

## 1. Requirements

- Python 3.9+
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

Submit a batch of problems (opens one chat per problem and sends the prompt):

```bash
python3 solve_submit.py --reverse --start 0 --limit 50
python3 deepseek_submit.py --reverse --start 0 --limit 50 --delay 60
```

Then collect answers and label each saved file `[solved]/[unsolved] + completeness`:

```bash
python3 solve_rename.py --watch --interval 60
python3 deepseek_rename.py --watch --interval 45
```

Solutions are written to:

- `solutions/<category>/` (ChatGPT)
- `solutions_deepseek/<category>/` (DeepSeek)

A second, human-named copy of every answer is also written to an `outputs/`
folder, named by verdict and completeness score:

- `outputs/chatgpt/<category>/Erdős #N [solved] 88%.md`
- `outputs/deepseek/<category>/Erdős #N [unsolved] 0%.md`

## 7. Resuming after the computer is closed

Progress is saved to disk continuously, so you can close the computer (or stop a
script) at any time and pick up where you left off:

- Submitted chats are recorded in the chat maps as they happen.
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
