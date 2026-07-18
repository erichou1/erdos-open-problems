"""Tests for verification hardening adopted from the strongest public
Lean-verification records (Kerger zero-order-bounds repo, 2026-07):
broadened escape-hatch source scan, --trust=0 kernel replay, and recorded
formalization divergences."""

from __future__ import annotations

from types import SimpleNamespace

from egmra.lean.aristotle_api import hash_quarantine_tree
from egmra.lean.kernel_checker import run_kernel_check
from egmra.lean.service import native_findings
from egmra.lean.sketch import validate_sketch


# ── broadened escape-hatch scan (production-source scan parity) ──────────────

def test_native_findings_flags_escape_hatch_declarations():
    assert any("axiom" in f for f in native_findings("axiom bad : 1 = 2"))
    assert any("opaque" in f for f in native_findings("opaque magic : Nat"))
    assert any("partial" in f for f in native_findings("partial def loop : Nat → Nat := loop"))
    assert any("unsafe" in f for f in native_findings("unsafe def u : Nat := 0"))
    assert any("extern" in f for f in native_findings('@[extern "c_fn"] def f : Nat := 0'))
    assert any("implemented_by" in f
               for f in native_findings("@[implemented_by fast] def g : Nat := 0"))
    # Attribute-prefixed and visibility-prefixed declarations are still caught.
    assert any("axiom" in f
               for f in native_findings("@[simp] private axiom sneaky : True"))


def test_native_findings_ignores_identifiers_and_comments():
    clean = (
        "import Mathlib\n"
        "-- a partial explanation mentioning axiom and unsafe in a comment\n"
        "/- opaque discussion -/\n"
        "theorem partialSum_ok (partialSum : Nat) : partialSum = partialSum := rfl\n"
        "theorem axioms_named (externality : Nat) : externality = externality := rfl\n"
    )
    assert native_findings(clean) == []


def test_kernel_check_rejects_declared_axiom_at_scan_time(tmp_path):
    src = tmp_path / "q"
    src.mkdir()
    (src / "P.lean").write_text(
        "import Mathlib\naxiom helper : 2 + 2 = 4\n"
        "theorem egmra_live_check : 2 + 2 = 4 := helper\n",
        encoding="utf-8")
    verdict = run_kernel_check(
        {"source_root": str(src), "declaration_name": "egmra_live_check",
         "expected_type_source": "2 + 2 = 4",
         "source_hash": hash_quarantine_tree(src)},
        lean_project=tmp_path,
        lake_runner=lambda args, cwd: SimpleNamespace(
            returncode=0, stdout="", stderr=""),
    )
    assert verdict["kernel_verified"] is False
    assert any("axiom" in f for f in verdict["unsafe_findings"])


# ── --trust=0 kernel replay ──────────────────────────────────────────────────

def test_kernel_replay_runs_at_trust_level_zero(tmp_path):
    src = tmp_path / "q"
    src.mkdir()
    (src / "P.lean").write_text(
        "import Mathlib\ntheorem egmra_live_check : 2 + 2 = 4 := rfl\n",
        encoding="utf-8")
    seen: list[list[str]] = []

    def _runner(args, cwd):
        seen.append(list(args))
        return SimpleNamespace(
            returncode=0,
            stdout="'egmra_live_check' does not depend on any axioms",
            stderr="")

    verdict = run_kernel_check(
        {"source_root": str(src), "declaration_name": "egmra_live_check",
         "expected_type_source": "2 + 2 = 4",
         "source_hash": hash_quarantine_tree(src)},
        lean_project=tmp_path, lake_runner=_runner)
    assert verdict["kernel_verified"] is True
    assert seen and seen[0][:3] == ["env", "lean", "--trust=0"]


# ── recorded formalization divergences (fidelity notes) ──────────────────────

def test_sketch_divergence_records_are_parsed():
    source = (
        "-- NOTATION: rows are `Fin m → ℝ`\n"
        "-- DIVERGENCE: proved at d^-3 accuracy; mean-width machinery for\n"
        "lemma child_one : ∀ n : ℕ, n ≤ n + 1 := sorry\n"
        "-- DIVERGENCE: constant 8 instead of 6; downstream slack absorbs it\n"
        "theorem target_thm : ∀ n : ℕ, n ≤ n + 2 :=\n"
        "  fun n => Nat.le_succ_of_le (child_one n)\n"
    )
    report = validate_sketch(source, problem_id="erdos-1",
                             target_declaration="target_thm",
                             target_statement="∀ n : ℕ, n ≤ n + 2")
    assert len(report.divergences) == 2
    assert "d^-3" in report.divergences[0]
    assert "constant 8" in report.divergences[1]
    assert report.to_dict()["divergences"] == list(report.divergences)


def test_sketch_without_divergences_is_unchanged():
    source = (
        "lemma child_one : ∀ n : ℕ, n ≤ n + 1 := sorry\n"
        "theorem target_thm : ∀ n : ℕ, n ≤ n + 2 :=\n"
        "  fun n => Nat.le_succ_of_le (child_one n)\n"
    )
    report = validate_sketch(source, problem_id="erdos-1",
                             target_declaration="target_thm")
    assert report.divergences == ()
    assert report.viable


def test_sketch_prompt_carries_coverage_and_slack_rules():
    from egmra.orchestrator.runner_worker import sketch_prompt

    text = sketch_prompt("S.", formal_target="theorem t : True",
                         target_declaration="t")
    assert "MATHLIB COVERAGE RULE" in text
    assert "-- DIVERGENCE:" in text
    assert "SLACK RULE" in text
    assert "NOTATION" in text
    assert "at least three materially different assembly plans" in text
    assert "RESULTS THAT DO NOT COUNT" in text
    assert "LOCKED COMMUNITY FORMAL TARGET" in text
    assert "walk dependencies forward" in text


def test_formalization_prompt_bans_escape_hatches_and_demands_slack():
    from egmra.lean.formalizer import build_formalization_prompt

    text = build_formalization_prompt(
        declaration_name="d", expected_type="True", informal_statement="S.")
    assert "trust level zero" in text
    assert "@[extern]" in text and "opaque" in text and "partial" in text
    assert "library-first" in text and "slack" in text
    assert "LOCKED FORMAL OBLIGATION" in text
    assert "preserve binder order" in text
    assert "RESULTS THAT DO NOT COUNT" in text
