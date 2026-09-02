
from datetime import datetime
from pathlib import Path

from database.database import get_db_connection


FRESHNESS_THRESHOLD_HOURS = 24
REPORTS_DIR = Path("reports")


def run_data_quality_checks():
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
       
        # 1. Total records

        cursor.execute("""
            SELECT COUNT(*)
            FROM public.user_features
        """)
        total_records = cursor.fetchone()[0]

        # 2. Null checks
    
        cursor.execute("""
            SELECT
                COUNT(*) FILTER (WHERE user_id IS NULL),
                COUNT(*) FILTER (WHERE quiz_attempts_total IS NULL),
                COUNT(*) FILTER (WHERE quiz_pass_rate IS NULL),
                COUNT(*) FILTER (WHERE avg_quiz_score IS NULL),
                COUNT(*) FILTER (WHERE computed_at IS NULL)
            FROM public.user_features
        """)

        (
            null_user_id,
            null_quiz_attempts,
            null_pass_rate,
            null_avg_score,
            null_computed_at,
        ) = cursor.fetchone()

    
        # 3. Range checks
        
        cursor.execute("""
            SELECT COUNT(*)
            FROM public.user_features
            WHERE quiz_attempts_total < 0
        """)
        invalid_quiz_attempts = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*)
            FROM public.user_features
            WHERE quiz_pass_rate < 0
               OR quiz_pass_rate > 1
        """)
        invalid_pass_rate = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*)
            FROM public.user_features
            WHERE avg_quiz_score < 0
               OR avg_quiz_score > 1
        """)
        invalid_avg_score = cursor.fetchone()[0]

        # 4. Freshness checks
        
        cursor.execute("""
            SELECT
                COUNT(*) FILTER (
                    WHERE computed_at IS NULL
                       OR computed_at < NOW() - INTERVAL '24 hours'
                ),
                COUNT(*) FILTER (
                    WHERE computed_at IS NULL
                ),
                COALESCE(
                    MAX(
                        EXTRACT(
                            EPOCH FROM (NOW() - computed_at)
                        ) / 3600
                    ) FILTER (
                        WHERE computed_at IS NOT NULL
                    ),
                    0
                )
            FROM public.user_features
        """)

        (
            stale_records,
            missing_timestamps,
            oldest_age_hours,
        ) = cursor.fetchone()

        
        # 5. Overall status
        
        has_issues = (
            null_user_id > 0
            or null_quiz_attempts > 0
            or null_pass_rate > 0
            or null_avg_score > 0
            or null_computed_at > 0
            or invalid_quiz_attempts > 0
            or invalid_pass_rate > 0
            or invalid_avg_score > 0
            or stale_records > 0
        )

        status = "FAIL" if has_issues else "PASS"

        
        # 6. Return structured results

        return {
            "total_records": total_records,

            "nulls": {
                "user_id": null_user_id,
                "quiz_attempts_total": null_quiz_attempts,
                "quiz_pass_rate": null_pass_rate,
                "avg_quiz_score": null_avg_score,
                "computed_at": null_computed_at,
            },

            "invalid_values": {
                "quiz_attempts_total": invalid_quiz_attempts,
                "quiz_pass_rate": invalid_pass_rate,
                "avg_quiz_score": invalid_avg_score,
            },

            "freshness": {
                "stale_records": stale_records,
                "missing_timestamps": missing_timestamps,
                "oldest_age_hours": float(oldest_age_hours),
                "threshold_hours": FRESHNESS_THRESHOLD_HOURS,
            },

            "status": status,
        }

    finally:
        cursor.close()
        connection.close()


def format_report(results):
    report_date = datetime.now().strftime("%Y-%m-%d")

    nulls = results["nulls"]
    invalid = results["invalid_values"]
    freshness = results["freshness"]

    report = f"""
========== FEATURE STORE DATA QUALITY REPORT ==========

Report date: {report_date}
Overall status: {results["status"]}

--- RECORD COUNT ---
Total records: {results["total_records"]}

--- COMPLETENESS / NULL CHECKS ---
user_id: {nulls["user_id"]} nulls
quiz_attempts_total: {nulls["quiz_attempts_total"]} nulls
quiz_pass_rate: {nulls["quiz_pass_rate"]} nulls
avg_quiz_score: {nulls["avg_quiz_score"]} nulls
computed_at: {nulls["computed_at"]} nulls

--- VALIDITY / RANGE CHECKS ---
Invalid quiz_attempts_total: {invalid["quiz_attempts_total"]}
Invalid quiz_pass_rate: {invalid["quiz_pass_rate"]}
Invalid avg_quiz_score: {invalid["avg_quiz_score"]}

--- FRESHNESS CHECK ---
Stale records: {freshness["stale_records"]}
Missing timestamps: {freshness["missing_timestamps"]}
Oldest record age: {freshness["oldest_age_hours"]:.2f} hours
Freshness threshold: {freshness["threshold_hours"]} hours

--- RESULT ---
STATUS: {results["status"]}

========================================================
"""

    return report.strip()


def save_report(report):
    REPORTS_DIR.mkdir(exist_ok=True)

    report_date = datetime.now().strftime("%Y-%m-%d")
    report_path = REPORTS_DIR / f"feature_quality_{report_date}.txt"

    report_path.write_text(report, encoding="utf-8")

    return report_path


def main():
    results = run_data_quality_checks()

    report = format_report(results)

    print(report)

    report_path = save_report(report)

    print(f"\nReport saved to: {report_path}")


if __name__ == "__main__":
    main()

