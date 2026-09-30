# import time
# from unittest.mock import MagicMock, patch

# from fastapi.testclient import TestClient

# from app.main import app


# client = TestClient(app)

# ORDER_ID = "ae55f1d8-e767-4b28-b6a9-2bbe5cf58c80"


# def test_fraud_score_api_latency_under_200ms():
#     order = {
#         "id": ORDER_ID,
#         "user_id": "performance-user",
#         "symbol": "NSE:RELIANCE",
#         "side": "BUY",
#         "shares": 10,
#         "price_per_share": 2500.0,
#         "total_amount": 25000.0,
#         "order_type": "MARKET",
#         "xp_earned": 0,
#         "created_at": None,
#     }

#     fake_model = MagicMock()
#     fake_model.predict_proba.return_value = [[0.85, 0.15]]

#     with patch(
#         "app.api.routes.fraud.FraudOrderRepository"
#     ) as repository_class, patch(
#         "app.api.routes.fraud.fraud_runtime"
#     ) as runtime:

#         repository = MagicMock()
#         repository.get_order_by_id.return_value = order
#         repository_class.return_value = repository

#         runtime_service = MagicMock()
#         runtime_service.model = fake_model
#         runtime.get_runtime.return_value = runtime_service

#         start = time.perf_counter()

#         response = client.post(
#             "/fraud/score",
#             json={"order_id": ORDER_ID},
#         )

#         elapsed_ms = (time.perf_counter() - start) * 1000

#     assert response.status_code == 200

#     data = response.json()

#     assert data["order_id"] == ORDER_ID
#     assert data["fraud_probability"] == 0.15
#     assert data["decision"] == "ALLOW"

#     print(f"\nFraud API latency: {elapsed_ms:.3f} ms")

#     assert elapsed_ms < 200.0

import time
from unittest.mock import MagicMock, patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.routes.fraud import router as fraud_router


# Keep this performance test focused on the fraud route.
# It avoids starting unrelated application services.
test_app = FastAPI()
test_app.include_router(fraud_router)

ORDER_ID = "ae55f1d8-e767-4b28-b6a9-2bbe5cf58c80"


def test_fraud_score_api_latency_under_200ms():
    order = {
        "id": ORDER_ID,
        "user_id": "performance-user",
        "symbol": "NSE:RELIANCE",
        "side": "BUY",
        "shares": 10,
        "price_per_share": 2500.0,
        "total_amount": 25000.0,
        "order_type": "MARKET",
        "xp_earned": 0,
        "created_at": None,
    }

    fake_model = MagicMock()
    fake_model.predict_proba.return_value = [[0.85, 0.15]]

    with patch(
        "app.api.routes.fraud.FraudOrderRepository"
    ) as repository_class, patch(
        "app.api.routes.fraud.fraud_runtime"
    ) as runtime:
        repository = MagicMock()
        repository.get_order_by_id.return_value = order
        repository_class.return_value = repository

        runtime_service = MagicMock()
        runtime_service.model = fake_model
        runtime.get_runtime.return_value = runtime_service

        # Entering TestClient starts its request portal before timing.
        with TestClient(test_app) as client:
            # Warm up the first request so startup overhead is excluded.
            warmup_response = client.post(
                "/fraud/score",
                json={"order_id": ORDER_ID},
            )
            assert warmup_response.status_code == 200

            start = time.perf_counter()

            response = client.post(
                "/fraud/score",
                json={"order_id": ORDER_ID},
            )

            elapsed_ms = (time.perf_counter() - start) * 1000

    assert response.status_code == 200

    data = response.json()

    assert data["order_id"] == ORDER_ID
    assert data["fraud_probability"] == 0.15
    assert data["decision"] == "ALLOW"

    print(f"\nFraud API latency: {elapsed_ms:.3f} ms")

    assert elapsed_ms < 200.0