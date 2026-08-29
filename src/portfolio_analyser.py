# Portfolio Diversification Analyser

holdings = [
    {"stock": "Company A", "sector": "IT", "amount": 40000},
    {"stock": "Company B", "sector": "IT", "amount": 20000},
    {"stock": "Company C", "sector": "Banking", "amount": 25000},
    {"stock": "Company D", "sector": "Pharma", "amount": 15000}
]


# Calculate total portfolio value
total_value = sum(
    holding["amount"]
    for holding in holdings
)


print("Total Portfolio Value:", total_value)


# Calculate sector concentration
sector_values = {}

for holding in holdings:

    sector = holding["sector"]

    sector_values[sector] = (
        sector_values.get(sector, 0)
        + holding["amount"]
    )


print("\nSector Concentration:")

for sector, amount in sector_values.items():

    percentage = (
        amount / total_value
    ) * 100

    print(
        sector,
        ":", round(percentage, 2), "%"
    )


# Calculate single-stock concentration
print("\nSingle Stock Concentration:")

for holding in holdings:

    percentage = (
        holding["amount"] / total_value
    ) * 100

    print(
        holding["stock"],
        ":", round(percentage, 2), "%"
    )