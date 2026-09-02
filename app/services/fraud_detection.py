from typing import Dict, List

# Thresholds used by the rules below.
#  Kept as named constants so they
# are easy to find and tune later instead of being buried as magic
# numbers inside the functions.

LARGE_ORDER_VALUE = 50_000
NEW_ACCOUNT_DAYS = 7
VELOCITY_ORDERS_30MIN = 10  # see note in week10_fraud_anomaly_categories.md
FAILED_MPIN_THRESHOLD = 3


def extract_fraud_features(event: Dict) -> Dict:
    
    return {
        "device_changed": bool(event.get("device_changed", False)),
        "location_changed": bool(event.get("location_changed", False)),
        "time_since_registration": event.get("time_since_registration", 9999),
        "order_value": event.get("order_value", 0),
        "orders_last_30min": event.get("orders_last_30min", 0),
        "failed_mpin_count_24hr": event.get("failed_mpin_count_24hr", 0),
        "login_count_today": event.get("login_count_today", 0),
    }


def check_account_takeover(features: Dict) -> bool:
    #Category 1: new device + large withdrawal same day.
    return features["device_changed"] and features["order_value"] > LARGE_ORDER_VALUE


def check_unusual_trading_velocity(features: Dict) -> bool:
    #Category 2: too many orders in a short window.
    return features["orders_last_30min"] >= VELOCITY_ORDERS_30MIN


def check_new_account_large_order(features: Dict) -> bool:
    #Category 3: account under 7 days old placing an order over INR 50,000.
    return (
        features["time_since_registration"] < NEW_ACCOUNT_DAYS
        and features["order_value"] > LARGE_ORDER_VALUE
    )


def check_impossible_location_change(features: Dict) -> bool:
    #Category 4: login from a city that is not geographically possible
    #given how recently the user logged in from a different city.
    return features["location_changed"]


def check_failed_mpin_then_large_order(features: Dict) -> bool:
    #Category 5: multiple failed MPIN attempts, then a big order.
    return (
        features["failed_mpin_count_24hr"] >= FAILED_MPIN_THRESHOLD
        and features["login_count_today"] >= 1
        and features["order_value"] > LARGE_ORDER_VALUE
    )


CATEGORY_CHECKS = {
    "account_takeover": check_account_takeover,
    "unusual_trading_velocity": check_unusual_trading_velocity,
    "new_account_large_order": check_new_account_large_order,
    "impossible_location_change": check_impossible_location_change,
    "failed_mpin_then_large_order": check_failed_mpin_then_large_order,
}


def evaluate_fraud_event(event: Dict) -> Dict:
    # Run all 5 category checks against one event.

    # Returns the extracted features, which categories triggered, and
    # whether the event should be treated as an anomaly.


    features = extract_fraud_features(event)

    triggered: List[str] = [
        name for name, check in CATEGORY_CHECKS.items() if check(features)
    ]

    return {
        "features": features,
        "triggered_categories": triggered,
        "is_anomaly": len(triggered) > 0,
    }
