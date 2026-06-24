import pytest

from holiday_management.utils.query_processing import (
    handle_query,
    transform_query,
    validate_query,
)


def test_validate_rejects_too_short():
    with pytest.raises(ValueError):
        validate_query("hi")


def test_validate_rejects_invalid_characters():
    with pytest.raises(ValueError):
        validate_query("plan a trip ☃☃☃ ★★★")


def test_validate_accepts_realistic_request():
    assert validate_query("Plan a 5-day trip to Paris for $2,000") is True


def test_transform_normalises_and_signs():
    result = transform_query("  Plan a  HOLIDAY   to Paris  ")
    assert result["normalized"] == "plan a holiday to paris"
    # 'holiday' -> 'trip' synonym, stop-words removed
    assert result["cleaned"] == "plan trip paris"
    assert result["signature"] == "plan_trip_paris"


def test_synonyms_map_equivalent_requests_to_same_signature():
    a = handle_query("a cheap holiday for my kids")
    b = handle_query("a budget trip for my family")
    assert a["signature"] == b["signature"]


def test_handle_query_validates_then_transforms():
    out = handle_query("Plan a relaxing beach vacation")
    assert out["original"] == "Plan a relaxing beach vacation"
    assert "signature" in out
