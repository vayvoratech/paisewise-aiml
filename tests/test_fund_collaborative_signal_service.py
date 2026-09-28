from app.services.fund_collaborative_signal_service import (
    FundCollaborativeSignalService,
)


def test_no_peer_data_returns_unavailable_signal():
    service = FundCollaborativeSignalService()

    result = service.calculate_signal(
        "FUND001",
        [],
    )

    assert result["signal"] == 0.0
    assert result["available"] is False
    assert result["similar_user_count"] == 0
    assert result["interaction_count"] == 0


def test_unknown_scheme_returns_unavailable_signal():
    service = FundCollaborativeSignalService()

    result = service.calculate_signal(
        "FUND001",
        [
            {
                "scheme_code": "FUND002",
                "similar_user_count": 10,
                "interaction_count": 20,
            }
        ],
    )

    assert result["signal"] == 0.0
    assert result["available"] is False


def test_peer_activity_produces_signal():
    service = FundCollaborativeSignalService()

    result = service.calculate_signal(
        "FUND001",
        [
            {
                "scheme_code": "FUND001",
                "similar_user_count": 10,
                "interaction_count": 20,
            }
        ],
    )

    assert result["available"] is True
    assert result["similar_user_count"] == 10
    assert result["interaction_count"] == 20
    assert 0.0 < result["signal"] <= 1.0


def test_multiple_records_are_aggregated():
    service = FundCollaborativeSignalService()

    result = service.calculate_signal(
        "FUND001",
        [
            {
                "scheme_code": "FUND001",
                "similar_user_count": 5,
                "interaction_count": 10,
            },
            {
                "scheme_code": "FUND001",
                "similar_user_count": 3,
                "interaction_count": 8,
            },
        ],
    )

    assert result["similar_user_count"] == 8
    assert result["interaction_count"] == 18
    assert result["available"] is True


def test_negative_activity_is_not_used():
    service = FundCollaborativeSignalService()

    result = service.calculate_signal(
        "FUND001",
        [
            {
                "scheme_code": "FUND001",
                "similar_user_count": -10,
                "interaction_count": -5,
            }
        ],
    )

    assert result["signal"] == 0.0
    assert result["available"] is False


def test_empty_scheme_code_is_rejected():
    service = FundCollaborativeSignalService()

    try:
        service.calculate_signal("", [])
        assert False
    except ValueError as exc:
        assert "scheme_code cannot be empty" in str(exc)