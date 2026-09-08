LESSON_CURRICULUM = [
    {"lesson_name": "resistance", "prerequisites": []},
    {"lesson_name": "volume", "prerequisites": []},
    {"lesson_name": "pe_ratio", "prerequisites": []},
    {"lesson_name": "market_cap", "prerequisites": []},
    {"lesson_name": "52_week_high_low", "prerequisites": ["resistance"]},
    {"lesson_name": "relative_volume", "prerequisites": ["volume"]},
    {"lesson_name": "sector_performance", "prerequisites": ["market_cap"]},
    {"lesson_name": "banking_sector_basics", "prerequisites": ["sector_performance"]},
    {"lesson_name": "pharma_sector_basics", "prerequisites": ["sector_performance"]},
    {"lesson_name": "mutual_fund_basics", "prerequisites": ["pe_ratio", "market_cap"]},
    {"lesson_name": "risk_and_diversification", "prerequisites": ["mutual_fund_basics"]},
    {"lesson_name": "paper_trading_intro", "prerequisites": [
        "resistance", "volume", "52_week_high_low", "relative_volume"
    ]},
]

LESSON_ORDER = [lesson["lesson_name"] for lesson in LESSON_CURRICULUM]

LESSON_PREREQUISITES = {
    lesson["lesson_name"]: lesson["prerequisites"] for lesson in LESSON_CURRICULUM
}
