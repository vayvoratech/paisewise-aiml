import pytest

from app.services.fraud_feature_service import FraudFeatureService


def test_extract_features_buy_market_order():
    order = {
        "shares": 10,
        "price_per_share": 2500.0,
        "total_amount": 25000.0,
        "side": "BUY",
        "order_type": "MARKET",
    }

    features = FraudFeatureService.extract_features(order)

    assert features == [
        10.0,
        2500.0,
        25000.0,
        1.0,
        0.0,
        1.0,
        0.0,
    ]


def test_extract_features_sell_limit_order():
    order = {
        "shares": 5,
        "price_per_share": 1500.0,
        "total_amount": 7500.0,
        "side": "SELL",
        "order_type": "LIMIT",
    }

    features = FraudFeatureService.extract_features(order)

    assert features == [
        5.0,
        1500.0,
        7500.0,
        0.0,
        1.0,
        0.0,
        1.0,
    ]


def test_feature_names_match_feature_vector():
    order = {
        "shares": 10,
        "price_per_share": 2500.0,
        "total_amount": 25000.0,
        "side": "BUY",
        "order_type": "MARKET",
    }

    features = FraudFeatureService.extract_features(order)

    assert len(features) == len(FraudFeatureService.FEATURE_NAMES)
    assert len(features) == 7


def test_missing_required_field_is_rejected():
    order = {
        "shares": 10,
        "price_per_share": 2500.0,
        "total_amount": 25000.0,
        "side": "BUY",
    }

    with pytest.raises(
        ValueError,
        match="Missing required order fields",
    ):
        FraudFeatureService.extract_features(order)


def test_invalid_numeric_type_is_rejected():
    order = {
        "shares": "10",
        "price_per_share": 2500.0,
        "total_amount": 25000.0,
        "side": "BUY",
        "order_type": "MARKET",
    }

    with pytest.raises(TypeError, match="shares must be numeric"):
        FraudFeatureService.extract_features(order)


@pytest.mark.parametrize(
    "field",
    [
        "shares",
        "price_per_share",
        "total_amount",
    ],
)
def test_non_positive_numeric_values_are_rejected(field):
    order = {
        "shares": 10,
        "price_per_share": 2500.0,
        "total_amount": 25000.0,
        "side": "BUY",
        "order_type": "MARKET",
    }

    order[field] = 0

    with pytest.raises(ValueError):
        FraudFeatureService.extract_features(order)


def test_invalid_side_is_rejected():
    order = {
        "shares": 10,
        "price_per_share": 2500.0,
        "total_amount": 25000.0,
        "side": "HOLD",
        "order_type": "MARKET",
    }

    with pytest.raises(
        ValueError,
        match="Unsupported order side",
    ):
        FraudFeatureService.extract_features(order)


def test_invalid_order_type_is_rejected():
    order = {
        "shares": 10,
        "price_per_share": 2500.0,
        "total_amount": 25000.0,
        "side": "BUY",
        "order_type": "STOP",
    }

    with pytest.raises(
        ValueError,
        match="Unsupported order type",
    ):
        FraudFeatureService.extract_features(order)


def test_lowercase_categories_are_normalized():
    order = {
        "shares": 10,
        "price_per_share": 2500.0,
        "total_amount": 25000.0,
        "side": "buy",
        "order_type": "market",
    }

    features = FraudFeatureService.extract_features(order)

    assert features[3] == 1.0
    assert features[4] == 0.0
    assert features[5] == 1.0
    assert features[6] == 0.0