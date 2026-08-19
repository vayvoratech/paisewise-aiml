# Week 6 Feature Dictionary

| Feature | Source | Calculation / meaning | Expected range |
|---|---|---|---|
| city_tier | users.kyc_city | mapped via app/utils/city_tier.py (tier_1/tier_2/tier_3 city list) | tier_1, tier_2, tier_3, or null if city unknown |
| lesson_completion_rate | lesson_progress | completed lessons / lesson records | 0–1 |
| quiz_avg_score | quiz_attempts | average quiz score per user | 0–100 |
| streak_days | behaviour dates | consecutive active days | >= 0 |
| paper_trade_count | paper_trades | number of trades in lookback window | >= 0 |
| paper_trade_profit_rate | paper_trades | profitable trades / total trades | 0–1 |
| time_of_day | user_sessions.login_time | session start bucket | night/morning/afternoon/evening |
| session_duration | user_sessions | total session duration | >= 0 |
| screens_visited | user_sessions | total screens visited | >= 0 |
| lessons_started | user_sessions | total lessons started | >= 0 |
| quizzes_taken | user_sessions | total quizzes taken | >= 0 |

## Validation

The pipeline checks null-sensitive calculations and valid numeric ranges before committing updates.

## Incremental behaviour

The pipeline is incremental by default. It looks at the latest `updated_at` timestamp already stored in `user_features` (the "watermark") and only recomputes users who have new session/lesson/quiz/trade activity after that timestamp, plus any brand-new users with no feature row yet.

Each recomputed user's stats still use a rolling 90-day lookback window (streaks, completion rate etc need history to be meaningful) - what's incremental is *which users* get touched each day, not how far back each user's own numbers look.

Call `run_behaviour_feature_pipeline(full_refresh=True)` to force a one-off full recompute of every user, e.g. for a backfill.
