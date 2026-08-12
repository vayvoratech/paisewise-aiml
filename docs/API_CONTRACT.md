# AI Service API Contract

## Overview

This document defines the API contract for the AI Service.

Base URL:

http://127.0.0.1:8000

---

## 1. POST `/ai/jargon`

### Purpose

Explain a financial/investment-related term in the requested language.

### Request Schema

    {
      "term": "SIP",
      "language": "en"
    }

### Request Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `term` | string | Yes | Financial term to explain |
| `language` | string | No | Response language. Defaults to `en` |

### Success Response — 200

    {
      "term": "SIP",
      "language": "en",
      "explanation": "Systematic Investment Plan is a method of investing a fixed amount regularly in a mutual fund."
    }

### Response Fields

| Field | Type | Description |
|---|---|---|
| `term` | string | Term provided by the user |
| `language` | string | Language used for the explanation |
| `explanation` | string | Generated or fallback explanation |

### Error Responses

**429 — Rate Limit Exceeded**

    {
      "detail": "Rate limit exceeded. Please try again later."
    }

---

## 2. POST `/ai/portfolio-insight`

### Purpose

Generate an AI-based insight from the user's investment portfolio.

### Request Schema

    {
      "user_id": "11111111-1111-1111-1111-111111111111",
      "language": "en"
    }

### Request Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `user_id` | UUID/string | Yes | User identifier |
| `language` | string | No | Response language. Defaults to `en` |

### Success Response — 200

    {
      "source": "llm",
      "insight": "Your portfolio currently holds shares in TCS and Infosys, placing all your invested capital within the technology sector."
    }

### Response Fields

| Field | Type | Description |
|---|---|---|
| `source` | string | Source of the insight: `llm`, `cache`, or `fallback` |
| `insight` | string | Portfolio insight |

### Error Responses

**429 — Rate Limit Exceeded**

    {
      "detail": "Rate limit exceeded. Please try again later."
    }

---

## 3. GET `/portfolio/insight/{user_id}`

### Purpose

Retrieve the portfolio insight for a specific user.

### Path Parameter

| Parameter | Type | Required | Description |
|---|---|---|---|
| `user_id` | UUID/string | Yes | User identifier |

### Example

    GET /portfolio/insight/11111111-1111-1111-1111-111111111111

### Success Response — 200

    {
      "source": "cache",
      "insight": "Your portfolio currently holds shares in TCS and Infosys, placing all your invested capital within the technology sector."
    }

### Response Fields

| Field | Type | Description |
|---|---|---|
| `source` | string | Source of the insight: `llm`, `cache`, or `fallback` |
| `insight` | string | Portfolio insight |

---

## 4. GET `/features/{userId}`

### Purpose

Retrieve the latest available feature values for a user.

### Path Parameter

| Parameter | Type | Required | Description |
|---|---|---|---|
| `userId` | UUID/string | Yes | User identifier |

### Example

    GET /features/11111111-1111-1111-1111-111111111111

### Success Response — 200

    {
      "user_id": "11111111-1111-1111-1111-111111111111",
      "features": {
        "quiz_attempts_total": 5,
        "quiz_pass_rate": 0.8,
        "avg_quiz_score": 0.75
      },
      "updated_at": "2026-08-03 19:08:31.107794+05:30"
    }

### Response Fields

| Field | Type | Description |
|---|---|---|
| `user_id` | UUID/string | User identifier |
| `features.quiz_attempts_total` | integer/null | Total number of quiz attempts |
| `features.quiz_pass_rate` | number/null | Quiz pass rate |
| `features.avg_quiz_score` | number/null | Average quiz score |
| `updated_at` | string/null | Timestamp of the feature data |

### Error Responses

**404 — User Features Not Found**

    {
      "detail": "User features not found"
    }

---

## 5. POST `/ai/fund-recommend`

### Purpose

Recommend the most suitable mutual funds based on the user's risk profile, investment amount, and investment horizon.

### Request Schema

    {
      "userId": "11111111-1111-1111-1111-111111111111",
      "riskProfile": "Moderate",
      "investmentAmount": 100000,
      "investmentHorizon": 5
    }

### Request Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `userId` | UUID | Yes | User identifier |
| `riskProfile` | string | Yes | User's risk profile |
| `investmentAmount` | number | Yes | Amount available for investment |
| `investmentHorizon` | integer | Yes | Investment horizon in years |

