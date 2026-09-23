from datetime import datetime, timedelta


class QualityImprovement:

    LOW_SCORE_THRESHOLD = 3.5

    def find_low_quality(
        self,
        evaluation_records
    ):
        """
        Find all evaluation records with a
        quality score below 3.5.
        """

        flagged = []

        for record in evaluation_records:

            score = record.get("score")

            if score is None:
                continue

            if float(score) < self.LOW_SCORE_THRESHOLD:

                flagged.append({
                    "timestamp": record.get(
                        "timestamp"
                    ),
                    "feature": record.get(
                        "feature"
                    ),
                    "score": float(score),
                    "reason": record.get(
                        "reason"
                    ),
                    "user_id": record.get(
                        "user_id"
                    ),
                    "response_id": record.get(
                        "response_id"
                    ),
                    "action": "Review prompt"
                })

        return flagged

    def find_weekly_low_quality(
        self,
        evaluation_records
    ):
        """
        Find low-quality responses from
        the last 7 days.
        """

        current_time = datetime.now()

        start_time = current_time - timedelta(
            days=7
        )

        weekly_records = []

        for record in evaluation_records:

            timestamp = record.get(
                "timestamp"
            )

            if not timestamp:
                continue

            try:
                record_time = datetime.fromisoformat(
                    timestamp
                )

            except ValueError:
                continue

            if (
                start_time
                <= record_time
                <= current_time
            ):
                weekly_records.append(
                    record
                )

        return self.find_low_quality(
            weekly_records
        )

    def create_weekly_review(
        self,
        evaluation_records
    ):
        """
        Create the weekly quality improvement
        review for the team.
        """

        flagged = self.find_weekly_low_quality(
            evaluation_records
        )

        return {
            "review_period": "Last 7 days",
            "total_flagged": len(flagged),
            "status": (
                "Review required"
                if flagged
                else "No major issues"
            ),
            "flagged_responses": flagged
        }


if __name__ == "__main__":

    print("=" * 60)
    print("WEEKLY QUALITY IMPROVEMENT WORKFLOW")
    print("=" * 60)

    improvement = QualityImprovement()

    current_time = datetime.now()

    evaluation_records = [
        {
            "timestamp": current_time.isoformat(),
            "feature": "jargon",
            "score": 4.5,
            "reason": "Clear and accurate response.",
            "user_id": "U001",
            "response_id": "R001"
        },
        {
            "timestamp": current_time.isoformat(),
            "feature": "portfolio",
            "score": 3.2,
            "reason": "Response needs more explanation.",
            "user_id": "U002",
            "response_id": "R002"
        },
        {
            "timestamp": current_time.isoformat(),
            "feature": "market_context",
            "score": 2.7,
            "reason": "Response was incomplete.",
            "user_id": "U003",
            "response_id": "R003"
        }
    ]

    print("\n1. FINDING LOW-QUALITY RESPONSES")

    flagged = improvement.find_low_quality(
        evaluation_records
    )

    print(
        "Total flagged:",
        len(flagged)
    )

    for record in flagged:

        print(
            f"\nFeature: {record['feature']}"
        )

        print(
            f"Score: {record['score']}/5"
        )

        print(
            f"Reason: {record['reason']}"
        )

        print(
            f"Action: {record['action']}"
        )

    print("\n2. WEEKLY REVIEW")

    weekly_review = improvement.create_weekly_review(
        evaluation_records
    )

    print(
        "Review Period:",
        weekly_review["review_period"]
    )

    print(
        "Total Flagged:",
        weekly_review["total_flagged"]
    )

    print(
        "Status:",
        weekly_review["status"]
    )

    if weekly_review["flagged_responses"]:

        print("\nResponses for Prompt Review:")

        for record in weekly_review[
            "flagged_responses"
        ]:

            print(
                f"- {record['feature']} "
                f"({record['score']}/5) "
                f"→ {record['action']}"
            )

    else:

        print(
            "\nNo low-quality responses "
            "require review."
        )

    print("\n" + "=" * 60)
    print("QUALITY IMPROVEMENT TEST COMPLETED")
    print("=" * 60)