from sentence_transformers import SentenceTransformer, util


# Load the model used for comparing the question and documents
model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")


def rerank_results(question, documents):

    # Convert the question into an embedding
    question_embedding = model.encode(
        question,
        convert_to_tensor=True
    )

    ranked_results = []

    # Compare the question with every retrieved document
    for document in documents:

        document_embedding = model.encode(
            document,
            convert_to_tensor=True
        )

        # Calculate similarity score
        score = util.cos_sim(
            question_embedding,
            document_embedding
        ).item()

        ranked_results.append(
            (document, score)
        )

    # Put the most relevant document first
    ranked_results.sort(
        key=lambda item: item[1],
        reverse=True
    )

    return ranked_results