from fastapi.testclient import TestClient

from main import app
from services.jargon_service import llm_client


client = TestClient(app)


def test_jargon_endpoint_20_terms(monkeypatch):

    def mock_generate_response(prompt):
        return "This is a test financial explanation."

    monkeypatch.setattr(
        llm_client,
        "generate_response",
        mock_generate_response
    )

    terms = [
        "Mutual Fund",
        "Stock Market",
        "SIP",
        "IPO",
        "Inflation",
        "Insurance",
        "Bitcoin",
        "Credit Score",
        "Loan",
        "Interest Rate",
        "Bond",
        "Equity",
        "Dividend",
        "Portfolio",
        "Asset",
        "Liability",
        "Tax",
        "Savings",
        "Investment",
        "Trading"
    ]

    for index, term in enumerate(terms):

        response = client.post(
            "/ai/jargon",
            json={
                "term": term,
                "language": "english",
                "userId": f"test-user-{index}"
            }
        )

        assert response.status_code == 200
        assert response.json()["term"] == term
        assert response.json()["language"] == "en"
        assert "explanation" in response.json()
