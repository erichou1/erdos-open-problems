# EGMRA Independent End-to-End Audit

**Audit date:** 2026-07-14  
**Audit scope:** the checked-out repository, its complete EGMRA specification, production CLI paths, local external dependencies, and fresh runtime executions  
**Final verdict:** **NOT RELIABLY FUNCTIONAL**

## Executive summary

EGMRA is not yet a complete autonomous Erdős-problem solver. It has substantial, unusually careful safety infrastructure: immutable statement records, a typed truth/evidence graph, signed and hash-chained events, scoped computational evidence, release gates, local Lean kernel replay, durable campaign leases, and fail-closed result states. Those pieces are real and many were verified at runtime.

The principal end-to-end path is nevertheless incomplete. In a fresh authenticated browser run on the trivial theorem `∀ n : ℕ, n = n`, the browser model completed structured exploration after a transport repair, but no claim acquired mathematical evidence and the honest result was `OPEN_NO_PROGRESS`. The production loop does not turn natural-language proof steps into independently reviewed informal evidence, does not execute model-proposed falsifiers, does not import retrieved literature through the source-audit/evidence path, and does not run an iterative proof-state-guided Lean repair loop. Most of the sophisticated long-horizon search, checkpoint, theorem-retrieval, and expert-iteration modules are standalone implementations rather than an integrated production research loop.

The audit found and fixed correctness defects rather than merely documenting them. The most severe was that a released finite computation at truth gate T2 rendered `proof_complete: true`, even while its result state correctly said `COMPUTATIONAL_EVIDENCE`. It now renders `proof_complete: false`; only a complete T3 rigorous informal argument or T5/F2 formal result may set it true. Other fixes include stable content-bound ad-hoc problem identities, non-overwriting attempt logs, correct counterexample detection, cycle-safe claim admission, malformed artifact quarantine, worker/verifier crash isolation, honest `OPEN_NO_PROGRESS` classification, browser-safe JSON/source transport, fixture-bound intent review, and actionable computation failure diagnostics.

The final suite collected 1,173 tests with live PostgreSQL enabled and passed. Lean 4.28.0/Mathlib built and a real local kernel replay sealed `True`. Live OEIS and multiple scholarly sources returned data. Live Aristotle was attempted and returned HTTP 401 for the configured credential, so that route is externally blocked. These successes establish that important components work; they do not establish that the combined system can solve and verify even a simple theorem through its primary browser-to-proof path.

## Audit method and evidence standard

I read the two complete normative architecture/specification documents, `DECISIONS.md`, the code implementing every major subsystem, schemas and prompts, and the tests. Earlier summaries, ledgers, test counts, and self-assessments were treated only as navigation aids and were not used as completion evidence.

A requirement is marked:

- **verified** only when code inspection, a behavior-level test, and/or fresh runtime evidence agree;
- **partially verified** when a real implementation exists but the production composition, coverage, or external execution is incomplete;
- **missing** when the specified behavior has no working production implementation;
- **incorrect** when observable behavior violates the requirement;
- **untestable** when an external prerequisite prevented a responsible conclusion.

Passing unit tests alone was never considered sufficient.

## Architecture assessment

The production CLI performs this reduced flow:

1. Resolve and freeze a problem input.
2. Parse two interpretations and run bounded integrity probes when an operator predicate is supplied.
3. Audit locally supplied status claims and build a frozen retrieval packet.
4. Ask a cold-pass model for hypotheses/queries.
5. Select at most three mechanism programs and execute one branch pass for each.
6. Admit syntactically valid claims; execute valid finite experiments; query OEIS for proposed sequences; optionally submit/check Lean candidates.
7. Assemble supported graph nodes, run a mechanical attack evaluator, apply signed gates, and classify the result.

This is a bounded proposal-and-verification loop, not the long-horizon architecture described by the specification. The following distinctions are essential:

- Browser prose and `proof_steps` are retained as problem-local notes, not proof evidence.
- A model-created claim is `PROPOSED`, not proved.
- A finite exhaustive run can establish a finite subcase, not an unrestricted theorem.
- A literature record enters a packet but does not become an imported theorem without source auditing and independent validation.
- An Aristotle `COMPLETE` status is not trusted; only local Lean replay can seal formal evidence.
- Campaign completion means every selected problem reached a terminal workflow status, not that any problem was solved.

## Requirement traceability matrix

Dependencies use `→` to show important downstream consumers. Runtime evidence labels refer to the detailed commands in `EGMRA_VERIFICATION_EVIDENCE.md`.

