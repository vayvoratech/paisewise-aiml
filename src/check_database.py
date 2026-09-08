import chromadb


# Connect to the same ChromaDB used by ingestion
client = chromadb.PersistentClient(
    path="../chroma_db"
)

collection = client.get_or_create_collection(
    name="paisewise_knowledge_base"
)


print("Collection name:", collection.name)
print("Number of documents:", collection.count())


# Get stored documents
data = collection.get(
    include=["documents", "metadatas"]
)


print("\nStored documents:")

for number, document in enumerate(
    data["documents"],
    start=1
):

    print(f"\nDocument {number}:")
    print(document)


print("\nMetadata:")

for metadata in data["metadatas"]:
    print(metadata)