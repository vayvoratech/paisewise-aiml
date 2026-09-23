from typing import Any

from app.schemas.chat import UserContext


class ContextService:
    """
    Database-independent context service.

    User context is supplied through JSON.

    No PostgreSQL.
    No ProfileRepository.
    No HoldingsRepository.
    No OrdersRepository.
    """

    @staticmethod
    def build_context(
        user_context: UserContext | None,
    ) -> dict[str, Any]:
        """
        Convert supplied JSON user context into
        a structure usable by the AI pipeline.
        """

        if user_context is None:
            return {
                "profile": {},
                "holdings": [],
                "recent_orders": [],
            }

        profile = {
            "goal": user_context.goal,
            "level": user_context.level,
            "kycStatus": user_context.kycStatus,
        }

        holdings = []

        if user_context.holdingSummary:
            holdings.append(
                user_context.holdingSummary
            )

        return {
            "profile": profile,
            "holdings": holdings,
            "recent_orders": [],
        }