| ID | Requirement | Implementation | Tests | Dependencies / runtime evidence | Status |
|---|---|---|---|---|---|
| SP-01 | One end-to-end research pipeline | `egmra/cli.py:cmd_run/cmd_campaign`, `orchestrator/triage_source.py`, `orchestrator/loop.py:research` | CLI/triage/orchestrator suites | ranked browser launch B2 | partially verified; legacy drivers retired and triage drains into EGMRA |
| SP-02 | Arbitrary statement/file/Erdős intake | `corpus/sources.py`, CLI resolver | `test_cli_arbitrary.py`, `test_corpus_sources.py` | intake → parser; R1/R4 | verified |
| SP-03 | Immutable, content-addressed input identity | `ProblemInput`, content-derived IDs | corpus/CLI regressions | repeated-run test | verified |
| SP-04 | Preserve distinct attempts and logs | `_new_attempt_id`, per-attempt event log | repeated identical-run regression | R1 | verified |
| SP-05 | Normalize notation without silently changing target | `intake/statement_ir.py` | intake/adversarial tests | parser → contract | partially verified |
| SP-06 | Detect ambiguity/missing hypotheses | dual parser, integrity contract | intake/result-state tests | R3/R4 | verified for recognized patterns; limited coverage |
| SP-07 | Test simple/boundary cases | integrity probes and operator predicate | intake/CLI tests | R2/R3 | partially verified; requires operator predicate |
| SP-08 | Search immediate counterexamples | bounded predicate probe | false-statement regression | R2 found n=3 | verified for executable predicates only |
| SP-09 | Detect equivalent formulations | parser candidates/reformulation records | parser tests | no semantic equivalence E2E | partially verified |
| SP-10 | Distinguish original/weak/strong variants | interpretation/claim hashes | truth graph tests | graph bindings | partially verified |
| SP-11 | Known/open/false/misquoted status audit | `status/*`, corpus claims | status tests | local corpus R4 | partially verified; no live authoritative status synthesis |
| SP-12 | Uncertainty-aware problem prioritization | `selection/*`, searcher rankings, `triage_source.py` | selection/triage tests | B2 reads `current.json` order | partially verified; ranking is a separate build step, not in-loop rerank |
| SP-13 | Erdős database/corpus integration | vendored TeX/catalog resolver | corpus tests | R4/R8 | verified for snapshot; #605 absent |
| SP-14 | OEIS exact and transformed query | `retrieval/oeis.py` | OEIS/property tests | live OEIS L1 | verified as service |
| SP-15 | OEIS offsets/signs/complements/subsequences | transform/query helpers | OEIS tests | not all transforms invoked by loop | partially verified |
| SP-16 | OEIS is conjectural, never proof | evidence router/result gates | adversarial tests | B1 OEIS did not promote | verified |
| SP-17 | Query OEIS when experimental sequence appears | RunnerWorker → loop | production wiring tests | B1 attempted | verified |
| SP-18 | Exact-statement/object/technique literature retrieval | scholarly clients + local index | retrieval tests | L2 | partially verified; mostly lexical query construction |
| SP-19 | Citation graph/author/program retrieval | source record metadata | retrieval tests | no full graph traversal E2E | partially verified |
| SP-20 | Formal-library declaration retrieval | local theorem index/Lean helpers | retrieval/Lean tests | no Mathlib semantic retrieval in run | partially verified |
| SP-21 | Frozen literature packet | `retrieval/packets.py` | packet/provenance tests | loop freezes packet | verified |
| SP-22 | Rank, summarize, check retrieved sources | corpus scoring/packet | retrieval tests | source failures are suppressed | partially verified |
| SP-23 | Provenance for every imported fact | source/evidence schemas | provenance/truth tests | imports not integrated in main loop | partially verified |
| SP-24 | Hallucinated citations fail closed | source auditor/record validation | adversarial retrieval tests | not invoked on branch prose | partially verified |
| SP-25 | Blind pass before literature | cold-pass prompt precedes packet use | production wiring tests | B1 events | verified |
| SP-26 | Mechanism-first, genuinely distinct branches | search programs/role prompts | search/runner tests | max three prompt-prior branches | partially verified |
| SP-27 | Direct/minimal-counterexample/extremal/etc. roles | program catalog and role prompt | search tests | production selects subset | partially verified |
| SP-28 | Separate falsifier/referee incentives | referee prompt/mechanical attacks | runner/referee tests | falsifiers are not executed generally | partially verified |
| SP-29 | Independent retriever agent | retrieval service | retrieval tests | no live agent with branch re-entry | missing |
| SP-30 | Formalization architect/Lean engineer loop | Lean candidate path | Lean/production wiring tests | L3 separate replay only | partially verified |
| SP-31 | Shared typed definitions/claims/evidence state | truth graph + blackboard | extensive graph tests | all runs | verified |
| SP-32 | Claim dependency DAG | `truth/graph.py` | graph/property/adversarial tests | cycle injection F1 | verified |
| SP-33 | Reject circular/unknown dependencies | staged topological admission | new regression | F1 | verified |
| SP-34 | Distinguish formal/informal/unverified/numerical/speculative/false | epistemic lattice/evidence profiles | truth/result tests | R2/R5 | verified |
| SP-35 | Conditional claims and scopes | claim scope/evidence profile | graph/result tests | worker controls non-goal scope | partially verified |
| SP-36 | Contradiction detection | contradiction/reconciliation modules | truth tests | not a rich alternate-model agent | partially verified |
| SP-37 | Revocation cascades through dependents | revocation engine | adversarial truth tests | F2 | verified |
| SP-38 | Stale evidence cannot promote | freshness/certificate checks | result/adversarial tests | F2 | verified |
| SP-39 | Provenance and compute spent per branch | graph/events/budget ledger | orchestrator tests | B1/R5 | verified |
| SP-40 | Best-first/PUCT/beam/MAP-Elites hybrid | `search/*` algorithms | search tests | production loop uses shallow controller subset | partially verified |
| SP-41 | Duplicate approach detection | structural/semantic dedup helpers | dedup/property tests | not applied to production branch proposals | partially verified |
| SP-42 | Compress failed branches into lessons | failure certificate helpers | search tests | not wired to loop/memory | missing in production |
| SP-43 | Pause/terminate/reopen branches | graph statuses/controller helpers | search/graph tests | no long-horizon reopen in main loop | partially verified |
| SP-44 | Depth/breadth allocation and value-of-compute | budget/controller scores | controller tests | fixed max 3 branches/4 iterations | partially verified |
| SP-45 | Scale test-time compute with difficulty | problem scoring/budget object | selection tests | no learned/adaptive production policy | missing in production |
| SP-46 | Python exact computation | restricted subprocess + service | compute/adversarial tests | R5 | verified |
| SP-47 | Reproducible computational artifacts | immutable bundle/replay hashes | compute persistence tests | R5 | verified |
| SP-48 | Independent computation replay | environment-bound replay | compute tests | R5 R2 | verified |
| SP-49 | Label evidence vs finite proof vs full proof | evidence profile/result state | result/adversarial tests | T2 correction R5 | verified after fix |
| SP-50 | SAT/SMT backends | protocol and certificate helpers | unit tests | no configured production solver | missing in production |
| SP-51 | CAS/Sage/Mathematica-equivalent backend | protocols | unit tests | no production backend | missing in production |
| SP-52 | Integer programming/graph enumeration | generic Python only | sandbox tests | no specialized backend | partially verified |
| SP-53 | Automatic conjecture generation | sequence/claim proposals | runner tests | model-only, no validation loop | partially verified |
| SP-54 | Statement-to-Lean translation | model/Aristotle candidate interface | runner/Aristotle tests | external Aristotle 401 | untestable live; partial locally |
| SP-55 | Mathlib lemma retrieval | local theorem index/ReProver-like helpers | Lean retrieval tests | no production semantic retrieval | partially verified |
| SP-56 | Lean-sized subgoal decomposition | `lean/proof_state.py` | proof-state tests | not wired into `research` | missing in production |
| SP-57 | Aristotle submit/poll/download | `lean/aristotle_api.py` | adapter/security tests | L4 returned 401 | untestable with valid credential |
| SP-58 | Harden vendor archive extraction | Aristotle quarantine extractor | adversarial archive tests | local | verified |
| SP-59 | Vendor completion never self-promotes | Aristotle + local replay boundary | Lean tests | L3/L4 | verified |
| SP-60 | Pinned local Lean kernel verification | `lean/service.py`, replay checker | Lean adversarial tests | Lean build and L3 | verified as standalone path |
| SP-61 | Formal correspondence review | correspondence certificate/gates | Lean release tests | no complete live browser→Lean release | partially verified |
| SP-62 | Early formalization of important lemmas | optional branch candidate path | production wiring tests | not scheduled systematically | partially verified |
| SP-63 | Tactic repair from compiler feedback | proof-state helpers | proof-state tests | no iterative production repair | missing in production |
| SP-64 | Claims too costly to formalize get honest status | result taxonomy | result tests | no cost estimator | partially verified |
| SP-65 | Independent adversarial verifier | mechanical attack evaluator/referee | attack tests | same orchestration; not an independent model/tool run | partially verified |
| SP-66 | Quantifier/edge/hidden-assumption attacks | attack names and intake probes | attack/intake tests | evaluator often structural | partially verified |
| SP-67 | Independent recalculation | computation replay | compute tests | R5 | verified for computation |
| SP-68 | Compare informal and formal statements | type/correspondence hashes | Lean release tests | no successful full run | partially verified |
| SP-69 | Detect circular proof | DAG + dependency attack | adversarial tests | F1 | verified structurally |
| SP-70 | Hierarchical verification standards | T/I/F/N/S/R gates | release tests | R5 | verified |
| SP-71 | Never report proved without configured verification | renderer + release gates | result/release regressions | R5/F1 | verified after fix for known paths |
| SP-72 | Temporary vs trusted persistent memory | memory tiers | memory tests | main run records only eligible verified entries | verified |
| SP-73 | Learn only from verified patterns | expert-iteration eligibility | learning tests | no model update/training loop | partially verified |
| SP-74 | Failure-mode library/value learning | learning/search data models | tests | no persistent production trainer | missing in production |
| SP-75 | Signed append-only event log | JSONL/Postgres event stores | event/Postgres tests | R5/R7 | verified |
| SP-76 | Duplicate-event idempotency | event stores | adversarial event tests | F2 | verified |
| SP-77 | Deterministic replay | canonical hashes/event replay | replay tests | model outputs themselves are nondeterministic | partially verified |
| SP-78 | Durable stage checkpoints | `orchestrator/checkpoint.py` | checkpoint tests | explicitly in-memory/not used by `research` | missing in production |
| SP-79 | Resume interrupted work at exact stage | campaign problem-level state | campaign tests | R7 resumes problem terminal state only | missing at stage level |
| SP-80 | Durable leases/fencing/crash recovery | file/Postgres campaign stores | campaign/Postgres tests | R7 | verified at problem-attempt granularity |
| SP-81 | Rate limit waits rather than math failure | BrowserRunner adaptive throttle/retain | browser/campaign tests | provider exhaustion can be immediately re-leased | partially verified |
| SP-82 | Cooldown capped at 120 seconds | throttle clamp | browser tests | B1 no throttles | verified in runner |
| SP-83 | Token/compute/concurrency controls | budget ledger, 1–5 workers | budget/campaign tests | R7 max concurrency 5 | verified for coarse controls |
| SP-84 | Final synthesis cites dependencies/evidence | candidate assembly/release | assembly tests | browser prose not assembled as proof | partially verified |
| SP-85 | Honest partial/no-progress/blocked result | result taxonomy | result tests | R1–R5/B1 | verified after fix |
| SP-86 | Detect malformed JSON and repair | RunnerWorker parser/repair | runner tests | B1 transport | verified |
| SP-87 | Browser rendered-DOM source integrity | fenced JSON + base64 code/source | new transport tests | B1 v1 failure, B1 v2 success | verified after fix |
| SP-88 | Worker/verifier crash isolation | loop exception boundaries | new failure tests | F1 | verified after fix |
| SP-89 | Retrieval failure explicit, not silent | per-call errors for selected client | retrieval tests | aggregate suppresses source errors | incorrect |
| SP-90 | Corrupted state fails closed | HMAC/store integrity checks | adversarial persistence tests | F2 | verified |
| SP-91 | Realistic open-problem run | production CLI/ranked campaign | triage/campaign tests | R4/R7 and ranked browser B2 | partially verified; no proof/research progress established |
| SP-92 | Evaluation suite elementary→open | fixture/eval suites | eval tests | very few research-level hidden-solution cases | partially verified |
| SP-93 | Metrics beyond final accuracy | evaluation metrics models | eval tests | limited live benchmark execution | partially verified |
| SP-94 | Reproducible audit artifacts | events, hashes, reports | verification commands | this audit | verified |

