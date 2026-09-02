def get_portfolio_fallback(daily_change_pct=None):
    if daily_change_pct is not None:
        try:
            value = float(daily_change_pct)
            direction = "up" if value >= 0 else "down"
            return (
                f"Your portfolio is {direction} {abs(value):.2f}% today. "
                "Markets moved due to general sentiment. "
                "This is educational information, not investment advice."
            )
        except (TypeError, ValueError):
            pass
    return (
        "Your portfolio is being reviewed using today's available market context. "
        "Markets moved due to general sentiment. "
        "This is educational information, not investment advice."
    )
