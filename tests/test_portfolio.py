from services.portfolio_service import (
    get_portfolio_insight,
    llm_client
)


def test_portfolio_cache_miss():

    result = get_portfolio_insight(
        "test_user_1",
        "english"
    )

    assert "insight" in result
    assert result["source"] in [
        "llm",
        "cache"
    ]


def test_portfolio_cache_hit():

    cache_key = "portfolio_insight:test_user_1"

    cache_value = "Test cached portfolio insight response"


    from services.portfolio_service import cache

    cache.set(
        cache_key,
        cache_value,
        expiry=86400
    )


    result = get_portfolio_insight(
        "test_user_1",
        "english"
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


    result = get_portfolio_insight(
        "failure_user",
        "english"
    )


    assert result["source"] == "fallback"
    assert "insight" in result



def test_portfolio_hindi_request():

    result = get_portfolio_insight(
        "hindi_user",
        "hindi"
    )

    assert "insight" in result