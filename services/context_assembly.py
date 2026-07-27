def assemble_portfolio_context(user_id: str):

    # Temporary mock data.
    # Replace with portfolio database and market data service later.

    portfolio_data = {
        "user_id": user_id,
        "holdings": [
            {
                "symbol": "TCS",
                "quantity": 10,
                "current_price": 3500
            },
            {
                "symbol": "INFY",
                "quantity": 5,
                "current_price": 1600
            }
        ]
    }

    return portfolio_data