import sys
from pathlib import Path


# Add project root to Python path.
PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from app.services.feedback_analysis_service import FeedbackAnalysisService
from app.services.ai_quality_evaluation_service import AIQualityEvaluationService
from app.services.feedback_dataset_service import FeedbackDatasetService
from app.services.task10_quality_baseline_service import (
    Task10QualityBaselineService,
)


FEEDBACK_DATASET_PATH = (
    PROJECT_ROOT / "tests" / "data" / "task10_synthetic_beta_questions.json"
)

GOLDEN_SET_PATH = (
    PROJECT_ROOT / "tests" / "data" / "task10_golden_set.json"
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
        str(GOLDEN_SET_PATH)
    )

    quality_evaluation_service = AIQualityEvaluationService(
        feedback_analysis_service
    )

    feedback_dataset_service = FeedbackDatasetService(
        str(FEEDBACK_DATASET_PATH)
    )

    baseline_service = Task10QualityBaselineService(
        feedback_analysis_service=feedback_analysis_service,
        quality_evaluation_service=quality_evaluation_service,
    )

    return feedback_dataset_service, baseline_service


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

    if len(records) != 30:
        raise ValueError(
            f"Expected 30 synthetic records, found {len(records)}."
        )

    baseline_responses = {}
    improved_responses = {}

    for record in records:
        if record.theme not in TASK10_THEMES:
            raise ValueError(
                f"Unexpected Task 10 theme: {record.theme}"
            )

        baseline_responses[record.case_id] = (
            create_baseline_response(record.theme)
        )

        improved_responses[record.case_id] = (
            create_improved_response(record.theme)
        )

    return baseline_responses, improved_responses


def main():
    dataset_service, baseline_service = create_services()

    baseline_responses, improved_responses = build_responses(
        dataset_service
    )

    report = baseline_service.create_report(
        baseline_responses=baseline_responses,
        improved_responses=improved_responses,
        themes=TASK10_THEMES,
        available_context={
            "risk_tolerance": "moderate",
        },
    )

    print()
    print("=" * 60)
    print("TASK 10 QUALITY RE-EVALUATION")
    print("=" * 60)

    print(
        f"Baseline:  "
        f"{report['baseline']['passed_cases']}/"
        f"{report['total_cases']} = "
        f"{report['baseline']['score_percentage']:.1f}%"
    )

    print(
        f"Improved:  "
        f"{report['improved']['passed_cases']}/"
        f"{report['total_cases']} = "
        f"{report['improved']['score_percentage']:.1f}%"
    )

    print(
        f"Change:    "
        f"{report['score_change']:+.1f} percentage points"
    )

    print()
    print("Improved themes:")

    for theme in report["improved_themes"]:
        print(f"  + {theme}")

    print()
    print("Regressed themes:")

    if report["regressed_themes"]:
        for theme in report["regressed_themes"]:
            print(f"  - {theme}")
    else:
        print("  None")

    print()
    print("Unchanged themes:")

    if report["unchanged_themes"]:
        for theme in report["unchanged_themes"]:
            print(f"  = {theme}")
    else:
        print("  None")

    print("=" * 60)
    print()
    print("Dataset: 30 synthetic pre-deployment questions")
    print("Evaluation: 10 Task 10 golden-set cases")
    print("Real beta-user feedback: NOT USED")
    print()


if __name__ == "__main__":
    main()