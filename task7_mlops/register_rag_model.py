import mlflow
from sentence_transformers import SentenceTransformer


class RAGModelRegistrar:
    """
    Registers the actual RAG SentenceTransformer model in MLflow.

    Existing application files are not modified.
    """

    def __init__(
        self,
        tracking_uri: str,
        experiment_name: str = "Task7_RAG_Model_Registry",
        registered_model_name: str = "RAGEmbeddingModel",
    ) -> None:
        if not tracking_uri:
            raise ValueError("tracking_uri cannot be empty")

        mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment_name)

        self.registered_model_name = registered_model_name

    def register(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        model_version: str = "v1",
        dataset_version: str = "dataset-v1",
    ):
        model = SentenceTransformer(model_name)

        with mlflow.start_run() as run:
            mlflow.set_tag("model_name", "RAG Embedding")
            mlflow.set_tag("model_version", model_version)
            mlflow.set_tag("dataset_version", dataset_version)
            mlflow.set_tag("model_type", "sentence_transformer")

            mlflow.log_param(
                "embedding_model",
                model_name,
            )

            embedding_dimension = (
                model.get_sentence_embedding_dimension()
            )

            mlflow.log_metric(
                "embedding_dimension",
                float(embedding_dimension),
            )

            model_info = mlflow.sentence_transformers.log_model(
                model,
                name="rag_embedding_model",
            )

            registered_model = mlflow.register_model(
                model_uri=model_info.model_uri,
                name=self.registered_model_name,
            )

            print("Run ID:", run.info.run_id)
            print("Model URI:", model_info.model_uri)
            print(
                "Registered model:",
                registered_model.name,
            )
            print(
                "Registered version:",
                registered_model.version,
            )

            return registered_model