# Pipeline Gap and Improvement Analysis

**Objective audited:** what would it actually take for this system to *solve an open Erdős
problem* — a correct, genuinely novel, independently verifiable result?

**Date:** 2026-07-14 · **Method:** read-only code/document audit of the repository at
commit `591ab8f` (branch `audit/egmra-independent-remediation-20260713`, dirty worktree),
cross-checked against live web sources (erdosproblems.com, teorth/erdosproblems,
google-deepmind/formal-conjectures, arXiv) fetched on 2026-07-14. Every non-obvious claim
cites a repo `file:line` or a dated external source. No code was modified.

---

## 1. Executive summary

**Bottom line: No. As built, this system cannot solve-and-verify an open Erdős problem
today, and the gap is not primarily an engineering gap in the verification harness — it is
(a) a mathematical-capability gap in the reasoning loop, (b) a truth-admission design that
makes a *general* open statement provable only via a full Lean kernel proof, and (c) a
stale, content-blind view of which problems are attackable at all.** The verification/
honesty machinery (EGMRA gates, referee, kernel checker, promotion policy) is genuinely
strong and fails closed almost everywhere — the system is currently much better at *not
lying* than at *doing mathematics*.

Live-run evidence to date: the legacy candidate pipeline has completed 6 full runs
(problems 601, 661, 724, 782, 849, and 312), all gate status `candidate_rejected`
(5 `candidate_unclassified`, 1 `resource_exhausted`; `proof_runs_sol2/*/manifest.json`).
The EGMRA loop has 18 persisted runs in `egmra_runs/`: 14 stall at
`INTERPRETATION_ADDED` (parser disagreement → `BLOCKED_BY_INTERPRETATION`), 3 reach
`CLAIM_PROPOSED`, 1 reaches `CLAIM_PROMOTED`. Zero `ReleaseCertificate`s exist. The
outcome ledger used for triage calibration is empty.

### The five true blockers, ranked

1. **Reasoning depth (blocker).** In the live EGMRA loop, each mechanism branch gets *one*
   single-shot JSON-schema prompt (`egmra/orchestrator/runner_worker.py:274-305`), with at
   most 3 program families each attempted once inside `max_iterations=4`
   (`egmra/orchestrator/loop.py:531,683,757-810`). There is no live iterative lemma
   decomposition, revision, or proof repair. The deep multi-stage reasoning
   (scouts→synthesis→construction→7 reviews→regulate→revise) lives only in the *legacy*
   pipeline (`proof_pipeline.py`), which by design retires at
   `awaiting_authenticated_release` and can never release (`verification.py:448-455,
   539-547`). Neither pipeline can iteratively *develop and then verify* a research-level
   proof.

2. **The only live truth path for a general claim is a full Lean kernel proof (blocker).**
   The evidence router marks a claim `SUPPORTED` on its own evidence only via
   `formal_verification` (kernel-checked, correspondence-bound) — exact computation
   supports only `finite_domain` scope, and the `informal_review: DOUBLE_INDEPENDENT`
   (T3) path has **no live producer** anywhere in the loop
   (`egmra/truth/router.py:110-127`; `egmra/orchestrator/loop.py:289-360`). So "solve an
   open Erdős problem" currently *means* "autoformalize and kernel-prove the full open
   statement" — beyond the demonstrated frontier for genuinely open targets (AlphaProof
   Nexus closed 9/353 formal Erdős conjectures, arXiv:2605.22763).

3. **The adversarial referee is a mechanical checklist, with attacks that are
   simultaneously unsatisfiable for honest informal work and blind to subtle informal
   errors (blocker).** `MechanicalAttackEvaluator` (`egmra/orchestrator/loop.py:164-256`)
   maps the ten §11.2 attacks to local boolean checks: `independent_computation` and
   `proof_reconstruction` **require finite-experiment replay reports even for a purely
   formal proof**, and `countermodel_search` requires an executable `--predicate`. No
   model ever attacks the mathematics; the checker lineage is the constant string
   `"mechanical-checks-v1"` (`loop.py:1189-1200`), which makes
   `model_family_independence` true by construction (`egmra/verification/referee.py:20-27`).

4. **Stale corpus + no live literature at attack time (blocker for novelty).** The problem
   corpus is frozen ~2025-08-31 (616 files in `individual/`; only 78 mention 2026), while
   the outside world moved dramatically: the community "AI contributions" wiki (data
   through 2026-06-30) lists dozens of *full solutions* to problems this repo still
   marks open — including several in the repo's own 601–899 sweep range (e.g. #650, #659,
   #694, #728/729, #848, #858, #863, #871, #888, #896, #897) — and the repo's ranked
   target #312 had its best-known bound improved in June–July 2026 (arXiv:2607.04157).
   The solver runs literature-blind by policy (`solver_prompts.py:9-17`), the
   "literature grounding" is offline TF-IDF over the frozen local corpus
   (`literature_research.py:1-21`), and EGMRA's live scholarly retrievers only feed ≤5
   record titles truncated to 160 chars into the branch prompt
   (`egmra/orchestrator/runner_worker.py:322-330`).

