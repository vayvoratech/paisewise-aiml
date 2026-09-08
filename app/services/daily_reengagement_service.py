from collections.abc import Iterable

from app.repositories.user_journey_repository import (
    UserJourneyRepository,
)
from app.services.reengagement_message_service import (
    ReengagementMessageRequest,
)
from app.services.reengagement_notification_service import (
    ReengagementNotificationService,
)


class DailyReengagementService:
    """
    Processes already-calculated churn results and sends
    high-risk users through the re-engagement notification flow.

    Database access is kept in UserJourneyRepository.
    The AI/re-engagement services receive only JSON-style journey data.
    """

    HIGH_RISK_THRESHOLD = 0.7

    def __init__(
        self,
        notification_service: ReengagementNotificationService,
        journey_repository: UserJourneyRepository | None = None,
    ) -> None:
        self.notification_service = notification_service
        self.journey_repository = (
            journey_repository or UserJourneyRepository()
        )

    async def process(
        self,
        churn_results: Iterable,
    ) -> int:
        processed_count = 0

        for result in churn_results:
            if result.score <= self.HIGH_RISK_THRESHOLD:
                continue

            journey_context = (
                self.journey_repository.get_incomplete_journey(
                    result.userId
                )
            )

            request = ReengagementMessageRequest(
                userId=result.userId,
                churnScore=result.score,
                journeyContext=journey_context,
            )

            published = await self.notification_service.process(
                request
            )

            if published:
                processed_count += 1

        return processed_count