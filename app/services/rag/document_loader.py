from pathlib import Path
from typing import TypedDict


class Document(TypedDict):
    source: str
    content: str


class DocumentLoader:
    """Loads text documents from the complete local knowledge base."""

    def __init__(self, knowledge_base_path: str | Path):
        self.knowledge_base_path = Path(knowledge_base_path)

    def load_documents(self) -> list[Document]:
        if not self.knowledge_base_path.exists():
            raise FileNotFoundError(f"Knowledge base not found: {self.knowledge_base_path}")
        if not self.knowledge_base_path.is_dir():
            raise NotADirectoryError(f"Knowledge base path is not a directory: {self.knowledge_base_path}")

        documents: list[Document] = []
        for file_path in sorted(self.knowledge_base_path.rglob("*.txt")):
            content = file_path.read_text(encoding="utf-8").strip()
            if content:
                documents.append({"source": str(file_path.relative_to(self.knowledge_base_path)), "content": content})
        return documents
