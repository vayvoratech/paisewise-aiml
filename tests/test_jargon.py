from services.jargon_service import get_jargon, llm_client


def test_cache_hit():

    result = get_jargon(
        "Mutual Fund",
        "en"
    )

    assert result["term"] == "Mutual Fund"
    assert result["language"] == "en"


def test_cache_miss():

    result = get_jargon(
        "New Term",
        "en"
    )

    assert result["term"] == "New Term"
    assert result["language"] == "en"
    assert "explanation" in result


def test_llm_failure_fallback(monkeypatch):

    def mock_failure(prompt):
        raise Exception("LLM failed")


    monkeypatch.setattr(
        llm_client,
        "generate_response",
        mock_failure
    )


    result = get_jargon(
        "Mutual Fund",
        "en"
    )


    assert result["term"] == "Mutual Fund"
    assert "explanation" in result


def test_telugu_language_support():

    result = get_jargon(
        "Mutual Fund",
        "te"
    )

    assert result["term"] == "Mutual Fund"
    assert result["language"] == "te"
    assert "explanation" in result