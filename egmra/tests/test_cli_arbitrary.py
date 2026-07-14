"""Integration tests for the arbitrary-problem CLI, doctor, and status commands."""

from __future__ import annotations

import json

import pytest

from egmra.cli import main
from egmra.lean import sign_formal_correspondence_certificate
from egmra.policy import sign_policy
from egmra.provenance.hashing import sha256_hex
from egmra.truth.entities import FormalCorrespondenceCertificate, Verdict


def _signed_policy_file(tmp_path):
    policy = sign_policy({
        "claim_graph": True, "literature_retrieval": True,
        "computation_service": True, "promotion": False,
    })
    path = tmp_path / "policy.json"
    path.write_text(json.dumps(policy.to_document()))
    return path


def _config_file(tmp_path):
    cfg = tmp_path / "cfg.json"
    cfg.write_text(json.dumps({"events_dir": str(tmp_path / "runs")}))
    return cfg


_CORPUS_TEX = r"""\documentclass{article}
\begin{document}
\section{Problem \#7}
\noindent\textbf{Statement:}

Does every sufficiently large integer have property $P$?

\end{document}
"""


def test_run_statement_is_honest_open_state(tmp_path, capsys):
    cfg = _config_file(tmp_path)
    policy = _signed_policy_file(tmp_path)
    rc = main(["--config", str(cfg), "run",
               "--statement", "Every group of prime order is cyclic.",
               "--provider", "deterministic", "--policy", str(policy)])
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert out["result_state"]["state"] in {"OPEN_NO_PROGRESS", "PARTIAL_PROGRESS"}
    assert out["proof_complete"] is False
    assert out["release"] is None
    assert out["input"]["kind"] == "statement"
    assert out["provider"] == "deterministic"


def test_run_browser_provider_without_profile_fails_cleanly(tmp_path, capsys, monkeypatch):
    # The primary provider must fail explicitly, never silently degrade — and the
    # test must never launch a real browser.
    import egmra.agents.browser_runner as br

    def _no_browser(self):
        raise RuntimeError("no authenticated profile / no display")

    monkeypatch.setattr(br.PlaywrightChatGPTBackend, "start", _no_browser)
    cfg = _config_file(tmp_path)
    policy = _signed_policy_file(tmp_path)
    rc = main(["--config", str(cfg), "run", "--statement", "A statement.",
               "--provider", "browser", "--policy", str(policy)])
    assert rc == 2
    err = json.loads(capsys.readouterr().err)
    assert err["error"] == "ValueError"
    assert "browser provider is not operational" in err["detail"]


def test_run_rejects_out_of_range_workers(tmp_path, capsys):
    cfg = _config_file(tmp_path)
    policy = _signed_policy_file(tmp_path)
    rc = main(["--config", str(cfg), "run", "--statement", "A statement.",
               "--provider", "deterministic", "--workers", "9", "--policy", str(policy)])
    assert rc == 2


def test_provider_unavailable_is_retained_not_a_math_failure(tmp_path, capsys, monkeypatch):
    # Defect 13: browser exhaustion must retain the job and report a retryable
    # status with a distinct exit code — never a mathematical verdict.
    import egmra.cli as cli_module
    from egmra.agents.browser_runner import BrowserProviderUnavailable

    def _throttled(**_kwargs):
        raise BrowserProviderUnavailable("throttled after 6 cooldowns")

    monkeypatch.setattr(cli_module, "research", _throttled)
    cfg = _config_file(tmp_path)
    policy = _signed_policy_file(tmp_path)
    rc = main(["--config", str(cfg), "run", "--statement", "A statement.",
               "--provider", "deterministic", "--policy", str(policy)])
    assert rc == 4
    out = json.loads(capsys.readouterr().out)
    assert out["status"] == "provider_unavailable"
    assert out["retain"] is True
    assert "not a mathematical result" in out["note"]


