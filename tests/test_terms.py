import csv
from pathlib import Path


def test_financial_terms_file_has_200_terms():
    path = Path(__file__).resolve().parents[1] / "data" / "financial_terms.csv"
    with path.open(encoding="utf-8", newline="") as file:
        rows = list(csv.DictReader(file))

    assert len(rows) == 200
    assert all(row["term"] for row in rows)
    assert all(row["category"] for row in rows)
    assert all(row["difficulty"] in {"Beginner", "Intermediate", "Advanced"} for row in rows)
