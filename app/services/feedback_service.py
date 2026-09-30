from typing import Any

from app.repositories.feedback_repository import FeedbackRepository
from app.services.slack_notification_service import SlackNotificationService


class FeedbackService:
    """
    Service for AI chat feedback.

    PostgreSQL is used only for feedback
    persistence and analytics.

    This service is separate from ChatService.
    """

    ALLOWED_FEEDBACK = {
        "up",
        "down",
    }

    def __init__(
        self,
        feedback_repository: FeedbackRepository | None = None,
        slack_service: SlackNotificationService | None = None,
    ) -> None:
        self.feedback_repository = (
            feedback_repository
            or FeedbackRepository()
        )

        self.slack_service = slack_service

    # --------------------------------------------------
    # Submit feedback
    # --------------------------------------------------

    def submit_feedback(
        self,
        response_id: str,
        user_id: str,
        category: str,
        feedback: str,
    ) -> dict[str, Any]:

        if not isinstance(
            response_id,
            str,
        ):
            raise TypeError(
                "response_id must be a string"
            )

        if not response_id.strip():
            raise ValueError(
                "response_id cannot be empty"
            )

        if not isinstance(
            user_id,
            str,
        ):
            raise TypeError(
                "user_id must be a string"
            )

        if not user_id.strip():
            raise ValueError(
                "user_id cannot be empty"
            )

        if not isinstance(
            category,
            str,
        ):
            raise TypeError(
                "category must be a string"
            )

        if not category.strip():
            raise ValueError(
                "category cannot be empty"
            )

        if feedback not in self.ALLOWED_FEEDBACK:
            raise ValueError(
                "feedback must be 'up' or 'down'"
            )

        # Existing feedback persistence
        self.feedback_repository.create_feedback(
            response_id=response_id.strip(),
            user_id=user_id.strip(),
            category=category.strip(),
            feedback=feedback,
        )

        # --------------------------------------------------
        # Task 10.3 - Automatic negative feedback alert
        # --------------------------------------------------

        if (
            feedback == "down"
            and self.slack_service is not None
        ):
            self.slack_service.notify(
                (
                    "⚠️ AI Feedback Alert\n\n"
                    f"Response ID: {response_id.strip()}\n"
                    f"User ID: {user_id.strip()}\n"
                    f"Category: {category.strip()}\n"
                    "Feedback: thumbs down\n"
                    "Action: Review during the feedback improvement cycle."
                )
            )

        # Existing response remains unchanged
        return {
            "status": "success",
            "message": (
                "Feedback submitted successfully."
            ),
        }

    # --------------------------------------------------
    # Weekly analytics
    # --------------------------------------------------

    def get_weekly_analytics(
        self,
    ) -> list[dict[str, Any]]:

        return (
            self.feedback_repository
            .get_weekly_analytics()
        )