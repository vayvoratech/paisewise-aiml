def format_holdings(holdings):
    formatted_holdings = []
    total_value = 0.0

    for holding in holdings:
        quantity = float(holding["quantity"])
        average_price = float(holding["average_price"])
        current_price = holding.get("current_price")

        if current_price is None:
            formatted_holdings.append(
                {
                    "symbol": holding["symbol"],
                    "quantity": quantity,
                    "average_price": average_price,
                    "current_price": None,
                    "current_value": None,
                    "total_gain_loss": None,
                    "allocation_percent": None,
                }
            )
            continue

        current_price = float(current_price)
        current_value = quantity * current_price
        invested_amount = quantity * average_price
        total_gain_loss = current_value - invested_amount
        total_value += current_value

        formatted_holdings.append(
            {
                "symbol": holding["symbol"],
                "quantity": quantity,
                "average_price": average_price,
                "current_price": current_price,
                "current_value": current_value,
                "total_gain_loss": total_gain_loss,
                "allocation_percent": None,
            }
        )

    if total_value:
        for holding in formatted_holdings:
            if holding["current_value"] is not None:
                holding["allocation_percent"] = round(
                    holding["current_value"] / total_value * 100,
                    2,
                )

    return formatted_holdings
