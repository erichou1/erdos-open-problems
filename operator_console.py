"""Local-only EGMRA update/launch console.

Why a localhost web console instead of Electron/native packaging:

* zero new runtime/framework dependencies;
* it launches the exact checked-in Python CLI, so there is no second pipeline;
* secrets stay in gitignored ``egmra.keys.sh`` and are never returned by HTTP;
* browser cookies stay in a gitignored/out-of-repo Playwright profile;
* safe update is fetch + fast-forward only, with a retained stash backup for
  tracked/untracked local edits; ignored keys/runs/profiles are never stashed;
* binds 127.0.0.1 only and requires a random per-process action token.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import os
import re
import shlex
import shutil
import signal
import socket
import stat
import subprocess
import sys
import threading
import time
import webbrowser
from dataclasses import dataclass, field
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.error import URLError
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parent
STATE_DIR = ROOT / ".egmra_operator"
CONFIG_PATH = ROOT / "operator.local.json"
STATE_PATH = STATE_DIR / "state.json"
HOST = "127.0.0.1"
DEFAULT_PORT = 8765
REQUIRED_CAMPAIGN_KEYS = (
    "EGMRA_EVENT_KEY", "EGMRA_POLICY_KEY", "EGMRA_EVIDENCE_KEY",
    "EGMRA_RELEASE_KEY", "EGMRA_GATE_KEY", "EGMRA_PROMOTION_KEY",
    "EGMRA_LEAN_CHECKER_KEY", "EGMRA_AUTHORITY_KEY",
    "EGMRA_TRUTH_SNAPSHOT_KEY", "EGMRA_CHECKPOINT_KEY",
    "EGMRA_MODEL_ATTESTATION_KEY", "EGMRA_INTENT_REVIEW_KEY",
    "EGMRA_FORMAL_CORRESPONDENCE_KEY", "EGMRA_LEGACY_REVIEW_KEY",
    "EGMRA_LEGACY_EVIDENCE_KEY", "EGMRA_EXPERT_REVIEW_KEY",
)


class OperatorError(RuntimeError):
    pass


def _venv_python(root: Path, *, windowless: bool = False) -> Path:
    if os.name == "nt":
        name = "pythonw.exe" if windowless else "python.exe"
        candidate = root / ".venv" / "Scripts" / name
        if windowless and not candidate.is_file():
            return root / ".venv" / "Scripts" / "python.exe"
        return candidate
    return root / ".venv" / "bin" / "python"


def _hostname() -> str:
    return socket.gethostname().split(".", 1)[0] or "unknown-host"


def _run(args: list[str], *, root: Path = ROOT, timeout: float | None = None,
         check: bool = False, env: dict[str, str] | None = None) -> subprocess.CompletedProcess:
    try:
        result = subprocess.run(
            args, cwd=root, text=True, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, timeout=timeout, check=False, env=env,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise OperatorError(f"cannot run {args[0]}: {exc}") from exc
    if check and result.returncode != 0:
        raise OperatorError(
            f"command failed ({result.returncode}): {' '.join(args)}\n"
            f"{result.stdout[-4000:]}")
    return result


def _load_shell_exports(path: Path) -> dict[str, str]:
    """Parse the simple `export KEY="value"` format used by egmra.keys.sh."""
    result: dict[str, str] = {}
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return result
    for raw in lines:
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].strip()
        try:
            parts = shlex.split(line, comments=True, posix=True)
        except ValueError:
            continue
        if len(parts) != 1 or "=" not in parts[0]:
            continue
        name, value = parts[0].split("=", 1)
        if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name):
            result[name] = value
    return result


def _atomic_private_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    fd = os.open(temp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        json.dump(value, handle, indent=2, sort_keys=True)
        handle.write("\n")
    os.replace(temp, path)


def _default_config(root: Path = ROOT) -> dict[str, Any]:
    profile_candidates = [root / ".chatgpt_profile", root.parent / ".chatgpt_profile"]
    profile = next((path for path in profile_candidates if path.is_dir()), profile_candidates[0])
    policy_candidates = [
        root / "egmra_campaigns" / "policy-promotion-v3-local.json",
        root / "egmra_campaigns" / "policy-local.json",
    ]
    policy = next((path for path in policy_candidates if path.is_file()), policy_candidates[0])
    repl_name = "repl.exe" if os.name == "nt" else "repl"
    repl = root.parent / "repl" / ".lake" / "build" / "bin" / repl_name
    repl_command = (
        subprocess.list2cmdline(["lake", "env", str(repl)])
        if os.name == "nt"
        else shlex.join(["lake", "env", str(repl)])
    )
    return {
        "schema_version": 1,
        "branch": "audit/egmra-independent-remediation-20260713",
        "campaign_id": "shared-current-v1",
        "workers": 3,
        "aristotle_max_concurrent": 3,
        "prefer_solvable": False,
        "keys_file": "egmra.keys.sh",
        "chatgpt_profile": str(profile),
        "triage_dir": "triage",
        "triage_lane": "current",
        "max_problems": 0,
        "derive_missing_intents": True,
        "policy": str(policy.relative_to(root)) if policy.is_relative_to(root) else str(policy),
        "reviews_dir": "reviews",
        "targets_dir": "targets",
        "lean_project": "aristotle_lean_project",
        "lean_dev_repl": repl_command,
        "checkpoint_dir": "egmra_campaigns/ckpts-shared",
        "lemma_library": "egmra_lemma_library.jsonl",
        "stop_file": ".egmra_operator/stop-request.json",
        "state_store": "postgres",
        # Long-horizon search ceilings: six independent mechanism families,
        # each allowed up to eight continuation rounds. Existing stagnation,
        # blocker, lease, and budget rules still stop unproductive routes.
        "research_iterations": 6,
        "worker_rounds": 8,
        "lean_repair_rounds": 2,
        "hostile_review": 2,
        "budget": 100,
        "log_file": str(
            (Path(os.environ.get("TEMP", "/tmp"))
             / f"egmra_campaign_{_hostname()}.log")),
        # Deep-thinking controls: how long one browser exchange may reason
        # (Pro/thinking models legitimately run 30 min - many hours on hard
        # targets; the public breakthrough cases all did), and whether the
        # main call reasons freely in prose with a second browser exchange
        # doing the clerical JSON extraction (no API key needed). Default 10h
        # so a long reasoning run is never truncated.
        "browser_response_timeout_s": 36000,
        "free_reasoning": True,
        # Auto-restart supervisor: the console relaunches a campaign that dies
        # unexpectedly (e.g. the liveness watchdog force-exited a wedged
        # process), unless the operator asked it to stop. Bounded so a
        # genuinely broken environment can't hot-loop forever.
        "auto_restart": True,
        "auto_restart_window_seconds": 900,
        "auto_restart_max_in_window": 5,
    }


def _load_config(root: Path = ROOT) -> dict[str, Any]:
    defaults = _default_config(root)
    path = root / "operator.local.json"
    if not path.is_file():
        _atomic_private_json(path, defaults)
        return defaults
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise OperatorError(f"invalid {path.name}: {exc}") from exc
    if not isinstance(value, dict):
        raise OperatorError(f"{path.name} must be a JSON object")
    return defaults | value


def _save_config(config: dict[str, Any], root: Path = ROOT) -> None:
    allowed = set(_default_config(root))
    clean = {key: value for key, value in config.items() if key in allowed}
    clean["schema_version"] = 1
    workers = int(clean.get("workers", 3))
    if not 1 <= workers <= 5:
        raise OperatorError("workers must be between 1 and 5")
    clean["workers"] = workers
    aristotle_slots = int(clean.get("aristotle_max_concurrent", workers))
    if not 1 <= aristotle_slots <= 5:
        raise OperatorError("Aristotle concurrency must be between 1 and 5")
    clean["aristotle_max_concurrent"] = aristotle_slots
    state_store = str(clean.get("state_store", "postgres"))
    if state_store not in {"file", "postgres"}:
        raise OperatorError("state store must be 'file' or 'postgres'")
    clean["state_store"] = state_store
    for name, minimum, maximum in (
        ("research_iterations", 1, 8),
        ("worker_rounds", 1, 8),
        ("lean_repair_rounds", 0, 3),
        ("hostile_review", 0, 4),
    ):
        value = int(clean[name])
        if not minimum <= value <= maximum:
            raise OperatorError(f"{name} must be between {minimum} and {maximum}")
        clean[name] = value
    max_problems = int(clean["max_problems"])
    if max_problems < 0:
        raise OperatorError("maximum problems cannot be negative")
    clean["max_problems"] = max_problems
    budget = float(clean["budget"])
    if not math.isfinite(budget) or budget <= 0:
        raise OperatorError("problem budget must be finite and positive")
    clean["budget"] = budget
    for name in ("branch", "campaign_id"):
        if not str(clean[name]).strip():
            raise OperatorError(f"{name} must not be empty")
    _atomic_private_json(root / "operator.local.json", clean)


def _resolve(root: Path, value: str) -> Path:
    path = Path(value).expanduser()
    return path if path.is_absolute() else root / path


def _git(root: Path, *args: str, timeout: float = 30.0,
         check: bool = False) -> subprocess.CompletedProcess:
    return _run(["git", *args], root=root, timeout=timeout, check=check)


def _sha256_file(path: Path) -> str | None:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return None


def _pid_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def _pid_cwd(pid: int) -> Path | None:
    proc = Path(f"/proc/{pid}/cwd")
    try:
        return proc.resolve(strict=True)
    except OSError:
        pass
    result = _run(["lsof", "-a", "-p", str(pid), "-d", "cwd", "-Fn"], timeout=3)
    for line in result.stdout.splitlines():
        if line.startswith("n/"):
            return Path(line[1:]).resolve()
    return None


def _campaign_processes(root: Path = ROOT) -> list[dict[str, Any]]:
    if os.name == "nt":
        script = (
            "Get-CimInstance Win32_Process | "
            "Select-Object ProcessId,CommandLine | ConvertTo-Json -Compress")
        result = _run([
            "powershell.exe", "-NoProfile", "-NonInteractive",
            "-Command", script,
        ], timeout=8)
        try:
            payload = json.loads(result.stdout or "[]")
        except json.JSONDecodeError:
            return []
        records = payload if isinstance(payload, list) else [payload]
        root_text = str(root.resolve()).lower()
        rows = []
        for record in records:
            command = str(record.get("CommandLine") or "")
            pid = int(record.get("ProcessId") or 0)
            if "-m egmra.cli campaign" in command \
                    and root_text in command.lower():
                rows.append({"pid": pid, "command": command, "managed": True})
        return rows
    result = _run(["ps", "-axo", "pid=,command="], timeout=5)
    rows = []
    for line in result.stdout.splitlines():
        match = re.match(r"\s*(\d+)\s+(.*)", line)
        if not match:
            continue
        pid, command = int(match.group(1)), match.group(2)
        if "-m egmra.cli campaign" not in command:
            continue
        cwd = _pid_cwd(pid)
        if cwd == root.resolve():
            rows.append({"pid": pid, "command": command, "managed": True})
    return rows


def build_campaign_command(config: dict[str, Any], root: Path = ROOT) -> list[str]:
    python = _venv_python(root)
    command = [
        str(python), "-u", "-m", "egmra.cli", "campaign",
        "--campaign-id", str(config["campaign_id"]),
        "--triage", str(config["triage_dir"]),
        "--triage-lane", str(config["triage_lane"]),
        "--max-problems", str(int(config["max_problems"])),
        "--provider", "browser", "--workers", str(int(config["workers"])),
        "--research-iterations", str(int(config["research_iterations"])),
        "--worker-rounds", str(int(config["worker_rounds"])),
        "--budget", str(float(config["budget"])),
        "--reviews-dir", str(config["reviews_dir"]),
        "--targets-dir", str(config["targets_dir"]),
        "--lemma-library", str(config["lemma_library"]),
        "--formalizer", "aristotle",
        "--lean-project", str(config["lean_project"]),
        "--lean-repair-rounds", str(int(config["lean_repair_rounds"])),
        "--lean-dev-repl", str(config["lean_dev_repl"]),
        "--hostile-review", str(int(config["hostile_review"])),
        "--retrieval", "corpus", "--oeis", "offline", "--explore-blocked",
        "--checkpoint-dir", str(config["checkpoint_dir"]),
        "--stop-file", str(config["stop_file"]),
        "--auto-rerank",
        "--outcome-ledger", f"egmra_outcomes/shared-{_hostname()}.jsonl",
        "--state-store", str(config["state_store"]),
        "--policy", str(config["policy"]),
    ]
    if config.get("prefer_solvable", False) \
            and config.get("triage_lane") != "current":
        command.append("--prefer-solvable")
    if config.get("derive_missing_intents", True):
        command.append("--derive-missing-intents")
    if config.get("free_reasoning", True):
        # Two-call mode with the worker's own browser tab as the extractor:
        # the MAIN exchange reasons freely in prose (no JSON format pressure),
        # a second clerical exchange structures it. No API key required.
        command.extend(["--extraction-provider", "browser"])
    return command


@dataclass
class Operator:
    root: Path = ROOT
    home: Path = field(default_factory=Path.home)
    platform: str = field(default_factory=lambda: sys.platform)
    environment: dict[str, str] = field(
        default_factory=lambda: dict(os.environ), repr=False)
    lock: threading.RLock = field(default_factory=threading.RLock)
    job: dict[str, Any] = field(default_factory=lambda: {
        "running": False, "name": "", "message": "", "ok": None,
        "started_at": None, "finished_at": None,
    })
    lines: list[str] = field(default_factory=list)
    # Auto-restart supervisor state (see supervise_once). Non-init: process
    # exit-code awareness survives only within one console lifetime; a restarted
    # console falls back to the PID + stop-file heuristic.
    _campaign_process: Any = field(default=None, init=False, repr=False)
    _restart_history: list[float] = field(default_factory=list, init=False, repr=False)
    _autorestart_paused: bool = field(default=False, init=False, repr=False)

    def log(self, message: str) -> None:
        stamp = time.strftime("%H:%M:%S")
        with self.lock:
            self.lines.append(f"{stamp} {message}")
            del self.lines[:-200]

    def config(self) -> dict[str, Any]:
        return _load_config(self.root)

    def _git_state(self, config: dict[str, Any], *, fetch: bool = False) -> dict[str, Any]:
        branch = str(config["branch"])
        if fetch:
            _git(self.root, "fetch", "--quiet", "origin", branch, timeout=30, check=True)
        local = _git(self.root, "rev-parse", "HEAD", check=True).stdout.strip()
        remote_result = _git(self.root, "rev-parse", f"origin/{branch}")
        remote = remote_result.stdout.strip() if remote_result.returncode == 0 else ""
        dirty = _git(self.root, "status", "--porcelain").stdout.splitlines()
        if not remote:
            relation = "remote unavailable"
        elif local == remote:
            relation = "current"
        elif _git(self.root, "merge-base", "--is-ancestor", local, remote).returncode == 0:
            relation = "update available"
        elif _git(self.root, "merge-base", "--is-ancestor", remote, local).returncode == 0:
            relation = "local commits ahead"
        else:
            relation = "diverged — manual Git help required"
        return {"local": local, "remote": remote, "relation": relation,
                "dirty_count": len(dirty), "dirty_preview": dirty[:12]}

    def _prerequisites(self, config: dict[str, Any]) -> dict[str, Any]:
        keys = _resolve(self.root, str(config["keys_file"]))
        profile = _resolve(self.root, str(config["chatgpt_profile"]))
        policy = _resolve(self.root, str(config["policy"]))
        lean = _resolve(self.root, str(config["lean_project"]))
        python = _venv_python(self.root)
        env = _load_shell_exports(keys)
        env.update(_load_shell_exports(self.root / ".env"))
        key_mode_safe = keys.is_file() and (
            os.name == "nt"
            or stat.S_IMODE(keys.stat().st_mode) & 0o077 == 0
        )
        required_keys_present = all(
            len(env.get(name, "").encode("utf-8")) >= 32
            for name in REQUIRED_CAMPAIGN_KEYS)
        policy_valid = False
        if policy.is_file() and required_keys_present:
            try:
                from egmra.policy import load_policy
                load_policy(policy, env=env)
            except (OSError, ValueError):
                pass
            else:
                policy_valid = True
        try:
            repl_parts = shlex.split(
                str(config["lean_dev_repl"]), posix=os.name != "nt")
        except ValueError:
            repl_parts = []
        repl_path = (
            Path(repl_parts[-1].strip("\"'")) if len(repl_parts) >= 3 else None)
        return {
            "venv": python.is_file(),
            "keys_file": key_mode_safe and required_keys_present,
            "aristotle_key": bool(env.get("ARISTOTLE_API_KEY")),
            "chatgpt_workspace": bool(env.get("CHATGPT_PROJECT_URL")),
            "postgres_dsn": bool(env.get("EGMRA_POSTGRES_DSN"))
                if config.get("state_store") == "postgres" else True,
            "chatgpt_profile": profile.is_dir(),
            "postgres_driver": config.get("state_store") != "postgres"
                or importlib.util.find_spec("psycopg") is not None,
            "policy": policy_valid,
            "lean_project": (lean / ".lake").is_dir(),
            "lean_repl": bool(repl_path and repl_path.is_file()),
            "reviews": _resolve(self.root, str(config["reviews_dir"])).is_dir(),
            "targets": _resolve(self.root, str(config["targets_dir"])).is_dir(),
        }

    def status(self, *, fetch: bool = False) -> dict[str, Any]:
        config = self.config()
        processes = _campaign_processes(self.root)
        state = {}
        try:
            state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            pass
        managed_pid = int(state.get("campaign_pid", 0) or 0)
        with self.lock:
            job = dict(self.job)
            logs = list(self.lines[-80:])
        return {
            "config": config,
            "git": self._git_state(config, fetch=fetch),
            "prerequisites": self._prerequisites(config),
            "campaign": {
                "running": bool(processes), "processes": processes,
                "managed_pid": managed_pid,
                "managed_pid_alive": _pid_alive(managed_pid),
            },
            "job": job, "log": logs,
        }

    def _safe_update(self) -> str:
        processes = _campaign_processes(self.root)
        if processes:
            pids = ", ".join(str(row["pid"]) for row in processes)
            raise OperatorError(
                f"refusing to update while campaign processes are running: {pids}. "
                "Use Update + restart for a cooperative stop, or Stop cleanly first.")
        config = self.config()
        branch = str(config["branch"])
        keys_path = _resolve(self.root, str(config["keys_file"]))
        keys_before = _sha256_file(keys_path)
        for protected in (str(config["keys_file"]), ".env",
                  str(config["chatgpt_profile"]),
                  "operator.local.json", ".egmra_operator",
                          "egmra_runs", "egmra_campaigns", "egmra_outcomes",
                          str(config["lemma_library"]), str(config["stop_file"])):
            result = _git(self.root, "check-ignore", "-q", protected)
            # An out-of-repo absolute profile cannot be checked and is safe by location.
            if Path(protected).is_absolute():
                continue
            if result.returncode != 0 and _resolve(self.root, protected).exists():
                raise OperatorError(f"refusing update: local path is not gitignored: {protected}")
        self.log(f"Fetching origin/{branch}")
        before = self._git_state(config, fetch=True)
        if before["relation"] == "current":
            return "Already current; local files unchanged."
        if before["relation"] != "update available":
            raise OperatorError(before["relation"])
        old_head = before["local"]
        stash_hash = ""
        if before["dirty_count"]:
            self.log(f"Backing up {before['dirty_count']} local changes in Git stash")
            result = _git(
                self.root, "stash", "push", "--include-untracked",
                "-m", f"egmra-operator-backup-{int(time.time())}", check=True)
            if "No local changes" not in result.stdout:
                stash_hash = _git(self.root, "rev-parse", "refs/stash", check=True).stdout.strip()
                self.log(f"Backup retained as stash {stash_hash[:12]}")
        _git(self.root, "merge", "--ff-only", f"origin/{branch}", check=True)
        new_head = _git(self.root, "rev-parse", "HEAD", check=True).stdout.strip()
        changed = _git(self.root, "diff", "--name-only", old_head, new_head).stdout.splitlines()
        dependency_error: OperatorError | None = None
        if any(path in changed for path in ("requirements.txt", "pyproject.toml")):
            self.log("Dependencies changed; updating virtual environment")
            python = str(_venv_python(self.root))
            try:
                _run([python, "-m", "pip", "install", "-r", "requirements.txt"],
                     root=self.root, timeout=1800, check=True)
                _run([python, "-m", "pip", "install", "-e",
                      ".[aristotle,postgres]"],
                     root=self.root, timeout=1800, check=True)
                _run([python, "-m", "playwright", "install", "chromium"],
                     root=self.root, timeout=1800, check=True)
            except OperatorError as exc:
                dependency_error = exc
        if stash_hash:
            self.log("Reapplying local tracked/untracked changes")
            applied = _git(self.root, "stash", "apply", "--index", stash_hash)
            if applied.returncode != 0:
                raise OperatorError(
                    "code updated, but local changes conflict. Nothing was lost: "
                    f"backup stash {stash_hash[:12]} is retained. Resolve Git conflicts "
                    "before starting the pipeline.\n" + applied.stdout[-2000:])
        if dependency_error is not None:
            raise OperatorError(
                "code updated and local edits were restored, but dependency update "
                f"failed; repair the virtual environment before starting. {dependency_error}")
        if _sha256_file(keys_path) != keys_before:
            raise OperatorError("safety violation: keys file changed during update")
        return (
            f"Updated {old_head[:8]} → {new_head[:8]}. "
            + (f"Local backup retained as stash {stash_hash[:12]}." if stash_hash else "No local changes needed backup."))

    def _start(self) -> str:
        config = self.config()
        prereqs = self._prerequisites(config)
        missing = [name for name, ok in prereqs.items() if not ok]
        if missing:
            raise OperatorError("cannot start; fix prerequisites: " + ", ".join(missing))
        existing = _campaign_processes(self.root)
        if existing:
            raise OperatorError(
                "campaign already running: " + ", ".join(str(row["pid"]) for row in existing))
        keys_path = _resolve(self.root, str(config["keys_file"]))
        private_env = _load_shell_exports(keys_path)
        private_env.update(_load_shell_exports(self.root / ".env"))
        env = os.environ.copy() | private_env
        env["EGMRA_ARISTOTLE_MAX_CONCURRENT"] = str(
            int(config["aristotle_max_concurrent"]))
        env["EGMRA_BROWSER_RESPONSE_TIMEOUT_S"] = str(
            int(config.get("browser_response_timeout_s", 36000)))
        env["CHATGPT_PROFILE_DIR"] = str(
            _resolve(self.root, str(config["chatgpt_profile"])))
        stop_path = _resolve(self.root, str(config["stop_file"]))
        try:
            stop_path.unlink(missing_ok=True)
        except OSError as exc:
            raise OperatorError(f"cannot clear prior stop request: {exc}") from exc
        command = build_campaign_command(config, self.root)
        log_path = Path(str(config["log_file"])).expanduser()
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_handle = open(log_path, "ab", buffering=0)
        try:
            process = subprocess.Popen(
                command, cwd=self.root, env=env, stdin=subprocess.DEVNULL,
                stdout=log_handle, stderr=subprocess.STDOUT, start_new_session=True,
            )
        finally:
            log_handle.close()
        time.sleep(.2)
        return_code = process.poll()
        if return_code is not None:
            if return_code == 0:
                return f"Pipeline finished immediately; check log: {log_path}"
            try:
                tail = log_path.read_text(encoding="utf-8", errors="replace")[-2000:]
            except OSError:
                tail = ""
            raise OperatorError(
                f"pipeline exited immediately with code {return_code}; log: {log_path}\n"
                + tail)
        _atomic_private_json(STATE_PATH, {
            "campaign_pid": process.pid, "started_at": time.time(),
            "log_file": str(log_path), "command": command,
        })
        self._campaign_process = process
        return f"Pipeline started as PID {process.pid}; log: {log_path}"

    def _stop(self, *, wait_seconds: float = 12.0) -> str:
        config = self.config()
        stop_path = _resolve(self.root, str(config["stop_file"]))
        processes = _campaign_processes(self.root)
        if not processes:
            stop_path.unlink(missing_ok=True)
            return "No campaign process is running."
        legacy = [row["pid"] for row in processes
                  if "--stop-file" not in str(row.get("command", ""))]
        if legacy:
            raise OperatorError(
                f"campaign processes {legacy} predate cooperative stop support. "
                "No signal was sent. Let them finish, or have the operator explicitly "
                "approve a one-time manual interruption; then start the updated app.")
        pids = [row["pid"] for row in processes]
        _atomic_private_json(stop_path, {
            "requested_at": time.time(), "process_ids": pids,
        })
        deadline = time.time() + max(0.0, wait_seconds)
        while time.time() < deadline and _campaign_processes(self.root):
            time.sleep(.25)
        remaining = [row["pid"] for row in _campaign_processes(self.root)]
        if remaining:
            return (
                f"Stop requested; processes {remaining} are finishing their current "
                "problems and will take no new leases. Wait and refresh.")
        return "Pipeline stopped cleanly: " + ", ".join(map(str, pids))

    def _terminate_campaign_processes(
            self, processes: list[dict[str, Any]], *, wait_seconds: float = 8.0,
    ) -> str:
        """Terminate only this checkout's campaign process trees, then verify exit.

        Campaigns are launched in their own process group/session. Update + restart
        first requests the cooperative stop marker; this escalation exists because
        a worker blocked in a multi-hour browser Future cannot inspect that marker.
        Exchange-level caches make the interrupted generation safely retryable.
        """
        pids = sorted({int(row.get("pid", 0)) for row in processes
                       if int(row.get("pid", 0)) > 0})
        if not pids:
            return "No campaign process required termination."
        for pid in pids:
            try:
                if self.platform.startswith("win"):
                    _run(["taskkill", "/PID", str(pid), "/T"], timeout=10)
                else:
                    os.killpg(pid, signal.SIGTERM)
            except OSError:
                try:
                    os.kill(pid, signal.SIGTERM)
                except OSError:
                    pass
        deadline = time.time() + max(0.0, wait_seconds)
        while time.time() < deadline and _campaign_processes(self.root):
            time.sleep(.25)
        remaining = [row["pid"] for row in _campaign_processes(self.root)]
        for pid in remaining:
            try:
                if self.platform.startswith("win"):
                    _run(["taskkill", "/F", "/PID", str(pid), "/T"], timeout=10)
                else:
                    os.killpg(pid, signal.SIGKILL)
            except OSError:
                try:
                    os.kill(pid, signal.SIGKILL)
                except OSError:
                    pass
        final_deadline = time.time() + 3.0
        while time.time() < final_deadline and _campaign_processes(self.root):
            time.sleep(.1)
        still_running = [row["pid"] for row in _campaign_processes(self.root)]
        if still_running:
            raise OperatorError(
                f"campaign processes did not exit after termination: {still_running}")
        return "Terminated campaign process trees: " + ", ".join(map(str, pids))

    def _update_restart(self) -> str:
        """One-click update that cannot stall behind a multi-hour generation."""
        initial = _campaign_processes(self.root)
        stop_message = self._stop(wait_seconds=15.0)
        termination_message = ""
        remaining = _campaign_processes(self.root)
        if remaining:
            termination_message = self._terminate_campaign_processes(remaining)
        killed = self._kill_orphaned_browser_profile()
        update_message = self._safe_update()
        start_message = self._start()
        pieces = [stop_message, termination_message, update_message, start_message]
        if killed:
            pieces.append(f"Cleared {killed} orphan browser process(es).")
        if not initial:
            pieces[0] = "No running campaign needed stopping."
        return " ".join(piece for piece in pieces if piece)

    def _kill_orphaned_browser_profile(self) -> int:
        """Kill browser processes still holding THIS checkout's ChatGPT profile.

        A watchdog/hard exit can orphan the campaign's Chromium; because the
        profile is single-instance, a leftover browser would block the relaunch.
        Matches ONLY processes whose command references the resolved profile
        path, so the operator's personal browsers are never touched.
        """
        profile = str(_resolve(self.root, str(self.config()["chatgpt_profile"])))
        pids: list[int] = []
        try:
            if os.name == "nt":
                script = ("Get-CimInstance Win32_Process | "
                          "Select-Object ProcessId,CommandLine | ConvertTo-Json -Compress")
                result = _run(["powershell.exe", "-NoProfile", "-NonInteractive",
                               "-Command", script], timeout=8)
                try:
                    payload = json.loads(result.stdout or "[]")
                except json.JSONDecodeError:
                    payload = []
                for record in (payload if isinstance(payload, list) else [payload]):
                    command = str(record.get("CommandLine") or "")
                    pid = int(record.get("ProcessId") or 0)
                    if pid and profile in command and (
                            "chrome" in command.lower() or "chromium" in command.lower()):
                        pids.append(pid)
            else:
                result = _run(["ps", "-axo", "pid=,command="], timeout=5)
                for line in result.stdout.splitlines():
                    match = re.match(r"\s*(\d+)\s+(.*)", line)
                    if not match:
                        continue
                    pid, command = int(match.group(1)), match.group(2)
                    if profile in command and "chrom" in command.lower():
                        pids.append(pid)
        except OSError:
            return 0
        killed = 0
        for pid in pids:
            try:
                os.kill(pid, signal.SIGTERM)
                killed += 1
            except OSError:
                pass
        if pids:
            time.sleep(2.0)
            for pid in pids:
                try:
                    os.kill(pid, signal.SIGKILL)
                except OSError:
                    pass
        return killed

    def supervise_once(self) -> str:
        """One monitor tick: relaunch a campaign that died unexpectedly.

        Restart happens ONLY when: auto-restart is enabled, a campaign was
        started from this console, no campaign process is currently running, the
        operator did not request a stop (stop-file absent), and the last known
        exit was not a clean rc 0. Bounded by ``auto_restart_max_in_window``
        restarts per ``auto_restart_window_seconds`` — exceeding it PAUSES
        auto-restart (a genuinely broken environment needs a human, not a
        hot-loop). Safe to call on a fixed interval; never raises.
        """
        config = self.config()
        if not bool(config.get("auto_restart", True)):
            return "auto-restart disabled"
        with self.lock:
            if self.job["running"]:
                return f"job running ({self.job['name']}); skip"
        try:
            state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return "no campaign state; nothing to supervise"
        if not int(state.get("campaign_pid", 0) or 0):
            return "no campaign tracked"
        now = time.time()
        window = float(config.get("auto_restart_window_seconds", 900) or 900)
        if _campaign_processes(self.root):
            # Healthy. Once it has been stable for a full window, reset the
            # restart budget so a later, independent failure is recoverable.
            started = float(state.get("started_at", 0.0) or 0.0)
            if started and now - started >= window:
                self._restart_history = []
                self._autorestart_paused = False
            return "campaign running"
        stop_path = _resolve(self.root, str(config["stop_file"]))
        if stop_path.is_file():
            return "stopped by request; not restarting"
        process = self._campaign_process
        if process is not None and process.poll() == 0:
            return "clean exit (rc 0); not restarting"
        if self._autorestart_paused:
            return "auto-restart paused (manual attention needed)"
        self._restart_history = [t for t in self._restart_history if now - t < window]
        if len(self._restart_history) >= int(config.get("auto_restart_max_in_window", 5) or 5):
            self._autorestart_paused = True
            self.log(f"auto-restart PAUSED: too many restarts within {int(window)}s "
                     "— campaign keeps dying; manual attention needed")
            return "auto-restart paused after too many restarts"
        killed = self._kill_orphaned_browser_profile()
        self._restart_history.append(now)
        try:
            message = self._start()
        except OperatorError as exc:
            self.log(f"auto-restart attempt failed: {exc}")
            return f"auto-restart failed: {exc}"
        self.log(f"AUTO-RESTARTED campaign (cleared {killed} orphan browser "
                 f"process(es)): {message}")
        return f"auto-restarted: {message}"

    def _install_app(self) -> str:
        """Install a native launcher; all control logic stays in this checkout."""
        if self.platform == "darwin":
            source = self.root / "EGMRA Operator.app"
            if not source.is_dir():
                raise OperatorError("EGMRA Operator.app is missing from this checkout")
            destination = self.home / "Applications" / source.name
            support = self.home / "Library" / "Application Support" / "EGMRA Operator"
            destination.parent.mkdir(parents=True, exist_ok=True)
            support.mkdir(parents=True, exist_ok=True)
            shutil.copytree(source, destination, dirs_exist_ok=True)
            (destination / "Contents" / "MacOS" / "egmra-operator").chmod(0o755)
            pointer = support / "repo-path"
            pointer.write_text(str(self.root.resolve()) + "\n", encoding="utf-8")
            pointer.chmod(0o600)
            return f"Installed {destination}. Open it from Finder or Spotlight."

        if self.platform.startswith("win"):
            source = self.root / "EGMRA Operator.cmd"
            if not source.is_file():
                raise OperatorError("EGMRA Operator.cmd is missing from this checkout")
            local = Path(self.environment.get(
                "LOCALAPPDATA", self.home / "AppData" / "Local"))
            app_dir = local / "EGMRA Operator"
            app_dir.mkdir(parents=True, exist_ok=True)
            destination = app_dir / source.name
            shutil.copyfile(source, destination)
            pointer = app_dir / "repo-path.txt"
            pointer.write_text(str(self.root.resolve()) + "\n", encoding="utf-8")
            shortcut_paths = [self.home / "Desktop" / "EGMRA Operator.lnk"]
            appdata = self.environment.get("APPDATA")
            if appdata:
                shortcut_paths.append(
                    Path(appdata) / "Microsoft" / "Windows" / "Start Menu"
                    / "Programs" / "EGMRA Operator.lnk")
            installed = []
            for shortcut in shortcut_paths:
                shortcut.parent.mkdir(parents=True, exist_ok=True)
                shortcut_ps = str(shortcut).replace("'", "''")
                destination_ps = str(destination).replace("'", "''")
                root_ps = str(self.root).replace("'", "''")
                script = (
                    "$w=New-Object -ComObject WScript.Shell;"
                    f"$s=$w.CreateShortcut('{shortcut_ps}');"
                    f"$s.TargetPath='{destination_ps}';"
                    f"$s.WorkingDirectory='{root_ps}';"
                    "$s.Save()")
                result = _run([
                    "powershell.exe", "-NoProfile", "-NonInteractive",
                    "-Command", script], timeout=20)
                if result.returncode == 0:
                    installed.append(str(shortcut))
            return (
                f"Installed Windows launcher at {destination}. "
                + ("Shortcuts: " + ", ".join(installed) if installed else
                   "Open that .cmd directly; shortcut creation was unavailable."))

        applications = self.home / ".local" / "share" / "applications"
        applications.mkdir(parents=True, exist_ok=True)
        destination = applications / "egmra-operator.desktop"
        python = _venv_python(self.root)
        content = (
            "[Desktop Entry]\nType=Application\nName=EGMRA Operator\n"
            f"Exec={shlex.quote(str(python))} -u "
            f"{shlex.quote(str(self.root / 'operator_console.py'))}\n"
            "Terminal=false\nIcon=utilities-terminal\nCategories=Science;Development;\n")
        destination.write_text(content, encoding="utf-8")
        destination.chmod(0o755)
        return f"Installed {destination}. Open EGMRA Operator from the application menu."

    def _chatgpt_login(self) -> str:
        """Open the persistent ChatGPT profile headed for human login/2FA."""
        if _campaign_processes(self.root):
            raise OperatorError(
                "stop this checkout's pipeline before opening the same ChatGPT profile")
        config = self.config()
        profile = _resolve(self.root, str(config["chatgpt_profile"]))
        private_env = _load_shell_exports(
            _resolve(self.root, str(config["keys_file"])))
        private_env.update(_load_shell_exports(self.root / ".env"))
        url = private_env.get("CHATGPT_PROJECT_URL", "https://chatgpt.com")
        try:
            from playwright.sync_api import Error as PlaywrightError
            from playwright.sync_api import sync_playwright
        except ImportError as exc:
            raise OperatorError(
                "Playwright is not installed; complete dependency setup first") from exc
        profile.mkdir(parents=True, exist_ok=True)
        self.log("Opening headed ChatGPT login window; close it when login/2FA is complete")
        try:
            with sync_playwright() as playwright:
                context = playwright.chromium.launch_persistent_context(
                    str(profile), headless=False,
                    args=["--disable-blink-features=AutomationControlled"])
                page = context.pages[0] if context.pages else context.new_page()
                page.goto(url, wait_until="domcontentloaded")
                while any(not item.is_closed() for item in context.pages):
                    time.sleep(.5)
                context.close()
        except PlaywrightError as exc:
            raise OperatorError(f"ChatGPT login browser failed: {exc}") from exc
        return "ChatGPT login window closed; profile retained locally."

    def perform(self, action: str, payload: dict[str, Any]) -> str:
        if action == "save_config":
            _save_config(dict(payload.get("config") or {}), self.root)
            return "Local machine configuration saved (mode 600, gitignored)."
        if action == "check_update":
            status = self._git_state(self.config(), fetch=True)
            return f"{status['relation']}: local {status['local'][:8]}, remote {status['remote'][:8]}"
        if action == "update":
            return (
                self._update_restart() if _campaign_processes(self.root)
                else self._safe_update())
        if action == "start":
            return self._start()
        if action == "stop":
            return self._stop()
        if action == "install_app":
            return self._install_app()
        if action == "chatgpt_login":
            return self._chatgpt_login()
        if action == "update_restart":
            return self._update_restart()
        raise OperatorError(f"unknown action: {action}")

    def launch_job(self, action: str, payload: dict[str, Any]) -> None:
        with self.lock:
            if self.job["running"]:
                raise OperatorError(f"another action is running: {self.job['name']}")
            self.job = {"running": True, "name": action, "message": "",
                        "ok": None, "started_at": time.time(), "finished_at": None}
        self.log(f"Starting action: {action}")

        def run() -> None:
            try:
                message = self.perform(action, payload)
            except Exception as exc:  # action boundary: report, never crash server
                ok, message = False, f"{type(exc).__name__}: {exc}"
            else:
                ok = True
            self.log(message)
            with self.lock:
                self.job.update({"running": False, "ok": ok, "message": message,
                                 "finished_at": time.time()})

        threading.Thread(target=run, name=f"egmra-operator-{action}", daemon=True).start()


HTML = r'''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>EGMRA Operator</title><style>
:root{--bg:#eeece3;--ink:#1e2220;--line:#c4c5bd;--paper:#faf9f3;--green:#29775e;--red:#bd4736;--amber:#ae781f;--blue:#35677f}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:13px ui-monospace,SFMono-Regular,Menlo,monospace}header{height:74px;border-bottom:1px solid var(--ink);display:flex;align-items:center;justify-content:space-between;padding:0 4vw;position:sticky;top:0;background:rgba(238,236,227,.96);z-index:3}h1{font:600 24px Georgia,serif;margin:0}header span{font-size:10px;color:#656a66}main{max-width:1200px;margin:auto;padding:30px 4vw 60px}.grid{display:grid;grid-template-columns:1fr 1fr;gap:18px}.panel{border-top:1px solid var(--ink);padding-top:13px}.panel h2{font:600 18px Georgia,serif;margin:0 0 14px}.cards{display:grid;grid-template-columns:repeat(2,1fr);gap:1px;background:var(--line);border:1px solid var(--line)}.card{background:var(--paper);padding:13px}.card small,.card strong{display:block}.card small{font-size:8px;color:#676b68;text-transform:uppercase;margin-bottom:7px}.card strong{font-size:11px;overflow-wrap:anywhere}.ok{color:var(--green)}.bad{color:var(--red)}.actions{display:grid;grid-template-columns:1fr 1fr;gap:8px}.actions button{min-height:42px;border:1px solid var(--ink);background:transparent;font:600 10px inherit;cursor:pointer}.actions button:hover{background:var(--ink);color:var(--bg)}.actions .primary{background:var(--green);border-color:var(--green);color:white}.actions .danger{color:var(--red);border-color:var(--red)}.job{margin:12px 0;padding:12px;border-left:3px solid var(--amber);background:var(--paper);font-size:10px;line-height:1.5}.job.good{border-color:var(--green)}.job.fail{border-color:var(--red)}pre{background:var(--ink);color:#d9ded9;padding:14px;height:230px;overflow:auto;font-size:9px;line-height:1.5;white-space:pre-wrap}.config{display:grid;grid-template-columns:1fr 1fr;gap:9px}.field label{font-size:8px;text-transform:uppercase;color:#676b68;display:block;margin-bottom:4px}.field input{width:100%;height:34px;border:1px solid var(--line);background:var(--paper);padding:0 8px;font:10px inherit}.field.check{display:flex;align-items:end;gap:8px;padding-bottom:8px}.field.check label{margin:0}.footer-note{font-size:9px;line-height:1.6;color:#676b68;margin-top:13px}@media(max-width:750px){.grid{grid-template-columns:1fr}.config{grid-template-columns:1fr}.actions{grid-template-columns:1fr}header{padding:0 14px}main{padding:22px 14px}}</style></head><body><header><div><span>LOCALHOST ONLY / MACHINE CONTROL</span><h1>EGMRA Operator</h1></div><span id="clock">Loading…</span></header><main><div class="grid"><section class="panel"><h2>This computer</h2><div id="cards" class="cards"></div><div id="job" class="job">Ready.</div><div class="actions"><button data-action="check_update">Check for update</button><button data-action="update">Safe update</button><button class="primary" data-action="start">Run / resume pipeline</button><button data-action="update_restart">Update + restart</button><button class="danger" data-action="stop">Stop cleanly</button><button id="refresh">Refresh</button></div><p class="footer-note">Safe update is fast-forward only. Tracked and untracked local edits are backed up in a retained Git stash and reapplied. Ignored keys, browser cookies, runs, checkpoints, outcomes, reviews, targets, local config, and Lean caches are never touched.</p></section><section class="panel"><h2>Activity log</h2><pre id="log">No activity yet.</pre></section></div><section class="panel" style="margin-top:26px"><h2>Per-machine settings</h2><div id="config" class="config"></div><div class="actions" style="margin-top:12px"><button class="primary" id="save">Save local settings</button></div><p class="footer-note">Saved to operator.local.json (mode 600, gitignored). Secret values are never displayed here; edit egmra.keys.sh directly if credentials change.</p></section></main><script>
const TOKEN='__TOKEN__';let last={},submitting=false;const $=s=>document.querySelector(s);const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":"&#39;"}[c]));
const labels={branch:'Git branch',campaign_id:'Campaign ID',workers:'Browser workers (1–5)',aristotle_max_concurrent:'Aristotle proof slots (1–5)',state_store:'State store (postgres or file)',worker_rounds:'Reasoning rounds per branch',lean_repair_rounds:'Lean repair rounds',hostile_review:'Hostile reviewers',budget:'Problem budget',chatgpt_profile:'ChatGPT profile directory',policy:'Signed policy path',lean_project:'Lean project',lean_dev_repl:'Warm Lean REPL command',keys_file:'Keys file',triage_dir:'Triage directory',triage_lane:'Triage lane',max_problems:'Maximum problems (0 = all ranked)',reviews_dir:'Reviews directory',targets_dir:'Targets directory',checkpoint_dir:'Checkpoint directory',lemma_library:'Lemma library',log_file:'Log file'};
async function api(path,options={}){options.headers={...(options.headers||{}),'Content-Type':'application/json','X-EGMRA-Token':TOKEN};const r=await fetch(path,options);const d=await r.json();if(!r.ok)throw new Error(d.error||r.statusText);return d}
function render(d){last=d;$('#clock').textContent=new Date().toLocaleTimeString();const p=d.prerequisites,g=d.git,c=d.campaign;const chatReady=p.chatgpt_profile&&p.chatgpt_workspace;const leanReady=p.lean_project&&p.lean_repl&&p.policy;const stateReady=p.postgres_dsn&&p.postgres_driver;const rows=[['Pipeline',c.running?`Running · ${c.processes.map(x=>x.pid).join(', ')}`:'Stopped',c.running],['Version',`${g.relation} · ${g.local.slice(0,8)}`,g.relation==='current'],['Shared state',stateReady?'Driver + configuration ready':'Driver / configuration missing',stateReady],['Keys',p.keys_file&&p.aristotle_key?'Verified + provider configured':'Missing / invalid',p.keys_file&&p.aristotle_key],['ChatGPT',chatReady?'Profile present; login is human-verified':p.chatgpt_profile?'Workspace URL missing':'Profile missing',chatReady],['Lean + policy',leanReady?'Build + REPL + signature ready':'Not ready',leanReady]];$('#cards').innerHTML=rows.map(x=>`<div class="card"><small>${x[0]}</small><strong class="${x[2]?'ok':'bad'}">${esc(x[1])}</strong></div>`).join('');const j=d.job;$('#job').className='job '+(j.ok===true?'good':j.ok===false?'fail':'');$('#job').textContent=j.running?`Running: ${j.name}…`:j.message||'Ready.';document.querySelectorAll('[data-action]').forEach(button=>button.disabled=Boolean(j.running||submitting));$('#log').textContent=(d.log||[]).join('\n')||'No activity yet.';$('#log').scrollTop=$('#log').scrollHeight;if(!$('#config').children.length){$('#config').innerHTML=Object.entries(labels).map(([k,l])=>`<div class="field"><label>${l}</label><input data-key="${k}" value="${esc(d.config[k])}"></div>`).join('')+`<div class="field check"><input id="prefer" type="checkbox" ${d.config.prefer_solvable?'checked':''}><label for="prefer">Prefer most solvable pending problems</label></div>`}}
async function refresh(fetch=false){if(submitting)return;try{render(await api('/api/status'+(fetch?'?fetch=1':'')))}catch(e){$('#job').textContent=e.message;$('#job').className='job fail'}}
document.querySelectorAll('[data-action]').forEach(b=>b.onclick=async()=>{if(submitting)return;submitting=true;document.querySelectorAll('[data-action]').forEach(button=>button.disabled=true);$('#job').textContent=`Starting: ${b.dataset.action}…`;try{await api('/api/action',{method:'POST',body:JSON.stringify({action:b.dataset.action})})}catch(e){alert(e.message)}finally{submitting=false;refresh()}});$('#refresh').onclick=()=>refresh();$('#save').onclick=async()=>{const config={...last.config};document.querySelectorAll('[data-key]').forEach(i=>config[i.dataset.key]=i.type==='number'?Number(i.value):i.value);config.workers=Number(config.workers);config.aristotle_max_concurrent=Number(config.aristotle_max_concurrent);config.max_problems=Number(config.max_problems);config.prefer_solvable=$('#prefer').checked;await api('/api/action',{method:'POST',body:JSON.stringify({action:'save_config',config})});refresh()};refresh();setInterval(refresh,2000);
</script></body></html>'''

HTML = HTML.replace(
    '<button id="refresh">Refresh</button>',
    '<button data-action="install_app">Install / refresh app</button>'
    '<button data-action="chatgpt_login">Open ChatGPT login</button>'
    '<button id="refresh">Refresh</button>',
)


class Handler(BaseHTTPRequestHandler):
    operator: Operator
    token: str

    def log_message(self, _format: str, *_args: object) -> None:
        return

    def _json(self, value: Any, status: int = 200) -> None:
        payload = json.dumps(value).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self) -> None:
        if self.path == "/" or self.path.startswith("/?"):
            payload = HTML.replace("__TOKEN__", self.token).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return
        if self.path.startswith("/api/status"):
            try:
                value = self.operator.status(fetch="fetch=1" in self.path)
            except Exception as exc:
                self._json({"error": f"{type(exc).__name__}: {exc}"}, 500)
            else:
                self._json(value)
            return
        self.send_error(HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:
        if self.path != "/api/action":
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        origin = self.headers.get("Origin", "")
        expected_origins = {f"http://{HOST}:{self.server.server_port}",
                            f"http://localhost:{self.server.server_port}"}
        if self.headers.get("X-EGMRA-Token") != self.token \
                or (origin and origin not in expected_origins) \
                or not self.headers.get("Content-Type", "").startswith("application/json"):
            self._json({"error": "invalid local action token/origin"}, 403)
            return
        try:
            length = min(int(self.headers.get("Content-Length", "0")), 1_000_000)
            body = json.loads(self.rfile.read(length))
            self.operator.launch_job(str(body.get("action", "")), body)
        except (ValueError, json.JSONDecodeError, OperatorError) as exc:
            self._json({"error": str(exc)}, 400)
        else:
            self._json({"accepted": True}, 202)


def main() -> int:
    parser = argparse.ArgumentParser(description="local-only EGMRA update/launch console")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args()
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    _load_config(ROOT)  # create private local defaults on first launch
    url = f"http://{HOST}:{args.port}/"
    try:
        with urlopen(url, timeout=.7) as response:
            existing = response.read(4096).decode("utf-8", errors="ignore")
        if "EGMRA Operator" in existing:
            print(f"EGMRA Operator is already running: {url}")
            if not args.no_browser:
                webbrowser.open(url)
            return 0
    except (OSError, URLError):
        pass
    operator = Operator(ROOT)
    token = os.urandom(24).hex()
    handler = type("OperatorHandler", (Handler,), {"operator": operator, "token": token})
    try:
        server = ThreadingHTTPServer((HOST, args.port), handler)
    except OSError as exc:
        raise OperatorError(
            f"cannot bind {url}; another program is using that port: {exc}") from exc
    url = f"http://{HOST}:{server.server_port}/"
    print(f"EGMRA Operator: {url}")
    print("Localhost only. Press Ctrl-C to stop the console (campaign continues).")
    # Auto-restart supervisor: relaunch a campaign that dies unexpectedly (e.g.
    # the liveness watchdog force-exited a wedged process) while this console is
    # open. Respects a requested stop and a clean exit; bounded to avoid a
    # hot-loop. Runs only while the console is running.
    supervisor_stop = threading.Event()

    def _supervisor_loop() -> None:
        while not supervisor_stop.wait(15.0):
            try:
                operator.supervise_once()
            except Exception:  # noqa: BLE001 - supervisor must never crash the console
                pass

    threading.Thread(target=_supervisor_loop, name="egmra-operator-supervisor",
                     daemon=True).start()
    if not args.no_browser:
        threading.Timer(.4, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        supervisor_stop.set()
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
