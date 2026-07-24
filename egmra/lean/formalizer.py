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

import os
import json
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

from egmra.provenance.hashing import sha256_hex

# Defensive ceiling on how much candidate Lean text we read back from a vendor
# quarantine (the archive extractor already enforces per-entry / total limits).
_MAX_SOURCE_BYTES = 2_000_000
_ARTIFACT_LINK_NAME = "egmra-artifact-link.json"


def _write_artifact_link(
    quarantine_dir: Path, *, problem_id: str, declaration_name: str,
    expected_type: str, informal_statement: str, project_id: str,
) -> None:
    """Attach search metadata to a vendor draft without conferring authority.

    The sidecar contains no prompt, proof text, credential, or signature. It
    exists only so operations tooling can say which problem produced a draft;
    the Lean kernel and correspondence certificate remain the only formal
    trust path. Persistence failure is an ops miss, never a math failure.
    """
    if not problem_id.strip() or not quarantine_dir.is_dir():
        return
    record = {
        "schema_version": 1,
        "authority": "metadata only; not proof evidence",
        "problem_id": problem_id,
        "declaration_name": declaration_name,
        "expected_type_hash": sha256_hex(expected_type),
        "informal_statement_hash": sha256_hex(informal_statement),
        "aristotle_project_id": project_id,
    }
    path = quarantine_dir / _ARTIFACT_LINK_NAME
    try:
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW
        fd = os.open(path, flags, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(record, handle, sort_keys=True)
            handle.write("\n")
    except OSError:
        return

# The Aristotle service allows at most this many proof tasks in flight per
# ACCOUNT. The budget is shared process-wide across every AristotleFormalizer
# instance (campaign workers each hold their own client, but they share the one
# account), so parallel formalization can never exceed the vendor limit.
_ARISTOTLE_ACCOUNT_LIMIT = 5
_shared_slots: threading.BoundedSemaphore | None = None
_shared_slots_lock = threading.Lock()


def _aristotle_max_concurrent(env: Any = None) -> int:
    """Concurrent-proof budget: EGMRA_ARISTOTLE_MAX_CONCURRENT clamped to 1..5."""
    source = os.environ if env is None else env
    raw = source.get("EGMRA_ARISTOTLE_MAX_CONCURRENT", "")
    try:
        value = int(raw)
    except (TypeError, ValueError):
        return _ARISTOTLE_ACCOUNT_LIMIT
    return max(1, min(_ARISTOTLE_ACCOUNT_LIMIT, value))


def _shared_aristotle_slots() -> threading.BoundedSemaphore:
    global _shared_slots
    with _shared_slots_lock:
        if _shared_slots is None:
            _shared_slots = threading.BoundedSemaphore(_aristotle_max_concurrent())
        return _shared_slots


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
    # Vendor-task slot budget. None = the process-wide shared semaphore (the
    # account allows at most 5 concurrent proofs); injectable for tests.
    slots: Any = None
    # Set by the CLI for the worker's current problem. This only labels the
    # quarantined draft; it is never sent to a trust gate.
    problem_id: str = ""

    def formalize(self, *, declaration_name: str, expected_type: str,
                  informal_statement: str, previous_source: str = "",
                  kernel_feedback: str = "") -> str | None:
        prompt = build_formalization_prompt(
            declaration_name=declaration_name, expected_type=expected_type,
            informal_statement=informal_statement,
            previous_source=previous_source, kernel_feedback=kernel_feedback)
        slots = self.slots if self.slots is not None else _shared_aristotle_slots()
        # Hold one account slot for the task's full submit→completion window so
        # concurrent callers (parallel candidates × campaign workers) can never
        # exceed the vendor's concurrent-proof limit; excess callers just wait.
        with slots:
            submission = self.client.submit(prompt)
            artifact = self.client.fetch(submission, wait=True)
        # The vendor archive is already extracted into a hardened quarantine and
        # is NEVER promotable on arrival; we only read the source to re-check it.
        quarantine_dir = Path(artifact.quarantine_dir)
        _write_artifact_link(
            quarantine_dir,
            problem_id=self.problem_id,
            declaration_name=declaration_name,
            expected_type=expected_type,
            informal_statement=informal_statement,
            project_id=str(getattr(submission, "project_id", "")),
        )
        return read_lean_source(quarantine_dir)

    def close(self) -> None:
        close = getattr(self.client, "close", None)
        if callable(close):  # pragma: no cover - only the live SDK holds a loop
            try:
                close()
            except Exception:  # noqa: BLE001 - best-effort teardown
                pass


def extract_lean_source(text: str) -> str:
    """Extract Lean source from a model reply (fenced block preferred)."""
    if not isinstance(text, str) or not text.strip():
        return ""
    marker = "```lean"
    start = text.find(marker)
    if start < 0:
        marker = "```"
        start = text.find(marker)
    if start >= 0:
        body_start = start + len(marker)
        end = text.find("```", body_start)
        if end > body_start:
            return text[body_start:end].strip()
    # No fence: accept only text that plausibly IS a Lean file.
    stripped = text.strip()
    if stripped.startswith("import ") or "theorem " in stripped or "lemma " in stripped:
        return stripped
    return ""


@dataclass
class ApiFormalizer:
    """A prover portfolio member backed by any :class:`ModelRunner`.

    Point it at an attested API runner (e.g. ``deepseek-api`` — DeepSeek's
    prover models are OpenAI-compatible) for a second, independent formal
    engine beside Aristotle.  Its output is exactly as untrusted as any other
    formalizer's: the pinned kernel re-checks every candidate downstream, so a
    weak or hallucinating provider can waste budget but never mint a proof.
    """

    runner: Any
    formalizer_id: str = "api"

    def formalize(self, *, declaration_name: str, expected_type: str,
                  informal_statement: str, previous_source: str = "",
                  kernel_feedback: str = "") -> str | None:
        prompt = build_formalization_prompt(
            declaration_name=declaration_name, expected_type=expected_type,
            informal_statement=informal_statement,
            previous_source=previous_source, kernel_feedback=kernel_feedback)
        response = self.runner.run(prompt, stage="formalize")
        return extract_lean_source(getattr(response, "text", "")) or None

    def close(self) -> None:
        close = getattr(self.runner, "close", None)
        if callable(close):
            try:
                close()
            except Exception:  # noqa: BLE001 - best-effort teardown
                pass


@dataclass
class PortfolioFormalizer:
    """Try several formal engines in order until one produces a candidate (R6).

    A member outage or empty answer falls through to the next member; the
    portfolio never fabricates source.  Repair rounds forward the kernel
    feedback to every member the same way, so whichever engine answers gets
    the diagnostics.
    """

    members: list[Any]
    formalizer_id: str = "portfolio"

    def formalize(self, *, declaration_name: str, expected_type: str,
                  informal_statement: str, previous_source: str = "",
                  kernel_feedback: str = "") -> str | None:
        for member in self.members:
            try:
                produced = member.formalize(
                    declaration_name=declaration_name,
                    expected_type=expected_type,
                    informal_statement=informal_statement,
                    previous_source=previous_source,
                    kernel_feedback=kernel_feedback,
                )
            except TypeError:
                # A legacy member without repair kwargs still serves round 1.
                if previous_source or kernel_feedback:
                    continue
                try:
                    produced = member.formalize(
                        declaration_name=declaration_name,
                        expected_type=expected_type,
                        informal_statement=informal_statement,
                    )
                except Exception:  # noqa: BLE001 - member outage is not a failure
                    continue
            except Exception:  # noqa: BLE001 - member outage is not a math failure
                continue
            if produced and produced.strip():
                return produced
        return None

    def close(self) -> None:
        for member in self.members:
            close = getattr(member, "close", None)
            if callable(close):
                try:
                    close()
                except Exception:  # noqa: BLE001 - best-effort teardown
                    pass
