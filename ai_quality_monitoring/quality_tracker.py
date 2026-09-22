from datetime import datetime


class QualityTracker:
    def create_record(
        self,
        feature,
        score,
        user_id=None,
        response_id=None,
        reason=None
    ):
        """
        Create one quality evaluation record.
        """

        return {
            "timestamp": datetime.now().isoformat(),
            "feature": feature,
            "score": float(score),
            "user_id": user_id,
            "response_id": response_id,
            "reason": reason
        }

    def create_record_from_evaluation(
        self,
        evaluation,
        user_id=None,
        response_id=None
    ):
        """
        Create a quality tracking record from the
        result returned by QualityEvaluator.
        """

        return self.create_record(
            feature=evaluation["feature"],
            score=evaluation["score"],
            user_id=user_id,
            response_id=response_id,
            reason=evaluation.get("reason")
        )

    def average_score(self, records):
        """
        Calculate the average quality score.
        """

        if not records:
            return 0.0

        total_score = sum(
            record["score"]
            for record in records
        )

        return round(
            total_score / len(records),
            2
        )

    def feature_scores(self, records):
        """
        Calculate average score for each AI feature.
        """

        feature_data = {}

        for record in records:
            feature = record["feature"]

            if feature not in feature_data:
                feature_data[feature] = []

            feature_data[feature].append(
                record["score"]
            )

        result = {}

        for feature, scores in feature_data.items():
            result[feature] = round(
                sum(scores) / len(scores),
                2
            )

        return result


if __name__ == "__main__":

    from quality_evaluator import QualityEvaluator

    evaluator = QualityEvaluator()
    tracker = QualityTracker()

    prompt = "What is diversification in investing?"

    ai_response = (
        "Diversification means spreading your investments "
        "across different assets or sectors so that the impact "
        "of poor performance in one investment can be reduced."
    )

    evaluation = evaluator.evaluate(
        feature="jargon",
        prompt=prompt,
        response=ai_response
    )

    record = tracker.create_record_from_evaluation(
        evaluation=evaluation,
        user_id="U001",
        response_id="R001"
    )

    print("=" * 60)
    print("QUALITY TRACKING WITH REAL GEMINI EVALUATION")
    print("=" * 60)

    print("Feature:", record["feature"])
    print("Score:", record["score"], "/ 5")
    print("Reason:", record["reason"])
    print("User ID:", record["user_id"])
    print("Response ID:", record["response_id"])
    print("Timestamp:", record["timestamp"])