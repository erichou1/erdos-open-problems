#!/usr/bin/env python3
"""Independent local Lean-kernel re-verification of an Aristotle project.

Aristotle returns a Lean project archive; trusting its self-reported "no sorry"
is weaker than the kernel itself. This module rebuilds the project with
`lake build` so the Lean kernel is the ground truth (matching the strongest
community practice on erdosproblems.com). It fails safe: if Lean/lake is not
installed it reports ``tool_unavailable`` rather than a false pass, so callers
can distinguish a real kernel check from a vendor-reported one.
"""

from __future__ import annotations

import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

# Terminal verification statuses.
KERNEL_VERIFIED = "kernel_verified"
BUILD_FAILED = "build_failed"
HAS_SORRY = "has_sorry"
TOOL_UNAVAILABLE = "tool_unavailable"
NO_PROJECT = "no_project"


# ── shared Lean source helpers (also used by aristotle_verifier) ─────────────

def strip_lean_comments(source: str) -> str:
    source = re.sub(r"/-.*?-/", " ", source, flags=re.DOTALL)
    source = re.sub(r"--[^\n]*", " ", source)
    return source


def has_incomplete_proof(lean_source: str) -> bool:
    """True if the Lean source still contains a `sorry`/`admit` placeholder."""
    return bool(re.search(r"\b(sorry|admit)\b", strip_lean_comments(lean_source)))


def find_lean_proof(root: Path) -> Path | None:
    mains = sorted(Path(root).rglob("Main.lean"))
    if mains:
        return mains[0]
    leans = sorted(p for p in Path(root).rglob("*.lean") if p.name != "lakefile.lean")
    return leans[0] if leans else None


def extract_formal_statements(lean_source: str) -> list[str]:
    """Return the signatures of every top-level `theorem`/`lemma` (name + type).

    Used for statement-fidelity review: the human/independent check that the
    Lean theorem faithfully matches the informal Erdos statement.
    """
    stripped = strip_lean_comments(lean_source)
    statements: list[str] = []
    for match in re.finditer(
        r"\b(theorem|lemma)\s+([A-Za-z0-9_'.]+)([\s\S]*?):=", stripped
    ):
        signature = " ".join(
            f"{match.group(1)} {match.group(2)} {match.group(3)}".split()
        )
        statements.append(signature)
    return statements


# ── local kernel verification ────────────────────────────────────────────────

@dataclass(frozen=True)
class LeanVerification:
    status: str
    kernel_verified: bool
    detail: str
    project_root: str = ""
    lean_toolchain: str = ""


def lake_available(lake_path: str = "lake") -> bool:
    return shutil.which(lake_path) is not None or Path(lake_path).exists()


def find_project_root(extracted: Path) -> Path | None:
    for name in ("lakefile.toml", "lakefile.lean"):
        matches = sorted(Path(extracted).rglob(name))
        if matches:
            return matches[0].parent
    return None


def _read_toolchain(root: Path) -> str:
    toolchain = root / "lean-toolchain"
    if toolchain.is_file():
        return toolchain.read_text(encoding="utf-8", errors="ignore").strip()
    return ""


def verify_project(
    extracted: Path, *, runner=None, lake_path: str = "lake",
    fetch_cache: bool = True, timeout_s: float = 3600.0,
) -> LeanVerification:
    """Rebuild the extracted Lean project and report a kernel verdict.

    ``runner`` (callable ``(args, cwd) -> CompletedProcess``) is injectable for
    tests; by default it shells out to ``lake``.
    """
    root = find_project_root(Path(extracted))
    if root is None:
        return LeanVerification(NO_PROJECT, False, "no lakefile.toml/lakefile.lean found")
    toolchain = _read_toolchain(root)

    lean_file = find_lean_proof(root)
    if lean_file is None:
        return LeanVerification(NO_PROJECT, False, "no Lean source found",
                                str(root), toolchain)
    if has_incomplete_proof(lean_file.read_text(encoding="utf-8", errors="ignore")):
        return LeanVerification(HAS_SORRY, False, "Lean source contains sorry/admit",
                                str(root), toolchain)

    if runner is None:
        if not lake_available(lake_path):
            return LeanVerification(
                TOOL_UNAVAILABLE, False,
                "lake/Lean not installed; cannot run an independent kernel check",
                str(root), toolchain,
            )

        def runner(args, cwd):  # noqa: ANN001
            return subprocess.run(
                [lake_path, *args], cwd=cwd, capture_output=True, text=True,
                check=False, timeout=timeout_s,
            )

    try:
        if fetch_cache:
            runner(["exe", "cache", "get"], str(root))  # best-effort Mathlib cache
        build = runner(["build"], str(root))
    except FileNotFoundError:
        return LeanVerification(TOOL_UNAVAILABLE, False, "lake executable not found",
                                str(root), toolchain)
    except subprocess.TimeoutExpired:
        return LeanVerification(BUILD_FAILED, False, f"lake build timed out after {timeout_s:.0f}s",
                                str(root), toolchain)

    if getattr(build, "returncode", 1) == 0:
        return LeanVerification(KERNEL_VERIFIED, True, "lake build succeeded; no sorry",
                                str(root), toolchain)
    detail = (getattr(build, "stderr", "") or getattr(build, "stdout", "") or "").strip()
    return LeanVerification(BUILD_FAILED, False, f"lake build failed: {detail[:400]}",
                            str(root), toolchain)
