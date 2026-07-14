"""Tests for the OEIS service: transforms, client policy/cache, matching workflow."""

from fractions import Fraction

import pytest

from egmra.oeis import (
    Match,
    OEISClient,
    OEISPolicyError,
    OEISUnavailable,
    TransformError,
    apply_transform,
    get_transform,
    held_out_verification,
    prefix_overlap,
    run_oeis_workflow,
)
from egmra.oeis.transforms import REGISTERED_TRANSFORMS


# ── transforms ────────────────────────────────────────────────────────────────

def test_all_twenty_transforms_registered():
    expected = {
        "identity", "shift_index", "drop_prefix", "negate", "absolute", "complement",
        "normalize_gcd", "first_difference", "higher_differences", "partial_sums",
        "ratios_if_exact", "even_subsequence", "odd_subsequence", "arithmetic_subsequence",
        "interleave_split", "binomial_transform", "inverse_binomial", "euler_transform",
        "mobius_transform", "dirichlet_inverse",
    }
    assert expected <= set(REGISTERED_TRANSFORMS)


def test_first_difference_and_partial_sums_are_inverse_ish():
    seq = [1, 4, 9, 16, 25]
    diff = apply_transform("first_difference", seq)
    assert diff == [3, 5, 7, 9]
    assert apply_transform("partial_sums", [1, 3, 5, 7, 9]) == [1, 4, 9, 16, 25]


def test_ratios_reject_zero_denominator():
    with pytest.raises(TransformError):
        apply_transform("ratios_if_exact", [0, 1, 2])
    assert apply_transform("ratios_if_exact", [1, 2, 4]) == [Fraction(2), Fraction(2)]


def test_complement_requires_universe():
    with pytest.raises(TransformError):
        apply_transform("complement", [1, 2, 3])
    assert apply_transform("complement", [1, 2, 3], universe=10) == [9, 8, 7]


def test_binomial_transform_roundtrips_with_inverse():
    seq = [1, 2, 4, 8, 16]
    fwd = apply_transform("binomial_transform", seq)
    back = apply_transform("inverse_binomial", fwd)
    assert back == seq


def test_dirichlet_inverse_requires_invertible_first_term():
    with pytest.raises(TransformError):
        apply_transform("dirichlet_inverse", [2, 3, 4])  # a(1)=2 not invertible
    # a(n)=1 -> Dirichlet inverse is the Mobius function
    inv = apply_transform("dirichlet_inverse", [1, 1, 1, 1, 1, 1])
    assert inv[0] == 1 and inv[1] == -1 and inv[3] == 0  # mu(1),mu(2),mu(4)


def test_mobius_transform_of_ones_gives_indicator():
    # sum_{d|n} mu(n/d)*1 = [n==1]
    out = apply_transform("mobius_transform", [1, 1, 1, 1, 1, 1])
    assert out[0] == 1 and all(x == 0 for x in out[1:])


def test_undefined_transform_fails_visibly():
    with pytest.raises(TransformError):
        get_transform("does_not_exist")
    with pytest.raises(TransformError):
        apply_transform("identity", [1, 2], bogus_param=1)


# ── client policy & cache ─────────────────────────────────────────────────────

def test_client_refuses_submission():
    client = OEISClient(offline=True)
    with pytest.raises(OEISPolicyError):
        client.submit(sequence=[1, 2, 3])


def test_client_offline_without_cache_raises():
    client = OEISClient(offline=True)
    with pytest.raises(OEISUnavailable):
        client.query_terms([1, 2, 5, 14, 42])


def test_client_uses_injected_fetcher_and_caches(tmp_path):
    calls = {"n": 0}

    def fake_fetcher(url):
        calls["n"] += 1
        return '{"results": [{"number": 108, "data": "1,1,2,5,14,42"}]}'

    client = OEISClient(fetcher=fake_fetcher, cache_dir=tmp_path, offline=False)
    r1 = client.query_terms([1, 1, 2, 5, 14, 42])
    assert r1.entries()[0]["number"] == 108
    assert r1.content_hash
    # second call served from cache; fetcher not called again
    r2 = client.query_terms([1, 1, 2, 5, 14, 42])
    assert r2.from_cache and calls["n"] == 1


# ── matching workflow ──────────────────────────────────────────────────────────

def test_prefix_overlap():
    assert prefix_overlap([1, 2, 3, 9], [1, 2, 3, 4]) == 3


def test_workflow_marks_match_as_conjecture_not_proof():
    terms = [1, 4, 9, 16, 25, 36]
    match = Match(a_number="A000290", matched_transform=("identity",),
                  prefix_overlap=6, prefix_exact=True, name="squares")
    held = [held_out_verification(lambda n: n * n, [(7, 49), (8, 64)], formula="n^2")]
    result = run_oeis_workflow(interpretation_id="int-1", query_terms=terms,
                               candidate_matches=[match], held_out=held)
    assert result.conjecture_claim["evidence_kind"] == "numerical"
    assert result.conjecture_claim["truth_tier"] == "T1_supported_conjecture"
    assert result.conjecture_claim["held_out_supported_formula"] == "n^2"
    assert result.ranked_matches[0][0].a_number == "A000290"


def test_held_out_verification_rejects_wrong_formula():
    res = held_out_verification(lambda n: n + 1, [(7, 49)], formula="n+1")
    assert not res.passed