def test_run_does_not_touch_fixture_loader(tmp_path, capsys, monkeypatch):
    # The primary run path must never call the bundled fixture loader.
    import egmra.cli as cli_module

    def _boom(*_a, **_k):  # pragma: no cover - only fails if wrongly called
        raise AssertionError("arbitrary run must not call fixture()")

    monkeypatch.setattr(cli_module, "fixture", _boom)
    cfg = _config_file(tmp_path)
    policy = _signed_policy_file(tmp_path)
    rc = main(["--config", str(cfg), "run", "--statement", "A statement.",
               "--provider", "deterministic", "--policy", str(policy)])
    assert rc == 0
    assert json.loads(capsys.readouterr().out)["result_state"]["state"]


def test_run_erdos_from_local_corpus(tmp_path, capsys):
    tex = tmp_path / "corpus.tex"
    tex.write_text(_CORPUS_TEX, encoding="utf-8")
    catalog = tmp_path / "catalog.json"
    catalog.write_text(json.dumps({"problems": {"7": {
        "problem": 7, "source_state": "open",
        "source_problem_url": "https://www.erdosproblems.com/7",
        "source_last_update": "2025-01-01", "tags": ["number theory"],
    }}}), encoding="utf-8")
    cfg = _config_file(tmp_path)
    policy = _signed_policy_file(tmp_path)
    rc = main(["--config", str(cfg), "run", "--erdos", "7",
               "--corpus-tex", str(tex), "--catalog", str(catalog),
               "--provider", "deterministic", "--policy", str(policy)])
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert out["problem_id"] == "erdos-7"
    assert out["input"]["kind"] == "erdos"
    # A no-solver arbitrary run can only reach an honest pre-release state, never
    # a released/validated one.
    assert out["result_state"]["state"] in {
        "OPEN_NO_PROGRESS", "PARTIAL_PROGRESS",
        "BLOCKED_BY_INTERPRETATION", "CANDIDATE_DISPROOF",
    }
    assert out["proof_complete"] is False
    assert out["release"] is None


def test_run_requires_exactly_one_input(tmp_path, capsys):
    cfg = _config_file(tmp_path)
    policy = _signed_policy_file(tmp_path)
    rc = main(["--config", str(cfg), "run", "--policy", str(policy)])
    assert rc == 2
    assert json.loads(capsys.readouterr().err)["error"] == "ValueError"


def test_run_rejects_multiple_inputs(tmp_path, capsys):
    cfg = _config_file(tmp_path)
    policy = _signed_policy_file(tmp_path)
    rc = main(["--config", str(cfg), "run", "--statement", "x", "--erdos", "7",
               "--policy", str(policy)])
    assert rc == 2
    assert json.loads(capsys.readouterr().err)["error"] == "ValueError"


def test_run_unknown_erdos_number_fails_cleanly(tmp_path, capsys):
    tex = tmp_path / "corpus.tex"
    tex.write_text(_CORPUS_TEX, encoding="utf-8")
    cfg = _config_file(tmp_path)
    policy = _signed_policy_file(tmp_path)
    rc = main(["--config", str(cfg), "run", "--erdos", "999999",
               "--corpus-tex", str(tex), "--policy", str(policy)])
    assert rc == 2
    assert json.loads(capsys.readouterr().err)["error"] == "SourceResolutionError"


def test_status_lists_persisted_runs(tmp_path, capsys):
    cfg = _config_file(tmp_path)
    policy = _signed_policy_file(tmp_path)
    main(["--config", str(cfg), "run", "--statement", "A statement.",
          "--provider", "deterministic", "--policy", str(policy)])
    capsys.readouterr()
    rc = main(["--config", str(cfg), "status"])
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert out["run_count"] >= 1
    assert all(run.get("integrity") for run in out["runs"])


