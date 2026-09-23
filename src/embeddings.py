from sentence_transformers import SentenceTransformer


# Model is loaded only when create_embedding() is called
model = None


def get_model():
    global model

    if model is None:
        model = SentenceTransformer(
            "paraphrase-multilingual-MiniLM-L12-v2"
        )

    return model


def create_embedding(text):
    embedding_model = get_model()

    embedding = embedding_model.encode(text)

    return embedding.tolist()
