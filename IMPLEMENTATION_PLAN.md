# EGMRA Implementation Plan

Implements `docs/AUTONOMOUS_MATH_RESEARCH_ARCHITECTURE_2026.md`. Each milestone
lists the requirement IDs it satisfies (see `IMPLEMENTATION_LEDGER.md`).

## Repository structure (new `egmra/` package)

```
egmra/
  __init__.py
  provenance/        hashing, stage identity, provenance rules       REQ-012,020b,064
  policy/            signed feature policy + central enforcement      REQ-020g,140
  truth/             epistemic graph plane                            REQ-004,029,060-065,031
    entities.py      Problem/Interpretation/Claim/Branch/Evidence/certs
    events.py        append-only event log + signatures
    graph.py         EpistemicGraph store (SQLite + JSONL events)
    views.py         materialized derived views (manifest projection)
    validators.py    evidence-kind validators
    router.py        evidence router dispatch
    revocation.py    invalidate_evidence / refute_claim / SCC
    blackboard.py    least-privilege claim-graph slices
  intake/            module A                                         REQ-002,021,040,020m
    statement_ir.py  typed IR + dual parse + reconciliation
    interpretation.py interpretation lattice
    probes.py        integrity/boundary/mutation/counterexample probes
    contract.py      ProblemContract
  corpus/            status hygiene                                   REQ-050
  retrieval/         module D                                        REQ-023,043,053-055
    records.py       TheoremRecord, PremiseCandidate
    packet.py        frozen SourcePacket
    service.py       LiteratureQuery + retriever + import auditor
    premises.py      theorem/premise retrieval (local index)
    source_priority.py claim-specific priority matrix
  oeis/              module C                                        REQ-042,051,052
    transforms.py    typed transform registry
    client.py        read-only OEIS HTTP client (mockable)
    matching.py      match ranking + held-out verification workflow
  compute/           module H                                        REQ-008,047
    spec.py          ExperimentSpec
    artifact.py      ComputationalArtifact + 6-way classification
    sandbox.py       sandboxed python backend
    service.py       submit/poll/artifact/replay/verify_certificate
    backends.py      SAT/SMT/CAS/ILP adapter interfaces
  lean/              module I                                        REQ-048,090-09A,007
    service.py       Lean service API + FormalCertificate + GoalCapsule
    target_package.py L0
    sentinels.py     L1 + risk-weighted selection
    blueprint.py     L2 AND/OR formal blueprint (quarantine)
    proof_state.py   L3 portfolio + PUCT + diagnostics routing
    sync.py          L4 informal<->formal
    hardening.py     L5 axiom closure/whitelist/second checker
    missing_library.py REQ-098
    coverage.py      F(c) + expensive-claim policy
    aristotle_routing.py REQ-09A
  search/            module G                                        REQ-005,006,046,080-088,163
    mechanism.py     mechanism fingerprint
    archive.py       MAP-Elites QD archive
    blueprint.py     AND/OR claim blueprint + verified debt
    verified_debt.py debt definition (frozen)
    dedup.py         6-stage duplicate cascade
    failure.py       failure certificates
    bands.py         compute bands 0-5
    controller.py    posterior EU + VOI + PUCT + pause/reopen
    programs.py      12 research-program families
    algorithms.py    Thompson/UCB/AO*/PUCT routing
  agents/            module E                                        REQ-024,044,020k
    authorities.py   7 durable authorities
    profiles.py      dispatchable method profiles + diversity
    prompts.py       compact role prompt specs
    runner.py        model-runner protocol + attested identity
  verification/      module J                                        REQ-009,027,110-113
    referee.py       independent referee (obligations not score)
    attacks.py       10 required attacks + taint
    standards.py     T0-T5 + I/F/N/S/R/autonomy
    aggregation.py   pessimistic aggregation + conflict flow
  release/           five gates                                      REQ-001,011,026,070,114
    gates.py         intent/truth/novelty/significance/replay
    certificate.py   ReleaseCertificate + signature
    compiler.py      proof compiler from admitted claims
    policy.py        promotion policy (kernel+intent+correspondence)
  selection/         module B                                        REQ-022,041,081
    features.py      9 feature families
    posterior.py     competing-risk posterior + censoring
    acquisition.py   A_p score + Thompson + protected exploration
  learning/          module K                                        REQ-010,04A,065,020i
    memory.py        6 memory stores
    calibration.py   calibration ledger
    expert_iteration.py verified-only iteration
  control/           control plane                                   REQ-020c,08A,162,164,165
    leases.py        leases/heartbeats
    throttle.py      provider-aware backoff (Retry-After+jitter+120s)
    parallel.py      parallel/serialize policy
    recovery.py      failure recovery table
    congestion.py    verification-congestion pricing
  comms/             communication plane                             REQ-166
    human.py         intervention log + steering
    render.py        five-gate rendering (no confidence %)
  orchestrator/      top-level                                       REQ-003,032,063,089,143
    loop.py          research() main loop (17 steps)
    checkpoint.py    checkpoint/resume
    roles.py         runtime role layout
  eval/              evaluation                                      REQ-130-135,145
    levels.py protocol.py metrics.py progress.py ablations.py stats.py
    datasets/        fixtures + manifests
  services.py        service-interface protocols                     REQ-04B
  design_status.py   machine-readable design-status table            REQ-033
  topology.py        service topology registry                       REQ-160
  models/registry.py model registry + local bake-off                 REQ-161
  risks.py           risk register                                   REQ-170
  cli.py             command-line interface
  config.py          configuration + secrets handling
  tests/             pytest suite for all of the above
```

