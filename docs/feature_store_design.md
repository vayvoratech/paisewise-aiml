# Feature Store Design

The feature store is the PostgreSQL `user_features` table.

## Base user features

- user_id
- age
- annual_income
- monthly_investment
- portfolio_value
- risk_profile
- investment_experience_years
- sip_count
- kyc_completed

## Week 6 behaviour features

The following fields were added because the Week 6 task explicitly requires them:

- lesson_completion_rate
- quiz_avg_score
- streak_days
- total_xp
- preferred_language
- onboarding_goal
- age_proxy
- city_tier
- paper_trade_count
- paper_trade_profit_rate
- time_of_day
- session_duration
- screens_visited
- lessons_started
- quizzes_taken

The behaviour pipeline reads a rolling 90-day window and updates the feature row for each user. If a user has no feature row yet, the pipeline creates it from the real `users` table.
