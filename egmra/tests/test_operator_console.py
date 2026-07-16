"""Safety tests for the localhost EGMRA update/launch console."""

from __future__ import annotations

import hashlib
import json
import os
import stat
import subprocess
from pathlib import Path

from operator_console import (
    Operator,
    _load_config,
    _load_shell_exports,
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
    assert path.is_file() and config["prefer_solvable"] is True
    assert stat.S_IMODE(path.stat().st_mode) == 0o600


def test_campaign_command_contains_preferences_but_no_secrets(tmp_path):
    config = _load_config(tmp_path)
    command = build_campaign_command(config, tmp_path)
    joined = " ".join(command)
    assert "--prefer-solvable" in command
    assert "--state-store postgres" in joined
    assert "ARISTOTLE_API_KEY" not in joined
    assert "CHATGPT_PROJECT_URL" not in joined
    assert "egmra.keys.sh" not in joined


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
