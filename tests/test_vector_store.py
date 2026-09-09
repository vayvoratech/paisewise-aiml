import pytest

from app.services.rag.vector_store import (
    VectorStore,
)


def test_add_and_count():

    store = VectorStore()

    store.add(
        chunk_id="etf:0",
        source="etf.txt",
        content="ETF information",
        embedding=[1.0, 0.0, 0.0],
    )

    assert store.count() == 1


def test_search_returns_most_similar():

    store = VectorStore()

    store.add(
        chunk_id="etf:0",
        source="etf.txt",
        content="ETF information",
        embedding=[1.0, 0.0, 0.0],
    )

    store.add(
        chunk_id="bond:0",
        source="bond.txt",
        content="Bond information",
        embedding=[0.0, 1.0, 0.0],
    )

    results = store.search(
        query_embedding=[1.0, 0.0, 0.0],
        top_k=1,
    )

    assert len(results) == 1

    assert results[0].chunk_id == "etf:0"

    assert results[0].score > 0.99


def test_top_k_limits_results():

    store = VectorStore()

    for i in range(10):
        store.add(
            chunk_id=f"chunk:{i}",
            source="test.txt",
            content=f"Content {i}",
            embedding=[1.0, 0.0, 0.0],
        )

    results = store.search(
        query_embedding=[1.0, 0.0, 0.0],
        top_k=5,
    )

    assert len(results) == 5


def test_empty_store_returns_empty():

    store = VectorStore()

    results = store.search(
        query_embedding=[1.0, 0.0, 0.0],
        top_k=5,
    )

    assert results == []


def test_invalid_top_k():

    store = VectorStore()

    with pytest.raises(ValueError):
        store.search(
            query_embedding=[1.0, 0.0, 0.0],
            top_k=0,
        )


def test_empty_embedding():

    store = VectorStore()

    with pytest.raises(ValueError):
        store.add(
            chunk_id="test:0",
            source="test.txt",
            content="Test",
            embedding=[],
        )

import pytest

from app.services.rag.vector_store import VectorStore


def test_search_with_top_k_greater_than_store_size():

    store = VectorStore()

    store.add(
        chunk_id="chunk:1",
        source="test.txt",
        content="First document",
        embedding=[1.0, 0.0, 0.0],
    )

    store.add(
        chunk_id="chunk:2",
        source="test.txt",
        content="Second document",
        embedding=[0.0, 1.0, 0.0],
    )

    results = store.search(
        query_embedding=[1.0, 0.0, 0.0],
        top_k=5,
    )

    assert len(results) == 2


def test_negative_top_k_is_rejected():

    store = VectorStore()

    with pytest.raises(ValueError):
        store.search(
            query_embedding=[1.0, 0.0, 0.0],
            top_k=-1,
        )


def test_zero_query_vector_is_rejected():

    store = VectorStore()

    store.add(
        chunk_id="chunk:1",
        source="test.txt",
        content="Test content",
        embedding=[1.0, 0.0, 0.0],
    )

    with pytest.raises(ValueError):
        store.search(
            query_embedding=[0.0, 0.0, 0.0],
            top_k=5,
        )


def test_empty_query_embedding_is_rejected():

    store = VectorStore()

    with pytest.raises(ValueError):
        store.search(
            query_embedding=[],
            top_k=5,
        )


def test_empty_chunk_id_is_rejected():

    store = VectorStore()

    with pytest.raises(ValueError):
        store.add(
            chunk_id="",
            source="test.txt",
            content="Test",
            embedding=[1.0, 0.0, 0.0],
        )


def test_empty_source_is_rejected():

    store = VectorStore()

    with pytest.raises(ValueError):
        store.add(
            chunk_id="chunk:1",
            source="",
            content="Test",
            embedding=[1.0, 0.0, 0.0],
        )


def test_empty_content_is_rejected():

    store = VectorStore()

    with pytest.raises(ValueError):
        store.add(
            chunk_id="chunk:1",
            source="test.txt",
            content="",
            embedding=[1.0, 0.0, 0.0],
        )


def test_empty_vector_store_returns_no_results():

    store = VectorStore()

    results = store.search(
        query_embedding=[1.0, 0.0, 0.0],
        top_k=5,
    )

    assert results == []


def test_results_are_sorted_by_similarity():

    store = VectorStore()

    store.add(
        chunk_id="low",
        source="low.txt",
        content="Low similarity",
        embedding=[0.0, 1.0, 0.0],
    )

    store.add(
        chunk_id="high",
        source="high.txt",
        content="High similarity",
        embedding=[1.0, 0.0, 0.0],
    )

    results = store.search(
        query_embedding=[1.0, 0.0, 0.0],
        top_k=2,
    )

    assert results[0].chunk_id == "high"
    assert results[1].chunk_id == "low"
    assert results[0].score >= results[1].score

def test_embedding_dimension_mismatch_is_rejected():

    store = VectorStore()

    store.add(
        chunk_id="chunk:1",
        source="test.txt",
        content="Test",
        embedding=[1.0, 0.0, 0.0],
    )

    with pytest.raises(ValueError):
        store.add(
            chunk_id="chunk:2",
            source="test.txt",
            content="Test 2",
            embedding=[1.0, 0.0],
        )


def test_query_dimension_mismatch_is_rejected():

    store = VectorStore()

    store.add(
        chunk_id="chunk:1",
        source="test.txt",
        content="Test",
        embedding=[1.0, 0.0, 0.0],
    )

    with pytest.raises(ValueError):
        store.search(
            query_embedding=[1.0, 0.0],
            top_k=5,
        )