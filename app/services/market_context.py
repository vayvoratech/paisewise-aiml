from typing import Dict, List


def build_market_context(
    index_movements: List[Dict],
    sector_performance: List[Dict],
    news: List[Dict],
) -> str:
    """Combine fetched market, sector and news data into prompt context."""
    lines = ["Today's Market"]

    if index_movements:
        lines.append("\nTop market movements")
        for item in index_movements[:5]:
            lines.append(
                f"- {item.get('symbol')}: {item.get('change_percent')}%"
            )

    if sector_performance:
        lines.append("\nSector performance")
        for item in sector_performance:
            lines.append(
                f"- {item.get('sector')}: {item.get('change_percent')}%"
            )

    if news:
        lines.append("\nFinancial news")
        for item in news[:3]:
            lines.append(f"- {item.get('title')}")

    return "\n".join(lines)
