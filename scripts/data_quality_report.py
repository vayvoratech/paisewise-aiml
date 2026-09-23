"""Daily quality checks for the current user_features schema."""
from datetime import datetime
from pathlib import Path
from database.database import get_db_connection

REPORTS_DIR = Path("reports")


def run_data_quality_checks():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM public.user_features")
            total = cursor.fetchone()[0]
            cursor.execute("""
                SELECT
                    COUNT(*) FILTER (WHERE user_id IS NULL),
                    COUNT(*) FILTER (WHERE quiz_avg_score IS NULL),
                    COUNT(*) FILTER (WHERE lesson_completion_rate IS NULL),
                    COUNT(*) FILTER (WHERE updated_at IS NULL),
                    COUNT(*) FILTER (WHERE quiz_avg_score < 0 OR quiz_avg_score > 100),
                    COUNT(*) FILTER (WHERE lesson_completion_rate < 0 OR lesson_completion_rate > 1),
                    COUNT(*) FILTER (WHERE feature_version IS NULL)
                FROM public.user_features
            """)
            null_user, null_quiz, null_completion, null_updated, invalid_quiz, invalid_completion, null_version = cursor.fetchone()
            cursor.execute("""
                SELECT COUNT(*) FROM public.user_features
                WHERE updated_at IS NULL OR updated_at < NOW() - INTERVAL '24 hours'
            """)
            stale = cursor.fetchone()[0]
        status = "PASS" if not any([null_user, null_quiz, null_completion, null_updated, invalid_quiz, invalid_completion, null_version]) else "FAIL"
        return {
            "total_records": total,
            "nulls": {"user_id": null_user, "quiz_avg_score": null_quiz, "lesson_completion_rate": null_completion, "updated_at": null_updated, "feature_version": null_version},
            "invalid_values": {"quiz_avg_score": invalid_quiz, "lesson_completion_rate": invalid_completion},
            "stale_records": stale,
            "status": status,
        }
    finally:
        connection.close()


def format_report(results):
    return f"""FEATURE STORE DATA QUALITY REPORT\nReport date: {datetime.now():%Y-%m-%d}\nOverall status: {results['status']}\nTotal records: {results['total_records']}\nNulls: {results['nulls']}\nInvalid values: {results['invalid_values']}\nStale records (>24h): {results['stale_records']}\n""".strip()


def save_report(report):
    REPORTS_DIR.mkdir(exist_ok=True)
    path = REPORTS_DIR / f"feature_quality_{datetime.now():%Y-%m-%d}.txt"
    path.write_text(report, encoding="utf-8")
    return path


def main():
    results = run_data_quality_checks()
    report = format_report(results)
    print(report)
    print(f"Report saved to: {save_report(report)}")


if __name__ == "__main__":
    main()
