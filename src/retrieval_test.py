import chromadb
from embeddings import create_embedding


# Connect to the existing ChromaDB database
client = chromadb.PersistentClient(path="../chroma_db")

# Open the PaiseWise knowledge base
collection = client.get_collection(
    name="paisewise_knowledge_base"
)


# Questions used for testing
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


# Test every question
for number, question in enumerate(questions, start=1):

    # Convert the question into an embedding
    question_embedding = create_embedding(question)

    # Search ChromaDB for similar content
    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=3
    )

    print("\n" + "=" * 60)
    print(f"Question {number}: {question}")
    print("=" * 60)

    documents = results["documents"][0]
    distances = results["distances"][0]

    for i, document in enumerate(documents, start=1):
        print(f"\nResult {i}")
        print("Similarity distance:", distances[i - 1])
        print("Retrieved content:")
        print(document[:500])