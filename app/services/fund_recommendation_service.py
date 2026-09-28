from __future__ import annotations

from typing import Any

from app.repositories.fund_repository import FundRepository
from app.repositories.profile_repository import ProfileRepository
from app.repositories.recommendation_exposure_repository import (
    RecommendationExposureRepository,
)
from app.schemas.fund_recommendation import (
    FundRecommendationResponse,
)
from app.services.fund_collaborative_signal_service import (
    FundCollaborativeSignalService,
)
from app.services.fund_recommendation_diversity_service import (
    FundRecommendationDiversityService,
)
from app.services.fund_recommendation_scoring_config import (
    FundRecommendationScoringConfigProvider,
)
from app.services.fund_recommendation_scoring_service import (
    FundRecommendationScoringService,
)
from app.services.fund_trending_service import (
    FundTrendingService,
)


class FundRecommendationService:
    """Orchestrates the hybrid mutual-fund recommendation flow."""

    def __init__(
        self,
        fund_repository: FundRepository | None = None,
        profile_repository: ProfileRepository | None = None,
        exposure_repository: (
            RecommendationExposureRepository | None
        ) = None,
        scoring_service: (
            FundRecommendationScoringService | None
        ) = None,
        collaborative_service: (
            FundCollaborativeSignalService | None
        ) = None,
        diversity_service: (
            FundRecommendationDiversityService | None
        ) = None,
        trending_service: FundTrendingService | None = None,
    ) -> None:
        self.fund_repository = (
            fund_repository
            or FundRepository()
        )

        self.profile_repository = (
            profile_repository
            or ProfileRepository()
        )

        self.exposure_repository = (
            exposure_repository
            or RecommendationExposureRepository()
        )

        self.scoring_service = (
            scoring_service
            or FundRecommendationScoringService(
                config=FundRecommendationScoringConfigProvider.load()
            )
        )

        self.collaborative_service = (
            collaborative_service
            or FundCollaborativeSignalService()
        )

        self.diversity_service = (
            diversity_service
            or FundRecommendationDiversityService()
        )

        self.trending_service = (
            trending_service
            or FundTrendingService()
        )

    def recommend(
        self,
        *,
        user_id: str,
        goal: str | None = None,
        level: str | None = None,
        limit: int = 3,
    ) -> FundRecommendationResponse:
        """Generate mutual-fund recommendations for one user."""

        if not user_id or not user_id.strip():
            raise ValueError(
                "user_id cannot be empty"
            )

        if limit <= 0:
            raise ValueError(
                "limit must be greater than zero"
            )

        user_id = user_id.strip()

        profile = self.profile_repository.get_profile(
            user_id
        )

        if profile is None:
            raise ValueError(
                f"Profile not found for user: {user_id}"
            )

        resolved_level = self._resolve_level(
            level,
            profile,
        )

        funds = self.fund_repository.get_active_funds()

        if not funds:
            return FundRecommendationResponse(
                userId=user_id,
                recommendations=[],
                trendingAmongLearners=[],
            )

        scored_candidates = self.scoring_service.score_funds(
            funds,
            goal=goal,
            level=resolved_level,
        )

        recent_exposures = (
            self.exposure_repository.get_recent_user_exposures(
                user_id,
                days=28,
            )
        )

        diverse_candidates = (
            self.diversity_service.select_diverse_funds(
                scored_candidates,
                recent_exposures,
                limit=limit,
            )
        )

        recommendations = []

        for candidate in diverse_candidates:
            collaborative = (
                self.collaborative_service.calculate_signal(
                    candidate["scheme_code"],
                    [],
                )
            )

            explanation = candidate["explanation"]

            if collaborative["available"]:
                explanation += (
                    " Users with similar activity "
                    "also considered this fund."
                )

            recommendations.append(
                {
                    "schemeCode": candidate["scheme_code"],
                    "schemeName": candidate["scheme_name"],
                    "amcName": candidate["amc_name"],
                    "category": candidate["category"],
                    "score": candidate["score"],
                    "explanation": explanation,
                    "collaborativeAvailable": (
                        collaborative["available"]
                    ),
                }
            )

        for rank, recommendation in enumerate(
            recommendations,
            start=1,
        ):
            self.exposure_repository.record_exposure(
                user_id=user_id,
                scheme_code=recommendation["schemeCode"],
                amc_name=recommendation["amcName"],
                recommendation_rank=rank,
                recommendation_source="HYBRID",
            )

        trending = self.trending_service.get_trending(
            level=int(resolved_level),
            days=28,
            limit=5,
        )

        return FundRecommendationResponse(
            userId=user_id,
            recommendations=recommendations,
            trendingAmongLearners=trending,
        )

    @staticmethod
    def _resolve_level(
        requested_level: str | None,
        profile: dict[str, Any],
    ) -> str:
        if requested_level:
            normalized = requested_level.strip()

            if normalized:
                try:
                    level_number = int(normalized)
                except ValueError as exc:
                    raise ValueError(
                        "level must be a positive integer"
                    ) from exc

                if level_number < 1:
                    raise ValueError(
                        "level must be a positive integer"
                    )

                return normalized

        profile_level = profile.get("level")

        if profile_level is None:
            raise ValueError(
                "Learner level is unavailable"
            )

        try:
            profile_level = int(profile_level)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                "Stored learner level is invalid"
            ) from exc

        if profile_level < 1:
            raise ValueError(
                "Stored learner level is invalid"
            )

        return str(profile_level)