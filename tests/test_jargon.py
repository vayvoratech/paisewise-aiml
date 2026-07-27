from services.jargon_service import get_jargon, llm_client


def test_cache_hit():

    result = get_jargon(
        "Mutual Fund",
        "english"
    )

    assert result["term"] == "Mutual Fund"
    assert result["language"] == "english"
def test_cache_miss():

    result = get_jargon(
        "New Term",
        "english"
    )

    assert result["term"] == "New Term"
    assert result["language"] == "english"
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
        "english"
    )


    assert result["term"] == "Mutual Fund"
    assert "explanation" in result