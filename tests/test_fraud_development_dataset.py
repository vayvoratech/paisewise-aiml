import json
from pathlib import Path


DATASET_PATH = (
    Path(__file__).resolve().parent
    / "data"
    / "fraud_development_dataset.json"
)


EXPECTED_FEATURES = [
    "shares",
    "price_per_share",
    "total_amount",
    "side_buy",
    "side_sell",
    "order_type_market",
    "order_type_limit",
]


def load_dataset():
    with DATASET_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def test_dataset_metadata():
    dataset = load_dataset()

    assert dataset["environment"] == "development"
    assert dataset["data_source"] == "synthetic"
    assert dataset["production_use"] is False


def test_dataset_size_and_class_balance():
    dataset = load_dataset()
    records = dataset["records"]

    assert len(records) == 200
    assert dataset["total_samples"] == 200

    true_fraud = sum(
        record["fraud_label"] == 1
        for record in records
    )

    false_positive = sum(
        record["fraud_label"] == 0
        for record in records
    )

    assert true_fraud == 100
    assert false_positive == 100

    assert dataset["true_fraud_samples"] == 100
    assert dataset["false_positive_samples"] == 100


def test_case_ids_are_unique():
    dataset = load_dataset()

    case_ids = [
        record["case_id"]
        for record in dataset["records"]
    ]

    assert len(case_ids) == len(set(case_ids))


def test_feature_schema():
    dataset = load_dataset()

    assert dataset["feature_names"] == EXPECTED_FEATURES

    for record in dataset["records"]:
        assert len(record["features"]) == 7


def test_transaction_amounts_are_consistent():
    dataset = load_dataset()

    for record in dataset["records"]:
        features = record["features"]

        shares = features[0]
        price_per_share = features[1]
        total_amount = features[2]

        expected_total = round(
            shares * price_per_share,
            2,
        )

        assert shares > 0
        assert price_per_share > 0
        assert total_amount > 0

        assert abs(
            total_amount - expected_total
        ) <= 0.01


def test_side_encoding_is_valid():
    dataset = load_dataset()

    for record in dataset["records"]:
        features = record["features"]

        side_buy = features[3]
        side_sell = features[4]

        assert side_buy in (0.0, 1.0)
        assert side_sell in (0.0, 1.0)

        assert side_buy + side_sell == 1.0


def test_order_type_encoding_is_valid():
    dataset = load_dataset()

    for record in dataset["records"]:
        features = record["features"]

        market = features[5]
        limit = features[6]

        assert market in (0.0, 1.0)
        assert limit in (0.0, 1.0)

        assert market + limit == 1.0


def test_labels_and_reviewer_decisions_match():
    dataset = load_dataset()

    for record in dataset["records"]:
        label = record["fraud_label"]
        decision = record["reviewer_decision"]

        assert label in (0, 1)

        if label == 1:
            assert decision == "TRUE_FRAUD"
        else:
            assert decision == "FALSE_POSITIVE"


def test_all_records_have_required_fields():
    dataset = load_dataset()

    required_fields = {
        "case_id",
        "features",
        "fraud_label",
        "reviewer_decision",
    }

    for record in dataset["records"]:
        assert required_fields.issubset(
            record.keys()
        )