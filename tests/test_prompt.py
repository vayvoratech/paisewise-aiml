from app.prompts.portfolio_prompt import create_prompt


def test_portfolio_prompt_contains_required_sections():
    prompt = create_prompt(
        {
            "full_name": "Test User",
            "age": 30,
            "risk_profile": "Moderate",
            "monthly_investment": 10000,
        },
        "one holding",
        "market context",
        "English",
    )

    assert "User Details" in prompt
    assert "Portfolio Holdings" in prompt
    assert "Market Information" in prompt
    assert "Do not guarantee future returns" in prompt
