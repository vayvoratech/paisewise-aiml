from pathlib import Path

from app.services.rag.chunker import TextChunker
from app.services.rag.document_loader import DocumentLoader
from app.services.rag.embedding_service import EmbeddingService
from app.services.rag.reranker import Reranker
from app.services.rag.chroma_vector_store import ChromaVectorStore


class RAGService:
    def __init__(self, knowledge_base_path: str | Path, document_loader=None, chunker=None, embedding_service=None, vector_store=None, reranker=None):
        self.document_loader = document_loader or DocumentLoader(knowledge_base_path)
        self.chunker = chunker or TextChunker(chunk_size=200, chunk_overlap=40)
        self.embedding_service = embedding_service or EmbeddingService()
        self.vector_store = vector_store or ChromaVectorStore()
        self.reranker = reranker or Reranker()
        self._initialized = False

    def ingest(self) -> int:
        documents = self.document_loader.load_documents()
        chunks = self.chunker.chunk_documents(documents)
        if not chunks:
            self._initialized = True
            return 0
        embeddings = self.embedding_service.embed_documents([chunk.content for chunk in chunks])
        if len(embeddings) != len(chunks):
            raise RuntimeError("Number of embeddings does not match number of chunks")
        for chunk, embedding in zip(chunks, embeddings):
            self.vector_store.add(chunk.chunk_id, chunk.source, chunk.content, embedding)
        self._initialized = True
        return len(chunks)

    def refresh(self) -> int:
        self.vector_store = ChromaVectorStore()
        self._initialized = False
        return self.ingest()

    def retrieve(self, query: str, top_k: int = 5):
        if not query.strip():
            raise ValueError("query cannot be empty")
        if top_k <= 0:
            raise ValueError("top_k must be greater than 0")
        if not self._initialized:
            self.ingest()
        query_embedding = self.embedding_service.embed_text(query)
        initial = self.vector_store.search(query_embedding, top_k=max(10, top_k * 2))
        return self.reranker.rerank(query, initial, top_k=top_k)
