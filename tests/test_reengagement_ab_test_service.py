from app.services.reengagement_ab_test_service import (
    ReengagementABTestService,
)


def test_assignment_is_deterministic() -> None:
    service = ReengagementABTestService()

    first = service.assign("user-123")
    second = service.assign("user-123")

    assert first == second
    assert first.user_id == "user-123"
    assert first.variant in {"ai", "template"}


def test_different_users_can_be_assigned() -> None:
    service = ReengagementABTestService()

    assignments = [
        service.assign(f"user-{index}")
        for index in range(100)
    ]

    variants = {assignment.variant for assignment in assignments}

    assert "ai" in variants
    assert "template" in variants


def test_assignment_normalizes_user_id() -> None:
    service = ReengagementABTestService()

    assignment = service.assign("  user-123  ")

    assert assignment.user_id == "user-123"


def test_empty_user_id_is_rejected() -> None:
    service = ReengagementABTestService()

    try:
        service.assign("")
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert str(exc) == "user_id cannot be empty"