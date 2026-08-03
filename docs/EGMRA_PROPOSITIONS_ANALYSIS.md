# Analysis of the EGMRA Effectiveness & Efficiency Report's Propositions

**Date:** 2026-07-15
**Analyst scope:** every recommendation (R1–R13) in
[EGMRA_EFFECTIVENESS_AND_EFFICIENCY_REPORT.md](EGMRA_EFFECTIVENESS_AND_EFFICIENCY_REPORT.md),
judged against the actual code at `11d6161`, the live-run telemetry gathered
this week, and the system's real binding constraints.
**Method:** (1) verify every factual premise the recommendation rests on by
reading the cited code; (2) judge expected effect against the *binding
constraint* (a single throttle-serialized ChatGPT account — model calls are the
scarcest resource, kernel time second, Aristotle tasks third); (3) check the
proposal preserves the trust invariants; (4) estimate effort and regression
risk from the affected modules' maturity.

---

## 0. Premise verification (done before any verdict)

The report's credibility rests on five factual claims. I checked each in the
checked-out code rather than trusting the report:

| # | Report claim | Verified? | Evidence |
|---|---|---|---|
| P1 | Duplicate cold pass: `runner.run(stage="cold_pass")` then `worker.cold_pass()` runs the model again | **TRUE** | [loop.py](../egmra/orchestrator/loop.py) ~L1106: `runner_cold = runner.run(...)` followed ~10 lines later by `cold_output = worker.cold_pass(...)`. The first response is only folded into packet `techniques` as raw text. |
| P2 | Branch-selection model call is ignored | **TRUE** | `"Select among branch mechanisms: ..."` response is recorded, then `direct_first` / `controller.select_posterior_actions` decide. The model's answer never affects selection. |
| P3 | First-three-family prefix bias | **TRUE, with nuance** | `METHOD_FAMILIES` order confirmed: `direct_structural, contradiction_minimal_counterexample, extremal_invariant, …`; `instantiate_programs` truncates `families[:max_programs]` (≤3). Nuance the report misses: for *unclassified* domains only `{any}`-fit families survive the filter, so the first three become `direct, contradiction, computational_finite_reduction` — which is why live runs did show computational branches. Also `contradiction_minimal_counterexample` maps to the **skeptic** role, so refutation-first is partially reachable today. But for classified domains, `computational_finite_reduction`, `formal_library_first`, and `counterexample_model_construction` are indeed **unreachable** — the experimentalist and formalizer roles never run there. This is a real, live selection bug. |
| P4 | Controller feedback is goal-level only | **TRUE** | `controller.update_posterior(branch_id, success=supported, …)` where `supported` is the goal claim's status. A branch that proved a decisive child lemma but not the goal scores identically to one that produced nothing. |
| P5 | All cited file paths exist | **TRUE** | Checked all seven load-bearing citations (`compute/backends.py`, `truth/graph.py`, `search/verified_debt.py`, `search/mechanism.py`, `lean/proof_state.py`, `release/gates.py`, `search/controller.py`) — every one exists. The report did not fabricate integration points. |

The telemetry (§3.2: 235 runs, 390 branches, 171 claims, 2 evidence
attachments, 5 outcomes) is consistent with what I observed live this week
(the "hundreds of branches, almost no admissible evidence" funnel is exactly
the shape of the v3/v5/shared campaigns). Its central inference is correct
and important: **formal verification throughput is not the current
bottleneck — almost nothing reaches verification.** Search quality is.

