from typing import Any

from app.repositories.churn_repository import ChurnRepository


class ChurnRiskService:
    def __init__(
        self,
        churn_repository: ChurnRepository | None = None,
        user_features_repository: Any | None = None,
    ) -> None:
        self.churn_repository = churn_repository or ChurnRepository()
        self.user_features_repository = user_features_repository

    def get_churn_risk(self, user_id: str) -> dict[str, Any]:
        if not user_id or not user_id.strip():
            raise ValueError("user_id cannot be empty")

        normalized_user_id = user_id.strip()

        if self.user_features_repository is not None:
            result = self.user_features_repository.get_features(
                normalized_user_id
            )

            if result is None:
                raise LookupError(
                    f"Churn risk not found for user {normalized_user_id}"
                )

            score = result.get("churn_score")

            if score is None:
                raise LookupError(
                    f"Churn risk has not been computed for user {normalized_user_id}"
                )

            computed_at = result.get("churn_score_computed_at")
            result_user_id = result.get("user_id", normalized_user_id)
        else:
            result = self.churn_repository.get_latest_score(
                normalized_user_id
            )

            if result is None:
                raise LookupError(
                    f"Churn risk not found for user {normalized_user_id}"
                )

            score = result["score"]
            computed_at = result["computed_at"]
            result_user_id = result["user_id"]

        score = float(score)

        if score > 0.7:
            risk_level = "high"
        elif score >= 0.4:
            risk_level = "medium"
        else:
            risk_level = "low"

        return {
            "userId": str(result_user_id),
            "score": round(score, 4),
            "riskLevel": risk_level,
            "computedAt": computed_at,
        }
