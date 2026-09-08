from dataclasses import dataclass


@dataclass(frozen=True)
class DocumentChunk:
    chunk_id: str
    source: str
    content: str


class TextChunker:
    """Splits knowledge-base documents into overlapping text chunks."""

    def __init__(
        self,
        chunk_size: int = 800,
        chunk_overlap: int = 100,
    ):
        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than 0")

        if chunk_overlap < 0:
            raise ValueError(
                "chunk_overlap cannot be negative"
            )

        if chunk_overlap >= chunk_size:
            raise ValueError(
                "chunk_overlap must be smaller than chunk_size"
            )

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_document(
        self,
        source: str,
        content: str,
    ) -> list[DocumentChunk]:

        if not source.strip():
            raise ValueError("source cannot be empty")

        if not content.strip():
            return []

        text = content.strip()
        chunks: list[DocumentChunk] = []

        start = 0
        chunk_number = 0

        while start < len(text):
            end = min(
                start + self.chunk_size,
                len(text),
            )

            chunk_text = text[start:end].strip()

            if chunk_text:
                chunks.append(
                    DocumentChunk(
                        chunk_id=f"{source}:{chunk_number}",
                        source=source,
                        content=chunk_text,
                    )
                )

            if end >= len(text):
                break

            start = end - self.chunk_overlap
            chunk_number += 1

        return chunks

    def chunk_documents(
        self,
        documents: list[dict[str, str]],
    ) -> list[DocumentChunk]:

        chunks: list[DocumentChunk] = []

        for document in documents:
            chunks.extend(
                self.chunk_document(
                    source=document["source"],
                    content=document["content"],
                )
            )

        return chunks