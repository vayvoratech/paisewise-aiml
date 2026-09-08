from uuid import UUID, uuid4

from services.login_location_tracker import track_login_location


def test_first_login_location():
    user_id = uuid4()

    result = track_login_location(
        user_id,
        "10.10.10.1",
        "Hyderabad",
    )

    assert result["city"] == "Hyderabad"
    assert result["previous_city"] is None
    assert result["location_changed"] is False


def test_changed_login_location():
    user_id = uuid4()

    first_result = track_login_location(
        user_id,
        "10.10.10.1",
        "Hyderabad",
    )

    assert first_result["previous_city"] is None

    second_result = track_login_location(
        user_id,
        "10.10.10.2",
        "Bengaluru",
    )

    assert second_result["city"] == "Bengaluru"
    assert second_result["previous_city"] == "Hyderabad"
    assert second_result["location_changed"] is True