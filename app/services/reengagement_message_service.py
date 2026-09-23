from typing import Any

from pydantic import BaseModel, Field


class ReengagementMessageRequest(BaseModel):
    userId: str = Field(..., min_length=1, max_length=100)
    churnScore: float = Field(..., ge=0, le=1)
    journeyContext: dict[str, Any]


class ReengagementMessageResponse(BaseModel):
    userId: str
    message: str
    generatedBy: str


class ReengagementMessageService:
    def generate(
        self,
        request: ReengagementMessageRequest,
    ) -> ReengagementMessageResponse:
        user_id = request.userId.strip()

        if not user_id:
            raise ValueError("userId cannot be empty")

        context = request.journeyContext

        completed_steps = context.get("completed_steps", [])
        incomplete_steps = context.get("incomplete_steps", [])

        message = self._build_template_message(
            completed_steps=completed_steps,
            incomplete_steps=incomplete_steps,
        )

        return ReengagementMessageResponse(
            userId=user_id,
            message=message,
            generatedBy="template",
        )

    @staticmethod
    def _build_template_message(
        completed_steps: list[Any],
        incomplete_steps: list[Any],
    ) -> str:

        if incomplete_steps:
            first_step = incomplete_steps[0]

            # Handle dictionary-based journey steps
            if isinstance(first_step, dict):
                step = first_step.get("step")
                status = first_step.get("status")

                if step == "paper_trading" and status == "inactive_last_7_days":
                    return (
                        "You've made a great start with your investment "
                        "journey. Try paper trading again today to keep "
                        "building your investing skills."
                    )

                if step == "paper_trading":
                    return (
                        "Continue your paper-trading journey today "
                        "and keep building your investing skills."
                    )

                if step == "kyc":
                    return (
                        "Your investment journey is almost there. "
                        "Complete your KYC to continue."
                    )

                if step == "learning":
                    return (
                        "Continue your learning journey and complete "
                        "your next lesson today."
                    )

                if step == "real_investment":
                    return (
                        "You're making good progress. Explore the next "
                        "step in your investment journey."
                    )

                # Generic dictionary step
                if step:
                    return (
                        f"You're almost there. Continue your "
                        f"{str(step).replace('_', ' ')} journey today."
                    )

            # Handle string-based journey steps
            if isinstance(first_step, str):
                step_name = first_step.strip()

                if step_name:
                    return (
                        f"You're almost there. Complete your "
                        f"{step_name} to continue your investment journey."
                    )

            return (
                "You're almost there. Come back and continue "
                "your investment journey today."
            )

        if completed_steps:
            return (
                "You've made a great start on your investment journey. "
                "Come back and take your next step today."
            )

        return (
            "Your investment journey is waiting for you. "
            "Come back and get started today."
        )