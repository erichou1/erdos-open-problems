"""Adversarial referee: independence + obligations-not-score (spec §6.10, §11.1)."""

from __future__ import annotations

from dataclasses import dataclass

from egmra.verification.attacks import AttackReport, AttackResult


@dataclass(frozen=True)
class DiversityProfile:
    """Recorded separately, per §11.1 (fresh conversation IDs are insufficient)."""

    generator_lineages: tuple[str, ...]
    checker_trust_bases: tuple[str, ...]
    replay_environments: tuple[str, ...]
    human_reviewers_and_conflicts: tuple[str, ...] = ()

    @property
    def model_family_independence(self) -> bool:
        # Genuine independence needs distinct generator vs checker lineages.
        return len(set(self.generator_lineages) - set(self.checker_trust_bases)) >= 1 and \
            len(set(self.checker_trust_bases)) >= 1

    @property
    def replay_independence(self) -> bool:
        return len(set(self.replay_environments)) >= 2


@dataclass(frozen=True)
class RefereeResult:
    """A referee's positive result is a set of discharged obligations, not a score."""

    discharged_obligations: tuple[str, ...]
    residual_uncertainty: tuple[str, ...]
    attack_report: AttackReport
    diversity: DiversityProfile
    reports_to: str = "release_auditor"

    @property
    def found_defect(self) -> bool:
        return bool(self.attack_report.defects())

    @property
    def blocks_release(self) -> bool:
        # A single valid central defect blocks; incomplete attack coverage blocks.
        return bool(
            self.found_defect
            or not self.attack_report.complete()
            or self.residual_uncertainty
            or not self.diversity.model_family_independence
        )

    def to_dict(self) -> dict:
        return {
            "discharged_obligations": list(self.discharged_obligations),
            "residual_uncertainty": list(self.residual_uncertainty),
            "defects": [d.attack for d in self.attack_report.defects()],
            "attacks_complete": self.attack_report.complete(),
            "model_family_independence": self.diversity.model_family_independence,
            "replay_independence": self.diversity.replay_independence,
            "reports_to": self.reports_to,
        }


class AdversarialReferee:
    """Organizationally separate; rewarded for finding defects, not agreement.

    The referee cannot repair the proof in the same pass and reports to the
    release auditor, never the research governor (spec §11.1).
    """

    reward_metric = "valid_defects_found_or_documented_replay"

    def __init__(self, *, referee_id: str, diversity: DiversityProfile):
        self.referee_id = referee_id
        self.diversity = diversity
        self._results: list[AttackResult] = []
        self._finalized = False

    def run_attack(self, result: AttackResult) -> None:
        if self._finalized:
            raise RuntimeError("referee report is already finalized")
        if any(existing.attack == result.attack for existing in self._results):
            raise ValueError(f"duplicate attack result {result.attack!r}")
        self._results.append(result)

    def repair(self, *_args, **_kwargs):
        raise RuntimeError("the referee cannot repair the proof in the same adjudication pass")

    def finalize(self, *, discharged: tuple[str, ...] = (),
                 residual: tuple[str, ...] = ()) -> RefereeResult:
        if self._finalized:
            raise RuntimeError("referee report is already finalized")
        self._finalized = True
        return RefereeResult(
            discharged_obligations=discharged,
            residual_uncertainty=residual,
            attack_report=AttackReport(tuple(self._results)),
            diversity=self.diversity,
        )

    def reward(self, result: RefereeResult) -> float:
        """Reward is for valid defects / documented replay, never for agreement."""
        return float(len(result.attack_report.defects())) + (
            0.5 if result.attack_report.complete() else 0.0
        )
