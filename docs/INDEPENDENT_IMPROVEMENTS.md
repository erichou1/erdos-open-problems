# Independent Improvements

These proposals come from combining repository evidence with first-principles failure analysis. They are not claims of measured performance; each has an explicit falsification path.

## 1. Exact-context outcome learning

### Observation

“Problem difficulty” is not a stable label. A failure belongs to one statement version, pipeline implementation, model portfolio, toolset, budget, and execution. Existing selection systems often pool outcomes too broadly.

### Design

Hash the actual local pipeline sources, not only Git `HEAD`, and require outcome records to match that fingerprint and budget before updating a posterior. Hierarchical sharing across versions is allowed only through an explicit similarity model later.

### Current implementation

[`pipeline_fingerprint()`](../erdos_searcher.py) hashes behavior-defining local pipeline files and runtime, including uncommitted bytes; unrelated Git commits do not change it. Reusable run-contract schema v2 additionally binds the exact research-directive hash, and reusable allocation context includes `allocation_top_k`. The outcome loader has exact fingerprint/run-contract/budget matching, but this release forces every record ranking-ineligible because local replay is not authenticated provenance. Exact-context learning remains a proposal pending that adapter; censored attempts cannot alter counts.

### Falsification

Compare exact-only, Git-commit-only, and pooled predictors on forward-held-out pipeline upgrades. Exact conditioning is rejected if it worsens calibrated selection after accounting for data sparsity.

## 2. Statement mutation covariance

### Observation

Backtranslation and semantic similarity can miss one changed quantifier, domain, number, or operator—the changes most likely to make an open problem easy or vacuous.

### Design

For every proposed formal target, generate a battery of local mutations in the source statement. The corresponding formal target must change in the expected syntactic/semantic region; unchanged formalizations are flagged as insensitive. Pair this with meaning-preserving global paraphrases that should not change the target up to equivalence.

### Current implementation boundary

Current source-question decomposition does not replace the theorem text with a
fragment. Each subproblem card retains the complete parent source statement and
parent hash, and separately hashes a focus question and combined
parent/focus/part contract. All card routes and subproblem targets enter the
bound research directive passed to `ProofPipeline`; they remain search guidance,
not a mutation of the exact parent truth target. Mutation covariance and
independent interpretation approval remain future work.

### Falsification

Measure detection of seeded formalization errors against expert labels and compare to backtranslation alone.

## 3. Proof-debt accounting

### Observation

“Number of proved lemmas” rewards peripheral easy work. Search should value how much uncertainty and unchecked reasoning remains on the path to the exact goal.

### Design

Each Fact Graph node carries proof debt: unverified dependencies, imported theorem risk, statement-fidelity risk, computational coverage debt, and novelty debt. Scheduler reward is reduction in central dependency-cone debt per unit cost, not raw fact count.

### Falsification

Compare time/cost to first verified central progress and final verified outcomes against centrality-only and FIFO scheduling.

## 4. Counterfactual claim admission

### Observation

A plausible false high-centrality fact contaminates many downstream claims. A verifier that only asks “is this proof acceptable?” is vulnerable to confirmation and style.

### Design

Every high-centrality admission spawns a skeptical twin tasked to establish the negation, find the smallest counterexample, identify a missing hypothesis, or produce a nearby-world mutation where the proof fails. Admission requires both positive evidence and a recorded adversarial search outcome. The twin shares the exact claim contract but not the proposer’s narrative.

### Falsification

Seed false lemmas and measure first-error localization, false admission, and downstream revocation cost with/without twins.

## 5. Revocation shadow evaluation

### Observation

Revocation logic is usually tested only after a real mistake, when the graph is already contaminated.

### Design

Periodically shadow-revoke a random accepted nonfinal fact without changing production truth. Compute the predicted dependent closure, invalidated caches, scheduler response, and recovery plan; compare to the actual graph structure. This continuously tests disaster readiness.

### Falsification

The mechanism is useful only if shadow and real revocation closure agree and overhead stays bounded.

## 6. Capability-change revisit policy

### Observation

Permanent dead ends are wrong after a stronger model, new theorem library, fixed statement, or new computation tool arrives. Immediate retries under the same context are wasteful.

### Design

Negative memory records the exact capability vector and an obstruction signature. A problem becomes revisit-eligible when a new pipeline changes a capability plausibly connected to that obstruction. Examples: Lean retrieval upgrade for missing theorem import; improved transfinite reasoning model for an ordinal bottleneck; statement clarification for interpretation block.

### Falsification

Compare useful revisit yield and wasted reruns against fixed cooldown and retry-everything policies.

## 7. Verification-congestion pricing

### Observation

Generating candidates faster than they can be mechanically/expert reviewed creates a persuasive-proof backlog and distorts selection toward cheap generation.

### Design

The allocator prices compute, mechanical verification, and expert review separately. Acquisition value falls when the relevant verifier queue is congested, except for high-significance or fast-falsification jobs. This turns review capacity into an explicit resource.

### Falsification

Measure candidate age, unreviewed backlog, verified yield, and expert hours under priced versus generation-only allocation.

## 8. Cross-problem infrastructure options

### Observation

A failed full proof may still build a reusable formal definition, parser, exact checker, theorem packet, or lemma that unlocks many other problems.

### Design

Treat infrastructure as a real option with a separate posterior and downstream dependency count. Require an executable reuse demonstration before assigning corpus-unlock credit. The searcher already exposes `p_reusable_formal_infrastructure`; measured reuse replaces the current proxy later.

### Falsification

Track actual cross-problem imports and compare predicted versus realized unlocks.

## 9. First-error benchmark from native failures

### Observation

Generic proof benchmarks do not test this project’s dominant failures: statement drift, wrong interpretation, citation misuse, malformed schema, missing cache provenance, and resource-exhausted partials.

### Design

Convert native failed runs into a versioned diagnostic set with the first material error, dependency cone, evidence tier, and repair class. Keep an untouched temporal holdout. Score reviewers on first-error localization, not rhetorical critique volume.

### Falsification

Require improved first-error accuracy on temporal holdout and reduced downstream wasted calls.

## 10. Two-key publication

### Observation

Correctness and research contribution fail independently.

### Design

Publication requires two separate evidence decisions:

- truth decision: correctness + intended-statement fidelity;
- contribution decision: novelty + significance.

The current ledger replays deterministic gate/intent/negative-disposition
evidence against a closed privacy-scanned manifest projection and the exact
required candidate, run-contract, canonical snapshot, source-record, and
statement support. Raw runtime manifests are not copied into public ledger
evidence. Replay proves consistency, not authenticated provenance, so every
event—including deterministic negatives and external human novelty/partial
labels—is forced to `learning_eligible=false` and cannot alter ranking. The
feature flag is off and the closed kind/issuer/adapter-version registry has no
production adapters.
`independent_rediscovery` and `literature_identification` may still supersede an
earlier `verified_novel_resolution` as append-only audit corrections.

A formal proof with an unresolved novelty audit may be published only as a formalization/artifact, never as a solved open problem. A novel computational observation without full proof is labeled partial progress.

### Falsification

Audit false-solved and false-novel rates against a single combined gate.

## Priority

Implement next: statement mutation covariance, claim-level proof debt, counterfactual twins, and executable evidence adapters. Verification-congestion pricing and capability-change revisit require cost/outcome telemetry first.
