from contextlib import contextmanager

from app.db.connection import get_connection


@contextmanager
def get_db():
    connection = get_connection()

    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()