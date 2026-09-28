from app.services.ai_quality_evaluation_service import (
    AIQualityEvaluationService,
)
from app.services.feedback_analysis_service import (
    FeedbackAnalysisService,
)
from app.services.task10_quality_baseline_service import (
    Task10QualityBaselineService,
)


GOLDEN_SET_PATH = "tests/data/task10_golden_set.json"


def create_service():
    feedback_service = FeedbackAnalysisService(
        GOLDEN_SET_PATH
    )

    quality_service = AIQualityEvaluationService(
        feedback_analysis_service=feedback_service
    )

    return Task10QualityBaselineService(
        feedback_analysis_service=feedback_service,
        quality_evaluation_service=quality_service,
    )


def test_baseline_comparison_detects_quality_improvement():
    service = create_service()

    baseline_responses = {
        "TC001": "ETF fund.",
        "TC002": "stock bond.",
        "TC003": "diversification.",
    }

    improved_responses = {
        "TC001": (
            "An ETF is an exchange-traded fund "
            "that trades on a stock exchange."
        ),
        "TC002": (
            "A stock represents ownership in a company, "
            "while a bond represents a loan to an issuer."
        ),
        "TC003": (
            "Diversification means spreading investments "
            "across different assets to reduce reliance "
            "on one investment."
        ),
    }

    report = service.evaluate(
        baseline_responses=baseline_responses,
        improved_responses=improved_responses,
        themes=[
            "answer_relevance",
            "topic_understanding",
            "rag_relevance",
        ],
    )

    assert report.total_cases == 3
    assert report.baseline_passed == 0
    assert report.improved_passed == 3

    assert report.baseline_score == 0.0
    assert report.improved_score == 100.0
    assert report.score_change == 100.0

    assert len(report.improved_themes) == 3
    assert report.regressed_themes == []


def test_baseline_comparison_detects_regression():
    service = create_service()

    baseline_responses = {
        "TC001": (
            "An ETF is an exchange-traded fund "
            "that trades on a stock exchange."
        ),
    }

    improved_responses = {
        "TC001": "ETF fund.",
    }

    report = service.evaluate(
        baseline_responses=baseline_responses,
        improved_responses=improved_responses,
        themes=["answer_relevance"],
    )

    assert report.total_cases == 1
    assert report.baseline_passed == 1
    assert report.improved_passed == 0

    assert report.baseline_score == 100.0
    assert report.improved_score == 0.0
    assert report.score_change == -100.0

    assert report.improved_themes == []
    assert report.regressed_themes == ["answer_relevance"]


def test_baseline_comparison_detects_unchanged_quality():
    service = create_service()

    responses = {
        "TC001": (
            "An ETF is an exchange-traded fund "
            "that trades on a stock exchange."
        ),
    }

    report = service.evaluate(
        baseline_responses=responses,
        improved_responses=responses,
        themes=["answer_relevance"],
    )

    assert report.total_cases == 1
    assert report.baseline_passed == 1
    assert report.improved_passed == 1

    assert report.baseline_score == 100.0
    assert report.improved_score == 100.0
    assert report.score_change == 0.0

    assert report.improved_themes == []
    assert report.regressed_themes == []
    assert report.unchanged_themes == [
        "answer_relevance"
    ]


def test_baseline_comparison_supports_all_task10_cases():
    service = create_service()

    baseline_responses = {
        "TC001": "ETF fund.",
        "TC002": "Stocks and bonds are different.",
        "TC003": "Diversification is investing in different things.",
        "TC004": "Compound interest is interest on interest.",
        "TC005": "A mutual fund is an investment fund.",
        "TC006": "Your risk depends on your investments.",
        "TC007": "The second investment is better.",
        "TC008": "The stock price may increase.",
        "TC009": "The sentiment is positive.",
        "TC010": "Portfolio health depends on several factors.",
    }

    improved_responses = {
        "TC001": (
            "An ETF is an exchange-traded fund that holds a collection "
            "of assets such as stocks or bonds and trades on a stock exchange."
        ),
        "TC002": (
            "A stock represents ownership in a company, while a bond "
            "represents debt issued by a company or government."
        ),
        "TC003": (
            "Diversification means spreading investments across different "
            "assets, sectors, or regions to reduce reliance on one investment."
        ),
        "TC004": (
            "Compound interest means earning interest on the original "
            "principal and previously accumulated interest."
        ),
        "TC005": (
            "A mutual fund pools money from multiple investors and invests "
            "it in assets such as stocks or bonds."
        ),
        "TC006": (
            "Risk tolerance describes how much investment loss or volatility "
            "an investor can financially and emotionally handle. It can be "
            "considered alongside investment goals, time horizon, and "
            "financial circumstances."
        ),
        "TC007": (
            "To compare the two investments using the earlier conversation "
            "context, we should consider the characteristics, risks, and "
            "goals discussed previously rather than treating the new "
            "question as completely unrelated."
        ),
        "TC008": (
            "A future stock price cannot be known with certainty. Its price "
            "may rise or fall depending on company and market conditions."
        ),
        "TC009": (
            "The sentiment is positive because the provided text expresses "
            "favorable views about the subject."
        ),
        "TC010": (
            "Portfolio health can be assessed using diversification, "
            "risk exposure, asset allocation, investment goals, and "
            "time horizon."
        ),
    }

    available_context = {
        "risk_tolerance": "moderate",
    }

    report = service.evaluate(
        baseline_responses=baseline_responses,
        improved_responses=improved_responses,
        themes=[
            "answer_relevance",
            "topic_understanding",
            "rag_relevance",
            "explanation_clarity",
            "response_conciseness",
            "personalization",
            "conversation_continuity",
            "insufficient_knowledge",
            "news_sentiment",
            "risk_factor_explainability",
        ],
        available_context=available_context,
    )

    assert report.total_cases == 10

    assert 0 <= report.baseline_passed <= 10
    assert 0 <= report.improved_passed <= 10

    assert 0.0 <= report.baseline_score <= 100.0
    assert 0.0 <= report.improved_score <= 100.0

    assert len(report.results) == 10

    case_ids = {
        result.case_id
        for result in report.results
    }

    assert case_ids == {
        "TC001",
        "TC002",
        "TC003",
        "TC004",
        "TC005",
        "TC006",
        "TC007",
        "TC008",
        "TC009",
        "TC010",
    }


def test_create_report_returns_serializable_structure():
    service = create_service()

    baseline_responses = {
        "TC001": "ETF fund.",
    }

    improved_responses = {
        "TC001": (
            "An ETF is an exchange-traded fund "
            "that trades on a stock exchange."
        ),
    }

    report = service.create_report(
        baseline_responses=baseline_responses,
        improved_responses=improved_responses,
        themes=["answer_relevance"],
    )

    assert isinstance(report, dict)

    assert report["total_cases"] == 1

    assert "baseline" in report
    assert "improved" in report
    assert "score_change" in report

    assert report["baseline"]["passed_cases"] == 0
    assert report["improved"]["passed_cases"] == 1

    assert report["baseline"]["score_percentage"] == 0.0
    assert report["improved"]["score_percentage"] == 100.0

    assert isinstance(report["results"], list)
    assert len(report["results"]) == 1

    result = report["results"][0]

    assert result["case_id"] == "TC001"
    assert result["theme"] == "answer_relevance"
    assert result["baseline_passed"] is False
    assert result["improved_passed"] is True