**Overall report quality: high.** Premises check out, trust boundaries are
respected throughout, and the "do not do" list (don't replace Lean, don't
weaken trust, don't add static reviewers) is exactly right. My disagreements
below are about *sequencing, cost accounting on a browser-only budget, and
what already exists*.

---

## 1. Verdict summary

| Rec | Title | Verdict | Why in one line |
|---|---|---|---|
| R1 | Remove duplicate/ignored model calls | **ADOPT (P0)** | Verified waste of 2 serialized browser calls per problem; trivial fix |
| R2 | Fix mechanism-family selection | **ADOPT (P0)** | Verified prefix bias silences 3 of 4 worker roles on classified domains |
| R13 | Cost + yield instrumentation | **ADOPT (P0)** | Right that it gates everything else; ~40% already exists to extend |
| R3 | Claim graph drives dynamic waves | **ADOPT-PHASED (P1)** | Correct diagnosis; full ObligationScheduler is too big a bite — phase it |
| R5 | Warm local Lean development service | **ADOPT (P1)** | Real bottleneck (minutes/check); biggest engineering lift; prerequisite for R4/R6's full value |
| R4 | Formal-native AND/OR lane | **ADOPT AFTER R5 (P1)** | Highest ceiling for the 20 problems with community Lean targets |
| R6 | Aristotle value-aware escalation | **ADOPT-MODIFIED (P1)** | Cheap dispatch gate now; full ladder only makes sense once R5 exists |
| R9 | Auditable retrieval re-entry | **ADOPT (P1)** | Re-entry plumbing already exists unused; corroboration-by-identity is right |
| R7 | Narrow prompt contract | **ADOPT-MODIFIED (P1/P2)** | Right diagnosis, wrong cost model for a browser-only budget — needs a cheap API extractor |
| R8 | Adaptive inference-time compute | **ADOPT-LITE (P2)** | Half already exists; encode the stop rules, skip the framework |
| R12 | Precise human escalation | **ADOPT (P2)** | Cheap renderer over state that already exists |
| R11 | Reconstructed symbolic backends | **ADOPT-SCOPED (P2)** | Real for finite leaves; start SAT + exact arithmetic; defer proof-log checking |
| R10 | Mechanism library | **DEFER-PARTIAL (P3)** | Right idea, speculative retrieval; take the cheap half now |

Nothing in the report warrants outright rejection. Two proposals need
material modification (R6, R7); one deferral (R10).

---

## 2. Per-recommendation analysis

### R1 — Remove duplicate and ignored model calls — **ADOPT (P0)**

**Premise:** verified true (P1, P2 above).
**Genuine improvement?** Yes, unambiguously. On the binding constraint this
is the purest win available: two frontier calls per problem-attempt that
produce either duplicated or unused output. On the throttled single account,
each call is minutes of serialized wall-clock *plus* throttle pressure; over
a 25-problem campaign with retries, this is on the order of **50–100 wasted
browser generations** — hours of the scarcest resource.
**Caveats the report underweights:**
- `runner_cold.text` currently feeds the packet's `techniques` (retrieval
  input). Removal changes packet composition; the replacement must feed
  `cold_output.search_queries`/`falsifiers` (already richer) or retrieval
  recall regresses. The report's acceptance test ("no reduction in retrieval
  recall") covers this — keep that test.
- The exchange cache already amortizes these calls across crash-retries, but
  attempt-salted resamples re-pay them. So the saving recurs per resample —
  the fix compounds with `--requeue-promising`.
**Effort:** hours. **Risk:** low (fixtures pin decisions).

### R2 — Correct mechanism-family selection — **ADOPT (P0)**

**Premise:** verified true with the nuance in P3.
**Genuine improvement?** Yes — this is quietly the highest
effectiveness-per-effort item in the report. Concretely, on classified
domains the current code **never runs** the experimentalist
(`computational_finite_reduction`), formalizer (`formal_library_first`), or
model-construction skeptic families. That directly contradicts three
investments already made: the ErdosBench finding that finite computation is
the highest-yield track, the `--targets-dir` work (formal-library-first is
exactly the lane community Lean targets reward), and the skeptic role. The
report's stratified wave (one prove / one refute-or-construct / one tool
route) is the correct fix and matches the role design already in
`WORKER_ROLE_BY_FAMILY`.
**Addition from live data:** family selection should also consult
formal-target availability (choose `formal_library_first` when
`targets/<id>.lean` exists) and predicate availability (choose
`computational_finite_reduction` when a probe predicate exists) — both
signals are already in scope at selection time.
**Effort:** 1–2 days (selection layer only; QD archive already exists).
**Risk:** low-medium — changes which branches run, so outcome distributions
shift; the acceptance tests (deterministic per seed, materially different
mechanisms) are the right guardrails.

### R3 — Claim graph drives dynamic work waves — **ADOPT-PHASED (P1)**

