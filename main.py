from src.chunking import chunk_text


sample_text = """
Saving and investing are two important parts of managing personal finances.
Saving generally involves keeping money aside for short-term needs and emergencies.
Investing involves putting money into financial assets with the expectation of generating
returns over time. The choice between saving and investing depends on factors such as
financial goals, time horizon, and risk tolerance.

A person may choose to maintain savings for unexpected expenses while considering
investments for longer-term goals. Different investment products have different levels
of risk and return potential. Understanding these differences can help an individual
make informed financial decisions.
"""


chunks = chunk_text(
    sample_text,
    chunk_size=200,
    overlap=50
)


print("Number of chunks:", len(chunks))

for i, chunk in enumerate(chunks, start=1):
    print(f"\n--- Chunk {i} ---")
    print(chunk)
    print("Word count:", len(chunk.split()))
    