"""Tests for the significant-progress email notifier (egmra.comms.notify)."""

from __future__ import annotations

import json
import os
import stat

import pytest

from egmra.cli import main
from egmra.comms import notify
from egmra.comms.notify import (
    EmailSender,
    FormSubmitSender,
    MailAppSender,
    NotifyError,
    build_email_sender,
    build_sender,
    classify_outcome,
    format_email,
    load_state,
    save_state,
    scan_events,
)


def _outcome(problem="erdos-312", state="OPEN_NO_PROGRESS", **extra):
    row = {
        "problem_id": problem, "run_id": f"run-{problem}", "public_state": state,
        "released": False, "candidate_assembly_complete": False,
        "salvage": {"supported": [], "refuted": []},
        "recorded_at": "2026-07-16T00:00:00Z",
    }
    row.update(extra)
    return row


def _write_jsonl(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row) + "\n")


# ── significance classification ──────────────────────────────────────────────

def test_classify_release_is_strongest_signal():
    row = _outcome(state="FORMALLY_VERIFIED_CANDIDATE", released=True)
    assert classify_outcome(row) == "release_certificate"


@pytest.mark.parametrize("state", sorted(notify.PROGRESS_STATES))
def test_classify_progress_states(state):
    assert classify_outcome(_outcome(state=state)) == f"progress:{state}"


def test_classify_assembly_and_salvage():
    assert classify_outcome(_outcome(candidate_assembly_complete=True)) \
        == "candidate_assembly_complete"
    row = _outcome(salvage={"supported": [{"claim_id": "c1"}], "refuted": []})
    assert classify_outcome(row) == "salvaged_supported_claims:1"


def test_classify_insignificant_and_malformed():
    assert classify_outcome(_outcome()) is None
    assert classify_outcome(_outcome(state="BLOCKED_BY_INTERPRETATION")) is None
    assert classify_outcome("not a dict") is None
    assert classify_outcome({}) is None


# ── incremental scanning ─────────────────────────────────────────────────────

def test_scan_events_baseline_then_incremental(tmp_path):
    ledger = tmp_path / "outcomes" / "shared-host.jsonl"
    _write_jsonl(ledger, [_outcome(), _outcome(state="BLOCKED_BY_INTERPRETATION")])
    events, state = scan_events(
        outcome_paths=[tmp_path / "outcomes"], lemma_path=None, state={})
    assert events == []  # nothing significant yet
    assert state[str(ledger.resolve())] == 2
    # A release lands; only the NEW row is reported.
    _write_jsonl(ledger, [_outcome(problem="erdos-7", released=True)])
    events, state = scan_events(
        outcome_paths=[tmp_path / "outcomes"], lemma_path=None, state=state)
    assert [e["reason"] for e in events] == ["release_certificate"]
    assert events[0]["problem_id"] == "erdos-7"
    assert state[str(ledger.resolve())] == 3


def test_scan_events_picks_up_new_ledger_files(tmp_path):
    directory = tmp_path / "outcomes"
    first = directory / "a.jsonl"
    _write_jsonl(first, [_outcome()])
    _, state = scan_events(outcome_paths=[directory], lemma_path=None, state={})
    # A second campaign starts a NEW ledger file later (e.g. the Kimi worker).
    second = directory / "kimi-host.jsonl"
    _write_jsonl(second, [_outcome(problem="erdos-42",
                                   state="COMPUTATIONAL_EVIDENCE")])
    events, state = scan_events(
        outcome_paths=[directory], lemma_path=None, state=state)
    assert [e["problem_id"] for e in events] == ["erdos-42"]
    assert state[str(second.resolve())] == 1


def test_scan_events_reports_sealed_lemmas(tmp_path):
    library = tmp_path / "egmra_lemma_library.jsonl"
    _write_jsonl(library, [
        {"problem_id": "erdos-312", "declaration_name": "erdos_312_step1"},
    ])
    events, state = scan_events(
        outcome_paths=[], lemma_path=library, state={})
    assert [e["reason"] for e in events] == ["kernel_sealed_lemma"]
    assert events[0]["declaration_name"] == "erdos_312_step1"
    # Idempotent: nothing new on the next scan.
    events, _ = scan_events(outcome_paths=[], lemma_path=library, state=state)
    assert events == []


