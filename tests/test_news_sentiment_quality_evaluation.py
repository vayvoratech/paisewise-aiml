import pytest

from app.services.news_sentiment_service import NewsSentimentService


def test_positive_sentiment_is_accepted():
    response = """
    [
        {
            "title": "Markets gain after strong economic data",
            "sentiment": "positive"
        }
    ]
    """

    articles = [
        type(
            "Article",
            (),
            {
                "title": "Markets gain after strong economic data",
                "summary": "Markets rose after positive economic data.",
                "source": "Test",
            },
        )()
    ]

    result = NewsSentimentService._parse_response(
        response,
        articles,
    )

    assert result[0]["sentiment"] == "positive"


def test_negative_sentiment_is_accepted():
    response = """
    [
        {
            "title": "Markets fall amid weak economic data",
            "sentiment": "negative"
        }
    ]
    """

    articles = [
        type(
            "Article",
            (),
            {
                "title": "Markets fall amid weak economic data",
                "summary": "Markets declined after weak economic data.",
                "source": "Test",
            },
        )()
    ]

    result = NewsSentimentService._parse_response(
        response,
        articles,
    )

    assert result[0]["sentiment"] == "negative"


def test_neutral_sentiment_is_accepted():
    response = """
    [
        {
            "title": "Central bank maintains current policy",
            "sentiment": "neutral"
        }
    ]
    """

    articles = [
        type(
            "Article",
            (),
            {
                "title": "Central bank maintains current policy",
                "summary": "The central bank kept its policy unchanged.",
                "source": "Test",
            },
        )()
    ]

    result = NewsSentimentService._parse_response(
        response,
        articles,
    )

    assert result[0]["sentiment"] == "neutral"


def test_invalid_sentiment_is_rejected():
    response = """
    [
        {
            "title": "Market update",
            "sentiment": "very_positive"
        }
    ]
    """

    articles = [
        type(
            "Article",
            (),
            {
                "title": "Market update",
                "summary": "Market update.",
                "source": "Test",
            },
        )()
    ]

    with pytest.raises(RuntimeError, match="Invalid sentiment value"):
        NewsSentimentService._parse_response(
            response,
            articles,
        )


def test_invalid_json_is_rejected():
    response = "not valid json"

    articles = [
        type(
            "Article",
            (),
            {
                "title": "Market update",
                "summary": "Market update.",
                "source": "Test",
            },
        )()
    ]

    with pytest.raises(
        RuntimeError,
        match="invalid sentiment JSON",
    ):
        NewsSentimentService._parse_response(
            response,
            articles,
        )