from app.services.holdings_formatter import format_holdings


def test_holdings_are_formatted_with_allocation():
    result = format_holdings([
        {
            "symbol": "TEST1",
            "quantity": 10,
            "average_price": 100,
            "current_price": 110,
        },
        {
            "symbol": "TEST2",
            "quantity": 10,
            "average_price": 100,
            "current_price": 90,
        },
    ])

    assert result[0]["current_value"] == 1100
    assert result[1]["current_value"] == 900
    assert result[0]["allocation_percent"] == 55
    assert result[1]["allocation_percent"] == 45
