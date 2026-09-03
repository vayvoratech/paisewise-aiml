# Portfolio Correlation Matrix

import yfinance as yf
import pandas as pd


# --------------------------------------------------
# 1. User Portfolio
# --------------------------------------------------

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


# --------------------------------------------------
# 2. Get Stock Names
# --------------------------------------------------

tickers = [
    holding["stock"]
    for holding in holdings
]


# --------------------------------------------------
# 3. Download Last 1 Year Stock Prices
# --------------------------------------------------

print("Downloading stock data...")

prices = yf.download(
    tickers,
    period="1y",
    interval="1d",
    auto_adjust=True
)["Close"]


# --------------------------------------------------
# 4. Make Sure Prices Are DataFrame
# --------------------------------------------------

if isinstance(prices, pd.Series):
    prices = prices.to_frame()


# --------------------------------------------------
# 5. Calculate Daily Returns
# --------------------------------------------------

returns = prices.pct_change().dropna()


# --------------------------------------------------
# 6. Calculate Correlation Matrix
# --------------------------------------------------

correlation_matrix = returns.corr()


# --------------------------------------------------
# 7. Display Correlation Matrix
# --------------------------------------------------

print()
print("Portfolio Correlation Matrix")
print("----------------------------")

print(
    correlation_matrix.round(4)
)


# --------------------------------------------------
# 8. Identify Highly Correlated Holdings
# --------------------------------------------------

print()
print("Concentrated Bets")
print("-----------------")

threshold = 0.70

found = False

for i in range(len(tickers)):

    for j in range(i + 1, len(tickers)):

        stock_1 = tickers[i]
        stock_2 = tickers[j]

        correlation = correlation_matrix.loc[
            stock_1,
            stock_2
        ]

        if abs(correlation) >= threshold:

            print(
                f"{stock_1} and {stock_2}: "
                f"{correlation:.4f}"
            )

            found = True


if not found:

    print(
        "No highly correlated stock pairs found "
        f"using threshold {threshold}."
    )


print()
print("Correlation analysis completed successfully.")