from __future__ import annotations

import json
import random
import uuid
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent

OUTPUT_PATH = (
    PROJECT_ROOT
    / "tests"
    / "data"
    / "fraud_development_dataset.json"
)

RANDOM_SEED = 42

TOTAL_SAMPLES = 200
TRUE_FRAUD_SAMPLES = 100
FALSE_POSITIVE_SAMPLES = 100

FEATURE_NAMES = [
    "shares",
    "price_per_share",
    "total_amount",
    "side_buy",
    "side_sell",
    "order_type_market",
    "order_type_limit",
]


def create_features(
    shares: float,
    price_per_share: float,
    side: str,
    order_type: str,
) -> list[float]:

    total_amount = round(
        shares * price_per_share,
        2,
    )

    return [
        float(shares),
        float(price_per_share),
        float(total_amount),
        1.0 if side == "BUY" else 0.0,
        1.0 if side == "SELL" else 0.0,
        1.0 if order_type == "MARKET" else 0.0,
        1.0 if order_type == "LIMIT" else 0.0,
    ]


def create_fraud_case(
    index: int,
    rng: random.Random,
) -> dict:

    # Fraudulent transactions intentionally overlap
    # with legitimate transaction ranges.

    shares = rng.randint(5, 100)

    price_per_share = round(
        rng.uniform(500, 5000),
        2,
    )

    side = rng.choice(
        ["BUY", "SELL"]
    )

    order_type = rng.choice(
        ["MARKET", "LIMIT"]
    )

    # Some fraud cases have elevated transaction size.
    # Others remain close to normal transactions.
    if index % 3 == 0:
        shares = rng.randint(50, 120)

    if index % 4 == 0:
        price_per_share = round(
            rng.uniform(2500, 6000),
            2,
        )

    return {
        "case_id": str(uuid.uuid4()),
        "features": create_features(
            shares=shares,
            price_per_share=price_per_share,
            side=side,
            order_type=order_type,
        ),
        "fraud_label": 1,
        "reviewer_decision": "TRUE_FRAUD",
    }


def create_false_positive_case(
    index: int,
    rng: random.Random,
) -> dict:

    # Legitimate transactions deliberately overlap
    # with fraud transaction ranges.

    shares = rng.randint(5, 100)

    price_per_share = round(
        rng.uniform(500, 5000),
        2,
    )

    side = rng.choice(
        ["BUY", "SELL"]
    )

    order_type = rng.choice(
        ["MARKET", "LIMIT"]
    )

    # Some legitimate transactions can also be large.
    if index % 4 == 0:
        shares = rng.randint(40, 110)

    if index % 5 == 0:
        price_per_share = round(
            rng.uniform(2500, 6000),
            2,
        )

    return {
        "case_id": str(uuid.uuid4()),
        "features": create_features(
            shares=shares,
            price_per_share=price_per_share,
            side=side,
            order_type=order_type,
        ),
        "fraud_label": 0,
        "reviewer_decision": "FALSE_POSITIVE",
    }


def validate_records(records: list[dict]) -> None:

    if len(records) != TOTAL_SAMPLES:
        raise ValueError(
            f"Expected {TOTAL_SAMPLES} records, "
            f"got {len(records)}"
        )

    true_fraud_count = sum(
        record["fraud_label"] == 1
        for record in records
    )

    false_positive_count = sum(
        record["fraud_label"] == 0
        for record in records
    )

    if true_fraud_count != TRUE_FRAUD_SAMPLES:
        raise ValueError(
            "Incorrect TRUE_FRAUD count."
        )

    if false_positive_count != FALSE_POSITIVE_SAMPLES:
        raise ValueError(
            "Incorrect FALSE_POSITIVE count."
        )

    for record in records:

        features = record["features"]

        if len(features) != 7:
            raise ValueError(
                "Every record must contain exactly 7 features."
            )

        shares = features[0]
        price_per_share = features[1]
        total_amount = features[2]

        if shares <= 0:
            raise ValueError(
                "Shares must be greater than zero."
            )

        if price_per_share <= 0:
            raise ValueError(
                "Price per share must be greater than zero."
            )

        expected_total = round(
            shares * price_per_share,
            2,
        )

        if abs(
            total_amount - expected_total
        ) > 0.01:
            raise ValueError(
                "Total amount calculation is invalid."
            )

        side_buy = features[3]
        side_sell = features[4]

        if side_buy not in (0.0, 1.0):
            raise ValueError(
                "Invalid BUY encoding."
            )

        if side_sell not in (0.0, 1.0):
            raise ValueError(
                "Invalid SELL encoding."
            )

        if side_buy + side_sell != 1.0:
            raise ValueError(
                "BUY/SELL encoding is invalid."
            )

        market = features[5]
        limit = features[6]

        if market not in (0.0, 1.0):
            raise ValueError(
                "Invalid MARKET encoding."
            )

        if limit not in (0.0, 1.0):
            raise ValueError(
                "Invalid LIMIT encoding."
            )

        if market + limit != 1.0:
            raise ValueError(
                "MARKET/LIMIT encoding is invalid."
            )


def generate_dataset() -> dict:

    rng = random.Random(
        RANDOM_SEED
    )

    records = []

    for index in range(
        TRUE_FRAUD_SAMPLES
    ):
        records.append(
            create_fraud_case(
                index=index,
                rng=rng,
            )
        )

    for index in range(
        FALSE_POSITIVE_SAMPLES
    ):
        records.append(
            create_false_positive_case(
                index=index,
                rng=rng,
            )
        )

    rng.shuffle(records)

    validate_records(records)

    return {
        "dataset_name": "fraud_development_dataset",
        "dataset_version": "1.0.1",
        "environment": "development",
        "data_source": "synthetic",
        "production_use": False,
        "total_samples": len(records),
        "true_fraud_samples": TRUE_FRAUD_SAMPLES,
        "false_positive_samples": FALSE_POSITIVE_SAMPLES,
        "feature_names": FEATURE_NAMES,
        "label_mapping": {
            "FALSE_POSITIVE": 0,
            "TRUE_FRAUD": 1,
        },
        "records": records,
    }


def main() -> None:

    dataset = generate_dataset()

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with OUTPUT_PATH.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            dataset,
            file,
            indent=2,
        )

    print("=" * 60)
    print(
        "FRAUD DEVELOPMENT DATASET GENERATED"
    )
    print("=" * 60)

    print(
        f"Output: {OUTPUT_PATH}"
    )

    print(
        f"Samples: {dataset['total_samples']}"
    )

    print(
        f"TRUE_FRAUD: "
        f"{dataset['true_fraud_samples']}"
    )

    print(
        f"FALSE_POSITIVE: "
        f"{dataset['false_positive_samples']}"
    )

    print(
        f"Features: "
        f"{len(dataset['feature_names'])}"
    )

    print(
        f"Production use: "
        f"{dataset['production_use']}"
    )

    print("=" * 60)


if __name__ == "__main__":
    main()