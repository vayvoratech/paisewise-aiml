from app.services.fraud_detection import (
    evaluate_fraud_event,
    extract_fraud_features,
)


def test_extract_fraud_features_fills_defaults_for_missing_keys():
    features = extract_fraud_features({})

    assert features["device_changed"] is False
    assert features["order_value"] == 0
    assert features["failed_mpin_count_24hr"] == 0


def test_normal_event_is_not_an_anomaly():
    event = {
        "device_changed": False,
        "location_changed": False,
        "time_since_registration": 400,
        "order_value": 5000,
        "orders_last_30min": 2,
        "failed_mpin_count_24hr": 0,
        "login_count_today": 1,
    }

    result = evaluate_fraud_event(event)

    assert result["is_anomaly"] is False
    assert result["triggered_categories"] == []


def test_account_takeover_is_detected():
    event = {
        "device_changed": True,
        "order_value": 80000,
        "time_since_registration": 500,
    }

    result = evaluate_fraud_event(event)

    assert result["is_anomaly"] is True
    assert "account_takeover" in result["triggered_categories"]


def test_unusual_trading_velocity_is_detected():
    event = {"orders_last_30min": 15}

    result = evaluate_fraud_event(event)

    assert "unusual_trading_velocity" in result["triggered_categories"]


def test_new_account_large_order_is_detected():
    event = {"time_since_registration": 2, "order_value": 60000}

    result = evaluate_fraud_event(event)

    assert "new_account_large_order" in result["triggered_categories"]


def test_new_account_small_order_is_not_flagged():
    event = {"time_since_registration": 2, "order_value": 2000}

    result = evaluate_fraud_event(event)

    assert "new_account_large_order" not in result["triggered_categories"]
    assert result["is_anomaly"] is False


def test_impossible_location_change_is_detected():
    event = {"location_changed": True}

    result = evaluate_fraud_event(event)

    assert "impossible_location_change" in result["triggered_categories"]


def test_failed_mpin_then_large_order_is_detected():
    event = {
        "failed_mpin_count_24hr": 4,
        "login_count_today": 1,
        "order_value": 70000,
    }

    result = evaluate_fraud_event(event)

    assert "failed_mpin_then_large_order" in result["triggered_categories"]


def test_failed_mpin_alone_without_large_order_is_not_flagged():
    event = {
        "failed_mpin_count_24hr": 4,
        "login_count_today": 1,
        "order_value": 1000,
    }

    result = evaluate_fraud_event(event)

    assert "failed_mpin_then_large_order" not in result["triggered_categories"]


def test_event_can_trigger_multiple_categories_at_once():
    event = {
        "device_changed": True,
        "location_changed": True,
        "time_since_registration": 1,
        "order_value": 100000,
        "failed_mpin_count_24hr": 5,
        "login_count_today": 1,
    }

    result = evaluate_fraud_event(event)

    assert result["is_anomaly"] is True
    assert len(result["triggered_categories"]) >= 3
