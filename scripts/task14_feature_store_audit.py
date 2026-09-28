from __future__ import annotations

import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import UUID

from app.db.session import get_db


SAMPLE_SIZE = 100
SAMPLE_PERCENTAGES = (0.5, 1, 2, 4, 8, 16, 32, 64, 100)

INTEGER_FEATURES = (
    "days_since_last_active",
    "sessions_7d",
    "lessons_completed_7d",
    "chapters_completed",
    "days_since_registration",
    "paper_trades_total",
    "paper_trades_7d",
)

REQUIRED_COLUMNS = (
    "user_id",
    *INTEGER_FEATURES,
    "notification_open_rate_30d",
    "has_real_investment",
)


def _column_name(description: Any) -> str:
    """Support psycopg column descriptions across driver versions."""
    return getattr(description, "name", description[0])


def _add_issue(issues: dict[str, int], name: str) -> None:
    issues[name] = issues.get(name, 0) + 1


def _sample_feature_rows() -> tuple[list[dict[str, Any]], float]:
    """
    Read up to 100 randomly sampled feature-store rows.

    The read-only transaction and fixed sample percentages keep this
    audit separate from application behavior and limit database work.
    """
    with get_db() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SET TRANSACTION READ ONLY")

            for percentage in SAMPLE_PERCENTAGES:
                # percentage is selected only from the fixed tuple above.
                query = f"""
                    SELECT {", ".join(REQUIRED_COLUMNS)}
                    FROM public.user_features
                    TABLESAMPLE SYSTEM ({percentage})
                    LIMIT %s
                """
                cursor.execute(query, (SAMPLE_SIZE,))

                columns = [
                    _column_name(item)
                    for item in cursor.description
                ]
                rows = cursor.fetchall()

                if len(rows) >= SAMPLE_SIZE or percentage == 100:
                    return (
                        [
                            dict(zip(columns, row))
                            for row in rows[:SAMPLE_SIZE]
                        ],
                        percentage,
                    )

    return [], 100


def audit_feature_store() -> dict[str, Any]:
    rows, sampling_percentage = _sample_feature_rows()
    issues: dict[str, int] = {}
    seen_user_ids: set[str] = set()

    for row in rows:
        raw_user_id = row.get("user_id")

        if isinstance(raw_user_id, (str, UUID)):
            user_id = str(raw_user_id).strip()
        else:
            user_id = ""

        if not user_id:
            _add_issue(issues, "user_id:missing_or_invalid")
        elif user_id in seen_user_ids:
            _add_issue(issues, "user_id:duplicate")
        else:
            seen_user_ids.add(user_id)

        for field in INTEGER_FEATURES:
            value = row.get(field)

            if isinstance(value, bool) or not isinstance(value, int):
                _add_issue(issues, f"{field}:missing_or_not_integer")
            elif value < 0:
                _add_issue(issues, f"{field}:negative")

        raw_open_rate = row.get("notification_open_rate_30d")
        try:
            open_rate = float(raw_open_rate)
        except (TypeError, ValueError):
            open_rate = math.nan

        if not math.isfinite(open_rate):
            _add_issue(
                issues,
                "notification_open_rate_30d:missing_or_not_numeric",
            )
        elif not 0.0 <= open_rate <= 1.0:
            _add_issue(
                issues,
                "notification_open_rate_30d:outside_0_to_1",
            )

        if not isinstance(row.get("has_real_investment"), bool):
            _add_issue(
                issues,
                "has_real_investment:missing_or_not_boolean",
            )

    population_size = (
        len(rows)
        if sampling_percentage == 100 and len(rows) < SAMPLE_SIZE
        else None
    )

    failure_reasons: list[str] = []

    if len(rows) < SAMPLE_SIZE:
        failure_reasons.append(
            f"Only {len(rows)} row(s) were available; "
            f"{SAMPLE_SIZE} are required."
        )

    if issues:
        failure_reasons.append(
            "One or more sampled rows failed integrity checks."
        )

    return {
        "audit": "task14_user_features_integrity",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "passed" if not failure_reasons else "failed",
        "sample_size": len(rows),
        "required_sample_size": SAMPLE_SIZE,
        "population_size": population_size,
        "sampling_percentage_used": sampling_percentage,
        "issues_by_field": issues,
        "failure_reasons": failure_reasons,
        "accuracy_status": "not_measured",
        "accuracy_limit": (
            "This checks record integrity and value ranges. "
            "It does not compare feature values with source event records."
        ),
        "sampling_method": (
            "PostgreSQL TABLESAMPLE SYSTEM; random page-based sample."
        ),
        "user_identifiers_written": False,
    }


def main() -> int:
    try:
        report = audit_feature_store()
    except Exception as exc:
        print(
            "Feature-store audit could not complete "
            f"({type(exc).__name__}). Check the database connection "
            "and the public.user_features schema.",
            file=sys.stderr,
        )
        return 2

    output_dir = Path("artifacts")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / "task14_feature_store_audit.json"
    output_path.write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )

    print(json.dumps(report, indent=2))
    print(f"\nReport saved to: {output_path}")

    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())