from dataclasses import dataclass
import hashlib


@dataclass(frozen=True)
class ABTestAssignment:
    user_id: str
    variant: str


class ReengagementABTestService:
    """
    Assigns high-risk users to either the AI or template
    re-engagement variant.

    Assignment is deterministic for a user, so the same user
    remains in the same variant across repeated processing.
    """

    AI_VARIANT = "ai"
    TEMPLATE_VARIANT = "template"

    def assign(self, user_id: str) -> ABTestAssignment:
        if not user_id or not user_id.strip():
            raise ValueError("user_id cannot be empty")

        normalized_user_id = user_id.strip()

        digest = hashlib.sha256(
            normalized_user_id.encode("utf-8")
        ).hexdigest()

        bucket = int(digest[:8], 16) % 100

        if bucket < 50:
            variant = self.AI_VARIANT
        else:
            variant = self.TEMPLATE_VARIANT

        return ABTestAssignment(
            user_id=normalized_user_id,
            variant=variant,
        )