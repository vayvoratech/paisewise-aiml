import chromadb
from sentence_transformers import SentenceTransformer


# Load embedding model
model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

# Connect to ChromaDB
client = chromadb.PersistentClient(path="../chroma_db")

collection = client.get_collection(
    name="paisewise_knowledge_base"
)


# Test questions
questions = [
    "What is SIP?",
    "What is NAV?",
    "What is Expense Ratio?",
    "What is an Equity Fund?"
]


for question in questions:

    print(f"\nQuestion: {question}")

    # Generate embedding for the question
    query_embedding = model.encode(question).tolist()

    # Retrieve only the most relevant document
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=1
    )

    # Get the top result
    retrieved_document = results["documents"][0][0]

    print("Retrieved context:")
    print(retrieved_document)

    # Check whether an answer was retrieved
    if retrieved_document:
        print("Answer found: YES")
    else:
        print("Answer found: NO")

    print("-" * 50)