# EGMRA — Exact Architecture & Pipeline Reference

**Repo:** `erdos_problems/` (github.com/erichou1/erdos-open-problems, branch
`audit/egmra-independent-remediation-20260713`)
**System:** EGMRA — a verification-first autonomous mathematical research
pipeline over the Erdős open-problem catalog (~600 problems).
**Core design rule:** *never upgrade* — no signal is ever reported stronger
than it is; a model's claim is never evidence; only the pinned local Lean
kernel and signed certificates confer trust.

---

## 1. Repository layout

```
erdos_problems/
├── egmra/                      # THE pipeline (Python package, ~100 modules)
├── erdos_searcher.py           # corpus-wide triage/ranking builder (591 problems)
├── triage/                     # searcher output: rankings/, snapshots/, labels/
├── aristotle_lean_project/     # pinned Lean 4.28.0 + Mathlib project (lake)
├── targets/                    # per-problem community Lean statements (gitignored)
├── reviews/                    # signed intent/correspondence/expert certs (gitignored)
├── egmra_campaigns/            # campaign state + checkpoints (gitignored runtime)
├── egmra_outcomes/             # append-only outcome ledgers (gitignored runtime)
├── egmra_runs/                 # per-attempt signed event logs (JSONL)
├── egmra_quarantine/           # fetched Aristotle proof archives (never trusted)
├── egmra_lemma_library.jsonl   # kernel-sealed lemma library (compounding)
├── egmra.keys.sh               # ALL signing keys + API keys (gitignored, 0600)
├── corpus_supplement/          # fetched statements for non-open-status problems
├── AGENT_SETUP.md              # executable runbook for a new machine/agent
├── policy-template.json        # unsigned feature-policy template
└── run_*.py, solve_*.py, …     # LEGACY pipeline drivers (retired; refuse without
                                #   --force-legacy; superseded by `egmra campaign`)
```

Legacy note: `proof_pipeline.py`, `run_continuous.py`, `run_verified_*.py`,
`run_sol2_batch.py`, `run_adjudication.py` are the pre-EGMRA ChatGPT pipeline.
They are gated off; `egmra campaign --triage` is the single production driver.

---

## 2. The `egmra/` package — planes and subsystems

Four architectural **planes** plus supporting subsystems:

| Package | Role |
|---|---|
| `truth/` | Claim graph, evidence router, truth statuses, certificates (IntentCertificate etc.), five-gate release lattice |
| `search/` | Research-program families, mechanism fingerprints, quality-diversity archive, controller posteriors |
| `control/` | Budget ledger, verified-debt obligations, branch leases + fencing, authority tokens |
| `comms/` | Blackboard (packet slices), signed event log, replay |
| `intake/` | Statement parsing → interpretation lattice, integrity probes, problem contract, bounded predicate compiler, intent review |
| `corpus/` | Erdős catalog ingestion (`from_erdos_number`), formal-conjectures fetcher, corpus supplement |
| `retrieval/` | TF-IDF corpus index, frozen SourcePacket, scholarly fetchers (arXiv/Crossref/S2/MathOverflow), **lemma_library** |
| `oeis/` | OEIS client (live/offline cache) |
| `compute/` | Capability-free sandbox for finite experiments + independent replay |
| `lean/` | Aristotle SDK/API adapters, formalizer portfolio, pinned kernel checker, LeanService, correspondence certs, **verdict_cache** |
| `agents/` | ModelRunner protocol: browser ChatGPT (sync + async multi-tab), attested API runners, **exchange_cache**, throttle handling |
| `verification/` | Hostile informal review (T3 producer), referee attack semantics |
| `release/` | Release certificates, promotion, expert review (S2) |
| `learning/` | LongTermMemory (problem_local / procedural stores) |
| `orchestrator/` | **loop.py** (the research loop), **campaign.py** (fleet), runner_worker, result_states, checkpoint, dossier, rerank, calibration, outcome_ledger, triage_source |
| `policy/` | Signed feature policy (HMAC); `egmra` refuses unsigned policies |
| `provenance/` | Canonical JSON, sha256 content ids, stage identity + model attestation |
| `eval/`, `models/`, `selection/`, `services/` | Fixtures/benchmarks, entities, problem selector, service wiring |

---

## 3. End-to-end pipeline (one problem)

