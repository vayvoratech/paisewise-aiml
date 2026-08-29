import chromadb

from embeddings import create_embedding


# Connect to ChromaDB
client = chromadb.PersistentClient(
    path="../chroma_db"
)

collection = client.get_collection(
    name="paisewise_knowledge_base"
)


# Hindi questions for multilingual testing
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


print("=" * 60)
print("HINDI RETRIEVAL TEST")
print("=" * 60)

print("Total Hindi questions:", len(hindi_questions))
print("Documents available:", collection.count())


for number, question in enumerate(
    hindi_questions,
    start=1
):

    print("\n" + "=" * 60)
    print(f"Question {number}: {question}")
    print("=" * 60)

    # Create embedding
    question_embedding = create_embedding(
        question
    )

    # Retrieve top 3 results
    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=3
    )

    documents = results["documents"][0]
    distances = results["distances"][0]

    print("\nRetrieved results:")

    for i, document in enumerate(
        documents,
        start=1
    ):

        print(f"\nResult {i}")
        print(
            "Similarity distance:",
            round(distances[i - 1], 4)
        )

        print("Retrieved content:")
        print(document[:300])

    print("\nResponse should be: Hindi")