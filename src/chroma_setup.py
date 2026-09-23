import chromadb

# Connect to a local ChromaDB database
client = chromadb.PersistentClient(path="./chroma_db")

# Create the collection if it doesn't already exist
knowledge_base = client.get_or_create_collection(
    name="paisewise_knowledge_base"
)

print("ChromaDB collection created successfully!")
print("Collection name:", knowledge_base.name)
print("Number of documents:", knowledge_base.count())