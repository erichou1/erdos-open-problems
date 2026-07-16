# EGMRA Agent Setup: Executable Cross-Platform Runbook

**Audience:** an AI coding agent setting up EGMRA on a fresh macOS, Windows,
or Linux computer. Work through the phases in order. Stop at every checkpoint
and fix failures before continuing. Ask the human for the setup mode and local
credentials in Phase 0 before running commands that need them.

EGMRA is a verification-first research pipeline over the Erdos problem catalog.
One campaign coordinates triage-ranked browser ChatGPT research, multi-round
branching, Aristotle Lean formalization, warm development checks, sealed local
kernel verification, hostile review, release gates, learning, and durable
outcomes. Computers using the same signed campaign state coordinate through
Postgres so only one active lease owns a problem at a time.

## Definition of done

Setup is complete only when all of the following are true:

1. The virtual environment imports `egmra`, `aristotlelib`, and Playwright.
2. Private credentials are local and gitignored.
3. The signed policy verifies under this campaign's policy key.
4. The pinned Lean project and warm REPL both build and pass smoke checks.
5. The human has logged into ChatGPT in this machine's persistent profile.
6. Tests, intent-review audit, Aristotle smoke test, and database check pass.
7. The operator app starts the campaign and the machine heartbeat appears at
   <https://egmra-status.vercel.app> with the expected Git version.

## Daily operation after one-time setup

Use the operator app rather than editing a campaign command:

- **macOS:** open `EGMRA Operator.app` in the checkout. After clicking
  **Install / refresh app**, use `~/Applications/EGMRA Operator.app` or
  Spotlight.
- **Windows:** double-click `EGMRA Operator.cmd`. After clicking
  **Install / refresh app**, use the Desktop or Start Menu shortcut.
- **Linux:** run `.venv/bin/python -u operator_console.py`. Click
  **Install / refresh app** to add EGMRA Operator to the application menu.

The console binds only `127.0.0.1`, uses a random action token, and never sends
secrets to its browser UI. Its controls are:

- **Check for update:** fetch and compare the configured Git branch.
- **Safe update:** available only while the campaign is stopped. It fast-forwards
  only, retains a Git stash backup of local edits, updates dependencies and
  Chromium when manifests changed, and reapplies the edits. If dependency
  installation fails, local edits are still restored and the retained stash
  remains available.
- **Update + restart:** request campaign stop, update safely, then resume the
  same campaign and local checkpoints.
- **Run / resume pipeline:** launch the current full campaign command.
- **Stop cleanly:** request stop without an unconditional force-kill.
- **Open ChatGPT login:** open the configured persistent browser profile headed
  for human login and 2FA. Stop the campaign before using this action.
- **Install / refresh app:** install a native pointer to this checkout. The
  implementation continues to come from the checked-out `operator_console.py`.

Updates preserve these gitignored local paths:

```text
.env
egmra.keys.sh
.chatgpt_profile*/
operator.local.json
.egmra_operator/
egmra_runs/
egmra_artifacts/
egmra_cache/
egmra_campaigns/
egmra_outcomes/
egmra_quarantine/
egmra_lemma_library.jsonl
reviews/
targets/
aristotle_lean_project/.lake/
```

The updater refuses non-fast-forward/diverged branches and refuses to start
after an update conflict. It never resets, rebases, drops its retained stash,
or chooses a conflict side automatically.

---

## Phase 0: ask the human first

Ask this in one message:

> Which setup is this: (A) join the existing shared campaign, (B) create a new
> shared campaign, or (C) run standalone? I also need this machine's Aristotle
> API key, its allocated Aristotle proof-slot count (`1`-`5`), and the exact
> ChatGPT workspace/project URL. For security, put the provider values directly
> into the local `.env` file when I provide the template; do not paste the API
> key into chat. For a shared campaign I will also need the existing encrypted
> setup bundle, or a Neon Postgres DSN for a new campaign.

