from fastapi.testclient import TestClient

from main import app
from app.services.jargon_service import llm_client

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
        "Trading",
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


def test_jargon_endpoint_kannada(monkeypatch):
    monkeypatch.setattr(
        "app.services.jargon_service.cache.get",
        lambda key: None
    )

    captured_prompts = []

    def mock_generate_response(prompt):
        captured_prompts.append(prompt)
        return "ಕನ್ನಡದಲ್ಲಿ ಹಣಕಾಸಿನ ವಿವರಣೆ."

    monkeypatch.setattr(
        llm_client,
        "generate_response",
        mock_generate_response
    )

    response = client.post(
        "/ai/jargon",
        json={
            "term": "Mutual Fund",
            "language": "Kannada",
            "userId": "test-kannada-user"
        }
    )

    assert response.status_code == 200
    assert response.json()["language"] == "kn"
    assert response.json()["explanation"] == "ಕನ್ನಡದಲ್ಲಿ ಹಣಕಾಸಿನ ವಿವರಣೆ."
    assert "Respond completely in Kannada" in captured_prompts[0]


def test_jargon_endpoint_telugu(monkeypatch):
    monkeypatch.setattr(
        "app.services.jargon_service.cache.get",
        lambda key: None
    )

    captured_prompts = []

    def mock_generate_response(prompt):
        captured_prompts.append(prompt)
        return "తెలుగులో ఆర్థిక వివరణ."

    monkeypatch.setattr(
        llm_client,
        "generate_response",
        mock_generate_response
    )

    response = client.post(
        "/ai/jargon",
        json={
            "term": "Mutual Fund",
            "language": "Telugu",
            "userId": "test-telugu-user"
        }
    )

    assert response.status_code == 200
    assert response.json()["language"] == "te"
    assert response.json()["explanation"] == "తెలుగులో ఆర్థిక వివరణ."
    assert "Respond completely in Telugu" in captured_prompts[0]


def test_jargon_endpoint_tamil(monkeypatch):
    monkeypatch.setattr(
        "app.services.jargon_service.cache.get",
        lambda key: None
    )

    captured_prompts = []

    def mock_generate_response(prompt):
        captured_prompts.append(prompt)
        return "தமிழில் நிதி விளக்கம்."

    monkeypatch.setattr(
        llm_client,
        "generate_response",
        mock_generate_response
    )

    response = client.post(
        "/ai/jargon",
        json={
            "term": "Mutual Fund",
            "language": "Tamil",
            "userId": "test-tamil-user"
        }
    )

    assert response.status_code == 200
    assert response.json()["language"] == "ta"
    assert response.json()["explanation"] == "தமிழில் நிதி விளக்கம்."
    assert "Respond completely in Tamil" in captured_prompts[0]
