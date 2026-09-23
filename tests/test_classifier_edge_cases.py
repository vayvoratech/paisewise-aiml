import pytest

from app.services.topic_classifier import (
    TopicCategory,
    classify_question,
)


# ---------------------------------------------------------
# PERSONAL-ADVICE INDIRECT WORDING
# ---------------------------------------------------------

@pytest.mark.parametrize(
    "question",
    [
        "What would you invest in if you were me?",
        "What would you buy if you were me?",
        "What would you choose if you were me?",
        "What would you recommend for me?",
        "Where would you put my savings?",
        "What would be suitable for my situation?",
        "Which investment fits my goals?",
        "Can you help me decide what to invest in?",
        "Can you pick something for my portfolio?",
        "What should someone like me invest in?",
    ],
)
def test_indirect_personal_advice(question):
    assert classify_question(question) == TopicCategory.PERSONAL_ADVICE


# ---------------------------------------------------------
# MARKET VARIATIONS
# ---------------------------------------------------------

@pytest.mark.parametrize(
    "question",
    [
        "Why are markets volatile today?",
        "Why are markets rising?",
        "Why are markets falling?",
        "How are markets performing?",
        "What are markets doing today?",
        "How are global markets performing?",
        "How are Indian markets performing?",
        "What is happening across the markets?",
        "Are markets trending upward?",
        "Are markets trending downward?",
    ],
)
def test_market_variations(question):
    assert classify_question(question) == TopicCategory.MARKET


# ---------------------------------------------------------
# PRODUCT VS PERSONAL ADVICE
# ---------------------------------------------------------

@pytest.mark.parametrize(
    "question",
    [
        "What is an ETF?",
        "What is a mutual fund?",
        "What is a bond?",
        "How does an ETF work?",
        "How does a mutual fund work?",
    ],
)
def test_product_educational_questions(question):
    assert classify_question(question) == TopicCategory.PRODUCT


@pytest.mark.parametrize(
    "question",
    [
        "Should I buy an ETF?",
        "Should I invest in a mutual fund?",
        "Which bond should I buy?",
        "Which ETF is best for me?",
        "Can you recommend a mutual fund for me?",
    ],
)
def test_product_personal_advice_boundary(question):
    assert classify_question(question) == TopicCategory.PERSONAL_ADVICE


# ---------------------------------------------------------
# MARKET VS PRODUCT
# ---------------------------------------------------------

@pytest.mark.parametrize(
    "question",
    [
        "What is a stock?",
        "What are stocks?",
        "What is a bond?",
        "What is an ETF?",
    ],
)
def test_investment_product_questions(question):
    assert classify_question(question) == TopicCategory.PRODUCT


@pytest.mark.parametrize(
    "question",
    [
        "How is the stock market performing?",
        "Why is the stock market falling?",
        "What is the market trend?",
        "What is the NIFTY trend?",
        "How is Sensex performing?",
    ],
)
def test_market_questions_with_product_words(question):
    assert classify_question(question) == TopicCategory.MARKET


# ---------------------------------------------------------
# JARGON VS PRODUCT
# ---------------------------------------------------------

@pytest.mark.parametrize(
    "question",
    [
        "What does NAV mean?",
        "Explain volatility.",
        "What is diversification?",
        "What does an expense ratio mean?",
        "Explain compounding.",
        "What does liquidity mean?",
    ],
)
def test_jargon_questions(question):
    assert classify_question(question) == TopicCategory.JARGON


def test_etf_is_product_not_jargon():
    assert classify_question("What is an ETF?") == TopicCategory.PRODUCT


def test_volatility_is_jargon_not_market():
    assert classify_question("What does volatility mean?") == TopicCategory.JARGON


# ---------------------------------------------------------
# MIXED INTENT
# ---------------------------------------------------------

@pytest.mark.parametrize(
    "question",
    [
        "Should I buy an ETF because the market is rising?",
        "Which stock should I buy if NIFTY is falling?",
        "Should I invest in a mutual fund because the market is recovering?",
        "Which investment is best for me in the current market?",
        "Should I sell my stock because Sensex is falling?",
    ],
)
def test_personal_advice_has_highest_priority(question):
    assert classify_question(question) == TopicCategory.PERSONAL_ADVICE


# ---------------------------------------------------------
# NORMALIZATION
# ---------------------------------------------------------

@pytest.mark.parametrize(
    "question",
    [
        "WHAT IS AN ETF?",
        "what is an etf?",
        "  What is an ETF?  ",
        "What is an ETF!!!",
        "WHAT IS THE MARKET PERFORMING?",
        "  Why are markets volatile today?  ",
    ],
)
def test_case_and_spacing_variations(question):
    result = classify_question(question)

    assert result in {
        TopicCategory.PRODUCT,
        TopicCategory.MARKET,
    }


# ---------------------------------------------------------
# INVALID INPUT
# ---------------------------------------------------------

def test_empty_question_raises_error():
    with pytest.raises(ValueError):
        classify_question("")


def test_whitespace_question_raises_error():
    with pytest.raises(ValueError):
        classify_question("     ")


def test_non_string_question_raises_error():
    with pytest.raises(TypeError):
        classify_question(None)