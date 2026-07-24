# Lean Integration Specification

Status: designed, not enabled. No Lean or Lake binary was installed in the audited workspace on 2026-07-12. [`config/pipeline_features.json`](../config/pipeline_features.json) therefore keeps `lean_execution` false.

## Purpose

Lean is an evidence and search environment, not a universal rewrite of the research system. Initial integration should target high-centrality, high-risk leaves and exact finite certificates where faithful formalization is practical. Natural-language discovery and literature work remain necessary.

## Trust claims kept separate

Every formal artifact reports three independent decisions:

1. **Formal validity**: the pinned Lean kernel accepts the exact declaration under the allowed axiom policy.
2. **Statement fidelity**: independent review supports that the formal declaration represents the intended informal claim.
3. **Research status**: independent literature/expert review supports novelty and significance.

No single decision implies the other two.

## Pinned environment

The first executable milestone must create a dedicated `formal/` project containing:

```text
formal/
  lean-toolchain
  lakefile.toml or lakefile.lean
  lake-manifest.json
  Erdos/
    Statements/
    Lemmas/
    Certificates/
  Main.lean
  README.md
```

Each certificate binds:

- Lean version;
- Mathlib Git commit;
- Lake manifest hash;
- imports and options;
- exact elaborated theorem expression;
- source statement and statement-contract hashes;
- proof source hash;
- allowed/trusted axiom policy;
- `#print axioms` output;
- clean-build and independent-replay logs.

Dependency versions must be explicit; “latest” is prohibited for evidence.

## Formalization-fidelity gate

Before proof search:

1. Generate at least three independent formalization candidates when feasible.
2. Compile candidates only as a syntax/type filter.
3. Prove pairwise equivalence or implication differences where Lean can express them.
4. Backtranslate each target; treat similarity as evidence, not proof.
5. Test global paraphrase invariance.
6. Test local mutation covariance: numbers, operators, quantifiers, hypotheses, domains, and conclusions must change correspondingly.
7. Run vacuity probes, satisfiability/example construction, and negated-target attempts.
8. Obtain independent target review for the selected declaration.
9. Freeze a content hash of the approved target.
10. Invalidate and revoke every dependent proof if that hash changes.

Materially ambiguous source statements remain `BLOCKED_BY_INTERPRETATION`; a convenient formalization may not silently choose a branch.

## Agent interface

The formal service exposes typed operations:

```text
check_declaration(source, imports, options)
get_goals(source, declaration)
apply_tactic(state_id, tactic)
verify_proof(statement_hash, target, proof)
print_axioms(declaration)
attempt_formal_negation(target)
extract_dependencies(declaration)
minimize_imports(source)
replay_certificate(certificate_id)
```

Provider adapters may use local Lean, Pantograph, LeanDojo, or AXLE for interactive work. Final evidence always replays in a clean pinned local environment. A hosted `okay` or compilation response is not final evidence.

## Goal cache

Cache key:

```text
Lean version
+ Mathlib commit
+ Lake manifest hash
+ imports
+ options
+ elaborated local context
+ exact target expression
+ trusted-axiom policy
```

Cache values may include successful proofs, formal negations, tactic segments, dependency slices, cost, and value estimates. Every successful cache hit is replayed through the current kernel before admission. Textual goal strings and theorem names alone are unsafe keys.

## Blueprint and scheduling

The formal blueprint is an AND-OR dependency graph:

- AND nodes require every dependency;
- OR nodes represent alternative sufficient strategies;
- each node binds an informal claim, formal target hash when available, dependencies, evidence tier, proof debt, centrality, and status;
- workers claim only currently open leaves;
- disproved or corrected nodes cascade-revoke dependents;
- successful nodes survive local replanning;
- no `sorry`, `admit`, undeclared unsafe axiom, or target-changing edit may cross the merge gate.

The scheduler prioritizes central leaves with high uncertainty, high expected proof-debt reduction, and affordable verification, while preserving alternative branches.

## Evidence adapter

Formal evidence is accepted only through:

```text
prepare → execute → audit → clean replay
```

The adapter emits raw stdout/stderr, command, environment hashes, declaration identity, proof/target/source hashes, axiom list, and replay result. It fails closed on missing toolchain, timeout, unsafe imports/metaprograms, `sorry`, signature mismatch, target drift, or replay disagreement.

## Initial milestones

1. Install and pin Lean/Mathlib in a feature branch; no research claim.
2. Replay one existing trusted Mathlib theorem and one deliberately invalid theorem in CI.
3. Formalize a tiny source-faithful lemma from an Erdős card, not a full open theorem.
4. Add statement mutation tests and axiom audit.
5. Connect one high-centrality leaf to the Fact Graph evidence tier.
6. Compare no-Lean versus Lean-assisted cost/time/false-positive metrics.
7. Enable `lean_execution` only after clean replay works on a fresh CI machine.

## Rollback

Lean is an optional route. Disabling it leaves natural-language and exact-computation routes available, retains formal artifacts as immutable evidence, and marks affected facts `FORMAL_EVIDENCE_UNAVAILABLE` rather than deleting them. No cached formal result remains admitted after toolchain/hash mismatch.
