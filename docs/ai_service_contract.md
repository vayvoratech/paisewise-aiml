# AI Service Contract

## Request pipeline

Spring Boot sends JSON to the AI service. The AI service validates the JSON,
preprocesses/assembles only AI-required context, calls the model/LLM, validates
the generated response, applies fallback/guardrails, and returns structured JSON.

`Java/backend -> JSON -> AI service -> validation/preprocessing -> Gemini/model -> response validation/fallback -> JSON`

## Authentication

Internal callers send `X-API-KEY` containing the shared `SHARED_SECRET`.
`/ai/health` is public for health probes.

## Portfolio insight

The portfolio-insight endpoint does **not** query application tables. Backend/domain
services must supply holdings and market context in the request JSON. The AI service
only performs AI-side validation, prompt construction, LLM execution, response quality
checks and caching.

Example request:

```json
{
  "user_id": "uuid",
  "language": "en",
  "holdings": [{"symbol": "INFY", "quantity": 10, "avg_buy_price": 1500, "current_price": 1550}],
  "market_context": {"daily_change_pct": 1.2, "sentiment": "positive"}
}
```

Response:

```json
{"source": "llm", "insight": "..."}
```

## Feature API

`GET /features/{userId}` reads the latest precomputed feature vector. Feature creation/update remains a data-pipeline concern.

## Fraud API

`POST /ai/fraud-check` returns `risk_score` from 0-100, `risk_level`, and `triggered_flags`.
Thresholds: `>70 HIGH`, `40-70 MEDIUM`, `<40 LOW`.
