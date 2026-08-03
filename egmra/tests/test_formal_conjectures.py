"""Community formal targets from formal-conjectures (audit R5).

Hermetic tests for fetching/parsing the community Lean statement and for the
CLI wiring (`egmra formal-target`, `egmra run --formal-target-file`,
`--worker-rounds`).  The live GitHub fetch is exercised only through an
injected fake fetcher; trust boundaries (never authority, size caps, host
allowlist shape) are pinned here.
"""

from __future__ import annotations

import json

import pytest

from egmra.corpus.formal_conjectures import (
    DEFAULT_REF,
    FORMAL_CONJECTURES_HOST,
    FormalConjectureUnavailable,
    fetch_formal_conjecture,
    parse_declarations,
)

LEAN_SAMPLE = b"""/-!
# Erdos Problem 336
-/
import Mathlib

open scoped Classical

@[category research open, AMS 11]
theorem erdos_336 : \xe2\x88\x80 r : \xe2\x84\x95, 2 \xe2\x89\xa4 r \xe2\x86\x92 True := by
  trivial

noncomputable def erdos_336.helper (r : \xe2\x84\x95) : \xe2\x84\x95 := r
"""


def test_fetch_parses_declarations_and_hashes():
    calls = []

    def fetcher(url):
        calls.append(url)
        return LEAN_SAMPLE

    target = fetch_formal_conjecture(336, fetcher=fetcher)
    assert calls == [
        "https://raw.githubusercontent.com/google-deepmind/formal-conjectures/"
        "main/FormalConjectures/ErdosProblems/336.lean"
    ]
    assert target.problem == 336
    assert target.declaration_names[0] == "erdos_336"
    assert "erdos_336.helper" in target.declaration_names
    assert len(target.sha256) == 64
    assert not target.reproducible_ref  # 'main' is mutable
    assert "never truth authority" in target.to_dict()["trust_note"]


def test_pinned_tag_is_reproducible():
    target = fetch_formal_conjecture(
        7, ref="bench-v1-lean4.27.0", fetcher=lambda url: LEAN_SAMPLE)
    assert target.reproducible_ref
    assert "/bench-v1-lean4.27.0/" in target.url


@pytest.mark.parametrize("number", [0, -3, True, "7"])
def test_invalid_problem_numbers_rejected(number):
    with pytest.raises(ValueError):
        fetch_formal_conjecture(number, fetcher=lambda url: LEAN_SAMPLE)


def test_ref_injection_rejected():
    with pytest.raises(ValueError):
        fetch_formal_conjecture(7, ref="main?x=1", fetcher=lambda url: LEAN_SAMPLE)


def test_oversized_and_empty_and_undeclared_sources_rejected():
    with pytest.raises(FormalConjectureUnavailable):
        fetch_formal_conjecture(7, fetcher=lambda url: b"x" * 1_000_001)
    with pytest.raises(FormalConjectureUnavailable):
        fetch_formal_conjecture(7, fetcher=lambda url: b"   \n")
    with pytest.raises(FormalConjectureUnavailable):
        fetch_formal_conjecture(7, fetcher=lambda url: b"-- just a comment\n")


def test_transport_failures_normalized():
    def broken(url):
        raise OSError("connection refused")

    with pytest.raises(FormalConjectureUnavailable):
        fetch_formal_conjecture(7, fetcher=broken)


def test_parse_declarations_handles_attributes_and_kinds():
    names = parse_declarations(
        "@[category research open]\ntheorem a_1 : True := trivial\n"
        "lemma b.c' : True := trivial\n"
        "noncomputable def d : Nat := 0\nabbrev e := Nat\n"
        "-- theorem commented_out : False\n"
    )
    assert names == ("a_1", "b.c'", "d", "e")


def test_default_fetcher_is_host_allowlisted():
    # The default (live) fetcher must refuse anything off the pinned host —
    # verified without network because the check precedes any request.
    from egmra.corpus.formal_conjectures import _default_fetcher

    for url in (
        "http://raw.githubusercontent.com/x",           # not https
        "https://example.com/x",                        # wrong host
        f"https://user:pw@{FORMAL_CONJECTURES_HOST}/x",  # embedded credentials
    ):
        with pytest.raises(FormalConjectureUnavailable):
            _default_fetcher(url)


def test_cli_formal_target_writes_and_reports(tmp_path, monkeypatch, capsys):
    from egmra import cli as cli_module
    from egmra.corpus import formal_conjectures as fc

    monkeypatch.setattr(fc, "_default_fetcher", lambda url: LEAN_SAMPLE)
    output = tmp_path / "erdos_336.lean"
    rc = cli_module.main([
        "formal-target", "--erdos", "336", "--output", str(output)])
    assert rc == 0
    document = json.loads(capsys.readouterr().out)
    assert document["problem"] == 336
    assert document["declaration_names"][0] == "erdos_336"
    assert document["reproducible_ref"] is False
    assert output.read_bytes() == LEAN_SAMPLE
    # Refuses to overwrite (main() reports the refusal as a JSON error).
    rc = cli_module.main(["formal-target", "--erdos", "336",
                          "--output", str(output)])
    assert rc != 0
    captured = capsys.readouterr()
    error = json.loads(captured.err or captured.out)
    assert error["error"] == "FileExistsError"
    assert output.read_bytes() == LEAN_SAMPLE  # original left intact


def test_cli_formal_target_reports_unavailable(monkeypatch, capsys):
    from egmra import cli as cli_module
    from egmra.corpus import formal_conjectures as fc

    def broken(url):
        raise FormalConjectureUnavailable("offline")

    monkeypatch.setattr(fc, "_default_fetcher", broken)
    rc = cli_module.main(["formal-target", "--erdos", "336"])
    assert rc == 3
    assert "error" in json.loads(capsys.readouterr().out)


def test_load_formal_target_guards(tmp_path):
    from egmra.cli import _load_formal_target

    assert _load_formal_target(None) == ""
    lean = tmp_path / "target.lean"
    lean.write_text("theorem t : True := trivial\n", encoding="utf-8")
    assert _load_formal_target(lean).startswith("theorem t")
    empty = tmp_path / "empty.lean"
    empty.write_text("  \n", encoding="utf-8")
    with pytest.raises(ValueError):
        _load_formal_target(empty)
    link = tmp_path / "link.lean"
    link.symlink_to(lean)
    with pytest.raises(ValueError):
        _load_formal_target(link)
