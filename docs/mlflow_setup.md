# MLflow Setup

Week 2 requires local experiment tracking.

Start MLflow from the project environment:

```bash
mlflow server --host 127.0.0.1 --port 5000
```

The portfolio insight service logs the prompt, model inputs, response length and execution time to the `Portfolio Insight` experiment.

Do not commit `mlruns/`, `mlflow.db` or other local tracking data.
