
import importlib.util
from pathlib import Path

# We load this file directly by path instead of "import airflow.dags...".
# Reason: our own project folder is called "airflow/", and the real
# installed Airflow package is also called "airflow". If we import by
# dotted path, Python gets confused about which "airflow" we mean.
# Loading by file path sidesteps that name clash completely.


_DAG_PATH = (
    Path(__file__).resolve().parents[1]
    / "airflow"
    / "dags"
    / "portfolio_insight_daily.py"
)
_spec = importlib.util.spec_from_file_location(
    "portfolio_insight_daily_dag", _DAG_PATH
)
dag_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(dag_module)


def _fake_users(count):
    users = []
    for i in range(count):
        users.append(
            {
                "user_id": i + 1,
                "full_name": f"Test User {i + 1}",
                "risk_profile": "Moderate",
            }
        )
    return users


class FakeTaskInstance:
    """Very small stand-in for Airflow's xcom, just enough for this test."""

    def __init__(self):
        self.store = {}

    def xcom_pull(self, task_ids):
        return self.store[task_ids]

    def xcom_push(self, task_ids, value):
        self.store[task_ids] = value


def test_ten_simulated_users_generate_and_save_insights(monkeypatch):
    simulated_users = _fake_users(10)

    saved_insights = []

    def fake_call_ai(user_id, language):
        # simulate the ai-service always returning a simple insight
        return {"insight": f"Insight for user {user_id}"}

    def fake_save_portfolio_insight(user_id, insight, language):
        saved_insights.append(
            {"user_id": user_id, "insight": insight, "language": language}
        )

    monkeypatch.setattr(dag_module, "call_ai", fake_call_ai)
    monkeypatch.setattr(
        dag_module, "save_portfolio_insight", fake_save_portfolio_insight
    )

    ti = FakeTaskInstance()
    ti.store["get_users"] = simulated_users

    ai_results = dag_module.call_ai_task(ti=ti)
    ti.store["call_ai_service"] = ai_results

    dag_module.save_insights_task(ti=ti)

    assert len(ai_results) == 10
    assert len(saved_insights) == 10
    assert {row["user_id"] for row in saved_insights} == {
        user["user_id"] for user in simulated_users
    }


def test_batching_still_works_with_fewer_than_fifty_users(monkeypatch):
    simulated_users = _fake_users(10)

    monkeypatch.setattr(
        dag_module, "call_ai", lambda user_id, language: {"insight": "ok"}
    )

    ti = FakeTaskInstance()
    ti.store["get_users"] = simulated_users

    results = dag_module.call_ai_task(ti=ti)

    # 10 users, batch size 50 -> everyone should still be processed
    # in a single batch, nothing gets dropped.
    assert len(results) == 10


def test_batch_error_alert_only_fires_when_a_user_fails(monkeypatch):
    simulated_users = _fake_users(3)
    alert_calls = []

    def fake_call_ai(user_id, language):
        if user_id == 2:
            raise RuntimeError("ai-service timeout")
        return {"insight": "ok"}

    monkeypatch.setattr(dag_module, "call_ai", fake_call_ai)
    monkeypatch.setattr(
        dag_module,
        "send_batch_error_message",
        lambda errors: alert_calls.append(errors),
    )

    ti = FakeTaskInstance()
    ti.store["get_users"] = simulated_users

    results = dag_module.call_ai_task(ti=ti)

    assert len(results) == 2
    assert len(alert_calls) == 1
    assert alert_calls[0][0]["user_id"] == 2
