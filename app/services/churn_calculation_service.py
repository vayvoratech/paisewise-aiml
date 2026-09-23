from datetime import datetime, timezone

from app.repositories.user_features_repository import UserFeaturesRepository
from app.services.churn_service import ChurnRequest, ChurnResponse, ChurnService


class ChurnCalculationService:
    def __init__(
        self,
        churn_service: ChurnService | None = None,
        user_features_repository: UserFeaturesRepository | None = None,
    ) -> None:
        self.churn_service = churn_service or ChurnService()
        self.user_features_repository = (
            user_features_repository or UserFeaturesRepository()
        )

    def calculate_for_user(self, user_id: str) -> ChurnResponse:
        if not user_id or not user_id.strip():
            raise ValueError("user_id cannot be empty")

        user_id = user_id.strip()

        features = self.user_features_repository.get_features(user_id)

        if features is None:
            raise ValueError(
                f"Churn features not found for user {user_id}"
            )

        # Convert database feature-store fields into the
        # JSON contract expected by ChurnService.
        request = ChurnRequest(
            userId=user_id,
            daysSinceLastActivity=int(
                features.get("days_since_last_active", 0)
            ),
            sessionCount7d=int(
                features.get("sessions_7d", 0)
            ),
            completedJourneySteps=int(
                features.get("lessons_completed_7d", 0)
            ),
            totalJourneySteps=max(
                1,
                int(features.get("chapters_completed", 1))
            ),
            daysSinceRegistration=int(
                features.get("days_since_registration", 0)
            ),
        )

        result = self.churn_service.calculate(request)

        computed_at = datetime.now(timezone.utc)

        # Store the latest score in user_features
        # and the historical score in user_churn_scores.
        self.user_features_repository.update_churn_score(
            user_id=user_id,
            churn_score=result.score,
            computed_at=computed_at,
        )

        return result