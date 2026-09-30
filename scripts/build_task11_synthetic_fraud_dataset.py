"""Build the Task 11 development-only synthetic fraud training dataset.

The dataset is a reproducible engineering fixture.  It does not contain real
orders or confirmed real-world fraud, and must never support production
fraud decisions.
"""

from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Any

from app.services.fraud_training_dataset_service import (
    FraudTrainingDatasetService,
)


RANDOM_SEED = 20260922
SAMPLES_PER_LABEL = 180
OUTPUT_PATH = Path("tests/data/task11_synthetic_fraud_training_dataset.json")


def _round_amount(shares: int, price_per_share: float) -> float:
    """Keep the monetary value exactly consistent with the generated order."""
    return round(shares * price_per_share, 2)


def _make_order(
    rng: random.Random,
    order_id: str,
    fraud_label: int,
    index: int,
) -> dict[str, Any]:
    """Create overlapping trading profiles with no single-feature label rule."""
    # Both labels deliberately contain BUY/SELL and MARKET/LIMIT orders, and
    # their quantity, price, and notional ranges overlap.  The label reflects
    # a simulated reviewer outcome for an overall behavioural profile, not a
    # threshold applied to an exported feature.
    profile = rng.randrange(4)

    if fraud_label == 0:
        profiles = (
            ("BUY", "MARKET", 1, 180, 75.0, 1_200.0),
            ("SELL", "LIMIT", 20, 1_100, 60.0, 2_800.0),
            ("BUY", "LIMIT", 80, 2_400, 110.0, 3_900.0),
            ("SELL", "MARKET", 5, 700, 45.0, 1_750.0),
        )
    else:
        profiles = (
            ("BUY", "MARKET", 30, 1_900, 85.0, 3_700.0),
            ("SELL", "MARKET", 10, 2_700, 55.0, 3_200.0),
            ("BUY", "LIMIT", 100, 3_100, 130.0, 4_200.0),
            ("SELL", "LIMIT", 50, 1_600, 70.0, 2_600.0),
        )

    side, order_type, min_shares, max_shares, min_price, max_price = (
        profiles[profile]
    )

    # Small deterministic variation avoids template-like duplicate records.
    shares = rng.randint(min_shares, max_shares) + (index % 7)
    price_per_share = round(
        rng.uniform(min_price, max_price) + ((index % 5) * 0.13),
        2,
    )

    return {
        "id": order_id,
        "shares": shares,
        "price_per_share": price_per_share,
        "total_amount": _round_amount(shares, price_per_share),
        "side": side,
        "order_type": order_type,
    }


def build_dataset() -> dict[str, Any]:
    """Return a reproducible, balanced development dataset payload."""
    rng = random.Random(RANDOM_SEED)
    rows: list[dict[str, Any]] = []

    for fraud_label in (0, 1):
        decision = "TRUE_FRAUD" if fraud_label else "FALSE_POSITIVE"

        for index in range(SAMPLES_PER_LABEL):
            order_id = f"synthetic-order-{decision.lower()}-{index:03d}"
            fraud_case = {
                "id": f"synthetic-case-{decision.lower()}-{index:03d}",
                "order_id": order_id,
                "reviewer_decision": decision,
            }
            order = _make_order(rng, order_id, fraud_label, index)
            training_record = FraudTrainingDatasetService.build_record(
                fraud_case,
                order,
            )

            rows.append(
                {
                    "fraud_case": fraud_case,
                    "order": order,
                    "training_record": training_record,
                }
            )

    rng.shuffle(rows)

    return {
        "dataset_name": "task11_synthetic_fraud_training",
        "version": "1.0",
        "status": "development_synthetic_only",
        "source": "synthetic_development",
        "random_seed": RANDOM_SEED,
        "production_decision_use": False,
        "description": (
            "Synthetic development data for exercising the Task 11 fraud "
            "training pipeline; it is not real fraud data."
        ),
        "limitations": (
            "Synthetic reviewer outcomes do not establish real-world fraud "
            "performance and must not be used for production decisions."
        ),
        "feature_names": [
            "shares",
            "price_per_share",
            "total_amount",
            "side_buy",
            "side_sell",
            "order_type_market",
            "order_type_limit",
        ],
        "label_mapping": {
            "TRUE_FRAUD": 1,
            "FALSE_POSITIVE": 0,
        },
        "records": rows,
    }


def main() -> None:
    payload = build_dataset()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(payload, indent=2) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