**Premise:** verified true (static work set; open subgoals collected but
never scheduled; P4 confirms coarse credit).
**Genuine improvement?** Yes in direction — this is the DeepSeek-Prover-V2
recursive-decomposition pattern and the single biggest architectural gap
between EGMRA and systems that solve hard problems. The 44/51/57-event runs
in the telemetry are exactly the runs that generated subgoals and had
nowhere to put them.
**But the full `ObligationScheduler` as specced is a rewrite of the loop's
middle third** — new scheduling state, budget integration, lease semantics,
checkpoint schema, and event actions, layered on the most safety-audited
file in the repo. Big-bang risk is high.
**Phased adoption:**
1. *(days)* Promote worker `open_subgoals` into new branch programs within
   the existing `max_iterations` budget — the controller, leases, and
   diversity archive already handle "another branch"; only program
   *generation* is new. One-verb task framing (the report's design rule)
   fits the existing role prompts.
2. *(week+)* Obligation-level controller credit: update posteriors from
   supported child claims / refutations / salvage, not just the goal (fixes
   P4 with a contained change to the post-branch update).
3. *(later)* Full obligation graph with content-deduped scheduling, blocked
   conditions, and crash-resume — only after 1–2 prove out.
**Risk if skipped:** the funnel stays "hundreds of branches → 2 evidence."

### R4 — Formal-native AND/OR proof lane — **ADOPT AFTER R5 (P1)**

**Premise:** true — the loop verifies candidates but never uses Lean to
validate a *decomposition* before spending on children.
**Genuine improvement?** Yes, with the highest ceiling of any proposal — a
compiling parent sketch turns "model prose says these lemmas suffice" into a
machine-checked dependency relation, which composes perfectly with the
existing correspondence certificates and the lemma library (children land
there and compound). Scoped correctly: only the ~20/25 problems with
community Lean targets qualify today.
**Hard dependency the report acknowledges but underplays:** compiling
sketches with `sorry` placeholders requires a development-grade compile
path; the pinned checker (rightly) rejects `sorry`. Without R5, every sketch
compile costs a cold Mathlib load, and the iterative sketch-repair loop that
makes this lane work is uneconomical. **Sequence strictly after R5.**
The acceptance tests (development artifacts can never pass a release gate;
ancestor-equivalent children rejected — note this needs *more* than the
existing token-Jaccard circularity check, since Lean-level equivalence can
survive rewording) are the right trust guardrails.
**Effort:** 1–2 weeks after R5. **Risk:** medium; contained to a new lane.

### R5 — Warm local Lean development service — **ADOPT (P1, biggest lift)**

**Premise:** true — every kernel interaction is a stateless `lake env lean`
with a fresh Mathlib load (~1–2 min observed). The verdict cache (already
built) removes *repeat* cost but does nothing for *iteration* — and
iteration is how proofs actually get written.
**Genuine improvement?** Yes — this is the difference between ~30
proof-repair iterations/hour and ~1–2. Every serious neural-prover system
(ReProver, DeepSeek-Prover, AxProverBase per the report's review) is built
on a warm REPL. It also unlocks R4 and gives R6 its "local development"
rung.
**Trust analysis:** the report gets the boundary exactly right —
explicitly non-authoritative, final seal unchanged through the pinned
checker. The acceptance test "a malicious development process cannot mint a
formal certificate" is already structurally guaranteed (certificates require
the checker's HMAC key), which makes this *safe* to adopt despite its size.
**Honest cost:** the biggest engineering item in the report — a new
long-lived process to manage (health, restarts, environment identity for
cache keys, memory ceilings on a laptop already running Chromium + lake).
Recommend LeanInteract/Pantograph spike first; wrap it in the same
fail-open-to-cold-check pattern used everywhere else.

### R6 — Aristotle value-aware escalation — **ADOPT-MODIFIED (P1)**

**Premise:** partially true. The report is right that dispatch is
value-blind, but the current state is better than it implies: obligation
dedupe, 5-slot account cap, failed-dispatch slot release, repair rounds, and
formal-target pinning all already exist.
**Genuine improvement?** The *dispatch gate* — yes. Aristotle tasks run
30–90+ min; spending one on a peripheral or already-refuted claim is the
third-scarcest resource wasted. A cheap gate is implementable **now** with
existing signals: (a) candidate's claim is in the goal's dependency cone,
(b) branch not refuted at dispatch time, (c) correspondence-stable when a
cert exists, (d) not already in flight (exists). The *full six-rung ladder*
— not yet: rungs 1–3 (deterministic tactics, warm loop, cheap formal models)
don't exist; building the ladder before its rungs inverts the dependency.
Adopt the gate now; grow the ladder as R5/R11 land.
**The "Aristotle prompt package" sub-proposal** (send verified helpers,
exact errors, forbidden mechanisms) is cheap, compatible with the existing
repair-round plumbing, and worth doing immediately.

### R7 — Narrow the frontier-model prompt contract — **ADOPT-MODIFIED (P1/P2)**

**Premise:** true — the branch schema demands 14 output categories per
response, and the "touch everything shallowly" failure mode is visible in
live transcripts (many broad claims, few decisive artifacts).
**Genuine improvement?** Directionally yes, **but the report's cost model is
wrong for this deployment.** Its two-step design (strong model does math,
"cheap extraction step" normalizes) assumes a cheap second model exists. On
the browser-only budget, a second serialized ChatGPT call per round would
*halve* throughput — a regression, not an optimization. Modified adoption:
- Single-verb obligation prompts make sense **only where R3-phase-1 provides
  single-verb tasks** — adopt them there.
- The extraction step must run on a **cheap attested API model**
  (`deepseek-api` — the key already wired) or not at all. If the user wants
  strictly browser-only, keep the schema tail but *shorten it* (the report's
  own "additional rules" list — constraints first, dependency cone only,
  drop confidence — is adoptable today for free).
- The report's A/B acceptance test (artifact rate, tokens per accepted
  artifact) is the right way to settle it — run it before committing.

### R8 — Adaptive inference-time compute — **ADOPT-LITE (P2)**

**Premise:** partially true — the report under-credits what exists:
pass@k-with-memory (`--requeue-promising` + attempt-salt + dossiers),
stagnation stop + one reframe, provider-outage salvage, budget ledger, and
per-family posteriors are all live. What's missing is the *escalation*
direction (spend more on hot obligations) and some stop rules (repeated
proof states — which needs R5's goal-state visibility; theorem-strength
equivalence — needs more than token overlap).
**Genuine improvement?** Modest and real, but as *policy over existing
knobs*, not a new subsystem. Encode: budget/round escalation for problems
with recorded progress signals (mirror of the requeue-promising test), and
the cheap stop rules. Skip the "framework" framing. The GPT-5.6-specific
list is mostly already implemented (items 3,4,7,8 exist verbatim in the
codebase) — evidence the report didn't fully audit what's built.

### R9 — Auditable retrieval re-entry + real corroboration — **ADOPT (P1)**

**Premise:** verified true on both counts — `SourcePacket.reentry()` exists
with exactly the right semantics (versioned, linked, reason-required) and
nothing calls it; corroboration is `≥0.5` token overlap + two distinct
*hosts*, and mirrored sources genuinely defeat it.
**Genuine improvement?** Yes. The mid-run refocus shipped this week re-ranks
the *frozen* packet, which helps only if the needed theorem was retrieved at
freeze time; a new-subgoal query can't be answered. Re-entry closes that
while preserving auditability (parent hash, trigger, negative coverage — the
report's record schema is right). Corroboration-by-identity (DOI/arXiv id,
authorship, citation lineage) over corroboration-by-host is a real
correctness fix to an existing weakness, not just an improvement.
**Caveats:** live scholarly fetches mid-run add network fragility to
browser runs — make re-entry fail-open (a failed fetch is a note, never a
failure) and rate-bounded per problem. The full "applicability artifact"
with hypothesis maps is the expensive half; adopt the packet re-entry +
identity-corroboration first, hypothesis maps opportunistically.
**Effort:** ~2–4 days for the valuable half.

### R10 — Mechanism library — **DEFER-PARTIAL (P3)**

**Premise:** true (lemma library stores Lean declarations; procedural memory
stores coarse family outcomes; no mechanism-level layer).
**Genuine improvement?** Eventually, but this is the most speculative
proposal: "retrieve mechanisms by mathematical structure and obstruction" is
an unsolved retrieval problem dressed as a schema, and the transfer evidence
(one problem's mechanism cracking another) doesn't exist yet in this corpus
— there are 5 outcomes total. The honest cheap half: **tag** dossier entries
and lemma-library records with mechanism metadata (invariant, transformation,
obstruction) at write time, so the corpus accumulates *now* and the
retrieval layer can be built when there's something to retrieve. The
transfer-credit rule (credit only after executable/formal reuse) is
excellent and should be kept whenever this lands.

### R11 — Reconstructed symbolic backends — **ADOPT-SCOPED (P2)**

**Premise:** true — the sandbox is capability-free pure Python; there is no
SAT/SMT/CAS path, and finite leaves are exactly where ErdosBench found the
highest yield.
**Genuine improvement?** Yes for the right subset. Scoping matters:
- **Adopt first:** PySAT/Kissat (finite propositional leaves) and exact
  integer arithmetic via Python-native tooling — witness/model checking is
  cheap and fits the existing "independent replay" pattern verbatim
  (`solver testimony is not evidence until its witness is checked` is
  already the sandbox's rule).
- **Defer:** UNSAT proof-log checking (DRAT/LRAT checker integration is its
  own project — until then, UNSAT results are only *search guidance*, never
  evidence; this asymmetry must be explicit), interval-arithmetic analytic
  certificates (heavy), and **reject Mathematica** (unattestable
  closed-source oracle with licensing — contradicts the reconstruction
  principle the report itself states).
- Every backend enters through `compute/backends.py` + the router's
  existing evidence vocabulary — the cited integration points are correct.

### R12 — Precise human escalation — **ADOPT (P2)**

**Premise:** true — expert input today is the S2 certificate; there is no
structured "ask a human the one blocking question" artifact.
**Genuine improvement?** Yes, cheap: every field in the
`ExpertEscalationPacket` already exists in machine state (dossier, graph,
failed approaches, refuted routes, formal target, literature extracts) — 
this is a *renderer*, roughly `egmra escalation-packet --erdos N`. The
guardrails (input becomes an event/obligation, never a certificate; no
repeat escalation without new evidence) match the existing out-of-band
review discipline. Given one operator-mathematician is in the loop anyway
(you), this converts stalls into single concrete questions instead of
transcript archaeology. 

### R13 — Instrument cost and mathematical yield — **ADOPT (P0)**

**Premise:** mostly true, with material under-crediting: exchange records
already persist provider/model identity/stage/prompt+response hashes;
outcome ledger has state/gate/salvage; the calibration report aggregates
by-state/by-problem; the verdict cache and exchange cache expose hit/miss.
**Genuine improvement?** Yes — the *missing* pieces are exactly the ones
that would have caught this week's problems faster: `decision_used` per call
(would have flagged R1's ignored selector immediately), tokens/duration per
call, per-formalization dispatch→seal funnels, and the yield ratios
(verified sublemmas per 100 calls). The report's "P0 because it gates every
later decision" is correct — R2/R7/R8's acceptance tests are unmeasurable
without it. Implement as extensions of the existing records (exchange
transcript fields + a `egmra yield-report` aggregator), not a new system.
**One push-back:** don't block R1/R2 on R13 — those two are
premise-verified already; land them in parallel.

---

## 3. Recommended adoption sequence (dependency-corrected)

The report's own ordering is close but misses two dependencies (R4→R5,
R6-ladder→R5) and treats already-built pieces as new. Corrected:

**Wave 1 (days, pure win):** R1 + R2 + R13-core (decision_used, per-call
tokens/time, yield-report command). No new trust surface.
**Wave 2 (week):** R3-phase-1 (subgoal→branch promotion) + R6 dispatch gate
+ R9 packet re-entry with identity corroboration + R12 escalation packets.
**Wave 3 (weeks):** R5 warm Lean service → then R4 AND/OR lane on the 20
target problems → R6 full ladder rungs as they exist. R3-phase-2
(obligation-level credit).
**Wave 4 (opportunistic):** R7 A/B with an API extractor, R8 stop/escalate
policies, R11 SAT + exact backends, R10 mechanism tags.

**Standing constraints for every wave** (all consistent with the report):
never weaken the pinned-kernel/certificate boundary; development artifacts
can never reach a release gate; every new cache/service fails open to the
authoritative cold path; every change lands with the report's acceptance
tests against a frozen fixture set.

---

## 4. Bottom line

The report's central thesis — **strong trust architecture, weak search
engine; make the claim graph generate work instead of running a fixed
three-branch script** — is correct, and its two P0 findings (R1, R2) are
verified bugs with immediate, cheap fixes worth roughly *hours of wasted
browser time per campaign* and the un-silencing of three of the four worker
roles. The deepest structural items (R3, R4, R5) are genuinely the right
direction and match the external evidence (DeepSeek-Prover-V2, ReProver,
AxProverBase), but must be phased: R5 before R4, R3 incrementally inside the
existing loop.

The two places the report needs correction: **R7's two-call design is a
throughput regression on a browser-only budget** (adopt only with a cheap
API extractor, or as prompt-slimming), and **R6/R8 under-credit machinery
that already exists** (dedupe/caps/salvage/requeue-promising/salt) — the
remaining value there is a dispatch gate and stop rules, not new frameworks.
R10 is the only proposal whose core bet (structure-based mechanism
retrieval) isn't yet supported by evidence in this corpus; take its cheap
half and defer the rest.