## Defects found and fixes made

### Critical/high-severity correctness fixes

1. **Finite evidence falsely rendered as a complete proof.** A T2 scoped computation produced `proof_complete: true`. `ResearchResult.render` now requires complete assembly and either T3 with rigorous informal review or T5/F2 with formal verification. Regression tests and a fresh fixture run confirm T2 now reports false.
2. **Counterexample masking.** The statement `∀ n ∈ ℕ, n < 3` was parsed as though `n < 3` restricted the domain, preventing discovery of `n=3`. Constraint extraction now accepts only explicit hypothesis/domain cues or direct quantified-domain comparisons. The fresh run returns `CANDIDATE_DISPROOF` with `n=3`.
3. **Browser response corruption.** Rendered ChatGPT Markdown consumed JSON backslash escapes inside Python/Lean source. Branch responses were structurally useful but unparsable. The protocol now requires one fenced JSON object and base64-encoded source fields with strict UTF-8/size validation. A fresh browser run had no JSON parse failures.
4. **False partial progress.** Merely compiling an incomplete target graph counted as `PARTIAL_PROGRESS`. Partial progress now requires at least one supported subclaim. Empty attempts return `OPEN_NO_PROGRESS`.

### Reliability and auditability fixes

5. Ad-hoc inputs formerly shared the literal ID `adhoc-problem`; different statements collided and repeated runs overwrote one event path. IDs are now content-bound and attempts have unique run IDs/logs.
6. Out-of-order and cyclic claim batches formerly raised graph exceptions and aborted a run. Batches are validated and topologically admitted; unknown/cyclic dependencies are quarantined as branch failures.
7. Ordinary worker crashes formerly aborted the whole problem. They are isolated and recorded while other branches remain schedulable. Browser-provider outages retain their special retry semantics.
8. Missing/malformed evidence IDs, non-object evidence, malformed formal candidates, and Lean verifier exceptions formerly could abort the run. They now fail closed per artifact with explicit failure records.
9. External CLI failures such as Aristotle HTTP errors formerly emitted tracebacks. They now return structured JSON errors and nonzero status without exposing secrets.
10. Fixture intent reviews could not bind to fixture interpretation hashes. `sign-review intent` now accepts `--fixture` and resolves the exact fixture input.
11. Failed computation records formerly omitted the sandbox diagnostic. Failure records now distinguish syntax, policy, timeout, and execution errors.
12. The model prompt said only “capability-free Python,” encouraging unsupported `inputs.get` method calls. It now states the exact restricted language boundary and safe builtins.
13. Event logs created by fixture and arbitrary-run CLI paths are now closed reliably in `finally` blocks.
14. Purely formal results formerly could not discharge the referee's independent-computation/reconstruction attacks without an unrelated finite experiment. An admitted, correspondence-bound, attested kernel replay can now discharge those two attacks; informal, unattested, failed-replay, and mixed bad-replay paths remain fail-closed. Twelve semantic regressions cover the boundary.
15. Campaign event run IDs formerly used only `problem_id.fencing_token`; two campaigns over the same problem collided in the global PostgreSQL event store and shared JSONL filename. Attempts are now namespaced by a path-safe hash of the campaign ID. A fresh repeat campaign completed in exactly five runs instead of generating four collision retries.
16. Every campaign exception formerly consumed up to five retries, including a permanently absent corpus entry. The driver now accepts a typed permanent-failure class, and the production CLI marks `SourceResolutionError` terminal after one attempt while preserving retries for ordinary worker crashes.
17. The live asynchronous browser opened project pages at `domcontentloaded` and immediately searched for the React composer. All five tabs raced into “Could not find ChatGPT input box” and consumed 25 attempts. The driver now waits up to 30 seconds for a visible composer and fails explicitly if it never appears; two regressions cover delayed and absent composers. A relaunch reached five concurrent leased first attempts instead of rapid retry failure.

