# Erdős Open Problems — Solver Pipeline

An automated pipeline that submits the open [Erdős problems](https://www.erdosproblems.com)
to ChatGPT and DeepSeek under a strict research-grade prompt, then collects and
labels the answers by verdict and completeness.

The repository ships with the full LaTeX problem set (622 open problems) plus
the automation scripts. It drives a real browser via Playwright, so it uses your
own ChatGPT / DeepSeek session — no API keys required.

## Quick start

```bash
git clone https://github.com/erichou1/erdos-open-problems.git
cd erdos-open-problems

python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium

cp .env.example .env          # optional: set your ChatGPT Project URL
python3 solve_submit.py --login

# submit a batch, then collect the answers
python3 solve_submit.py --reverse --start 0 --limit 50
python3 solve_rename.py --watch --interval 60
```

See [SETUP_GUIDE.md](SETUP_GUIDE.md) (or the printable `SETUP_GUIDE.pdf`) for the
full walkthrough, including DeepSeek and resume behavior.

## What's in here

| Path | Purpose |
| --- | --- |
| `open/`, `falsifiable/`, `verifiable/`, `individual/` | The Erdős problem set as LaTeX (`problem_N.tex`). |
| `solve_submit.py` / `solve_rename.py` | Submit problems to ChatGPT and collect answers. |
| `deepseek_submit.py` / `deepseek_rename.py` | Same pipeline for DeepSeek. |
| `erdos_common.py` / `deepseek_common.py` | Shared prompt, parsing, browser and output helpers. |
| `fetch_erdos.py` / `fetch_categories.py` | (Re)download and categorize the problem set. |
| `build_guide.py` | Render `SETUP_GUIDE.md` to `SETUP_GUIDE.pdf`. |

## Output

Each answer is saved twice:

- `solutions/<category>/solution_N.md` — raw machine-readable record.
- `outputs/<platform>/<category>/Erdős #N [verdict] <completeness>%.md` — a
  human-named copy. The percentage is the model's **completeness score** (how
  much of the argument is rigorously established), not its confidence.

Both folders are git-ignored, so your runs stay local.

## Privacy

Your browser session, conversation IDs, and project URL never leave your
machine — `.env`, `.chatgpt_profile/`, `.deepseek_profile/`, and the
`*_chat_map.json` files are all git-ignored.

## Source

Problems are sourced from Tom Bloom's [Erdős Problems](https://www.erdosproblems.com)
database, openly maintained at <https://github.com/teorth/erdosproblems>.
