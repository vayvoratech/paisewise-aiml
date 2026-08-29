from embeddings import create_embedding


text = "A mutual fund collects money from different investors and invests it in financial assets."

embedding = create_embedding(text)

print("Embedding created successfully.")
print("Number of values:", len(embedding))
print("First 5 values:", embedding[:5])