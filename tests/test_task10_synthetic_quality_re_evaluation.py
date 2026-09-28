from app.services.feedback_analysis_service import FeedbackAnalysisService
from app.services.ai_quality_evaluation_service import AIQualityEvaluationService
from app.services.feedback_dataset_service import FeedbackDatasetService
from app.services.task10_quality_baseline_service import (
    Task10QualityBaselineService,
)


FEEDBACK_DATASET_PATH = (
    "tests/data/task10_synthetic_beta_questions.json"
)

GOLDEN_SET_PATH = (
    "tests/data/task10_golden_set.json"
)


TASK10_THEMES = [
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
]


def create_services():
    feedback_analysis_service = FeedbackAnalysisService(
        GOLDEN_SET_PATH
    )

    quality_evaluation_service = AIQualityEvaluationService(
        feedback_analysis_service
    )

    feedback_dataset_service = FeedbackDatasetService(
        FEEDBACK_DATASET_PATH
    )

    baseline_service = Task10QualityBaselineService(
        feedback_analysis_service=feedback_analysis_service,
        quality_evaluation_service=quality_evaluation_service,
    )

    return (
        feedback_dataset_service,
        baseline_service,
    )


def create_baseline_response(theme):
    responses = {
        "answer_relevance": (
            "This response discusses general investing concepts."
        ),
        "topic_understanding": (
            "This explains some general financial information."
        ),
        "rag_relevance": (
            "This provides general information about the topic."
        ),
        "explanation_clarity": (
            "This gives a basic explanation of the subject."
        ),
        "response_conciseness": (
            "This provides information about the requested subject."
        ),
        "personalization": (
            "Risk tolerance is an important concept for investors."
        ),
        "conversation_continuity": (
            "This is a general response about investing."
        ),
        "insufficient_knowledge": (
            "Some information may not be known with certainty."
        ),
        "news_sentiment": (
            "The news sentiment is neutral."
        ),
        "risk_factor_explainability": (
            "Portfolio risk can be affected by diversification "
            "and market conditions."
        ),
    }

    return responses[theme]


def create_improved_response(theme):
    responses = {
        "answer_relevance": (
            "An ETF is a fund that trades on an exchange and can hold "
            "a diversified basket of investments."
        ),
        "topic_understanding": (
            "Stocks represent ownership in companies, while bonds "
            "represent lending to an issuer. They differ in risk, "
            "income characteristics, and potential returns."
        ),
        "rag_relevance": (
            "Using the provided context, the relevant information "
            "should be connected directly to the question being asked."
        ),
        "explanation_clarity": (
            "Diversification means spreading investments across "
            "different assets so that one investment has less impact "
            "on the overall portfolio."
        ),
        "response_conciseness": (
            "Compound interest means earning returns on both your "
            "original investment and previously earned interest."
        ),
        "personalization": (
            "Based on your moderate risk tolerance, risk tolerance "
            "describes how much investment uncertainty and potential "
            "loss you are comfortable accepting."
        ),
        "conversation_continuity": (
            "To compare the two investments using the earlier "
            "conversation context, we should consider the risks, "
            "characteristics, and goals discussed previously."
        ),
        "insufficient_knowledge": (
            "A future stock price cannot be known with certainty. "
            "It can be discussed using available information and "
            "scenarios, but the future outcome remains uncertain."
        ),
        "news_sentiment": (
            "The sentiment of the reported news is neutral."
        ),
        "risk_factor_explainability": (
            "Portfolio risk can be influenced by diversification, "
            "asset allocation, market volatility, concentration, "
            "and the investor's risk tolerance."
        ),
    }

    return responses[theme]


def build_responses(feedback_dataset_service):
    records = feedback_dataset_service.load_records()

    assert len(records) == 30

    baseline_responses = {}
    improved_responses = {}

    for record in records:
        baseline_responses[record.case_id] = (
            create_baseline_response(record.theme)
        )

        improved_responses[record.case_id] = (
            create_improved_response(record.theme)
        )

    return baseline_responses, improved_responses


def test_full_synthetic_quality_re_evaluation():
    (
        feedback_dataset_service,
        baseline_service,
    ) = create_services()

    baseline_responses, improved_responses = build_responses(
        feedback_dataset_service
    )

    report = baseline_service.evaluate(
        baseline_responses=baseline_responses,
        improved_responses=improved_responses,
        themes=TASK10_THEMES,
        available_context={
            "risk_tolerance": "moderate",
        },
    )

    assert report.total_cases == 10

    assert report.baseline_passed >= 0
    assert report.improved_passed >= 0

    assert report.improved_score >= report.baseline_score

    assert report.score_change >= 0


def test_synthetic_re_evaluation_reports_improved_themes():
    (
        feedback_dataset_service,
        baseline_service,
    ) = create_services()

    baseline_responses, improved_responses = build_responses(
        feedback_dataset_service
    )

    report = baseline_service.evaluate(
        baseline_responses=baseline_responses,
        improved_responses=improved_responses,
        themes=TASK10_THEMES,
        available_context={
            "risk_tolerance": "moderate",
        },
    )

    assert isinstance(report.improved_themes, list)
    assert isinstance(report.regressed_themes, list)
    assert isinstance(report.unchanged_themes, list)


def test_synthetic_re_evaluation_report_is_serializable():
    (
        feedback_dataset_service,
        baseline_service,
    ) = create_services()

    baseline_responses, improved_responses = build_responses(
        feedback_dataset_service
    )

    report = baseline_service.create_report(
        baseline_responses=baseline_responses,
        improved_responses=improved_responses,
        themes=TASK10_THEMES,
        available_context={
            "risk_tolerance": "moderate",
        },
    )

    assert isinstance(report, dict)

    assert "total_cases" in report
    assert "baseline" in report
    assert "improved" in report

    assert "passed_cases" in report["baseline"]
    assert "score_percentage" in report["baseline"]

    assert "passed_cases" in report["improved"]
    assert "score_percentage" in report["improved"]

    assert "score_change" in report
    assert "improved_themes" in report
    assert "regressed_themes" in report
    assert "unchanged_themes" in report