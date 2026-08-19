from typing import Any, Dict, List


TRADING_CONCEPTS = [
    "Resistance level",
    "Volume",
    "P/E ratio",
    "Market capitalization",
    "52-week high",
    "52-week low",
    "Relative volume",
    "Sector performance",
    "Price level",
    "User lesson history",
]


def extract_trade_context(
    order: Dict[str, Any],
    market: Dict[str, Any],
    lesson_history: List[Dict[str, Any]] | None = None,
) -> Dict[str, Any]:
    """Build the context needed to evaluate a paper-trade decision."""
    lesson_history = lesson_history or []

    return {
        "symbol": order.get("symbol"),
        "side": order.get("side", "BUY").upper(),
        "price": order.get("price"),
        "quantity": order.get("quantity"),
        "sector": market.get("sector"),
        "52_week_high": market.get("52_week_high"),
        "52_week_low": market.get("52_week_low"),
        "volume": market.get("volume"),
        "average_volume": market.get("average_volume"),
        "relative_volume": market.get("relative_volume"),
        "pe_ratio": market.get("pe_ratio"),
        "market_cap": market.get("market_cap"),
        "sector_change_percent": market.get("sector_change_percent"),
        "lessons_studied": [
            item.get("lesson_name")
            for item in lesson_history
            if item.get("completed")
        ],
    }


def evaluate_trade(context: Dict[str, Any]) -> Dict[str, Any]:
    """Apply the Week 9 rubric and return structured coaching signals."""
    checks = []

    price = context.get("price")
    high = context.get("52_week_high")
    low = context.get("52_week_low")
    volume = context.get("volume")
    average_volume = context.get("average_volume")
    lessons = {str(item).lower() for item in context.get("lessons_studied", [])}

    if price is not None and high is not None:
        distance_from_high = (float(high) - float(price)) / float(high) * 100
        checks.append({
            "criterion": "52-week price level",
            "passed": distance_from_high >= 5,
            "detail": "Price has reasonable distance from the 52-week high."
            if distance_from_high >= 5
            else "Price is close to the 52-week high; review resistance before entering.",
        })

    if price is not None and low is not None:
        checks.append({
            "criterion": "52-week low context",
            "passed": True,
            "detail": "52-week low context is available for review.",
        })

    if volume is not None and average_volume:
        relative_volume = float(volume) / float(average_volume)
        checks.append({
            "criterion": "Volume",
            "passed": relative_volume >= 0.8,
            "detail": "Volume is reasonably close to or above its average."
            if relative_volume >= 0.8
            else "Volume is below average; confirm that the price move has enough participation.",
        })

    if "resistance" not in " ".join(lessons):
        checks.append({
            "criterion": "Learning history",
            "passed": False,
            "detail": "The user has not completed the resistance lesson; review it before treating the trade as a strong decision.",
        })

    if "volume" not in " ".join(lessons):
        checks.append({
            "criterion": "Learning history",
            "passed": False,
            "detail": "The user has not completed the volume lesson; review volume before evaluating the entry.",
        })

    sector = context.get("sector")
    if sector:
        sector_lesson_name = str(sector).strip().lower()
        studied_sector = any(
            sector_lesson_name in lesson_name for lesson_name in lessons
        )
        checks.append({
            "criterion": "Sector studied",
            "passed": studied_sector,
            "detail": (
                f"The user has studied the {sector} sector before this trade."
                if studied_sector
                else f"The user has not studied the {sector} sector; review sector basics before treating this as a strong decision."
            ),
        })

    passed = sum(1 for item in checks if item["passed"])
    score = round((passed / len(checks)) * 100, 2) if checks else 0.0

    return {
        "score": score,
        "checks": checks,
        "decision": "good" if score >= 70 else "needs_review",
    }


def build_coach_prompt(context: Dict[str, Any], evaluation: Dict[str, Any], language: str) -> str:
    return f"""
You are a financial education coach evaluating a paper trade.

Trade context:
{context}

Rubric evaluation:
{evaluation}

Give concise educational feedback in {language}.
Explain what the user should review before making a similar paper-trade decision.
Do not guarantee returns, predict prices, or give a real-money buy/sell instruction.
Keep it below 120 words.
""".strip()