def test_scan_skips_malformed_lines_without_losing_position(tmp_path):
    ledger = tmp_path / "l.jsonl"
    ledger.write_text('not json\n' + json.dumps(_outcome(released=True)) + "\n")
    events, state = scan_events(outcome_paths=[ledger], lemma_path=None, state={})
    assert [e["reason"] for e in events] == ["release_certificate"]
    assert state[str(ledger.resolve())] == 2


# ── email formatting ─────────────────────────────────────────────────────────

def test_format_email_release_subject_and_dashboard_links():
    events, _ = [
        {"kind": "outcome", "reason": "release_certificate",
         "problem_id": "erdos-7", "public_state": "FORMALLY_VERIFIED_CANDIDATE",
         "run_id": "run-1", "recorded_at": "t", "ledger": "a.jsonl"},
    ], None
    subject, body = format_email(events)
    assert "RELEASED" in subject and "erdos-7" in subject
    assert "https://egmra-status.vercel.app/#problem=7" in body
    assert "release_certificate" in body


def test_format_email_lemma_only_subject():
    events = [{"kind": "lemma", "reason": "kernel_sealed_lemma",
               "problem_id": "erdos-312", "declaration_name": "erdos_312_l1",
               "ledger": "egmra_lemma_library.jsonl"}]
    subject, body = format_email(events)
    assert "kernel-verified lemma" in subject
    assert "erdos_312_l1" in body


def test_format_email_progress_subject():
    events = [{"kind": "outcome", "reason": "progress:CANDIDATE_SOLUTION",
               "problem_id": "erdos-42", "public_state": "CANDIDATE_SOLUTION",
               "run_id": "r", "recorded_at": "t", "ledger": "a.jsonl"}]
    subject, body = format_email(events)
    assert subject.startswith("EGMRA progress: 1 event(s)")
    assert "not solved problems" in body  # honesty note present


# ── state persistence ────────────────────────────────────────────────────────

def test_state_round_trip_mode_and_first_run(tmp_path):
    path = tmp_path / "state.json"
    assert load_state(path) is None  # first run
    save_state(path, {"/a/b.jsonl": 3})
    assert load_state(path) == {"/a/b.jsonl": 3}
    assert stat.S_IMODE(os.stat(path).st_mode) == 0o600
    path.write_text("garbage")
    assert load_state(path) is None  # malformed → honest re-baseline


# ── sender configuration and delivery ────────────────────────────────────────

def test_build_email_sender_requires_configuration():
    with pytest.raises(NotifyError):
        build_email_sender({})
    with pytest.raises(NotifyError):
        build_email_sender({"EGMRA_SMTP_USER": "u@example.com",
                            "EGMRA_SMTP_PASSWORD": "p"})  # no recipients
    sender = build_email_sender({
        "EGMRA_SMTP_USER": "sender@example.com",
        "EGMRA_SMTP_PASSWORD": "app-password",
        "EGMRA_NOTIFY_TO": "first@example.com, second@example.com",
    })
    assert sender.recipients == ("first@example.com", "second@example.com")
    assert sender.host == "smtp.gmail.com" and sender.port == 465
    assert "app-password" not in repr(sender)  # never leaks into logs


class _FakeSMTP:
    instances: list = []

    def __init__(self, host, port, timeout=None):
        self.host, self.port = host, port
        self.logins: list = []
        self.messages: list = []
        _FakeSMTP.instances.append(self)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def login(self, user, password):
        self.logins.append((user, password))

    def send_message(self, message):
        self.messages.append(message)


def test_email_sender_sends_via_smtp_ssl(monkeypatch):
    _FakeSMTP.instances = []
    monkeypatch.setattr(notify.smtplib, "SMTP_SSL", _FakeSMTP)
    sender = EmailSender(user="u@example.com", password="secret",
                         recipients=("a@example.com", "b@example.com"))
    sender.send("subject line", "body text")
    smtp = _FakeSMTP.instances[-1]
    assert smtp.host == "smtp.gmail.com" and smtp.port == 465
    assert smtp.logins == [("u@example.com", "secret")]
    message = smtp.messages[-1]
    assert message["Subject"] == "subject line"
    assert message["To"] == "a@example.com, b@example.com"
    assert "body text" in message.get_content()