def test_doctor_reports_readiness_without_leaking_secrets(tmp_path, capsys, monkeypatch):
    import egmra.cli as cli_module

    # Keep the probe hermetic: no real lake/lean/aristotle subprocess in tests.
    monkeypatch.setattr(cli_module, "_probe_executable",
                        lambda name, args: {"found": False, "path": "", "operational": False})
    policy = _signed_policy_file(tmp_path)
    rc = main(["doctor", "--policy", str(policy)])
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert out["python_supported"] is True
    assert out["policy"]["loadable"] is True
    assert set(out["ready_for"]) == {
        "local_research", "browser_reasoning", "formal_verification", "aristotle",
    }
    # Only booleans are reported per key — never a value.
    for entry in out["signing_keys"].values():
        assert set(entry) == {"configured", "sufficient_length"}
    serialized = json.dumps(out)
    assert "test-key-that-is-at-least-32-bytes" not in serialized


def test_doctor_distinguishes_launcher_from_operational_lean(tmp_path, capsys, monkeypatch):
    # Defect 16 regression: a launcher on PATH must NOT be reported as ready.
    import egmra.cli as cli_module

    monkeypatch.setattr(
        cli_module, "_probe_executable",
        lambda name, args: {"found": True, "path": f"/usr/bin/{name}",
                            "operational": False, "version": ""},
    )
    policy = _signed_policy_file(tmp_path)
    rc = main(["doctor", "--policy", str(policy)])
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert out["executables"]["lake"]["found"] is True
    assert out["executables"]["lake"]["operational"] is False
    assert out["lean_toolchain"]["operational"] is False
    assert out["ready_for"]["formal_verification"] is False


def test_doctor_reports_unloadable_default_policy(capsys, monkeypatch):
    import egmra.cli as cli_module

    monkeypatch.setattr(cli_module, "_probe_executable",
                        lambda name, args: {"found": False, "path": "", "operational": False})
    rc = main(["doctor"])
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert out["policy"]["loadable"] is False
    assert out["ready_for"]["local_research"] is False


# ── --formal-correspondence-review loader + wiring (task 4.6) ────────────────────

def _correspondence_file(tmp_path, name="corr.json"):
    """Write an independently signed formal-correspondence review JSON artifact."""
    signed = sign_formal_correspondence_certificate(FormalCorrespondenceCertificate(
        certificate_id="corr-goal",
        intent_certificate_id="intent-1",
        informal_claim_hash=sha256_hex("claim"),
        lean_declaration_name="egmra_demo",
        elaborated_type_hash=sha256_hex("2 + 2 = 4"),
        notation_and_definition_map_hash=sha256_hex("map"),
        methods=["backtranslation", "examples", "anti_examples", "paraphrase",
                 "local_mutation"],
        reviewer_ids=["formal-correspondence-reviewer"],
        reviewer_independence_and_conflicts=[{
            "reviewer_id": "formal-correspondence-reviewer",
            "independent_from": ["formalization_authority", "governor"],
            "conflicts": [],
        }],
        verdict=Verdict.APPROVED,
    ))
    path = tmp_path / name
    path.write_text(json.dumps(signed.to_dict()), encoding="utf-8")
    return path, signed


def test_load_formal_correspondence_reviews_none_is_none():
    from egmra.cli import _load_formal_correspondence_reviews

    assert _load_formal_correspondence_reviews(None) is None
    assert _load_formal_correspondence_reviews([]) is None


def test_load_formal_correspondence_reviews_explicit_and_default_claim(tmp_path):
    from egmra.cli import _load_formal_correspondence_reviews

    path, signed = _correspondence_file(tmp_path)
    # Explicit CLAIM_ID=PATH keys the review to the named claim.
    explicit = _load_formal_correspondence_reviews([f"branch-lemma={path}"])
    assert set(explicit) == {"branch-lemma"}
    assert explicit["branch-lemma"].certificate_id == signed.certificate_id
    assert explicit["branch-lemma"].verdict is Verdict.APPROVED
    # A bare path (even one containing '=' in the directory) binds the goal claim.
    default = _load_formal_correspondence_reviews([str(path)])
    assert set(default) == {"goal"}
    assert default["goal"].lean_declaration_name == "egmra_demo"


