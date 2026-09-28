from app.services.news_cache_service import NewsCacheService


def test_same_article_does_not_require_refresh():
    cached = {
        "latest_article_key": "article-1",
        "latest_published_at": "2026-09-11T10:30:00+00:00",
    }

    should_refresh = (
        NewsCacheService.is_newer_article_available(
            cached=cached,
            latest_article_key="article-1",
            latest_published_at="2026-09-11T10:30:00+00:00",
        )
    )

    assert should_refresh is False


def test_new_article_requires_refresh():
    cached = {
        "latest_article_key": "article-1",
        "latest_published_at": "2026-09-11T10:30:00+00:00",
    }

    should_refresh = (
        NewsCacheService.is_newer_article_available(
            cached=cached,
            latest_article_key="article-2",
            latest_published_at="2026-09-11T11:00:00+00:00",
        )
    )

    assert should_refresh is True


def test_newer_timestamp_requires_refresh():
    cached = {
        "latest_article_key": None,
        "latest_published_at": "2026-09-11T10:30:00+00:00",
    }

    should_refresh = (
        NewsCacheService.is_newer_article_available(
            cached=cached,
            latest_article_key=None,
            latest_published_at="2026-09-11T11:00:00+00:00",
        )
    )

    assert should_refresh is True


def test_same_timestamp_does_not_require_refresh():
    cached = {
        "latest_article_key": None,
        "latest_published_at": "2026-09-11T10:30:00+00:00",
    }

    should_refresh = (
        NewsCacheService.is_newer_article_available(
            cached=cached,
            latest_article_key=None,
            latest_published_at="2026-09-11T10:30:00+00:00",
        )
    )

    assert should_refresh is False


def test_missing_cache_metadata_requires_refresh():
    cached = {
        "articles": {
            "news": []
        }
    }

    should_refresh = (
        NewsCacheService.is_newer_article_available(
            cached=cached,
            latest_article_key="article-1",
            latest_published_at="2026-09-11T11:00:00+00:00",
        )
    )

    assert should_refresh is True