"""Email notifications for significant campaign progress (ops aid).

Watches the append-only EGMRA outcome ledgers and the kernel-sealed lemma
library and emails a short summary when something *significant* lands:

* a released certificate (the only authoritative "solved" signal);
* a progress-class public state (the same vocabulary the rerank policy uses);
* salvaged SUPPORTED subsidiary claims or a complete candidate assembly;
* a new kernel-sealed lemma (verified formal progress).

Honesty invariants: this module only ever *reads* pipeline artifacts — it is
telemetry, never a truth or release authority, and a notification failure must
never affect a mathematical outcome (the watcher is fail-open by design).
Credentials are read from the environment only (``EGMRA_SMTP_PASSWORD``) and
are never logged or echoed into messages.
"""

from __future__ import annotations

import json
import os
import smtplib
import time
from dataclasses import dataclass, field
from email.message import EmailMessage
from pathlib import Path
from typing import Any

from egmra.orchestrator.rerank import PROGRESS_STATES

DASHBOARD_URL = "https://egmra-status.vercel.app"

_STATE_SCHEMA = 1


class NotifyError(RuntimeError):
    """Configuration or delivery failure (operational, never mathematical)."""


def classify_outcome(record: dict[str, Any]) -> str | None:
    """Return a significance reason for one outcome record, or ``None``.

    Ordered by strength; only the strongest reason is reported. ``released``
    is the sole solve-grade signal — everything else is progress telemetry.
    """
    if not isinstance(record, dict):
        return None
    if record.get("released"):
        return "release_certificate"
    state = str(record.get("public_state", ""))
    if state in PROGRESS_STATES:
        return f"progress:{state}"
    if record.get("candidate_assembly_complete"):
        return "candidate_assembly_complete"
    salvaged = len(((record.get("salvage") or {}).get("supported")) or [])
    if salvaged:
        return f"salvaged_supported_claims:{salvaged}"
    return None


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    try:
        raw_lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return []
    rows: list[dict[str, Any]] = []
    for raw in raw_lines:
        raw = raw.strip()
        if not raw:
            continue
        try:
            value = json.loads(raw)
        except ValueError:
            value = {}
        rows.append(value if isinstance(value, dict) else {})
    return rows


def _ledger_files(paths: list[Path]) -> list[Path]:
    """Expand ledger arguments; a directory means every ``*.jsonl`` inside it."""
    files: list[Path] = []
    for path in paths:
        if path.is_dir():
            files.extend(sorted(path.glob("*.jsonl")))
        elif path.is_file():
            files.append(path)
    return files


