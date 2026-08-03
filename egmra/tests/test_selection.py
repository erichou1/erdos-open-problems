"""Tests for the selection plane: features, competing-risk posterior, acquisition."""

from egmra.selection import (
    CompetingRiskPosterior,
    ProblemFeatures,
    ProblemSelector,
    acquisition_score,
)


def test_posterior_censors_timeouts():
    post = CompetingRiskPosterior()
    post.observe("timeout", censored=True)
    post.observe("rate_limit")
    # censored data does not increment no_progress
    assert post.alpha["no_progress"] == 0.5
    assert post.censored == 2


def test_posterior_updates_and_expected_value():
    post = CompetingRiskPosterior()
    for _ in range(5):
        post.observe("novel_full")
    ev = post.expected_value({"novel_full": 10.0, "no_progress": 0.0})
    assert ev > 0
    # wide interval when few observations
    assert post.credible_width() > 0


def test_acquisition_penalizes_ambiguity_and_stale_status():
    clear = ProblemFeatures("p1", ambiguity_count=0, last_status_review="2026-07-01",
                            reuse_probability=0.5, expected_cost=1.0)
    ambiguous = ProblemFeatures("p2", ambiguity_count=4, last_status_review="",
                                reuse_probability=0.5, expected_cost=1.0)
    post = CompetingRiskPosterior()
    for _ in range(3):
        post.observe("verified_partial")
    s_clear = acquisition_score(clear, post)
    s_ambig = acquisition_score(ambiguous, post)
    assert s_clear.score > s_ambig.score
    assert s_ambig.penalties > 0


def test_protected_lane_adds_uncertainty_bonus():
    f = ProblemFeatures("p1", expected_cost=1.0)
    post = CompetingRiskPosterior()  # weak prior -> high SD
    exploit = acquisition_score(f, post, protected_lane=False)
    explore = acquisition_score(f, post, protected_lane=True)
    assert explore.numerator >= exploit.numerator


def test_selector_reserves_exploration_and_excludes_malformed():
    sel = ProblemSelector(protected_fraction=0.2, seed=1)
    good = [
        (ProblemFeatures(f"p{i}", expected_cost=1.0, prior_attempts=i,
                         reuse_probability=0.3), CompetingRiskPosterior())
        for i in range(5)
    ]
    malformed = (ProblemFeatures("bad", number_of_parts=0), CompetingRiskPosterior())
    picks = sel.select(good + [malformed], k=4)
    assert "bad" not in picks
    assert len(picks) == len(set(picks)) <= 4


def test_hard_constraints_exclude_only_malformed():
    sel = ProblemSelector()
    ok, _ = sel.hard_constraints_ok(ProblemFeatures("p", number_of_parts=2))
    assert ok
    bad_ok, reason = sel.hard_constraints_ok(ProblemFeatures("p", number_of_parts=0))
    assert not bad_ok and "malformed" in reason
