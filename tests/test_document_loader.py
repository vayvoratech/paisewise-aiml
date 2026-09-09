from pathlib import Path

import pytest

from app.services.rag.document_loader import DocumentLoader


def test_load_documents(tmp_path: Path):
    knowledge_base = tmp_path / "knowledge_base"
    knowledge_base.mkdir()

    (knowledge_base / "b.txt").write_text(
        "Bond information.",
        encoding="utf-8",
    )

    (knowledge_base / "a.txt").write_text(
        "ETF information.",
        encoding="utf-8",
    )

    loader = DocumentLoader(knowledge_base)

    documents = loader.load_documents()

    assert len(documents) == 2

    assert documents[0]["source"] == "a.txt"
    assert documents[0]["content"] == "ETF information."

    assert documents[1]["source"] == "b.txt"
    assert documents[1]["content"] == "Bond information."


def test_missing_knowledge_base():
    loader = DocumentLoader(
        "does_not_exist"
    )

    with pytest.raises(FileNotFoundError):
        loader.load_documents()


def test_empty_documents_are_skipped(tmp_path: Path):
    knowledge_base = tmp_path / "knowledge_base"
    knowledge_base.mkdir()

    (knowledge_base / "empty.txt").write_text(
        "",
        encoding="utf-8",
    )

    (knowledge_base / "valid.txt").write_text(
        "Valid knowledge.",
        encoding="utf-8",
    )

    loader = DocumentLoader(knowledge_base)

    documents = loader.load_documents()

    assert len(documents) == 1
    assert documents[0]["source"] == "valid.txt"