## Representative end-to-end runs

| Scenario | Fresh path | Observable result | Assessment |
|---|---|---|---|
| Trivial theorem | deterministic CLI, `∀n, n=n`, executable probe | `OPEN_NO_PROGRESS`, `proof_complete=false`, 9 signed events | Honest, but discovery cannot prove it |
| Standard known theorem | `fx-true-square` with signed intent and real exact replay | `COMPUTATIONAL_EVIDENCE`, T2/I2/R2, `proof_complete=false` | Correct finite evidence boundary; not a universal proof |
| False statement | `∀n∈ℕ, n<3`, predicate `n<3` | `CANDIDATE_DISPROOF`, counterexample `n=3` | Correct after fix |
| Underspecified | ambiguous sequence statement | `BLOCKED_BY_INTERPRETATION`, 2 events | Correct fail-closed behavior |
| Literature-required | live arXiv/Crossref/Semantic Scholar/MathOverflow probes | real records from three sources; Semantic Scholar 429 omitted by aggregate | Retrieval exists, import/audit integration incomplete |
| Computation-required | finite square fixture | sandbox, immutable artifact, independent replay, T2 release | Component works; universal scope not promoted |
| Lean-required | local `True` declaration in pinned project | Lean/Mathlib build passed; local kernel replay sealed | Standalone formal path works |
| Primary browser theorem | browser ChatGPT, `∀n, n=n` | 19 events, structured branches, experiments/OEIS attempted, `OPEN_NO_PROGRESS` | Transport fixed; no proof/evidence synthesis |
| Open-problem style | Erdős #601 | `BLOCKED_BY_INTERPRETATION` | No mathematical research reached |
| Five-worker campaign | #601–605, PostgreSQL stores | concurrency 5; four blocked; #605 missing and failed once as permanent; 5 total runs | Durable concurrency/namespacing works, research/corpus coverage does not |
| Aristotle formalization | live API submit `Prove True` | HTTP 401 invalid API key, structured error | Externally blocked/unverified |

