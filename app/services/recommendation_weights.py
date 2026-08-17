import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WEIGHTS_FILE = ROOT / "data" / "revised_recommendation_weights.json"

DEFAULT_WEIGHTS = {
    "return": 0.40,
    "risk": 0.30,
    "expense": 0.20,
    "amc": 0.10,
}


def get_active_weights():
    if not WEIGHTS_FILE.exists():
        return DEFAULT_WEIGHTS.copy()

    try:
        weights = json.loads(WEIGHTS_FILE.read_text(encoding="utf-8"))
        if set(weights) != set(DEFAULT_WEIGHTS):
            return DEFAULT_WEIGHTS.copy()

        total = sum(float(value) for value in weights.values())
        if total <= 0:
            return DEFAULT_WEIGHTS.copy()

        return {
            key: float(value) / total
            for key, value in weights.items()
        }
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        return DEFAULT_WEIGHTS.copy()
