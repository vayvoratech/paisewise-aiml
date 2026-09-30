
import json

import pytest

from app.services.ai_quality_evaluation_service import (
    AIQualityEvaluationService,
)
from app.services.feedback_analysis_service import (
    FeedbackAnalysisService,
)
from tests.test_chat_service import create_chat_service
from app.schemas.chat import ChatRequest


@pytest.mark.anyio
async def test_chat_response_can_be_quality_evaluated(tmp_path):
    dataset = {
        "dataset_name": "chat_quality_test",
        "version": "1.0",
        "cases": [
            {
                "id": "CHAT001",
                "theme": "answer_relevance",
                "question": "What is an ETF?",
                "expected_behavior": "Explain what an ETF is.",
                "required_terms": ["ETF", "fund"],
                "forbidden_terms": [],
            }
        ],
    }

    dataset_path = tmp_path / "dataset.json"

    with dataset_path.open("w", encoding="utf-8") as file:
        json.dump(dataset, file)

    analysis_service = FeedbackAnalysisService(
        dataset_path
    )

    evaluation_service = AIQualityEvaluationService(
        analysis_service
    )

    chat_service, _, _, _, _ = create_chat_service(
        llm_response="An ETF is an exchange-traded fund."
    )

    request = ChatRequest(
        userId="quality_test_user",
        sessionId="quality_test_session",
        message="What is an ETF?",
    )

    response = await chat_service.process_chat(request)

    report = evaluation_service.create_report(
        {
            "CHAT001": response.message,
        }
    )

    assert response.status == "success"

    assert report["total_cases"] == 1
    assert report["passed_cases"] == 1
    assert report["failed_cases"] == 0
    assert report["score_percentage"] == 100.0
