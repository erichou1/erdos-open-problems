# Verified Erdős Solver Architecture

## Why the previous pipeline was unreliable

The original pipeline used one very long prompt and accepted the same model's
`PROVED` response as `[solved]`. That combines search, proof construction,
refereeing, and adjudication in one context. It encourages correlated errors,
premature convergence, prompt fatigue, and confidence-based promotion. A fixed
list of twelve attack styles also wastes effort when methods such as transfinite
induction or cardinal arithmetic do not fit the problem.

## Trust boundary

There are three distinct facts and they must never be conflated:

1. **Source status**: what the online Erdős Problems database currently reports.
2. **Candidate result**: what a solver run claims to prove or disprove.
3. **Verified result**: a candidate that passed independent review and the
   deterministic promotion gate.

A candidate result is never named or displayed as solved. Only the gate in
`verification.py` can emit `verified_proved` or `verified_disproved`.

## Pipeline

1. **Normalize**: restate the exact theorem, quantifiers, definitions, and
   admissible background facts. Detect ambiguity before searching.
2. **Lock the statement**: preserve the exact normalized statement and SHA-256
   digest. Every later role must attest to that immutable contract.
3. **Scout independently**: run several isolated scouts with complementary
   mandates (constructive/direct, contradiction/extremal, computational
   falsification, and structure/invariant discovery). Scouts do not see each
   other's output.
4. **Build a validated subgoal DAG**: rank attacks by mathematical fit, unresolved obligations,
   falsifiability, and expected information gain. Do not rank by eloquence.
5. **Construct**: write one auditable candidate with numbered claims, explicit
   dependencies, theorem hypotheses, and a gap ledger.
6. **Verify independently**: use fresh contexts for statement integrity,
   dependency structure, local logic, counterexamples, theorem hypotheses,
   mechanical evidence, and global synthesis:
   - a logical referee checks every inference and dependency;
   - a counterexample referee searches boundary cases and tries to falsify each
     lemma and the final statement;
   - a theorem-hypothesis referee checks every imported result and convention.
7. **Regulate and repair**: an independent regulator chooses proof revision,
   plan revision, or full rewrite. Any material defect returns the proof to the last
   verified claim. The solver must not silently patch around a failed lemma.
8. **Adjudicate**: a fresh context sees the statement, candidate, and referee
   reports but not solver confidence. It produces a structured review record.
9. **Promote deterministically**: all mandatory reviews must pass, all claims
   must be checked, no gap may remain, and proof/completeness/adversarial scores
   must clear configured thresholds. The adjudicator must agree on proof versus
   disproof, every reviewer must attest to the complete claim-ID ledger from a
   unique context, and statement-bound formal, computational, or expert evidence
   must pass. A model cannot override this gate.

## Search policy

All solving prompts explicitly prohibit internet access, browsing, retrieval,
citations as substitutes for proof, and literature-status reasoning. The online
status synchronizer is a separate metadata process and its output is never
included in solver prompts.

Search is broad but adaptive. The solver must consider direct proof,
contradiction, induction/minimal counterexample, extremal arguments,
probabilistic and analytic methods, algebraic transforms, graph/hypergraph
encodings, compactness/local-to-global arguments, computation for discovery or
falsification, and new definitions/invariants **when applicable**. It must also
try stronger/weaker/equivalent formulations and invent new structures when the
standard toolkit fails. Numerical evidence can guide search but cannot close a
proof obligation.

## Operational artifacts

- `solver_prompts.py`: role-separated, offline prompts and the candidate prompt
  used by the existing browser submitters.
- `proof_pipeline.py`: provider-agnostic long-horizon orchestrator that persists
  four scouts, a validated DAG, construction attempts, seven layered reviews,
  regulation, revisions, adjudication, and gate evidence.
- `research_state.py`: immutable statement lock, DAG validation, verified lemma
  memory, failure memory, and attempt history.
- `run_verified_pipeline.py`: executable ChatGPT browser adapter; it creates a
  fresh conversation for every stage and stores the complete audit trail.
- `promote_verified_run.py`: post-run promotion command that binds independent
  evidence to the exact candidate and statement hashes before publication.
- `verification.py`: machine-readable reviews and the sole solved-status gate.
- `sync_problem_catalog.py`: authoritative source-status snapshot.
- `problem_catalog.json`: source status for every online database entry,
  including whether it is reported resolved and its source URL.

The orchestrator runs these roles through an interchangeable `IsolatedRunner`
adapter and persists every stage. Model diversity is preferable where
available, but independent contexts and deterministic gating are mandatory even
when only one model family is available.

The source comparison behind this iteration is recorded in
`HARNESS_RESEARCH.md`.
