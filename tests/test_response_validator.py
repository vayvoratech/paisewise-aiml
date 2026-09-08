import pytest

from app.services.response_validator import (
    validate_response,
)


def test_valid_educational_response():
    result = validate_response(
        "An ETF is a fund that can be traded on a stock exchange."
    )

    assert result.valid is True
    assert result.message is None


def test_empty_response_is_invalid():
    result = validate_response("")

    assert result.valid is False
    assert result.message is not None


def test_whitespace_response_is_invalid():
    result = validate_response("   \n\t   ")

    assert result.valid is False


def test_non_string_response_raises_type_error():
    with pytest.raises(TypeError):
        validate_response(None)

    with pytest.raises(TypeError):
        validate_response(123)


def test_should_buy_is_blocked():
    result = validate_response(
        "You should buy this stock."
    )

    assert result.valid is False


def test_should_sell_is_blocked():
    result = validate_response(
        "You should sell this stock."
    )

    assert result.valid is False


def test_should_invest_is_blocked():
    result = validate_response(
        "You should invest in this fund."
    )

    assert result.valid is False


def test_recommend_buying_is_blocked():
    result = validate_response(
        "I recommend buying this stock."
    )

    assert result.valid is False


def test_recommend_selling_is_blocked():
    result = validate_response(
        "I recommend selling this stock."
    )

    assert result.valid is False


def test_guaranteed_profit_is_blocked():
    result = validate_response(
        "This investment provides guaranteed profit."
    )

    assert result.valid is False


def test_guaranteed_return_is_blocked():
    result = validate_response(
        "You are guaranteed a return from this investment."
    )

    assert result.valid is False


def test_risk_free_claim_is_blocked():
    result = validate_response(
        "This is a risk-free investment."
    )

    assert result.valid is False


def test_case_variation_is_blocked():
    result = validate_response(
        "YOU SHOULD BUY this stock."
    )

    assert result.valid is False


def test_multiple_spaces_are_handled():
    result = validate_response(
        "You   should   buy   this stock."
    )

    assert result.valid is False


def test_newlines_are_handled():
    result = validate_response(
        "You should\nbuy this stock."
    )

    assert result.valid is False


def test_tabs_are_handled():
    result = validate_response(
        "You should\tbuy this stock."
    )

    assert result.valid is False


def test_hyphen_variation_is_handled():
    result = validate_response(
        "This is a risk-free investment."
    )

    assert result.valid is False


def test_general_financial_education_is_allowed():
    result = validate_response(
        "Diversification means spreading investments "
        "across different assets to manage risk."
    )

    assert result.valid is True