import pytest

from app.services.topic_classifier import (
    TopicCategory,
    classify_question,
)


# ---------------------------------------------------------
# PERSONAL ADVICE — HIGH PRIORITY
# ---------------------------------------------------------

@pytest.mark.parametrize(
    "question",
    [
        "Which stock should I buy?",
        "Should I invest in an ETF?",
        "Can you recommend a mutual fund for me?",
        "Where should I invest my savings?",
        "What should I invest in?",
        "Which investment is best for me?",
        "Would this investment suit my financial situation?",
        "What would you invest in if you were me?",
        "Can you choose an investment for me?",
        "Help me decide where to invest.",
        "Should I sell this stock?",
        "Should I change my portfolio?",
        "Which fund fits my goals?",
        "Is this investment right for me?",
        "Can you suggest a stock for me?",
    ],
)
def test_personal_advice_edge_cases(question):
    assert classify_question(question) == TopicCategory.PERSONAL_ADVICE


# ---------------------------------------------------------
# MIXED INTENT — PERSONAL ADVICE MUST WIN
# ---------------------------------------------------------

@pytest.mark.parametrize(
    "question",
    [
        "Should I buy an ETF because NIFTY is rising?",
        "Which stock should I buy if the market is falling?",
        "Should I invest in a mutual fund because the market is recovering?",
        "Which investment is best for me in the current market?",
        "Should I sell my stock because Sensex is falling?",
    ],
)
def test_personal_advice_overrides_other_categories(question):
    assert classify_question(question) == TopicCategory.PERSONAL_ADVICE


# ---------------------------------------------------------
# MARKET
# ---------------------------------------------------------

@pytest.mark.parametrize(
    "question",
    [
        "How is the market performing?",
        "Why is the market falling?",
        "Why is the stock market rising?",
        "What is the NIFTY trend?",
        "How is the Sensex performing?",
        "What is happening in the market today?",
        "Why are Indian indices falling?",
        "What is the current market outlook?",
        "How is the broader market performing?",
        "Why are markets volatile today?",
    ],
)
def test_market_edge_cases(question):
    assert classify_question(question) == TopicCategory.MARKET


# ---------------------------------------------------------
# PRODUCT
# ---------------------------------------------------------

@pytest.mark.parametrize(
    "question",
    [
        "What is an ETF?",
        "What is a mutual fund?",
        "What is a bond?",
        "What is an IPO?",
        "What is an SIP?",
        "How does an index fund work?",
        "Tell me about stocks.",
        "What is a REIT?",
        "Explain bond ETFs.",
        "What is a demat account?",
    ],
)
def test_product_edge_cases(question):
    assert classify_question(question) == TopicCategory.PRODUCT


# ---------------------------------------------------------
# JARGON
# ---------------------------------------------------------

@pytest.mark.parametrize(
    "question",
    [
        "What is diversification?",
        "Explain volatility.",
        "What does NAV mean?",
        "What is an expense ratio?",
        "Explain compounding.",
        "What does liquidity mean?",
        "What is risk tolerance?",
        "Explain asset allocation.",
        "What is CAGR?",
        "What does tracking error mean?",
    ],
)
def test_jargon_edge_cases(question):
    assert classify_question(question) == TopicCategory.JARGON


# ---------------------------------------------------------
# IMPORTANT BOUNDARY CASES
# ---------------------------------------------------------

def test_should_learn_is_not_personal_advice():
    assert (
        classify_question("Should I learn about ETFs?")
        == TopicCategory.JARGON
    )


def test_what_is_stock_is_product():
    assert (
        classify_question("What is a stock?")
        == TopicCategory.PRODUCT
    )


def test_stock_market_is_market():
    assert (
        classify_question("How is the stock market performing?")
        == TopicCategory.MARKET
    )


def test_market_keyword_alone_does_not_break_product():
    assert (
        classify_question("What is a market-linked investment product?")
        == TopicCategory.PRODUCT
    )


# ---------------------------------------------------------
# CASE / PUNCTUATION / WHITESPACE
# ---------------------------------------------------------

@pytest.mark.parametrize(
    "question",
    [
        "WHAT IS AN ETF?",
        "what is an etf?",
        "  What is an ETF?  ",
        "What is an ETF!!!",
        "WHAT IS THE MARKET PERFORMING?",
    ],
)
def test_normalization(question):
    result = classify_question(question)

    assert result in {
        TopicCategory.PRODUCT,
        TopicCategory.MARKET,
    }


# ---------------------------------------------------------
# INVALID INPUT
# ---------------------------------------------------------

def test_empty_question():
    with pytest.raises(ValueError):
        classify_question("")


def test_whitespace_question():
    with pytest.raises(ValueError):
        classify_question("     ")


def test_non_string_input():
    with pytest.raises(TypeError):
        classify_question(None)