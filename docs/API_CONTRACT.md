# AI Service API Contract

## Overview

This document defines the API contract for the AI Service.

Base URL:

```text
http://127.0.0.1:8000
```

---

## 1. POST `/ai/jargon`

### Purpose

Explain a financial/investment-related term in the requested language.

### Request

```json
{
  "term": "SIP",
  "language": "en"
}
```

### Request Fields

| Field      | Type   | Required | Description                         |
| ---------- | ------ | -------- | ----------------------------------- |
| `term`     | string | Yes      | Financial term to explain           |
| `language` | string | No       | Response language. Defaults to `en` |

### Success Response — 200

```json
{
  "term": "SIP",
  "language": "en",
  "explanation": "Systematic Investment Plan is a method of investing a fixed amount regularly in a mutual fund."
}
```

### Response Fields

| Field         | Type   | Description                       |
| ------------- | ------ | --------------------------------- |
| `term`        | string | Term provided by the user         |
| `language`    | string | Language used for the explanation |
| `explanation` | string | Generated or fallback explanation |

### Error Responses

**429 — Rate Limit Exceeded**

```json
{
  "detail": "Rate limit exceeded. Please try again later."
}
```

---

## 2. POST `/ai/portfolio-insight`

### Purpose

Generate an AI-based insight from the user's investment portfolio.

### Request

```json
{
  "user_id": "11111111-1111-1111-1111-111111111111",
  "language": "en"
}
```

### Request Fields

| Field      | Type   | Required | Description                         |
| ---------- | ------ | -------- | ----------------------------------- |
| `user_id`  | string | Yes      | User identifier                     |
| `language` | string | No       | Response language. Defaults to `en` |

### Success Response — 200

```json
{
  "source": "llm",
  "insight": "Your portfolio is diversified across multiple investments. Consider reviewing your asset allocation regularly based on your investment goals."
}
```

### Response Fields

| Field     | Type   | Description                                          |
| --------- | ------ | ---------------------------------------------------- |
| `source`  | string | Source of the insight: `llm`, `cache`, or `fallback` |
| `insight` | string | Portfolio insight                                    |

### Error Responses

**429 — Rate Limit Exceeded**

```json
{
  "detail": "Rate limit exceeded. Please try again later."
}
```

---

## 3. GET `/portfolio/insight/{user_id}`

### Purpose

Retrieve/generate the portfolio insight for a specific user.

### Path Parameter

| Parameter | Type   | Required | Description     |
| --------- | ------ | -------- | --------------- |
| `user_id` | string | Yes      | User identifier |

### Example

```text
GET /portfolio/insight/11111111-1111-1111-1111-111111111111
```

### Success Response — 200

```json
{
  "source": "cache",
  "insight": "Your portfolio is diversified across multiple investments."
}
```

### Response Fields

| Field     | Type   | Description                                          |
| --------- | ------ | ---------------------------------------------------- |
| `source`  | string | Source of the insight: `llm`, `cache`, or `fallback` |
| `insight` | string | Portfolio insight                                    |

---

## 4. GET `/features/{userId}`

### Purpose

Retrieve the latest available feature values for a user.

### Path Parameter

| Parameter | Type   | Required | Description     |
| --------- | ------ | -------- | --------------- |
| `userId`  | string | Yes      | User identifier |

### Example

```text
GET /features/11111111-1111-1111-1111-111111111111
```

### Success Response — 200

```json
{
  "user_id": "11111111-1111-1111-1111-111111111111",
  "features": {
    "quiz_attempts_total": 10,
    "quiz_pass_rate": 0.8,
    "avg_quiz_score": 0.75
  },
  "updated_at": "2026-08-10 10:30:00+00:00"
}
```

### Response Fields

| Field                          | Type         | Description                   |
| ------------------------------ | ------------ | ----------------------------- |
| `user_id`                      | string       | User identifier               |
| `features.quiz_attempts_total` | integer/null | Total number of quiz attempts |
| `features.quiz_pass_rate`      | number/null  | Quiz pass rate                |
| `features.avg_quiz_score`      | number/null  | Average quiz score            |
| `updated_at`                   | string/null  | Timestamp of the feature data |

### Error Responses

**404 — User Features Not Found**

```json
{
  "detail": "User features not found"
}
```

---

## 5. POST `/ai/fund-recommend`

### Purpose

Recommend the most suitable mutual funds based on the user's risk profile, investment amount, and investment horizon.

### Request

```json
{
  "userId": "11111111-1111-1111-1111-111111111111",
  "riskProfile": "Moderate",
  "investmentAmount": 100000,
  "investmentHorizon": 5
}
```

### Request Fields

| Field               | Type    | Required | Description                     |
| ------------------- | ------- | -------- | ------------------------------- |
| `userId`            | UUID    | Yes      | User identifier                 |
| `riskProfile`       | string  | Yes      | User's risk profile             |
| `investmentAmount`  | number  | Yes      | Amount available for investment |
| `investmentHorizon` | integer | Yes      | Investment horizon in years     |

### Success Response — 200

```json
{
  "recommendedFunds": [
    {
      "fundName": "Axis Bluechip Fund",
      "score": 80,
      "reason": "The Axis Bluechip Fund matches your profile because its moderate risk level aligns with your preference for a balanced approach to equity investing.",
      "keyMetrics": {
        "riskLevel": "Moderate",
        "category": "Equity",
        "return1Y": null,
        "return3Y": null,
        "return5Y": null,
        "expenseRatio": 0.5,
        "aumCrore": 50000
      }
    }
  ]
}
```

### Response Fields

| Field                     | Type        | Description                        |
| ------------------------- | ----------- | ---------------------------------- |
| `recommendedFunds`        | array       | List of recommended funds          |
| `fundName`                | string      | Name of the mutual fund            |
| `score`                   | number      | Recommendation score               |
| `reason`                  | string      | Explanation for the recommendation |
| `keyMetrics.riskLevel`    | string      | Fund risk level                    |
| `keyMetrics.category`     | string      | Fund category                      |
| `keyMetrics.return1Y`     | number/null | 1-year return                      |
| `keyMetrics.return3Y`     | number/null | 3-year return                      |
| `keyMetrics.return5Y`     | number/null | 5-year return                      |
| `keyMetrics.expenseRatio` | number/null | Fund expense ratio                 |
| `keyMetrics.aumCrore`     | number/null | Assets under management in crore   |

---

## Common Status Codes

| Status Code | Meaning                           |
| ----------- | --------------------------------- |
| `200`       | Request successful                |
| `404`       | Requested user/resource not found |
| `429`       | Rate limit exceeded               |
| `500`       | Internal server error             |

---

## Notes

* API responses are JSON.
* Fields marked `null` indicate that the corresponding data is currently unavailable.
* Portfolio insights may come from the LLM, cache, or fallback service.
* Fund recommendations are limited to the active funds available in the fund catalogue.
* The API contract should be updated if request or response structures change.
