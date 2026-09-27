def assemble_portfolio_context(portfolio_input: dict):
    holdings = portfolio_input.get("holdings") or []
    market_context = portfolio_input.get("market_context") or {}
    return {
        "holdings": holdings,
        "market_context": market_context,
    }
