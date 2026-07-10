# Research Harness Review — July 10, 2026

This iteration compared the repository against the newest reproducible and
published mathematical-agent architectures. The solver remains strictly
offline; these sources informed harness design only.

## Primary sources

- [AI Co-Mathematician](https://arxiv.org/abs/2605.06651): persistent state,
  asynchronous workstreams, uncertainty and failed-hypothesis tracking.
- [Aletheia](https://arxiv.org/abs/2602.10177): generator–verifier–reviser loops
  and the observed danger of satisfying a technically convenient but unintended
  interpretation of an Erdős problem.
- [QED](https://arxiv.org/abs/2604.24021) and its
  [open implementation](https://github.com/proofQED/QED): immutable problem
  comparison, decomposition, structural-before-detailed verification, and a
  regulator that chooses proof revision, plan revision, or full rewrite.
- [LEAP](https://arxiv.org/abs/2606.03303): informal blueprints decomposed into
  smaller formal units with repeated compiler feedback.
- [A Minimal Agent for Automated Theorem Proving](https://arxiv.org/abs/2602.24273):
  evidence that iterative refinement, context management, and tool feedback
  provide most of the reproducible value without excessive orchestration.
- [Evaluating SageMath-Augmented LLM Agents](https://arxiv.org/abs/2607.06820):
  current evidence that exact CAS feedback improves research-derived
  mathematical problem solving.

## Implemented conclusions

1. The exact source statement is normalized, SHA-256 locked, and included in
   every stage. Every reviewer must attest to the same digest.
2. Planning produces JSON subgoals whose identifiers, dependencies, centrality,
   and acyclicity are validated by code before proof construction begins.
3. Independent reviewers are layered by failure mode: statement integrity,
   structural dependencies, local logic, counterexamples, theorem hypotheses,
   mechanical evidence, and global synthesis.
4. A rejected candidate is not a terminal artifact. Its exact gaps and errors
   enter persistent failure memory, then an independent regulator selects
   `REVISE_PROOF`, `REVISE_PLAN`, or `REWRITE` before another isolated attempt.
5. Only a fully passing attempt enters verified-lemma memory. Model agreement
   alone still cannot bypass the deterministic promotion gate: promotion also
   requires a hashed formal-proof, exact-computation, or expert-review artifact
   bound to the locked statement and claimed direction.

## Deliberate exclusions

- Literature retrieval is not exposed to solving agents because this project
  requires offline first-principles proof search. Online source status remains a
  separate provenance catalog.
- Formal checking is required as a dedicated review lane and recorded as
  evidence, but universal Lean formalization is not assumed feasible. Future
  adapters can attach Lean, SageMath, SAT/SMT, or exhaustive-search artifacts to
  specific DAG nodes.
- Branch count is fixed initially; subsequent compute is allocated through DAG
  centrality, bottleneck flags, and regulator feedback rather than blind retries.
