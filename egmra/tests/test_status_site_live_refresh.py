"""Regression tests for the public status publisher and live client contract."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from status_site.live_refresh import _load_private_file, _run, _semantic


ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / "status_site"


def test_private_file_parser_reads_exports_without_executing_shell(tmp_path):
    private_file = tmp_path / "private.env"
    private_file.write_text(
        "# private configuration\n"
        "export EGMRA_CHECKPOINT_KEY='local checkpoint value'\n"
        'EGMRA_POSTGRES_DSN="local-db"\n'
        "source /tmp/must-not-run\n",
        encoding="utf-8",
    )

    assert _load_private_file(private_file) == {
        "EGMRA_CHECKPOINT_KEY": "local checkpoint value",
        "EGMRA_POSTGRES_DSN": "local-db",
    }


def test_failed_child_output_redacts_private_values():
    secret = "local-sensitive-test-value"
    with pytest.raises(RuntimeError) as raised:
        _run(
            sys.executable,
            "-c",
            f"print({secret!r}); raise SystemExit(3)",
            redact=(secret,),
        )

    assert secret not in str(raised.value)
    assert "<redacted>" in str(raised.value)


def test_snapshot_change_detection_includes_generation_time():
    document = {"generated_at": "first", "summary": {"total_runs": 3}}
    assert _semantic(document) == document


def test_both_pages_reference_the_branded_favicon():
    assert (SITE / "favicon.svg").read_text(encoding="utf-8").startswith("<svg")
    for name in ("index.html", "ranking.html"):
        html = (SITE / name).read_text(encoding="utf-8")
        assert 'rel="icon" type="image/svg+xml" href="/favicon.svg?v=' in html


def test_both_clients_refresh_on_timer_focus_and_reconnect():
    for name in ("app.js", "ranking.js"):
        javascript = (SITE / name).read_text(encoding="utf-8")
        assert "AUTO_REFRESH_MS=60_000" in javascript
        assert 'addEventListener("visibilitychange"' in javascript
        assert 'addEventListener("online"' in javascript
        assert "Updates delayed" in javascript
        assert "Update check failed" in javascript


def test_clients_do_not_reuse_an_expired_immutable_status_ref_after_api_failure():
    for name in ("app.js", "ranking.js"):
        javascript = (SITE / name).read_text(encoding="utf-8")
        assert "if(cached?.sha)return immutableDataUrl(cached.sha);" not in javascript
