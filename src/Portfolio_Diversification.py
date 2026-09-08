# Portfolio Diversification Score

holdings = [
    {"sector": "IT", "market_cap": "Large", "amount": 25000},
    {"sector": "Banking", "market_cap": "Large", "amount": 25000},
    {"sector": "Pharma", "market_cap": "Mid", "amount": 25000},
    {"sector": "FMCG", "market_cap": "Small", "amount": 25000}
]


# Calculate total portfolio value

total_value = sum(
    holding["amount"]
    for holding in holdings
)


# Calculate sector weights

sector_values = {}

for holding in holdings:

    sector = holding["sector"]

    sector_values[sector] = (
        sector_values.get(sector, 0)
        + holding["amount"]
    )


sector_weights = []

for amount in sector_values.values():

    weight = amount / total_value

    sector_weights.append(weight)


# Calculate market-cap weights

market_cap_values = {}

for holding in holdings:

    market_cap = holding["market_cap"]

    market_cap_values[market_cap] = (
        market_cap_values.get(market_cap, 0)
        + holding["amount"]
    )


market_cap_weights = []

for amount in market_cap_values.values():

    weight = amount / total_value

    market_cap_weights.append(weight)


# Simple diversification score

sector_score = (
    1 - max(sector_weights)
) * 100


market_cap_score = (
    1 - max(market_cap_weights)
) * 100


# Final score

diversification_score = (
    sector_score + market_cap_score
) / 2


print(
    "Diversification Score:",
    round(diversification_score, 2),
    "/ 100"
)