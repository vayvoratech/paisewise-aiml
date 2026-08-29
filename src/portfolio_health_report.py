# Portfolio Health Report

portfolio_value = 100000

diversification_score = 72
portfolio_risk = "Moderate"
weekly_return = 2.4

sector_concentration = {
    "IT": 60,
    "Banking": 25,
    "Pharma": 15
}

stock_concentration = {
    "Company A": 40,
    "Company B": 20,
    "Company C": 25,
    "Company D": 15
}


print("=" * 50)
print("WEEKLY PORTFOLIO HEALTH REPORT")
print("=" * 50)

print("\nPortfolio Value:", "₹", portfolio_value)

print("\nDiversification")
print("----------------")
print("Diversification Score:",
      diversification_score, "/ 100")

print("\nSector Concentration")
print("--------------------")

for sector, percentage in sector_concentration.items():

    print(
        sector,
        ":",
        percentage,
        "%"
    )


print("\nSingle Stock Concentration")
print("--------------------------")

for stock, percentage in stock_concentration.items():

    print(
        stock,
        ":",
        percentage,
        "%"
    )


print("\nRisk")
print("----")
print("Portfolio Risk:", portfolio_risk)


print("\nWeekly Performance")
print("------------------")
print("Weekly Return:",
      weekly_return,
      "%")


print("\nOverall Portfolio Health")

if diversification_score >= 70 and portfolio_risk == "Moderate":
    health = "Healthy"
else:
    health = "Needs Attention"

print("Status:", health)

print("\nReport generated successfully.")