## Data models & schemas
- Truth entities from spec §10.1 (`egmra/truth/entities.py`): dataclasses with
  explicit multidimensional `evidence_profile`, typed relations as first-class
  edges. Serialized to canonical JSON (reuse `run_contract.canonical_json`).
- Event schema §10.3 with signature; append-only JSONL + SQLite index.
- `ProblemContract`, `TheoremRecord`, `PremiseCandidate`, `SourcePacket`,
  `ExperimentSpec`, `ComputationalArtifact`, `FormalCertificate`, `GoalCapsule`,
  `IntentCertificate`, `FormalCorrespondenceCertificate`, `ReleaseCertificate`.

## Orchestration flow (§5.2 / §7.9)
`research(problem_source, budget)`: freeze → IR → lattice → probes → status →
cold pass (5%) → frozen packet → acquire → graph+archive+blueprint → controller
loop (frontier → dedup+price → posterior actions → execute → validate → append
events → revoke+reopen → update) → compile → referee → five gates → distill.

## Agent roles (§6.5)
7 authorities: research governor, intake/retrieval, program workers,
computational falsifier, formalization authority, adversarial referee, release
auditor. Method profiles dispatched conditionally; diversity requires ≥2 axes.

## Model-provider abstraction (§14.2)
`agents/runner.py` `ModelRunner` protocol + `AttestedModelIdentity`. Local
`DeterministicRunner` for tests; real providers behind adapters requiring keys.

## Retrieval & literature (§6.4/§8)
Local TF-IDF + formula/type index over a bundled corpus; TheoremRecord with
verbatim extract + provenance; import auditor; separate novelty query log.
Real web/citation-graph retrieval behind an interface (documented cred command).

## Formal verification (§9)
Reuse `lean_verify.py` kernel replay; add axiom/import/placeholder scan, target
type-check, correspondence certificate. Real `lake build` requires Lean install
(documented); local tests use injected runners + fixture projects.

## Persistence / observability / security / config
- Persistence: SQLite + append-only JSONL events + content-addressed artifact store.
- Observability: event-derived dashboard projection + structured logging + tracing spans.
- Security: sandbox policy (network off, RO mounts, bounded resources), secrets via
  env only, no secret in logs/artifacts.
- Config: `egmra/config.py` layered (defaults → file → env), signed feature policy.

## Testing strategy
Pytest under `egmra/tests/`. Unit tests per module; integration test for M1 slice;
20 acceptance tests (§13.6); eval-harness tests. External calls mocked/injected.
Keep existing `tests/` green.

## Deployment strategy
`egmra/cli.py` entry points; `egmra/topology.py` documents service layout; M2
interfaces (Postgres/containers) implemented with local backends + documented
production commands.

## Milestones (dependency-ordered)
- **M0** (REQ-140,020g,012,090,020,020h,061,062): feature policy + stage identity +
  reject vendor COMPLETE + append-only events + evidence precedence + telemetry;
  patch existing pipeline. Regression tests.
- **M1** (REQ-141 + all of §6 core): truth plane, intake, retrieval, OEIS, compute,
  Lean iface, search/control, agents, verification, release, selection, learning,
  orchestration loop, eval harness, 20 acceptance tests.
- **M2** (REQ-142,160-165): scale interfaces + local backends (Postgres iface,
  containers iface, more provers, concurrency, congestion pricing).
- **Eval & docs** (REQ-130-135,145,170,033,161): evaluation harness, datasets,
  risk register, design-status, model registry, FINAL_VERIFICATION_REPORT.md.
