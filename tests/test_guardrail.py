import pytest

from app.services.guardrail_service import (
    PERSONAL_ADVICE_RESPONSE,
    check_guardrail,
)
from app.services.topic_classifier import TopicCategory


# ---------------------------------------------------------
# PERSONAL ADVICE MUST BE BLOCKED
# ---------------------------------------------------------

@pytest.mark.parametrize(
    "question",
    [
        "Which stock should I buy?",
        "Should I invest in an ETF?",
        "Which mutual fund should I choose?",
        "Where should I invest my savings?",
        "What should I invest in?",
        "Can you recommend a stock for me?",
        "Which investment is best for me?",
        "What would you invest in if you were me?",
        "Would this investment suit my financial situation?",
    ],
)
def test_personal_advice_is_blocked(question):
    result = check_guardrail(question)

    assert result.blocked is True
    assert result.category == TopicCategory.PERSONAL_ADVICE
    assert result.message == PERSONAL_ADVICE_RESPONSE


# ---------------------------------------------------------
# NORMAL QUESTIONS MUST NOT BE BLOCKED
# ---------------------------------------------------------

@pytest.mark.parametrize(
    "question",
    [
        "What is an ETF?",
        "What is a mutual fund?",
        "What does diversification mean?",
        "Explain volatility.",
        "How is the market performing?",
        "Why is NIFTY falling?",
        "How is Sensex performing?",
    ],
)
def test_normal_questions_are_not_blocked(question):
    result = check_guardrail(question)

    assert result.blocked is False
    assert result.category != TopicCategory.PERSONAL_ADVICE
    assert result.message is None


# ---------------------------------------------------------
# MIXED QUESTIONS
# PERSONAL ADVICE MUST WIN
# ---------------------------------------------------------

@pytest.mark.parametrize(
    "question",
    [
        "Should I buy an ETF because the market is rising?",
        "Which stock should I buy if NIFTY is falling?",
        "Should I invest in a mutual fund because the market is recovering?",
    ],
)
def test_personal_advice_overrides_other_topics(question):
    result = check_guardrail(question)

    assert result.blocked is True
    assert result.category == TopicCategory.PERSONAL_ADVICE
    assert result.message == PERSONAL_ADVICE_RESPONSE


# ---------------------------------------------------------
# INVALID INPUT
# ---------------------------------------------------------

def test_empty_question():
    with pytest.raises(ValueError):
        check_guardrail("")


def test_whitespace_question():
    with pytest.raises(ValueError):
        check_guardrail("   ")


def test_non_string_question():
    with pytest.raises(TypeError):
        check_guardrail(None)