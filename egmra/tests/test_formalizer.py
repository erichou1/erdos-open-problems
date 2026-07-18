"""Tests for the autonomous formalization worker (Aristotle integration, task #5).

The live Aristotle SDK is exercised only with a real key (never in CI); here a
fake SDK client proves the submit -> fetch -> read-source flow, the pinned-
obligation prompt, and safe source reading. The trust boundary is unchanged: the
vendor supplies only the proof term and its output is re-checked by the pinned
kernel elsewhere.
"""

from __future__ import annotations

from types import SimpleNamespace

from egmra.lean.formalizer import (
    AristotleFormalizer,
    build_formalization_prompt,
    read_lean_source,
)

_CANDIDATE_LEAN = "import Mathlib\n\ntheorem egmra_demo : 2 + 2 = 4 := rfl\n"


class _FakeSdkClient:
    """A synchronous stand-in for AristotleSdkClient (no network, no key)."""

    def __init__(self, quarantine_dir) -> None:
        self._dir = quarantine_dir
        self.prompts: list[str] = []
        self.closed = False

    def submit(self, prompt: str):
        self.prompts.append(prompt)
        return SimpleNamespace(project_id="proj", agent_task_id="task")

    def fetch(self, submission, *, wait: bool = True):
        return SimpleNamespace(quarantine_dir=self._dir, promotable=False)

    def close(self) -> None:
        self.closed = True


def test_build_formalization_prompt_pins_the_exact_obligation():
    prompt = build_formalization_prompt(
        declaration_name="egmra_demo", expected_type="2 + 2 = 4",
        informal_statement="two plus two is four")
    assert "egmra_demo : 2 + 2 = 4" in prompt
    assert "EXACTLY" in prompt
    assert "sorry" in prompt and "native_decide" in prompt  # forbidden escapes named
    assert "LOCKED FORMAL OBLIGATION" in prompt
    assert "RESULTS THAT DO NOT COUNT" in prompt
    assert "several materially different routes" in prompt
    assert "Independent kernel replay decides success" in prompt
    assert "return no source rather than fabricating a proof" in prompt


def test_read_lean_source_concatenates_and_handles_missing(tmp_path):
    quarantine = tmp_path / "q"
    quarantine.mkdir()
    (quarantine / "A.lean").write_text("theorem a : True := trivial", encoding="utf-8")
    (quarantine / "B.lean").write_text("theorem b : True := trivial", encoding="utf-8")
    source = read_lean_source(quarantine)
    assert "theorem a" in source and "theorem b" in source
    assert read_lean_source(tmp_path / "missing") is None  # absent dir
    empty = tmp_path / "empty"
    empty.mkdir()
    assert read_lean_source(empty) is None  # no .lean files


def test_aristotle_formalizer_submits_and_reads_produced_lean(tmp_path):
    quarantine = tmp_path / "quar"
    quarantine.mkdir()
    (quarantine / "Candidate.lean").write_text(_CANDIDATE_LEAN, encoding="utf-8")
    client = _FakeSdkClient(quarantine)
    formalizer = AristotleFormalizer(client=client)

    source = formalizer.formalize(
        declaration_name="egmra_demo", expected_type="2 + 2 = 4",
        informal_statement="two plus two is four")

    assert "theorem egmra_demo : 2 + 2 = 4 := rfl" in source
    # The submitted prompt pinned the exact obligation (name + type).
    assert client.prompts and "egmra_demo : 2 + 2 = 4" in client.prompts[0]
    formalizer.close()
    assert client.closed is True


def test_aristotle_formalizer_returns_none_when_vendor_produced_no_lean(tmp_path):
    quarantine = tmp_path / "quar"
    quarantine.mkdir()  # vendor produced nothing usable
    formalizer = AristotleFormalizer(client=_FakeSdkClient(quarantine))
    assert formalizer.formalize(
        declaration_name="d", expected_type="True", informal_statement="x") is None
