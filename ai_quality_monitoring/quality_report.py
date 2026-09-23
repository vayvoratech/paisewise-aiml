from collections import defaultdict
from datetime import datetime


class QualityReport:

    def __init__(
        self,
        records
    ):
        self.records = records

    def _get_datetime(
        self,
        timestamp
    ):
        """
        Convert a timestamp into a datetime object.
        """

        if isinstance(
            timestamp,
            datetime
        ):
            return timestamp

        if isinstance(
            timestamp,
            str
        ):
            try:
                return datetime.fromisoformat(
                    timestamp
                )

            except ValueError:
                return None

        return None

    def quality_by_feature(self):
        """
        Calculate average quality score
        for each AI feature.
        """

        data = defaultdict(list)

        for record in self.records:

            feature = record.get(
                "feature"
            )

            score = record.get(
                "score"
            )

            if feature is None or score is None:
                continue

            data[feature].append(
                float(score)
            )

        result = {}

        for feature, scores in data.items():

            result[feature] = round(
                sum(scores) / len(scores),
                2
            )

        return result

    def quality_by_month(self):
        """
        Calculate overall average quality
        score for each month.
        """

        data = defaultdict(list)

        for record in self.records:

            timestamp = self._get_datetime(
                record.get("timestamp")
            )

            if timestamp is None:
                continue

            score = record.get(
                "score"
            )

            if score is None:
                continue

            month = timestamp.strftime(
                "%Y-%m"
            )

            data[month].append(
                float(score)
            )

        result = {}

        for month, scores in data.items():

            result[month] = round(
                sum(scores) / len(scores),
                2
            )

        return result

    def quality_by_feature_and_month(self):
        """
        Calculate the average quality score
        for each feature for each month.
        """

        data = defaultdict(
            lambda: defaultdict(list)
        )

        for record in self.records:

            timestamp = self._get_datetime(
                record.get("timestamp")
            )

            if timestamp is None:
                continue

            feature = record.get(
                "feature"
            )

            score = record.get(
                "score"
            )

            if feature is None or score is None:
                continue

            month = timestamp.strftime(
                "%Y-%m"
            )

            data[month][feature].append(
                float(score)
            )

        result = {}

        for month, features in data.items():

            result[month] = {}

            for feature, scores in features.items():

                result[month][feature] = round(
                    sum(scores) / len(scores),
                    2
                )

        return result

    def generate_monthly_report(self):
        """
        Generate the monthly AI quality report
        required for product-owner review.
        """

        return {
            "quality_by_month": self.quality_by_month(),
            "quality_by_feature_and_month":
                self.quality_by_feature_and_month()
        }

    def generate_report(self):
        """
        Generate the complete AI quality report.
        """

        scores = []

        for record in self.records:

            score = record.get(
                "score"
            )

            if score is not None:
                scores.append(
                    float(score)
                )

        overall_score = (
            sum(scores) / len(scores)
            if scores
            else 0
        )

        return {
            "overall_quality_score": round(
                overall_score,
                2
            ),
            "quality_by_feature":
                self.quality_by_feature(),
            "quality_by_month":
                self.quality_by_month(),
            "quality_by_feature_and_month":
                self.quality_by_feature_and_month(),
            "total_evaluations":
                len(self.records)
        }


if __name__ == "__main__":

    print("=" * 60)
    print("MONTHLY AI QUALITY REPORT")
    print("=" * 60)

    from quality_storage import QualityStorage

    storage = QualityStorage()

    records = storage.get_records()

    report = QualityReport(
        records
    )

    result = report.generate_report()

    print("\n1. OVERALL QUALITY")

    print(
        "Overall Quality Score:",
        result["overall_quality_score"],
        "/ 5"
    )

    print(
        "Total Evaluations:",
        result["total_evaluations"]
    )

    print("\n2. QUALITY BY FEATURE")

    if result["quality_by_feature"]:

        for feature, score in result[
            "quality_by_feature"
        ].items():

            print(
                f"{feature}: {score}/5"
            )

    else:

        print(
            "No feature evaluation data available."
        )

    print("\n3. QUALITY BY MONTH")

    if result["quality_by_month"]:

        for month, score in result[
            "quality_by_month"
        ].items():

            print(
                f"{month}: {score}/5"
            )

    else:

        print(
            "No monthly evaluation data available."
        )

    print(
        "\n4. FEATURE-BY-FEATURE MONTHLY TREND"
    )

    monthly_trend = result[
        "quality_by_feature_and_month"
    ]

    if monthly_trend:

        for month, features in monthly_trend.items():

            print(
                f"\nMonth: {month}"
            )

            for feature, score in features.items():

                print(
                    f"  {feature}: {score}/5"
                )

    else:

        print(
            "No monthly feature trend available."
        )

    print("\n" + "=" * 60)
    print("QUALITY REPORT TEST COMPLETED")
    print("=" * 60)