## Major unresolved risks

1. **No complete informal-proof verification path.** Natural-language proof steps cannot reach T3 because the production loop creates no rigorous independent informal-review evidence from them.
2. **No complete autonomous formal loop.** Model/Aristotle source may be checked, but decomposition, compilation-feedback repair, proof-state search, and correspondence review are not an autonomous integrated cycle.
3. **Search architecture is mostly dormant.** Deduplication, PUCT/MAP-Elites, failure certificates, branch reopening, learned value allocation, and expert iteration are tested modules but are not composed into the production loop.
4. **Stage-level resumability is absent.** The checkpoint object is explicitly local/in-memory and `research` does not restore it. Campaign resume restarts a whole problem attempt.
5. **Retrieved literature is prompt context, not reusable audited mathematics.** Import auditing and source-derived evidence do not feed the production truth graph.
6. **Falsifiers are mostly prose.** Only an operator-provided bounded predicate executes. A branch’s counterexample plan does not drive SAT/SMT/CAS/enumeration automatically.
7. **External solver backends are absent.** SAT, SMT, CAS, and specialized graph/integer-programming layers are interfaces/helpers rather than configured production services.
8. **Scholarly aggregate failures are silent.** A live Semantic Scholar 429 was swallowed while the aggregate returned other sources, violating the requirement to make unavailable sources explicit.
9. **Provider retry scheduling remains incomplete.** Permanent corpus-resolution failures are now terminal and ordinary crashes still retry, but a provider outage can be retained and immediately re-leased after its local pause budget because campaign state has no persisted `not_before` time.
10. **Interpretation approval cannot resolve many parser disagreements.** The intent review is rejected when intake is already release-blocked, so the independent reviewer cannot select a correct parse for some valid statements.
11. **The mechanical attack evaluator remains shallow.** A formal-only proof can now discharge computation/reconstruction through an attested local kernel replay without an irrelevant finite experiment, but most named attacks are still evaluated structurally rather than by an independent mathematical agent.
12. **No successful primary-path proof was observed.** The browser path failed to prove a trivial identity; therefore claims of autonomous open-problem capability are unsupported.
13. **The T2 ranking and source corpus are completely misaligned.** The T2 lane includes decidable/verified problems that are absent from the open-only TeX snapshot. A mechanical resolution check found that all 43 ranked T2 IDs, including #742/#848, raise `SourceResolutionError`; the lane currently cannot drain through EGMRA at all.

## What is genuinely production-usable now

- Safe problem resolution and honest intake triage for covered grammar/predicates.
- Signed, replay-verifiable JSONL and PostgreSQL event storage.
- Durable five-worker campaign leasing/fencing at problem-attempt granularity.
- Restricted exact finite experiments with immutable artifacts and independent replay.
- Fail-closed truth/evidence/revocation/release primitives.
- Browser-based structured proposal generation after the transport repair.
- Standalone pinned local Lean verification of a supplied declaration.
- OEIS and scholarly retrieval clients, subject to the integration gaps above.

## Final verdict

**NOT RELIABLY FUNCTIONAL**

This verdict does not mean the repository is empty or that its safety mechanisms are ineffective. It means the specified end-to-end outcome—autonomously researching, discovering, adversarially checking, formally verifying, resuming, and rigorously reporting difficult Erdős-style mathematics—was not demonstrated and is not fully implemented. The remaining gaps include core architectural composition, not only unavailable credentials.