def test_load_formal_correspondence_reviews_rejects_symlink(tmp_path):
    from egmra.cli import _load_formal_correspondence_reviews

    path, _ = _correspondence_file(tmp_path)
    link = tmp_path / "link.json"
    link.symlink_to(path)
    with pytest.raises(ValueError, match="regular non-symlink file"):
        _load_formal_correspondence_reviews([f"goal={link}"])


def test_load_formal_correspondence_reviews_rejects_oversize(tmp_path):
    from egmra.cli import _load_formal_correspondence_reviews

    big = tmp_path / "big.json"
    big.write_text("x" * 1_000_001, encoding="utf-8")
    with pytest.raises(ValueError, match="too large"):
        _load_formal_correspondence_reviews([f"goal={big}"])


def test_load_formal_correspondence_reviews_rejects_duplicate_claim(tmp_path):
    from egmra.cli import _load_formal_correspondence_reviews

    path, _ = _correspondence_file(tmp_path)
    with pytest.raises(ValueError, match="duplicate formal-correspondence-review"):
        _load_formal_correspondence_reviews([f"goal={path}", f"goal={path}"])


def test_run_passes_formal_correspondence_review_through(tmp_path, monkeypatch):
    # The run path parses --formal-correspondence-review, loads the signed artifact,
    # and hands it to research() as the claim-keyed formal_correspondence_reviews.
    import egmra.cli as cli_module
    from egmra.agents.browser_runner import BrowserProviderUnavailable

    captured: dict = {}

    def _capture(**kwargs):
        captured.update(kwargs)
        raise BrowserProviderUnavailable("captured")  # cleanly retained -> rc 4

    monkeypatch.setattr(cli_module, "research", _capture)
    path, signed = _correspondence_file(tmp_path)
    cfg = _config_file(tmp_path)
    policy = _signed_policy_file(tmp_path)
    rc = main(["--config", str(cfg), "run", "--statement", "A statement.",
               "--provider", "deterministic", "--policy", str(policy),
               "--formal-correspondence-review", f"goal={path}"])
    assert rc == 4  # research() short-circuited after capture; not a math verdict
    reviews = captured["formal_correspondence_reviews"]
    assert set(reviews) == {"goal"}
    assert reviews["goal"].certificate_id == signed.certificate_id


def test_run_without_formal_correspondence_review_passes_none(tmp_path, monkeypatch):
    import egmra.cli as cli_module
    from egmra.agents.browser_runner import BrowserProviderUnavailable

    captured: dict = {}

    def _capture(**kwargs):
        captured.update(kwargs)
        raise BrowserProviderUnavailable("captured")

    monkeypatch.setattr(cli_module, "research", _capture)
    cfg = _config_file(tmp_path)
    policy = _signed_policy_file(tmp_path)
    rc = main(["--config", str(cfg), "run", "--statement", "A statement.",
               "--provider", "deterministic", "--policy", str(policy)])
    assert rc == 4
    assert captured["formal_correspondence_reviews"] is None


# ── informal_only is driven by whether a Lean project is configured (task 4.6) ──

def test_run_sets_informal_only_false_when_lean_enabled(tmp_path, monkeypatch):
    import egmra.cli as cli_module
    from egmra.agents.browser_runner import BrowserProviderUnavailable
    from types import SimpleNamespace

    captured: dict = {}

    def _capture(**kwargs):
        captured.update(kwargs)
        raise BrowserProviderUnavailable("captured")

    monkeypatch.setattr(cli_module, "research", _capture)
    # A configured Lean project makes this a formal run without needing a real .lake.
    monkeypatch.setattr(cli_module, "_build_lean_service",
                        lambda args: (SimpleNamespace(), "4.28.0", "v4.28.0"))
    cfg = _config_file(tmp_path)
    policy = _signed_policy_file(tmp_path)
    rc = main(["--config", str(cfg), "run", "--statement", "A statement.",
               "--provider", "deterministic", "--policy", str(policy)])
    assert rc == 4
    assert captured["lean_service"] is not None
    assert captured["informal_only"] is False


