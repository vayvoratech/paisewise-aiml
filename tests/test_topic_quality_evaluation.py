
import pytest

from app.services.topic_classifier import (
    TopicCategory,
    classify_question,
)


@pytest.mark.parametrize(
    ("question", "expected_category"),
    [
        (
            "Which stock should I buy?",
            TopicCategory.PERSONAL_ADVICE,
        ),
        (
            "Why is the stock market falling?",
            TopicCategory.MARKET,
        ),
        (
            "What is an ETF?",
            TopicCategory.PRODUCT,
        ),
        (
            "What does diversification mean?",
            TopicCategory.JARGON,
        ),
        (
            "Explain compound interest.",
            TopicCategory.JARGON,
        ),
        (
            "What is a mutual fund?",
            TopicCategory.PRODUCT,
        ),
        (
            "How is the market performing?",
            TopicCategory.MARKET,
        ),
        (
            "Should I invest all my money in stocks?",
            TopicCategory.PERSONAL_ADVICE,
        ),
    ],
)
def test_topic_classification_baseline(
    question,
    expected_category,
):
    assert classify_question(question) == expected_category
