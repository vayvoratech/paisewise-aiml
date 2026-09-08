from uuid import UUID

from services import recommendation_refresh


USER_ID = UUID("11111111-1111-1111-1111-111111111111")


def test_refresh_on_lesson_completion(monkeypatch):
    called = {}

    def mock_invalidate(user_id):
        called["user_id"] = user_id

    monkeypatch.setattr(
        recommendation_refresh,
        "invalidate_recommendation_cache",
        mock_invalidate
    )

    recommendation_refresh.refresh_recommendation_for_lesson_completion(
        USER_ID
    )

    assert called["user_id"] == USER_ID


def test_refresh_on_goal_update(monkeypatch):
    called = {}

    def mock_invalidate(user_id):
        called["user_id"] = user_id

    monkeypatch.setattr(
        recommendation_refresh,
        "invalidate_recommendation_cache",
        mock_invalidate
    )

    recommendation_refresh.refresh_recommendation_for_goal_update(
        USER_ID
    )

    assert called["user_id"] == USER_ID