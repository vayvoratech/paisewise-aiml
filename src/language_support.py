# ============================================================
# PAISEWISE MULTI-LANGUAGE SUPPORT
# ============================================================

SUPPORTED_LANGUAGES = {
    "en": "English",
    "hi": "Hindi",
    "ta": "Tamil",
    "te": "Telugu",
    "kn": "Kannada",
    "ml": "Malayalam",
}

DEFAULT_LANGUAGE = "en"


def is_supported_language(language: str) -> bool:
    """
    Check whether the requested language is supported.
    """
    if not language:
        return False

    return language.lower() in SUPPORTED_LANGUAGES


def normalize_language(language: str) -> str:
    """
    Convert language code to lowercase
    and return English if invalid.
    """
    if not language:
        return DEFAULT_LANGUAGE

    language = language.lower()

    if language in SUPPORTED_LANGUAGES:
        return language

    return DEFAULT_LANGUAGE


def get_language_name(language: str) -> str:
    """
    Get the full language name from language code.
    """
    language = normalize_language(language)

    return SUPPORTED_LANGUAGES[language]


def get_supported_languages():
    """
    Return all supported languages.
    """
    return SUPPORTED_LANGUAGES.copy()


def get_fallback_chain(language: str):
    """
    Return the language fallback order.

    Example:
    Tamil -> Hindi -> English
    """

    language = normalize_language(language)

    fallback_chains = {
        "en": [
            "en"
        ],

        "hi": [
            "hi",
            "en"
        ],

        "ta": [
            "ta",
            "hi",
            "en"
        ],

        "te": [
            "te",
            "hi",
            "en"
        ],

        "kn": [
            "kn",
            "hi",
            "en"
        ],

        "ml": [
            "ml",
            "hi",
            "en"
        ]
    }

    return fallback_chains[language]


def get_next_fallback_language(
    current_language: str,
    fallback_chain: list[str]
):
    """
    Return the next language in the fallback chain.

    Example:
    Tamil chain = ["ta", "hi", "en"]

    ta -> hi
    hi -> en
    en -> None
    """

    current_language = normalize_language(current_language)

    if current_language not in fallback_chain:
        return None

    current_index = fallback_chain.index(current_language)

    if current_index + 1 < len(fallback_chain):
        return fallback_chain[current_index + 1]

    return None

def should_fallback(quality_score):
    """
    Determine whether the response should fall back
    to another language.

    Quality rules:
    - 3.0 or above -> acceptable
    - Below 3.0 -> fallback required
    - None -> do not force fallback
    """

    if quality_score is None:
        return False

    return float(quality_score) < 3.0    