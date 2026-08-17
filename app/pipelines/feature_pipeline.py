from collections import defaultdict
from datetime import datetime, timedelta

from app.db.database import SessionLocal
from app.db.schema import (
    User,
    UserFeatures,
    UserSession,
    LessonProgress,
    QuizAttempt,
    PaperTrade,
)
from app.pipelines.validate_features import validate_feature_ranges


LOOKBACK_DAYS = 90


def _lesson_completion_rate(lessons):
    if not lessons:
        return 0.0
    completed = sum(1 for row in lessons if row.completed)
    return round(completed / len(lessons), 4)


def _quiz_average(quizzes):
    if not quizzes:
        return 0.0
    return round(sum(row.score for row in quizzes) / len(quizzes), 2)


def _trade_profit_rate(trades):
    if not trades:
        return 0.0
    profitable = sum(
        1 for row in trades
        if row.profit_percent is not None and row.profit_percent > 0
    )
    return round(profitable / len(trades), 4)


def _calculate_streak_days(lessons, quizzes, trades, sessions):
    dates = set()

    for rows, field in (
        (lessons, "completed_at"),
        (quizzes, "attempted_at"),
        (trades, "created_at"),
        (sessions, "login_time"),
    ):
        for row in rows:
            value = getattr(row, field)
            if value:
                dates.add(value.date())

    if not dates:
        return 0

    dates = sorted(dates, reverse=True)
    streak = 1

    for index in range(1, len(dates)):
        if dates[index - 1] - dates[index] == timedelta(days=1):
            streak += 1
        else:
            break

    return streak


def _session_features(sessions):
    if not sessions:
        return {
            "time_of_day": None,
            "session_duration": 0,
            "screens_visited": 0,
            "lessons_started": 0,
            "quizzes_taken": 0,
        }

    total_duration = sum(row.session_duration or 0 for row in sessions)
    total_screens = sum(row.screens_visited or 0 for row in sessions)
    total_lessons = sum(row.lessons_started or 0 for row in sessions)
    total_quizzes = sum(row.quizzes_taken or 0 for row in sessions)

    latest = max(sessions, key=lambda row: row.login_time)
    hour = latest.login_time.hour

    if hour < 6:
        time_of_day = "night"
    elif hour < 12:
        time_of_day = "morning"
    elif hour < 18:
        time_of_day = "afternoon"
    else:
        time_of_day = "evening"

    return {
        "time_of_day": time_of_day,
        "session_duration": total_duration,
        "screens_visited": total_screens,
        "lessons_started": total_lessons,
        "quizzes_taken": total_quizzes,
    }


def run_behaviour_feature_pipeline():
    db = SessionLocal()

    try:
        start_date = datetime.utcnow() - timedelta(days=LOOKBACK_DAYS)

        users = db.query(User).all()
        sessions = db.query(UserSession).filter(UserSession.login_time >= start_date).all()
        lessons = db.query(LessonProgress).filter(LessonProgress.completed_at >= start_date).all()
        quizzes = db.query(QuizAttempt).filter(QuizAttempt.attempted_at >= start_date).all()
        trades = db.query(PaperTrade).filter(PaperTrade.created_at >= start_date).all()

        grouped = {
            "sessions": defaultdict(list),
            "lessons": defaultdict(list),
            "quizzes": defaultdict(list),
            "trades": defaultdict(list),
        }

        for row in sessions:
            grouped["sessions"][row.user_id].append(row)
        for row in lessons:
            grouped["lessons"][row.user_id].append(row)
        for row in quizzes:
            grouped["quizzes"][row.user_id].append(row)
        for row in trades:
            grouped["trades"][row.user_id].append(row)

        updated_users = 0

        for user in users:
            user_sessions = grouped["sessions"][user.user_id]
            user_lessons = grouped["lessons"][user.user_id]
            user_quizzes = grouped["quizzes"][user.user_id]
            user_trades = grouped["trades"][user.user_id]

            session_features = _session_features(user_sessions)

            existing = db.query(UserFeatures).filter(
                UserFeatures.user_id == user.user_id
            ).first()

            selected_language = (
                existing.preferred_language
                if existing and existing.preferred_language
                else "hi"
            )
            selected_goal = (
                existing.onboarding_goal
                if existing and existing.onboarding_goal
                else None
            )

            features = {
                "lesson_completion_rate": _lesson_completion_rate(user_lessons),
                "quiz_avg_score": _quiz_average(user_quizzes),
                "streak_days": _calculate_streak_days(
                    user_lessons,
                    user_quizzes,
                    user_trades,
                    user_sessions,
                ),
                "total_xp": (
                    len([row for row in user_lessons if row.completed]) * 100
                    + len(user_quizzes) * 50
                ),
                "preferred_language": selected_language,
                "onboarding_goal": selected_goal,
                "age_proxy": user.age,
                "city_tier": None,
                "paper_trade_count": len(user_trades),
                "paper_trade_profit_rate": _trade_profit_rate(user_trades),
                **session_features,
            }

            errors = validate_feature_ranges(features)
            if errors:
                raise ValueError(
                    f"Invalid features for user {user.user_id}: {', '.join(errors)}"
                )

            if existing is None:
                existing = UserFeatures(
                    user_id=user.user_id,
                    age=user.age,
                    annual_income=user.annual_income,
                    monthly_investment=user.monthly_investment,
                    portfolio_value=user.portfolio_value,
                    risk_profile=user.risk_profile,
                    investment_experience_years=user.investment_experience_years,
                    sip_count=user.sip_count,
                    kyc_completed=user.kyc_completed,
                )
                db.add(existing)

            for name, value in features.items():
                setattr(existing, name, value)

            updated_users += 1

        db.commit()
        print(f"Behaviour feature pipeline completed. Users updated: {updated_users}")
        return updated_users

    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run_behaviour_feature_pipeline()
