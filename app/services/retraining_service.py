from pathlib import Path
import json
import shutil
import pandas as pd

from app.services.churn_model_service import ChurnModelService
from app.services.model_registry_service import ModelRegistryService
from app.services.slack_service import send_retraining_message


class RetrainingService:
    def __init__(self):
        self.registry = ModelRegistryService()

    def _log_mlflow(self, model_name: str, metrics: dict, version: str) -> None:
        try:
            import mlflow
            mlflow.set_experiment("PaiseWise Model Retraining")
            with mlflow.start_run(run_name=f"{model_name}-{version}"):
                mlflow.log_params({"model_name": model_name, "version": version})
                for key, value in metrics.items():
                    if isinstance(value, (int, float)):
                        mlflow.log_metric(key, float(value))
        except Exception:
            pass

    def retrain_fund(self) -> dict:
        source = Path("data/fund/fund_performance.csv")
        current = Path("data/fund/models/current_model.json")
        previous = Path("data/fund/models/previous_model.json")
        df = pd.read_csv(source)
        weights = {"return_1y": 0.20, "return_3y": 0.20, "risk": 0.20, "sharpe_ratio": 0.20, "expense_ratio": 0.20}

        for key in weights:
            if key in df:
                value = float(df[key].std() or 1)
                weights[key] = 1 / value

        total = sum(weights.values())
        weights = {k: round(v / total, 4) for k, v in weights.items()}
        candidate = {"weights": weights, "dataset_version": str(source.stat().st_mtime_ns)}
        old = json.loads(current.read_text()) if current.exists() else {"weights": {}}
        old_score = self._fund_score(df, old.get("weights", {}))
        new_score = self._fund_score(df, weights)
        improvement = ((new_score - old_score) / abs(old_score)) if old_score else 1.0
        deployed = improvement > 0.02

        if deployed:
            if current.exists():
                shutil.copy2(current, previous)
            current.write_text(json.dumps(candidate, indent=2))

        metrics = {
            "validation_score": round(new_score, 6),
            "improvement": round(improvement, 6),
            "deployed": deployed,
        }

        entry = self.registry.register(
            "fund_recommendation",
            str(current),
            metrics,
            candidate["dataset_version"],
        )
        self._log_mlflow("fund_recommendation", metrics, entry["version"])
        send_retraining_message("fund_recommendation", metrics)
        return entry

    @staticmethod
    def _fund_score(df, weights):
        normalized = df.copy()
        score = 0.0

        for col, weight in weights.items():
            if col not in normalized:
                continue

            lo, hi = normalized[col].min(), normalized[col].max()
            normalized[col] = (normalized[col] - lo) / ((hi - lo) or 1)
            score += normalized[col].mean() * float(weight)

        return float(score)

    def retrain_churn(self) -> dict:
        service = ChurnModelService()
        output = "data/churn/models/candidate_churn_model.pkl"

        metrics = service.train(
            "data/churn/churn_training_dataset.csv",
            output,
        )

        current = Path("data/churn/models/current_churn_model.pkl")
        previous = Path("data/churn/models/previous_churn_model.pkl")

        candidate_auc = float(metrics.get("auc_roc", 0.0))
        latest = self.registry.latest("churn")

        current_auc = None
        if latest:
            current_auc = latest.get("metrics", {}).get("auc_roc")

        if current_auc is None:
            deployed = not current.exists()
        else:
            deployed = candidate_auc > float(current_auc)

        if deployed:
            if current.exists():
                shutil.copy2(current, previous)
            shutil.copy2(output, current)

        metrics["deployed"] = deployed
        metrics["candidate_auc_roc"] = candidate_auc
        if current_auc is not None:
            metrics["previous_auc_roc"] = float(current_auc)

        entry = self.registry.register(
            "churn",
            str(current),
            metrics,
            "last_90_days",
        )
        self._log_mlflow("churn", metrics, entry["version"])
        send_retraining_message("churn", metrics)

        return entry
