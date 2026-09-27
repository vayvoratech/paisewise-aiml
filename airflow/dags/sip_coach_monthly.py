from datetime import datetime

try:
    from airflow import DAG
    from airflow.operators.python import PythonOperator
except ImportError:  # keeps the module importable in environments without Airflow
    DAG = None
    PythonOperator = None


def generate_monthly_sip_reports():
    from app.db.database import SessionLocal
    from app.db.schema import User
    from app.services.sip_coach import coach_sip
    from sqlalchemy import text
    from app.services.notification_events import publish_sip_report_event

    db = SessionLocal()
    try:
        users = db.query(User).filter(User.sip_count > 0).all()
        created = 0
        for user in users:
            # Monthly batch uses available account values as the baseline. Goal
            # and remaining months can be supplied by the product service later.
            result = coach_sip({
                "userId": str(user.user_id),
                "monthlySIP": float(user.monthly_investment or 0) / max(int(user.sip_count or 1), 1),
                "targetAmount": max(float(user.portfolio_value or 0) * 1.10, 1),
                "currentAmount": float(user.portfolio_value or 0),
                "monthsRemaining": 12,
                "expectedAnnualReturn": 10.0,
                "language": "English",
            })
            inserted = db.execute(text("""
                INSERT INTO sip_coach_reports (user_id, report_text, generated_at)
                VALUES (:user_id, :report_text, CURRENT_TIMESTAMP)
                RETURNING id
            """), {"user_id": user.user_id, "report_text": result["coachingAnalysis"]})
            report_id = inserted.scalar_one()
            publish_sip_report_event(user.user_id, report_id)
            created += 1
        db.commit()
        return created
    finally:
        db.close()


if DAG is not None:
    with DAG(
        dag_id="sip_coach_monthly",
        start_date=datetime(2026, 1, 1),
        schedule="0 2 1 * *",
        catchup=False,
        tags=["financial-ai", "sip", "phase2"],
    ) as dag:
        PythonOperator(
            task_id="generate_sip_coach_reports",
            python_callable=generate_monthly_sip_reports,
        )
