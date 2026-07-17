"""Safety tests for the localhost EGMRA update/launch console."""

from __future__ import annotations

import hashlib
import json
import os
import stat
import subprocess
from types import SimpleNamespace
from pathlib import Path

import pytest

import operator_console as console_module
from egmra.policy import sign_policy
from operator_console import (
    Operator,
    REQUIRED_CAMPAIGN_KEYS,
    _load_config,
    _load_shell_exports,
    _save_config,
    build_campaign_command,
)


def _git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args], cwd=root, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=True)
    return result.stdout.strip()


def test_keys_parser_handles_quoted_exports_without_executing_shell(tmp_path):
    path = tmp_path / "keys.sh"
    path.write_text(
        '# comment\nexport ARISTOTLE_API_KEY="arstl_local-only"\n'
        "export CHATGPT_PROJECT_URL='https://chatgpt.com/g/project id'\n"
        "NOT-VALID=x\nsource /tmp/danger\n",
        encoding="utf-8")
    values = _load_shell_exports(path)
    assert values == {
        "ARISTOTLE_API_KEY": "arstl_local-only",
        "CHATGPT_PROJECT_URL": "https://chatgpt.com/g/project id",
    }


def test_local_config_is_private_and_gitignored(tmp_path):
    (tmp_path / ".gitignore").write_text(
        "operator.local.json\n.egmra_operator/\negmra.keys.sh\n")
    config = _load_config(tmp_path)
    path = tmp_path / "operator.local.json"
    assert path.is_file() and config["prefer_solvable"] is False
    assert stat.S_IMODE(path.stat().st_mode) == 0o600


def test_campaign_command_preserves_current_allocation_and_contains_no_secrets(tmp_path):
    config = _load_config(tmp_path)
    assert config["aristotle_max_concurrent"] == 3
    assert config["max_problems"] == 0          # full ranked corpus by default
    command = build_campaign_command(config, tmp_path)
    joined = " ".join(command)
    assert "--prefer-solvable" not in command
    assert "--derive-missing-intents" in command
    assert "--max-problems 0" in joined
    assert "--state-store postgres" in joined
    assert "ARISTOTLE_API_KEY" not in joined
    assert "CHATGPT_PROJECT_URL" not in joined
    assert "egmra.keys.sh" not in joined


def test_deep_thinking_defaults_flow_into_the_campaign_command(tmp_path):
    config = _load_config(tmp_path)
    assert config["browser_response_timeout_s"] == 36000  # 10 h: never truncate
    assert config["free_reasoning"] is True
    assert config["research_iterations"] == 6
    assert config["worker_rounds"] == 8
    command = build_campaign_command(config, tmp_path)
    joined = " ".join(command)
    assert "--extraction-provider browser" in joined       # keyless two-call
    assert "--research-iterations 6" in joined
    assert "--worker-rounds 8" in joined
    # Free reasoning is a config choice, not hardwired.
    config["free_reasoning"] = False
    assert "--extraction-provider" not in " ".join(
        build_campaign_command(config, tmp_path))


def test_current_lane_is_not_overridden_by_legacy_solvability_sort(tmp_path):
    config = _load_config(tmp_path)
    config["triage_lane"] = "current"
    config["prefer_solvable"] = True
    assert "--prefer-solvable" not in build_campaign_command(config, tmp_path)

    config["triage_lane"] = "tractable_frontier"
    assert "--prefer-solvable" in build_campaign_command(config, tmp_path)


def test_local_config_validates_aristotle_account_slots(tmp_path):
    config = _load_config(tmp_path)
    config["aristotle_max_concurrent"] = 0
    with pytest.raises(console_module.OperatorError, match="Aristotle concurrency"):
        _save_config(config, tmp_path)


def test_local_config_validates_research_iterations(tmp_path):
    config = _load_config(tmp_path)
    config["research_iterations"] = 9
    with pytest.raises(console_module.OperatorError, match="research_iterations"):
        _save_config(config, tmp_path)