Record the answer without recording any secret value.

### A. Joining an existing shared campaign

Ask the primary operator to transfer the following through an encrypted secret
channel, never through Git or chat:

- `egmra.keys.sh`, containing the shared `EGMRA_*` signing keys and
  `EGMRA_POSTGRES_DSN`;
- the signed policy, normally
  `egmra_campaigns/policy-promotion-v3-local.json`;
- `reviews/` and `targets/`, whose signed intent certificates and formal
  targets bind the exact problem statements;
- `egmra_lemma_library.jsonl`, if the primary has a learned library;
- the exact campaign ID, Git branch, triage lane, and maximum problem count.

The transferred key file must contain only shared campaign signing keys and the
DSN. If the primary's historical `egmra.keys.sh` also contains
`ARISTOTLE_API_KEY` or `CHATGPT_PROJECT_URL`, remove those machine-local entries
from the transfer copy. Every computer supplies its own provider values in
`.env`.

For the current production campaign those nonsecret settings are:

```text
branch: audit/egmra-independent-remediation-20260713
campaign_id: shared-current-v1
triage_lane: current
max_problems: 25
state_store: postgres
```

Do not generate new signing keys for a joining machine. In particular,
`EGMRA_CHECKPOINT_KEY`, `EGMRA_POLICY_KEY`, review keys, and evidence/release
keys must match the primary. Mismatches fail closed. Do not copy another
machine's ChatGPT profile or active checkpoint directory.

### B. Creating a new shared campaign

Ask the human to put the Neon Postgres DSN in `egmra.keys.sh` during Phase 2.
The first machine initializes the schema in Phase 3. Later machines follow the
joining path and copy this first machine's shared bundle.

### C. Standalone

Generate new signing keys in Phase 2 and use `state_store: file`. No Postgres
DSN is required. Use a campaign ID that will not be confused with production,
such as `local-<hostname>-v1`.

### Provider concurrency rule

Each machine needs its own ChatGPT profile and should use its own ChatGPT
account. Sharing an account shares its rate limit. Aristotle permits at most
five concurrent proofs per account. In Phase 0, ask how many of those slots
this machine owns. If machines share one Aristotle API key, the sum of their
**Aristotle proof slot** settings must not exceed that account's quota; the
limiter is process-local, not coordinated through Postgres. Separate Aristotle
accounts have separate quotas. The tested default is three browser workers and
three Aristotle slots per machine; five is a maximum, not a requirement.
The operator maps this setting to `EGMRA_ARISTOTLE_MAX_CONCURRENT` in the
campaign process; do not rely on worker count as the formalizer quota.

## Phase 1: prerequisites, clone, and Python dependencies

Use a short local path outside cloud-synced folders. On Windows, a path such as
`C:\src\erdos_problems` avoids Lean/Mathlib path-length and OneDrive locking
problems.

### macOS

First run `xcode-select -p`. If it fails, run `xcode-select --install`, let the
human finish the installer dialog, and restart this phase. Do not continue
while the installer is still open.

```bash
# This must print a developer-directory path.
xcode-select -p

if ! command -v brew >/dev/null; then
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi
if [ -x /opt/homebrew/bin/brew ]; then
  eval "$(/opt/homebrew/bin/brew shellenv)"
else
  eval "$(/usr/local/bin/brew shellenv)"
fi
brew install git python@3.14

git clone --branch audit/egmra-independent-remediation-20260713 --single-branch \
  https://github.com/erichou1/erdos-open-problems.git erdos_problems
cd erdos_problems

python3.14 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m pip install -e ".[aristotle,postgres]"
.venv/bin/python -m playwright install chromium
```

### Ubuntu 22.04+ or Debian 12+ Linux

