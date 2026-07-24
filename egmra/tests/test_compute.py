"""Tests for the compute plane: sandbox isolation, artifacts, replay, backends."""

from egmra.compute import (
    ComputeService,
    ExactArithmetic,
    ExperimentSpec,
    TrustedCertificateChecker,
    check_sat_model,
    reconstruct_unsat,
)

# An experiment that exhaustively checks a finite claim with exact arithmetic.
FINITE_OK = """
def experiment(inputs):
    n = inputs["n"]
    ok = all((k * k) >= 0 for k in range(n + 1))
    return {"result": ok, "coverage": "k in 0..n exhaustive", "checked": n + 1}
"""

# An experiment that finds a counterexample (n not prime).
COUNTER = """
def experiment(inputs):
    def is_prime(m):
        if m < 2:
            return False
        i = 2
        while i * i <= m:
            if m % i == 0:
                return False
            i += 1
        return True
    for n in range(inputs["lo"], inputs["hi"]):
        if not is_prime(n):
            return {"result": "counterexample", "witness": n, "coverage": "scanned range"}
    return {"result": "none"}
"""

NET = """
def experiment(inputs):
    import socket
    socket.socket()
    return {"result": "should not reach"}
"""


def test_sandbox_runs_finite_experiment():
    svc = ComputeService()
    spec = ExperimentSpec(purpose="finite check", inputs={"n": 50}, arithmetic_mode="exact",
                          coverage="k in 0..n")
    job = svc.submit_experiment(spec, FINITE_OK, claimed_classification="exhaustive_finite_subcase")
    assert svc.poll(job) == "done"
    art = svc.artifact(job)
    assert art.output["result"] is True
    assert art.effective_classification() == "exhaustive_finite_subcase"


def test_sandbox_blocks_network():
    svc = ComputeService()
    spec = ExperimentSpec(purpose="net", inputs={})
    job = svc.submit_experiment(spec, NET)
    assert svc.poll(job) == "failed"  # socket blocked -> job fails


def test_float_cannot_claim_exact_classification():
    svc = ComputeService()
    spec = ExperimentSpec(purpose="float", inputs={"n": 5}, arithmetic_mode="float",
                          coverage="range")
    job = svc.submit_experiment(spec, FINITE_OK, claimed_classification="exhaustive_finite_subcase")
    art = svc.artifact(job)
    # float arithmetic mode forces a downgrade away from an exact classification
    assert art.is_downgraded()
    assert art.effective_classification() == "heuristic_numerical"


def test_exact_counterexample_refutes_only_with_exact_mode():
    svc = ComputeService()
    spec = ExperimentSpec(purpose="counter", inputs={"lo": 4, "hi": 10}, arithmetic_mode="exact")
    job = svc.submit_experiment(spec, COUNTER, claimed_classification="exact_counterexample")
    art = svc.artifact(job)
    assert art.output["witness"] == 4
    assert art.refutes()


def test_replay_matches_output_hash():
    svc = ComputeService()
    spec = ExperimentSpec(purpose="finite", inputs={"n": 30}, arithmetic_mode="exact",
                          coverage="c")
    job = svc.submit_experiment(spec, FINITE_OK, claimed_classification="exhaustive_finite_subcase")
    art = svc.artifact(job)
    report = svc.replay(art.artifact_id, environment_label="independent")
    assert report.replayed and report.output_hash_matches


def test_certificate_checker_updates_classification():
    checker = TrustedCertificateChecker(
        checker_id="finite-checker",
        version="1",
        implementation_hash="0" * 64,
        check=lambda a, c: c == {"output_hash": a.output_hash},
    )
    svc = ComputeService(certificate_checkers={checker.checker_id: checker})
    spec = ExperimentSpec(
        purpose="cert", inputs={"n": 5}, arithmetic_mode="exact", coverage="c",
        certificate_kind="finite-output-v1", checker_id=checker.checker_id,
    )
    job = svc.submit_experiment(spec, FINITE_OK, claimed_classification="certificate_checked_lemma")
    art = svc.artifact(job)
    # before checker passes, cannot claim certificate_checked_lemma
    assert art.effective_classification() == "heuristic_numerical"
    report = svc.verify_certificate(
        art.artifact_id,
        checker_id="finite-checker",
        certificate={"output_hash": art.output_hash},
    )
    assert report.passed
    art = svc.artifact(job)
    assert art.effective_classification() == "certificate_checked_lemma"


# ── solver backends ────────────────────────────────────────────────────────────

def test_sat_model_check():
    cnf = [[1, 2], [-1, 2], [-2, 3]]
    assert check_sat_model(cnf, {1: False, 2: True, 3: True})
    assert not check_sat_model(cnf, {1: True, 2: False, 3: True})


def test_unsat_needs_reconstruction():
    # (x) and (-x) is unsat; the empty clause is RUP from these.
    cnf = [[1], [-1]]
    assert not reconstruct_unsat(cnf, None)          # no trace -> testimony only
    assert reconstruct_unsat(cnf, [[]])              # empty clause is RUP -> checked


def test_exact_arithmetic_float_never_proves_exact():
    assert ExactArithmetic.float_proves_exact() is False
    assert ExactArithmetic.interval_contains(
        ExactArithmetic.as_fraction("1/3"), ExactArithmetic.as_fraction("1/2"),
        ExactArithmetic.as_fraction("2/5"))
