import argparse
import csv
from collections import defaultdict
from pathlib import Path


def review(input_file: str, output_file: str, threshold: float = 3.0):
    rows = list(csv.DictReader(Path(input_file).open(encoding="utf-8", newline="")))

    by_term = defaultdict(list)
    for row in rows:
        values = []
        for key in (
            "clarity",
            "accuracy",
            "analogy_relevance",
            "beginner_friendliness",
            "completeness",
            "language_quality",
        ):
            try:
                values.append(float(row[key]))
            except (TypeError, ValueError):
                pass

        if values:
            by_term[row.get("term", "")].append(sum(values) / len(values))

    results = []
    for term, scores in by_term.items():
        average = sum(scores) / len(scores)
        if average <= threshold:
            results.append({
                "term": term,
                "average_score": round(average, 2),
                "action": (
                    "Rewrite prompt for clarity and beginner friendliness; "
                    "review analogy and accuracy."
                ),
            })

    results.sort(key=lambda row: row["average_score"])

    with Path(output_file).open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["term", "average_score", "action"],
        )
        writer.writeheader()
        writer.writerows(results)

    print(f"Low-scoring terms: {len(results)}")
    print(f"Saved: {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file")
    parser.add_argument("--output", default="data/jargon_prompt_revisions.csv")
    parser.add_argument("--threshold", type=float, default=3.0)
    args = parser.parse_args()

    review(args.input_file, args.output, args.threshold)
