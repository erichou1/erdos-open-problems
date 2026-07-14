"""Risk register (spec §15).

The seventeen general risks and seven innovation-specific risks, each with an
actionable mitigation link and residual uncertainty. Risks whose mitigation is
implemented reference the module that enforces it, so the register is auditable.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Risk:
    risk_id: str
    description: str
    likelihood_impact: str
    mitigation: str
    mitigation_component: str
    residual: str


GENERAL_RISKS = [
    Risk("R01", "wrong formalization proves convenient theorem", "high/critical",
         "interpretation lattice, multi-translation, mutation tests, human target review",
         "egmra.intake, egmra.lean.target_package", "semantic equivalence can itself be hard"),
    Risk("R02", "LLM verifier admits false central fact", "high/critical",
         "evidence-specific validators, kernel/exact replay, revocation",
         "egmra.truth.validators, egmra.truth.revocation", "many research claims lack hard checkers"),
    Risk("R03", "hidden circularity/import dependency", "medium-high/critical",
         "source/dependency graph, proof reconstruction, taint analysis",
         "egmra.verification.attacks", "literature proofs may have opaque dependencies"),
    Risk("R04", "rediscovery marketed as novelty", "high/high",
         "frozen broad retrieval, citation graph, separate novelty audit, experts",
         "egmra.retrieval.service.NoveltyQueryLog", "absence of prior art cannot be proved"),
    Risk("R05", "evaluator/reward hacking", "high-in-evolution/high",
         "independent checker, multi-objective fitness, adversarial tests",
         "egmra.search.algorithms.evolution_allowed", "subtle specification loopholes remain"),
    Risk("R06", "correlated multi-agent consensus", "high/high",
         "tool/model/information independence; no consensus promotion",
         "egmra.agents.profiles, egmra.verification.aggregation", "frontier families may share data"),
    Risk("R07", "branch explosion/nontermination", "high/high",
         "posterior budgets, dedup, pause rules, verification congestion",
         "egmra.search.controller, egmra.control.congestion", "value estimates initially weak"),
    Risk("R08", "problem selector self-reinforces easy domains", "medium-high/medium",
         "protected exploration, hierarchical calibration, domain quotas",
         "egmra.selection.acquisition", "verified outcomes sparse"),
    Risk("R09", "benchmark contamination/saturation", "high/high",
         "rotating/sealed sets, dated snapshots, mutation suites",
         "egmra.eval", "model training data opaque"),
    Risk("R10", "benchmark itself wrong", "medium/high",
         "source/statement versioning, semantic audit, corrections",
         "egmra.corpus.status", "expert benchmarks still contain errors"),
    Risk("R11", "formal proof uses unsafe trust path", "medium/critical",
         "clean environment, axiom/unsafe scan, independent checker",
         "egmra.lean.service, egmra.lean.hardening", "proof-assistant/toolchain bugs possible"),
    Risk("R12", "proprietary service drift/outage", "high/medium",
         "provider abstraction, open baseline, exact version contracts",
         "egmra.agents.runner, egmra.models.registry", "strongest capabilities may stay closed"),
    Risk("R13", "computation irreproducible or numerically unsound", "medium/high",
         "exact arithmetic, containers, seeds, coverage, certificates",
         "egmra.compute", "huge computations strain independent replay"),
    Risk("R14", "literature access/licensing gaps", "medium/high",
         "source provenance, human access, 'unknown' novelty",
         "egmra.retrieval", "no universal full-text corpus"),
    Risk("R15", "malicious source/code/Lean metaprogram", "medium/critical",
         "sandbox, network off, allowlisted imports/tools, minimal TCB",
         "egmra.compute.sandbox, egmra.lean.aristotle_routing", "supply-chain security ongoing"),
    Risk("R16", "persistent memory contamination", "medium/critical",
         "verified-only semantic memory, quarantine, revocation",
         "egmra.learning.memory", "validators can still be wrong"),
    Risk("R17", "communication overstates evidence", "high/high",
         "machine-generated five-gate certificate and fixed vocabulary",
         "egmra.release.certificate, egmra.comms.render", "external summaries may strip caveats"),
]

INNOVATION_RISKS = [
    Risk("I01", "interpretation lattice may multiply search unnecessarily", "-",
         "ablate whether it prevents enough false-target work", "egmra.eval.ablations", "test required"),
    Risk("I02", "cold pass may waste budget or still anchor", "-",
         "ablate 0%, 5%, 10%", "egmra.eval.ablations", "test required"),
    Risk("I03", "posterior branch controller may be worse than best-first", "-",
         "compare vs simple best-first under sparse rewards", "egmra.eval.ablations", "test required"),
    Risk("I04", "risk-weighted Lean sentinels may miss the true subtle step", "-",
         "measure whether sentinels catch real defects", "egmra.eval.ablations", "test required"),
    Risk("I05", "verified-DAG credit may reward useless lemmas", "-",
         "measure downstream unlock, not node count", "egmra.search.verified_debt", "test required"),
    Risk("I06", "cross-problem reuse reward may bias toward library work", "-",
         "measure actual downstream reuse", "egmra.eval.metrics", "test required"),
    Risk("I07", "different-provider verification is not proof independence", "-",
         "record diversity as separate evidenced fields", "egmra.verification.referee", "shared training data"),
]


def all_risks() -> list[Risk]:
    return [*GENERAL_RISKS, *INNOVATION_RISKS]


def risk(risk_id: str) -> Risk:
    for r in all_risks():
        if r.risk_id == risk_id:
            return r
    raise KeyError(f"unknown risk {risk_id!r}")
