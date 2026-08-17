from app.services.llm_service import generate_portfolio_response


def generate_fund_reason(
    fund_name,
    risk_level,
    category,
    user_risk,
    investment_horizon,
    user_goal=None,
    language="English",
):
    prompt = f"""
Give one simple reason why this mutual fund may match the user's profile.

Fund name: {fund_name}
Fund risk: {risk_level}
Category: {category}
User risk profile: {user_risk}
Investment horizon: {investment_horizon} years
User goal: {user_goal or "No goal provided"}

Use only the information above.
Give exactly one sentence.
Do not guarantee returns or predict future performance.
Do not make up missing information.
Respond only in {language}.
"""

    try:
        reason = generate_portfolio_response(prompt)
        if reason:
            return reason.strip()
    except Exception as error:
        print("Fund explanation error:", error)

    return "This fund matches the available fund characteristics and selected profile."
