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


def _run(*args: str, cwd: Path = ROOT, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        args, cwd=cwd, check=check, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
    )


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
    copy = dict(document)
    copy.pop("generated_at", None)
    return copy


def refresh(worktree: Path) -> bool:
    _ensure_worktree(worktree)
    live_path = worktree / "status_site" / "data.json"
    with tempfile.TemporaryDirectory(prefix="egmra-status-") as directory:
        fresh_path = Path(directory) / "data.json"
        result = _run(
            sys.executable, str(ROOT / "status_site" / "build_data.py"),
            "--output", str(fresh_path),
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
