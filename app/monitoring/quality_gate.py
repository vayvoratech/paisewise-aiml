from collections import defaultdict
from datetime import datetime


class QualityGate:
    ALERT_THRESHOLD = 3.5
    DISABLE_THRESHOLD = 3.0

    def evaluate(
        self,
        feature,
        score
    ):
        """
        Check the quality score and decide
        what action is needed.
        """

        if score < self.DISABLE_THRESHOLD:
            return {
                "feature": feature,
                "score": round(score, 2),
                "status": "disabled",
                "alert": True,
                "fallback": True,
                "message": (
                    f"{feature} quality is below 3.0. "
                    "Feature disabled and fallback activated."
                )
            }

        if score < self.ALERT_THRESHOLD:
            return {
                "feature": feature,
                "score": round(score, 2),
                "status": "warning",
                "alert": True,
                "fallback": False,
                "message": (
                    f"{feature} quality is below 3.5. "
                    "Team alert required."
                )
            }

        return {
            "feature": feature,
            "score": round(score, 2),
            "status": "healthy",
            "alert": False,
            "fallback": False,
            "message": (
                f"{feature} quality is healthy."
            )
        }

    def daily_feature_scores(
        self,
        records
    ):
        """
        Calculate the daily average quality score
        for each AI feature.
        """

        today = datetime.now().date()

        feature_scores = defaultdict(list)

        for record in records:
            timestamp = record.get("timestamp")

            if not timestamp:
                continue

            try:
                record_date = datetime.fromisoformat(
                    timestamp
                ).date()

            except ValueError:
                continue

            if record_date != today:
                continue

            feature = record.get("feature")
            score = record.get("score")

            if feature is None or score is None:
                continue

            feature_scores[feature].append(
                float(score)
            )

        result = {}

        for feature, scores in feature_scores.items():
            result[feature] = round(
                sum(scores) / len(scores),
                2
            )

        return result

    def evaluate_daily(
        self,
        records
    ):
        """
        Evaluate the daily average quality score
        for every AI feature.
        """

        daily_scores = self.daily_feature_scores(
            records
        )

        results = {}

        for feature, score in daily_scores.items():
            results[feature] = self.evaluate(
                feature,
                score
            )

        return results


if __name__ == "__main__":

    from quality_storage import QualityStorage

    print("=" * 60)
    print("AUTOMATIC DAILY QUALITY GATE")
    print("=" * 60)

    storage = QualityStorage()

    records = storage.get_records()

    gate = QualityGate()

    daily_scores = gate.daily_feature_scores(
        records
    )

    if not daily_scores:
        print("\nNo evaluation records found for today.")

    else:
        print("\nToday's Feature Scores:")

        for feature, score in daily_scores.items():
            print(
                f"{feature}: {score}/5"
            )

        print("\nQuality Gate Results:")

        results = gate.evaluate_daily(
            records
        )

        for feature, result in results.items():

            print(
                f"\nFeature: {feature}"
            )

            print(
                f"Daily Score: {result['score']}/5"
            )

            print(
                f"Status: {result['status']}"
            )

            print(
                f"Alert: {result['alert']}"
            )

            print(
                f"Fallback: {result['fallback']}"
            )

            print(
                f"Message: {result['message']}"
            )

    print("\n" + "=" * 60)
    print("QUALITY GATE TEST COMPLETED")
    print("=" * 60)