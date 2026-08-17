# Week 1-7 Task Mapping

This file maps the implementation to the task screenshots shared for this project. It is kept as a checklist so unfinished work is visible instead of being replaced by unrelated features.

| Week | Task area | Implementation |
|---|---|---|
| 1 | Feature store schema | `app/db/schema.py`, `app/db/create_tables.py` |
| 1 | User extraction | `app/pipelines/extract_users.py` |
| 1 | Airflow setup/test DAG | `airflow/dags/financial_ai_test_dag.py`, `docs/airflow_setup.md` |
| 1 | Mutual fund data structure | `data/NAVAll.txt`, `scripts/load_mutual_funds.py`, `docs/mutual_fund_data_structure.md` |
| 2 | MLflow setup | `app/services/portfolio_service.py`, `docs/mlflow_setup.md` |
| 2 | Data validation | `app/utils/data_validation.py`, `app/pipelines/validate_features.py` |
| 2 | 200 financial terms | `data/financial_terms.csv`, `scripts/create_terms_excel.py` |
| 2 | Jargon PostgreSQL loader | `scripts/load_jargon_terms.py` |
| 2 | Hindi translation checklist | `docs/hindi_translation_checklist.md` |
| 2 | 50-term prompt testing | `scripts/run_jargon_prompt_tests.py` |
| 3 | 100-response quality evaluation | `scripts/evaluate_jargon_responses.py`, `docs/jargon_evaluation_criteria.md` |
| 3 | Worst-performing terms and prompt rewrite | `scripts/evaluate_jargon_responses.py` |
| 4 | Financial AI safety research | `docs/financial_ai_safety.md` |
| 4 | Guardrails | `app/services/llm_service.py`, `docs/financial_ai_guardrails.md` |
| 4 | Guardrail tests | `tests/test_guardrails.py` |
| 5 | Portfolio insight data model | `docs/portfolio_insight_data_requirements.md`, `app/db/schema.py` |
| 5 | Market context aggregator | `app/services/market_context.py`, market/news services |
| 5 | Holdings formatter | `app/services/holdings_formatter.py` |
| 5 | Portfolio explanation research/examples | `docs/portfolio_insight_examples.md` |
| 5 | Prompt structure | `app/prompts/portfolio_prompt.py` |
| 6 | 3-month behaviour extraction | `app/pipelines/extract_user_behaviour.py` |
| 6 | Behaviour features and validation | `app/pipelines/feature_pipeline.py`, `app/pipelines/validate_features.py` |
| 6 | Incremental feature-store update | `app/pipelines/feature_pipeline.py` |
| 6 | Daily portfolio DAG | `airflow/dags/portfolio_insight_daily.py` |
| 6 | Batch size 50 and Slack error handling | `airflow/dags/portfolio_insight_daily.py`, `app/services/slack_service.py` |
| 7 | Mutual fund recommendation scoring | `app/services/fund_recommendation.py` |
| 7 | Recommendation API | `app/api/fund_recommend.py` |
| 7 | API request/response validation | Pydantic models and FastAPI errors |
| 7 | API testing | `tests/test_fund_recommend.py` |

No extra application feature is added outside these task areas.


> This file is retained as the original Week 1-7 map. The current authoritative map is `docs/week1_to_week9_task_mapping.md`.
