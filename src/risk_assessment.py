# Portfolio Risk Assessment
# Calculate portfolio beta vs NIFTY 50 using daily returns

import yfinance as yf
import pandas as pd


# --------------------------------------------------
# 1. User Portfolio
# --------------------------------------------------

holdings = [
    {
        "stock": "RELIANCE.NS",
        "weight": 0.40
    },
    {
        "stock": "TCS.NS",
        "weight": 0.20
    },
    {
        "stock": "HDFCBANK.NS",
        "weight": 0.25
    },
    {
        "stock": "SUNPHARMA.NS",
        "weight": 0.15
    }
]


# --------------------------------------------------
# 2. Check Portfolio Weights
# --------------------------------------------------

total_weight = sum(
    holding["weight"]
    for holding in holdings
)

if abs(total_weight - 1.0) > 0.001:
    raise ValueError(
        "Portfolio weights must add up to 100%"
    )


# --------------------------------------------------
# 3. Get Stock Names
# --------------------------------------------------

tickers = [
    holding["stock"]
    for holding in holdings
]


# --------------------------------------------------
# 4. Download Stock Prices
# --------------------------------------------------

print("Downloading stock data...")

prices = yf.download(
    tickers,
    period="1y",
    interval="1d",
    auto_adjust=True
)["Close"]


# --------------------------------------------------
# 5. Download NIFTY 50 Data
# --------------------------------------------------

print("Downloading NIFTY 50 data...")

nifty = yf.download(
    "^NSEI",
    period="1y",
    interval="1d",
    auto_adjust=True
)["Close"]


# --------------------------------------------------
# 6. Calculate Daily Returns
# --------------------------------------------------

stock_returns = prices.pct_change().dropna()

nifty_returns = nifty.pct_change().dropna()


# --------------------------------------------------
# 7. Fix NIFTY DataFrame / Series Issue
# --------------------------------------------------

if isinstance(nifty_returns, pd.DataFrame):
    nifty_returns = nifty_returns.iloc[:, 0]

nifty_returns.name = "NIFTY"


# --------------------------------------------------
# 8. Make Sure Stock Returns Are a DataFrame
# --------------------------------------------------

if isinstance(stock_returns, pd.Series):
    stock_returns = stock_returns.to_frame()


# --------------------------------------------------
# 9. Combine Stock and NIFTY Returns
# --------------------------------------------------

combined_returns = pd.concat(
    [
        stock_returns,
        nifty_returns
    ],
    axis=1
).dropna()


# --------------------------------------------------
# 10. Check That We Have Enough Data
# --------------------------------------------------

if combined_returns.empty:
    raise ValueError(
        "No matching daily return data was found."
    )


# --------------------------------------------------
# 11. Calculate Portfolio Daily Returns
# --------------------------------------------------

portfolio_returns = pd.Series(
    0.0,
    index=combined_returns.index
)


for holding in holdings:

    stock = holding["stock"]
    weight = holding["weight"]

    if stock not in combined_returns.columns:
        raise ValueError(
            f"No data found for {stock}"
        )

    portfolio_returns += (
        combined_returns[stock] * weight
    )


# --------------------------------------------------
# 12. Calculate Correlation
# --------------------------------------------------

correlation = portfolio_returns.corr(
    combined_returns["NIFTY"]
)


# --------------------------------------------------
# 13. Calculate Volatility
# --------------------------------------------------

portfolio_volatility = (
    portfolio_returns.std()
)

nifty_volatility = (
    combined_returns["NIFTY"].std()
)


# --------------------------------------------------
# 14. Calculate Beta
# --------------------------------------------------

beta = (
    correlation
    * portfolio_volatility
    / nifty_volatility
)


# --------------------------------------------------
# 15. Display Results
# --------------------------------------------------

print()
print("Portfolio Risk Assessment")
print("-------------------------")

print(
    "Portfolio-NIFTY Correlation:",
    round(correlation, 4)
)

print(
    "Portfolio Daily Volatility:",
    round(
        portfolio_volatility * 100,
        2
    ),
    "%"
)

print(
    "NIFTY Daily Volatility:",
    round(
        nifty_volatility * 100,
        2
    ),
    "%"
)

print(
    "Portfolio Beta vs NIFTY 50:",
    round(beta, 4)
)

print()
print("Analysis completed successfully.")