```bash
sudo apt-get update
sudo apt-get install -y git curl build-essential python3 python3-venv

git clone --branch audit/egmra-independent-remediation-20260713 --single-branch \
  https://github.com/erichou1/erdos-open-problems.git erdos_problems
cd erdos_problems

python3 -c 'import sys; assert sys.version_info >= (3, 10), sys.version'
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m pip install -e ".[aristotle,postgres]"
sudo .venv/bin/python -m playwright install-deps chromium
.venv/bin/python -m playwright install chromium
```

### Windows 10/11 PowerShell

Run PowerShell as the normal user. Install prerequisites if absent, then open a
new PowerShell window so `git` and `py` are on `PATH`.

```powershell
winget install --id Git.Git --exact --source winget
winget install --id Python.Python.3.13 --exact --source winget
winget install --id Microsoft.PowerShell --exact --source winget
```

In a new PowerShell 7 (`pwsh`) window:

```powershell
New-Item -ItemType Directory -Force C:\src | Out-Null
Set-Location C:\src
git config --global core.longpaths true
git clone --branch audit/egmra-independent-remediation-20260713 --single-branch `
  https://github.com/erichou1/erdos-open-problems.git erdos_problems
Set-Location .\erdos_problems

py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip install -e ".[aristotle,postgres]"
.\.venv\Scripts\python.exe -m playwright install chromium
```

### Dependency checkpoint

macOS/Linux:

```bash
.venv/bin/python -c "import egmra, aristotlelib, playwright; print('dependencies ok')"
```

Windows:

```powershell
.\.venv\Scripts\python.exe -c "import egmra, aristotlelib, playwright; print('dependencies ok')"
```

Do not continue until this exits zero.

## Phase 2: private environment and signing keys

Both files below are gitignored. Provider credentials are machine-local in
`.env`; campaign signing material is in `egmra.keys.sh`. The `.sh` name is
historical: the operator parses the file without executing it on every OS.

### 2.1 Machine-local provider file

Have the human create `.env` in the repo root with an editor. They must replace
both placeholders locally and must not show the resulting file to the agent:

```text
export ARISTOTLE_API_KEY='<THIS-MACHINE-ARISTOTLE-KEY>'
export CHATGPT_PROJECT_URL='<EXACT-HTTPS-CHATGPT-WORKSPACE-OR-PROJECT-URL>'
```

Use the exact ChatGPT workspace/project URL when available. A bare
`https://chatgpt.com` works but loses project scoping. On Windows, verify the
file is named `.env`, not `.env.txt`.

### 2.2 Shared campaign key file

**Joining:** place the transferred `egmra.keys.sh` in the repo root and do not
alter its shared keys or DSN. Skip key generation.

**New shared or standalone:** generate all signing keys once.

macOS/Linux:

```bash
test ! -e egmra.keys.sh || { printf '%s\n' 'egmra.keys.sh already exists; refusing overwrite' >&2; false; }
umask 077
for name in \
  EGMRA_EVENT_KEY EGMRA_POLICY_KEY EGMRA_EVIDENCE_KEY EGMRA_RELEASE_KEY \
  EGMRA_GATE_KEY EGMRA_PROMOTION_KEY EGMRA_LEAN_CHECKER_KEY \
  EGMRA_AUTHORITY_KEY EGMRA_TRUTH_SNAPSHOT_KEY EGMRA_CHECKPOINT_KEY \
  EGMRA_MODEL_ATTESTATION_KEY EGMRA_INTENT_REVIEW_KEY \
  EGMRA_FORMAL_CORRESPONDENCE_KEY EGMRA_LEGACY_REVIEW_KEY \
  EGMRA_LEGACY_EVIDENCE_KEY EGMRA_EXPERT_REVIEW_KEY; do
  value=$(.venv/bin/python -c 'import secrets; print(secrets.token_hex(32))')
  printf "export %s='%s'\n" "$name" "$value" >> egmra.keys.sh
done
chmod 600 egmra.keys.sh .env
```

Windows PowerShell:

```powershell
if (Test-Path .\egmra.keys.sh) { throw 'egmra.keys.sh already exists; refusing overwrite' }
$python = '.\.venv\Scripts\python.exe'
$keyNames = @(
  'EGMRA_EVENT_KEY', 'EGMRA_POLICY_KEY', 'EGMRA_EVIDENCE_KEY',
  'EGMRA_RELEASE_KEY', 'EGMRA_GATE_KEY', 'EGMRA_PROMOTION_KEY',
  'EGMRA_LEAN_CHECKER_KEY', 'EGMRA_AUTHORITY_KEY',
  'EGMRA_TRUTH_SNAPSHOT_KEY', 'EGMRA_CHECKPOINT_KEY',
  'EGMRA_MODEL_ATTESTATION_KEY', 'EGMRA_INTENT_REVIEW_KEY',
  'EGMRA_FORMAL_CORRESPONDENCE_KEY', 'EGMRA_LEGACY_REVIEW_KEY',
  'EGMRA_LEGACY_EVIDENCE_KEY', 'EGMRA_EXPERT_REVIEW_KEY'
)
$lines = foreach ($name in $keyNames) {
  $value = & $python -c "import secrets; print(secrets.token_hex(32))"
  "export $name='$value'"
}
[IO.File]::WriteAllLines(
  (Join-Path $PWD 'egmra.keys.sh'), $lines,
  (New-Object Text.UTF8Encoding($false)))
icacls .\egmra.keys.sh /inheritance:r /grant:r "$($env:USERNAME):(R,W)" | Out-Null
icacls .\.env /inheritance:r /grant:r "$($env:USERNAME):(R,W)" | Out-Null
```

For a **new shared** campaign, have the human add this line to
`egmra.keys.sh` in their editor, replacing the value locally. Postgres
credentials containing reserved URL characters must be percent-encoded.

```text
export EGMRA_POSTGRES_DSN='<NEON-POSTGRES-DSN>'
```

### 2.3 Load private values for setup commands

The operator app loads both files safely itself. For manual checkpoints in the
current terminal, load them as follows.

macOS/Linux, using only files obtained from a trusted source:

```bash
set -a
. ./egmra.keys.sh
. ./.env
set +a
PY=.venv/bin/python
```

Windows PowerShell:

```powershell
function Import-EgmraEnv([string]$Path) {
  foreach ($line in Get-Content $Path) {
    if ($line -match '^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)=(.*)$') {
      $name = $Matches[1]
      $value = $Matches[2].Trim()
      if ($value.Length -ge 2 -and
          (($value.StartsWith('"') -and $value.EndsWith('"')) -or
           ($value.StartsWith("'") -and $value.EndsWith("'")))) {
        $value = $value.Substring(1, $value.Length - 2)
      }
      Set-Item -Path "Env:$name" -Value $value
    }
  }
}
Import-EgmraEnv .\egmra.keys.sh
Import-EgmraEnv .\.env
$PY = '.\.venv\Scripts\python.exe'
```

Checkpoint, on either OS:

```text
ARISTOTLE_API_KEY is nonempty
CHATGPT_PROJECT_URL starts with https://chatgpt.com
EGMRA_CHECKPOINT_KEY is at least 32 characters
EGMRA_POSTGRES_DSN is nonempty when state_store is postgres
```

Check without printing values:

```bash
"$PY" -c "import os; assert os.environ.get('ARISTOTLE_API_KEY'); assert os.environ.get('CHATGPT_PROJECT_URL','').startswith('https://chatgpt.com'); assert len(os.environ.get('EGMRA_CHECKPOINT_KEY','')) >= 32; print('private environment ok')"
```

In PowerShell, use `& $PY` in place of `"$PY"` for this and later commands.

## Phase 3: signed policy, reviews, targets, learning, and database

### Joining an existing shared campaign

Place the transferred artifacts at the same relative paths used by the primary:

