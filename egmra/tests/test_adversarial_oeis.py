"""Adversarial local-transform, cache, and conjecture-tier tests for OEIS."""

from __future__ import annotations

import json
from unittest import mock

import pytest

import egmra.oeis.matching as matching_module
from egmra.oeis import (
    Match,
    OEISClient,
    OEISUnavailable,
    TransformError,
    TransformStep,
    apply_transform,
    held_out_verification,
    run_oeis_workflow,
    score_match,
)


class _HTTPResponse:
    def __init__(
        self,
        *,
        url: str,
        payload: bytes = b'{"results": []}',
        status_code: int = 200,
        headers: dict[str, str] | None = None,
    ) -> None:
        self.url = url
        self.text = payload.decode("utf-8")
        self.status_code = status_code
        self.headers = headers or {}
        self.closed = False
        self._payload = payload

    def raise_for_status(self) -> None:
        return None

    def iter_content(self, chunk_size: int):
        del chunk_size
        return iter((self._payload,))

    def close(self) -> None:
        self.closed = True


def test_live_oeis_fetch_rejects_redirect_downgrade_before_following() -> None:
    response = _HTTPResponse(
        url="https://oeis.org/search?q=1",
        status_code=302,
        headers={"Location": "http://oeis.org/search?q=1"},
    )
    client = OEISClient(offline=False, min_interval_s=0)
    with mock.patch(
        "requests.sessions.Session.request", return_value=response
    ) as transport:
        with pytest.raises(OEISUnavailable):
            client.query_terms([1], use_cache=False)
    assert transport.call_count == 1
    assert response.closed


def test_live_oeis_fetch_is_bounded_and_preserves_default_tls_verification() -> None:
    response = _HTTPResponse(
        url="https://oeis.org/search?q=1",
        headers={"Content-Length": str(4 * 1024 * 1024 + 1)},
    )
    client = OEISClient(offline=False, min_interval_s=0)
    with mock.patch(
        "requests.sessions.Session.request", return_value=response
    ) as transport:
        with pytest.raises(OEISUnavailable, match="size limit"):
            client.query_terms([1], use_cache=False)
    assert "verify" not in transport.call_args.kwargs
    assert transport.call_args.kwargs["allow_redirects"] is False
    assert transport.call_args.kwargs["stream"] is True
    assert response.closed


def test_transform_enumeration_does_not_swallow_internal_failures(monkeypatch):
    def broken_transform(*_args, **_kwargs):
        raise RuntimeError("transform implementation defect")

    monkeypatch.setattr(matching_module, "apply_path", broken_transform)
    with pytest.raises(RuntimeError, match="implementation defect"):
        matching_module.enumerate_transform_paths([1, 2, 3])


def test_integer_transforms_reject_float_and_boolean_inputs() -> None:
    for bad in ([1.5, 2.5], [True, 2]):
        with pytest.raises(TransformError):
            apply_transform("binomial_transform", bad)
        with pytest.raises(TransformError):
            apply_transform("mobius_transform", bad)


def test_missing_required_transform_parameter_is_typed_error_and_step_is_immutable() -> None:
    with pytest.raises(TransformError):
        apply_transform("complement", [1, 2])
    step = TransformStep("drop_prefix", {"count": 1})
    with pytest.raises(TypeError):
        step.params["count"] = 0


def test_empty_held_out_set_never_passes_and_checked_count_is_actual() -> None:
    empty = held_out_verification(lambda n: n, [], formula="n")
    assert not empty.passed and empty.checked_terms == 0
    failed_first = held_out_verification(lambda n: n + 1, [(1, 99), (2, 2)], formula="n+1")
    assert not failed_first.passed and failed_first.checked_terms == 1


def test_no_match_or_no_held_out_support_stays_t0() -> None:
    no_match = run_oeis_workflow(
        interpretation_id="i", query_terms=[1, 2, 3], candidate_matches=[]
    )
    assert no_match.conjecture_claim["truth_tier"] == "T0_unknown"
    match = Match("A000027", ("identity",), 3, True)
    unverified = run_oeis_workflow(
        interpretation_id="i", query_terms=[1, 2, 3], candidate_matches=[match], held_out=[]
    )
    assert unverified.conjecture_claim["truth_tier"] == "T0_unknown"


def test_impossible_caller_supplied_prefix_metadata_is_rejected() -> None:
    impossible = Match("A000000", ("identity",), prefix_overlap=4, prefix_exact=True)
    with pytest.raises(ValueError):
        score_match([1, 2, 3], impossible, transform_len=1)


def test_cache_content_hash_is_verified_before_offline_use(tmp_path) -> None:
    client = OEISClient(
        fetcher=lambda _url: '{"results": [{"number": 27}]}',
        cache_dir=tmp_path,
        offline=False,
        min_interval_s=0,
    )
    client.query_terms([1, 2, 3])
    cache_file = next(tmp_path.glob("*.json"))
    document = json.loads(cache_file.read_text(encoding="utf-8"))
    document["response_text"] = '{"results": [{"number": 999999}]}'
    cache_file.write_text(json.dumps(document), encoding="utf-8")

    restarted = OEISClient(cache_dir=tmp_path, offline=True, min_interval_s=0)
    with pytest.raises(OEISUnavailable, match="integrity"):
        restarted.query_terms([1, 2, 3])


def test_malformed_http_json_and_query_injection_fail_closed() -> None:
    client = OEISClient(fetcher=lambda _url: "<html>error</html>", offline=False, min_interval_s=0)
    with pytest.raises(OEISUnavailable, match="JSON"):
        client.query_terms([1, 2, 3])
    with pytest.raises(ValueError):
        client.query_anumber("A000045&id:A000027")
    with pytest.raises(ValueError):
        client.query_terms([1, 2.5])
