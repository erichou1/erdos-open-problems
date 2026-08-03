# Risk Register

Scales: likelihood and impact are Low/Medium/High/Critical. Residual risk assumes listed controls, not perfect execution.

| ID | Risk | Likelihood | Impact | Current evidence | Control / detection | Residual | Owner / gate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R01 | Wrong source corpus membership | Medium | High | Baseline 25 missing + 6 extras | First-party snapshot, exact set audit, CI block | Low | Searcher/source gate |
| R02 | Source theorem text parsed incorrectly | Medium | Critical | Regex extraction can include remarks | Hash raw page; dedicated content block parser; future theorem-level diff | Medium | Statement contract |
| R03 | Wrong interpretation presented as solution | High | Critical | 601 ambiguity; Aletheia/Danus failures | Branch audit, human/independent intent approval, blocked status | Medium | Intent key |
| R04 | Formal target does not match intended theorem | High | Critical | Current fidelity studies show compile/meaning gap | Multi-candidate formalization, mutation covariance, equivalence, independent review | Medium | Lean fidelity gate |
| R05 | False proof passes LLM reviewers | Medium/High | Critical | Same-family/context independence only | Claim evidence tiers, counterexample twins, formal/exact replay, expert audit | Medium | Truth key |
| R06 | Formal proof uses unsafe axioms/metaprograms | Medium | Critical | AXLE trust caveat | Pinned clean environment, allowlist, `#print axioms`, independent replay | Low/Medium | Formal adapter |
| R07 | Evidence record is label-trusted, self-issued consistency is mistaken for provenance, or support leaks private run state | Medium today | Critical | Closed privacy-scanned audit replay; shared classifier recomputes negatives; schema/runtime force all events ranking-ineligible; external adapter registry is empty | Keep all events audit-only; retain workflow transaction through ledger fsync; implement authenticated typed adapters | Low for ranking, high before any learning/promotion | Promotion gate |
| R08 | Correct result falsely labeled novel | Medium | Critical | Prior Axiom/Aletheia/Erdős corrections | Independent theorem-level novelty search and expert contribution key | Medium | Novelty key |
| R09 | Resource exhaustion treated as solved/done | Previously certain | High | Five legacy markers | Verified-only skip, normalized disposition, regression tests | Low | Run status |
| R10 | Censored run becomes negative training label | Medium | High | Initial MVP weak penalty found | Censoring regression; contextual ledger schema | Low | Searcher model |
| R11 | Outcome from old pipeline contaminates new predictor | High without binding | High | Git-only identity insufficient for local edits | Local source fingerprint + budget filter | Low/Medium | Outcome loader |
| R12 | Probability numbers appear calibrated | High | High | Weak priors and sparse outcomes | Mandatory uncalibrated label; evaluation gate before v2 | Medium | Communication plane |
| R13 | Selector collapses domain diversity | Medium | Medium/High | Many tied/formal cards | Diversified queue, protected exploration, domain metrics | Medium | Allocator |
| R14 | Prize/popularity/formalization leakage drives ranking | Medium | Medium | Easy shortcut temptation | Separate features/ablations; no single-feature promotion | Low/Medium | Evaluation |
| R15 | Worker duplicate execution | Medium | High | Baseline had no claims | Atomic claims now; add leases/heartbeats/campaign stress test | Medium | Scheduler flag remains off |
| R16 | Stale claim prevents future retry | High in current experimental queue | Medium/High | Claims survive completed rejection | Campaign IDs, capability-change revisit, lease expiry | High until fixed | Scheduler enable gate |
| R17 | Rate-limit loop opens idle chats or over-backs off | Medium | Medium | Earlier workers; early reset bug | Shared adaptive limiter, complete-response reset, 120s cap, telemetry pending | Medium | Browser runner |
| R18 | Infinite rate-limit wait masks provider outage | Medium | Medium | Rate limits intentionally do not consume proof retries | Provider-health/outage classification and operator alert; no proof abandonment | Medium | Operational policy |
| R19 | Cache replays changed/stale prompt | Previously high | High | Baseline text-only cache | Prompt/response hashes and metadata v2 | Low/Medium | Cache |
| R20 | Cache context provenance fabricated/lost | Previously high | Critical for independence | Problem 782 resume failure | Persist/restore URL; legacy review cache regenerated | Low | Review gate |
| R21 | Partial/torn state accepted after crash | Medium | High | Baseline non-atomic writes | Atomic cache files; append-only event store still pending | Medium | Persistence |
| R22 | Malformed model schema consumes entire budget | High | Medium | 724 replan and role/result failures | Deterministic parser, validation, bounded repair (pending for all stages) | Medium | Structured output |
| R23 | Reviewer prompt injection from candidate/source | Medium | High | Model text is untrusted | Delimiters, explicit untrusted instructions, separate contexts, structured parser | Medium | Prompt boundary |
| R24 | Browser UI/model changes silently alter pipeline | High | High | Model/version unrecorded | Persist model UI identity/config, canary tests, exact fingerprint | High until telemetry | Model adapter |
| R25 | Secrets/context URLs committed | Low/Medium | Critical | Runtime dirs ignored; tracked subset exists | Closed evidence projection, byte-level private-content scans before persistence and on read, transactional failed-admission rollback, release secret scan, artifact allowlist, synthetic test URLs, no blanket `git add` | Low/Medium | Release checklist |
| R26 | Large generated snapshots bloat repository | Medium | Medium | Triage tens of MB | Snapshot retention policy, hashes/manifests, Git LFS/external object store if needed | Medium | Data governance |
| R27 | Test suite passes but browser workflow fails | High | High | Unit tests use fakes; UI mutable | Recorded fixtures/canary, one bounded manual E2E, durable diagnostics | High until E2E |
| R28 | Python/dependency drift breaks reproducibility | Medium | Medium | Open lower bounds; 3.9 claim wrong | Correct floor, CI matrix, lock dependencies/browser version | Medium | Build/release |
| R29 | Fact Graph amplifies one false high-centrality fact | High if added | Critical | Danus case studies | Evidence-tier admission, skeptical twin, revocation, random expert audits | Medium | Fact Graph flag |
| R30 | Revocation misses cached/derived consumers | Medium | Critical | Not implemented | Content-addressed dependency index, shadow revocation, invariant tests | Medium | Fact Graph gate |
| R31 | Evolution exploits evaluator or target drift | High | Critical | MaxProof reward hacking; formal vacuity risk | Multi-objective hard evaluator, frozen target, adversarial audit, sandbox | Medium/High | Experimental flag |
| R32 | Expert-review bottleneck overwhelms throughput | High | High | Research validation is expensive | Verification-congestion pricing, triage, high-centrality review, report queue age | Medium | Allocator |
| R33 | Published legacy candidate labels are mistaken for proofs | High | Critical | 43 `candidate-proved` filenames | Prominent archival disclaimer; migrate to evidence-tiered board | Medium | Communication migration |

## Immediate stop-ship risks

Do not enable automatic theorem publication, Fact Graph truth admission, Lean evidence promotion, or continuous five-worker scheduling until R07, R15/R16, R24, and the relevant replay/revocation controls meet their migration gates.
