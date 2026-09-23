import os
import chromadb

from chunking import chunk_text
from embeddings import create_embedding


# Connect to our existing ChromaDB
client = chromadb.PersistentClient(
    path="../chroma_db"
)

collection = client.get_collection(
    name="paisewise_knowledge_base"
)

# Location of lesson files
lesson_folder = "../data/lessons"

# Get documents already stored in ChromaDB
stored_data = collection.get()

existing_lessons = []

for metadata in stored_data["metadatas"]:

    if metadata["type"] == "lesson":
        existing_lessons.append(
            metadata["source"]
        )


print("Checking for new lessons...")


# Check all files in the lessons folder
for filename in os.listdir(lesson_folder):

    if filename.startswith("."):
        continue

    # If lesson is already stored, skip it
    if filename in existing_lessons:

        print(
            f"Already exists: {filename}"
        )

        continue


    # Read the new lesson
    file_path = os.path.join(
        lesson_folder,
        filename
    )

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as file:

        content = file.read()


    # Split lesson into chunks
    chunks = chunk_text(
        content,
        chunk_size=200,
        overlap=50
    )

    # Store each chunk
    for number, chunk in enumerate(
        chunks,
        start=1
    ):

        embedding = create_embedding(
            chunk
        )

        collection.add(
            ids=[
                f"lesson_{filename}_{number}"
            ],
            documents=[chunk],
            embeddings=[embedding],
            metadatas=[{
                "source": filename,
                "type": "lesson",
                "chunk": number
            }]
        )

    print(
        f"New lesson added: {filename}"
    )

print("\nKnowledge base refresh completed.")
print(
    "Total documents:",
    collection.count()
)