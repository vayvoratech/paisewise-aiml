from database.database import get_db_connection


def get_fallback_definition(term, language="english"):

    connection = get_db_connection()

    cursor = connection.cursor()

    query = """
        SELECT term, language, definition
        FROM jargon_terms
        WHERE LOWER(term) = LOWER(%s)
        AND language = %s
    """

    cursor.execute(
        query,
        (term, language)
    )

    result = cursor.fetchone()

    cursor.close()
    connection.close()

    if result:
        return {
            "term": result[0],
            "language": result[1],
            "explanation": result[2]
        }

    return None