from sqlalchemy import text

from app.db.database import SessionLocal


def save_portfolio_insight(

    user_id,

    insight,

    language,

):

    db = SessionLocal()

    try:

        query = text("""

            INSERT INTO portfolio_insights

            (

                user_id,

                insight,

                language

            )

            VALUES

            (

                :user_id,

                :insight,

                :language

            )

        """)

        db.execute(

            query,

            {

                "user_id": user_id,

                "insight": insight,

                "language": language,

            },

        )

        db.commit()

        print("Insight saved successfully.")

    except Exception as e:

        db.rollback()

        print(e)

    finally:

        db.close()