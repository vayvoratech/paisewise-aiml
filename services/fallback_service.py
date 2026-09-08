from database.database import get_db_connection


def get_fallback_definition(term, language="en"):

    

    connection = get_db_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT term, category, difficulty
            FROM jargon_terms
            WHERE LOWER(term) = LOWER(%s)
            LIMIT 1
            """,
            (term,),
        )

        result = cursor.fetchone()
        cursor.close()

    finally:
        connection.close()

    if result:
        canonical_term, category, difficulty = result

        explanation = (
            f"{canonical_term} is a financial term in the "
            f"{category} category. Its difficulty level is {difficulty}."
        )

        return {
            "term": canonical_term,
            "language": language,
            "explanation": explanation,
        }

    return {
        "term": term,
        "language": language,
        "explanation": (
            f"{term} is a financial term. "
            "A detailed explanation is currently unavailable."
        ),
    }
