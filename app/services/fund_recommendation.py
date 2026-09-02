from typing import Dict, List

from app.config.amc_reputation import get_amc_reputation_score


RISK_SCORES = {
    "low": {"low": 100, "moderate": 60, "high": 20},
    "moderate": {"low": 70, "moderate": 100, "high": 70},
    "high": {"low": 30, "moderate": 70, "high": 100},
}

# can update without changing the scoring code.
RETURN_WEIGHT = 0.4
RISK_WEIGHT = 0.3
EXPENSE_WEIGHT = 0.2
AMC_WEIGHT = 0.1

RISK_ALIASES = {
    "beginner": "low",
    "low": "low",
    "intermediate": "moderate",
    "moderate": "moderate",
    "advanced": "high",
    "high": "high",
}

GOAL_RULES = {
    "house purchase": ("balanced", "large cap"),
    "house": ("balanced", "large cap"),
    "retirement": ("equity", "debt"),
    "education": ("equity", "large cap"),
    "no goal": ("large cap", "conservative"),
}


def normalize_risk(risk: str) -> str:
    return RISK_ALIASES.get((risk or "").strip().lower(), "moderate")


def normalize_goal(goal: str | None) -> str:
    value = (goal or "no goal").strip().lower()
    return value if value in GOAL_RULES else "no goal"


def calculate_return_score(fund: Dict) -> float:
    returns = [
        fund.get("returns_1y"),
        fund.get("returns_3y"),
        fund.get("returns_5y"),
    ]
    valid_returns = [float(value) for value in returns if value is not None]

    if not valid_returns:
        return 50.0

    average_return = sum(valid_returns) / len(valid_returns)
    return round(min(max(average_return * 5, 0), 100), 2)


def calculate_risk_score(fund: Dict, user_risk: str) -> float:
    fund_risk = (fund.get("risk_level") or "").strip().lower()
    user_risk = normalize_risk(user_risk)
    return float(RISK_SCORES.get(user_risk, {}).get(fund_risk, 50))


def calculate_expense_score(fund: Dict) -> float:
    expense_ratio = fund.get("expense_ratio")

    if expense_ratio is None:
        return 50.0

    return round(min(max(100 - (float(expense_ratio) * 20), 0), 100), 2)


def calculate_amc_score(fund: Dict) -> float:

    # AMC reputation is not a column in mf_schemes, so this looks it up
    # from a manual tier list (app/config/amc_reputation.py) based on
    # the fund's amc_name. Unknown AMCs fall back to a neutral score
    # instead of guessing.
    return float(get_amc_reputation_score(fund.get("amc_name")))


def calculate_goal_score(fund: Dict, user_goal: str | None) -> float:
    goal = normalize_goal(user_goal)
    category = " ".join(
        str(fund.get(key) or "")
        for key in ("category", "sub_category", "scheme_type")
    ).lower()

    if goal == "retirement":
        return 100.0 if any(word in category for word in ("equity", "debt", "hybrid")) else 50.0

    preferred = GOAL_RULES[goal]
    if any(word in category for word in preferred):
        return 100.0
    if goal == "education" and any(word in category for word in ("equity", "index", "large cap", "flexi")):
        return 100.0
    return 60.0


def calculate_horizon_score(fund: Dict, investment_horizon: int) -> float:
    category = (fund.get("category") or "").lower()

    if investment_horizon <= 3:
        if any(word in category for word in ("debt", "liquid", "money market")):
            return 100.0
        return 60.0

    if investment_horizon >= 7:
        if any(word in category for word in ("equity", "large cap", "flexi cap", "index")):
            return 100.0
        return 70.0

    return 80.0


