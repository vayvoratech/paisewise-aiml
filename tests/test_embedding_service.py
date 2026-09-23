from app.services.rag.embedding_service import (
    EmbeddingService,
)


def test_embed_text():

    service = EmbeddingService()

    embedding = service.embed_text(
        "What is an ETF?"
    )

    assert isinstance(embedding, list)

    assert len(embedding) > 0

    assert all(
        isinstance(value, float)
        for value in embedding
    )


def test_similar_texts_have_embeddings():

    service = EmbeddingService()

    first = service.embed_text(
        "What is an ETF?"
    )

    second = service.embed_text(
        "Explain exchange traded funds."
    )

    assert len(first) == len(second)


def test_embed_documents():

    service = EmbeddingService()

    embeddings = service.embed_documents(
        [
            "What is an ETF?",
            "What is a bond?",
        ]
    )

    assert len(embeddings) == 2

    assert len(embeddings[0]) > 0

    assert len(embeddings[0]) == len(
        embeddings[1]
    )