```mermaid
flowchart TD
    T[triage/rankings/current.json<br/>searcher order] --> L[Campaign.lease<br/>Neon advisory lock + fencing]
    L --> I[intake: parse → interpretation lattice<br/>+ integrity probes → ProblemContract]
    I --> IC{signed intent cert?<br/>reviews/intent-&lt;id&gt;.json}
    IC -- valid + lattice-blocked --> LIFT[I2 lift: resolve ambiguity,<br/>approve primary reading]
    IC -- none --> BLOCK[BLOCKED_BY_INTERPRETATION<br/>honest terminal]
    LIFT --> CP[cold pass<br/>blind falsifiers + search queries]
    CP --> PKT[freeze SourcePacket<br/>multi-query TF-IDF + lemma library]
    PKT --> SEL[ProblemSelector acquire<br/>+ program families ≤3]
    SEL --> BR[branches: prover / experimentalist /<br/>formalizer / skeptic roles]
    BR --> RND[≤4 rounds each: claims, experiments,<br/>Lean candidates, literature imports<br/>+ reframe-on-stagnation]
    RND --> FRM[Aristotle formalizer<br/>≤5 parallel vendor proofs]
    FRM --> KC[pinned kernel re-check<br/>lake env lean + axiom audit<br/>(verdict cache; passing → lemma library)]
    RND --> EXP[finite experiments in sandbox<br/>+ independent replay]
    KC --> REV[hostile review ×2<br/>assume-wrong referees]
    EXP --> REV
    REV --> ASM[dependency-cone assembly<br/>compiled proof]
    ASM --> REF[referee: 10 mechanical attacks]
    REF --> GATES[five gates T/I/F/N/S]
    GATES --> CLS[classify_result → 1 of 10 states]
    CLS --> LED[outcome ledger append<br/>+ dossier update + auto-rerank]
    LED --> DONE[Campaign.complete<br/>durable in Neon]
```

### 3.1 Intake (`egmra/intake/`)
- `from_erdos_number(n)` resolves the problem from the packaged
  `all_open_problems.tex` snapshot (fallback: `corpus_supplement/`).
- `build_problem_contract` parses with multiple independent parsers →
  **interpretation lattice** (nodes = readings; disagreements =
  `ambiguity_nodes`) + **integrity probes** (invariance, covariance,
  dimensional, boundary enumeration, counterexample search — the last two need
  an executable `--predicate`).
- Empirical fact: **every real catalog statement parses ambiguous**, so
  `release_blocked=True` without an intent certificate.

### 3.2 Intent certificates (the interpretation unlock)
- `egmra derive-intents --erdos N…` batch-signs certs adopting the primary
  reading, corroborated against the community **formal-conjectures** Lean
  statement (19/25 current problems corroborated), writing
  `reviews/intent-<problem_id>.json` + `reviews/evidence-intent-<id>.json`
  (sidecar must NOT match the `intent-*.json` glob) and optional
  `targets/<problem_id>.lean` (`--targets-dir`).
- Loop **I2 lift**: a valid cert resolves *lattice ambiguity only* — probes,
  malformed checks, and all solve/release gates are untouched.
- Keys: signed with `EGMRA_INTENT_REVIEW_KEY`; reviewer id
  `operator-literature-derived` marks machine provenance honestly.

### 3.3 The research loop (`orchestrator/loop.py :: research()`)
Ordered phases (each emits signed events to `egmra_runs/<run_id>.jsonl`):
1. **freeze problem** (source bytes hash → contract hash)
2. **interpretation** + intent-cert binding (I2 lift)
3. **cold pass** — blind falsifiers/queries (no literature yet)
4. **freeze SourcePacket** — multi-query TF-IDF over corpus (+ scholarly modes,
   + sealed **lemma library** records) — every query its own auditable event
5. **acquire** (ProblemSelector; `--explore-blocked` overrides acquisition
   only when release-blocked)
6. **program families** (≤3 distinct mechanisms from
   `search/programs.py`; controller posteriors seeded from procedural memory +
   dossiers) — worker prompts get **problem traps** (from ambiguities/failed
   probes) and the **approach-family registry** (blocked routes)
