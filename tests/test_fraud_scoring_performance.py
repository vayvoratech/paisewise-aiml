import time

from app.services.fraud_decision_policy import FraudDecisionPolicy
from app.services.fraud_model_service import FraudModelService
from app.services.fraud_scoring_service import FraudScoringService


class FakeFraudModel:
    def predict_proba(self, features):
        return [[0.85, 0.15]]


ORDER = {
    "id": "performance-order",
    "user_id": "performance-user",
    "symbol": "NSE:RELIANCE",
    "side": "BUY",
    "shares": 10,
    "price_per_share": 2500.0,
    "total_amount": 25000.0,
    "order_type": "MARKET",
}


def test_fraud_scoring_latency_under_200ms():
    model_service = FraudModelService(FakeFraudModel())

    decision_policy = FraudDecisionPolicy(
        review_threshold=0.50,
        block_threshold=0.80,
    )

    scoring_service = FraudScoringService(
        model_service=model_service,
        decision_policy=decision_policy,
    )

    start = time.perf_counter()

    result = scoring_service.score_order(ORDER)

    elapsed_ms = (time.perf_counter() - start) * 1000

    assert result.fraud_probability == 0.15
    assert result.decision.value == "ALLOW"

    print(f"\nFraud scoring latency: {elapsed_ms:.3f} ms")

    assert elapsed_ms < 200.0