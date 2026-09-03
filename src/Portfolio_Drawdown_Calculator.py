# Portfolio Drawdown Calculator

import yfinance as yf
import pandas as pd


# User's current holdings
holdings = [
    {
        "stock": "RELIANCE.NS",
        "amount": 40000
    },
    {
        "stock": "TCS.NS",
        "amount": 20000
    },
    {
        "stock": "HDFCBANK.NS",
        "amount": 25000
    },
    {
        "stock": "SUNPHARMA.NS",
        "amount": 15000
    }
]


# Get stock names
tickers = [
    holding["stock"]
    for holding in holdings
]


# Download last 1 year data
prices = yf.download(
    tickers,
    period="1y",
    interval="1d",
    auto_adjust=True
)["Close"]


# Make sure prices are in DataFrame format
if isinstance(prices, pd.Series):
    prices = prices.to_frame()


# Calculate current number of shares
shares = {}

for holding in holdings:

    stock = holding["stock"]

    # Get the latest available price
    latest_price = prices[stock].dropna().iloc[-1]

    shares[stock] = (
        holding["amount"] / latest_price
    )


# Calculate portfolio value for every day
portfolio_values = pd.Series(
    0.0,
    index=prices.index
)


for stock in tickers:

    portfolio_values += (
        prices[stock] * shares[stock]
    )


# Find the highest portfolio value
previous_high = portfolio_values.cummax()


# Calculate daily drawdown
drawdown = (
    portfolio_values - previous_high
) / previous_high * 100


# Find maximum drawdown
maximum_drawdown = drawdown.min()


# Find highest portfolio value
highest_value = portfolio_values.max()


# Find lowest value after a previous high
lowest_value = portfolio_values[
    drawdown == maximum_drawdown
].iloc[0]


# Display results
print()
print("Portfolio Drawdown Analysis")
print("---------------------------")

print(
    "Highest Portfolio Value:",
    round(highest_value, 2)
)

print(
    "Lowest Value During Maximum Drawdown:",
    round(lowest_value, 2)
)

print(
    "Maximum Drawdown:",
    round(abs(maximum_drawdown), 2),
    "%"
)