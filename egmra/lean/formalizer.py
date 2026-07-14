"""Autonomous formalization worker (DECISIONS.md D-B: Aristotle as a research tool).

`egmra formalize` re-checks a candidate Lean proof; this module lets the research
controller *autonomously* obtain that candidate during `egmra run`/campaigns. A
:class:`Formalizer` turns a pinned obligation — a declaration name and its intended
Lean type — into candidate Lean **source**; the worker then emits a formal
candidate that the pinned kernel re-checks on the existing 4.6 path.

Trust boundary (unchanged and central): the vendor supplies only the *proof term*.
The *obligation* (``expected_type`` + ``declaration_name``) is pinned by the caller
and hashed deterministically, and the produced Lean is UNTRUSTED — it is admitted
only after the pinned local kernel verifies ``example : <expected_type> :=
@<declaration_name>`` (plus an axiom-whitelist audit). A vendor ``COMPLETE`` never
promotes on its own.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

# Defensive ceiling on how much candidate Lean text we read back from a vendor
# quarantine (the archive extractor already enforces per-entry / total limits).
_MAX_SOURCE_BYTES = 2_000_000


class Formalizer(Protocol):
    """Produce candidate Lean source for a pinned obligation (untrusted output)."""

    formalizer_id: str

    def formalize(self, *, declaration_name: str, expected_type: str,
                  informal_statement: str, previous_source: str = "",
                  kernel_feedback: str = "") -> str | None:
        """Return Lean source proving ``declaration_name : expected_type``, or None.

        The returned source is UNTRUSTED: the caller re-checks it with the pinned
        kernel against the exact pinned obligation. Returns None when the
        formalizer is unavailable (a transient provider outage — never a
        mathematical failure).  ``previous_source``/``kernel_feedback`` carry a
        rejected attempt plus the pinned kernel's diagnostics for a bounded
        repair round; they never change the obligation being proved.
        """


def build_formalization_prompt(*, declaration_name: str, expected_type: str,
                               informal_statement: str, previous_source: str = "",
                               kernel_feedback: str = "") -> str:
    """A prompt that pins the exact obligation the vendor must prove."""
    repair = ""
    if previous_source or kernel_feedback:
        repair = (
            "\n\nREPAIR ROUND — a previous attempt was REJECTED by the pinned "
            "Lean kernel. Fix the proof; the obligation above is unchanged.\n"
            f"Kernel diagnostics:\n{kernel_feedback[:1200] or '(none provided)'}\n"
            + (
                f"\nRejected source (for reference; replace as needed):\n"
                f"```lean\n{previous_source[:4000]}\n```\n"
                if previous_source else ""
            )
        )
    return (
        "Produce a single self-contained Lean 4 file (Mathlib is available; begin "
        "with `import Mathlib`) that defines the declaration below with EXACTLY "
        "this name and type and proves it:\n\n"
        f"    {declaration_name} : {expected_type}\n\n"
        f"Informal statement (context only): {informal_statement}\n\n"
        "Requirements:\n"
        f"- The declaration MUST be named `{declaration_name}` and have EXACTLY the "
        "type above (do not weaken, generalize, or restate it).\n"
        "- Do NOT use `sorry`, `admit`, `native_decide`, or any axiom beyond "
        "Mathlib's classical logic.\n"
        "- Return only Lean source."
        + repair
    )


def read_lean_source(quarantine_dir: Path, *, max_bytes: int = _MAX_SOURCE_BYTES) -> str | None:
    """Concatenate the candidate ``.lean`` files from a vendor quarantine.

    The directory was already extracted under strict traversal/symlink/bomb limits
    (:func:`egmra.lean.aristotle_api.safe_extract_archive`); we still refuse to
    follow symlinks and cap the total bytes read. Returns None when no Lean is
    present.
    """
    root = Path(quarantine_dir)
    if root.is_symlink() or not root.is_dir():
        return None
    parts: list[str] = []
    total = 0
    for path in sorted(root.rglob("*.lean")):
        if path.is_symlink() or not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        total += len(text.encode("utf-8", errors="ignore"))
        if total > max_bytes:
            break
        parts.append(text)
    source = "\n".join(part.strip("\n") for part in parts if part.strip())
    return source or None


@dataclass
class AristotleFormalizer:
    """A live :class:`Formalizer` backed by the official Aristotle SDK.

    ``client`` is an :class:`~egmra.lean.aristotle_sdk.AristotleSdkClient` (or any
    object exposing ``submit``/``fetch``/``close``); it is injectable so the
    submit→fetch→read-source flow is exercised by a fake in tests. Reachable live
    only with ``ARISTOTLE_API_KEY`` + a built pinned Lean project.
    """

    client: Any
    formalizer_id: str = "aristotle"

    def formalize(self, *, declaration_name: str, expected_type: str,
                  informal_statement: str, previous_source: str = "",
                  kernel_feedback: str = "") -> str | None:
        prompt = build_formalization_prompt(
            declaration_name=declaration_name, expected_type=expected_type,
            informal_statement=informal_statement,
            previous_source=previous_source, kernel_feedback=kernel_feedback)
        submission = self.client.submit(prompt)
        artifact = self.client.fetch(submission, wait=True)
        # The vendor archive is already extracted into a hardened quarantine and
        # is NEVER promotable on arrival; we only read the source to re-check it.
        return read_lean_source(Path(artifact.quarantine_dir))

    def close(self) -> None:
        close = getattr(self.client, "close", None)
        if callable(close):  # pragma: no cover - only the live SDK holds a loop
            try:
                close()
            except Exception:  # noqa: BLE001 - best-effort teardown
                pass