def test_run_informal_only_true_without_lean(tmp_path, monkeypatch):
    import egmra.cli as cli_module
    from egmra.agents.browser_runner import BrowserProviderUnavailable

    captured: dict = {}

    def _capture(**kwargs):
        captured.update(kwargs)
        raise BrowserProviderUnavailable("captured")

    monkeypatch.setattr(cli_module, "research", _capture)
    cfg = _config_file(tmp_path)
    policy = _signed_policy_file(tmp_path)
    rc = main(["--config", str(cfg), "run", "--statement", "A statement.",
               "--provider", "deterministic", "--policy", str(policy)])
    assert rc == 4
    assert captured["lean_service"] is None
    assert captured["informal_only"] is True


# ── campaign browser provider drives genuine multi-tab workers (task #3) ────────

class _FakeEngine:
    def __init__(self, workers: int) -> None:
        self.pages = [f"tab{i}" for i in range(workers)]
        self.closed = False

    def close(self) -> None:
        self.closed = True


def test_campaign_browser_multiworker_assigns_distinct_tabs(tmp_path, monkeypatch):
    # The browser campaign no longer rejects --workers > 1: it builds an async
    # multi-tab engine and hands each worker its OWN tab-runner. A 2-worker,
    # 2-problem campaign is forced (via a barrier in the stubbed research) to have
    # both workers active at once, so two DISTINCT tab-runners must be used.
    import threading
    from types import SimpleNamespace
    import egmra.cli as cli_module

    engines: list = []
    monkeypatch.setattr(cli_module, "_build_browser_engine",
                        lambda workers: engines.append(_FakeEngine(workers)) or engines[-1])
    monkeypatch.setattr(cli_module, "from_erdos_number",
                        lambda number, **kw: SimpleNamespace(
                            problem_id=f"erdos-{number}", source_bytes=b"S", source_id="fx",
                            display_statement="S", status_claims=[], novelty_verdict="N1"))

    captured_runners: list = []
    lock = threading.Lock()
    barrier = threading.Barrier(2, timeout=5.0)

    def _fake_research(**kwargs):
        with lock:
            captured_runners.append(kwargs["runner"])
        barrier.wait()  # force genuine 2-worker overlap
        return object()

    monkeypatch.setattr(cli_module, "research", _fake_research)
    monkeypatch.setattr(cli_module, "classify_result",
                        lambda result, **kw: SimpleNamespace(state="OPEN_NO_PROGRESS"))

    cfg = _config_file(tmp_path)
    policy = _signed_policy_file(tmp_path)
    rc = main(["--config", str(cfg), "campaign", "--provider", "browser", "--workers", "2",
               "--erdos-range", "5-6", "--policy", str(policy),
               "--state", str(tmp_path / "camp.json")])
    assert rc == 0
    # Two distinct tab-runners were used (genuine multi-tab), and the shared
    # browser engine was torn down afterward.
    assert len({id(runner) for runner in captured_runners}) == 2
    assert engines and engines[0].closed is True


