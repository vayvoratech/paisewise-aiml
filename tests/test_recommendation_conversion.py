from uuid import UUID

from services import recommendation_service


def test_recommendation_conversion_true(monkeypatch):

    def mock_get_db_connection():

        class MockCursor:

            def execute(self, query, params):
                self.params = params

            def fetchone(self):
                return (True,)

            def close(self):
                pass

        class MockConnection:

            def cursor(self):
                return MockCursor()

            def close(self):
                pass

        return MockConnection()

    monkeypatch.setattr(
        recommendation_service,
        "get_db_connection",
        mock_get_db_connection
    )

    result = recommendation_service.has_recommendation_converted(
        UUID("11111111-1111-1111-1111-111111111111"),
        UUID("22222222-2222-2222-2222-222222222222"),
        "TEST001"
    )

    assert result is True


def test_recommendation_conversion_false(monkeypatch):

    def mock_get_db_connection():

        class MockCursor:

            def execute(self, query, params):
                self.params = params

            def fetchone(self):
                return (False,)

            def close(self):
                pass

        class MockConnection:

            def cursor(self):
                return MockCursor()

            def close(self):
                pass

        return MockConnection()

    monkeypatch.setattr(
        recommendation_service,
        "get_db_connection",
        mock_get_db_connection
    )

    result = recommendation_service.has_recommendation_converted(
        UUID("11111111-1111-1111-1111-111111111111"),
        UUID("22222222-2222-2222-2222-222222222222"),
        "TEST001"
    )

    assert result is False