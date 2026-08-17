from app.services.fund_recommendation import (
    apply_week8_exclusions,
    calculate_fund_score,
    filter_funds_by_risk,
    get_top_recommendations,
)


def fund(
    name,
    risk,
    category,
    r1,
    r3,
    r5,
    expense,
    amc="AMC A",
    tax_saver=False,
):
    return {
        "scheme_name": name,
        "risk_level": risk,
        "category": category,
        "sub_category": category,
        "amc_name": amc,
        "returns_1y": r1,
        "returns_3y": r3,
        "returns_5y": r5,
        "expense_ratio": expense,
        "is_tax_saver": tax_saver,
        "min_lumpsum": 1000,
    }


def test_risk_filter_for_beginner_allows_low_and_moderate():
    funds = [
        fund("Low Fund", "Low", "Debt", 5, 6, 7, 0.5),
        fund("Moderate Fund", "Moderate", "Balanced", 8, 9, 10, 0.6),
        fund("High Fund", "High", "Equity", 12, 14, 15, 0.7),
    ]

    result = filter_funds_by_risk(funds, "Beginner")

    assert [item["scheme_name"] for item in result] == [
        "Low Fund",
        "Moderate Fund",
    ]


def test_intermediate_can_use_high_risk():
    funds = [
        fund("High Fund", "High", "Equity", 12, 14, 15, 0.7),
    ]

    assert len(filter_funds_by_risk(funds, "Intermediate")) == 1


def test_score_is_between_zero_and_hundred():
    value = calculate_fund_score(
        fund("Moderate Fund", "Moderate", "Balanced", 8, 9, 10, 0.6),
        "Moderate",
        5,
        "retirement",
    )

    assert 0 <= value <= 100


def test_beginner_expense_ratio_exclusion():
    funds = [
        fund("Expensive", "Low", "Debt", 10, 10, 10, 1.6),
        fund("Affordable", "Low", "Debt", 9, 9, 9, 1.2),
    ]

    result = apply_week8_exclusions(funds, "Beginner", 5)

    assert [item["scheme_name"] for item in result] == ["Affordable"]


def test_elss_is_excluded_for_short_horizon():
    funds = [
        fund("ELSS Fund", "Moderate", "Equity Tax Saver", 10, 10, 10, 0.8, tax_saver=True),
        fund("Debt Fund", "Low", "Debt", 7, 7, 7, 0.5),
    ]

    result = apply_week8_exclusions(funds, "Beginner", 2)

    assert [item["scheme_name"] for item in result] == ["Debt Fund"]


def test_top_three_prefer_different_categories_and_amcs():
    funds = [
        fund("Fund A", "Moderate", "Equity", 15, 15, 15, 0.5, "AMC A"),
        fund("Fund B", "Moderate", "Equity", 14, 14, 14, 0.5, "AMC A"),
        fund("Fund C", "Moderate", "Debt", 13, 13, 13, 0.5, "AMC B"),
        fund("Fund D", "Moderate", "Hybrid", 12, 12, 12, 0.5, "AMC C"),
    ]

    result = get_top_recommendations(
        funds,
        "Intermediate",
        5,
        100000,
        "retirement",
    )

    assert len(result) == 3
    categories = {item["fund"]["category"] for item in result}
    amcs = {item["fund"]["amc_name"] for item in result}
    assert len(categories) == 3
    assert len(amcs) == 3
