import json
from pathlib import Path

import streamlit as st

from quality_storage import QualityStorage
from quality_report import QualityReport
from quality_gate import QualityGate
from feedback_aggregator import FeedbackAggregator
from quality_improvement import QualityImprovement


# ==================================================
# PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="PaiseWise AI Quality Monitoring",
    layout="wide"
)


# ==================================================
# TITLE
# ==================================================

st.title(
    "PaiseWise AI Quality Monitoring"
)

st.caption(
    "Monitor AI quality scores, quality gates, "
    "user feedback, low-quality responses, "
    "and monthly quality trends."
)


# ==================================================
# REFRESH
# ==================================================

if st.button("Refresh Dashboard"):
    st.rerun()


# ==================================================
# LOAD EVALUATION RECORDS
# ==================================================

storage = QualityStorage()

records = storage.get_records()

report = QualityReport(
    records
).generate_report()


# ==================================================
# OVERALL QUALITY
# ==================================================

st.header(
    "Overall AI Quality"
)

col1, col2, col3 = st.columns(3)

col1.metric(
    "Overall Quality Score",
    f"{report['overall_quality_score']}/5.0"
)

col2.metric(
    "Total Evaluations",
    report["total_evaluations"]
)

if records:
    latest_score = records[-1].get(
        "score",
        0
    )

    col3.metric(
        "Latest Quality Score",
        f"{float(latest_score):.1f}/5.0"
    )
else:
    col3.metric(
        "Latest Quality Score",
        "N/A"
    )


# ==================================================
# QUALITY THRESHOLDS
# ==================================================

st.subheader(
    "Quality Gate Thresholds"
)

threshold_col1, threshold_col2, threshold_col3 = (
    st.columns(3)
)

threshold_col1.success(
    "Healthy: 3.5 or above"
)

threshold_col2.warning(
    "Warning: below 3.5"
)

threshold_col3.error(
    "Disabled / Fallback: below 3.0"
)


# ==================================================
# QUALITY BY FEATURE
# ==================================================

st.header(
    "Quality by Feature"
)

feature_data = report[
    "quality_by_feature"
]

if feature_data:

    st.bar_chart(
        feature_data
    )

    st.subheader(
        "Feature Quality Scores"
    )

    for feature, score in feature_data.items():

        if score >= 3.5:
            st.success(
                f"{feature}: {score}/5.0 - Healthy"
            )

        elif score >= 3.0:
            st.warning(
                f"{feature}: {score}/5.0 - Warning"
            )

        else:
            st.error(
                f"{feature}: {score}/5.0 - Disabled / Fallback"
            )

else:

    st.info(
        "No evaluation data available."
    )


# ==================================================
# QUALITY TREND
# ==================================================

st.header(
    "AI Quality Trend Over Time"
)

month_data = report[
    "quality_by_month"
]

if month_data:

    st.line_chart(
        month_data
    )

else:

    st.info(
        "No monthly quality data available."
    )


# ==================================================
# MONTHLY FEATURE TREND
# ==================================================

st.header(
    "Feature-wise Monthly Quality Trend"
)

monthly_feature_data = report[
    "quality_by_feature_and_month"
]

if monthly_feature_data:

    for month, features in (
        monthly_feature_data.items()
    ):

        st.subheader(
            f"Month: {month}"
        )

        st.bar_chart(
            features
        )

else:

    st.info(
        "No monthly feature trend available."
    )


# ==================================================
# DAILY QUALITY GATE
# ==================================================

st.header(
    "Daily Quality Gate Status"
)

gate = QualityGate()

daily_results = gate.evaluate_daily(
    records
)

if daily_results:

    for feature, result in (
        daily_results.items()
    ):

        status = result["status"]
        score = result["score"]

        if status == "healthy":

            st.success(
                f"{feature}: "
                f"{score}/5 - Healthy"
            )

        elif status == "warning":

            st.warning(
                f"{feature}: "
                f"{score}/5 - Alert Team"
            )

        else:

            st.error(
                f"{feature}: "
                f"{score}/5 - "
                "Feature Disabled / Fallback"
            )

