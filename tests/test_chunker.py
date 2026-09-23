import pytest

from app.services.rag.chunker import (
    TextChunker,
)


def test_chunk_document():

    chunker = TextChunker(
        chunk_size=20,
        chunk_overlap=5,
    )

    content = (
        "This is a sample document "
        "used to test our chunking logic."
    )

    chunks = chunker.chunk_document(
        source="sample.txt",
        content=content,
    )

    assert len(chunks) > 1

    assert chunks[0].source == "sample.txt"

    assert chunks[0].chunk_id == "sample.txt:0"

    assert all(
        chunk.content
        for chunk in chunks
    )


def test_empty_document_returns_no_chunks():

    chunker = TextChunker()

    chunks = chunker.chunk_document(
        source="empty.txt",
        content="",
    )

    assert chunks == []


def test_empty_source_is_rejected():

    chunker = TextChunker()

    with pytest.raises(ValueError):
        chunker.chunk_document(
            source="",
            content="Some content",
        )


def test_invalid_chunk_size():

    with pytest.raises(ValueError):
        TextChunker(
            chunk_size=0,
            chunk_overlap=0,
        )


def test_invalid_overlap():

    with pytest.raises(ValueError):
        TextChunker(
            chunk_size=100,
            chunk_overlap=100,
        )


def test_chunk_multiple_documents():

    chunker = TextChunker(
        chunk_size=50,
        chunk_overlap=10,
    )

    documents = [
        {
            "source": "etf.txt",
            "content": "ETF information.",
        },
        {
            "source": "bond.txt",
            "content": "Bond information.",
        },
    ]

    chunks = chunker.chunk_documents(
        documents
    )

    assert len(chunks) == 2

    assert chunks[0].source == "etf.txt"
    assert chunks[1].source == "bond.txt"