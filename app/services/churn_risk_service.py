from typing import Any

from app.repositories.user_features_repository import UserFeaturesRepository


class ChurnRiskService:
    def __init__(
        self,
        user_features_repository: UserFeaturesRepository | None = None,
    ) -> None:
        self.user_features_repository = (
            user_features_repository or UserFeaturesRepository()
        )

    def get_churn_risk(self, user_id: str) -> dict[str, Any]:
        if not user_id or not user_id.strip():
            raise ValueError("user_id cannot be empty")

        normalized_user_id = user_id.strip()

        features = self.user_features_repository.get_features(normalized_user_id)

        if features is None:
            raise LookupError(
                f"Churn risk not found for user {normalized_user_id}"
            )

        score_value = features.get("churn_score")

        # A missing churn score means it has not been computed yet.
        if score_value is None:
            raise LookupError(
                f"Churn risk has not been computed for user {normalized_user_id}"
            )

        score = float(score_value)

        if score > 0.7:
            risk_level = "high"
        elif score >= 0.4:
            risk_level = "medium"
        else:
            risk_level = "low"

        return {
            "userId": str(features.get("user_id", normalized_user_id)),
            "score": round(score, 4),
            "riskLevel": risk_level,
            "computedAt": features.get("churn_score_computed_at"),
        }