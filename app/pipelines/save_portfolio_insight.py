from sqlalchemy import text
from app.db.database import SessionLocal


def save_portfolio_insight(user_id, insight, language, portfolio_value=None,
                           daily_change_pct=None, top_gainer_symbol=None,
                           top_loser_symbol=None, market_summary=None,
                           tokens_used=None, generation_time_ms=None,
                           generation_status="GENERATED", llm_model_used=None):
    

    db = SessionLocal()

    try:
        db.execute(text("""
            INSERT INTO public.portfolio_insights (
                user_id,
                insight,
                language
            )
            VALUES (
                :user_id,
                :insight,
                :language
            )
        """), {
            "user_id": user_id,
            "insight": insight,
            "language": (language or "en")[:30],
        })

        db.commit()

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()
