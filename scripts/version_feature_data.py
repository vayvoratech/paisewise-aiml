"""Tag the current feature-store dataset/version in MLflow."""
import os
from datetime import datetime


def main():
    try:
        import mlflow
    except ImportError:
        print("MLflow is not installed")
        return
    version = datetime.now().strftime("features-%Y%m%d-%H%M%S")
    mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "http://127.0.0.1:5000"))
    mlflow.set_experiment("feature-store-versioning")
    with mlflow.start_run(run_name=version):
        mlflow.log_param("feature_version", version)
        mlflow.log_param("lookback_days", 90)
        mlflow.log_param("source", "user_features")
    print(f"Feature dataset version logged: {version}")


if __name__ == "__main__":
    main()
