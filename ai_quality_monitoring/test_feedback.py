import json
from pathlib import Path

from feedback_aggregator import FeedbackAggregator


def test_feedback_aggregation():
    # Get feedback_data.json from the same folder as this test file
    feedback_file = Path(__file__).resolve().parent / "feedback_data.json"

    with open(feedback_file, "r", encoding="utf-8") as file:
        feedback_records = json.load(file)

    aggregator = FeedbackAggregator()

    result = aggregator.aggregate(feedback_records)

    # Basic validation
    assert result is not None

    print("User Feedback Summary:")
    print(result)