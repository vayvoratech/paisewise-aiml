import json
from datetime import datetime, timedelta

from cost_storage import CostStorage


storage = CostStorage()

# Backup current records
original_records = storage._load_records()

# Create test records
test_records = [
    {
        "timestamp": (
            datetime.now() - timedelta(days=91)
        ).isoformat(),
        "user_id": "TEST_OLD",
        "feature": "test",
        "cost_inr": 1.0
    },
    {
        "timestamp": (
            datetime.now() - timedelta(days=10)
        ).isoformat(),
        "user_id": "TEST_RECENT",
        "feature": "test",
        "cost_inr": 1.0
    }
]

# Save test records
storage._save_records(test_records)

# Load records - retention should remove the 91-day-old record
cleaned_records = storage.get_records()

print("Retention test results:")
print("Records after cleanup:", len(cleaned_records))

for record in cleaned_records:
    print(
        record["user_id"],
        record["timestamp"]
    )

# Restore original records
storage._save_records(original_records)

print("\nOriginal records restored.")