def test_campaign_browser_workers_no_longer_capped_to_one(tmp_path, monkeypatch):
    # Regression: the browser provider previously raised "supports --workers 1".
    from types import SimpleNamespace
    import egmra.cli as cli_module

    monkeypatch.setattr(cli_module, "_build_browser_engine",
                        lambda workers: _FakeEngine(workers))
    monkeypatch.setattr(cli_module, "from_erdos_number",
                        lambda number, **kw: SimpleNamespace(
                            problem_id=f"erdos-{number}", source_bytes=b"S", source_id="fx",
                            display_statement="S", status_claims=[], novelty_verdict="N1"))
    monkeypatch.setattr(cli_module, "research", lambda **kw: object())
    monkeypatch.setattr(cli_module, "classify_result",
                        lambda result, **kw: SimpleNamespace(state="OPEN_NO_PROGRESS"))
    cfg = _config_file(tmp_path)
    policy = _signed_policy_file(tmp_path)
    rc = main(["--config", str(cfg), "campaign", "--provider", "browser", "--workers", "3",
               "--erdos-range", "5-7", "--policy", str(policy),
               "--state", str(tmp_path / "camp.json")])
    assert rc == 0  # was rc 2 (ValueError: browser supports --workers 1)


# ── autonomous Aristotle formalizer wired into egmra run (task #5) ──────────────

def test_build_formalizer_none_returns_none():
    from types import SimpleNamespace
    from egmra.cli import _build_formalizer

    assert _build_formalizer(SimpleNamespace(formalizer="none")) is None


def test_run_formalizer_aristotle_requires_lean_project(tmp_path, capsys):
    cfg = _config_file(tmp_path)
    policy = _signed_policy_file(tmp_path)
    rc = main(["--config", str(cfg), "run", "--statement", "A statement.",
               "--provider", "deterministic", "--policy", str(policy),
               "--formalizer", "aristotle"])
    assert rc == 2
    err = json.loads(capsys.readouterr().err)
    assert err["error"] == "ValueError"
    assert "--lean-project" in err["detail"]


def test_run_passes_formalizer_to_worker(tmp_path, monkeypatch):
    # `egmra run` builds the formalizer and hands it to the RunnerWorker, so
    # Aristotle is an integrated formalization worker (not a tool beside the run).
    from types import SimpleNamespace
    import egmra.cli as cli_module
    from egmra.agents.browser_runner import BrowserProviderUnavailable

    sentinel = SimpleNamespace(close=lambda: None)
    monkeypatch.setattr(cli_module, "_build_formalizer", lambda args: sentinel)
    captured: dict = {}

    def _capture(**kwargs):
        captured.update(kwargs)
        raise BrowserProviderUnavailable("captured")

    monkeypatch.setattr(cli_module, "research", _capture)
    cfg = _config_file(tmp_path)
    policy = _signed_policy_file(tmp_path)
    rc = main(["--config", str(cfg), "run", "--statement", "A statement.",
               "--provider", "deterministic", "--policy", str(policy)])
    assert rc == 4
    assert captured["worker"].formalizer is sentinel


# ── campaign builds one autonomous formalizer per worker (task #5, campaign) ────

def test_build_worker_formalizers_none_and_requires_project():
    from types import SimpleNamespace
    from egmra.cli import _build_worker_formalizers

    assert _build_worker_formalizers(SimpleNamespace(formalizer="none"), ("w0",)) == {}
    with pytest.raises(ValueError, match="--lean-project"):
        _build_worker_formalizers(
            SimpleNamespace(formalizer="aristotle", lean_project=None), ("w0",))


def test_build_worker_formalizers_one_client_per_worker(tmp_path, monkeypatch):
    from types import SimpleNamespace
    import egmra.cli as cli_module

    built: list = []

    class _FakeClient:
        def __init__(self, **kwargs):
            built.append(kwargs)
            self.closed = False

        def close(self):
            self.closed = True

    monkeypatch.setattr(cli_module, "AristotleSdkClient", _FakeClient)
    formalizers = cli_module._build_worker_formalizers(
        SimpleNamespace(formalizer="aristotle", lean_project=str(tmp_path)), ("w0", "w1"))
    assert set(formalizers) == {"w0", "w1"}
    # Distinct clients (own event loops) and distinct per-worker quarantine roots.
    assert len({id(f.client) for f in formalizers.values()}) == 2
    assert len({str(kw["quarantine_root"]) for kw in built}) == 2