```text
egmra_campaigns/policy-promotion-v3-local.json
reviews/
targets/
egmra_lemma_library.jsonl
```

The lemma library is optional for correctness, but copying its latest snapshot
avoids discarding verified search learning. The policy, reviews, and targets
are not optional for the full release pipeline.

### Creating a new verification policy

Create `policy-template.json` with this explicit production profile:

```json
{
  "flags": {
    "claim_graph": true,
    "computation_service": true,
    "formal_promotion": false,
    "literature_retrieval": true,
    "promotion": true
  }
}
```

This template matches the current shared campaign's verification policy.
`formal_promotion: false` means kernel-checked candidates may be produced and
audited, but they cannot be formally promoted or released. That is deliberate:
a setup agent may not grant release authority. To create a formally releasing
campaign, the human policy owner must separately approve `formal_promotion:
true`, review the intent/correspondence/release controls, and sign that reviewed
policy with the campaign's existing policy key. Never describe a campaign with
`formal_promotion: false` as release-enabled.

macOS/Linux:

```bash
mkdir -p egmra_campaigns reviews targets
"$PY" -m egmra.cli policy-sign \
  --input policy-template.json \
  --output egmra_campaigns/policy-promotion-v3-local.json
"$PY" -m egmra.cli policy-show \
  --policy egmra_campaigns/policy-promotion-v3-local.json
```

Windows PowerShell:

```powershell
New-Item -ItemType Directory -Force egmra_campaigns, reviews, targets | Out-Null
& $PY -m egmra.cli policy-sign `
  --input policy-template.json `
  --output egmra_campaigns/policy-promotion-v3-local.json
& $PY -m egmra.cli policy-show `
  --policy egmra_campaigns/policy-promotion-v3-local.json
```

`policy-sign` refuses to overwrite an existing policy. Do not delete a shared
policy merely to rerun setup; verify it instead.

For a brand-new campaign, derive and independently audit intent certificates
and formal targets for exactly the selected problem set before enabling
promotion. The supported generator is:

macOS/Linux:

```bash
"$PY" -m egmra.cli derive-intents --erdos <problem numbers> \
  --output-dir reviews --targets-dir targets
"$PY" -m egmra.cli verify-reviews --reviews-dir reviews
```

Windows:

```powershell
& $PY -m egmra.cli derive-intents --erdos <problem numbers> `
  --output-dir reviews --targets-dir targets
& $PY -m egmra.cli verify-reviews --reviews-dir reviews
```

Do not substitute generated intent text for independent mathematical review.
Joining machines copy the already reviewed bundle instead of regenerating it.

### Database

**New shared primary only:** initialize and migrate once.

```bash
"$PY" -m egmra.cli init-db
"$PY" -m egmra.cli migrate-db
```

PowerShell uses `& $PY` instead. A joining machine must not create a competing
database; it only checks reachability:

```bash
"$PY" -c "import os, psycopg; c=psycopg.connect(os.environ['EGMRA_POSTGRES_DSN']); c.close(); print('postgres ok')"
```

## Phase 4: pinned Lean/Mathlib and warm development REPL

The sealed checker remains authoritative. The warm REPL is development-only
search guidance; every accepted candidate still goes through the pinned cold
kernel path.

### macOS/Linux

```bash
curl -sSf https://elan.lean-lang.org/elan-init.sh | sh -s -- -y
export PATH="$HOME/.elan/bin:$PATH"

(cd aristotle_lean_project && lake exe cache get && lake build)

if [ ! -d ../repl/.git ]; then
  git clone --depth 1 --branch v4.28.0 \
    https://github.com/leanprover-community/repl.git ../repl
fi
(cd ../repl && git checkout v4.28.0 && lake build)
```

### Windows PowerShell

Use the official elan installer. It may request confirmation.

