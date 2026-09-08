# Week 8 - Recommendation Validation

## Implemented rules

### Beginner expense-ratio exclusion

A beginner cannot receive a fund with `expense_ratio > 1.5`.

### Diversity

The final three recommendations first try to use different fund categories and different AMCs. If the real catalogue does not contain three sufficiently diverse funds, the service fills the remaining slots from the highest-scoring eligible funds rather than inventing data.

### ELSS liquidity

If the investment horizon is less than three years, ELSS/tax-saver funds are excluded.

## 20-profile evaluation

`evaluation/week8_user_profiles.json` contains 20 synthetic evaluation profiles covering different goals, risk levels and horizons. These profiles are evaluation fixtures only; they are not inserted into the application database.

Run the evaluator against the real mutual-fund catalogue exported from `mf_schemes`.

## Domain review and five-person feedback

The code supports reviewer feedback and weight revision in
`app/services/recommendation_feedback.py`.

Real feedback from five internal team members must be entered by the team. It is intentionally not fabricated in the repository.

Once the five reviews are available, `calculate_revised_weights()` normalizes their ratings and `save_revised_weights()` stores the resulting weights.

This distinction keeps the project honest: code can automate feedback collection and weight calculation, but it cannot truthfully claim that five people gave feedback when they have not.