def scan_events(
    *, outcome_paths: list[Path], lemma_path: Path | None,
    state: dict[str, int],
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    """Collect significant events appended since ``state``; return new state.

    ``state`` maps resolved file path -> number of lines already examined.
    Files are append-only JSONL, so a line count is a complete cursor.
    """
    events: list[dict[str, Any]] = []
    new_state = dict(state)
    for path in _ledger_files(outcome_paths):
        key = str(path.resolve())
        rows = _read_jsonl(path)
        seen = int(new_state.get(key, 0))
        for row in rows[seen:]:
            reason = classify_outcome(row)
            if reason:
                events.append({
                    "kind": "outcome",
                    "reason": reason,
                    "problem_id": str(row.get("problem_id", "")),
                    "public_state": str(row.get("public_state", "")),
                    "run_id": str(row.get("run_id", "")),
                    "recorded_at": str(row.get("recorded_at", "")),
                    "ledger": path.name,
                })
        new_state[key] = len(rows)
    if lemma_path is not None and lemma_path.is_file():
        key = str(lemma_path.resolve())
        rows = _read_jsonl(lemma_path)
        seen = int(new_state.get(key, 0))
        for row in rows[seen:]:
            if row.get("declaration_name"):
                events.append({
                    "kind": "lemma",
                    "reason": "kernel_sealed_lemma",
                    "problem_id": str(row.get("problem_id", "")),
                    "declaration_name": str(row.get("declaration_name", "")),
                    "ledger": lemma_path.name,
                })
        new_state[key] = len(rows)
    return events, new_state


def load_state(path: Path) -> dict[str, int] | None:
    """Load the cursor state; ``None`` means "first run" (baseline, no email)."""
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    cursors = document.get("cursors") if isinstance(document, dict) else None
    if not isinstance(cursors, dict):
        return None
    return {str(k): int(v) for k, v in cursors.items()
            if isinstance(v, (int, float))}


def save_state(path: Path, state: dict[str, int]) -> None:
    payload = json.dumps(
        {"schema_version": _STATE_SCHEMA, "cursors": state,
         "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())},
        indent=2, sort_keys=True)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC | os.O_NOFOLLOW, 0o600)
    try:
        os.write(fd, payload.encode("utf-8"))
    finally:
        os.close(fd)
    os.replace(tmp, path)


def _problem_number(problem_id: str) -> str:
    return problem_id.split("-", 1)[1] if "-" in problem_id else problem_id


def format_email(events: list[dict[str, Any]]) -> tuple[str, str]:
    """One plain-text summary email for a batch of significant events."""
    releases = [e for e in events if e["reason"] == "release_certificate"]
    lemmas = [e for e in events if e["kind"] == "lemma"]
    if releases:
        subject = ("EGMRA: RELEASED result on "
                   + ", ".join(sorted({e["problem_id"] for e in releases})))
    elif lemmas and len(lemmas) == len(events):
        subject = f"EGMRA: {len(lemmas)} new kernel-verified lemma(s)"
    else:
        problems = sorted({e["problem_id"] for e in events if e["problem_id"]})
        subject = (f"EGMRA progress: {len(events)} event(s) on "
                   + ", ".join(problems[:4])
                   + ("…" if len(problems) > 4 else ""))
    lines = ["Significant EGMRA pipeline events:", ""]
    for event in events:
        problem = event.get("problem_id", "")
        if event["kind"] == "lemma":
            lines.append(
                f"* [{problem}] kernel-sealed lemma "
                f"`{event.get('declaration_name', '')}` "
                f"(library: {event.get('ledger', '')})")
        else:
            lines.append(
                f"* [{problem}] {event['reason']} "
                f"(state {event.get('public_state', '')}, "
                f"run {event.get('run_id', '')[:48]}, "
                f"at {event.get('recorded_at', '')})")
        if problem:
            lines.append(
                f"  dashboard: {DASHBOARD_URL}/#problem={_problem_number(problem)}")
    lines += [
        "",
        f"Full dashboard: {DASHBOARD_URL}",
        "",
        "Notes: 'release_certificate' is the only solve-grade signal; "
        "progress states and sealed lemmas are verified forward motion, "
        "not solved problems.",
    ]
    return subject, "\n".join(lines)


@dataclass
class EmailSender:
    """SMTP (SSL) sender; credentials come from the environment, never logs."""

    user: str
    password: str = field(repr=False)
    recipients: tuple[str, ...] = ()
    host: str = "smtp.gmail.com"
    port: int = 465
    timeout_s: float = 30.0

    def send(self, subject: str, body: str) -> None:
        if not self.recipients:
            raise NotifyError("no notification recipients configured")
        message = EmailMessage()
        message["From"] = self.user
        message["To"] = ", ".join(self.recipients)
        message["Subject"] = subject
        message.set_content(body)
        try:
            with smtplib.SMTP_SSL(self.host, self.port,
                                  timeout=self.timeout_s) as server:
                server.login(self.user, self.password)
                server.send_message(message)
        except (smtplib.SMTPException, OSError) as exc:
            raise NotifyError(f"email delivery failed: {type(exc).__name__}: {exc}") \
                from exc


def build_email_sender(env: dict[str, str] | None = None) -> EmailSender:
    """Build a sender from ``EGMRA_SMTP_*`` / ``EGMRA_NOTIFY_TO`` variables."""
    values = os.environ if env is None else env
    user = (values.get("EGMRA_SMTP_USER") or "").strip()
    password = values.get("EGMRA_SMTP_PASSWORD") or ""
    recipients = _recipients(values)
    if not user or not password:
        raise NotifyError(
            "EGMRA_SMTP_USER and EGMRA_SMTP_PASSWORD must be set (put them in "
            "egmra.keys.sh; for Gmail use an App Password, never the account "
            "password)")
    if not recipients:
        raise NotifyError("EGMRA_NOTIFY_TO must list at least one recipient")
    return EmailSender(
        user=user, password=password, recipients=recipients,
        host=(values.get("EGMRA_SMTP_HOST") or "smtp.gmail.com").strip(),
        port=int(values.get("EGMRA_SMTP_PORT") or 465),
    )


def _recipients(values) -> tuple[str, ...]:
    return tuple(
        part.strip() for part in (values.get("EGMRA_NOTIFY_TO") or "").split(",")
        if part.strip())


@dataclass
class MailAppSender:
    """Send through macOS Mail.app via AppleScript (no stored credentials).

    Mail.app holds the account session itself (e.g. a Gmail login via Google
    OAuth), so no password or API key ever touches this process. Values are
    passed as ``osascript`` argv — never interpolated into the script — so
    subjects/bodies cannot inject AppleScript.
    """

    recipients: tuple[str, ...] = ()
    timeout_s: float = 60.0

    _SCRIPT = (
        'on run argv\n'
        'tell application "Mail"\n'
        'set m to make new outgoing message with properties '
        '{subject:(item 1 of argv), content:(item 2 of argv), visible:false}\n'
        'tell m\n'
        'repeat with i from 3 to (count of argv)\n'
        'make new to recipient at end of to recipients '
        'with properties {address:(item i of argv)}\n'
        'end repeat\n'
        'end tell\n'
        'send m\n'
        'end tell\n'
        'end run'
    )

    def send(self, subject: str, body: str) -> None:
        if not self.recipients:
            raise NotifyError("no notification recipients configured")
        import subprocess

        command = ["osascript", "-e", self._SCRIPT, subject, body,
                   *self.recipients]
        try:
            result = subprocess.run(
                command, capture_output=True, text=True, timeout=self.timeout_s)
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise NotifyError(
                f"Mail.app delivery failed: {type(exc).__name__}: {exc}") from exc
        if result.returncode != 0:
            raise NotifyError(
                "Mail.app delivery failed: "
                + (result.stderr or result.stdout or "").strip()[:400]
                + " — make sure Mail.app has an account configured and "
                  "automation permission is granted")


@dataclass
class FormSubmitSender:
    """Send email through the formsubmit.co relay (no account, no secrets).

    One POST per recipient to ``https://formsubmit.co/ajax/<address>``. The
    first-ever submission to an address triggers a one-time activation email
    that the recipient must click; afterwards deliveries are immediate. The
    sender raises only when *every* recipient fails, so one unactivated
    recipient never blocks (or duplicates) the others.
    """

    recipients: tuple[str, ...] = ()
    timeout_s: float = 30.0
    #: Injectable transport for tests: (url, payload) -> parsed JSON dict.
    transport: Any = None

    _ENDPOINT = "https://formsubmit.co/ajax/"
    #: The relay rejects non-web submissions; it accepts our own public
    #: dashboard as the submitting origin.
    _ORIGIN = "https://egmra-status.vercel.app"

    def _post(self, url: str, payload: dict[str, Any]) -> dict[str, Any]:
        if self.transport is not None:
            return self.transport(url, payload)
        import urllib.request

        request = urllib.request.Request(
            url, data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json",
                     "Accept": "application/json",
                     "Origin": self._ORIGIN,
                     "Referer": self._ORIGIN + "/",
                     "User-Agent": ("Mozilla/5.0 (Macintosh; Intel Mac OS X "
                                    "10_15_7) AppleWebKit/537.36")},
            method="POST")
        with urllib.request.urlopen(request, timeout=self.timeout_s) as response:
            body = response.read(1_000_000)
        document = json.loads(body.decode("utf-8"))
        if not isinstance(document, dict):
            raise ValueError("relay response is not a JSON object")
        return document

    def send(self, subject: str, body: str) -> None:
        if not self.recipients:
            raise NotifyError("no notification recipients configured")
        failures: list[str] = []
        delivered = 0
        for recipient in self.recipients:
            payload = {
                "name": "EGMRA Pipeline",
                "_subject": subject,
                "message": body,
                "_template": "box",
                "_captcha": "false",
            }
            try:
                document = self._post(self._ENDPOINT + recipient, payload)
            except Exception as exc:  # noqa: BLE001 - per-recipient isolation
                failures.append(f"{recipient}: {type(exc).__name__}: {exc}")
                continue
            if str(document.get("success", "")).lower() == "true":
                delivered += 1
            else:
                failures.append(
                    f"{recipient}: {str(document.get('message', document))[:200]}")
        if delivered == 0:
            raise NotifyError(
                "formsubmit delivery failed for every recipient: "
                + "; ".join(failures)[:600])