```powershell
curl.exe -O --location https://elan.lean-lang.org/elan-init.ps1
pwsh -ExecutionPolicy Bypass -File .\elan-init.ps1 -NoPrompt $true
Remove-Item .\elan-init.ps1
$env:Path = "$HOME\.elan\bin;$env:Path"

Push-Location .\aristotle_lean_project
lake exe cache get
lake build
Pop-Location

if (-not (Test-Path ..\repl\.git)) {
  git clone --depth 1 --branch v4.28.0 `
    https://github.com/leanprover-community/repl.git ..\repl
}
Push-Location ..\repl
git checkout v4.28.0
lake build
Pop-Location
```

The Mathlib cache is several gigabytes and can take minutes to hours. Do not
cancel it merely because output pauses.

Checkpoint:

macOS/Linux:

```bash
(cd aristotle_lean_project && lake env lean --version)
test -x ../repl/.lake/build/bin/repl
```

Windows:

```powershell
Push-Location .\aristotle_lean_project
lake env lean --version
Pop-Location
if (-not (Test-Path ..\repl\.lake\build\bin\repl.exe)) { throw 'warm REPL missing' }
```

## Phase 5: operator configuration and ChatGPT login

Start the checkout-local operator:

macOS:

```bash
open "EGMRA Operator.app"
```

Windows:

```powershell
Start-Process ".\EGMRA Operator.cmd"
```

Linux:

```bash
.venv/bin/python -u operator_console.py
```

The browser opens `http://127.0.0.1:8765/`. Configure these values and click
**Save machine settings**:

| Setting | Current shared campaign | Standalone |
| --- | --- | --- |
| Git branch | `audit/egmra-independent-remediation-20260713` | same |
| Campaign ID | `shared-current-v1` | unique local ID |
| State store | `postgres` | `file` |
| Browser workers | `3` recommended, `1`-`5` allowed | `1`-`3` initially |
| Aristotle proof slots | allocated account share, normally `3` | `1`-`3` initially |
| Reasoning rounds | `4` | `4` |
| Lean repair rounds | `2` | `2` |
| Hostile reviewers | `2` | `2` |
| Problem budget | `100` | `100` |
| Maximum problems | `25` | selected campaign size |
| Prefer solvable | checked | checked |
| Signed policy | `egmra_campaigns/policy-promotion-v3-local.json` | local signed policy |
| Reviews directory | `reviews` | `reviews` |
| Targets directory | `targets` | `targets` |
| Lemma library | `egmra_lemma_library.jsonl` | same |
| Lean project | `aristotle_lean_project` | same |
| Warm Lean REPL | auto-detected sibling `../repl` command | same |
| Checkpoints | `egmra_campaigns/ckpts-shared` | unique local directory |
| ChatGPT profile | this machine's `.chatgpt_profile` | same |

Do not change campaign ID, triage lane, or maximum problem count on a joining
machine unless the primary changes them too. Shared state rejects a different
campaign/problem set.

Click **Open ChatGPT login**. The human must complete login and 2FA in the
headed Chromium window, navigate into the configured workspace if needed, and
then close the entire Chromium window. Never share `.chatgpt_profile` between
computers or run two processes against one profile.

Click **Install / refresh app** once the local console works. Future launches
can use the installed native app/shortcut.

## Phase 6: preflight verification

Reload the private environment in the terminal if necessary, then run every
applicable check.

### 6.1 Full automated suite

macOS/Linux:

```bash
"$PY" -m pytest egmra/tests tests -p no:cacheprovider -q
```

Windows:

```powershell
& $PY -m pytest egmra/tests tests -p no:cacheprovider -q
```

The exact test count changes over time. The requirement is exit code zero, not
an old hard-coded pass count.

### 6.2 Signed policy and intent bindings

```bash
"$PY" -m egmra.cli policy-show \
  --policy egmra_campaigns/policy-promotion-v3-local.json
"$PY" -m egmra.cli verify-reviews --reviews-dir reviews
```

