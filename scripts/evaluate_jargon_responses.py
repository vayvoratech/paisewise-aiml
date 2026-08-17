import argparse
import csv
import json
from pathlib import Path

from app.services.llm_service import generate_portfolio_response


ROOT = Path(__file__).resolve().parents[1]


def build_evaluation_prompt(term, response):
    return f"""
Evaluate this financial-jargon explanation for a beginner Indian investor.

Term: {term}
Response: {response}

Return JSON only with integer scores from 1 to 5 for:
clarity, accuracy, analogy_relevance, beginner_friendliness, completeness, language_quality.
Also return one short improvement suggestion.
"""


def evaluate(input_file, output_file, limit=100):
    with Path(input_file).open(encoding="utf-8", newline="") as file:
        rows = list(csv.DictReader(file))[:limit]

    results = []

    for row in rows:
        prompt = build_evaluation_prompt(
            row.get("term", ""),
            row.get("response", ""),
        )
        raw = generate_portfolio_response(prompt)

        try:
            score = json.loads(raw)
        except json.JSONDecodeError:
            score = {
                "clarity": None,
                "accuracy": None,
                "analogy_relevance": None,
                "beginner_friendliness": None,
                "completeness": None,
                "language_quality": None,
                "improvement": raw,
            }

        result = dict(row)
        result.update(score)
        results.append(result)

    fields = [
        "term",
        "prompt_style",
        "language",
        "response",
        "clarity",
        "accuracy",
        "analogy_relevance",
        "beginner_friendliness",
        "completeness",
        "language_quality",
        "improvement",
    ]

    with Path(output_file).open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(results)

    print(f"Evaluated {len(results)} responses.")
    print(f"Saved report to {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file")
    parser.add_argument("--output", default=str(ROOT / "data" / "jargon_quality_results.csv"))
    parser.add_argument("--limit", type=int, default=100)
    args = parser.parse_args()
    evaluate(args.input_file, args.output, args.limit)
