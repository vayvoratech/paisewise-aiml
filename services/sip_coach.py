import math
import random
from statistics import mean

DEFAULT_ANNUAL_RETURN = 10.0
MONTHS_PER_YEAR = 12
MONTE_CARLO_RUNS = 1000

SIP_COACH_PROMPT = """
You are a financial education coach.
Explain the user's SIP progress using the supplied numbers.
Use an encouraging tone, specific numbers and clear next steps.
Do not give buy/sell instructions, promise returns, or use financial-advice language.
This is educational guidance only.

SIP data:
{data}
""".strip()


def future_value_of_sip(monthly_sip: float, months: int, annual_return: float) -> float:
    rate = annual_return / 100 / MONTHS_PER_YEAR
    if rate == 0:
        return monthly_sip * months
    return monthly_sip * (((1 + rate) ** months - 1) / rate) * (1 + rate)


def required_monthly_sip(target_amount: float, current_amount: float, months: int, annual_return: float) -> float:
    rate = annual_return / 100 / MONTHS_PER_YEAR
    if months <= 0:
        return 0.0
    future_current = current_amount * ((1 + rate) ** months)
    remaining = max(target_amount - future_current, 0.0)
    if remaining == 0:
        return 0.0
    if rate == 0:
        return remaining / months
    factor = (((1 + rate) ** months - 1) / rate) * (1 + rate)
    return remaining / factor


def classify_sip_status(projected_amount: float, target_amount: float, current_amount: float) -> str:
    progress = projected_amount / target_amount if target_amount else 0
    if current_amount >= target_amount:
        return "goal_met"
    if progress >= 1.0:
        return "on_track"
    if progress >= 0.75:
        return "behind"
    if progress >= 0.50:
        return "way_behind"
    return "underfunded"


def monte_carlo_projection(monthly_sip: float, months: int, annual_return: float, runs: int = MONTE_CARLO_RUNS, seed: int = 42):
    rng = random.Random(seed)
    # A 10% long-term assumption is used by default. Volatility is simulated
    # around the assumption only for educational scenario analysis.
    annual_volatility = 0.12
    outcomes = []
    for _ in range(runs):
        annual_rate = max(-0.25, rng.gauss(annual_return / 100, annual_volatility))
        outcomes.append(future_value_of_sip(monthly_sip, months, annual_rate * 100))
    outcomes.sort()
    return {
        "runs": runs,
        "assumptionAnnualReturn": annual_return,
        "p10": round(outcomes[int(runs * 0.10)], 2),
        "median": round(outcomes[int(runs * 0.50)], 2),
        "p90": round(outcomes[int(runs * 0.90) - 1], 2),
        "average": round(mean(outcomes), 2),
    }


def build_coaching_analysis(monthly_sip, target_amount, current_amount, months, annual_return):
    projected = future_value_of_sip(monthly_sip, months, annual_return)
    progress = min(current_amount / target_amount * 100, 100) if target_amount else 0
    required = required_monthly_sip(target_amount, current_amount, months, annual_return)
    status = classify_sip_status(projected, target_amount, current_amount)
    gap = required - monthly_sip

    messages = {
        "goal_met": "The current amount has already reached the target. Review the plan periodically and keep learning about how SIPs work.",
        "on_track": "The current monthly SIP projects close to or above the target under the stated assumption. Keep tracking progress and review the numbers when your goal or timeline changes.",
        "behind": "The projection is below the target under the stated assumption. Compare the current SIP with the calculated monthly requirement and review the goal timeline.",
        "way_behind": "The projection is materially below the target under the stated assumption. Review the monthly gap and the remaining timeline rather than relying on a return assumption alone.",
        "underfunded": "The projection is well below the target under the stated assumption. Use the monthly gap and remaining months as the main numbers to review.",
    }
    return (
        f"Current progress is {progress:.1f}%. At an illustrative {annual_return:.1f}% annual return assumption, "
        f"the SIP projects to about INR {projected:,.0f} over {months} months. "
        f"The calculated monthly SIP needed for the target is about INR {required:,.0f}, "
        f"so the current monthly gap is INR {max(gap, 0):,.0f}. {messages[status]}"
    )


def coach_sip(data: dict) -> dict:
    monthly_sip = float(data["monthlySIP"])
    target = float(data["targetAmount"])
    current = float(data.get("currentAmount", 0))
    months = int(data["monthsRemaining"])
    annual_return = float(data.get("expectedAnnualReturn", DEFAULT_ANNUAL_RETURN))

    projected = future_value_of_sip(monthly_sip, months, annual_return)
    required = required_monthly_sip(target, current, months, annual_return)
    progress = min(current / target * 100, 100) if target else 0
    status = classify_sip_status(projected, target, current)
    gap = max(required - monthly_sip, 0)
    monte = monte_carlo_projection(monthly_sip, months, annual_return)

    return {
        "userId": str(data["userId"]),
        "status": status,
        "progressPercent": round(progress, 2),
        "projectedAmount": round(projected, 2),
        "requiredMonthlySIP": round(required, 2),
        "monthlyGap": round(gap, 2),
        "monteCarlo": monte,
        "coachingAnalysis": build_coaching_analysis(
            monthly_sip, target, current, months, annual_return
        ),
    }