def calculate_fund_score(
    fund: Dict,
    user_risk: str,
    investment_horizon: int,
    user_goal: str | None = None,
    weights: Dict[str, float] | None = None,
) -> float:
    return_score = calculate_return_score(fund)
    risk_score = calculate_risk_score(fund, user_risk)
    expense_score = calculate_expense_score(fund)
    amc_score = calculate_amc_score(fund)

    weights = weights or {
        "return": RETURN_WEIGHT,
        "risk": RISK_WEIGHT,
        "expense": EXPENSE_WEIGHT,
        "amc": AMC_WEIGHT,
    }

    base_score = (
        (return_score * weights["return"])
        + (risk_score * weights["risk"])
        + (expense_score * weights["expense"])
        + (amc_score * weights["amc"])
    )

    # Goal and horizon are suitability tie-breakers. This keeps the
    # requested 40/30/20/10 score unchanged while still using the
    # required Week 7 goal/time-horizon information.
    suitability_adjustment = (
        (calculate_goal_score(fund, user_goal) - 50) * 0.05
        + (calculate_horizon_score(fund, investment_horizon) - 50) * 0.05
    )

    return round(min(max(base_score + suitability_adjustment, 0), 100), 2)


def filter_funds_by_risk(funds: List[Dict], user_risk: str) -> List[Dict]:
    raw = (user_risk or "").strip().lower()

    allowed_risks = {
        "low": ["low"],
        "moderate": ["low", "moderate"],
        "high": ["low", "moderate", "high"],
        "beginner": ["low", "moderate"],
        "intermediate": ["low", "moderate", "high"],
        "advanced": ["low", "moderate", "high"],
    }

    allowed = allowed_risks.get(raw, allowed_risks["moderate"])

    return [
        fund
        for fund in funds
        if (fund.get("risk_level") or "").strip().lower() in allowed
    ]


def apply_week8_exclusions(
    funds: List[Dict],
    user_risk: str,
    investment_horizon: int,
) -> List[Dict]:
    """Apply the explicit Week 8 safety/suitability exclusions."""
    normalized_risk = (user_risk or "").strip().lower()
    result = []

    for fund in funds:
        expense_ratio = fund.get("expense_ratio")
        if (
            normalized_risk == "beginner"
            and expense_ratio is not None
            and float(expense_ratio) > 1.5
        ):
            continue

        is_elss = bool(fund.get("is_tax_saver")) or "elss" in (
            f"{fund.get('scheme_name', '')} {fund.get('category', '')} {fund.get('sub_category', '')}"
        ).lower()

        if investment_horizon < 3 and is_elss:
            continue

        result.append(fund)

    return result


def select_diverse_top_three(scored_funds: List[Dict]) -> List[Dict]:
    """Prefer different categories and AMCs for the three final results."""
    selected = []
    used_categories = set()
    used_amcs = set()

    # First pass: maximize category + AMC diversity.
    for item in scored_funds:
        fund = item["fund"]
        category = str(fund.get("category") or "").strip().lower()
        amc = str(fund.get("amc_name") or "").strip().lower()

        if category in used_categories or amc in used_amcs:
            continue

        selected.append(item)
        used_categories.add(category)
        used_amcs.add(amc)

        if len(selected) == 3:
            return selected

    # Second pass: fill remaining slots if the catalogue cannot provide
    # full diversity. Never invent a fund just to satisfy the rule.
    
    for item in scored_funds:
        if item in selected:
            continue
        selected.append(item)
        if len(selected) == 3:
            break

    return selected


def get_top_recommendations(
    funds: List[Dict],
    user_risk: str,
    investment_horizon: int,
    investment_amount: float | None = None,
    user_goal: str | None = None,
    weights: Dict[str, float] | None = None,
) -> List[Dict]:
    filtered_funds = filter_funds_by_risk(funds, user_risk)

    filtered_funds = apply_week8_exclusions(
        filtered_funds,
        user_risk,
        investment_horizon,
    )

    if investment_amount is not None:
        eligible_funds = []
        for fund in filtered_funds:
            minimum = fund.get("min_lumpsum")
            if minimum is None or float(minimum) <= investment_amount:
                eligible_funds.append(fund)
        filtered_funds = eligible_funds

    scored_funds = []
    for fund in filtered_funds:
        score = calculate_fund_score(
            fund,
            user_risk,
            investment_horizon,
            user_goal,
            weights,
        )
        scored_funds.append({"fund": fund, "score": score})

    scored_funds.sort(key=lambda item: item["score"], reverse=True)

    return select_diverse_top_three(scored_funds)
