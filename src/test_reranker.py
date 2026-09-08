import chromadb

from embeddings import create_embedding
from reranker import rerank_results


# Connect to our ChromaDB database
client = chromadb.PersistentClient(
    path="../chroma_db"
)


# Open the PaiseWise knowledge base
collection = client.get_collection(
    name="paisewise_knowledge_base"
)


print("Documents available:", collection.count())


# Question to test
question = "What is SIP?"


# Convert the question into an embedding
question_embedding = create_embedding(question)


# Retrieve available documents
number_to_retrieve = min(10, collection.count())

results = collection.query(
    query_embeddings=[question_embedding],
    n_results=number_to_retrieve
)


documents = results["documents"][0]


print("\nQuestion:", question)

print("\nInitial retrieved results:")
print("Number of results:", len(documents))


for i, document in enumerate(
    documents,
    start=1
):

    print(f"\nInitial Result {i}:")
    print(document[:300])


# Re-rank the retrieved documents
ranked_results = rerank_results(
    question,
    documents
)


print("\n" + "=" * 60)
print("Re-ranked results")
print("=" * 60)


for number, (document, score) in enumerate(
    ranked_results,
    start=1
):

    print(f"\nResult {number}")
    print("Relevance score:", round(score, 4))
    print("Content:", document[:300])