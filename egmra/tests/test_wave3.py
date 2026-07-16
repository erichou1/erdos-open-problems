"""Wave 3: warm Lean development service (R5) + AND/OR sketch lane (R4 phase 1).

Pins the trust boundary and the mechanics:

* ``WarmLeanService`` speaks the leanprover-community/repl protocol against
  an injected fake process; restart-once; every failure mode is
  ``WarmLeanUnavailable`` (callers fall open to the cold sealed path).
* The repair loop's DEV PRE-CHECK: a repaired candidate that fails the warm
  development compile never spends a sealed kernel run — its diagnostics
  feed the next repair round instead. Dev service outage = sealed behavior
  unchanged.
* Sketch validation: contract format, tempered parsing (a proved lemma is
  never captured as a child), binder rejection, target-circular children
  rejected, dev compile with sorries expected.
* Nothing in this layer can mint a certificate — reports say so explicitly.
"""

from __future__ import annotations

import json
import threading

import pytest

from egmra.lean.sketch import SketchReport, compile_sketch, validate_sketch
from egmra.lean.warm import (
    DevCheckResult,
    WarmLeanService,
    WarmLeanUnavailable,
    dev_obligation_source,
)
from egmra.orchestrator.loop import research
from egmra.tests.test_gap_closures import (
    TRUE_STATEMENT,
    _corpus,
    _enforcer,
    _FakeFormalizer,
    _FakeLeanService,
    _FormalCandidateWorker,
    _status,
)


# ── fake REPL process ────────────────────────────────────────────────────────

class _FakeStdin:
    def __init__(self):
        self.requests: list[dict] = []

    def write(self, text: str) -> None:
        self.requests.append(json.loads(text))

    def flush(self) -> None:
        pass


class _FakeProcess:
    """Scripted REPL: all responses provided upfront as stdout lines."""

    def __init__(self, response_lines: list[str]):
        self.stdin = _FakeStdin()
        self.stdout = iter(response_lines)
        self.killed = False

    def kill(self) -> None:
        self.killed = True

    def terminate(self) -> None:
        self.killed = True


def _service(*processes: _FakeProcess, **kwargs) -> WarmLeanService:
    remaining = list(processes)
    return WarmLeanService(
        command="fake-repl", cwd=".",
        spawn=lambda: remaining.pop(0), **kwargs)


def test_check_parses_errors_and_sorries():
    process = _FakeProcess([
        '{"env": 0}\n',                                    # header
        json.dumps({"env": 1,
                    "messages": [{"severity": "error",
                                  "data": "type mismatch at foo"},
                                 {"severity": "warning", "data": "unused"}],
                    "sorries": [{"goal": "G1"}, {"goal": "G2"}]}) + "\n",
    ])
    service = _service(process)
    result = service.check("theorem t : True := trivial")
    assert not result.ok and result.sorries == 2
    assert result.messages[0] == "error:type mismatch at foo"
    # protocol: header had no env, check bound the warm environment
    assert "env" not in process.stdin.requests[0]
    assert process.stdin.requests[1]["env"] == 0


def test_clean_check_is_ok_and_pretty_multiline_responses_parse():
    process = _FakeProcess([
        '{"env": 0}\n',
        '{\n', '  "env": 1,\n', '  "messages": [],\n', '  "sorries": []\n', '}\n',
    ])
    result = _service(process).check("def f := 2")
    assert result.ok and result.sorries == 0 and result.messages == ()


def test_restart_once_then_unavailable():
    dead = _FakeProcess([])                                # closes immediately
    alive = _FakeProcess(['{"env": 0}\n', '{"env": 1}\n'])
    service = _service(dead, alive)
    assert service.check("def f := 2").ok                  # survived one restart
    dead2 = _FakeProcess([])
    service2 = _service(dead2, _FakeProcess([]), _FakeProcess([]))
    with pytest.raises(WarmLeanUnavailable):
        service2.check("def f := 2")                       # second failure raises


def test_header_compile_error_is_unavailable_not_a_verdict():
    process = _FakeProcess([
        json.dumps({"env": 0, "messages": [
            {"severity": "error", "data": "unknown package Mathlib"}]}) + "\n",
        json.dumps({"env": 0, "messages": [
            {"severity": "error", "data": "unknown package Mathlib"}]}) + "\n",
    ])
    with pytest.raises(WarmLeanUnavailable):
        _service(process, process).check("def f := 2")


