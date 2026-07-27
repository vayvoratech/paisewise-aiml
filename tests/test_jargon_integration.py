from fastapi.testclient import TestClient
from main import app


client = TestClient(app)


def test_jargon_endpoint_20_terms():

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


    for term in terms:

        response = client.post(
            "/ai/jargon",
            json={
                "term": term,
                "language": "english"
            }
        )


        assert response.status_code == 200
        assert response.json()["term"] == term