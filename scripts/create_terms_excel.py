import csv
from pathlib import Path

from openpyxl import Workbook


ROOT = Path(__file__).resolve().parents[1]
CSV_FILE = ROOT / "data" / "financial_terms.csv"
OUTPUT_FILE = ROOT / "data" / "financial_terms.xlsx"


def create_excel():
    with CSV_FILE.open(encoding="utf-8", newline="") as file:
        rows = list(csv.DictReader(file))

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Financial Terms"

    sheet.append(["term", "category", "difficulty"])

    for row in rows:
        sheet.append([
            row["term"],
            row["category"],
            row["difficulty"],
        ])

    workbook.save(OUTPUT_FILE)
    print(f"Created {OUTPUT_FILE} with {len(rows)} financial terms.")


if __name__ == "__main__":
    create_excel()
