import chromadb

from pathlib import Path

from .embeddings import create_embedding
from .reranker import rerank_results

# --------------------------------------------------
# Project paths
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

CHROMA_DB_PATH = PROJECT_ROOT / "chroma_db"


# --------------------------------------------------
# Reranker Test
# --------------------------------------------------

def test_reranker():

    print("\n" + "=" * 60)
    print("PaiseWise Reranker Test")
    print("=" * 60)

    # Connect to ChromaDB
    client = chromadb.PersistentClient(
        path=str(CHROMA_DB_PATH)
    )

    # Get PaiseWise knowledge collection
    collection = client.get_collection(
        name="paisewise_knowledge_base"
    )

    # Check documents
    document_count = collection.count()

    print("\nDocuments available:", document_count)

    assert document_count > 0, (
        "PaiseWise knowledge base is empty."
    )

    # --------------------------------------------------
    # Test question
    # --------------------------------------------------

    question = "What is SIP?"

    print("\nQuestion:", question)

    # Create embedding
    question_embedding = create_embedding(question)

    # Retrieve top 10 documents
    number_to_retrieve = min(
        10,
        document_count
    )

    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=number_to_retrieve
    )

    documents = results["documents"][0]

    print(
        "\nDocuments retrieved:",
        len(documents)
    )

    assert len(documents) > 0, (
        "No documents were retrieved from ChromaDB."
    )

    # --------------------------------------------------
    # Reranking
    # --------------------------------------------------

    ranked_results = rerank_results(
        question,
        documents
    )

    print(
        "\nDocuments after reranking:",
        len(ranked_results)
    )

    assert ranked_results, (
        "Reranker returned no results."
    )

    # --------------------------------------------------
    # Display results
    # --------------------------------------------------

    print("\n" + "-" * 60)
    print("RERANKED RESULTS")
    print("-" * 60)

    for number, (document, score) in enumerate(
        ranked_results,
        start=1
    ):
        print(f"\nRank {number}")
        print(f"Score: {score}")
        print(f"Document: {document[:300]}")

    print("\n" + "=" * 60)
    print("Reranker test completed successfully.")
    print("=" * 60)