7. **branch work** (`runner_worker.work_branch`) — per branch:
   role-directed prompt (prover/experimentalist/formalizer/**skeptic**),
   ≤`--worker-rounds` rounds with lemma ledger, objections, failed approaches,
   refocused literature (packet re-ranked by the round's own queries),
   **anti-circularity** rejection (goal-equivalent claims), **reframe** round
   on stagnation, statement-level dedupe, experiment cap 3/branch,
   later-round provider-outage salvage; branch lease heartbeat every 20s
8. **formalization** — source-less Lean candidates dispatched to Aristotle
   (≤5 concurrent process-wide; obligation dedupe; failed dispatch releases
   its slot); with `--targets-dir` the prompt pins the community statement
9. **kernel verification** — `LeanService.verify_declaration` (wrapped by
   `SealedLeanService`): pinned checker runs `lake env lean` on
   `example : <expected_type> := @<decl>` + `#print axioms`; signed
   `FormalCertificate`; bounded repair rounds (`--lean-repair-rounds`) send
   kernel diagnostics back to the formalizer; obligation never changes
10. **hostile review** (`--hostile-review N`) — assume-wrong referees over the
    proposed dependency cone; unattested reviewers collapse to ONE lineage
    (browser can never mint DOUBLE_INDEPENDENT); the T3 informal path needs
    two attested distinct providers
11. **assembly** — dependency-cone compile; literature imports audited against
    the frozen packet (≥2 distinct hosts ⇒ INDEPENDENTLY_CORROBORATED)
12. **referee** — 10 mechanical attacks (countermodel needs a predicate;
    independent_computation/proof_reconstruction dischargeable by formal or
    informal-review evidence)
13. **five gates** — Truth (T1–T5), Interpretation (I1–I2), Formal (F1–F2),
    Novelty (N1–N3), Significance (S1–S2; S2 needs an expert-review cert)
14. **classification** (`result_states.classify_result`) + **checkpoint** +
    **dossier** + **outcome ledger** + optional **auto-rerank** of the pending
    campaign order

### 3.4 The ten honest result states
`BLOCKED_BY_INTERPRETATION · OPEN_NO_PROGRESS · PARTIAL_PROGRESS ·
CONDITIONAL_RESULT · COMPUTATIONAL_EVIDENCE · CANDIDATE_PROOF ·
CANDIDATE_DISPROOF · FORMALLY_VERIFIED_CANDIDATE ·
EXTERNALLY_VALIDATED_SOLUTION · EXTERNALLY_VALIDATED_DISPROOF`
Interpretation integrity dominates; a finite computation never becomes a
general proof; a local release is a *candidate*, never externally validated.

---

## 4. Campaign machinery (`orchestrator/campaign.py`)

- **State:** one signed record `{campaign_id, order, fencing_counter,
  assignments}`; HMAC by `EGMRA_CHECKPOINT_KEY`; tamper ⇒ fail closed.
- **Stores:** `FileCampaignStore` (signed JSON + fcntl) or
  `PostgresCampaignStore` (`--state-store postgres`, `EGMRA_POSTGRES_DSN`):
  one row in `campaign_state` (body as TEXT, signature), cross-host mutex via
  `pg_advisory_lock`, **reconnect-once on dropped connections** (Neon closes
  idle conns). Read-only SQL view `problem_status` for dashboards.
- **Assignment fields:** `status (pending|leased|retained|done|failed)`,
  `attempts` (math budget, max 5), `infra_retries` (infrastructure budget,
  max 24), `resamples` (evidence-based re-runs, max 2), `fencing_token`,
  `lease_expires_at`, `result_state`.
- **lease()** — atomic under lock; only pending/retained/expired-lease
  problems; fencing token increments; per-pickup re-read means reranks apply.
- **run_concurrent()** — worker threads; **heartbeat thread renews the lease
  every `lease_seconds/3` while the runner works** (a problem takes hours;
  without renewal every problem died at attempt 5 — the session's biggest bug).
- **Failure semantics:** provider outages (`BrowserProviderUnavailable`,
  `BrowserRunnerError`, playwright `Error`) ⇒ `retain()` — **refunds the math
  attempt**, spends `infra_retries`; exhausting that ⇒ honest
  `infrastructure_budget_exhausted`. Generic crashes ⇒ `fail()` (math budget).
  `SourceResolutionError` ⇒ permanent.
- **Maintenance verbs:** `--status`, `--requeue-failed` (reset infra-killed
  problems), `--requeue-promising` (completed problems whose *recorded*
  outcome shows progress get another independent sample).
- **Multi-machine:** same `egmra.keys.sh` + same `--campaign-id` +
  `--state-store postgres` ⇒ machines lease disjoint problems from shared
  Neon state (project `erdos-egmra`, `winter-brook-85466804`). `initialize()`
  joins on same id + same problem SET in any order (auto-rerank permutes).

---

## 5. Durability & caching layers (crash = resume, never redo)

| Layer | Granularity | Location | Mechanism |
|---|---|---|---|
| Exchange cache (`agents/exchange_cache.py CachedRunner`) | every model reply | `<ckpt>/<problem>/exchanges/<stage>.<key>.json` | keyed sha256(salt+prompt); attempt-salt = `retry-sample-<n>` after recorded outcomes ⇒ independent pass@k draws; crash retries replay free; attestation re-verified on load |
| Kernel verdict cache (`lean/verdict_cache.py SealedLeanService`) | every kernel check | `<ckpt>/<problem>/kernel_verdicts/` | replays the ORIGINAL signed FormalCertificate; `verify()` on load; only PASSING certs cached; tamper ⇒ live re-check |
| Lemma library (`retrieval/lemma_library.py`) | every kernel-PASSED lemma | `egmra_lemma_library.jsonl` | idempotent append; re-enters retrieval as `proof_status=kernel_checked` records |
| Signed checkpoints (`orchestrator/checkpoint.py`) | per completed branch | `<ckpt>/<problem>/checkpoint_*.json` | signed event-log prefix; `--resume-from` verifies chain or warm-starts |
| Dossier (`orchestrator/dossier.py`) | per attempt | `<ckpt>/<problem>/dossier.json` | family outcomes, failed approaches, terminal states; seeds next process's controller/registry/memory; fail-open |
| Outcome ledger (`orchestrator/outcome_ledger.py`) | per completion | `egmra_outcomes/*.jsonl` | append-only honest telemetry (public_state, gate profile, salvage); NEVER a release authority |
| Event logs | every loop event | `egmra_runs/<run>.jsonl` | hash-chained, signed (`EGMRA_EVENT_KEY`); postgres event store optional |
| Campaign state | per lease/transition | Neon / signed file | §4 |

---

## 6. Trust & verification architecture

**Providers are untrusted. Verification is local.**

- **Model output** = hypotheses/structure only. Parsers reject malformed
  output; nothing a model asserts becomes evidence.
- **Aristotle** (`lean/aristotle_sdk.py`): official async SDK driven from a
  dedicated client-owned loop thread; fetched archives extracted into
  `egmra_quarantine/` under traversal/symlink/bomb limits; vendor COMPLETE is
  never promotion. Concurrency: process-wide 5-slot semaphore
  (`EGMRA_ARISTOTLE_MAX_CONCURRENT`).
- **Pinned kernel** (`lean/kernel_checker.py` + `aristotle_lean_project/`):
  Lean 4.28.0 + Mathlib, `lake env lean` on a definitional obligation,
  `#print axioms` closure vs whitelist, sealed AttestedKernelRunner (embedded
  interpreter path; minimal env). Produces the signed `FormalCertificate`
  (`EGMRA_LEAN_CHECKER_KEY`), where `passed == verify()` (integrity AND
  qualification).
- **Certificates:** IntentCertificate (I2), FormalCorrespondenceCertificate
  (F2 — binds informal claim hash ↔ Lean declaration + elaborated type hash),
  ExpertReviewCertificate (S2), ReleaseCertificate + promotion (signed,
  claim/contract-hash bound, replay-verified). All HMAC-signed with dedicated
  keys from `egmra.keys.sh`; all verification fails closed.
- **Attestation:** API runners attest model identity from response bodies;
  browser runner is honest-unattested; unattested reviewers collapse to one
  lineage (D-013).
- **Sandbox:** finite experiments compile through an AST-whitelisted bounded
  predicate/experiment compiler; run capability-free; independent replay
  required; a finite check supports at most COMPUTATIONAL_EVIDENCE.

**16 signing keys** (all in `egmra.keys.sh`, 0600, gitignored): EVENT, POLICY,
EVIDENCE, RELEASE, GATE, PROMOTION, LEAN_CHECKER, AUTHORITY, TRUTH_SNAPSHOT,
CHECKPOINT (also campaign state), MODEL_ATTESTATION, INTENT_REVIEW,
FORMAL_CORRESPONDENCE, LEGACY_REVIEW, LEGACY_EVIDENCE, EXPERT_REVIEW — plus
`ARISTOTLE_API_KEY`, `EGMRA_POSTGRES_DSN`, browser env
(`CHATGPT_PROJECT_URL`, `CHATGPT_PROFILE_DIR`).

---

## 7. Agents / providers (`egmra/agents/`)

- `runner.py` — `ModelRunner` protocol (`run(prompt, stage=) → RunnerResponse`).
- `chatgpt_browser.py` / `browser_runner.py` — sync Playwright ChatGPT driver:
  ProseMirror paste injection, conversation-URL capture, rate-limit modal
  detection + bounded cooldowns (mid-generation throttles re-checked), 600s
  response timeout (`EGMRA_BROWSER_RESPONSE_TIMEOUT_S`), headed only
  (headless = Cloudflare block).
- `async_browser.py` — ONE Chromium on a dedicated asyncio thread, N tabs as
  independent `TabBackend`s ⇒ genuine multi-worker campaigns (`--workers`,
  default 5; one account throttle-serializes generation, so 3 is the
  sustainable single-account setting).
- `api_runner.py` — attested `openai-api` / `deepseek-api` / `anthropic-api`
  runners (HTTPS-pinned, no-redirect); enable genuine two-lineage T3 review.
- `exchange_cache.py` — §5.
- Legacy root `erdos_common.py` serves the retired pipeline only.

---

## 8. Search intelligence (from the CDC-prompt / ErdosBench / agentic-erdos study)

- **Roles** (`WORKER_ROLE_BY_FAMILY`): direct_structural→prover,
  computational_finite_reduction→experimentalist, formal_library_first→
  formalizer, counterexample families→**skeptic** (refutation-first).
- **Anti-circularity:** token-Jaccard ≥0.9 vs goal ⇒ claim rejected
  (`circular_claim_rejected`); rule also stated in every prompt.
- **Problem traps:** ambiguity nodes + failed probes rendered as an
  adversarial checklist in every prompt.
- **Family registry:** prior `branch_family_outcome`s (memory + dossier)
  rendered as BLOCKED/produced lines; blocked routes reopen only with a
  materially new mechanism.
- **Reframe-on-stagnation:** one materially-different-formulation round
  before a branch ends.
- **Targeted literature:** packet = union of per-query TF-IDF searches;
  continuation rounds re-rank the SAME frozen packet by the round's own
  queries/subgoals (no new retrieval; packet hash unchanged).
- **Calibration loop:** `egmra calibrate` aggregates outcome ledgers →
  `erdos_searcher build --egmra-calibration` applies **capped weak**
  posterior adjustments (an entire EGMRA history < one verified ledger
  record); `egmra refresh-ranking` / campaign `--refresh-ranking-after`
  automate it. `--auto-rerank` reorders the live pending set from outcomes.

---

## 9. CLI reference (`.venv/bin/python -m egmra.cli …`)

| Command | Purpose |
|---|---|
| `run` | single-problem research (`--erdos N` / `--statement`); flags: `--provider`, `--policy` (required), `--intent-review`, `--formal-correspondence-review`, `--formal-target-file`, `--formalizer none\|aristotle\|api\|portfolio`, `--lean-project`, `--lean-repair-rounds`, `--hostile-review N`, `--worker-rounds`, `--budget`, `--predicate`, `--retrieval`, `--oeis`, `--checkpoint-dir`, `--resume-from`, `--expert-review`, `--explore-blocked`, `--lemma-library` |
| `campaign` | fleet driver: `--triage --triage-lane current --max-problems N`, `--campaign-id`, `--state-store file\|postgres`, `--workers` (≤5), `--reviews-dir`, `--targets-dir`, `--lemma-library`, `--outcome-ledger`, `--auto-rerank`, `--refresh-ranking-after`, `--checkpoint-dir`, maintenance: `--status`, `--requeue-failed`, `--requeue-promising` |
| `derive-intents` | batch literature-corroborated intent certs (+`--targets-dir`) |
| `sign-review intent\|correspondence\|expert` | sign individual review certs |
| `formal-target` | fetch one community Lean statement |
| `formalize` | standalone Aristotle→kernel seal round-trip |
| `calibrate` | outcome ledgers → calibration report |
| `refresh-ranking` | calibration → full searcher rebuild |
| `policy-sign` | sign the feature policy |
| `init-db` / `migrate-db` / `verify-events` | event-store management |

**Canonical campaign launch** (current live config):
```bash
source egmra.keys.sh
export CHATGPT_PROFILE_DIR=/Users/eric/workspace/erdos/.chatgpt_profile
nohup .venv/bin/python -m egmra.cli campaign \
  --campaign-id shared-current-v1 --state-store postgres \
  --triage triage --triage-lane current --max-problems 25 \
  --provider browser --workers 3 --worker-rounds 4 --budget 100 \
  --policy egmra_campaigns/policy-promotion-v3-local.json \
  --reviews-dir reviews --targets-dir targets \
  --lemma-library egmra_lemma_library.jsonl \
  --formalizer aristotle --lean-project aristotle_lean_project \
  --lean-repair-rounds 2 --hostile-review 2 \
  --retrieval corpus --oeis offline --explore-blocked \
  --checkpoint-dir egmra_campaigns/ckpts-shared \
  --auto-rerank --refresh-ranking-after \
  --outcome-ledger egmra_outcomes/shared-$(hostname -s).jsonl \
  > /tmp/egmra_shared_$(hostname -s).log 2>&1 &
```

---

## 10. The searcher (`erdos_searcher.py`) and triage

- Builds `triage/rankings/current.json` (allocation_queue, 591 problems) plus
  objective lanes (`highest_probability_*`, `tractable_frontier`,
  `t2_closable`, `subproblem_attack_queue`, …) from the corpus snapshot,
  status labels, attempt exclusions, and (optionally) EGMRA calibration.
- Posteriors are transparent weak-prior Beta estimates
  (`calibration_status: uncalibrated_weak_prior_mvp` →
  `egmra_outcome_adjusted` when calibration is applied). The verified-run
  ledger it consumes is legacy-contract-bound — EGMRA never writes it;
  EGMRA feedback flows only through the capped calibration input.
- `egmra/orchestrator/triage_source.py` drains lanes fail-closed
  (symlink/malformed/not-ready rejected) in searcher order.

---

## 11. Operational invariants & gotchas (hard-won)

1. **Headed browser only**; one Chromium per profile; each machine needs its
   own ChatGPT account. Closing tabs mid-run = infra retains (survivable).
2. `egmra run`/`campaign` **require a signed policy**; test keys live in
   `egmra/tests/conftest.py` (root `tests/` files must set them explicitly).
3. Neon: idle connections drop — the store reconnects once; the heartbeat
   keeps assignment leases alive for hours-long problems.
4. Evidence sidecars are `evidence-intent-*.json` (must not match the
   `intent-*.json` reviews glob).
5. `FormalCertificate.passed == verify()` (integrity ∧ qualification); its
   `environment_id` must be a sha256; `to_dict()` adds derived keys
   (`certificate_digest`, `passed`) that are not constructor fields.
6. Aristotle SDK is fully async — all awaitables marshal to the client-owned
   loop thread; `--prompt` is required with `--formalizer aristotle`.
7. Fresh shared campaign = `DELETE FROM campaign_state WHERE name=…` first;
   same id + same problem set (any order) resumes/joins.
8. A problem completing is TERMINAL for the campaign — re-runs happen via
   `--requeue-promising` (bounded resamples; salt gives independent draws,
   dossiers carry learning).
9. Suite: `.venv/bin/python -m pytest egmra/tests tests -p no:cacheprovider`
   (~1330 tests; use subprocess exit-code capture — zsh capture can swallow
   the summary line).

---

## 12. Data flow summary (what feeds what)

```
searcher snapshot ──► triage lanes ──► campaign order ──► leases (Neon)
outcome ledger ──► calibrate ──► searcher posteriors (capped) ──► new rankings
outcome ledger ──► auto-rerank (live pending order) & requeue-promising
kernel PASS ──► lemma library ──► retrieval packets (all future problems)
every attempt ──► dossier ──► next attempt's controller/registry/memory
every reply ──► exchange cache ──► free replay on crash retry
every kernel verdict ──► verdict cache ──► free replay on identical re-check
```

The system is a closed loop: **rank → attempt → verify → record → learn →
re-rank**, with every expensive artifact cached, every claim gated, and every
outcome honest.
