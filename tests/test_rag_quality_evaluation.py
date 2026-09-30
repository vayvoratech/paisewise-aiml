from app.services.rag.rag_service import RAGService
from app.services.rag.vector_store import VectorStore


def test_rag_retrieves_relevant_context():
    vector_store = VectorStore()

    vector_store.add(
        chunk_id="etf:0",
        source="etf.txt",
        content="An ETF is an exchange-traded fund that can hold a diversified collection of assets.",
        embedding=[1.0, 0.0, 0.0],
    )

    vector_store.add(
        chunk_id="bond:0",
        source="bond.txt",
        content="A bond is a debt instrument issued by a borrower.",
        embedding=[0.0, 1.0, 0.0],
    )

    results = vector_store.search(
        query_embedding=[1.0, 0.0, 0.0],
        top_k=2,
    )

    assert results
    assert results[0].chunk_id == "etf:0"
    assert "ETF" in results[0].content


def test_rag_returns_results_in_similarity_order():
    vector_store = VectorStore()

    vector_store.add(
        chunk_id="high:0",
        source="high.txt",
        content="Relevant financial information.",
        embedding=[1.0, 0.0, 0.0],
    )

    vector_store.add(
        chunk_id="medium:0",
        source="medium.txt",
        content="Somewhat related financial information.",
        embedding=[0.7, 0.7, 0.0],
    )

    vector_store.add(
        chunk_id="low:0",
        source="low.txt",
        content="Less related information.",
        embedding=[0.0, 1.0, 0.0],
    )

    results = vector_store.search(
        query_embedding=[1.0, 0.0, 0.0],
        top_k=3,
    )

    assert len(results) == 3
    assert results[0].score >= results[1].score
    assert results[1].score >= results[2].score