def test_campaign_formalizer_aristotle_requires_lean_project(tmp_path, capsys):
    cfg = _config_file(tmp_path)
    policy = _signed_policy_file(tmp_path)
    rc = main(["--config", str(cfg), "campaign", "--provider", "deterministic",
               "--workers", "1", "--erdos-range", "5", "--policy", str(policy),
               "--state", str(tmp_path / "c.json"), "--formalizer", "aristotle"])
    assert rc == 2
    err = json.loads(capsys.readouterr().err)
    assert err["error"] == "ValueError"
    assert "--lean-project" in err["detail"]


def test_campaign_assigns_and_closes_per_worker_formalizers(tmp_path, monkeypatch):
    import threading
    from types import SimpleNamespace
    import egmra.cli as cli_module

    class _FZ:
        def __init__(self) -> None:
            self.closed = False

        def close(self) -> None:
            self.closed = True

    fzs = {"w0": _FZ(), "w1": _FZ()}
    monkeypatch.setattr(cli_module, "_build_worker_formalizers", lambda args, workers: fzs)
    monkeypatch.setattr(cli_module, "from_erdos_number",
                        lambda number, **kw: SimpleNamespace(
                            problem_id=f"erdos-{number}", source_bytes=b"S", source_id="fx",
                            display_statement="S", status_claims=[], novelty_verdict="N1"))
    seen: list = []
    lock = threading.Lock()
    barrier = threading.Barrier(2, timeout=5.0)

    def _fake_research(**kwargs):
        with lock:
            seen.append(kwargs["worker"].formalizer)
        barrier.wait()  # force genuine 2-worker overlap
        return object()

    monkeypatch.setattr(cli_module, "research", _fake_research)
    monkeypatch.setattr(cli_module, "classify_result",
                        lambda result, **kw: SimpleNamespace(state="OPEN_NO_PROGRESS"))
    cfg = _config_file(tmp_path)
    policy = _signed_policy_file(tmp_path)
    rc = main(["--config", str(cfg), "campaign", "--provider", "deterministic",
               "--workers", "2", "--erdos-range", "5-6", "--policy", str(policy),
               "--state", str(tmp_path / "c.json")])
    assert rc == 0
    # Each worker used its OWN formalizer, and all are closed afterward.
    assert {id(f) for f in seen} == {id(fzs["w0"]), id(fzs["w1"])}
    assert all(formalizer.closed for formalizer in fzs.values())


# ── live scholarly retrieval wired into egmra run (task #7) ─────────────────────

def test_run_retrieval_arxiv_builds_scholarly_corpus(tmp_path, monkeypatch, capsys):
    import egmra.cli as cli_module

    arxiv_xml = ('<?xml version="1.0"?><feed xmlns="http://www.w3.org/2005/Atom">'
                 '<entry><id>http://arxiv.org/abs/2401.00001v1</id>'
                 '<published>2024-01-01T00:00:00Z</published>'
                 '<title>On prime gaps</title><summary>We study gaps.</summary>'
                 '<author><name>Ada Lovelace</name></author></entry></feed>')

    class _FakeFetcher:  # stands in for UrllibFetcher (no network)
        def __init__(self, *a, **k):
            pass

        def __call__(self, url):
            return arxiv_xml

    monkeypatch.setattr(cli_module, "UrllibFetcher", _FakeFetcher)
    cfg = _config_file(tmp_path)
    policy = _signed_policy_file(tmp_path)
    rc = main(["--config", str(cfg), "run", "--statement", "gaps between consecutive primes",
               "--provider", "deterministic", "--policy", str(policy), "--retrieval", "arxiv"])
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert out["retrieval"]["mode"] == "arxiv"
    assert out["retrieval"]["corpus_records"] >= 1  # a real, auditable scholarly record
