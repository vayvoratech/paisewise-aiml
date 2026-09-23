
import chromadb
from pathlib import Path

from .embeddings import create_embedding


# ==================================================
# Project Paths
# ==================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

CHROMA_DB_PATH = PROJECT_ROOT / "chroma_db"


# ==================================================
# Test Questions
# ==================================================

questions = [
    "What is a mutual fund?",
    "What is SIP?",
    "What does NAV mean?",
    "What is an equity fund?",
    "What is the expense ratio of a mutual fund?",
    "What is the difference between saving and investing?",
    "What is investment risk?",
    "Why is diversification important?",
    "What are mutual fund categories?",
    "How does a Systematic Investment Plan work?",
    "What is an investor's risk tolerance?",
    "What are the benefits of long-term investing?",
    "What is an asset?",
    "What is a debt fund?",
    "What is the meaning of financial planning?",
    "What is the purpose of an emergency fund?",
    "What is a financial goal?",
    "What is the meaning of return on investment?",
    "Why should investors understand investment products?",
    "What is the difference between different types of mutual funds?"
]


# ==================================================
# Retrieval Test
# ==================================================

def test_retrieval():

    print("\n" + "=" * 60)
    print("PAISEWISE RETRIEVAL TEST")
    print("=" * 60)

    # --------------------------------------------------
    # Connect to ChromaDB
    # --------------------------------------------------

    client = chromadb.PersistentClient(
        path=str(CHROMA_DB_PATH)
    )

    collection = client.get_collection(
        name="paisewise_knowledge_base"
    )

    document_count = collection.count()

    print(
        "\nDocuments available:",
        document_count
    )

    # --------------------------------------------------
    # Make sure knowledge base is not empty
    # --------------------------------------------------

    assert document_count > 0, (
        "PaiseWise knowledge base is empty."
    )

    # --------------------------------------------------
    # Test every question
    # --------------------------------------------------

    for number, question in enumerate(
        questions,
        start=1
    ):

        question_embedding = create_embedding(
            question
        )

        results = collection.query(
            query_embeddings=[
                question_embedding
            ],
            n_results=min(
                3,
                document_count
            )
        )

        documents = results["documents"][0]

        distances = results["distances"][0]

        # --------------------------------------------------
        # Validate retrieval
        # --------------------------------------------------

        assert len(documents) > 0, (
            f"No documents retrieved for: {question}"
        )

        print("\n" + "=" * 60)

        print(
            f"Question {number}: {question}"
        )

        print("=" * 60)

        for i, document in enumerate(
            documents,
            start=1
        ):

            print(
                f"\nResult {i}"
            )

            print(
                "Similarity distance:",
                round(
                    distances[i - 1],
                    4
                )
            )

            print(
                "Retrieved content:"
            )

            print(
                document[:500]
            )

    # --------------------------------------------------
    # Final validation
    # --------------------------------------------------

    print("\n" + "=" * 60)
    print("RETRIEVAL TEST PASSED")
    print("=" * 60)

    assert True
