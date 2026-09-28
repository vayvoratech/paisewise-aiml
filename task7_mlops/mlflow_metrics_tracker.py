import mlflow
from task7_mlops.metrics_tracker import ModelMetrics


class MLflowMetricsTracker:
    def __init__(self, tracking_uri: str, experiment_name: str = "Task7_Model_Metrics"):
        if not tracking_uri:
            raise ValueError("tracking_uri cannot be empty")

        if not experiment_name:
            raise ValueError("experiment_name cannot be empty")

        mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment_name)

        self.tracking_uri = tracking_uri
        self.experiment_name = experiment_name

    def log_metrics(
        self,
        model_metrics: ModelMetrics,
        dataset_version: str = "dataset-v1",
    ) -> str:

        if not dataset_version:
            raise ValueError("dataset_version cannot be empty")

        with mlflow.start_run() as run:

            mlflow.set_tags({
                "model_name": model_metrics.model_name,
                "model_version": model_metrics.version,
                "dataset_version": dataset_version,
            })

            mlflow.log_metrics(model_metrics.metrics)

            return run.info.run_id