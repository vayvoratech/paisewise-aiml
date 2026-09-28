from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ChromaSearchResult:
    chunk_id: str
    source: str
    content: str
    score: float


class ChromaVectorStore:
    def __init__(
        self,
        path: str = "data/chroma",
        collection_name: str = "paisewise_knowledge_base",
    ):
        import chromadb

        Path(path).mkdir(parents=True, exist_ok=True)
        client = chromadb.PersistentClient(path=path)
        self.collection = client.get_or_create_collection(collection_name)

    def add(
        self,
        chunk_id: str,
        source: str,
        content: str,
        embedding: list[float],
    ) -> None:
        self.collection.upsert(
            ids=[chunk_id],
            embeddings=[embedding],
            documents=[content],
            metadatas=[{"source": source}],
        )

    def search(
        self,
        query_embedding: list[float],
        top_k: int = 10,
    ):
        result = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
        )

        ids = result.get("ids", [[]])[0]
        documents = result.get("documents", [[]])[0]
        metadatas = result.get("metadatas", [[]])[0]
        distances = result.get("distances", [[]])[0]

        output = []

        for index, chunk_id in enumerate(ids):
            distance = (
                float(distances[index])
                if distances
                else 0.0
            )

            output.append(
                ChromaSearchResult(
                    chunk_id,
                    metadatas[index].get("source", ""),
                    documents[index],
                    1.0 / (1.0 + distance),
                )
            )

        return output

    def count(self) -> int:
        return self.collection.count()
