"""Integration tests for the arbitrary-problem CLI, doctor, and status commands."""

from __future__ import annotations

import json

from egmra.cli import main
from egmra.policy import sign_policy


def _signed_policy_file(tmp_path):
    policy = sign_policy({
        "claim_graph": True, "literature_retrieval": True,
        "computation_service": True, "promotion": False,
    })
    path = tmp_path / "policy.json"
    path.write_text(json.dumps(policy.to_document()))
    return path


def _config_file(tmp_path):
    cfg = tmp_path / "cfg.json"
    cfg.write_text(json.dumps({"events_dir": str(tmp_path / "runs")}))
    return cfg


_CORPUS_TEX = r"""\documentclass{article}
\begin{document}
\section{Problem \#7}
\noindent\textbf{Statement:}

Does every sufficiently large integer have property $P$?

\end{document}
"""


def test_run_statement_is_honest_open_state(tmp_path, capsys):
    cfg = _config_file(tmp_path)
    policy = _signed_policy_file(tmp_path)
    rc = main(["--config", str(cfg), "run",
               "--statement", "Every group of prime order is cyclic.",
               "--provider", "deterministic", "--policy", str(policy)])
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert out["result_state"]["state"] in {"OPEN_NO_PROGRESS", "PARTIAL_PROGRESS"}
    assert out["proof_complete"] is False
    assert out["release"] is None
    assert out["input"]["kind"] == "statement"
    assert out["provider"] == "deterministic"


def test_run_browser_provider_without_profile_fails_cleanly(tmp_path, capsys, monkeypatch):
    # The primary provider must fail explicitly, never silently degrade — and the
    # test must never launch a real browser.
    import egmra.agents.browser_runner as br

    def _no_browser(self):
        raise RuntimeError("no authenticated profile / no display")

    monkeypatch.setattr(br.PlaywrightChatGPTBackend, "start", _no_browser)
    cfg = _config_file(tmp_path)
    policy = _signed_policy_file(tmp_path)
    rc = main(["--config", str(cfg), "run", "--statement", "A statement.",
               "--provider", "browser", "--policy", str(policy)])
    assert rc == 2
    err = json.loads(capsys.readouterr().err)
    assert err["error"] == "ValueError"
    assert "browser provider is not operational" in err["detail"]


def test_run_rejects_out_of_range_workers(tmp_path, capsys):
    cfg = _config_file(tmp_path)
    policy = _signed_policy_file(tmp_path)
    rc = main(["--config", str(cfg), "run", "--statement", "A statement.",
               "--provider", "deterministic", "--workers", "9", "--policy", str(policy)])
    assert rc == 2


def test_provider_unavailable_is_retained_not_a_math_failure(tmp_path, capsys, monkeypatch):
    # Defect 13: browser exhaustion must retain the job and report a retryable
    # status with a distinct exit code — never a mathematical verdict.
    import egmra.cli as cli_module
    from egmra.agents.browser_runner import BrowserProviderUnavailable

    def _throttled(**_kwargs):
        raise BrowserProviderUnavailable("throttled after 6 cooldowns")

    monkeypatch.setattr(cli_module, "research", _throttled)
    cfg = _config_file(tmp_path)
    policy = _signed_policy_file(tmp_path)
    rc = main(["--config", str(cfg), "run", "--statement", "A statement.",
               "--provider", "deterministic", "--policy", str(policy)])
    assert rc == 4
    out = json.loads(capsys.readouterr().out)
    assert out["status"] == "provider_unavailable"
    assert out["retain"] is True
    assert "not a mathematical result" in out["note"]


def test_run_does_not_touch_fixture_loader(tmp_path, capsys, monkeypatch):
    # The primary run path must never call the bundled fixture loader.
    import egmra.cli as cli_module

    def _boom(*_a, **_k):  # pragma: no cover - only fails if wrongly called
        raise AssertionError("arbitrary run must not call fixture()")

    monkeypatch.setattr(cli_module, "fixture", _boom)
    cfg = _config_file(tmp_path)
    policy = _signed_policy_file(tmp_path)
    rc = main(["--config", str(cfg), "run", "--statement", "A statement.",
               "--provider", "deterministic", "--policy", str(policy)])
    assert rc == 0
    assert json.loads(capsys.readouterr().out)["result_state"]["state"]