Use `& $PY` and PowerShell backticks on Windows. For the current shared bundle,
every listed intent review must report as binding. Stop on any stale, missing,
or mismatched review.

### 6.3 Warm Lean service

After the operator has written `operator.local.json`:

macOS/Linux:

```bash
REPL_CMD=$("$PY" -c 'import json; print(json.load(open("operator.local.json"))["lean_dev_repl"])')
printf '%s\n' 'example : True := by trivial' | "$PY" -m egmra.cli lean-dev-check \
  --lean-project aristotle_lean_project --repl-cmd "$REPL_CMD"
```

Windows:

```powershell
$replCmd = (Get-Content .\operator.local.json | ConvertFrom-Json).lean_dev_repl
'example : True := by trivial' | & $PY -m egmra.cli lean-dev-check `
  --lean-project aristotle_lean_project --repl-cmd $replCmd
```

The first Mathlib header load can take several minutes; subsequent checks
should be fast. REPL failure degrades to cold checking, but fix it before a
production launch because it materially affects repair throughput.

### 6.4 Aristotle live sealed round-trip

```bash
"$PY" -m egmra.cli formalize \
  --formalizer aristotle \
  --declaration egmra_setup_smoke \
  --expected-type True \
  --prompt 'Return complete Lean code proving theorem egmra_setup_smoke : True.' \
  --lean-project aristotle_lean_project \
  --claim-id setup-smoke
```

On Windows use `& $PY` and PowerShell backticks. This consumes an Aristotle job
and can take several minutes. It must produce a locally sealed/kernel-checked
result; vendor `COMPLETE` by itself is not sufficient.

### 6.5 Shared-state reachability

Shared campaigns only:

```bash
"$PY" -c "import os, psycopg; c=psycopg.connect(os.environ['EGMRA_POSTGRES_DSN']); c.execute('select 1'); c.close(); print('shared state ok')"
```

Do not launch until all applicable checks pass and the operator prerequisite
cards show Shared state, Keys, ChatGPT, and Lean + policy ready. The cards
verify local configuration, key lengths, policy signature, Postgres driver,
and build/REPL presence. ChatGPT authentication still requires the human login
check, and the live Phase 6 commands remain authoritative.

## Phase 7: start or resume the campaign

In the operator app, click **Check for update**. If the machine is current,
click **Run / resume pipeline** once. Do not start a second process for the
same checkout or browser profile.

The app's current full command includes all of these required behaviors:

- browser ChatGPT provider with `1`-`5` workers and four reasoning rounds;
- `--prefer-solvable`, which reorders only pending work by the tractable-frontier
  prior while preserving leased/completed assignments;
- shared Postgres or standalone file state;
- Aristotle formalization, pinned Lean project, two repair rounds, and the
  warm development REPL through `--lean-dev-repl`;
- signed intent reviews through `--reviews-dir`, formal targets through
  `--targets-dir`, and verified learning through `--lemma-library`;
- two hostile reviewers, corpus retrieval, offline OEIS, blocked-route
  exploration, checkpoints, automatic rerank, and a per-machine outcome ledger.

Do not add `--refresh-ranking-after` to a live campaign. It can replace the
triage queue during execution. The current app intentionally uses
`--auto-rerank` and solvability ordering without rewriting the shared problem
set.

Within roughly a heartbeat interval, verify:

1. The app reports a campaign PID and no prerequisite error.
2. The log shows worker leases rather than immediate policy/profile failures.
3. <https://egmra-status.vercel.app> shows this computer as heartbeat-active.
4. The machine card shows the expected branch/commit as current.
5. Active task cards equal live leases; old leases, if any, are labeled stale.

The public status snapshot can lag the database by a few minutes. It is an
observability surface, not a trust root. The signed database state and local
kernel evidence remain authoritative.

## Phase 8: monitoring and updates

- Dashboard: <https://egmra-status.vercel.app>
- Pipeline-fit ranking: <https://egmra-status.vercel.app/ranking.html>
- Local control/log: `http://127.0.0.1:8765/`
- Local outcome ledger: `egmra_outcomes/shared-<hostname>.jsonl`
- Local checkpoints/exchange cache: `egmra_campaigns/ckpts-shared/`

