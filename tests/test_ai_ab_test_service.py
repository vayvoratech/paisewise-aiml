from types import SimpleNamespace

from app.services.ai_ab_test_service import AIABTestService
from app.services.ai_quality_evaluation_service import (
    AIQualityEvaluationService,
)
from app.services.feedback_analysis_service import (
    FeedbackAnalysisService,
)
from app.services.feedback_dataset_service import (
    FeedbackDatasetService,
)


def test_ab_test_compares_top_three_improvements():
    feedback_service = FeedbackAnalysisService(
        "tests/data/task10_golden_set.json"
    )

    quality_service = AIQualityEvaluationService(
        feedback_analysis_service=feedback_service
    )

    ab_service = AIABTestService(
        feedback_analysis_service=feedback_service,
        quality_evaluation_service=quality_service,
    )

    variant_a = {
        "TC001": "ETF fund.",
        "TC002": "stock bond.",
        "TC003": "diversification.",
    }

    variant_b = {
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

    report = ab_service.evaluate(
        variant_a=variant_a,
        variant_b=variant_b,
        themes=[
            "answer_relevance",
            "topic_understanding",
            "rag_relevance",
        ],
    )

    assert report.total_cases == 3
    assert report.variant_a_passed == 0
    assert report.variant_b_passed == 3
    assert report.variant_a_score == 0.0
    assert report.variant_b_score == 100.0


def test_ab_test_creates_serializable_report():
    feedback_service = FeedbackAnalysisService(
        "tests/data/task10_golden_set.json"
    )

    quality_service = AIQualityEvaluationService(
        feedback_analysis_service=feedback_service
    )

    ab_service = AIABTestService(
        feedback_analysis_service=feedback_service,
        quality_evaluation_service=quality_service,
    )

    variant_a = {
        "TC001": "ETF fund.",
        "TC002": "stock bond.",
        "TC003": "diversification.",
    }

    variant_b = {
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

    report = ab_service.create_report(
        variant_a=variant_a,
        variant_b=variant_b,
        themes=[
            "answer_relevance",
            "topic_understanding",
            "rag_relevance",
        ],
    )

    assert report["total_cases"] == 3
    assert report["variant_a"]["passed_cases"] == 0
    assert report["variant_b"]["passed_cases"] == 3
    assert report["variant_a"]["score_percentage"] == 0.0
    assert report["variant_b"]["score_percentage"] == 100.0
    assert len(report["results"]) == 3


def test_evaluate_feedback_records_uses_feedback_themes():
    feedback_service = FeedbackAnalysisService(
        "tests/data/task10_golden_set.json"
    )

    quality_service = AIQualityEvaluationService(
        feedback_analysis_service=feedback_service
    )

    ab_service = AIABTestService(
        feedback_analysis_service=feedback_service,
        quality_evaluation_service=quality_service,
    )

    feedback_records = [
        SimpleNamespace(
            record_id="FB001",
            theme="answer_relevance",
            feedback="down",
        ),
        SimpleNamespace(
            record_id="FB002",
            theme="topic_understanding",
            feedback="down",
        ),
    ]

    variant_a = {
        "TC001": "ETF fund.",
        "TC002": "stock bond.",
    }

    variant_b = {
        "TC001": (
            "An ETF is an exchange-traded fund "
            "that trades on a stock exchange."
        ),
        "TC002": (
            "A stock represents ownership in a company, "
            "while a bond represents a loan to an issuer."
        ),
    }

    report = ab_service.evaluate_feedback_records(
        variant_a=variant_a,
        variant_b=variant_b,
        feedback_records=feedback_records,
    )

    assert report.total_cases == 2
    assert report.variant_a_passed == 0
    assert report.variant_b_passed == 2
    assert report.variant_a_score == 0.0
    assert report.variant_b_score == 100.0

    assert len(report.results) == 2

    assert report.results[0].case_id in {"TC001", "TC002"}
    assert report.results[1].case_id in {"TC001", "TC002"}

    assert {
        result.theme
        for result in report.results
    } == {
        "answer_relevance",
        "topic_understanding",
    }


def test_evaluate_full_task10_feedback_dataset():
    feedback_dataset_service = FeedbackDatasetService(
        "tests/data/task10_feedback_dataset.json"
    )

    feedback_records = feedback_dataset_service.load_records()

    feedback_service = FeedbackAnalysisService(
        "tests/data/task10_golden_set.json"
    )

    quality_service = AIQualityEvaluationService(
        feedback_analysis_service=feedback_service
    )

    ab_service = AIABTestService(
        feedback_analysis_service=feedback_service,
        quality_evaluation_service=quality_service,
    )

    variant_a = {
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

    variant_b = {
        "TC001": (
            "An ETF is an exchange-traded fund that holds a collection "
            "of assets such as stocks or bonds and trades on a stock exchange."
        ),
        "TC002": (
            "Stocks represent ownership in a company, while bonds represent "
            "debt issued by a company or government. Stocks generally have "
            "higher potential volatility, while bonds provide interest payments."
        ),
        "TC003": (
            "Diversification means spreading investments across different "
            "assets, sectors, or regions to reduce reliance on a single "
            "investment and manage portfolio risk."
        ),
        "TC004": (
            "Compound interest means earning interest on both the original "
            "principal and previously accumulated interest. Over time, this "
            "can cause savings to grow faster than simple interest."
        ),
        "TC005": (
            "A mutual fund pools money from multiple investors and invests "
            "that money in a portfolio of assets such as stocks or bonds. "
            "Investors own units of the fund."
        ),
        "TC006": (
            "Risk tolerance describes how much investment loss or volatility "
            "an investor can financially and emotionally handle. It can be "
            "considered alongside investment goals, time horizon, and financial "
            "circumstances."
        ),
        "TC007": (
            "Based on the available conversation context, the comparison "
            "should consider the characteristics and goals discussed earlier "
            "rather than treating the new question as completely unrelated."
        ),
        "TC008": (
            "A future stock price cannot be known with certainty. Its price "
            "may rise or fall depending on company performance, market "
            "conditions, economic factors, and investor expectations."
        ),
        "TC009": (
            "The sentiment is positive because the provided text expresses "
            "favorable views about the subject."
        ),
        "TC010": (
            "Portfolio health can be assessed using factors such as "
            "diversification, risk exposure, asset allocation, investment "
            "goals, time horizon, and concentration. These factors do not "
            "guarantee a particular investment outcome."
        ),
    }

    report = ab_service.evaluate_feedback_records(
        variant_a=variant_a,
        variant_b=variant_b,
        feedback_records=feedback_records,
    )

    assert len(feedback_records) == 10
    assert report.total_cases == 10

    assert report.variant_a_passed <= report.total_cases
    assert report.variant_b_passed <= report.total_cases

    assert 0.0 <= report.variant_a_score <= 100.0
    assert 0.0 <= report.variant_b_score <= 100.0

    assert len(report.results) == 10

    evaluated_case_ids = {
        result.case_id
        for result in report.results
    }

    expected_case_ids = {
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

    assert evaluated_case_ids == expected_case_ids


def test_full_task10_ab_test_report_with_controlled_responses():
    feedback_dataset_service = FeedbackDatasetService(
        "tests/data/task10_feedback_dataset.json"
    )

    feedback_records = feedback_dataset_service.load_records()

    feedback_service = FeedbackAnalysisService(
        "tests/data/task10_golden_set.json"
    )

    quality_service = AIQualityEvaluationService(
        feedback_analysis_service=feedback_service
    )

    ab_service = AIABTestService(
        feedback_analysis_service=feedback_service,
        quality_evaluation_service=quality_service,
    )

    available_context = {
        "risk_tolerance": "moderate",
    }

    variant_a = {
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

    variant_b = {
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
            "Based on your moderate risk tolerance, risk tolerance describes "
            "how much investment loss or volatility you may be financially "
            "and emotionally able to handle. It should be considered "
            "alongside your investment goals, time horizon, and financial "
            "situation."
        ),
        "TC007": (
            "To compare the two investments using the earlier conversation "
            "context, we should consider the characteristics, risks, and goals "
            "discussed previously rather than treating the new question as "
            "completely unrelated."
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
            "Portfolio health can be assessed using diversification, risk "
            "exposure, asset allocation, investment goals, and time horizon."
        ),
    }

    report = ab_service.evaluate_feedback_records(
        variant_a=variant_a,
        variant_b=variant_b,
        feedback_records=feedback_records,
        available_context=available_context,
    )

    assert report.total_cases == 10

    assert 0 <= report.variant_a_passed <= 10
    assert 0 <= report.variant_b_passed <= 10

    assert 0.0 <= report.variant_a_score <= 100.0
    assert 0.0 <= report.variant_b_score <= 100.0

    assert len(report.results) == 10

    assert {
        result.case_id
        for result in report.results
    } == {
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