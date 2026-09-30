import mlflow

from task7_mlops.model_versioning import ModelVersion


class Task7MLflowRegistry:
    """MLflow tracking and registry for Task 7 models."""

    def __init__(self, tracking_uri: str):
        if not tracking_uri:
            raise ValueError("tracking_uri cannot be empty")

        mlflow.set_tracking_uri(tracking_uri)
        self.tracking_uri = mlflow.get_tracking_uri()

    def track_model(
        self,
        model_version: ModelVersion,
        experiment_name: str = "Task7_Model_Lifecycle",
    ):
        mlflow.set_experiment(experiment_name)

        with mlflow.start_run() as run:
            mlflow.set_tag(
                "model_name",
                model_version.model_name,
            )

            mlflow.set_tag(
                "model_version",
                model_version.version,
            )

            mlflow.set_tag(
                "dataset_version",
                model_version.dataset_version,
            )

            mlflow.set_tag(
                "created_at",
                model_version.created_at,
            )

            mlflow.log_metrics(model_version.metrics)

            return run.info.run_id

    def register_model(
        self,
        model_uri: str,
        registered_name: str,
    ):
        if not model_uri:
            raise ValueError("model_uri cannot be empty")

        if not registered_name:
            raise ValueError(
                "registered_name cannot be empty"
            )

        return mlflow.register_model(
            model_uri=model_uri,
            name=registered_name,
        )