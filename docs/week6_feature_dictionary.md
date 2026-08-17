# Week 6 Feature Dictionary

| Feature | Source | Calculation / meaning | Expected range |
|---|---|---|---|
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

The pipeline uses a rolling 90-day lookback. It can be scheduled daily by Airflow so new activity is included without requiring a manual full-project refresh.