The ranking is a weak-prior pipeline-fit index, not the probability that an
open problem is mathematically solvable. Progress bars show evidence milestones,
not percent proof completion.

When the website or app says a machine is outdated:

1. Open that machine's EGMRA Operator.
2. Click **Update + restart**.
3. Wait for the update action to finish; do not close the app mid-update.
4. Confirm the same campaign ID resumes and the machine reports current.

If the updater reports a conflict or divergence, stop. Record the retained
stash hash shown by the app, inspect `git status` and `git stash list`, and ask
the human which local changes to keep. Never use `git reset --hard`, never drop
the safety stash, and never force checkout over credentials or generated work.

## Troubleshooting

- **`feature policy is unsigned` or signature mismatch:** load the correct
  shared keys and signed policy. Do not sign a replacement with new keys on a
  joining machine.
- **`campaign state already exists for a different campaign`:** campaign ID,
  triage lane, maximum problem count, or signed state does not match the
  primary. Align settings; do not delete shared state.
- **Postgres authentication/SSL failure:** verify the complete Neon DSN is
  present in `egmra.keys.sh`, percent-encode reserved password characters, and
  rerun the Phase 6 connection check without printing the DSN.
- **ChatGPT input box not found:** stop the campaign, click **Open ChatGPT
  login**, complete login/2FA in the configured profile, close Chromium, and
  retry. Do not switch to headless mode.
- **Browser rate limits:** bounded backoff is automatic. If persistent, lower
  workers or use a separate ChatGPT account on each machine.
- **Aristotle quota/rate errors:** coordinate the aggregate worker count for
  every machine sharing that Aristotle key. Never bypass sealed verification.
- **Warm REPL missing:** confirm `../repl` is tag `v4.28.0`, run `lake build`
  there, and check the operator's warm command. Cold verification still
  protects soundness, but throughput will fall.
- **Campaign interrupted:** relaunch the same campaign ID. Leases expire and
  resume; checkpoints, exchange cache, dossiers, and outcomes remain local.
  A new campaign ID creates separate coordination state.
- **Stop remains in progress:** wait for checkpoint activity to finish. The
  app writes the private `--stop-file` marker, lets active problems finalize,
  and does not take new leases. It deliberately does not escalate to a
  force-kill.
- **Campaign predates cooperative stop support:** the app sends no signal and
  refuses Update + restart. Let that legacy process finish, or ask the human to
  explicitly approve a one-time manual interruption after acknowledging that
  the in-flight problem may resume from its last durable checkpoint. Then open
  the updated app and launch the same campaign ID.
- **Website machine is stale:** verify the local campaign is running and its
  database connection works. Stale cards are not counted as active workers.
- **App port already in use:** launching the app again should open the existing
  localhost console. If another program owns port 8765, stop that program or
  run `operator_console.py --port <unused-port>`.

## Hard rules for every setup agent

- Never print, log, commit, upload, or paste `.env`, `egmra.keys.sh`, database
  credentials, browser cookies, API keys, or private signed artifacts.
- Never generate new shared keys on a joining machine.
- Never share one Playwright profile between running processes or machines.
- Never count an infrastructure failure as mathematical evidence.
- Never mark a problem solved or released manually. Only the signed pipeline
  gates may do so.
- Never treat model prose, a vendor `COMPLETE`, the warm REPL, or the public
  website as proof. Only the pinned sealed local kernel result can establish
  formal validity, and correspondence review must still bind it to the
  intended Erdos claim.
- Never weaken policy, intent, correspondence, hostile-review, or kernel gates
  merely to increase throughput.
- Never rewrite shared campaign state or refresh its problem set while workers
  are active.