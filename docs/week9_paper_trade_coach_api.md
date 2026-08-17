# Week 9 - Paper Trade Coach API

## Endpoint

`POST /ai/paper-trade-coach`

## Example request

```json
{
  "userId": "123",
  "language": "te",
  "order": {
    "symbol": "ABC",
    "side": "BUY",
    "price": 2500,
    "quantity": 10
  },
  "marketContext": {
    "sector": "IT",
    "52_week_high": 2700,
    "52_week_low": 1800,
    "volume": 1200000,
    "average_volume": 1000000,
    "pe_ratio": 24,
    "market_cap": "Large",
    "sector_change_percent": 1.2
  },
  "lessonHistory": [
    {"lesson_name": "resistance", "completed": true},
    {"lesson_name": "volume", "completed": true}
  ]
}
```

## Flow

```text
Order
  ↓
Trade context extractor
  ↓
Week 9 rubric
  ↓
Structured evaluation
  ↓
LLM educational feedback
```

The response contains the extracted context, rubric score/decision and coach
feedback.

The service is educational and does not provide guaranteed returns or a
real-money buy/sell instruction.