def test_email_sender_wraps_delivery_failures(monkeypatch):
    class _Boom:
        def __init__(self, *a, **kw):
            raise OSError("network down")

    monkeypatch.setattr(notify.smtplib, "SMTP_SSL", _Boom)
    sender = EmailSender(user="u@example.com", password="secret",
                         recipients=("a@example.com",))
    with pytest.raises(NotifyError):
        sender.send("s", "b")


# ── backend selection and Mail.app delivery ──────────────────────────────

def test_build_sender_selects_backends():
    env_common = {"EGMRA_NOTIFY_TO": "a@example.com,b@example.com"}
    smtp = build_sender({**env_common, "EGMRA_NOTIFY_METHOD": "smtp",
                         "EGMRA_SMTP_USER": "u@example.com",
                         "EGMRA_SMTP_PASSWORD": "p"})
    assert isinstance(smtp, EmailSender)
    mailapp = build_sender({**env_common, "EGMRA_NOTIFY_METHOD": "mailapp"})
    assert isinstance(mailapp, MailAppSender)
    assert mailapp.recipients == ("a@example.com", "b@example.com")
    relay = build_sender({**env_common, "EGMRA_NOTIFY_METHOD": "formsubmit"})
    assert isinstance(relay, FormSubmitSender)
    assert relay.recipients == ("a@example.com", "b@example.com")
    # auto prefers smtp when credentials exist, else the no-secret relay
    auto_smtp = build_sender({**env_common,
                              "EGMRA_SMTP_USER": "u@example.com",
                              "EGMRA_SMTP_PASSWORD": "p"})
    assert isinstance(auto_smtp, EmailSender)
    auto_relay = build_sender(env_common)
    assert isinstance(auto_relay, FormSubmitSender)
    with pytest.raises(NotifyError):
        build_sender({**env_common, "EGMRA_NOTIFY_METHOD": "carrier-pigeon"})
    with pytest.raises(NotifyError):
        build_sender({"EGMRA_NOTIFY_METHOD": "formsubmit"})  # no recipients
    with pytest.raises(NotifyError):
        build_sender({})  # nothing configured at all


def test_formsubmit_sender_posts_per_recipient():
    calls: list = []

    def _transport(url, payload):
        calls.append((url, payload))
        return {"success": "true", "message": "sent"}

    sender = FormSubmitSender(
        recipients=("a@example.com", "b@example.com"), transport=_transport)
    sender.send("the subject", "the body")
    assert [url for url, _ in calls] == [
        "https://formsubmit.co/ajax/a@example.com",
        "https://formsubmit.co/ajax/b@example.com",
    ]
    assert all(p["_subject"] == "the subject" for _, p in calls)
    assert all(p["message"] == "the body" for _, p in calls)
    assert all(p["_captcha"] == "false" for _, p in calls)


def test_formsubmit_sender_tolerates_partial_failure():
    def _transport(url, payload):
        if "a@example.com" in url:
            raise OSError("connection reset")
        return {"success": "true"}

    sender = FormSubmitSender(
        recipients=("a@example.com", "b@example.com"), transport=_transport)
    sender.send("s", "b")  # one delivery succeeded → no raise


def test_formsubmit_sender_raises_when_all_fail():
    def _transport(url, payload):
        return {"success": "false", "message": "activation required"}

    sender = FormSubmitSender(recipients=("a@example.com",),
                              transport=_transport)
    with pytest.raises(NotifyError) as excinfo:
        sender.send("s", "b")
    assert "activation required" in str(excinfo.value)


