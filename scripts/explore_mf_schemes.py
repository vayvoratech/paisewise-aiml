from collections import Counter
from statistics import mean

from sqlalchemy import text

from app.db.database import SessionLocal


def explore_funds():
    db = SessionLocal()

    try:
        rows = db.execute(
            text("""
                SELECT
                    category,
                    risk_level,
                    returns_1y,
                    returns_3y,
                    returns_5y,
                    expense_ratio
                FROM mf_schemes
                WHERE is_active = TRUE
            """)
        ).mappings().all()

        if not rows:
            print("No active mutual fund schemes found.")
            return

        categories = Counter(row["category"] for row in rows)
        print("Fund categories:")
        for category, count in categories.most_common():
            print(f"- {category}: {count}")

        for field in ("returns_1y", "returns_3y", "returns_5y", "expense_ratio"):
            values = [float(row[field]) for row in rows if row[field] is not None]
            if values:
                print(
                    f"{field}: min={min(values):.2f}, "
                    f"max={max(values):.2f}, average={mean(values):.2f}"
                )

    finally:
        db.close()


if __name__ == "__main__":
    explore_funds()
