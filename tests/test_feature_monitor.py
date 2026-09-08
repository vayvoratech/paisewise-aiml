#unit tests for monitoring logic
from services.feature_monitor import calculate_shift


def test_feature_shift_alert():

    old_distribution = {
        "risk_score": 0.50,
        "portfolio_value": 100000
    }

    new_distribution = {
        "risk_score": 0.75,
        "portfolio_value": 130000
    }


    alerts = calculate_shift(
        old_distribution,
        new_distribution
    )


    assert len(alerts) == 2

    assert alerts[0]["feature"] == "risk_score"
    assert alerts[1]["feature"] == "portfolio_value"



def test_no_feature_shift_alert():

    old_distribution = {
        "risk_score": 0.50,
        "portfolio_value": 100000
    }


    new_distribution = {
        "risk_score": 0.55,
        "portfolio_value": 105000
    }


    alerts = calculate_shift(
        old_distribution,
        new_distribution
    )


    assert len(alerts) == 0