def test_mailapp_sender_invokes_osascript_with_argv(monkeypatch):
    calls: list = []

    class _Done:
        returncode = 0
        stderr = ""
        stdout = ""

    import subprocess

    def _fake_run(command, **kw):
        calls.append(command)
        return _Done()

    monkeypatch.setattr(subprocess, "run", _fake_run)
    sender = MailAppSender(recipients=("a@example.com", "b@example.com"))
    sender.send('subject with "quotes"', "body line")
    command = calls[-1]
    assert command[0] == "osascript"
    # Argument passing (never string interpolation into the script source).
    assert 'subject with "quotes"' in command
    assert "body line" in command
    assert command[-2:] == ["a@example.com", "b@example.com"]
    assert 'quotes' not in sender._SCRIPT


def test_mailapp_sender_reports_failures(monkeypatch):
    import subprocess

    class _Failed:
        returncode = 1
        stderr = "Mail got an error: No account."
        stdout = ""

    monkeypatch.setattr(subprocess, "run", lambda *a, **kw: _Failed())
    sender = MailAppSender(recipients=("a@example.com",))
    with pytest.raises(NotifyError) as excinfo:
        sender.send("s", "b")
    assert "No account" in str(excinfo.value)


# ── CLI integration (notify-watch --once) ────────────────────────────────────

class _RecordingSender:
    def __init__(self):
        self.sent: list = []
        self.recipients = ("a@example.com",)
        self.fail_next = False

    def send(self, subject, body):
        if self.fail_next:
            self.fail_next = False
            raise NotifyError("delivery failed")
        self.sent.append((subject, body))


def test_notify_watch_once_baselines_then_notifies(tmp_path, monkeypatch, capsys):
    sender = _RecordingSender()
    monkeypatch.setattr(notify, "build_sender", lambda env=None: sender)
    ledger_dir = tmp_path / "outcomes"
    ledger = ledger_dir / "shared.jsonl"
    _write_jsonl(ledger, [_outcome(released=True)])  # history: must NOT email
    state_file = tmp_path / "state.json"
    argv = ["notify-watch", "--once",
            "--outcomes", str(ledger_dir),
            "--lemma-library", str(tmp_path / "lemmas.jsonl"),
            "--state-file", str(state_file)]
    assert main(argv) == 0
    assert sender.sent == []  # first run baselined silently
    # New significant event → exactly one email on the next cycle.
    _write_jsonl(ledger, [_outcome(problem="erdos-9",
                                   state="VERIFIED_CANDIDATE")])
    assert main(argv) == 0
    assert len(sender.sent) == 1
    subject, body = sender.sent[0]
    assert "erdos-9" in subject or "erdos-9" in body
    # Nothing new → no more email.
    assert main(argv) == 0
    assert len(sender.sent) == 1


def test_notify_watch_redelivers_after_send_failure(tmp_path, monkeypatch):
    sender = _RecordingSender()
    monkeypatch.setattr(notify, "build_sender", lambda env=None: sender)
    ledger = tmp_path / "outcomes" / "s.jsonl"
    state_file = tmp_path / "state.json"
    argv = ["notify-watch", "--once", "--outcomes", str(tmp_path / "outcomes"),
            "--lemma-library", str(tmp_path / "lemmas.jsonl"),
            "--state-file", str(state_file)]
    _write_jsonl(ledger, [_outcome()])
    assert main(argv) == 0  # baseline
    _write_jsonl(ledger, [_outcome(problem="erdos-3", released=True)])
    sender.fail_next = True
    assert main(argv) == 0  # delivery fails; cursor must NOT advance
    assert sender.sent == []
    assert main(argv) == 0  # retried and delivered
    assert len(sender.sent) == 1
    assert "erdos-3" in sender.sent[0][0] + sender.sent[0][1]


def test_notify_watch_test_flag_sends_immediately(tmp_path, monkeypatch, capsys):
    sender = _RecordingSender()
    monkeypatch.setattr(notify, "build_sender", lambda env=None: sender)
    assert main(["notify-watch", "--test",
                 "--outcomes", str(tmp_path),
                 "--state-file", str(tmp_path / "state.json")]) == 0
    assert len(sender.sent) == 1
    assert "test" in sender.sent[0][0].lower()


