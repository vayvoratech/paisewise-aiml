from typing import Any

from pydantic import BaseModel, Field, model_validator

from app.schemas.churn import ChurnScoreRequest


class ChurnRequest(BaseModel):
    userId: str = Field(..., min_length=1, max_length=100)

    daysSinceLastActivity: int | None = Field(default=None, ge=0)
    sessionCount7d: int | None = Field(default=None, ge=0)
    completedJourneySteps: int | None = Field(default=None, ge=0)
    totalJourneySteps: int | None = Field(default=None, gt=0)
    daysSinceRegistration: int | None = Field(default=None, ge=0)

    features: dict[str, Any] | None = None

    @model_validator(mode="after")
    def populate_from_features(self):
        if self.features is not None:
            self.daysSinceLastActivity = (
                self.daysSinceLastActivity
                if self.daysSinceLastActivity is not None
<<<<<<< HEAD
                else int(self.features.get("days_since_last_activity", 0))
=======
                else int(
                    self.features.get(
                        "days_since_last_activity",
                        0,
                    )
                )
>>>>>>> srikanth_paise_wise_aiml
            )

            self.sessionCount7d = (
                self.sessionCount7d
                if self.sessionCount7d is not None
<<<<<<< HEAD
                else int(self.features.get("sessions_7d", 0))
=======
                else int(
                    self.features.get(
                        "sessions_7d",
                        0,
                    )
                )
>>>>>>> srikanth_paise_wise_aiml
            )

            self.completedJourneySteps = (
                self.completedJourneySteps
                if self.completedJourneySteps is not None
<<<<<<< HEAD
                else int(self.features.get("completed_journey_steps", 0))
=======
                else int(
                    self.features.get(
                        "completed_journey_steps",
                        0,
                    )
                )
>>>>>>> srikanth_paise_wise_aiml
            )

            self.totalJourneySteps = (
                self.totalJourneySteps
                if self.totalJourneySteps is not None
                else max(
                    1,
                    int(self.features.get("total_journey_steps", 1)),
                )
            )

            self.daysSinceRegistration = (
                self.daysSinceRegistration
                if self.daysSinceRegistration is not None
                else int(
                    self.features.get("days_since_registration", 0)
                )
            )

        return self


class ChurnResponse(BaseModel):
    userId: str
    score: float
    riskLevel: str


class ChurnService:
    def calculate(
        self,
<<<<<<< HEAD
        request: ChurnRequest | ChurnScoreRequest,
    ) -> ChurnResponse:

=======
        request: ChurnRequest,
    ) -> ChurnResponse:
>>>>>>> srikanth_paise_wise_aiml
        if not request.userId.strip():
            raise ValueError("userId cannot be empty")

        # Old feature-based format
        if isinstance(request, ChurnRequest) and request.features is not None:
            features = request.features

            score = 0.0

            days_since_registration = int(
                features.get(
                    "days_since_registration",
                    0,
                )
            )

            notification_open_rate = float(
                features.get(
                    "notification_open_rate_30d",
                    0.0,
                )
            )

            paper_trades_total = int(
                features.get(
                    "paper_trades_total",
                    0,
                )
            )

            paper_trades_7d = int(
                features.get(
                    "paper_trades_7d",
                    0,
                )
            )

            has_real_investment = bool(
                features.get(
                    "has_real_investment",
                    False,
                )
            )

            if days_since_registration <= 14:
                score += 0.20

            if notification_open_rate < 0.20:
                score += 0.15

            if paper_trades_total == 0:
                score += 0.20

            if paper_trades_7d == 0:
                score += 0.20

            if not has_real_investment:
                score += 0.20

            score = min(max(score, 0.0), 1.0)

        # New API format
        else:
            score = 0.0

            if request.daysSinceRegistration <= 14:
                score += 0.20

            if request.sessionCount7d == 0:
                score += 0.20

            if request.completedJourneySteps == 0:
                score += 0.20

            if request.daysSinceLastActivity >= 7:
                score += 0.20

            if request.completedJourneySteps < request.totalJourneySteps:
                score += 0.10

            score = min(max(score, 0.0), 1.0)

        if score > 0.7:
            risk_level = "high"
        elif score >= 0.4:
            risk_level = "medium"
        else:
            risk_level = "low"

        return ChurnResponse(
            userId=request.userId.strip(),
            score=round(score, 4),
            riskLevel=risk_level,
        )
<<<<<<< HEAD
=======

    def explain_risk(
        self,
        request: ChurnRequest,
    ) -> list[dict[str, Any]]:
        """
        Explain the existing churn-score factors.

        This method does not modify or call the existing
        scoring logic. It reports the same factors and
        contributions used by calculate().
        """

        if not request.userId.strip():
            raise ValueError("userId cannot be empty")

        factors: list[dict[str, Any]] = []

        # Backward-compatible feature-based format
        if request.features is not None:
            features = request.features

            days_since_registration = int(
                features.get(
                    "days_since_registration",
                    0,
                )
            )

            notification_open_rate = float(
                features.get(
                    "notification_open_rate_30d",
                    0.0,
                )
            )

            paper_trades_total = int(
                features.get(
                    "paper_trades_total",
                    0,
                )
            )

            paper_trades_7d = int(
                features.get(
                    "paper_trades_7d",
                    0,
                )
            )

            has_real_investment = bool(
                features.get(
                    "has_real_investment",
                    False,
                )
            )

            if days_since_registration <= 14:
                factors.append(
                    {
                        "factor": "New user",
                        "contribution": 0.20,
                    }
                )

            if notification_open_rate < 0.20:
                factors.append(
                    {
                        "factor": "Low notification engagement",
                        "contribution": 0.15,
                    }
                )

            if paper_trades_total == 0:
                factors.append(
                    {
                        "factor": "No paper trades",
                        "contribution": 0.20,
                    }
                )

            if paper_trades_7d == 0:
                factors.append(
                    {
                        "factor": "No paper trades in the last 7 days",
                        "contribution": 0.20,
                    }
                )

            if not has_real_investment:
                factors.append(
                    {
                        "factor": "No real investment",
                        "contribution": 0.20,
                    }
                )

        # New API format
        else:
            if request.daysSinceRegistration <= 14:
                factors.append(
                    {
                        "factor": "Recently registered",
                        "contribution": 0.20,
                    }
                )

            if request.sessionCount7d == 0:
                factors.append(
                    {
                        "factor": "No sessions in the last 7 days",
                        "contribution": 0.20,
                    }
                )

            if request.completedJourneySteps == 0:
                factors.append(
                    {
                        "factor": "No completed journey steps",
                        "contribution": 0.20,
                    }
                )

            if request.daysSinceLastActivity >= 7:
                factors.append(
                    {
                        "factor": "Inactive for at least 7 days",
                        "contribution": 0.20,
                    }
                )

            if (
                request.completedJourneySteps
                < request.totalJourneySteps
            ):
                factors.append(
                    {
                        "factor": "Incomplete journey",
                        "contribution": 0.10,
                    }
                )

        return factors
>>>>>>> srikanth_paise_wise_aiml
