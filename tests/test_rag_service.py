import pytest

from app.services.rag.rag_service import RAGService


class FakeEmbeddingService:
    def __init__(self):
        self.embed_documents_calls = 0
        self.embed_text_calls = 0

    def embed_documents(self, texts):
        self.embed_documents_calls += 1

        return [
            [1.0, 0.0, 0.0]
            for _ in texts
        ]

    def embed_text(self, text):
        self.embed_text_calls += 1

        return [1.0, 0.0, 0.0]


class FailingEmbeddingService:
    def embed_documents(self, texts):
        raise RuntimeError("Embedding service unavailable")

    def embed_text(self, text):
        raise RuntimeError("Embedding service unavailable")


class FakeDocumentLoader:
    def load_documents(self):
        return [
            {
                "source": "etf.txt",
                "content": "ETF information.",
            },
            {
                "source": "bond.txt",
                "content": "Bond information.",
            },
        ]


class EmptyDocumentLoader:
    def load_documents(self):
        return []


class FailingDocumentLoader:
    def load_documents(self):
        raise RuntimeError(
            "Knowledge base unavailable"
        )


def create_service(
    loader=None,
    embedding_service=None,
):
    return RAGService(
        knowledge_base_path="unused",
        document_loader=(
            loader or FakeDocumentLoader()
        ),
        embedding_service=(
            embedding_service
            or FakeEmbeddingService()
        ),
    )


def test_ingest():

    service = create_service()

    count = service.ingest()

    assert count == 2
    assert service.vector_store.count() == 2


def test_retrieve():

    service = create_service()

    service.ingest()

    results = service.retrieve(
        "What is an ETF?",
        top_k=5,
    )

    assert len(results) == 2


def test_retrieve_returns_fewer_than_five_when_only_two_exist():

    service = create_service()

    service.ingest()

    results = service.retrieve(
        "What is an ETF?",
        top_k=5,
    )

    assert len(results) <= 5


def test_empty_query_is_rejected():

    service = create_service()

    with pytest.raises(ValueError):
        service.retrieve("")


def test_whitespace_query_is_rejected():

    service = create_service()

    with pytest.raises(ValueError):
        service.retrieve("   ")


def test_zero_top_k_is_rejected():

    service = create_service()

    with pytest.raises(ValueError):
        service.retrieve(
            "What is an ETF?",
            top_k=0,
        )


def test_negative_top_k_is_rejected():

    service = create_service()

    with pytest.raises(ValueError):
        service.retrieve(
            "What is an ETF?",
            top_k=-1,
        )


def test_empty_knowledge_base():

    service = create_service(
        loader=EmptyDocumentLoader()
    )

    count = service.ingest()

    assert count == 0
    assert service.vector_store.count() == 0


def test_retrieve_from_empty_knowledge_base():

    service = create_service(
        loader=EmptyDocumentLoader()
    )

    results = service.retrieve(
        "What is an ETF?",
        top_k=5,
    )

    assert results == []


def test_document_loader_failure_is_propagated():

    service = create_service(
        loader=FailingDocumentLoader()
    )

    with pytest.raises(RuntimeError):
        service.ingest()


def test_embedding_failure_is_propagated():

    service = create_service(
        embedding_service=FailingEmbeddingService()
    )

    with pytest.raises(RuntimeError):
        service.ingest()


def test_ingestion_is_not_repeated_on_every_retrieval():

    embedding_service = FakeEmbeddingService()

    service = create_service(
        embedding_service=embedding_service
    )

    service.retrieve(
        "What is an ETF?"
    )

    service.retrieve(
        "What is a bond?"
    )

    assert (
        embedding_service.embed_documents_calls
        == 1
    )

    assert (
        embedding_service.embed_text_calls
        == 2
    )


def test_ingestion_returns_number_of_chunks():

    service = create_service()

    count = service.ingest()

    assert count == 2


def test_retrieval_result_contains_source():

    service = create_service()

    service.ingest()

    results = service.retrieve(
        "What is an ETF?"
    )

    assert len(results) > 0

    assert results[0].source
    assert results[0].content
    assert results[0].chunk_id