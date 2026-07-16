import pytest

from ranking_policy import classify_prize, selection_priority_tier


@pytest.mark.parametrize("value", ["no", "NO", " No "])
def test_only_explicit_no_is_unpaid(value):
    assert classify_prize(value) == "unpaid"


@pytest.mark.parametrize("value", ["$500", "10,000 USD", "€500", "£500"])
def test_monetary_strings_are_paid_without_currency_conversion(value):
    assert classify_prize(value) == "paid"


@pytest.mark.parametrize("value", [None, "", "   ", 500, {}, [], "prize"])
def test_missing_or_malformed_prize_is_unknown(value):
    assert classify_prize(value) == "unknown"


def test_priority_tier_rejects_unknown():
    assert selection_priority_tier("unpaid") == 0
    assert selection_priority_tier("paid") == 1
    with pytest.raises(ValueError, match="unknown prize metadata"):
        selection_priority_tier("unknown")
