from app.services.portfolio_health_service import PortfolioHealthService


def test_portfolio_health_prompt_contains_required_explanation_elements():
    analytics = {
        "total_invested": 100000,
        "current_value": 110000,
        "total_profit_loss": 10000,
        "profit_loss_percentage": 10.0,
        "number_of_holdings": 4,
    }

    market_context = {
        "summary": "Market conditions were positive during the period."
    }

    prompt = PortfolioHealthService.build_prompt(
        analytics=analytics,
        market_context=market_context,
    )

    assert "total invested amount" in prompt
    assert "current portfolio value" in prompt
    assert "total profit or loss" in prompt
    assert "profit/loss percentage" in prompt
    assert "number of holdings" in prompt
    assert "notable holding-level observations" in prompt
    assert "relevant market context" in prompt
    assert "If the available data is insufficient" in prompt


def test_portfolio_health_prompt_requires_objective_explanation():
    analytics = {
        "total_invested": 50000,
        "current_value": 48000,
        "total_profit_loss": -2000,
        "profit_loss_percentage": -4.0,
        "number_of_holdings": 3,
    }

    prompt = PortfolioHealthService.build_prompt(
        analytics=analytics,
    )

    assert "Explain the portfolio objectively." in prompt
    assert "Do not invent financial facts" in prompt
    assert "Do not provide personalized buy, sell" in prompt
    assert "Do not guarantee investment returns." in prompt