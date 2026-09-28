from dataclasses import dataclass
from typing import Any

from app.services.fraud_decision_policy import (
    FraudDecision,
    FraudDecisionPolicy,
)
from app.services.fraud_feature_service import FraudFeatureService
from app.services.fraud_model_service import FraudModelService


@dataclass(frozen=True)
class FraudScoreResult:
    fraud_probability: float
    decision: FraudDecision


class FraudScoringService:
    def __init__(
        self,
        model_service: FraudModelService,
        decision_policy: FraudDecisionPolicy,
    ):
        if model_service is None:
            raise ValueError("model_service cannot be None")

        if decision_policy is None:
            raise ValueError("decision_policy cannot be None")

        self._model_service = model_service
        self._decision_policy = decision_policy

    def score_order(
        self,
        order: dict[str, Any],
    ) -> FraudScoreResult:
        features = FraudFeatureService.extract_features(order)

        fraud_probability = (
            self._model_service.predict_fraud_probability(
                features
            )
        )

        decision = self._decision_policy.decide(
            fraud_probability
        )

        return FraudScoreResult(
            fraud_probability=fraud_probability,
            decision=decision,
        )