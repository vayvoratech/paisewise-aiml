"""
Week 10 task: "Generate synthetic training data: create 10,000 normal
transactions and 500 anomaly examples."

Writes data/fraud_synthetic_data.csv with the 7 fraud-model features
plus a `label` column ("normal" or "anomaly") and a `category` column
(which of the 5 categories an anomaly belongs to, blank for normal
rows).
"""

import csv
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_FILE = ROOT / "data" / "fraud_synthetic_data.csv"

NORMAL_COUNT = 10_000
ANOMALY_COUNT = 500

FIELDNAMES = [
    "device_changed",
    "location_changed",
    "time_since_registration",
    "order_value",
    "orders_last_30min",
    "failed_mpin_count_24hr",
    "login_count_today",
    "label",
    "category",
]


def make_normal_row():
    return {
        "device_changed": random.random() < 0.05,
        "location_changed": random.random() < 0.02,
        "time_since_registration": random.randint(8, 2000),
        "order_value": round(random.uniform(500, 40000), 2),
        "orders_last_30min": random.randint(0, 4),
        "failed_mpin_count_24hr": random.randint(0, 1),
        "login_count_today": random.randint(1, 5),
        "label": "normal",
        "category": "",
    }


def make_account_takeover_row():
    return {
        "device_changed": True,
        "location_changed": random.random() < 0.5,
        "time_since_registration": random.randint(30, 2000),
        "order_value": round(random.uniform(50001, 200000), 2),
        "orders_last_30min": random.randint(0, 3),
        "failed_mpin_count_24hr": random.randint(0, 1),
        "login_count_today": 1,
        "label": "anomaly",
        "category": "account_takeover",
    }


def make_unusual_velocity_row():
    return {
        "device_changed": random.random() < 0.3,
        "location_changed": False,
        "time_since_registration": random.randint(30, 2000),
        "order_value": round(random.uniform(500, 20000), 2),
        "orders_last_30min": random.randint(10, 25),
        "failed_mpin_count_24hr": random.randint(0, 1),
        "login_count_today": random.randint(1, 3),
        "label": "anomaly",
        "category": "unusual_trading_velocity",
    }


def make_new_account_large_order_row():
    return {
        "device_changed": random.random() < 0.3,
        "location_changed": random.random() < 0.1,
        "time_since_registration": random.randint(0, 6),
        "order_value": round(random.uniform(50001, 150000), 2),
        "orders_last_30min": random.randint(0, 3),
        "failed_mpin_count_24hr": random.randint(0, 1),
        "login_count_today": random.randint(1, 3),
        "label": "anomaly",
        "category": "new_account_large_order",
    }


def make_impossible_location_row():
    return {
        "device_changed": random.random() < 0.4,
        "location_changed": True,
        "time_since_registration": random.randint(30, 2000),
        "order_value": round(random.uniform(500, 40000), 2),
        "orders_last_30min": random.randint(0, 3),
        "failed_mpin_count_24hr": random.randint(0, 1),
        "login_count_today": random.randint(2, 4),
        "label": "anomaly",
        "category": "impossible_location_change",
    }


def make_failed_mpin_row():
    return {
        "device_changed": random.random() < 0.3,
        "location_changed": random.random() < 0.2,
        "time_since_registration": random.randint(30, 2000),
        "order_value": round(random.uniform(50001, 180000), 2),
        "orders_last_30min": random.randint(0, 3),
        "failed_mpin_count_24hr": random.randint(3, 7),
        "login_count_today": random.randint(1, 3),
        "label": "anomaly",
        "category": "failed_mpin_then_large_order",
    }


ANOMALY_GENERATORS = [
    make_account_takeover_row,
    make_unusual_velocity_row,
    make_new_account_large_order_row,
    make_impossible_location_row,
    make_failed_mpin_row,
]


def generate_dataset(normal_count=NORMAL_COUNT, anomaly_count=ANOMALY_COUNT, seed=42):
    random.seed(seed)

    rows = [make_normal_row() for _ in range(normal_count)]

    # Spread the anomaly examples roughly evenly across the 5 categories.
    for i in range(anomaly_count):
        generator = ANOMALY_GENERATORS[i % len(ANOMALY_GENERATORS)]
        rows.append(generator())

    random.shuffle(rows)
    return rows


def save_dataset(rows, output_file=OUTPUT_FILE):
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with output_file.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    dataset = generate_dataset()
    save_dataset(dataset)

    normal_rows = sum(1 for row in dataset if row["label"] == "normal")
    anomaly_rows = sum(1 for row in dataset if row["label"] == "anomaly")

    print(f"Rows written: {len(dataset)}")
    print(f"Normal: {normal_rows}")
    print(f"Anomaly: {anomaly_rows}")
    print(f"Saved to: {OUTPUT_FILE}")
