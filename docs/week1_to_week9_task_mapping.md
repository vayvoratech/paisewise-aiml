# Week 1-9 Task Mapping

This is the implementation map for the task screenshots shared for the project.
It intentionally separates code that is implemented from real-world review work
that cannot be fabricated.

| Week | Task | Implementation |
|---|---|---|
| 1 | Feature store schema | `app/db/schema.py` |
| 1 | User extraction | `app/pipelines/extract_users.py` |
| 1 | Airflow test DAG | `airflow/dags/financial_ai_test_dag.py` |
| 1 | Mutual-fund source study | `data/NAVAll.txt`, `docs/mutual_fund_data_structure.md` |
| 1 | MLflow setup | `docs/mlflow_setup.md`, `app/services/portfolio_service.py` |
| 1 | Validation utilities | `app/utils/data_validation.py`, `app/pipelines/validate_features.py` |
| 2 | 200 financial terms | `data/financial_terms.csv`, `data/financial_terms.xlsx` |
| 2 | Jargon PostgreSQL loader | `scripts/load_jargon_terms.py` |
| 2 | Translation checklist | `docs/indian_language_translation_checklist.md` |
| 2 | Prompt testing | `scripts/run_jargon_prompt_tests.py` |
| 3 | 100-response evaluation | `scripts/evaluate_jargon_responses.py` |
| 3 | Worst-performing terms | `scripts/review_jargon_quality.py` |
| 3 | Prompt revision workflow | `docs/week3_prompt_revisions.md` |
| 3 | Financial AI safety | `docs/financial_ai_safety.md` |
| 3 | Guardrails | `app/services/llm_service.py`, `tests/test_guardrails.py` |
| 4 | Portfolio insight data model | `app/db/schema.py`, `docs/portfolio_insight_data_requirements.md` |
| 4 | Market context | `app/services/market_context.py`, market services |
| 4 | Holdings formatter | `app/services/holdings_formatter.py` |
| 4 | Explanation examples | `docs/portfolio_insight_examples.md` |
| 4 | Prompt structure | `app/prompts/portfolio_prompt.py` |
| 5 | Daily portfolio DAG | `airflow/dags/portfolio_insight_daily.py` |
| 5 | Real holdings | `app/pipelines/get_users.py` |
| 5 | Market data | `app/pipelines/fetch_market_data.py` |
| 5 | Top 3 news | `app/pipelines/fetch_news.py` |
| 5 | Batch size 50 | `airflow/dags/portfolio_insight_daily.py` |
| 5 | Store results | `app/pipelines/save_portfolio_insight.py` |
| 5 | Slack errors | `app/services/slack_service.py` |
| 6 | 3-month behaviour pipeline | `app/pipelines/extract_user_behaviour.py`, `feature_pipeline.py` |
| 6 | Behaviour validation/docs | `validate_features.py`, `docs/week6_feature_dictionary.md` |
| 6 | Incremental update | `feature_pipeline.py` |
| 7 | Fund catalogue | `MFScheme` and `mf_schemes` |
| 7 | Recommendation scoring | `app/services/fund_recommendation.py` |
| 7 | Goal mapping | `GOAL_RULES` and goal suitability score |
| 7 | Risk mapping | beginner/intermediate/advanced aliases and allowed risks |
| 7 | Recommendation API | `app/api/fund_recommend.py` |
| 7 | Explanation generator | `app/services/fund_explanation.py` |
| 8 | Beginner expense exclusion | `apply_week8_exclusions()` |
| 8 | Diversity rule | `select_diverse_top_three()` |
| 8 | ELSS liquidity rule | `apply_week8_exclusions()` |
| 8 | 20-profile evaluation | `evaluation/week8_user_profiles.json`, evaluator script |
| 8 | Domain review rubric | `docs/week8_recommendation_validation.md` |
| 8 | 5-person feedback capture | `docs/week8_reviewer_feedback_template.csv` |
| 8 | Weight revision | `app/services/recommendation_feedback.py`, `scripts/revise_recommendation_weights.py` |
| 8 | Scoring decisions documentation | `docs/week8_recommendation_validation.md` |
| 9 | Good/poor paper trade definition | `docs/week9_trade_rubric.md` |
| 9 | 10 trading concepts | `docs/week9_trading_concepts.md` |
| 9 | Paper-trade rubric | `app/services/paper_trade_coach.py` |
| 9 | 30 training scenarios | `evaluation/week9_paper_trade_scenarios.json` |
| 9 | Trade context extractor | `extract_trade_context()` |
| 9 | Coach feedback | `/ai/paper-trade-coach` |

## External evidence still required

Two Week 8 items are real-world actions rather than code:

1. Review the 20 generated recommendations with domain knowledge.
2. Collect actual feedback from five internal team members.

The repository provides the evaluator, rubric, feedback template and weight
revision code, but it does not fabricate human feedback.
