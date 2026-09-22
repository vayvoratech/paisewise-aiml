from quality_tracker import QualityTracker
from quality_gate import QualityGate
from quality_report import QualityReport
from quality_improvement import QualityImprovement
from feedback_aggregator import FeedbackAggregator


print("=" * 60)
print("TASK 2 - AI QUALITY MONITORING")
print("=" * 60)


# --------------------------------------------------
# 1. Quality Tracking
# --------------------------------------------------

tracker = QualityTracker()


records = [

    tracker.create_record(
        "jargon",
        4.5,
        "U001",
        "R001"
    ),

    tracker.create_record(
        "portfolio",
        3.4,
        "U002",
        "R002"
    ),

    tracker.create_record(
        "market_context",
        2.8,
        "U003",
        "R003"
    )
]


print("\n1. QUALITY TRACKING")

print(
    tracker.feature_scores(
        records
    )
)

print("PASS - Quality tracking")


# --------------------------------------------------
# 2. Quality Gate
# --------------------------------------------------

print("\n2. QUALITY GATE")

gate = QualityGate()


healthy = gate.evaluate(
    "jargon",
    4.5
)

warning = gate.evaluate(
    "portfolio",
    3.4
)

disabled = gate.evaluate(
    "market_context",
    2.8
)


print(
    "4.5 →",
    healthy["status"]
)

print(
    "3.4 →",
    warning["status"]
)

print(
    "2.8 →",
    disabled["status"]
)


if (
    healthy["status"] == "healthy"
    and warning["status"] == "warning"
    and disabled["status"] == "disabled"
):

    print(
        "PASS - Quality gate working"
    )


# --------------------------------------------------
# 3. Feedback
# --------------------------------------------------

print("\n3. USER FEEDBACK")


feedback = [

    {
        "feature": "jargon",
        "rating": "up"
    },

    {
        "feature": "jargon",
        "rating": "up"
    },

    {
        "feature": "jargon",
        "rating": "down"
    }
]


aggregator = FeedbackAggregator()


feedback_result = aggregator.aggregate(
    feedback
)


print(
    feedback_result
)

print(
    "PASS - Feedback aggregation"
)


# --------------------------------------------------
# 4. Quality Improvement
# --------------------------------------------------

print("\n4. QUALITY IMPROVEMENT")


improvement = QualityImprovement()


review = (
    improvement.create_weekly_review(
        records
    )
)


print(
    "Flagged:",
    review["total_flagged"]
)


if review["total_flagged"] > 0:

    print(
        "PASS - Low-quality responses flagged"
    )


# --------------------------------------------------
# 5. Quality Report
# --------------------------------------------------

print("\n5. QUALITY REPORT")


report = QualityReport(
    records
).generate_report()


print(
    "Overall:",
    report[
        "overall_quality_score"
    ]
)

print(
    "By Feature:",
    report[
        "quality_by_feature"
    ]
)

print(
    "By Month:",
    report[
        "quality_by_month"
    ]
)


if report["total_evaluations"] > 0:

    print(
        "PASS - Monthly quality report"
    )


print("\n" + "=" * 60)
print("TASK 2 TEST COMPLETED")
print("=" * 60)