5. **Content-blind problem selection (major).** The triage rankings are uniform weak
   priors: the "Highest Probability of a Verified Novel Solution" list ranks **the Collatz
   conjecture (#1135, "hopeless" per Erdős) 3rd** and **Singmaster's conjecture (#849)
   2nd**, with nearly every problem scored 0.044 and routed `formal_search`
   (`triage/rankings/highest_probability_verified_novel_solution.md:9-16`;
   `individual/problem_1135.tex`). The Littlewood conjecture (#495) appears at rank 7 of
   the allocation queue (`triage/rankings/current.md`). The posterior is honest about
   being uncalibrated, but it contains no mathematical-difficulty signal at all, and the
   outcome ledger that should calibrate it is empty (`triage/history/` absent/0 entries).

**What a realistic "first genuinely verified result" looks like:** not a full resolution
of a famous open problem, but (i) a **T2 `verified_finite_or_conditional_result`** on a
problem where a finite computation is decisive (the upstream database explicitly labels 9
problems "decidable", 27 "falsifiable", 7 "verifiable" — none of this classification is
imported into triage), or (ii) a **kernel-checked partial/variant result** of the kind the
AI-contributions wiki records as "🟡 Partial result (Lean)" — with a human expert closing
the N2/S2 gates. Section 5 gives concrete targets and section 6 a sequenced roadmap.

---

## 2. As-built vs as-documented pipeline map

### 2.1 The two pipelines and the actual reachability trace

**Pipeline 1 — legacy candidate pipeline** (root scripts + `proof_pipeline.py`):

```
problem_queue/erdos_searcher (weak-prior ranking, 4:1 protected exploration)
  → run_continuous.py / run_verified_pipeline.py (browser ChatGPT, headed, 1 account)
  → literature_research.py (offline TF-IDF packet, scouts+construction only)
  → 4 scouts → synthesis (JSON DAG) → construction → 7 fresh-context reviews
  → regulate → ≤2 revisions → adjudicate → deterministic gate (verification.py)
  → outcome: candidate_rejected | awaiting_authenticated_release   [TERMINAL]
```

Trace of where it actually stops today, from live artifacts:

| Stage | Observed behavior | Evidence |
|---|---|---|
| ranking | near-uniform priors, `allocation_status` contexts | `triage/rankings/current.md`; `run_continuous.py:52-120` |
| solve | ~15 browser stages/problem, ~5h/problem; #312 died `resource_exhausted`, `failure_plane: budget` | `proof_runs_sol2/problem_312/20260713T063508Z-26cc5e56/manifest.json` |
| reviews | 8 reviews recorded, statement-integrity reviewer failed multiple obligations | same manifest, `gate.reasons` |
| gate | requires **adjudicator model lineage distinct from all reviewers** — impossible with one ChatGPT account unless `--adjudicator deepseek` is used (default `same`) | `verification.py:478-486`; `run_continuous.py:143-144,207-209`; manifest `adjudicator_distinct_model: False` |
| release | even a perfect run terminates at `awaiting_authenticated_release`: "legacy truth promotion is retired; use the EGMRA ReleaseCertificate path" | `verification.py:539-547` |

So pipeline 1 is a *candidate generator* whose own gate cannot pass with the current
deployment (single lineage) and whose pass state is deliberately non-authoritative. All
6 completed runs were rejected; 5 legacy manifests (601/661/724/782/849) are quarantined
identity-incomplete records (spec §4.1; `docs/AUTONOMOUS_MATH_RESEARCH_ARCHITECTURE_2026.md:...`
"They were not solutions").

**Pipeline 2 — EGMRA** (`egmra/`, CLI `python -m egmra.cli`):

```
egmra run --erdos N | --statement ... [--predicate EXPR] [--lean-project ...]
  → build_problem_contract (dual parse, lattice, probes)      intake/contract.py
  → status audit → intent certificate check                   loop.py:552-576
  → cold pass (5% budget, blind)                              loop.py:597-616
  → frozen SourcePacket (corpus | arxiv/crossref/S2/MO)       loop.py:620-633
  → acquire (ProblemSelector, k=1)                            loop.py:640-660
  → ≤3 mechanism programs, 1 branch/iteration, ≤4 iterations  loop.py:683,757-810
  → RunnerWorker: ONE JSON-shot per branch                    runner_worker.py:274
  → evidence router (exact_computation | LEAN_PROOF)          loop.py:918-1150
  → MechanicalAttackEvaluator (10 checks)                     loop.py:164-256
  → run_five_gates (T/I/F/N/S/R, HMAC-attested)               release/gates.py:370+
  → PromotionPolicy.authorize → ReleaseCertificate.sign       loop.py:1310-1319
```

Trace of where it actually stops today:

| Step | Observed/derived stop condition | Evidence |
|---|---|---|
| intake | 14 of 18 live runs end at `INTERPRETATION_ADDED`: the two deterministic parsers disagree on dense LaTeX → `BLOCKED_BY_INTERPRETATION` | `egmra_runs/*.jsonl` last-event census (this audit); `SESSION2_PRODUCTION_REACHABILITY_REPORT.md` §1.3 table (Erdős #312/#1 blocked) |
| intent | live release requires a signed IntentCertificate matching source/interp/claim hashes; without it `failures: intent_review_unavailable` and release is off | `loop.py:560-586` |
| deep search | one JSON response per mechanism family; goal claim can only be proposed, never supported, by the model | `runner_worker.py:1-22` (epistemic boundaries), `branch_prompt` |
| truth | general-scope goal ⇒ `SUPPORTED` only via kernel-checked Lean evidence bound to an approved correspondence certificate | `truth/router.py:110-127,137-165`; `loop.py:940-1010` |
| referee | `independent_computation`/`proof_reconstruction` fail without finite-experiment replays; `countermodel_search` fails without `--predicate`; `novelty` fails if you claim N2 | `loop.py:164-256` (`checks` dict) |
| release | max achievable label today: `formally_proved_novelty_unresolved` (T4/T5+I2+F2+N1+S1+R2); `novel_autonomous_resolution` needs N2+S2 (human experts) | `release/gates.py:241-283`; `loop.py:1234` calls `run_five_gates` without `expert_reviewed` ⇒ S1 cap |

**The one fully-proven end-to-end path** is hermetic: the scenario-4 test drives a fake
worker that emits *both* a real sandboxed finite experiment *and* a Lean candidate checked
by a fake attested kernel, plus a compiled `--predicate` countermodel and operator-signed
certificates, reaching `FORMALLY_VERIFIED_CANDIDATE` (commit 55b814a; repo memory;
`egmra/tests/test_sign_review_cli.py` E2E). Live, the same path needs an authenticated
browser producing *valid Lean for an open theorem* — which is exactly the unsolved
research problem. The sealed local kernel (`lake env lean` + `#print axioms`) has been
live-verified only on toy obligations (`egmra/lean/kernel_checker.py`; commit ff9edef).

### 2.2 Spec-vs-implementation compliance table

The ledger says **120/120 VERIFIED** (`IMPLEMENTATION_LEDGER.md`;
`FINAL_VERIFICATION_REPORT.md` §1). The independent FABLE audit re-extracted **216**
requirements and, *after* remediation, graded only **13 VERIFIED**, 126 PARTIAL, 9
UNREACHABLE, 18 TEST-ONLY, 22 UNVERIFIED, 25 BLOCKED-EXTERNAL, 3 OMITTED
(`FABLE_AUDIT_REPORT.md` "Final verdict"), and found the claim "all §13.6 acceptance
criteria pass" **false** (only 4 of 18 fully verified). Substantial post-FABLE work
(commits 2e33424…591ab8f; suite now 1071 passed) has closed many of those gaps, but the
key deltas that matter for the *solve* objective are:

| Requirement | Intended (spec) | Actual (code, this audit) | Status | Evidence |
|---|---|---|---|---|
| REQ-032/089 — 17-step research loop | dynamic AND/OR search, dynamic leaves, reopen, days-long branches (§5.2, §7) | loop runs all 17 phases, but blueprint = 1 leaf/program, each family attempted once, `max_iterations=4`, no reopen/revision in-loop | **PARTIAL — search is a stub** | `loop.py:531,683,757-810`; `_build_blueprint` loop.py:1488 |
| REQ-111 — 10 required attacks | adversarial reconstruction, quantifier reordering, import challenge on real sources, independent skeleton (§11.2) | 10 *named* checks, all mechanical predicates over local state; no model-run attack | **DEVIATED** | `loop.py:164-256`; `verification/attacks.py:7-18` |
| REQ-110/D-007 — referee independence | different model family for high-value claims | `DiversityProfile` with checker lineage `"mechanical-checks-v1"` ⇒ independence true by construction; honest fields, no actual second family | **PARTIAL (honest, weak)** | `referee.py:20-27`; `loop.py:1189-1200` |
| REQ-001/114 — five gates + certificate | separate, never collapsed, signed | genuinely implemented: HMAC-attested `FiveGateResult` bound to event-log head, fail-closed vocab, `is_novel_autonomous_resolution` requires N2+S2+R2 | **VERIFIED (strong)** | `release/gates.py:199-283,370-488` |
| REQ-011/140/090 — M0 promotion safety | kernel + intent + correspondence + signed policy before any formal promotion | done: promotion disabled by default policy; `aristotle_verifier.verify_run` forces kernel; vendor `COMPLETE` never promotes | **VERIFIED** | `promote_verified_run.py`; `DECISIONS.md` D-011/D-014 |
| REQ-090 — real kernel | pinned `lake env lean`, axiom closure, sealed attestation | live-verified on toy obligations; pinned checker embeds interpreter; `#print axioms` closure | **VERIFIED (toy scale)** | `egmra/lean/kernel_checker.py:1-353`; repo memory commit ff9edef |
| REQ-043/053 — theorem-level retrieval | frozen packets with verbatim extracts, import auditor, citation graph | live arXiv/Crossref/SemanticScholar/MathOverflow retrievers exist (`retrieval/scholarly.py:1-401`); but packet reaches the worker as ≤5 titles ×160 chars; no citation graph (acknowledged follow-on); import auditor never exercised against real papers | **PARTIAL** | `runner_worker.py:322-330`; repo memory ("citation-graph follow-on") |
| REQ-041/081 — calibrated selector | competing-risk posterior over real outcomes, VOI | code exists (`egmra/selection/`), but in-loop selection is `k=1` over the single problem (always acquired if budget>0), and the *production* ranking is `erdos_searcher`'s uniform weak priors; outcome ledger empty | **PARTIAL — no calibration data** | `loop.py:640-660`; `triage/rankings/*.md` |
| REQ-131/134 — evaluation levels 1–7, 13 ablations | run against baselines, time-capsule Level 6 | protocol/ablation *code* exists (`egmra/eval/`); no evaluation artifact of any level exists in the repo | **TEST-ONLY** | absence of eval artifacts; `FABLE_TEST_QUALITY_REPORT.md` |
| REQ-020j/052 — OEIS | trigger on experiment sequences, held-out verification | implemented incl. live array-response fix; only triggered if the worker returns `candidate_sequences` | **VERIFIED (narrow trigger)** | `loop.py:868-890`; repo memory 8ee21cc |
| REQ-04A — verified-only learning | expert iteration from authenticated outcomes | stores exist; `promote_verified_fact` wired at release; zero verified facts exist to learn from | **VERIFIED (vacuous)** | `loop.py:1150-1170` |
| §14.7 / REQ-166 — human roles | expert novelty/significance adjudication workflow | `sign-review` CLI lets a key-holder sign intent/correspondence (with self-review honesty note); **no workflow at all** for N2/S2 expert audit | **OMITTED (live)** | `egmra/cli.py` sign-review; `gates.py:163-174` |
| `FINAL_VERIFICATION_REPORT.md` "complete EGMRA system … all 120 VERIFIED" | — | overstated at the "solve" level: honest about live-call exclusions, but "requirement = interface + local test" hides that the *research capability* itself is the untested part | **OVERSTATED** | compare `FABLE_LEDGER_DISCREPANCIES.md` ("Three complete nested searches — FALSE") |

The FABLE finding that the four planes existed but "`research()` invoked none of the
program archive, AND/OR controller, or Lean proof-state search" has been partially
remediated — the loop now instantiates programs, a blueprint, a controller, leases,
blackboard slices, and the debt policy (`loop.py:663-780`) — but the *depth* of that
search (one shot per family) still does not implement the spec's intent of "days-long
branches" and "dynamic leaves" (§7.8 band 4).

---

## 3. Gap analysis by subsystem

### 3.1 End-to-end reachability — why nothing has been solved+verified

**Current state.** Two pipelines, connected only by artifacts: legacy produces deep but
unverifiable candidates; EGMRA produces verifiable but shallow research. The single
scenario where EGMRA emits an authenticated release requires the model to hand over a
complete, kernel-checkable Lean proof of the exact locked statement plus a finite
experiment and a countermodel predicate in *one JSON response per branch*.

**Gap.** There is no path that carries the deep reasoning into the verified pipeline.
Because the end-state should be **one** production pipeline, the right fix is to port the
legacy prompt discipline and multi-stage repair into the EGMRA worker and then retire the
legacy pipeline (R3), with Aristotle as EGMRA's formal-candidate backend (never a trust
root, D-014). A legacy→EGMRA candidate bridge is at most a *one-time salvage* of the
gate-surviving candidates already paid for — building it as ongoing infrastructure would
entrench two pipelines. Today neither exists:
`run_verified_pipeline.publish_verified_result` and the EGMRA truth plane never exchange
mathematical content.

**Severity: blocker.** Evidence: `verification.py:539-547` (legacy terminal);
`runner_worker.py:274-305` (single shot); zero `ReleaseCertificate`s in `egmra_runs/`.

### 3.2 Informal reasoning / solver quality

**Current state.** The legacy prompt suite is genuinely well-designed: role separation,
immutable statement lock, untrusted-data fencing, structured `<result>` contract,
failure memory, regulator triage (`solver_prompts.py:43-63,105-140,178-210`). Per-stage
resume and rate-limit recovery are mature (repo memory). The EGMRA-side prompts are much
weaker: one cold-pass prompt and one branch prompt requesting a giant JSON object
(`runner_worker.py:259-305`), with the referee prompt (`referee_prompt`,
`runner_worker.py:307-318`) apparently used only for advisory falsifiers.

**Gaps.**
- No multi-turn proof development in EGMRA (no revision, no failed-approach memory
  consumption, no subgoal reattack).
- The legacy pipeline's stage budget (~15 browser stages ≈ 5h/problem;
  `resource_exhausted` on #312) spends most tokens re-serializing whole proofs, exactly
  the §4.2 "whole-proof constructor" weakness the spec ordered demoted.
- `max_repair_attempts: int = 1` for malformed JSON (`runner_worker.py:327,366-375`) — one
  malformed response kills a branch's entire contribution.
- The browser model is not used near capability: no branching best-of-n at the
  construction stage, no tool use (the sandbox exists but the model must volunteer an
  `experiment` in its single response), no premise retrieval into the prompt beyond 800
  chars of packet titles.

**Severity: blocker** (this is where solving actually happens).

### 3.3 Verification and the referee

**Current state.** Honest and fail-closed. Ten attacks enumerated
(`verification/attacks.py:7-18`), pessimistic aggregation, defect-reward
(`referee.py:100-107`), gates attested against the exact event-log head
(`gates.py:295-345`, `verify_attestation`), release invalidated on any concurrent state
change (`loop.py:1319`, `release_invalidated_before_return`).

**Gaps.**
1. *Attacks unsatisfiable for honest work:* a complete, correct, kernel-checked formal
   proof of a general statement with **no finite experiment** still fails
   `independent_computation` and `proof_reconstruction` (the `checks` dict in
   `loop.py:164-256` requires non-empty matching replay reports), and fails
   `countermodel_search` unless the
   operator supplied `--predicate`. For problems that are not naturally
   predicate-checkable (e.g. #312's multiset quantification over all A), this demands an
   artificial finite side-experiment as a release ticket.
2. *Attacks vacuous against dishonest work:* nothing model-driven ever re-derives the
   argument; `proof_reconstruction` ≙ "compiled DAG closes + replay ok"
   (within the `checks` dict, `loop.py:164-256`), which is not §11.2's "referee writes a
   concise independent skeleton". For an informal-only run there is **no mathematical
   soundness check at all** beyond the graph's own dependency closure — the T3 lane, if
   ever wired, would currently promote on structure, not on hostile reconstruction.
3. *Independence is definitional:* generator lineage (browser label) vs checker lineage
   (`"mechanical-checks-v1"`) always differ (`loop.py:1189-1200`; `referee.py:20-27`).
   D-007 acknowledges this honestly, but the effect is that `blocks_release` never
   triggers on the independence axis, i.e. the axis does no work.

**Severity: blocker** (both directions — false negatives for honest general results,
false confidence for informal ones).

### 3.4 Formalization / Lean

**Current state.** Strongest subsystem. Real pinned kernel checks with axiom-closure
extraction, sealed attestation, quarantine-hardened Aristotle intake, deterministic
obligation hashes (`expected_type_hash`), correspondence certificates verified three ways
(`truth/router.py:137-208`), formalizer protocol with Aristotle SDK adapter live-tested
(`egmra/lean/formalizer.py`; repo memory commits 48da500, ff9edef, c79b2f4).

**Gaps.**
- The informal→Lean gap for a real Erdős statement is the dominant cost, and the current
  path expects the *browser worker* to emit `lean_declaration_candidates` with correct
  `expected_type` in its single JSON reply (`runner_worker.py:60`). There is no
  L0 semantic-target package flow live (2–3 candidate translations, backtranslation,
  example/anti-example lemmas — `egmra/lean/target_package.py` exists but is not invoked
  from the loop).
- Autoformalization reliability at research level is known-poor: 89.5% compilation but
  60.5% faithfulness (Beyond Compilation, arXiv:2606.31002); paraphrase-robustness
  failures (arXiv:2606.14867); 31.8% formalization-error rate found in ProofNet ports
  (ProofNet#, ACL 2025). The repo's own spec cites these (§2.3). Nothing in the live loop
  runs the "translation firewall" against a *model-produced* Lean target; the intake
  probes guard only the *informal* statement.
- 496 of 1217 problems already have human-reviewed Lean statements in
  `google-deepmind/formal-conjectures` (README, fetched 2026-07-14; pinned Mathlib
  v4.27.0, immutable `bench-v{N}` tags). The repo does not consume them. This is the
  single cheapest correctness upgrade available: adopt the community formalization as the
  locked target instead of trusting a fresh model translation.
- No prover portfolio: the only proof producers are the browser model and Aristotle.
  No DeepSeek-Prover-V2 / Goedel-Prover-V2 / open prover integration, no LeanDojo-style
  premise retrieval, no `lean4checker` second trust path for T5.

**Severity: major** (works, but only for toy obligations; not yet a research instrument).

### 3.5 Compute / finite experiments

**Current state.** Hardened `RestrictedPython`/subprocess sandbox with independent-
interpreter replay, 6-way checked classification, float-never-proves-exact, RUP
reconstruction for SAT (`egmra/compute/`; `loop.py:289-360`). The epistemic boundary is
enforced and tested: exhaustive finite computation supports only `finite_domain` scope —
a general claim stays `UNKNOWN` (repo memory; `_execute_finite_experiment` docstring).

**Gaps.**
- No SAT/SMT/CAS backends actually wired (protocol only), no `sympy`/`numpy` in the
  sandbox (stdlib `Fraction` only) — real enumeration problems (e.g. basis/exact-order
  computations, covering systems) need more than capability-free pure-Python one-shots.
- Experiments only happen if the *model volunteers* code in its single JSON reply;
  there is no orchestrator-initiated experiment planning.
- The upstream DB's machine-relevant statuses — 9 decidable, 27 falsifiable, 7
  verifiable (teorth/erdosproblems README, commit 8b46f27, fetched 2026-07-14) — are not
  synced into `problem_catalog.json`/triage, so the systems best lane (finite
  computation that *settles* a problem) is invisible to selection.

**Severity: major** — this is the most credible near-term path to a first genuine
verified result and it is under-plumbed.

### 3.6 Literature grounding + novelty

**Current state.** Legacy: offline TF-IDF/tags/citations over the frozen local corpus,
explicitly untrusted, flags runs `rediscovery_eligible` (`literature_research.py:1-21`).
EGMRA: four live scholarly retrievers with host allowlists and injection guards
(`retrieval/scholarly.py`), OEIS client, frozen `SourcePacket`s, novelty *query log*
structures. `novelty_probe.py` greps catalog/forum text for prior-work signals
(heuristic, offline; lines 1-25).

**Gaps.**
- Corpus staleness is now the biggest single novelty risk: 616 snapshot files, 538
  showing no 2026 update, in a period when the AI-contribution wave resolved dozens of
  these exact problems (wiki, 2026-06-30 snapshot). A "verified novel solution" claim
  produced against this corpus would frequently be a rediscovery.
- Retrieved records seed almost nothing: the branch prompt gets titles only; there is no
  per-problem deep-dive (read the actual papers behind #312's `[ErGr80]`, the forum
  thread with Kovač's lower-bound construction and Korsky's method sketch — all publicly
  posted and directly strategy-relevant). `forum_threads/*.json` exists in the workspace
  and *no code reads it* (repo memory).
- `novelty_verdict` is a caller-supplied string into `research()` (default `"N1"`,
  `loop.py:517`); nothing computes it from an actual logged search. It is fail-closed
  (N2 self-claims are blocked by the referee's novelty check, `loop.py:247-250`), but N1 ("logged search
  found none") is being asserted without a logged search — a mislabel per §11.3.

**Severity: blocker for the novelty gate; major for solver quality.**

### 3.7 Problem selection / triage

**Current state.** Reproducible, contract-bound, honest about being uncalibrated
("transparent weak-prior MVP estimates", every ranking file header). Protected
exploration and per-context ranking caches work (`run_continuous.py:52-120`).

**Gap.** The scores carry no mathematics: Collatz (#1135) at rank 3 and Singmaster
(#849) at rank 2 for *verified novel solution*; #324 at rank 1 — a problem Erdős–Graham
call "very annoying", whose best partial result (Ruzsa 2001: `{n^5+⌊cn^4⌋}` is Sidon)
took a serious paper, and which the Lander–Parkin–Selfridge conjecture would only
*conditionally* settle (erdosproblems.com/324, fetched 2026-07-14). The
`subproblem_attack_queue.json` (326 entries) is contract metadata without mathematical
content per entry. The features that would matter — known-partial-result ladder,
decidable/falsifiable/verifiable status, formal-conjectures coverage, AI-wiki activity,
forum activity ("SamKorsky currently working on #312") — are all absent.

**Severity: major.** Evidence: ranking files cited above; `individual/problem_1135.tex`
("Erdős referred to this problem … as 'hopeless'").

### 3.8 Orchestration / ops

**Current state.** Mature for what it does: per-stage resume with content-addressed
caches, rate-limit modal recovery with bounded shared pause budget (`browser_runner`
mid-generation throttle detection, commit b3dc4fa), 3-worker settled configuration,
async multi-tab campaign engine (commit a5df951), file/Postgres campaign stores with
signed state (commit 2498909), launchd KeepAlive workers.

**Gaps.** Throughput arithmetic is the issue: ~5h/problem × 151 problems/worker on one
account is ~3 weeks per sweep of *unverifiable candidates*; EGMRA live runs stall in
intake. Headless is impossible (Cloudflare); one authenticated account is both the rate
limit and the model-diversity ceiling. Cost per *verified* progress unit is currently
infinite (denominator zero).

**Severity: minor-to-major** (dominated by upstream blockers; becomes binding once the
math works).

### 3.9 Human-in-the-loop

**Current state.** `egmra sign-review intent|correspondence` lets a review key-holder
sign the two correspondence-critical certificates, printing an explicit "signing ≠
independence; operator holding all keys = self-review" note (repo memory, commit
591ab8f). Human responsibilities are enumerated (`egmra/comms/human.py`).

**Gap.** The steps that genuinely require an *independent* human — intent review,
formal-correspondence review, novelty (N2) and significance (S2) adjudication — have no
defined operational workflow: no reviewer roster, no conflict declaration capture beyond
schema fields, no packet format for an external mathematician, no expected turnaround.
Since `novel_autonomous_resolution` requires N2+S2 (`gates.py:241-247`), *every* headline
outcome is human-gated, and that human process does not exist yet.

**Severity: blocker for the final claim; procedural, not code.**

---

## 4. Literature review

### 4A. Pipeline-improvement techniques → concrete changes here

| Work (year, venue/id) | Finding | Concrete application here |
|---|---|---|
| Aletheia Erdős sweep — arXiv:2601.22401 (2026) | 137/200 graded candidates fundamentally flawed; of 63 technically correct, only 13 meaningful (2 full, 2 partial, 4 rediscoveries, 5 literature IDs) | Calibrates expectations: correctness ≠ fidelity ≠ novelty. Justifies the repo's five-gate design; implies the *expected value* of each legacy sweep run is dominated by rediscovery/vacuity, so novelty tooling matters more than more scouts |
| QED — arXiv:2604.24021 (2026), github.com/proofQED/QED | structural review before local checking; regulator-directed repair; exact-stage resume | Legacy pipeline already mirrors this; port its *localized repair* (only failed dependency cone) into EGMRA's blueprint instead of whole-proof revision |
| Danus — arXiv:2607.06447 (2026) | typed fact DAG + cascading revocation; LLM-verified admission found insufficient | Validates EGMRA's stricter validator-typed admission; adopt its negative-memory reuse for the failed-approach store |
| AlphaProof — Nature (2025) | value-guided Lean search at extreme compute; manual formalization of targets | Confirms: don't autoformalize the target when a human-reviewed statement exists → consume formal-conjectures |
| AlphaProof Nexus — arXiv:2605.22763 (2026), results repo | **9/353 formal Erdős conjectures proved**; evolutionary fitness hacked by `sorry`-shaped helpers; hallucinated lemmas | Base rate for "formal search on open Erdős targets" ≈ 2.5%, mostly easy/already-solved items; verified-debt anti-gaming (already in `search/verified_debt.py`) is the right countermeasure |
| Aristotle — arXiv:2510.01346; Erdős #728 write-up arXiv:2601.07421 | research-level formal artifacts possible with manual targets; vendor status untrustworthy | Already integrated correctly (never a trust root, D-014); use it as the main formal-candidate worker on *partial* obligations, not whole problems |
| DeepSeek-Prover-V2 — arXiv:2504.21801 (2025, weights public) | informal sketch → recursive `have` subgoals + compiler feedback | The missing prover portfolio member; runs locally, breaks the one-account/one-lineage ceiling and gives the legacy gate its distinct adjudicator lineage for free |
| Goedel-Prover-V2 — arXiv:2508.03613 (2025, open) | expert iteration + two-round correction | Same role; open weights allow verified-only expert iteration later (REQ-04A) |
| Seed-Prover 1.5 — arXiv:2512.17260 (2025) | leading Lean artifact index; agentic search + RL | Watch item; artifacts public, engine closed |
| LeanDojo/ReProver — arXiv:2306.15626 (2023, NeurIPS) | premise retrieval + best-first tactic search, reproducible | Premise retrieval into formal branch prompts (currently zero Mathlib context is provided) |
| LeanSearch v2 — arXiv:2605.13137 (2026) | theorem retrieval measurably improves formal search | Same — wire into `retrievePremises` (`egmra/retrieval/premises.py` exists, unused live) |
| Beyond Compilation — arXiv:2606.31002 (2026) | 89.5% compile vs 60.5% faithful autoformalization | Justifies mandatory translation firewall before any model-produced Lean target is release-relevant; prefer community-reviewed statements |
| Autoformalization robustness audit — arXiv:2606.14867 (2026) | paraphrase-sensitive, mutation-insensitive formalizers | Run the existing paraphrase/mutation probes *on the Lean side* (L0 target package) — code exists (`lean/target_package.py`), not wired |
| ProofNet# — ACL 2025 (aclanthology 2025.emnlp-main.907) | 31.8% of existing formal ports had errors | Same lesson; also justifies pinning formal-conjectures *bench tags* rather than main |
| FunSearch — Nature (2023); AlphaEvolve — arXiv:2506.13131 + 67-problem study arXiv:2511.02864 | evolutionary search works only under hard executable fitness | For construction-type Erdős problems (Sidon-set constructions, coverings), an islanded search over *programs* scored by the exact sandbox is a genuine capability the compute plane can host |
| ProofCouncil — arXiv:2607.09474 (2026); FirstProof Batch 2 report (1stproof.org) | 6/10 research problems at $3,186/22.9h with full logs; critics still err both ways | Cost model reference: genuine research-problem attempts cost O($10²–10³) each even for strong systems; a $0-API browser pipeline trades money for wall-clock and reliability |
| Formal Conjectures — arXiv:2605.13171 (2026), google-deepmind/formal-conjectures | 496 Erdős statements formalized, human-reviewed, bench-versioned; AlphaProof used to catch misformalizations | **Adopt as the formal target source**; contribute repo formalizations upstream for review (free independent intent audit) |
| erdosproblems.com AI-contributions wiki (through 2026-06-30) | community ledger of AI results incl. dozens of full solutions and Lean formalizations; wiki frozen after Jun 30 | The de-facto novelty baseline and rediscovery database for this exact problem set; must be ingested into `novelty_probe` |

### 4B. Mathematics for the top-ranked candidate problems

**#312 (unit fractions; Erdős–Graham).** Is there `c>0` s.t. any finite multiset with
`∑ 1/n > K` has a subset with `1 − e^{−cK} < ∑_{S} 1/n ≤ 1`? Status: OPEN
(erdosproblems.com/312, edited 2026-01-20, fetched 2026-07-14). Known: Erdős–Graham got
gap `c/K²`; **S. Korsky (arXiv:2607.04157, July 2026) proves gap `exp(−c√(K log K))`**
via a compression + sparse-activation/Fourier argument (author-disclosed heavy GPT-5.5
assistance; forum reviewers raised authorship/rigor concerns — post-7409/7411,
erdosproblems.com/forum/thread/312). V. Kovač's forum construction (18 Aug 2025) shows
prime-multiset examples with `ε(A) ≥ e^{−(1+o(1))K log K}`, so the conjectured `e^{−cK}`
sits between the new upper bound and that floor. Remaining gap: `√(K log K)` → `K` in the
exponent — a real but focused analytic problem; the compression framework is public and
seedable. *Implication for the repo:* its frozen corpus (`individual/problem_312.tex`,
"Last updated: 2025-08-31") knows none of this; a run today attacks a 10-month-stale
frontier and cannot be novel below `exp(−c√K)`-strength results.

**#324 (Sidon values of a polynomial).** Does some `f ∈ ℤ[x]` make all `f(a)+f(b)`
distinct? Believed: `x^5` works; would follow from Lander–Parkin–Selfridge. Known:
quadratics/cubics/`x^4` fail (Dubickas–Novikas 2021 for cubics); Ruzsa [Ru01b]:
`{n^5+⌊cn^4⌋}` is Sidon for some `c` (erdosproblems.com/324, fetched 2026-07-14).
*Assessment:* rank-1 in the repo's "verified novel solution" list, but a full solve
likely needs new Diophantine input beyond current methods; the *tractable* subtarget is
formal/computational: formalize Ruzsa's construction or extend the excluded-degree
classification — partial-result lane only.

**#849 (Singmaster).** Erdős–Gordon/Singmaster: does every multiplicity `t` occur for
binomial coefficients? Known: Matomäki–Radziwiłł–Shao–Tao–Teräväinen (2022) — at most two
solutions in the regime `k ≥ exp((log n)^{2/3+ε})`; no examples with `t ≥ 5` known
(`individual/problem_849.tex`). Both Erdős and Singmaster believed the *negative*.
*Assessment:* famous, hard; the finite-computation lane (search for `t=5` patterns) is
astronomically explored already; not a credible solve target — its rank-2 position is a
selector artifact.

**#1135 (Collatz).** Ranked 3rd for "verified novel solution"; Erdős: "hopeless";
Lagarias 2010 survey is the canonical reference (`individual/problem_1135.tex`).
*Assessment:* the ranking's strongest self-indictment.

**#336 (exact order of additive bases, `h(r)`).** Known: `1/3 ≤ lim h(r)/r² ≤ 1/2`
(Grekos 1988; Nash 1993), refinements by Plagne (2004); small values `h(2)=4`, `h(3)=7`,
and **`h(4) ∈ {10, 11}` open** (`individual/problem_336.tex`). *Assessment:* determining
`h(4)` is a *finite-flavored, publishable, genuinely open* subproblem: a candidate for
exact search over structured basis families plus a combinatorial upper-bound argument —
exactly the T2 lane this system can verify end-to-end (exhaustive finite certificate +
kernel-checked combinatorial lemma). This is the kind of target the triage should be
surfacing and is not (it appears only via the generic lists).

**#153 (gaps in Sidon sumsets).** For finite Sidon `A`, does
`(1/t)∑(s_{i+1}−s_i)² → ∞`? Little on-record progress; related to well-studied Sidon
gap/density literature (`individual/problem_153.tex`; erdosproblems.com/153).
*Assessment:* plausibly approachable via known `B_2[g]`/gap-distribution techniques;
medium; needs a real literature deep-dive first (Cilleruelo-school results on Sidon set
gaps are the obvious seed corpus).

**Upstream finite-computation classes.** The community DB labels 9 problems `decidable`,
27 `falsifiable`, 7 `verifiable` (README, commit 8b46f27) — e.g. #7 (covering systems,
verifiable), #307 (unit fractions, verifiable), #647 (£25, verifiable), #364/#366
(verifiable), #19/#547/#551/#556 (decidable). These are the problems where a sandboxed
exact computation *is* a proof-of-statement (modulo a checked reduction), i.e. where this
system's strongest verified lane (T2 `exact_computation` + `finite_domain` scope, upgraded
by a kernel-checked reduction lemma to the general claim) actually closes something.
None of this status data is in `problem_catalog.json`.

---

## 5. Candidate problems most plausibly solvable now — shortlist

Validated against this system's *real capability*; openness/tractability of each pick is
**provisional until the R1 live status refresh runs** (the corpus is 10 months stale,
§3.6). Ranked by (capability fit) × (apparent openness as of the sources fetched
2026-07-14):

### 5.1 `h(4)` for exact additive bases — subproblem of #336 (provisional top pick)

- **Why tractable:** `10 ≤ h(4) ≤ 11` (Plagne 2004) — a two-valued open question.
  The lower bound is witnessed by an explicit order-4 basis with exact order 10+; closing
  it means either constructing a basis of order 4 and exact order 11 (finite certificate:
  verify order/exact-order properties up to an effective threshold via the
  Erdős–Graham coprimality criterion, `individual/problem_336.tex`) or proving no such
  basis exists (structured case analysis, plausibly formalizable).
- **Evidence/formalization that closes it:** construction direction = exact computation
  (sandbox, independent replay, T2/R2) + a kernel-checked "eventually periodic ⇒ exact
  order" reduction lemma; that combination is precisely the hermetically-proven
  scenario-4 shape (finite experiment + Lean candidate + predicate).
- **Pipeline support needed:** sympy-free exact enumeration is fine (integers only);
  orchestrator-initiated experiments (§3.5); import audit of Grekos/Nash/Plagne bounds;
  human intent review of the exact-order definitions (subtle: "every large integer").
- **Risk (why this pick is provisional):** the `10 ≤ h(4) ≤ 11` state is sourced from the
  frozen 2025-08-31 corpus record; Plagne's later work or the 2025–26 AI wave may already
  settle `h(4)`, and the repo cannot currently tell (§3.6). Confirm openness via R1 (live
  erdosproblems.com/#336 + literature pass) *before* committing compute; only then does
  this become a validated target.

### 5.2 A `verifiable`/`decidable`-class problem from the upstream DB (e.g. #7, #307, #647)

- **Why tractable:** the community has already certified that a finite computation
  decides or verifies these; the repo's compute plane + replay + T2 gate is exactly the
  right instrument, and the result label `verified_finite_or_conditional_result`
  (`gates.py:274-276`) is attainable *today* without any new proving capability.
- **Attack plan:** sync `data/problems.yaml` statuses; for each candidate, have the
  intake lattice lock the reduction statement; hand-audit the "finite computation
  suffices" reduction (human intent review — this is where the danger lives); run the
  enumeration in-sandbox with an independent replay; release at T2+I2+N1+S1+R2.
- **Pipeline support needed:** status sync; bigger compute budgets (some of these
  computations are large — pick the smallest); a documented human reduction-audit step.
- **Honest cap:** several of these computations may be infeasibly large (that's why
  they're open); select by estimated state-space size first.

### 5.3 #312 partial-progress / formal-infrastructure lane

- **Why:** active frontier with a public method (Korsky's compression + activation
  lemma, arXiv:2607.04157) and a public lower-bound construction (Kovač, forum
  2025-08-18); the remaining `√(K log K)` → `K` exponent gap is a live, well-posed
  analytic target. Also the cleanest *rediscovery-safe* play: formalize the
  Erdős–Graham `c/K²` baseline and/or the new `exp(−c√K)` argument in Lean (both would
  be firsts; formal-conjectures has the statement, 312.lean) — "reusable formal
  infrastructure" per the spec's own outcome taxonomy (§6.2).
- **Pipeline support needed:** ingest the forum thread + the two arXiv references into
  the solver packet (the crawler exists, `crawl_forum_threads.py`; the data is unused);
  multi-turn worker; Aristotle/DSP-V2 on the decomposed lemmas.
- **Honest cap:** a full solve of #312 by this system is not plausible now; a
  well-scoped verified partial (e.g. the prime-multiset lower bound as a kernel-checked
  theorem) is.

**Negative validations:** #324, #849, #1135, #495 (Littlewood), #602 (Property B) are
not attackable-to-resolution by this system's real capability; their top-of-queue
positions are selector noise (§3.7).

---

## 6. Prioritized recommendations

### 6.1 Scored table (Impact on P(first verified novel result) × Effort)

| # | Recommendation | Impact | Effort | Priority |
|---|---|---|---|---|
| R1 | **Live status/novelty sync**: re-fetch erdosproblems.com + `data/problems.yaml` + AI-contributions wiki into `problem_catalog.json`; auto-mark solved/stale; feed `novelty_probe` | Very high (kills the #1 false-positive channel; prunes dead targets) | Low (fetchers exist: `fetch_erdos.py`, `sync_problem_catalog.py`) | **P0** |
| R2 | **Import the upstream decidable/falsifiable/verifiable labels + formal-conjectures coverage into triage**; add a "T2-closable" ranked lane | Very high (creates the first genuinely winnable lane) | Low | **P0** |
| R3 | **Multi-turn EGMRA worker**: N-round branch conversations with lemma admission, failed-approach memory, and regulator-style repair (port legacy prompt discipline into `RunnerWorker`), then **retire the legacy pipeline** — EGMRA becomes the sole production pipeline, with Aristotle as its formal-candidate backend (never a trust root, D-014) | Very high (the core capability gap; ends the two-pipeline split) | High | **P1** |
| R4 | **Fix referee attack semantics**: make `independent_computation`/`proof_reconstruction` conditional on evidence kind (formal-only runs discharge via kernel + independent checker; informal runs *require* a model-driven hostile reconstruction with a distinct lineage); keep fail-closed | High (unblocks honest formal releases; adds real teeth) | Medium | **P1** |
| R5 | **Adopt formal-conjectures Lean statements as locked targets** (pin bench tag; map erdos N → declaration; human correspondence review references the community statement) | High (halves the semantic-risk surface; free independent review) | Medium | **P1** |
| R6 | **Local prover portfolio + distinct lineage**: DeepSeek-Prover-V2/Goedel-Prover-V2 worker for decomposed obligations; also flip `run_continuous --adjudicator deepseek` to default | High (formal capability + legacy gate satisfiable) | Medium-high | **P1** |
| R7 | **One-time salvage import** of gate-surviving legacy candidates' claim ledgers into EGMRA claim proposals + formalization requests — explicitly *not* an ongoing bridge (that would entrench two pipelines; R3 is the path) | Medium (reuses reasoning already paid for) | Medium | **P3** |
| R8 | **Orchestrator-initiated experiments + real enumeration backends** (permit stdlib-only but planned computations; add state-space estimator) | Medium-high (needed for R2 lane) | Medium | **P2** |
| R9 | **Deep literature packets**: per-target packet = forum thread + cited arXiv PDFs (abstract+key theorems), verbatim extracts with hashes; feed full packet, not 160-char titles | Medium-high | Medium | **P2** |
| R10 | **Define the human review workflow** (intent, correspondence, novelty N2, significance S2): reviewer packet format, roster, conflicts, turnaround; wire `expert_reviewed` into `run_five_gates` call | Medium (required for any headline claim) | Low (process, not code) | **P2** |
| R11 | **Calibration loop**: write every terminal outcome to the (currently empty) outcomes ledger; re-fit selector priors; run the Level-6 time-capsule eval that `egmra/eval/` already encodes | Medium (long-term compounding) | Medium | **P3** |
| R12 | **Evolutionary construction search** under exact sandbox fitness for construction-type problems (Sidon/covering/basis) | Medium | High | **P3** |

### 6.2 Sequenced roadmap to a first genuinely verified solve

1. **Week 0–1 (P0):** R1+R2. Deliverable: a truthful target list with a "T2-closable"
   lane; retire solved/stale targets from the queue. No solving capability changed, but
   every downstream claim becomes checkable against a live baseline.
2. **Weeks 1–4 (P1):** R4 (referee semantics) + R5 (formal targets) + R6 (prover
   portfolio). Deliverable: a *live* re-run of the hermetic scenario-4 on a toy-but-real
   theorem (e.g. an already-solved Erdős problem with a formal-conjectures statement),
   producing the system's first authentic end-to-end `ReleaseCertificate`
   (`kernel_checked_encoded_theorem` on a known result — a rediscovery-labeled dry run,
   never marketed as novel).
3. **Weeks 3–8 (P1–P2):** R3 (multi-turn worker — the single-pipeline pivot) + R8 + R9.
   Attack the §5.1/§5.2
   shortlist (after R1 re-validates each pick's openness). Success criterion: one
   T2+I2+N1+S1+R2 release on a genuinely open
   finite-closable statement, then human N2/S2 review (R10).
4. **Months 2–4 (P2–P3):** retire the legacy pipeline once R3 reaches parity (optionally
   running R7 as a one-time salvage of its surviving candidates); #312-lane partial
   results; R11 calibration; only
   then scale worker count (the spec's own P3 ordering, §16).

---

## 7. Risks, false-positive dangers, unknowns

1. **Operator-signed "independence."** All trust keys (event, gate, intent,
   correspondence, policy) are environment HMAC keys typically held by one operator;
   `egmra sign-review` makes self-signing easy (with an honesty note, but no technical
   bar). A single actor can produce I2+F2. Mitigation exists only as process (R10).
   Evidence: `gates.py:60-67`; sign-review CLI (commit 591ab8f).
2. **`novelty_verdict` is asserted, not computed.** N1 is passed by default with no
   logged search (`loop.py:517`); N2 is referee-blocked (good), but a false N1 label is
   live today. R1 + a real logged-search requirement close this.
3. **Wrong-theorem kernel proofs.** A misread statement + self-signed intent +
   model-authored Lean target could yield `kernel_checked_encoded_theorem` for the wrong
   proposition. Paraphrase/mutation intake probes and the triple hash-binding in
   `router._formal_correspondence_valid` (`truth/router.py:137-165`) reduce but don't
   eliminate this; R5 (community-reviewed statements) is the strongest fix.
4. **T5's "independent checker" is not independent yet.** The independent-checker flag
   comes from the same host toolchain (`router.py:200-207`); a `lean4checker`-style
   second trust path is unimplemented. Until then, treat T5 labels as T4.
5. **Rediscovery marketed as novelty** — the dominant realistic failure given the corpus
   staleness and the 2025–26 AI-solve wave (§3.6). Any pre-R1 "novel" claim should be
   assumed false.
6. **Attack-semantics deadlock** (§3.3): if R4 is done carelessly it could *weaken* the
   gate; the change must keep "informal-only ⇒ no release without hostile model
   reconstruction + distinct lineage" fail-closed.
7. **Unknowns:** whether `h(4)` (or any §5 pick) is still open after a live literature
   pass; whether ChatGPT-5.6-in-browser can sustain multi-turn Lean-adjacent work at
   useful quality; Aristotle service quotas/latency at research scale; whether the
   verifiable-class computations fit the sandbox's resource envelope.

---

## 8. Appendix

### 8.1 Repo file/line references (load-bearing)

- `egmra/orchestrator/loop.py` (1536 lines, **uncommitted local modifications**) — 164-256
  (`MechanicalAttackEvaluator` checks), 289-360 (`_execute_finite_experiment`,
  finite-scope boundary), 505-538 (`research()` signature: `novelty_verdict="N1"` at 517,
  `max_iterations=4` at 531), 570 (intent-review gate), 634 (literature packet), 670
  (acquire), 683 (`max_programs`), 757-810 (one-attempt-per-family branch loop), 880
  (OEIS trigger), 918-1150 (claim/evidence/formal admission; `formal_candidates` at 1001),
  1189-1200 (referee diversity: `"mechanical-checks-v1"` at 1193), 1203
  (`attack_evaluator.evaluate`), 1221 (`release_eligible`), 1234 (`run_five_gates` call,
  no `expert_reviewed`), 1310-1319 (promotion, sign, release re-check), 1488
  (`_build_blueprint`), 1521 (`_outcome_label`).
- `egmra/orchestrator/runner_worker.py` (632 lines, **uncommitted local modifications**)
  — 1-21 (epistemic boundaries), 50-64 (schema; `lean_declaration_candidates` at 60),
  259-318 (cold/branch/referee prompts; `branch_prompt` 274-305), 327 (repair attempts),
  338-364 (`for_role`, `_packet_summary` 5×160 chars), 366-375 (`_ask_structured`).
- `egmra/verification/attacks.py` — 7-18 (REQUIRED_ATTACKS); `referee.py` — 20-27
  (independence), 45-53 (`blocks_release`).
- `egmra/release/gates.py` — 91-117 (intent), 119-154 (correspondence), 152-198
  (truth 152 / novelty 160 / significance 167 / reproducibility 176), 241-283
  (`is_novel_autonomous_resolution` 241, `summary_label` 248), 370-488
  (`run_five_gates`, snapshot verification).
- `egmra/truth/router.py` — 110-127 (`_decide_status`), 137-208 (correspondence/formal
  certificate binding).
- `verification.py` — 448-455 & 539-547 (legacy terminal `awaiting_authenticated_release`),
  478-486 (distinct adjudicator lineage requirement).
- `solver_prompts.py` — 9-17 (OFFLINE_POLICY), 43-63 (OUTPUT_CONTRACT), 105-260 (role
  prompts). `literature_research.py` — 1-21. `novelty_probe.py` — 1-25.
- `run_continuous.py` — 143-144, 207-209 (`--adjudicator deepseek`), 52-120 (rerank).
- Status docs: `IMPLEMENTATION_LEDGER.md` (120×VERIFIED), `FINAL_VERIFICATION_REPORT.md`
  §1-§5, `FABLE_AUDIT_REPORT.md` (13/216; §13.6 claim false),
  `FABLE_LEDGER_DISCREPANCIES.md` (claim table), `DECISIONS.md` D-002/D-007/D-011–D-014,
  `SESSION2_PRODUCTION_REACHABILITY_REPORT.md` §1.3/§4.
- Run artifacts: `proof_runs_sol2/problem_312/20260713T063508Z-26cc5e56/manifest.json`;
  `proof_runs_sol2/.done/` (5 markers); `egmra_runs/*.jsonl` (18 logs; last-action census
  14/3/1); `triage/rankings/{current,highest_probability_verified_novel_solution,tractable_frontier,best_finite_computation_targets,highest_probability_lean_verification}.md`;
  `individual/problem_{312,324,336,849,1135,153}.tex`; corpus freshness: 616 files,
  78 mentioning 2026 (this audit's shell census).

### 8.2 Cited external sources

Verified live 2026-07-14:
- T. F. Bloom, Erdős Problem #312 / #324 / #153 pages and forum thread 312,
  erdosproblems.com (312 edited 2026-01-20; 324 edited 2026-04-11).
- S. Korsky, preprint on #312 gap `exp(−c√(K log K))`, arXiv:2607.04157 (July 2026);
  forum summary + method sketch, posts 7183/7392 (author-declared GPT-5.5 assistance;
  criticism in posts 7409-7411); random-sum inspiration credited by the author to
  arXiv:2404.07113. V. Kovač, lower-bound construction, forum post 118 (2025-08-18).
- teorth/erdosproblems README @ commit 8b46f270 (2026-07-09): 1217 problems / 616 open /
  496 formalized / 326 proved / 132 disproved / 9 decidable / 27 falsifiable /
  7 verifiable; "AI Attempts" column.
- "AI contributions to Erdős problems" wiki (final data 2026-06-30, 962 revisions):
  sections 1(a)-1(d), 2(a)-2(d) as excerpted in §4B (e.g. #90 full solutions May 2026;
  #741/#125 DeepMind prover agent full solutions (Lean); #848 Sawhney–Sellke+GPT-5 full
  solution Oct–Nov 2025; #650/#659/#694/#728/#729/#888/#897 solved).
- google-deepmind/formal-conjectures README (Mathlib v4.27.0 pin; bench-v{N} immutable
  tags; AlphaProof misformalization audits) + paper arXiv:2605.13171.
- arXiv math.NT recent listing (2026-07-14) — context on Lean-certified counterexample
  publication practice (e.g. arXiv:2607.09793, kernel-checked ancillary Lean).

Cited from the repo's own research map (`docs/AUTONOMOUS_MATH_RESEARCH_ARCHITECTURE_2026.md`
§2, URLs verified there): Aletheia arXiv:2602.10177 + Erdős sweep arXiv:2601.22401;
QED arXiv:2604.24021; AI Co-Mathematician arXiv:2605.06651; Danus arXiv:2607.06447;
AlphaProof (Nature 2025); Aristotle arXiv:2510.01346 + arXiv:2601.07421; AlphaProof
Nexus arXiv:2605.22763; AXLE arXiv:2606.26442; DeepSeek-Prover-V2 arXiv:2504.21801;
Goedel-Prover-V2 arXiv:2508.03613; OProver arXiv:2605.17283; Seed-Prover 1.5
arXiv:2512.17260; LeanDojo arXiv:2306.15626; LeanSearch v2 arXiv:2605.13137; Beyond
Compilation arXiv:2606.31002; robustness audit arXiv:2606.14867; ProofNet#
(EMNLP 2025); FunSearch (Nature 2023); AlphaEvolve arXiv:2506.13131 + arXiv:2511.02864;
ProofCouncil arXiv:2607.09474 + FirstProof Batch 2 report (1stproof.org); RMA
arXiv:2605.22875.

### 8.3 Web queries/fetches run for this report

1. Fetch erdosproblems.com/312 and /324 — "problem status open solved known results".
2. Fetch erdosproblems.com/forum/discuss/312 — "progress unit fractions subset sums
   close to 1".
3. Fetch github.com/teorth/erdosproblems and github.com/google-deepmind/formal-conjectures
   — "AI progress on Erdős problems solved statistics / formalized statements".
4. Fetch github.com/teorth/erdosproblems/wiki/AI-contributions-to-Erdős-problems —
   "list solved autonomous GPT Gemini Aletheia".
5. Fetch arxiv.org/list/math.NT/recent — "LLM automated theorem proving Erdős problems
   autonomous math research agents 2025 2026" (context scan).
   (An attempted fetch of erdosproblems.com/wiki/index.php/AI_contributions returned
   404; the GitHub wiki above is the canonical page.)

### 8.4 Honest scope limits of this audit

Single-session read-only audit. **Line-number caveat:** `egmra/orchestrator/loop.py`,
`egmra/orchestrator/runner_worker.py`, and `verification.py` carry *uncommitted*
modifications in the working tree (loop.py +182/−61 vs HEAD `591ab8f`); all line numbers
were grep-re-verified against the working tree on 2026-07-14 but will drift again on the
next edit — the named symbols (`MechanicalAttackEvaluator`, `branch_prompt`,
`release_eligible`, …) are the durable anchors. The EGMRA test suite (1071 tests) was
not re-run;
Lean live-verification claims are taken from the repository's own records (commits
ff9edef, 48da500) and prior session memory, not re-executed; external mathematical
status reflects sources fetched 2026-07-14 and the AI-wiki's 2026-06-30 freeze — the
frontier moves weekly, which is itself finding §3.6.
