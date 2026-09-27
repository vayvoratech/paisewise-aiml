from pathlib import Path

import joblib
import pandas as pd
from sklearn.metrics import roc_auc_score, precision_score


class ChurnModelService:
    FEATURES = [
        "d7_lesson_count", "d7_quiz_count", "d7_paper_trade_count", "d7_streak_days",
        "d7_xp_earned", "d7_notification_open_rate", "onboarding_goal_set",
        "kyc_completed_d7", "first_paper_trade_d7",
    ]

    def train(self, dataset_path: str, output_path: str) -> dict:
        from xgboost import XGBClassifier
        df = pd.read_csv(dataset_path)
        X = df[self.FEATURES]
        y = df["churned"]
        model = XGBClassifier(n_estimators=100, max_depth=3, learning_rate=0.05, subsample=0.9, colsample_bytree=0.9, eval_metric="logloss", random_state=42)
        model.fit(X, y)
        probabilities = model.predict_proba(X)[:, 1]
        predictions = (probabilities >= 0.5).astype(int)
        metrics = {
            "auc_roc": round(float(roc_auc_score(y, probabilities)), 4),
            "precision": round(float(precision_score(y, predictions, zero_division=0)), 4),
            "top_20_precision": self.top_20_precision(y, probabilities),
        }
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(model, output_path)
        return metrics

    @staticmethod
    def top_20_precision(y, probabilities) -> float:
        import numpy as np
        n = max(1, int(len(probabilities) * 0.2))
        idx = np.argsort(probabilities)[-n:]
        return round(float(sum(y.iloc[idx]) / n), 4)
