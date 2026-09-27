from app.services.sip_coach import (
    coach_sip,
    future_value_of_sip,
    monte_carlo_projection,
    required_monthly_sip,
)


def base_data():
    return {
        "userId": "1",
        "monthlySIP": 10000,
        "targetAmount": 500000,
        "currentAmount": 100000,
        "monthsRemaining": 36,
        "expectedAnnualReturn": 10,
        "language": "English",
    }


def test_sip_projection_is_positive():
    assert future_value_of_sip(10000, 12, 10) > 120000


def test_required_sip_is_positive():
    assert required_monthly_sip(500000, 100000, 36, 10) > 0


def test_monte_carlo_has_1000_runs():
    result = monte_carlo_projection(10000, 36, 10)
    assert result["runs"] == 1000
    assert result["p10"] <= result["median"] <= result["p90"]


def test_five_sip_scenarios():
    scenarios = [
        {**base_data(), "currentAmount": 500000},
        {**base_data(), "monthlySIP": 20000},
        {**base_data(), "monthlySIP": 2000},
        {**base_data(), "currentAmount": 520000},
        {**base_data(), "monthlySIP": 30000},
    ]
    results = [coach_sip(item) for item in scenarios]
    assert all("coachingAnalysis" in item for item in results)
    assert len(results) == 5


def test_sip_scenario_calculator():
    result = future_value_of_sip(5000, 24, 10)
    assert result > 120000
