from pathlib import Path

from app.services.rag.document_loader import DocumentLoader
from app.services.rag.chunker import TextChunker
from app.services.rag.embedding_service import EmbeddingService
from app.services.rag.vector_store import (
    SearchResult,
    VectorStore,
)


class RAGService:
    """Coordinates document ingestion and knowledge retrieval."""

    def __init__(
        self,
        knowledge_base_path: str | Path,
        document_loader: DocumentLoader | None = None,
        chunker: TextChunker | None = None,
        embedding_service: EmbeddingService | None = None,
        vector_store: VectorStore | None = None,
    ):
        self.document_loader = (
            document_loader
            or DocumentLoader(knowledge_base_path)
        )

        self.chunker = (
            chunker
            or TextChunker()
        )

        self.embedding_service = (
            embedding_service
            or EmbeddingService()
        )

        self.vector_store = (
            vector_store
            or VectorStore()
        )

        self._initialized = False

    def ingest(self) -> int:
        """Load, chunk, embed, and index the knowledge base."""

        documents = (
            self.document_loader.load_documents()
        )

        chunks = self.chunker.chunk_documents(
            documents
        )

        if not chunks:
            self._initialized = True
            return 0

        texts = [
            chunk.content
            for chunk in chunks
        ]

        embeddings = (
            self.embedding_service.embed_documents(
                texts
            )
        )

        if len(embeddings) != len(chunks):
            raise RuntimeError(
                "Number of embeddings does not match "
                "number of chunks"
            )

        for chunk, embedding in zip(
            chunks,
            embeddings,
        ):
            self.vector_store.add(
                chunk_id=chunk.chunk_id,
                source=chunk.source,
                content=chunk.content,
                embedding=embedding,
            )

        self._initialized = True

        return len(chunks)

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[SearchResult]:
        """Retrieve the most relevant knowledge chunks."""

        if not query or not query.strip():
            raise ValueError(
                "query cannot be empty"
            )

        if top_k <= 0:
            raise ValueError(
                "top_k must be greater than 0"
            )

        if not self._initialized:
            self.ingest()

        query_embedding = (
            self.embedding_service.embed_text(
                query
            )
        )

        return self.vector_store.search(
            query_embedding=query_embedding,
            top_k=top_k,
        )