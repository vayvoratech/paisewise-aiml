from services.jargon_service import (
    get_jargon,
    llm_client,
    _normalize_language,
    _build_jargon_prompt,
)


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


def test_language_name_to_code():

    assert _normalize_language("English") == "en"
    assert _normalize_language("Hindi") == "hi"
    assert _normalize_language("Telugu") == "te"
    assert _normalize_language("Kannada") == "kn"
    assert _normalize_language("Tamil") == "ta"
    assert _normalize_language("Malayalam") == "ml"


def test_language_code_is_preserved():

    assert _normalize_language("en") == "en"
    assert _normalize_language("hi") == "hi"
    assert _normalize_language("te") == "te"
    assert _normalize_language("kn") == "kn"
    assert _normalize_language("ta") == "ta"


def test_unsupported_language_falls_back_to_english():

    assert _normalize_language("French") == "en"
    assert _normalize_language("unknown") == "en"


def test_kannada_prompt_requests_kannada():

    prompt = _build_jargon_prompt(
        "Mutual Fund",
        "kn"
    )

    assert "Kannada" in prompt
    assert "Respond completely in Kannada" in prompt
    assert "Do not switch to English" in prompt


def test_telugu_prompt_requests_telugu():

    prompt = _build_jargon_prompt(
        "Mutual Fund",
        "te"
    )

    assert "Telugu" in prompt
    assert "Respond completely in Telugu" in prompt


def test_tamil_prompt_requests_tamil():

    prompt = _build_jargon_prompt(
        "Mutual Fund",
        "ta"
    )

    assert "Tamil" in prompt
    assert "Respond completely in Tamil" in prompt
