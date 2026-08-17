# Fund Recommendation API

## Endpoint

`POST /ai/fund-recommend`

## Request

```json
{
  "userId": "<user-id>",
  "riskProfile": "Beginner",
  "investmentAmount": 100000,
  "investmentHorizon": 5,
  "userGoal": "retirement",
  "language": "hi"
}
```

`riskProfile` accepts:

- `Beginner`
- `Intermediate`
- `Advanced`
- `Low`
- `Moderate`
- `High`

The Week 7 experience mapping is:

- Beginner → Low/Moderate funds only
- Intermediate → up to High
- Advanced → all risk categories

## Week 7 goal mapping

- House purchase → balanced/large-cap preference
- Retirement → equity + debt/hybrid preference
- Education → long-term equity preference
- No goal → conservative/large-cap preference

Goal and horizon are suitability signals while the required 40/30/20/10
score remains unchanged.

## Week 8 rules

Before final selection:

1. Beginner users cannot receive funds with expense ratio above 1.5%.
2. ELSS/tax-saver funds are excluded when the investment horizon is below
   three years.
3. The service first tries to select three funds from different categories
   and different AMCs.

If the real catalogue cannot provide full diversity, the service fills the
remaining slots from eligible high-scoring funds instead of inventing funds.

## Response

The service returns up to three active funds available in `mf_schemes`.

```json
{
  "recommendedFunds": [
    {
      "fundName": "<fund name>",
      "score": 75.0,
      "reason": "<one sentence explanation>",
      "keyMetrics": {
        "riskLevel": "Moderate",
        "category": "<category>",
        "return1Y": null,
        "return3Y": null,
        "return5Y": null,
        "expenseRatio": null,
        "aumCrore": null
      }
    }
  ]
}
```

## Language

`language` accepts any of the 22 supported Indian scheduled-language codes
or names. English is accepted only as a fallback.

## Validation and errors

- `200` - recommendation generated successfully
- `400` - invalid risk profile, language or request values
- `404` - no suitable active fund remains after eligibility rules
- `500` - database or recommendation service failure