else:

    st.info(
        "No quality evaluations available "
        "for today."
    )


# ==================================================
# QUALITY GATE SUMMARY
# ==================================================

st.subheader(
    "Quality Gate Summary"
)

if daily_results:

    healthy_count = 0
    warning_count = 0
    disabled_count = 0

    for result in daily_results.values():

        if result["status"] == "healthy":
            healthy_count += 1

        elif result["status"] == "warning":
            warning_count += 1

        elif result["status"] == "disabled":
            disabled_count += 1

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Healthy Features",
        healthy_count
    )

    col2.metric(
        "Warning Features",
        warning_count
    )

    col3.metric(
        "Disabled / Fallback",
        disabled_count
    )

else:

    st.info(
        "No daily quality gate data available."
    )


# ==================================================
# USER FEEDBACK
# ==================================================

st.header(
    "Weekly User Feedback"
)


feedback_file = (
    Path(__file__).resolve().parent
    / "feedback_data.json"
)


try:

    with open(
        feedback_file,
        "r",
        encoding="utf-8"
    ) as file:

        feedback_records = json.load(
            file
        )

except (
    FileNotFoundError,
    json.JSONDecodeError
):

    feedback_records = []


aggregator = FeedbackAggregator()

feedback_summary = (
    aggregator.weekly_feedback(
        feedback_records
    )
)


if feedback_summary:

    for feature, data in (
        feedback_summary.items()
    ):

        st.subheader(
            feature
        )

        col1, col2, col3, col4 = (
            st.columns(4)
        )

        col1.metric(
            "Total Feedback",
            data["total_feedback"]
        )

        col2.metric(
            "👍 Positive",
            data["positive"]
        )

        col3.metric(
            "👎 Negative",
            data["negative"]
        )

        col4.metric(
            "Positive Rate",
            f"{data['positive_rate']}%"
        )

else:

    st.info(
        "No user feedback available "
        "for the last 7 days."
    )


# ==================================================
# LOW-QUALITY RESPONSES
# ==================================================

st.header(
    "Weekly Low-Quality Response Review"
)

improvement = QualityImprovement()

weekly_review = (
    improvement.create_weekly_review(
        records
    )
)


col1, col2 = st.columns(2)

col1.metric(
    "Responses Flagged",
    weekly_review["total_flagged"]
)

col2.metric(
    "Review Status",
    weekly_review["status"]
)


if weekly_review["flagged_responses"]:

    st.dataframe(
        weekly_review["flagged_responses"],
        use_container_width=True
    )

else:

    st.success(
        "No low-quality responses "
        "require review."
    )


# ==================================================
# MONTHLY AI QUALITY REPORT
# ==================================================

st.header(
    "Monthly AI Quality Report"
)

monthly_report = (
    QualityReport(
        records
    ).generate_monthly_report()
)


if monthly_report[
    "quality_by_month"
]:

    for month, score in (
        monthly_report[
            "quality_by_month"
        ].items()
    ):

        st.write(
            f"**{month}**: "
            f"{score}/5.0"
        )

else:

    st.info(
        "No monthly report data available."
    )


# ==================================================
# DATA SUMMARY
# ==================================================

st.header(
    "Monitoring Data Summary"
)

summary_col1, summary_col2 = (
    st.columns(2)
)

summary_col1.metric(
    "Evaluation Records",
    len(records)
)

summary_col2.metric(
    "Feedback Records",
    len(feedback_records)
)


# ==================================================
# FOOTER
# ==================================================

st.divider()

st.caption(
    "PaiseWise AI Quality Monitoring | "
    "Quality scores are generated through "
    "AI response evaluation and monitored "
    "using defined quality-gate thresholds."
)