from fastapi.testclient import TestClient

from app.main import app
from app.api import fund_recommend


class FakeResult:
    def mappings(self):
        return self

    def all(self):
        return [
            {
                "scheme_name": "Fund A",
                "risk_level": "Moderate",
                "category": "Balanced",
                "returns_1y": 8,
                "returns_3y": 9,
                "returns_5y": 10,
                "expense_ratio": 0.5,
                "fund_size_cr": 1000,
            },
            {
                "scheme_name": "Fund B",
                "risk_level": "Low",
                "category": "Debt",
                "returns_1y": 6,
                "returns_3y": 7,
                "returns_5y": 8,
                "expense_ratio": 0.4,
                "fund_size_cr": 500,
            },
        ]


class FakeDB:
    def execute(self, query):
        return FakeResult()

    def close(self):
        pass


def test_fund_recommendation_api(monkeypatch):
    monkeypatch.setattr(fund_recommend, "SessionLocal", lambda: FakeDB())
    monkeypatch.setattr(
        fund_recommend,
        "generate_fund_reason",
        lambda **kwargs: "The fund matches the selected risk profile.",
    )

    client = TestClient(app)

    response = client.post(
        "/ai/fund-recommend",
        json={
            "userId": "test-user",
            "riskProfile": "Moderate",
            "investmentAmount": 100000,
            "investmentHorizon": 5,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert len(body["recommendedFunds"]) == 2
    assert "keyMetrics" in body["recommendedFunds"][0]


def test_invalid_risk_profile(monkeypatch):
    monkeypatch.setattr(fund_recommend, "SessionLocal", lambda: FakeDB())
    client = TestClient(app)

    response = client.post(
        "/ai/fund-recommend",
        json={
            "userId": "test-user",
            "riskProfile": "Unknown",
            "investmentAmount": 100000,
            "investmentHorizon": 5,
        },
    )

    assert response.status_code == 400
