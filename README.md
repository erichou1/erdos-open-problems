<h1 align="center">Erdős × ChatGPT</h1>

<p align="center">
  <em>An automated, transparent log of frontier-model attempts at every open Erdős problem.</em>
</p>

<p align="center">
  <a href="https://erichou1.github.io/erdos-open-problems/"><strong>🌐 Live status board →</strong></a>
  &nbsp;·&nbsp;
  <a href="https://www.erdosproblems.com">Erdős Problems</a>
  &nbsp;·&nbsp;
  <a href="SETUP_GUIDE.md">Setup guide</a>
</p>

---

Every open [Erdős problem](https://www.erdosproblems.com) can be investigated by
an offline-first, long-horizon proof harness. It locks the exact statement,
builds a validated subgoal DAG, explores independent branches, persists failed
approaches, and separates construction from layered adversarial verification.
The full reasoning artifacts remain auditable.

> [!IMPORTANT]
> **These are machine attempts, not peer-reviewed proofs.** A high completeness
> score is an invitation to verify a transcript — never a claim that a problem is
> actually solved. Treat every result as unverified until a human checks it.

## 🌐 The live board

**→ [erichou1.github.io/erdos-open-problems](https://erichou1.github.io/erdos-open-problems/)**

A single-page dashboard that loads directly from the committed solution files:

- headline stats — attempted, solved, ≥60 % complete, average completeness;
- a searchable, sortable, filterable table of every attempt;
- a **completeness bar** and verdict badge per problem, linking to the full transcript and to the original problem page;
- light / dark themes;
- collaborative **Fable / Cooked** review marks that sync to the repo (connect a fine-grained GitHub token in your browser — never committed).

The board **updates itself.** A GitHub Action ([`.github/workflows/build-site.yml`](.github/workflows/build-site.yml))
regenerates the feed (`data.json`) from `outputs/chatgpt/open/` on every push, so
new solutions appear on the site automatically — no manual rebuild step.

## ⚙️ How it works

1. **Submit** — `solve_submit.py` validates the complete canonical source snapshot before opening the browser, uses only its exact theorem text, and opens a chat per problem in a ChatGPT Project. The prompt and private chat-map entry bind the source snapshot, statement, prompt template, provider, and collection-contract hashes and are explicitly labeled `UNVERIFIED_CANDIDATE`. It drives a real browser via Playwright, so it uses *your* session — no API keys.
2. **Collect** — `solve_rename.py` revisits each chat, saves the answer, and names the file by candidate verdict and completeness, e.g. `Erdős #117 [candidate-proved] 82%.md`.
3. **Publish** — `build_status_sheet.py` turns those filenames into `data.json`; the static site renders it. The Action keeps it current.

For verified research runs, `run_verified_pipeline.py` creates isolated scout,
planner, constructor, reviewer, regulator, revision, and adjudicator contexts.
Only the deterministic gate can emit `verified_proved` or
`verified_disproved`; a model cannot promote its own candidate. Promotion also
requires a statement-bound formal-proof, exact-computation, or expert-review
artifact applied to the exact saved candidate by `promote_verified_run.py`.
Use [`verification-evidence.example.json`](verification-evidence.example.json)
as the schema. The harness hashes the referenced artifact itself.

The completeness score is **how much of the argument the model rigorously
established**, deliberately distinct from how confident the prose sounds.

## 🔎 Search and rank the full corpus

The opportunity searcher is the front door for large research allocations. It
preserves first-party source snapshots, checks that local open membership equals
the canonical catalog, builds one auditable problem card per open problem, and
publishes separate weak-prior rankings for full solutions, partial progress,
Lean, finite computation, literature cleanup, uncertainty, reuse, and protected
exploration. Its probabilities are explicitly **not calibrated yet**.

```bash
# Repair only source-open files missing locally (omit --apply for provenance-only output)
python3 erdos_ingest.py --apply

# Create the complete solver-grade canonical page/section snapshot. This resolves
# upstream main to an exact commit and verifies the commit-pinned catalog bytes.
python3 erdos_ingest.py --canonical

# Build cards and rankings (fails closed without a complete canonical snapshot)
python3 erdos_searcher.py build --top-k 25

# Verify that source state `open` and local open files are exactly equal
python3 check_corpus_integrity.py
```

Current artifacts live under `triage/`; the machine-readable ranking is
`triage/rankings/current.json`. See
[`docs/ERDOS_SEARCHER_SPEC.md`](docs/ERDOS_SEARCHER_SPEC.md) for prediction,
routing, ledger, calibration, and rollback details.

`run_continuous.py` and `problem_queue.py` provide an experimental atomic ranked
queue with disjoint protected exploration, immutable context+ranking hashes,
exact-run-contract claims, and a validated four-to-one allocation cadence.
Continuous multi-worker scheduling remains disabled
in release flags until lease/heartbeat crash tests pass. A bounded test requires the explicit
`--enable-experimental` switch; use `--new-campaign` only before any workers are
active.

## 🚀 Run the pipeline yourself

```bash
git clone https://github.com/erichou1/erdos-open-problems.git
cd erdos-open-problems

python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# For the exact audited dependency set instead: pip install -r requirements.lock
playwright install chromium

cp .env.example .env          # optional: set your ChatGPT Project URL
python3 solve_submit.py --login

# submit a batch, then collect the answers
python3 solve_submit.py --reverse --start 0 --limit 50
python3 solve_rename.py --watch --interval 60

# full statement-locked, independently reviewed workflow
python3 run_verified_pipeline.py --problem 137 --print-statement-sha \
  --model-id <exact-model-id>
python3 run_verified_pipeline.py --problem 137 --max-revisions 2 \
  --model-id <exact-model-id>
# Review proof_runs/problem_137/<run-id>/candidate.md, fill the evidence JSON,
# then promote that exact saved run:
python3 promote_verified_run.py --run-dir proof_runs/problem_137/<run-id> \
  --evidence-json verification-evidence.json --publish
```

Provider rate limits do not consume verified proof attempts. Both verified and
legacy collectors wait and retry with adaptive exponential backoff; every
cooldown and inter-request delay is hard-capped at 120 seconds. Legacy URL-only
chat-map entries are intentionally resubmitted because they lack source hashes.

See [SETUP_GUIDE.md](SETUP_GUIDE.md) (or the printable `SETUP_GUIDE.pdf`) for the
full walkthrough, including DeepSeek and resume behavior.

## 📂 Repository layout

| Path | Purpose |
| --- | --- |
| **`index.html`** | The live status board (static SPA, reads `data.json`). |
| **`build_status_sheet.py`** | Regenerates `data.json` + `status.csv` from `outputs/`. |
| **`.github/workflows/build-site.yml`** | Auto-rebuilds the feed on every push. |
| `outputs/chatgpt/open/` | Human-named solution copies — the source of truth for the site. |
| `solutions/<category>/` | Raw machine-readable solution records. |
| `open/`, `falsifiable/`, `verifiable/`, `individual/` | The Erdős problem set as LaTeX (`problem_N.tex`). |
| `solve_submit.py` / `solve_rename.py` | Submit problems to ChatGPT and collect answers. |
| `deepseek_submit.py` / `deepseek_rename.py` | Same pipeline for DeepSeek. |
| `proof_pipeline.py` | Long-horizon scout, DAG, construct, regulate, revise, and adjudicate orchestrator. |
| `erdos_ingest.py` | First-party corpus crawler with immutable raw snapshots and source hashes. |
| `erdos_searcher.py` | Problem cards, cheap probes, weak-prior rankings, exploration, and ledgers. |
| `run_status.py` | Normalized verified/partial/budget-exhausted/censored/operational outcomes. |
| `problem_queue.py` / `run_continuous.py` | Experimental ranked atomic work queue and continuous worker. |
| `promote_verified_run.py` | Bind external evidence to an exact saved candidate and publish only after the gate passes. |
| `research_state.py` | Immutable statement lock and persistent DAG/lemma/failure memory. |
| `solver_prompts.py` | Offline, role-separated search and verification prompts. |
| `verification.py` | Deterministic proof-promotion gate. |
| `schemas/` / `config/pipeline_features.json` | Artifact contracts and release-state feature flags. |
| `docs/` | Audit, SOTA evidence, architecture, searcher/Lean specs, migration, evaluation, and risks. |
| `problem_catalog.json` | Online source status/provenance, isolated from solver prompts. |
| `erdos_common.py` / `deepseek_common.py` | Shared prompt, parsing, browser and output helpers. |
| `fetch_erdos.py` / `fetch_categories.py` | (Re)download and categorize the problem set. |

## 🔒 Privacy

Your browser session, conversation IDs, and project URL never leave your
machine — `.env`, `.chatgpt_profile/`, `.deepseek_profile/`, and the
`*_chat_map.json` files are all git-ignored. Only the finished solution files and
the site feed are published.

## 🙏 Credits

Problems are sourced from Tom Bloom's [Erdős Problems](https://www.erdosproblems.com)
database, openly maintained at <https://github.com/teorth/erdosproblems>. This
project is an independent experiment and is not affiliated with that database.

See [`SOLVER_ARCHITECTURE.md`](SOLVER_ARCHITECTURE.md) for the trust model and
[`HARNESS_RESEARCH.md`](HARNESS_RESEARCH.md) for the July 2026 comparison with
current research harnesses.
