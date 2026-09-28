from app.services.response_validator import validate_response


def test_concise_response_is_valid():
    response = (
        "An ETF is a fund traded on an exchange. "
        "It can provide exposure to multiple assets."
    )

    result = validate_response(response)

    assert result.valid is True


def test_empty_response_is_not_valid():
    result = validate_response("")

    assert result.valid is False


def test_response_with_required_information_remains_valid():
    response = (
        "A diversified portfolio spreads investments across "
        "different assets, which can help reduce concentration risk."
    )

    result = validate_response(response)

    assert result.valid is True