def test_prerequisites_verify_shared_keys_policy_and_warm_repl(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    environment = {name: name.lower().ljust(40, "x") for name in REQUIRED_CAMPAIGN_KEYS}
    keys = root / "egmra.keys.sh"
    keys.write_text("".join(
        f"export {name}='{value}'\n" for name, value in environment.items()))
    keys.chmod(0o600)
    (root / ".env").write_text(
        "export ARISTOTLE_API_KEY='local-test-provider-key'\n"
        "export CHATGPT_PROJECT_URL='https://chatgpt.com/g/project'\n")
    (root / ".chatgpt_profile").mkdir()
    (root / ".venv" / "bin").mkdir(parents=True)
    (root / ".venv" / "bin" / "python").touch()
    (root / "aristotle_lean_project" / ".lake").mkdir(parents=True)
    (root / "reviews").mkdir()
    (root / "targets").mkdir()
    repl = tmp_path / "repl" / ".lake" / "build" / "bin" / "repl"
    repl.parent.mkdir(parents=True)
    repl.touch()
    policy = sign_policy({"claim_graph": True}, env=environment)
    policy_path = root / "egmra_campaigns" / "policy-promotion-v3-local.json"
    policy_path.parent.mkdir()
    policy_path.write_text(json.dumps(policy.to_document()))

    config = _load_config(root)
    config["state_store"] = "file"
    prerequisites = Operator(root=root)._prerequisites(config)
    assert all(prerequisites.values())

    keys.write_text(keys.read_text().replace("EGMRA_EVENT_KEY", "MISSING_EVENT_KEY"))
    prerequisites = Operator(root=root)._prerequisites(config)
    assert prerequisites["keys_file"] is False
    assert prerequisites["policy"] is False


def test_safe_update_preserves_ignored_secrets_and_local_tracked_edits(tmp_path):
    remote = tmp_path / "remote.git"
    subprocess.run(["git", "init", "--bare", str(remote)], check=True,
                   stdout=subprocess.DEVNULL)
    root = tmp_path / "checkout"
    subprocess.run(["git", "clone", str(remote), str(root)], check=True,
                   stdout=subprocess.DEVNULL)
    _git(root, "config", "user.name", "Test")
    _git(root, "config", "user.email", "test@example.invalid")
    _git(root, "checkout", "-b", "main")
    (root / ".gitignore").write_text(
        "egmra.keys.sh\noperator.local.json\n.egmra_operator/\n"
        ".chatgpt_profile/\negmra_runs/\negmra_campaigns/\negmra_outcomes/\n")
    (root / "tracked.txt").write_text("base\n")
    _git(root, "add", ".gitignore", "tracked.txt")
    _git(root, "commit", "-m", "base")
    _git(root, "push", "-u", "origin", "main")

    # Machine-local state: ignored secret + tracked local runtime edit.
    secret = root / "egmra.keys.sh"
    secret.write_text('export ARISTOTLE_API_KEY="do-not-touch"\n')
    before_hash = hashlib.sha256(secret.read_bytes()).hexdigest()
    (root / "tracked.txt").write_text("base\nlocal runtime edit\n")
    config = _load_config(root)
    config["branch"] = "main"
    (root / "operator.local.json").write_text(json.dumps(config))
    os.chmod(root / "operator.local.json", 0o600)

    # Independent upstream update.
    upstream = tmp_path / "upstream"
    subprocess.run(["git", "clone", str(remote), str(upstream)], check=True,
                   stdout=subprocess.DEVNULL)
    _git(upstream, "config", "user.name", "Upstream")
    _git(upstream, "config", "user.email", "upstream@example.invalid")
    _git(upstream, "checkout", "main")
    (upstream / "new-code.txt").write_text("new code\n")
    _git(upstream, "add", "new-code.txt")
    _git(upstream, "commit", "-m", "upstream")
    _git(upstream, "push", "origin", "main")

    message = Operator(root)._safe_update()
    assert "Updated" in message
    assert (root / "new-code.txt").read_text() == "new code\n"
    assert "local runtime edit" in (root / "tracked.txt").read_text()
    assert hashlib.sha256(secret.read_bytes()).hexdigest() == before_hash
    # The safety backup remains even after a clean reapplication.
    assert _git(root, "rev-parse", "refs/stash")


def test_safe_update_refuses_running_campaign(tmp_path, monkeypatch):
    root = tmp_path / "repo"
    root.mkdir()
    _load_config(root)
    process = {
        "pid": 789, "command": "campaign --stop-file stop.json", "managed": True}
    monkeypatch.setattr(console_module, "_campaign_processes", lambda _root: [process])
    with pytest.raises(console_module.OperatorError, match="refusing to update"):
        Operator(root=root)._safe_update()


def test_stop_writes_cooperative_marker_without_signaling(tmp_path, monkeypatch):
    root = tmp_path / "repo"
    root.mkdir()
    config = _load_config(root)
    process = {
        "pid": 123, "command": "campaign --stop-file stop.json", "managed": True}
    monkeypatch.setattr(console_module, "_campaign_processes", lambda _root: [process])

    def reject_signal(*_args, **_kwargs):
        raise AssertionError("cooperative stop must not send a process signal")

    monkeypatch.setattr(console_module.os, "kill", reject_signal)
    message = Operator(root=root)._stop(wait_seconds=0)
    marker = root / config["stop_file"]
    assert marker.is_file()
    assert json.loads(marker.read_text())["process_ids"] == [123]
    assert "finishing their current problems" in message


def test_stop_refuses_to_force_legacy_campaign(tmp_path, monkeypatch):
    root = tmp_path / "repo"
    root.mkdir()
    _load_config(root)
    process = {"pid": 456, "command": "campaign", "managed": True}
    monkeypatch.setattr(console_module, "_campaign_processes", lambda _root: [process])
    with pytest.raises(console_module.OperatorError, match="predate cooperative stop"):
        Operator(root=root)._stop(wait_seconds=0)
    assert not (root / ".egmra_operator" / "stop-request.json").exists()


def _fake_app_sources(root: Path) -> None:
    executable = root / "EGMRA Operator.app" / "Contents" / "MacOS" / "egmra-operator"
    executable.parent.mkdir(parents=True)
    executable.write_text("#!/bin/zsh\n")
    (root / "EGMRA Operator.cmd").write_text("@echo off\r\n")


def test_install_macos_app_writes_private_repo_pointer(tmp_path):
    root, home = tmp_path / "repo", tmp_path / "home"
    root.mkdir(); home.mkdir(); _fake_app_sources(root)
    message = Operator(root=root, home=home, platform="darwin")._install_app()
    installed = home / "Applications" / "EGMRA Operator.app"
    pointer = home / "Library" / "Application Support" / "EGMRA Operator" / "repo-path"
    assert installed.is_dir() and "Installed" in message
    assert pointer.read_text().strip() == str(root.resolve())
    assert stat.S_IMODE(pointer.stat().st_mode) == 0o600
    assert stat.S_IMODE((installed / "Contents" / "MacOS" / "egmra-operator").stat().st_mode) == 0o755


def test_install_windows_app_creates_launcher_pointer_and_shortcuts(
        tmp_path, monkeypatch):
    root, home = tmp_path / "repo", tmp_path / "home"
    root.mkdir(); home.mkdir(); _fake_app_sources(root)
    appdata = home / "AppData" / "Roaming"
    local = home / "AppData" / "Local"
    calls = []

    def fake_run(args, **_kwargs):
        calls.append(args)
        return SimpleNamespace(returncode=0, stdout="")

    monkeypatch.setattr(console_module, "_run", fake_run)
    message = Operator(
        root=root, home=home, platform="win32",
        environment={"APPDATA": str(appdata), "LOCALAPPDATA": str(local)},
    )._install_app()
    installed = local / "EGMRA Operator"
    assert (installed / "EGMRA Operator.cmd").is_file()
    assert (installed / "repo-path.txt").read_text().strip() == str(root.resolve())
    assert len(calls) == 2 and all(call[0] == "powershell.exe" for call in calls)
    assert "Installed Windows launcher" in message


def test_install_linux_desktop_entry_points_at_checkout(tmp_path):
    root, home = tmp_path / "repo", tmp_path / "home"
    root.mkdir(); home.mkdir()
    message = Operator(root=root, home=home, platform="linux")._install_app()
    desktop = home / ".local" / "share" / "applications" / "egmra-operator.desktop"
    text = desktop.read_text()
    assert "Name=EGMRA Operator" in text
    assert str(root / "operator_console.py") in text
    assert stat.S_IMODE(desktop.stat().st_mode) == 0o755
    assert "application menu" in message


# ── auto-restart supervisor ──────────────────────────────────────────────────

def _supervised_operator(tmp_path, monkeypatch, *, running, campaign_pid=999,
                         started_at=None, config_overrides=None):
    """An Operator wired for supervise_once tests (no real launch/ps)."""
    import time as _time

    root = tmp_path / "repo"
    root.mkdir(exist_ok=True)
    _load_config(root)
    if config_overrides:
        cfg = _load_config(root)
        cfg.update(config_overrides)
        _save_config(cfg, root)
    # supervise_once reads the module-global STATE_PATH; point it at a tmp file.
    state_path = root / ".egmra_operator" / "state.json"
    state_path.parent.mkdir(parents=True, exist_ok=True)
    if campaign_pid is not None:
        state_path.write_text(json.dumps({
            "campaign_pid": campaign_pid,
            "started_at": started_at if started_at is not None else _time.time(),
        }))
    monkeypatch.setattr(console_module, "STATE_PATH", state_path)
    monkeypatch.setattr(console_module, "_campaign_processes",
                        lambda _root: ([{"pid": campaign_pid, "command": "campaign",
                                         "managed": True}] if running else []))
    op = Operator(root=root)
    op._kill_orphaned_browser_profile = lambda: 0  # never touch real processes
    starts: list[int] = []

    def _fake_start():
        starts.append(1)
        return "Pipeline started as PID 4242"

    op._start = _fake_start
    op._starts = starts  # expose for assertions
    return op


def test_supervisor_restarts_a_campaign_that_died_unexpectedly(tmp_path, monkeypatch):
    op = _supervised_operator(tmp_path, monkeypatch, running=False)
    result = op.supervise_once()
    assert result.startswith("auto-restarted")
    assert op._starts == [1]


def test_supervisor_leaves_a_healthy_campaign_alone(tmp_path, monkeypatch):
    op = _supervised_operator(tmp_path, monkeypatch, running=True)
    assert op.supervise_once() == "campaign running"
    assert op._starts == []


def test_supervisor_does_not_restart_after_a_requested_stop(tmp_path, monkeypatch):
    op = _supervised_operator(tmp_path, monkeypatch, running=False)
    stop_path = console_module._resolve(op.root, str(op.config()["stop_file"]))
    stop_path.parent.mkdir(parents=True, exist_ok=True)
    stop_path.write_text(json.dumps({"requested_at": 1.0, "process_ids": [999]}))
    assert op.supervise_once() == "stopped by request; not restarting"
    assert op._starts == []


def test_supervisor_respects_a_clean_exit(tmp_path, monkeypatch):
    op = _supervised_operator(tmp_path, monkeypatch, running=False)
    op._campaign_process = SimpleNamespace(poll=lambda: 0)   # exited rc 0
    assert op.supervise_once() == "clean exit (rc 0); not restarting"
    assert op._starts == []


def test_supervisor_can_be_disabled(tmp_path, monkeypatch):
    op = _supervised_operator(tmp_path, monkeypatch, running=False,
                              config_overrides={"auto_restart": False})
    assert op.supervise_once() == "auto-restart disabled"
    assert op._starts == []


def test_supervisor_pauses_after_too_many_restarts(tmp_path, monkeypatch):
    import time as _time
    op = _supervised_operator(tmp_path, monkeypatch, running=False,
                              config_overrides={"auto_restart_max_in_window": 3,
                                                "auto_restart_window_seconds": 900})
    now = _time.time()
    op._restart_history = [now - 10, now - 8, now - 5]   # already at the cap
    result = op.supervise_once()
    assert "paused" in result
    assert op._starts == []
    assert op._autorestart_paused is True
    # And once paused it stays paused on the next tick (no restart).
    assert op.supervise_once() == "auto-restart paused (manual attention needed)"


def test_supervisor_skips_while_a_console_job_is_running(tmp_path, monkeypatch):
    op = _supervised_operator(tmp_path, monkeypatch, running=False)
    op.job = {**op.job, "running": True, "name": "update"}
    assert op.supervise_once().startswith("job running")
    assert op._starts == []
