import json
from pathlib import Path
from typing import Dict, List


DEFAULT_WEIGHTS = {
    "return": 0.40,
    "risk": 0.30,
    "expense": 0.20,
    "amc": 0.10,
}


def calculate_revised_weights(reviews: List[Dict]) -> Dict[str, float]:
    
    if not reviews:
        raise ValueError("At least one real reviewer response is required.")

    totals = {key: 0.0 for key in DEFAULT_WEIGHTS}

    for review in reviews:
        for key in totals:
            value = float(review[key])
            if not 1 <= value <= 5:
                raise ValueError(f"{key} rating must be between 1 and 5.")
            totals[key] += value

    total = sum(totals.values())
    return {key: round(value / total, 4) for key, value in totals.items()}


def save_revised_weights(weights: Dict[str, float], output_file: str) -> None:
    Path(output_file).write_text(
        json.dumps(weights, indent=2),
        encoding="utf-8",
    )
