import mlflow

TRACKING_URI = "postgresql://postgres:root123@localhost:5432/mlflow"

mlflow.set_tracking_uri(TRACKING_URI)

mlflow.set_experiment("Task7_RAG_Embedding")

with mlflow.start_run() as run:
    # Model version information
    mlflow.set_tag("model_name", "all-MiniLM-L6-v2")
    mlflow.set_tag("model_version", "v1")
    mlflow.set_tag("dataset_version", "v1")

    # Example model metric
    mlflow.log_metric("embedding_dimension", 384)

    # Additional model information
    mlflow.log_param("model_type", "SentenceTransformer")
    mlflow.log_param("purpose", "RAG document and query embeddings")

    print("Run ID:", run.info.run_id)
    print("MLflow tracking successful")

mlflow.end_run()