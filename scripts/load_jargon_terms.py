import csv
from pathlib import Path

from app.db.database import SessionLocal
from app.db.schema import JargonTerm


ROOT = Path(__file__).resolve().parents[1]
CSV_FILE = ROOT / "data" / "financial_terms.csv"


def load_jargon_terms():
    with CSV_FILE.open(encoding="utf-8", newline="") as file:
        rows = list(csv.DictReader(file))

    db = SessionLocal()

    try:
        inserted = 0
        updated = 0

        for row in rows:
            existing = (
                db.query(JargonTerm)
                .filter(JargonTerm.term == row["term"])
                .first()
            )

            if existing:
                existing.category = row["category"]
                existing.difficulty = row["difficulty"]
                updated += 1
                continue

            db.add(
                JargonTerm(
                    term=row["term"],
                    category=row["category"],
                    difficulty=row["difficulty"],
                )
            )
            inserted += 1

        db.commit()
        print(f"Jargon terms inserted: {inserted}")
        print(f"Jargon terms updated: {updated}")

    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    load_jargon_terms()
