from sentence_transformers import SentenceTransformer


# Load the embedding model
model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")


def create_embedding(text):

    embedding = model.encode(text)

    return embedding.tolist()