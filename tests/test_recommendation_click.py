from fastapi.testclient import TestClient

from main import app


def test_recommendation_click_endpoint(monkeypatch):
    expected_click_id = 333

    def mock_record_click(
        user_id,
        recommendation_run_id,
        scheme_code
    ):
        assert user_id == "11111111-1111-1111-1111-111111111111"
        assert recommendation_run_id == 222
        assert scheme_code == "TEST001"

        return expected_click_id

    monkeypatch.setattr(
        "app.api.fund_recommend.record_recommendation_click",
        mock_record_click
    )

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