### Success Response — 200

    {
      "recommendationRunId": "bc22be66-5f74-48ce-87e5-ce9f0fea601a",
      "recommendedFunds": [
        {
          "schemeCode": "ca255262-f617-46cc-b1a8-1c29dfe1ffac",
          "fundName": "Axis Bluechip Fund",
          "score": 80,
          "reason": "The Axis Bluechip Fund aligns with your profile because its moderate risk rating directly matches your moderate risk tolerance.",
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

### Response Fields

| Field | Type | Description |
|---|---|---|
| `recommendationRunId` | UUID | Identifier for the recommendation run |
| `recommendedFunds` | array | List of recommended funds |
| `recommendedFunds[].schemeCode` | string | Mutual fund scheme identifier |
| `recommendedFunds[].fundName` | string | Name of the mutual fund |
| `recommendedFunds[].score` | number | Recommendation score |
| `recommendedFunds[].reason` | string | Explanation for the recommendation |
| `recommendedFunds[].keyMetrics.riskLevel` | string | Fund risk level |
| `recommendedFunds[].keyMetrics.category` | string | Fund category |
| `recommendedFunds[].keyMetrics.return1Y` | number/null | 1-year return |
| `recommendedFunds[].keyMetrics.return3Y` | number/null | 3-year return |
| `recommendedFunds[].keyMetrics.return5Y` | number/null | 5-year return |
| `recommendedFunds[].keyMetrics.expenseRatio` | number/null | Fund expense ratio |
| `recommendedFunds[].keyMetrics.aumCrore` | number/null | Assets under management in crore |

---

## 6. POST `/ai/recommendation-click`

### Purpose

Record when a user clicks on a recommended fund.

### Request Schema

    {
      "userId": "11111111-1111-1111-1111-111111111111",
      "recommendationRunId": "bc22be66-5f74-48ce-87e5-ce9f0fea601a",
      "schemeCode": "ca255262-f617-46cc-b1a8-1c29dfe1ffac"
    }

### Request Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `userId` | UUID | Yes | User identifier |
| `recommendationRunId` | UUID | Yes | Recommendation run identifier returned by `/ai/fund-recommend` |
| `schemeCode` | string | Yes | Mutual fund scheme identifier |

### Success Response — 200

    {
      "clickId": "100bdc2f-2f25-461a-b48b-c4102cc2e109",
      "status": "recorded"
    }

### Response Fields

| Field | Type | Description |
|---|---|---|
| `clickId` | UUID | Identifier of the recorded click |
| `status` | string | Click recording status |

---

## 7. POST `/ai/recommendation/refresh/lesson/{userId}`

### Purpose

Refresh a user's recommendations after completing a lesson.

### Path Parameter

| Parameter | Type | Required | Description |
|---|---|---|---|
| `userId` | UUID/string | Yes | User identifier |

### Request Body

No request body.

### Example

    POST /ai/recommendation/refresh/lesson/11111111-1111-1111-1111-111111111111

### Success Response — 200

    {
      "status": "refreshed",
      "reason": "lesson_completion",
      "userId": "11111111-1111-1111-1111-111111111111"
    }

### Response Fields

| Field | Type | Description |
|---|---|---|
| `status` | string | Refresh status |
| `reason` | string | Reason for refresh |
| `userId` | UUID/string | User identifier |

---

## 8. POST `/ai/recommendation/refresh/goal/{userId}`

### Purpose

Refresh a user's recommendations after the user updates their investment goal.

### Path Parameter

| Parameter | Type | Required | Description |
|---|---|---|---|
| `userId` | UUID/string | Yes | User identifier |

### Request Body

No request body.

### Example

    POST /ai/recommendation/refresh/goal/11111111-1111-1111-1111-111111111111

### Success Response — 200

    {
      "status": "refreshed",
      "reason": "goal_update",
      "userId": "11111111-1111-1111-1111-111111111111"
    }

### Response Fields

| Field | Type | Description |
|---|---|---|
| `status` | string | Refresh status |
| `reason` | string | Reason for refresh |
| `userId` | UUID/string | User identifier |

---

## Common Status Codes

| Status Code | Meaning |
|---|---|
| `200` | Request successful |
| `404` | Requested user/resource not found |
| `422` | Request validation error |
| `429` | Rate limit exceeded |
| `500` | Internal server error |

---

## Notes

- API responses are JSON.
- Fields marked `null` indicate that the corresponding data is currently unavailable.
- Portfolio insights may come from the LLM, cache, or fallback service.
- Fund recommendations are limited to the active funds available in the fund catalogue.
- `recommendationRunId` identifies a specific recommendation run and is used for recommendation click tracking.
- Recommendation refresh endpoints invalidate the existing cached recommendation for the user.
- The API contract should be updated if request or response structures change.