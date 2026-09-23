import chromadb

from pathlib import Path

from .embeddings import create_embedding

# ==================================================
# Project Paths
# ==================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

CHROMA_DB_PATH = PROJECT_ROOT / "chroma_db"


# ==================================================
# Hindi Questions
# ==================================================

hindi_questions = [
    "म्यूचुअल फंड क्या है?",
    "SIP कैसे काम करता है?",
    "NAV का मतलब क्या है?",
    "एक्सपेंस रेशियो क्या होता है?",
    "इक्विटी फंड क्या है?",
    "डेट फंड क्या होता है?",
    "हाइब्रिड फंड क्या है?",
    "म्यूचुअल फंड में निवेश कैसे काम करता है?",
    "शेयर क्या होता है?",
    "स्टॉक मार्केट क्या है?",
    "KYC क्या है?",
    "Demat अकाउंट क्या होता है?",
    "SEBI क्या है?",
    "AMFI क्या है?",
    "महंगाई हमारे पैसों को कैसे प्रभावित करती है?",
    "कंपाउंड इंटरेस्ट क्या है?",
    "लिक्विडिटी का क्या मतलब है?",
    "डाइवर्सिफिकेशन क्यों जरूरी है?",
    "निवेश में जोखिम क्या होता है?",
    "बचत और निवेश में क्या अंतर है?"
]


# ==================================================
# Hindi Retrieval Test
# ==================================================

def test_hindi_retrieval():

    print("\n" + "=" * 60)
    print("HINDI RETRIEVAL TEST")
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

    print("\nDocuments available:", document_count)

    # --------------------------------------------------
    # Make sure database is not empty
    # --------------------------------------------------

    assert document_count > 0, (
        "PaiseWise knowledge base is empty."
    )

    print(
        "Total Hindi questions:",
        len(hindi_questions)
    )

    # --------------------------------------------------
    # Test Hindi questions
    # --------------------------------------------------

    for number, question in enumerate(
        hindi_questions,
        start=1
    ):

        print("\n" + "=" * 60)
        print(
            f"Question {number}: {question}"
        )
        print("=" * 60)

        # Create embedding
        question_embedding = create_embedding(
            question
        )

        # Retrieve top 3 documents
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
        # Validate results
        # --------------------------------------------------

        assert len(documents) > 0, (
            f"No documents retrieved for: {question}"
        )

        print("\nRetrieved results:")

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
                document[:300]
            )

        print(
            "\nResponse should be: Hindi"
        )

    # --------------------------------------------------
    # Final result
    # --------------------------------------------------

    print("\n" + "=" * 60)
    print("HINDI RETRIEVAL TEST PASSED")
    print("=" * 60)

    assert True
