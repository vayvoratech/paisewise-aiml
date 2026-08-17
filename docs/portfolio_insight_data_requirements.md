# Portfolio Insight Data Requirements

The Portfolio Insight feature will use user details, portfolio information, current holdings, and market data to generate a personalized daily investment insight.

## 1. User Details

The following user information will be used to personalize the insight:

- User ID
- Preferred language
- Risk profile
- Investment goal
- Monthly investment amount
- Investment experience

These details help the system generate insights based on the user's investment preferences and experience level.

## 2. Portfolio Summary

The portfolio summary will contain:

- Total portfolio value
- Total invested amount
- Overall profit or loss
- Number of holdings

This information provides an overall view of the user's current portfolio performance.

## 3. Holding Details

Each portfolio holding should include:

- Stock symbol
- Company name
- Quantity
- Average purchase price
- Current market price
- Current holding value
- Today's profit or loss
- Overall profit or loss
- Portfolio allocation percentage

The holding data will be formatted before sending it to the LLM.

## 4. Market Information

The system will collect the following market information:

- NIFTY 50 movement
- SENSEX movement
- Best- and worst-performing sectors
- Relevant financial news headlines

This information will help explain whether changes in the user's portfolio are related to broader market or sector movements.

## 5. Portfolio Insight Output

The generated insight should consider:

- User risk profile
- Investment goal
- Current portfolio performance
- Individual holdings
- Market conditions
- Preferred language

The output should provide a simple explanation of the portfolio's movement and highlight important factors affecting its performance.