from app.services.language_service import (
    get_language_code,
    get_language_name,
    get_languages,
    is_supported_language,
)


def test_all_22_scheduled_languages_are_loaded():
    languages = get_languages()
    assert len(languages) == 22


def test_hindi_and_telugu_are_supported():
    assert get_language_code("Hindi") == "hi"
    assert get_language_name("te") == "Telugu"


def test_english_is_fallback_not_scheduled_language():
    assert is_supported_language("English")
    assert len(get_languages()) == 22