def build_sender(env: dict[str, str] | None = None):
    """Select the delivery backend from ``EGMRA_NOTIFY_METHOD``.

    * ``formsubmit`` — :class:`FormSubmitSender` (no account or secrets;
      recipients activate once via a link emailed to them);
    * ``smtp``       — :class:`EmailSender` (needs ``EGMRA_SMTP_*``);
    * ``mailapp``    — :class:`MailAppSender` (macOS Mail.app session);
    * unset/auto     — smtp when a password is configured, else formsubmit.
    """
    values = os.environ if env is None else env
    method = (values.get("EGMRA_NOTIFY_METHOD") or "auto").strip().lower()
    recipients = _recipients(values)
    if method == "smtp":
        return build_email_sender(env)
    if method == "mailapp":
        if not recipients:
            raise NotifyError("EGMRA_NOTIFY_TO must list at least one recipient")
        return MailAppSender(recipients=recipients)
    if method == "formsubmit":
        if not recipients:
            raise NotifyError("EGMRA_NOTIFY_TO must list at least one recipient")
        return FormSubmitSender(recipients=recipients)
    if method != "auto":
        raise NotifyError(
            f"unknown EGMRA_NOTIFY_METHOD {method!r} "
            "(use formsubmit, smtp, or mailapp)")
    if values.get("EGMRA_SMTP_PASSWORD"):
        return build_email_sender(env)
    if recipients:
        return FormSubmitSender(recipients=recipients)
    raise NotifyError(
        "no notification method available: set EGMRA_NOTIFY_TO (formsubmit "
        "relay) or EGMRA_SMTP_USER/EGMRA_SMTP_PASSWORD (smtp)")
