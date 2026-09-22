import streamlit as st

from llm_cost_tracker import LLMCostTracker
from budget_monitor import BudgetMonitor
from cost_storage import CostStorage
from cost_report import MonthlyCostReport

from pricing_config import (
    USD_TO_INR,
    GEMINI_INPUT_INR_PER_1K,
    GEMINI_OUTPUT_INR_PER_1K
)


# --------------------------------------------------
# Page configuration
# --------------------------------------------------

st.set_page_config(
    page_title="PaiseWise LLM Cost Dashboard",
    layout="wide"
)

st.title("PaiseWise LLM Cost Dashboard")

st.caption(
    "LLM usage, token and cost monitoring"
)


# --------------------------------------------------
# Load stored records
# --------------------------------------------------

storage = CostStorage()

records = storage.get_records()


# --------------------------------------------------
# Monthly report
# --------------------------------------------------

monthly_report = MonthlyCostReport(
    records
)

report = monthly_report.generate_report()


# --------------------------------------------------
# Create tracker
# --------------------------------------------------

tracker = LLMCostTracker()


# --------------------------------------------------
# Load saved records into tracker
# --------------------------------------------------

for record in records:

    tracker.records.append(
        record
    )


# --------------------------------------------------
# Calculate total cost
# --------------------------------------------------

total_cost = tracker.get_total_cost()


# --------------------------------------------------
# Budget
# --------------------------------------------------

budget = BudgetMonitor()

budget.add_cost(
    total_cost
)

remaining = (
    budget.get_remaining_budget()
)


# --------------------------------------------------
# Top metrics
# --------------------------------------------------

col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "Total LLM Cost",
        f"₹{total_cost:.4f}"
    )


with col2:

    st.metric(
        "Daily Budget",
        "₹1,000"
    )


with col3:

    st.metric(
        "Remaining Budget",
        f"₹{remaining:.2f}"
    )


with col4:

    st.metric(
        "Usage Records",
        len(records)
    )


st.divider()


# --------------------------------------------------
# Gemini Pricing
# --------------------------------------------------

st.subheader(
    "Gemini Pricing Configuration"
)

pricing_col1, pricing_col2, pricing_col3 = (
    st.columns(3)
)


with pricing_col1:

    st.metric(
        "USD → INR",
        f"₹{USD_TO_INR:.2f}"
    )


with pricing_col2:

    st.metric(
        "Input / 1K Tokens",
        f"₹{GEMINI_INPUT_INR_PER_1K:.6f}"
    )


with pricing_col3:

    st.metric(
        "Output / 1K Tokens",
        f"₹{GEMINI_OUTPUT_INR_PER_1K:.6f}"
    )


st.caption(
    "Output pricing includes Gemini thinking tokens."
)


st.divider()


# --------------------------------------------------
# Cost by Feature
# --------------------------------------------------

st.subheader(
    "Cost by Feature"
)

feature_cost = (
    tracker.get_cost_by_feature()
)

if feature_cost:

    st.bar_chart(
        feature_cost
    )

else:

    st.info(
        "No LLM usage records available."
    )


# --------------------------------------------------
# Cost by User Tier
# --------------------------------------------------

st.subheader(
    "Cost by User Tier"
)

tier_cost = (
    tracker.get_cost_by_user_tier()
)

if tier_cost:

    st.bar_chart(
        tier_cost
    )

else:

    st.info(
        "No user tier data available."
    )


# --------------------------------------------------
# Daily Cost
# --------------------------------------------------

st.subheader(
    "Daily Cost Trend"
)

daily_cost = (
    tracker.get_cost_by_day()
)

if daily_cost:

    st.line_chart(
        daily_cost
    )

else:

    st.info(
        "No daily cost data available."
    )


# --------------------------------------------------
# Budget Status
# --------------------------------------------------

st.subheader(
    "Daily Budget Status"
)

if budget.DAILY_BUDGET > 0:

    percentage = (
        total_cost /
        budget.DAILY_BUDGET
    )

else:

    percentage = 0


st.progress(
    min(percentage, 1.0)
)

st.write(
    f"Budget used: "
    f"{percentage * 100:.2f}%"
)


# --------------------------------------------------
# Budget Thresholds
# --------------------------------------------------

st.write(
    "Budget thresholds: "
    "50% → Warning | "
    "80% → High Usage | "
    "100% → Budget Limit"
)


# --------------------------------------------------
# Alerts
# --------------------------------------------------

st.subheader(
    "Budget Alerts"
)

alerts = budget.check_budget()


if alerts:

    for alert in alerts:

        st.warning(
            alert
        )

else:

    st.success(
        "LLM usage is currently "
        "within the budget."
    )


# --------------------------------------------------
# Usage Records
# --------------------------------------------------

st.subheader(
    "LLM Usage Records"
)

if records:

    display_records = []

    for record in records:

        thinking_tokens = record.get(
            "thinking_tokens",
            0
        )

        output_tokens = record.get(
            "output_tokens",
            0
        )

        billable_output_tokens = (
            output_tokens
            + thinking_tokens
        )

        display_records.append(
            {
                "User":
                    record["user_id"],

                "Tier":
                    record["user_tier"],

                "Feature":
                    record["feature"],

                "Model":
                    record["model"],

                "Input Tokens":
                    record["input_tokens"],

                "Output Tokens":
                    output_tokens,

                "Thinking Tokens":
                    thinking_tokens,

                "Billable Output Tokens":
                    billable_output_tokens,

                "Total Tokens":
                    record["total_tokens"],

                "Cost (₹)":
                    record["cost_inr"],

                "Timestamp":
                    record["timestamp"]
            }
        )

    st.dataframe(
        display_records,
        use_container_width=True
    )

else:

    st.info(
        "No usage records available."
    )


# --------------------------------------------------
# Monthly Cost Report
# --------------------------------------------------

st.header(
    "Monthly Cost Report"
)


# --------------------------------------------------
# Total Reported Cost
# --------------------------------------------------

st.metric(
    "Total Reported Cost",
    f"₹{report['total_cost_inr']:.4f}"
)


# --------------------------------------------------
# Cost by Feature
# --------------------------------------------------

st.subheader(
    "Monthly Cost by Feature"
)

feature_data = (
    report["cost_by_feature"]
)

if feature_data:

    st.bar_chart(
        feature_data
    )

else:

    st.info(
        "No feature cost data available."
    )


# --------------------------------------------------
# Cost by User
# --------------------------------------------------

st.subheader(
    "Monthly Cost by User"
)

user_data = (
    report["cost_by_user"]
)

if user_data:

    st.bar_chart(
        user_data
    )

else:

    st.info(
        "No user cost data available."
    )


# --------------------------------------------------
# Cost by Month
# --------------------------------------------------

st.subheader(
    "Cost by Month"
)

month_data = (
    report["cost_by_month"]
)

if month_data:

    st.line_chart(
        month_data
    )

else:

    st.info(
        "No monthly cost data available."
    )