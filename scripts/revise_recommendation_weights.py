import argparse
import csv
from pathlib import Path

from app.services.recommendation_feedback import (
    calculate_revised_weights,
    save_revised_weights,
)


def load_reviews(path: str):
    with Path(path).open(encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("feedback_csv")
    parser.add_argument(
        "--output",
        default="data/revised_recommendation_weights.json",
    )
    args = parser.parse_args()

    reviews = load_reviews(args.feedback_csv)

    if len(reviews) < 5:
        raise SystemExit(
            "Week 8 requires feedback from at least 5 internal reviewers."
        )

    weights = calculate_revised_weights(reviews[:5])
    save_revised_weights(weights, args.output)
    print(weights)