def test_dev_obligation_mirrors_the_sealed_checker():
    source = dev_obligation_source(
        "theorem t : 1 + 1 = 2 := rfl",
        declaration_name="t", expected_type_source="1 + 1 = 2")
    assert "example : 1 + 1 = 2 := @t" in source
    # no obligation appended without an expected type
    bare = dev_obligation_source("def f := 2", declaration_name="f",
                                 expected_type_source="")
    assert "example" not in bare


def test_dev_result_never_claims_authority():
    result = DevCheckResult(ok=True, sorries=0, messages=(), elapsed_seconds=0.1)
    assert "never a formal certificate" in result.to_dict()["authority"]


def test_concurrent_checks_serialize_safely():
    lines = ['{"env": 0}\n'] + ['{"env": %d}\n' % i for i in range(1, 7)]
    service = _service(_FakeProcess(lines))
    results: list[bool] = []
    threads = [threading.Thread(
        target=lambda: results.append(service.check("def f := 2").ok))
        for _ in range(6)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert results == [True] * 6


# ── repair-loop dev pre-check ────────────────────────────────────────────────

class _ScriptedDevService:
    """First N checks fail development-compile, then pass."""

    def __init__(self, fail_first: int = 0, error: Exception | None = None):
        self.fail_first = fail_first
        self.error = error
        self.calls: list[str] = []

    def check(self, source: str) -> DevCheckResult:
        self.calls.append(source)
        if self.error is not None:
            raise self.error
        if len(self.calls) <= self.fail_first:
            return DevCheckResult(ok=False, sorries=0,
                                  messages=("error:unknown identifier 'bar'",),
                                  elapsed_seconds=0.01)
        return DevCheckResult(ok=True, sorries=0, messages=(),
                              elapsed_seconds=0.01)


def _dev_repair_research(tmp_path, *, service, formalizer, dev,
                         repair_rounds, problem_id):
    return research(
        problem_id=problem_id, source_bytes=TRUE_STATEMENT,
        source_id=problem_id, budget=100.0, enforcer=_enforcer(),
        worker=_FormalCandidateWorker(formalizer), goal_claim_id="goal",
        events_path=tmp_path / f"{problem_id}.jsonl",
        retrieval_corpus=_corpus(), status_claims=_status(problem_id),
        lean_service=service, informal_only=False,
        lean_repair_rounds=repair_rounds, dev_lean_service=dev,
        max_iterations=1,
    )


def test_dev_precheck_failure_skips_the_sealed_kernel_run(tmp_path):
    service = _FakeLeanService(fail_first=99)
    formalizer = _FakeFormalizer(sources=(
        "theorem a1 : True := bar", "theorem a2 : True := baz"))
    # Dev call order: 1 = equivalence-bridge attempt (fails -> no bridge),
    # 2 = round-1 repair pre-check (fails -> sealed check SKIPPED),
    # 3 = round-2 repair pre-check (passes -> sealed check spent).
    dev = _ScriptedDevService(fail_first=2)
    result = _dev_repair_research(
        tmp_path, service=service, formalizer=formalizer, dev=dev,
        repair_rounds=2, problem_id="dev-gate")
    # original sealed check + ONE sealed re-check (round 2 only): round 1's
    # candidate failed the dev pre-check and never reached the cold kernel.
    assert len(service.verify_calls) == 2
    assert len(dev.calls) == 3
    assert any(f.startswith("formal_dev_precheck_failed:") and "round1" in f
               for f in result.failures)
    # the dev diagnostics became the round-2 repair feedback
    assert "unknown identifier 'bar'" in formalizer.calls[1]["kernel_feedback"]
    # the bridge attempt carried its own pinned definitional obligation;
    # the round-1 pre-check carried the vendor declaration's obligation
    assert "_egmra_bridge" in dev.calls[0]
    assert "example : True := @erdos_test" in dev.calls[1]


def test_dev_service_outage_falls_open_to_sealed_behavior(tmp_path):
    service = _FakeLeanService(fail_first=1)
    formalizer = _FakeFormalizer()
    dev = _ScriptedDevService(error=WarmLeanUnavailable("REPL died"))
    result = _dev_repair_research(
        tmp_path, service=service, formalizer=formalizer, dev=dev,
        repair_rounds=2, problem_id="dev-outage")
    # identical to the no-dev path: repaired source sealed-checked and passing
    assert len(service.verify_calls) == 2
    repair_reports = [r for r in result.formal_reports if r.get("repair_round")]
    assert len(repair_reports) == 1 and repair_reports[0]["passed"]
    assert not any(f.startswith("formal_dev_precheck_failed:")
                   for f in result.failures)


def test_dev_precheck_rejects_sorried_repairs(tmp_path):
    class _SorryDev(_ScriptedDevService):
        def check(self, source):
            self.calls.append(source)
            return DevCheckResult(ok=True, sorries=1, messages=(),
                                  elapsed_seconds=0.01)

    service = _FakeLeanService(fail_first=99)
    formalizer = _FakeFormalizer(sources=(
        "theorem a1 : True := sorry", "theorem a2 : True := sorry"))
    result = _dev_repair_research(
        tmp_path, service=service, formalizer=formalizer, dev=_SorryDev(),
        repair_rounds=2, problem_id="dev-sorry")
    # no sorried repair ever reached the sealed kernel
    assert len(service.verify_calls) == 1
    assert "sorry placeholders are forbidden" in \
        formalizer.calls[1]["kernel_feedback"]
    assert sum(1 for f in result.failures
               if f.startswith("formal_dev_precheck_failed:")) == 2


# ── sketch lane (R4 phase 1) ─────────────────────────────────────────────────

_TARGET_STATEMENT = ("∀ (K : ℕ), ∃ N, ∀ A : Finset ℕ, "
                     "goodPartition K N A")

_GOOD_SKETCH = """
lemma child_density : ∀ n : ℕ, n ≤ 2 * n := sorry

lemma child_transfer :
    ∀ m : ℕ, m + 0 = m := sorry

theorem erdos_demo : ∀ (K : ℕ), ∃ N, ∀ A : Finset ℕ, goodPartition K N A := by
  intro K
  exact goodPartition_of (child_density K) (child_transfer K)
"""


def _validate(source: str, **overrides) -> SketchReport:
    kwargs = {
        "problem_id": "erdos-demo",
        "target_declaration": "erdos_demo",
        "target_statement": _TARGET_STATEMENT,
    } | overrides
    return validate_sketch(source, **kwargs)


def test_good_sketch_extracts_children_as_obligations():
    report = _validate(_GOOD_SKETCH)
    assert report.problems == () and report.viable
    assert [c.name for c in report.children] == [
        "child_density", "child_transfer"]
    assert report.children[0].statement == "∀ n : ℕ, n ≤ 2 * n"
    obligations = report.to_dict()["obligations"]
    assert obligations[0]["declaration_name"] == "child_density"
    assert obligations[0]["expected_type_source"] == "∀ n : ℕ, n ≤ 2 * n"
    assert "development-only" in report.to_dict()["authority"]


def test_sorried_target_and_missing_target_are_contract_violations():
    sorried = _validate(
        "theorem erdos_demo : ∀ n : ℕ, n = n := sorry")
    assert any(p.startswith("target_is_sorried") for p in sorried.problems)
    missing = _validate("lemma only_child : ∀ n : ℕ, n = n := sorry")
    assert any(p.startswith("target_declaration_missing")
               for p in missing.problems)
    assert not missing.viable


def test_proved_lemma_is_never_captured_as_a_sorried_child():
    source = (
        "lemma proved_one : ∀ n : ℕ, n = n := fun n => rfl\n\n"
        "lemma real_child : ∀ n : ℕ, 0 ≤ n := sorry\n\n"
        "theorem erdos_demo : ∀ n : ℕ, n = n := fun n => rfl\n"
    )
    report = _validate(source)
    assert [c.name for c in report.children] == ["real_child"]


def test_binder_form_children_are_rejected_by_contract():
    source = (
        "lemma bad_child (n : ℕ) : n ≤ 2 * n := sorry\n\n"
        "theorem erdos_demo : ∀ n : ℕ, n = n := fun n => rfl\n"
    )
    report = _validate(source)
    assert any(p.startswith("child_has_binders:bad_child")
               for p in report.problems)


def test_target_equivalent_children_are_rejected_as_circular():
    source = (
        "lemma sneaky : ∀ (K : ℕ), ∃ N, ∀ A : Finset ℕ, "
        "goodPartition K N A := sorry\n\n"
        "theorem erdos_demo : ∀ (K : ℕ), ∃ N, ∀ A : Finset ℕ, "
        "goodPartition K N A := sneaky\n"
    )
    report = _validate(source)
    assert report.rejected_children == ("sneaky",)
    assert any(p == "all_children_rejected_as_circular"
               for p in report.problems)


def test_compile_sketch_expects_the_sorries_and_fails_open():
    report = _validate(_GOOD_SKETCH)

    class _Dev:
        def check(self, source):
            return DevCheckResult(ok=True, sorries=2, messages=(),
                                  elapsed_seconds=0.05)

    compiled = compile_sketch(report, _GOOD_SKETCH, _Dev())
    assert compiled.compiled is True and compiled.dev_sorries == 2
    assert compiled.viable

    class _Mismatch:
        def check(self, source):
            return DevCheckResult(ok=True, sorries=5, messages=(),
                                  elapsed_seconds=0.05)

    mismatch = compile_sketch(report, _GOOD_SKETCH, _Mismatch())
    assert any(m.startswith("sorry_count_mismatch") for m in mismatch.dev_messages)

    class _Dead:
        def check(self, source):
            raise WarmLeanUnavailable("gone")

    dead = compile_sketch(report, _GOOD_SKETCH, _Dead())
    assert dead.compiled is None
    assert any("dev_service_unavailable" in m for m in dead.dev_messages)
    assert dead.viable            # unavailability is not a rejection


def test_failed_dev_compile_makes_the_sketch_nonviable():
    report = _validate(_GOOD_SKETCH)

    class _Broken:
        def check(self, source):
            return DevCheckResult(ok=False, sorries=0,
                                  messages=("error:unknown identifier",),
                                  elapsed_seconds=0.05)

    broken = compile_sketch(report, _GOOD_SKETCH, _Broken())
    assert broken.compiled is False and not broken.viable


# ── sketch CLI ───────────────────────────────────────────────────────────────

def test_sketch_cli_validates_against_the_community_target(tmp_path, capsys):
    from egmra.cli import main

    targets = tmp_path / "targets"
    targets.mkdir()
    (targets / "erdos-312.lean").write_text(
        "import Mathlib\n\n"
        "theorem erdos_312 : ∀ (K : ℕ), ∃ N, partitionProperty K N := sorry\n")
    sketch_path = tmp_path / "sketch.lean"
    sketch_path.write_text(
        "lemma step_one : ∀ K : ℕ, K ≤ K + 1 := sorry\n\n"
        "theorem erdos_312 : ∀ (K : ℕ), ∃ N, partitionProperty K N := by\n"
        "  intro K; exact partition_of (step_one K)\n")
    out_path = tmp_path / "report.json"
    rc = main(["sketch", "--erdos", "312", "--sketch-file", str(sketch_path),
               "--targets-dir", str(targets), "--output", str(out_path)])
    assert rc == 0
    report = json.loads(capsys.readouterr().out)
    assert report["problem_id"] == "erdos-312"
    assert report["target_declaration"] == "erdos_312"
    assert [c["name"] for c in report["children"]] == ["step_one"]
    assert report["compiled"] is None          # no REPL configured
    assert report["viable"] is True
    assert json.loads(out_path.read_text())["source_hash"] == report["source_hash"]


def test_sketch_cli_requires_a_community_target(tmp_path, capsys):
    from egmra.cli import main

    empty = tmp_path / "targets"
    empty.mkdir()
    sketch_path = tmp_path / "sketch.lean"
    sketch_path.write_text("theorem erdos_312 : True := trivial\n")
    rc = main(["sketch", "--erdos", "312", "--sketch-file", str(sketch_path),
               "--targets-dir", str(empty)])
    assert rc != 0
    assert "no community Lean target" in capsys.readouterr().err
