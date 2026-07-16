"""Near-live public snapshot refresher for the Vercel status site.

The campaign and its artifacts live on this machine; exposing the Neon DSN to
the browser would be unsafe. This daemon instead rebuilds the credential-free
snapshot every minute and force-updates ONE commit on the dedicated
``status-live`` branch only when semantic data changes. Main-branch history
stays clean and the website polls that branch every minute.

Run once:
    source egmra.keys.sh
    .venv/bin/python status_site/live_refresh.py --once

Run continuously:
    source egmra.keys.sh
    nohup .venv/bin/python -u status_site/live_refresh.py \
      > /tmp/egmra-status-refresh.log 2>&1 &
"""

from __future__ import annotations

import argparse
import fcntl
import json
import os
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_WORKTREE = Path("/tmp/erdos-status-live")
BRANCH = "status-live"
LOCK_PATH = Path("/tmp/egmra-status-refresh.lock")


def _run(
    *args: str,
    cwd: Path = ROOT,
    check: bool = True,
    env: dict[str, str] | None = None,
    redact: tuple[str, ...] = (),
) -> subprocess.CompletedProcess:
    result = subprocess.run(
        args, cwd=cwd, check=False, text=True, env=env,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
    )
    if check and result.returncode != 0:
        output = result.stdout[-4000:]
        for value in redact:
            if value:
                output = output.replace(value, "<redacted>")
        raise RuntimeError(
            f"command failed ({result.returncode}): {args[0]}\n{output}")
    return result


def _load_private_file(path: Path) -> dict[str, str]:
    """Parse simple shell exports without executing the private file."""
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return {}
    values: dict[str, str] = {}
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
        if name.replace("_", "a").isalnum() and not name[0].isdigit():
            values[name] = value
    return values


def _private_environment() -> dict[str, str]:
    values = _load_private_file(ROOT / "egmra.keys.sh")
    values.update(_load_private_file(ROOT / ".env"))
    return values


def _ensure_worktree(worktree: Path) -> None:
    if (worktree / ".git").exists():
        return
    if worktree.exists():
        shutil.rmtree(worktree)
    remote = _run(
        "git", "ls-remote", "--exit-code", "--heads", "origin", BRANCH,
        check=False,
    )
    if remote.returncode == 0:
        _run("git", "fetch", "origin", BRANCH)
        _run("git", "worktree", "add", "-B", BRANCH, str(worktree),
             f"origin/{BRANCH}")
    else:
        _run("git", "worktree", "add", "-b", BRANCH, str(worktree), "HEAD")


def _semantic(document: dict) -> dict:
    """Return the complete public snapshot for publication comparison.

    ``generated_at`` is a liveness signal: the browser marks a snapshot stale
    after four minutes.  Excluding it here left the immutable ``status-live``
    ref unchanged during quiet but healthy campaign periods, making active
    workers appear stale.  Publishing the timestamp on every refresh keeps
    the dashboard's liveness view honest.
    """
    return dict(document)


def refresh(worktree: Path) -> bool:
    _ensure_worktree(worktree)
    live_path = worktree / "status_site" / "data.json"
    with tempfile.TemporaryDirectory(prefix="egmra-status-") as directory:
        fresh_path = Path(directory) / "data.json"
        private = _private_environment()
        build_env = os.environ.copy()
        build_env.update(private)
        _run(
            sys.executable, str(ROOT / "status_site" / "build_data.py"),
            "--output", str(fresh_path),
            env=build_env,
            redact=tuple(private.values()),
        )
        fresh = json.loads(fresh_path.read_text(encoding="utf-8"))
        try:
            previous = json.loads(live_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            previous = {}
        if _semantic(fresh) == _semantic(previous):
            print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} no status change", flush=True)
            return False
        live_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(fresh_path, live_path)
    _run("git", "add", "status_site/data.json", cwd=worktree)
    _run(
        "git", "-c", "user.name=EGMRA Status Bot",
        "-c", "user.email=status-bot@local.invalid",
        "commit", "--amend", "--no-edit", cwd=worktree,
    )
    pushed = _run(
        "git", "push", "--force-with-lease", "-u", "origin",
        f"HEAD:{BRANCH}", cwd=worktree, check=False,
    )
    if pushed.returncode != 0:
        raise RuntimeError(f"status-live push failed:\n{pushed.stdout}")
    print(
        f"{time.strftime('%Y-%m-%d %H:%M:%S')} published "
        f"{fresh['summary']['total']} problems, "
        f"{fresh['summary']['total_runs']} attempts",
        flush=True,
    )
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--interval", type=int, default=60)
    parser.add_argument("--worktree", type=Path, default=DEFAULT_WORKTREE)
    args = parser.parse_args()
    if args.interval < 30:
        parser.error("--interval must be at least 30 seconds")
    LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOCK_PATH.open("w", encoding="utf-8") as lock:
        try:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            print("status refresher is already running", file=sys.stderr)
            return 2
        lock.write(str(os.getpid()))
        lock.flush()
        while True:
            try:
                refresh(args.worktree.resolve())
            except Exception as exc:  # ops aid: log and retry; never touch math state
                print(
                    f"{time.strftime('%Y-%m-%d %H:%M:%S')} refresh error: "
                    f"{type(exc).__name__}: {exc}",
                    file=sys.stderr, flush=True,
                )
                if args.once:
                    return 1
            if args.once:
                return 0
            time.sleep(args.interval)


if __name__ == "__main__":
    raise SystemExit(main())
