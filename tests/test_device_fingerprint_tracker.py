from uuid import UUID, uuid4

from services.device_fingerprint_tracker import (
    is_new_device,
    track_device,
)


USER_ID = UUID("22222222-2222-2222-2222-222222222222")


def test_known_device():
    result = is_new_device(USER_ID, "device-001")

    assert result is False


def test_new_device():
    device_id = f"device-test-new-{uuid4()}"

    result = is_new_device(USER_ID, device_id)

    assert result is True


def test_track_new_device():
    device_id = f"device-test-track-{uuid4()}"

    result = track_device(USER_ID, device_id)

    assert result is True
    assert is_new_device(USER_ID, device_id) is False


def test_track_known_device():
    device_id = f"device-test-known-{uuid4()}"

    first_result = track_device(USER_ID, device_id)
    second_result = track_device(USER_ID, device_id)

    assert first_result is True
    assert second_result is False