from app.repositories.churn_reengagement_repository import (
    ChurnReengagementRepository,
)
from app.services.churn_notification_service import ChurnNotificationService
from app.services.reengagement_campaign_service import (
    ReengagementCampaignService,
)
from app.services.reengagement_message_service import (
    ReengagementMessageRequest,
)


class ReengagementNotificationService:
    def __init__(
        self,
        campaign_service: ReengagementCampaignService,
        notification_service: ChurnNotificationService,
        reengagement_repository: ChurnReengagementRepository | None = None,
    ) -> None:
        self.campaign_service = campaign_service
        self.notification_service = notification_service
        self.reengagement_repository = reengagement_repository

    async def process(
        self,
        request: ReengagementMessageRequest,
    ) -> bool:
        result = await self.campaign_service.create_message(request)

        if result is None:
            return False

        published = self.notification_service.publish_if_high_risk(
            user_id=result.userId,
            churn_score=request.churnScore,
            message=result.message,
        )

        if not published:
            return False

        # Tracking is optional for isolated/unit-test usage.
        # The production DAG provides the repository explicitly.
        if self.reengagement_repository is not None:
            self.reengagement_repository.create_campaign(
                user_id=result.userId,
                churn_score=request.churnScore,
                variant=result.generatedBy,
                message=result.message,
            )

        return True