import os
import chromadb

from sentence_transformers import SentenceTransformer
from chunking import chunk_text


# Create ChromaDB
client = chromadb.PersistentClient(
    path="../chroma_db"
)

collection = client.get_or_create_collection(
    name="paisewise_knowledge_base"
)


# Load embedding model
model = SentenceTransformer(
    "paraphrase-multilingual-MiniLM-L12-v2"
)


print("Starting document ingestion...")


# Add documents to ChromaDB
def add_document(text, source, doc_type):

    if doc_type == "jargon":

        # Each non-empty line becomes one document
        chunks = [
            line.strip()
            for line in text.splitlines()
            if line.strip()
        ]

    else:

        # Lessons are divided into 200-word chunks
        chunks = chunk_text(text)


    for number, chunk in enumerate(chunks, start=1):

        embedding = model.encode(chunk).tolist()

        document_id = f"{source}_{number}"

        collection.add(
            ids=[document_id],
            documents=[chunk],
            embeddings=[embedding],
            metadatas=[{
                "source": source,
                "type": doc_type,
                "chunk": number
            }]
        )

    print(
        f"Added {source}: {len(chunks)} chunks"
    )


# Load lessons
def load_lessons():

    lesson_folder = "../data/lessons"

    for filename in sorted(
        os.listdir(lesson_folder)
    ):

        file_path = os.path.join(
            lesson_folder,
            filename
        )

        if os.path.isfile(file_path):

            with open(
                file_path,
                "r",
                encoding="utf-8"
            ) as file:

                text = file.read()

            add_document(
                text,
                filename,
                "lesson"
            )


# Load jargon
def load_jargon():

    jargon_file = "../data/jargon/jargon.txt"

    with open(
        jargon_file,
        "r",
        encoding="utf-8"
    ) as file:

        text = file.read()

    add_document(
        text,
        "jargon.txt",
        "jargon"
    )


# Run ingestion
load_lessons()
load_jargon()


print("\nDocument ingestion completed.")

print(
    "Total documents in ChromaDB:",
    collection.count()
)