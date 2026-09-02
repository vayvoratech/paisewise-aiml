from uuid import UUID

from services import recommendation_service


def test_record_recommendation_click(monkeypatch):

    captured = {}

    def mock_get_db_connection():
        class MockCursor:

            def execute(self, query, params):
                captured["query"] = query
                captured["params"] = params

            def fetchone(self):
                return (333,)

            def close(self):
                pass

        class MockConnection:

            def cursor(self):
                return MockCursor()

            def commit(self):
                captured["committed"] = True

            def close(self):
                pass

        return MockConnection()

    monkeypatch.setattr(
        recommendation_service,
        "get_db_connection",
        mock_get_db_connection
    )

    user_id = UUID("11111111-1111-1111-1111-111111111111")
    recommendation_run_id = 222
    scheme_code = "TEST001"

    click_id = recommendation_service.record_recommendation_click(
        user_id,
        recommendation_run_id,
        scheme_code
    )

    assert click_id == 333

    assert captured["params"] == (
        str(recommendation_run_id),
        str(user_id),
        scheme_code
    )

    assert captured["committed"] is True


def test_recommendation_click_endpoint(monkeypatch):

    expected_click_id = 333

    def mock_record_click(
        user_id,
        recommendation_run_id,
        scheme_code
    ):
        assert user_id == UUID(
            "11111111-1111-1111-1111-111111111111"
        )

        assert recommendation_run_id == 222

        assert scheme_code == "TEST001"

        return expected_click_id

    monkeypatch.setattr(
        "routes.fund_recommend.record_recommendation_click",
        mock_record_click
    )

    from fastapi.testclient import TestClient
    from main import app

    client = TestClient(app)

    response = client.post(
        "/ai/recommendation-click",
        json={
            "userId": "11111111-1111-1111-1111-111111111111",
            "recommendationRunId": 222,
            "schemeCode": "TEST001"
        }
    )

    assert response.status_code == 200

    assert response.json() == {
        "clickId": expected_click_id,
        "status": "recorded"
    }