def test_run_erdos_from_local_corpus(tmp_path, capsys):
    tex = tmp_path / "corpus.tex"
    tex.write_text(_CORPUS_TEX, encoding="utf-8")
    catalog = tmp_path / "catalog.json"
    catalog.write_text(json.dumps({"problems": {"7": {
        "problem": 7, "source_state": "open",
        "source_problem_url": "https://www.erdosproblems.com/7",
        "source_last_update": "2025-01-01", "tags": ["number theory"],
    }}}), encoding="utf-8")
    cfg = _config_file(tmp_path)
    policy = _signed_policy_file(tmp_path)
    rc = main(["--config", str(cfg), "run", "--erdos", "7",
               "--corpus-tex", str(tex), "--catalog", str(catalog),
               "--provider", "deterministic", "--policy", str(policy)])
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert out["problem_id"] == "erdos-7"
    assert out["input"]["kind"] == "erdos"
    # A no-solver arbitrary run can only reach an honest pre-release state, never
    # a released/validated one.
    assert out["result_state"]["state"] in {
        "OPEN_NO_PROGRESS", "PARTIAL_PROGRESS",
        "BLOCKED_BY_INTERPRETATION", "CANDIDATE_DISPROOF",
    }
    assert out["proof_complete"] is False
    assert out["release"] is None


def test_run_requires_exactly_one_input(tmp_path, capsys):
    cfg = _config_file(tmp_path)
    policy = _signed_policy_file(tmp_path)
    rc = main(["--config", str(cfg), "run", "--policy", str(policy)])
    assert rc == 2
    assert json.loads(capsys.readouterr().err)["error"] == "ValueError"


def test_run_rejects_multiple_inputs(tmp_path, capsys):
    cfg = _config_file(tmp_path)
    policy = _signed_policy_file(tmp_path)
    rc = main(["--config", str(cfg), "run", "--statement", "x", "--erdos", "7",
               "--policy", str(policy)])
    assert rc == 2
    assert json.loads(capsys.readouterr().err)["error"] == "ValueError"


def test_run_unknown_erdos_number_fails_cleanly(tmp_path, capsys):
    tex = tmp_path / "corpus.tex"
    tex.write_text(_CORPUS_TEX, encoding="utf-8")
    cfg = _config_file(tmp_path)
    policy = _signed_policy_file(tmp_path)
    rc = main(["--config", str(cfg), "run", "--erdos", "999999",
               "--corpus-tex", str(tex), "--policy", str(policy)])
    assert rc == 2
    assert json.loads(capsys.readouterr().err)["error"] == "SourceResolutionError"


def test_status_lists_persisted_runs(tmp_path, capsys):
    cfg = _config_file(tmp_path)
    policy = _signed_policy_file(tmp_path)
    main(["--config", str(cfg), "run", "--statement", "A statement.",
          "--provider", "deterministic", "--policy", str(policy)])
    capsys.readouterr()
    rc = main(["--config", str(cfg), "status"])
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert out["run_count"] >= 1
    assert all(run.get("integrity") for run in out["runs"])


def test_doctor_reports_readiness_without_leaking_secrets(tmp_path, capsys, monkeypatch):
    import egmra.cli as cli_module

    # Keep the probe hermetic: no real lake/lean/aristotle subprocess in tests.
    monkeypatch.setattr(cli_module, "_probe_executable",
                        lambda name, args: {"found": False, "path": "", "operational": False})
    policy = _signed_policy_file(tmp_path)
    rc = main(["doctor", "--policy", str(policy)])
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert out["python_supported"] is True
    assert out["policy"]["loadable"] is True
    assert set(out["ready_for"]) == {
        "local_research", "browser_reasoning", "formal_verification", "aristotle",
    }
    # Only booleans are reported per key — never a value.
    for entry in out["signing_keys"].values():
        assert set(entry) == {"configured", "sufficient_length"}
    serialized = json.dumps(out)
    assert "test-key-that-is-at-least-32-bytes" not in serialized


def test_doctor_distinguishes_launcher_from_operational_lean(tmp_path, capsys, monkeypatch):
    # Defect 16 regression: a launcher on PATH must NOT be reported as ready.
    import egmra.cli as cli_module

    monkeypatch.setattr(
        cli_module, "_probe_executable",
        lambda name, args: {"found": True, "path": f"/usr/bin/{name}",
                            "operational": False, "version": ""},
    )
    policy = _signed_policy_file(tmp_path)
    rc = main(["doctor", "--policy", str(policy)])
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert out["executables"]["lake"]["found"] is True
    assert out["executables"]["lake"]["operational"] is False
    assert out["lean_toolchain"]["operational"] is False
    assert out["ready_for"]["formal_verification"] is False


def test_doctor_reports_unloadable_default_policy(capsys, monkeypatch):
    import egmra.cli as cli_module

    monkeypatch.setattr(cli_module, "_probe_executable",
                        lambda name, args: {"found": False, "path": "", "operational": False})
    rc = main(["doctor"])
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert out["policy"]["loadable"] is False
    assert out["ready_for"]["local_research"] is False
