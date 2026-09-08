from .embeddings import create_embedding


def test_embedding():
    text = "What is a mutual fund?"

    embedding = create_embedding(text)

    assert embedding is not None
    assert len(embedding) > 0

    print("\nEmbedding created successfully.")
    print("Embedding length:", len(embedding))