def test_notify_watch_reports_missing_configuration(tmp_path, monkeypatch, capsys):
    monkeypatch.delenv("EGMRA_SMTP_USER", raising=False)
    monkeypatch.delenv("EGMRA_SMTP_PASSWORD", raising=False)
    monkeypatch.delenv("EGMRA_NOTIFY_TO", raising=False)
    monkeypatch.setenv("EGMRA_NOTIFY_METHOD", "smtp")  # force the strict path
    rc = main(["notify-watch", "--once",
               "--state-file", str(tmp_path / "state.json")])
    assert rc == 2
    err = json.loads(capsys.readouterr().err.strip().splitlines()[-1])
    assert "EGMRA_SMTP_USER" in err["error"]


# ── in-pipeline (campaign) notification wiring ───────────────────────────────

def test_build_campaign_notifier_modes(monkeypatch):
    from types import SimpleNamespace
    import egmra.cli as cli_module

    monkeypatch.delenv("EGMRA_NOTIFY_TO", raising=False)
    # auto + unconfigured → silently disabled
    assert cli_module._build_campaign_notifier(SimpleNamespace(notify="auto")) is None
    # off → always disabled
    monkeypatch.setenv("EGMRA_NOTIFY_TO", "a@example.com")
    monkeypatch.setenv("EGMRA_NOTIFY_METHOD", "formsubmit")
    assert cli_module._build_campaign_notifier(SimpleNamespace(notify="off")) is None
    # auto + configured → a sender is built
    assert cli_module._build_campaign_notifier(SimpleNamespace(notify="auto")) is not None
    # on + unconfigured → clean launch error
    monkeypatch.delenv("EGMRA_NOTIFY_TO", raising=False)
    monkeypatch.setenv("EGMRA_NOTIFY_METHOD", "smtp")
    monkeypatch.delenv("EGMRA_SMTP_PASSWORD", raising=False)
    with pytest.raises(ValueError):
        cli_module._build_campaign_notifier(SimpleNamespace(notify="on"))


def test_campaign_emails_significant_progress_inline(tmp_path, monkeypatch):
    """A campaign with recipients configured emails a solve without any watcher."""
    from types import SimpleNamespace
    import egmra.cli as cli_module
    from egmra.tests.test_cli_arbitrary import _config_file, _signed_policy_file

    sender = _RecordingSender()
    monkeypatch.setattr(cli_module, "_build_campaign_notifier",
                        lambda args: sender)
    monkeypatch.setattr(cli_module, "from_erdos_number",
                        lambda number, **kw: SimpleNamespace(
                            problem_id=f"erdos-{number}", source_bytes=b"S",
                            source_id="fx", display_statement="S",
                            status_claims=[], novelty_verdict="N1"))
    monkeypatch.setattr(cli_module, "research", lambda **kw: object())
    monkeypatch.setattr(cli_module, "classify_result",
                        lambda result, **kw: SimpleNamespace(state="done"))
    # The recorded outcome is what the notifier classifies: erdos-5 is a
    # released solve, erdos-6 a dead end. Keying off problem_id keeps the test
    # independent of research()'s internal signature.
    def _build_record(*, problem_id, result, run_id, state):
        released = problem_id == "erdos-5"
        return {"schema_version": 1, "problem_id": problem_id, "run_id": run_id,
                "recorded_at": "t",
                "public_state": ("VERIFIED_CANDIDATE" if released
                                 else "BLOCKED_BY_INTERPRETATION"),
                "released": released,
                "candidate_assembly_complete": False,
                "salvage": {"supported": [], "refuted": []}}

    monkeypatch.setattr(cli_module, "build_outcome_record", _build_record)

    cfg = _config_file(tmp_path)
    policy = _signed_policy_file(tmp_path)
    rc = main(["--config", str(cfg), "campaign", "--provider", "deterministic",
               "--erdos-range", "5-6", "--policy", str(policy),
               "--notify", "on", "--outcome-ledger", str(tmp_path / "out.jsonl"),
               "--state", str(tmp_path / "camp.json")])
    assert rc == 0
    # Exactly one email — for the released problem, not the dead end.
    assert len(sender.sent) == 1
    subject, body = sender.sent[0]
    assert "erdos-5" in subject + body
    assert "erdos-6" not in subject + body

