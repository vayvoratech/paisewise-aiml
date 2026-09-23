def chunk_text(text, chunk_size=200, overlap=50):
    """
    Split lesson text into smaller chunks.
    Each chunk contains up to 200 words.
    """

    words = text.split()
    chunks = []

    start = 0

    while start < len(words):

        end = start + chunk_size

        chunk = " ".join(words[start:end])

        chunks.append(chunk)

        start = end - overlap

        if start < 0:
            start = 0

    return chunks