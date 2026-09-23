import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOGUE = ROOT / "data" / "stock_catalogue.csv"
DISCLAIMER = "These are stocks to learn about, not buy recommendations."

RISK_RANK = {"low": 1, "moderate": 2, "high": 3, "beginner": 1, "intermediate": 2, "advanced": 3}


def load_stock_catalogue():
    with CATALOGUE.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def sector_from_lessons(completed_lessons):
    text = " ".join(str(x).lower() for x in completed_lessons)
    sectors = []
    if "it" in text or "technology" in text:
        sectors.append("IT")
    if "bank" in text:
        sectors.append("Banking")
    if "pharma" in text:
        sectors.append("Pharma")
    if "sector" in text and not sectors:
        sectors.extend(["IT", "Banking"])
    return sectors


def calculate_stock_score(stock, risk_profile, learning_level, familiar_sectors):
    user_risk = RISK_RANK.get(str(risk_profile).lower(), 2)
    stock_risk = RISK_RANK.get(str(stock.get("risk_level")).lower(), 2)
    risk_match = max(0, 100 - abs(user_risk - stock_risk) * 35)
    sector_score = 100 if stock.get("sector") in familiar_sectors else 45
    level_score = min(100, learning_level * 10)
    return round(sector_score * 0.5 + risk_match * 0.3 + level_score * 0.2, 2)


def discover_stocks(user_id, risk_profile="moderate", learning_level=5, completed_lessons=None, limit=5):
    completed_lessons = completed_lessons or []
    if learning_level < 5:
        return {
            "userId": str(user_id),
            "learningLevel": learning_level,
            "stocks": [],
            "disclaimer": DISCLAIMER,
            "message": "Stock discovery starts at learning Level 5. Complete more learning content first.",
        }

    familiar_sectors = sector_from_lessons(completed_lessons)
    stocks = load_stock_catalogue()
    eligible = []
    for stock in stocks:
        if str(stock["is_penny"]).lower() == "true" and str(risk_profile).lower() in {"beginner", "low"}:
            continue
        if str(stock["is_fno"]).lower() == "true" and learning_level < 8:
            continue
        stock["score"] = calculate_stock_score(stock, risk_profile, learning_level, familiar_sectors)
        stock["whyInteresting"] = (
            f"You may find {stock['sector']} useful to explore because it connects with the sector-learning context available to you."
            if stock["sector"] in familiar_sectors
            else f"This is an educational example from the {stock['sector']} sector for learning about stock metrics."
        )
        eligible.append(stock)

    eligible.sort(key=lambda x: x["score"], reverse=True)
    return {
        "userId": str(user_id),
        "learningLevel": learning_level,
        "stocks": eligible[:limit],
        "disclaimer": DISCLAIMER,
        "familiarSectors": familiar_sectors,
    }
