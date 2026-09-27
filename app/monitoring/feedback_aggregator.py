from collections import defaultdict
from datetime import datetime, timedelta


class FeedbackAggregator:

    def aggregate(
        self,
        feedback_records
    ):
        """
        Aggregate all feedback records by AI feature.
        """

        summary = defaultdict(
            lambda: {
                "total": 0,
                "positive": 0,
                "negative": 0
            }
        )

        for feedback in feedback_records:

            feature = feedback.get("feature")
            rating = feedback.get("rating")

            if not feature or not rating:
                continue

            summary[feature]["total"] += 1

            if rating == "up":
                summary[feature]["positive"] += 1

            elif rating == "down":
                summary[feature]["negative"] += 1

        result = {}

        for feature, data in summary.items():

            total = data["total"]

            positive_rate = (
                data["positive"] / total * 100
                if total > 0
                else 0
            )

            negative_rate = (
                data["negative"] / total * 100
                if total > 0
                else 0
            )

            result[feature] = {
                "total_feedback": total,
                "positive": data["positive"],
                "negative": data["negative"],
                "positive_rate": round(
                    positive_rate,
                    2
                ),
                "negative_rate": round(
                    negative_rate,
                    2
                )
            }

        return result

    def weekly_feedback(
        self,
        feedback_records
    ):
        """
        Aggregate feedback received during
        the last 7 days.
        """

        current_time = datetime.now()

        start_time = current_time - timedelta(
            days=7
        )

        weekly_records = []

        for feedback in feedback_records:

            timestamp = feedback.get(
                "timestamp"
            )

            if not timestamp:
                continue

            try:
                feedback_time = datetime.fromisoformat(
                    timestamp
                )

            except ValueError:
                continue

            if (
                start_time
                <= feedback_time
                <= current_time
            ):
                weekly_records.append(
                    feedback
                )

        return self.aggregate(
            weekly_records
        )


if __name__ == "__main__":

    print("=" * 60)
    print("WEEKLY USER FEEDBACK AGGREGATION")
    print("=" * 60)

    aggregator = FeedbackAggregator()

    current_time = datetime.now()

    feedback_records = [
        {
            "timestamp": current_time.isoformat(),
            "feature": "jargon",
            "rating": "up",
            "user_id": "U001"
        },
        {
            "timestamp": current_time.isoformat(),
            "feature": "jargon",
            "rating": "up",
            "user_id": "U002"
        },
        {
            "timestamp": current_time.isoformat(),
            "feature": "jargon",
            "rating": "down",
            "user_id": "U003"
        },
        {
            "timestamp": current_time.isoformat(),
            "feature": "portfolio",
            "rating": "up",
            "user_id": "U004"
        },
        {
            "timestamp": current_time.isoformat(),
            "feature": "portfolio",
            "rating": "down",
            "user_id": "U005"
        }
    ]

    print("\n1. ALL FEEDBACK")

    all_feedback = aggregator.aggregate(
        feedback_records
    )

    for feature, data in all_feedback.items():

        print(
            f"\nFeature: {feature}"
        )

        print(
            f"Total Feedback: "
            f"{data['total_feedback']}"
        )

        print(
            f"Positive: "
            f"{data['positive']}"
        )

        print(
            f"Negative: "
            f"{data['negative']}"
        )

        print(
            f"Positive Rate: "
            f"{data['positive_rate']}%"
        )

        print(
            f"Negative Rate: "
            f"{data['negative_rate']}%"
        )

    print("\n2. WEEKLY FEEDBACK")

    weekly_result = aggregator.weekly_feedback(
        feedback_records
    )

    for feature, data in weekly_result.items():

        print(
            f"\nFeature: {feature}"
        )

        print(
            f"Total Feedback: "
            f"{data['total_feedback']}"
        )

        print(
            f"Positive: "
            f"{data['positive']}"
        )

        print(  
            f"Negative: "
            f"{data['negative']}"
        )

        print(
            f"Positive Rate: "
            f"{data['positive_rate']}%"
        )

        print(
            f"Negative Rate: "
            f"{data['negative_rate']}%"
        )

    print("\n" + "=" * 60)
    print("FEEDBACK AGGREGATION TEST COMPLETED")
    print("=" * 60)