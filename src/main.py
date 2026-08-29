from fastapi import FastAPI
from pydantic import BaseModel
import chromadb

from embeddings import create_embedding
from reranker import rerank_results
from guardrails import is_guardrail_question
from market_context import create_market_context


app = FastAPI(
    title="PaiseWise RAG API",
    description="Retrieval Augmented Generation API for PaiseWise",
    version="1.0.0"
)


# --------------------------------------------------
# Connect to ChromaDB
# --------------------------------------------------

client = chromadb.PersistentClient(
    path="../chroma_db"
)

collection = client.get_collection(
    name="paisewise_knowledge_base"
)


# --------------------------------------------------
# Request model
# --------------------------------------------------

class QuestionRequest(BaseModel):
    question: str


# --------------------------------------------------
# Home endpoint
# --------------------------------------------------

@app.get("/")
def home():
    return {
        "message": "PaiseWise RAG API is running"
    }


# --------------------------------------------------
# RAG Ask endpoint
# --------------------------------------------------

@app.post("/ask")
def ask_question(request: QuestionRequest):

    question = request.question.strip()

    # ----------------------------------------------
    # Check empty question
    # ----------------------------------------------

    if not question:
        return {
            "question": question,
            "answer": "Please enter a question."
        }

    # ----------------------------------------------
    # Step 1: Guardrail check
    # ----------------------------------------------

    if is_guardrail_question(question):

        return {
            "question": question,
            "answer": (
                "I can provide general financial education, "
                "but I cannot recommend specific stocks, mutual funds, "
                "SIPs, or tell you whether to buy or sell an investment."
            ),
            "guardrail_triggered": True
        }



# market 

@app.get("/market-context")
def get_market_context():

    sector_sentiment = {
        "IT": {
            "sentiment": "Positive",
            "score": 0.42
        },
        "Banking": {
            "sentiment": "Neutral",
            "score": 0.01
        },
        "Pharma": {
            "sentiment": "Positive",
            "score": 0.35
        }
    }

    context = create_market_context(
        news_count=20,
        sector_sentiment=sector_sentiment,
        nifty_change=0.75
    )

    return context
    # ----------------------------------------------
    # Step 2: Create embedding
    # ----------------------------------------------

    question_embedding = create_embedding(question)

    # ----------------------------------------------
    # Step 3: Retrieve documents from ChromaDB
    # ----------------------------------------------

    number_to_retrieve = min(
        10,
        collection.count()
    )

    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=number_to_retrieve
    )

    documents = results["documents"][0]

    # ----------------------------------------------
    # Step 4: Re-rank retrieved documents
    # ----------------------------------------------

    ranked_results = rerank_results(
        question,
        documents
    )

    # ----------------------------------------------
    # Check if results were found
    # ----------------------------------------------

    if not ranked_results:

        return {
            "question": question,
            "answer": (
                "I could not find relevant information "
                "in the PaiseWise knowledge base."
            ),
            "retrieved_documents": 0,
            "guardrail_triggered": False
        }

    # ----------------------------------------------
    # Step 5: Get best result
    # ----------------------------------------------

    best_document, best_score = ranked_results[0]

    # ----------------------------------------------
    # Step 6: Relevance threshold
    # ----------------------------------------------

    RELEVANCE_THRESHOLD = 0.25

    if best_score < RELEVANCE_THRESHOLD:

        return {
            "question": question,
            "answer": (
                "I couldn't find relevant information "
                "in the PaiseWise knowledge base."
            ),
            "relevance_score": round(float(best_score), 4),
            "retrieved_documents": len(documents),
            "guardrail_triggered": False
        }

    # ----------------------------------------------
    # Step 7: Return relevant answer
    # ----------------------------------------------

    return {
        "question": question,
        "answer": best_document,
        "relevance_score": round(float(best_score), 4),
        "retrieved_documents": len(documents),
        "guardrail_triggered": False
    }