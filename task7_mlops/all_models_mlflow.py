import mlflow

from task7_mlops.model_registry import Task7ModelRegistry


class AllModelsMLflowTracker:
    """
    Tracks version metadata for all five Task 7 components in MLflow.

    Existing application files are not modified.
    """

    def __init__(
        self,
        tracking_uri: str,
        experiment_name: str = "Task7_All_Models",
    ) -> None:
        if not tracking_uri:
            raise ValueError("tracking_uri cannot be empty")

        mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment_name)

        self.tracking_uri = mlflow.get_tracking_uri()
        self.experiment_name = experiment_name
        self.registry = Task7ModelRegistry()

        # LLM-based components
        self.llm_models = {
            "News Sentiment": {
                "model_name": "News Sentiment",
                "model_version": "v1",
                "model_type": "llm_based",
            },
            "Portfolio Health": {
                "model_name": "Portfolio Health",
                "model_version": "v1",
                "model_type": "llm_based",
            },
        }

    def track_model(
        self,
        model_name: str,
        metrics: dict[str, float] | None = None,
        dataset_version: str = "dataset-v1",
    ) -> str:
        """
        Track one model/component in MLflow.
        """

        if model_name in self.llm_models:
            model_name_value = self.llm_models[model_name]["model_name"]
            model_version = self.llm_models[model_name]["model_version"]
            model_type = self.llm_models[model_name]["model_type"]

        else:
            model = self.registry.get_model(model_name)

            model_name_value = model.name
            model_version = model.version
            model_type = model.model_type

        with mlflow.start_run() as run:

            mlflow.set_tag(
                "model_name",
                model_name_value,
            )

            mlflow.set_tag(
                "model_version",
                model_version,
            )

            mlflow.set_tag(
                "model_type",
                model_type,
            )

            mlflow.set_tag(
                "dataset_version",
                dataset_version,
            )

            if metrics:
                mlflow.log_metrics(
                    {
                        key: float(value)
                        for key, value in metrics.items()
                    }
                )

            return run.info.run_id

    def track_all(
        self,
        dataset_version: str = "dataset-v1",
    ) -> dict[str, str]:
        """
        Track all five Task 7 components.
        """

        run_ids: dict[str, str] = {}

        # Track synchronous components
        for model_name in self.registry.list_models():

            run_ids[model_name] = self.track_model(
                model_name=model_name,
                dataset_version=dataset_version,
            )

        # Track LLM-based components
        for model_name in self.llm_models:

            run_ids[model_name] = self.track_model(
                model_name=model_name,
                dataset_version=dataset_version,
            )

        return run_ids