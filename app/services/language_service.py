import csv
from pathlib import Path
from typing import Dict, List


ROOT = Path(__file__).resolve().parents[2]
LANGUAGE_FILE = ROOT / "data" / "indian_languages.csv"


DEFAULT_LANGUAGE_CODE = "hi"

SUPPORTED_LANGUAGES: Dict[str, str] = {}


def _load_languages() -> Dict[str, str]:
    if not LANGUAGE_FILE.exists():
        raise FileNotFoundError(f"Language catalogue not found: {LANGUAGE_FILE}")

    with LANGUAGE_FILE.open(encoding="utf-8", newline="") as file:
        rows = csv.DictReader(file)
        return {
            row["language_code"].strip().lower(): row["language_name"].strip()
            for row in rows
            if row.get("language_code") and row.get("language_name")
        }


SUPPORTED_LANGUAGES = _load_languages()


def get_languages() -> List[dict]:
    
    return [
        {"code": code, "name": name}
        for code, name in SUPPORTED_LANGUAGES.items()
    ]


def get_language_name(language: str) -> str:
    
    value = (language or "").strip().lower()

    if value in SUPPORTED_LANGUAGES:
        return SUPPORTED_LANGUAGES[value]

    for code, name in SUPPORTED_LANGUAGES.items():
        if value == name.lower():
            return name

    if value in {"english", "en"}:
        return "English"

    raise ValueError(
        "Unsupported language. Use one of the 22 scheduled Indian languages."
    )


def get_language_code(language: str) -> str:
    
    value = (language or "").strip().lower()

    if value in SUPPORTED_LANGUAGES:
        return value

    for code, name in SUPPORTED_LANGUAGES.items():
        if value == name.lower():
            return code

    if value in {"english", "en"}:
        return "en"

    raise ValueError(
        "Unsupported language. Use one of the 22 scheduled Indian languages."
    )


def is_supported_language(language: str, allow_english: bool = True) -> bool:
    value = (language or "").strip().lower()
    if allow_english and value in {"english", "en"}:
        return True
    return value in SUPPORTED_LANGUAGES or any(
        value == name.lower() for name in SUPPORTED_LANGUAGES.values()
    )
