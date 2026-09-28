import mlflow
from sentence_transformers import SentenceTransformer

TRACKING_URI = "postgresql://postgres:root123@localhost:5432/mlflow"

mlflow.set_tracking_uri(TRACKING_URI)

mlflow.set_experiment("Task7_RAG_Model_Registry")

model_name = "all-MiniLM-L6-v2"
registry_name = "RAGEmbeddingModel"

model = SentenceTransformer(model_name)

with mlflow.start_run() as run:

    # Model version information
    mlflow.set_tag("model_name", model_name)
    mlflow.set_tag("model_version", "v1")
    mlflow.set_tag("dataset_version", "v1")

    # Model information
    mlflow.log_param("model_type", "SentenceTransformer")
    mlflow.log_param("model_name", model_name)

    # Model metric
    embedding_dimension = model.get_sentence_embedding_dimension()
    mlflow.log_metric(
        "embedding_dimension",
        float(embedding_dimension)
    )

    # Log the actual model
    model_info = mlflow.sentence_transformers.log_model(
        model,
        name="rag_embedding_model"
    )

    print("Run ID:", run.info.run_id)
    print("Model URI:", model_info.model_uri)

    # Register model
    registered_model = mlflow.register_model(
        model_uri=model_info.model_uri,
        name=registry_name
    )

    print("Registered model:", registered_model.name)
    print("Registered version:", registered_model.version)

print("Model registration successful")