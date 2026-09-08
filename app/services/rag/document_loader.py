from pathlib import Path
from typing import TypedDict


class Document(TypedDict):
    source: str
    content: str


class DocumentLoader:
    """Loads text documents from the RAG knowledge base."""

    def __init__(self, knowledge_base_path: str | Path):
        self.knowledge_base_path = Path(knowledge_base_path)

    def load_documents(self) -> list[Document]:
        if not self.knowledge_base_path.exists():
            raise FileNotFoundError(
                f"Knowledge base not found: {self.knowledge_base_path}"
            )

        if not self.knowledge_base_path.is_dir():
            raise NotADirectoryError(
                f"Knowledge base path is not a directory: "
                f"{self.knowledge_base_path}"
            )

        documents: list[Document] = []

        for file_path in sorted(
            self.knowledge_base_path.glob("*.txt")
        ):
            content = file_path.read_text(
                encoding="utf-8"
            ).strip()

            if not content:
                continue

            documents.append(
                {
                    "source": file_path.name,
                    "content": content,
                }
            )

        return documents