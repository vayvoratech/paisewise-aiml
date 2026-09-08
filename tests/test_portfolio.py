from services.portfolio_service import (
    get_portfolio_insight,
    llm_client
)


PORTFOLIO_INPUT = {
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "holdings": [
        {
            "symbol": "INFY",
            "quantity": 10,
            "avg_buy_price": 1500.0
        },
        {
            "symbol": "TCS",
            "quantity": 5,
            "avg_buy_price": 3800.0
        }
    ]
}


def test_portfolio_cache_miss():

    from services.portfolio_service import cache

    cache.delete(
        "portfolio_insight:550e8400-e29b-41d4-a716-446655440000:en"
    )

    result = get_portfolio_insight(
        PORTFOLIO_INPUT,
        "en"
    )

    assert "insight" in result
    assert result["source"] in [
        "llm",
        "cache",
        "fallback"
    ]


def test_portfolio_cache_hit():

    cache_key = (
        "portfolio_insight:"
        "550e8400-e29b-41d4-a716-446655440000:en"
    )

    cache_value = "Test cached portfolio insight response"

    from services.portfolio_service import cache

    cache.delete(cache_key)

    cache.set(
        cache_key,
        cache_value,
        expiry=86400
    )

    result = get_portfolio_insight(
        PORTFOLIO_INPUT,
        "en"
    )

    assert "insight" in result
    assert result["source"] == "cache"


def test_portfolio_llm_failure_fallback(monkeypatch):

    def mock_failure(prompt):
        raise Exception("LLM failed")

    monkeypatch.setattr(
        llm_client,
        "generate_response",
        mock_failure
    )

    portfolio_input = {
        "user_id": "550e8400-e29b-41d4-a716-446655440001",
        "holdings": [
            {
                "symbol": "INFY",
                "quantity": 10,
                "avg_buy_price": 1500.0
            }
        ]
    }

    result = get_portfolio_insight(
        portfolio_input,
        "en"
    )

    assert result["source"] == "fallback"
    assert "insight" in result


def test_portfolio_hindi_request():

    portfolio_input = {
        "user_id": "550e8400-e29b-41d4-a716-446655440002",
        "holdings": [
            {
                "symbol": "INFY",
                "quantity": 10,
                "avg_buy_price": 1500.0
            }
        ]
    }

    result = get_portfolio_insight(
        portfolio_input,
        "hi"
    )

    assert "insight" in result


def test_portfolio_telugu_request():

    portfolio_input = {
        "user_id": "550e8400-e29b-41d4-a716-446655440003",
        "holdings": [
            {
                "symbol": "TCS",
                "quantity": 5,
                "avg_buy_price": 3800.0
            }
        ]
    }

    result = get_portfolio_insight(
        portfolio_input,
        "te"
    )

    assert "insight" in result
