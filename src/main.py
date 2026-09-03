from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import chromadb

# --------------------------------------------------
# Existing PaiseWise modules
# --------------------------------------------------

from embeddings import create_embedding
from reranker import rerank_results
from guardrails import is_guardrail_question
from market_context import create_market_context

# --------------------------------------------------
# News modules
# --------------------------------------------------

from news_ingestion import fetch_market_news
from news_classifier import classify_article
from sector_sentiment import calculate_sector_sentiment
from corporate_events import extract_corporate_events
from market_data import get_nifty_change

# ==================================================
# FastAPI Application
# ==================================================

app = FastAPI(
    title="PaiseWise RAG API",
    description="Retrieval Augmented Generation API for PaiseWise",
    version="1.0.0"
)


# ==================================================
# Connect to ChromaDB
# ==================================================

client = chromadb.PersistentClient(
    path="../chroma_db"
)

collection = client.get_collection(
    name="paisewise_knowledge_base"
)


# ==================================================
# Request Models
# ==================================================

class QuestionRequest(BaseModel):
    question: str


class NewsRequest(BaseModel):
    title: str
    description: str = ""


# ==================================================
# 1. HOME ENDPOINT
# ==================================================

@app.get("/")
def home():

    return {
        "message": "PaiseWise RAG API is running"
    }


# ==================================================
# 2. HEALTH CHECK
# ==================================================

@app.get("/health")
def health():

    try:

        document_count = collection.count()

        return {
            "status": "healthy",
            "chroma_db": "connected",
            "collection": "paisewise_knowledge_base",
            "document_count": document_count
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Health check failed: {str(e)}"
        )


# ==================================================
# 3. RAG ASK ENDPOINT
# ==================================================

@app.post("/ask")
def ask_question(request: QuestionRequest):

    question = request.question.strip()

    # --------------------------------------------------
    # Check empty question
    # --------------------------------------------------

    if not question:

        return {
            "question": question,
            "answer": "Please enter a question."
        }

    # --------------------------------------------------
    # Step 1: Guardrail check
    # --------------------------------------------------

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

    # --------------------------------------------------
    # Step 2: Create embedding
    # --------------------------------------------------

    question_embedding = create_embedding(
        question
    )

    # --------------------------------------------------
    # Step 3: Check ChromaDB
    # --------------------------------------------------

    collection_count = collection.count()

    if collection_count == 0:

        return {
            "question": question,
            "answer": (
                "The PaiseWise knowledge base is currently empty."
            ),
            "retrieved_documents": 0,
            "guardrail_triggered": False
        }

    # --------------------------------------------------
    # Step 4: Retrieve documents
    # --------------------------------------------------

    number_to_retrieve = min(
        10,
        collection_count
    )

    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=number_to_retrieve
    )

    documents = results["documents"][0]

    # --------------------------------------------------
    # Step 5: Re-rank documents
    # --------------------------------------------------

    ranked_results = rerank_results(
        question,
        documents
    )

    # --------------------------------------------------
    # Check retrieval results
    # --------------------------------------------------

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

    # --------------------------------------------------
    # Step 6: Get best result
    # --------------------------------------------------

    best_document, best_score = ranked_results[0]

    # --------------------------------------------------
    # Step 7: Relevance threshold
    # --------------------------------------------------

    RELEVANCE_THRESHOLD = 0.25

    if best_score < RELEVANCE_THRESHOLD:

        return {
            "question": question,
            "answer": (
                "I couldn't find relevant information "
                "in the PaiseWise knowledge base."
            ),
            "relevance_score": round(
                float(best_score),
                4
            ),
            "retrieved_documents": len(documents),
            "guardrail_triggered": False
        }

    # --------------------------------------------------
    # Step 8: Return answer
    # --------------------------------------------------

    return {
        "question": question,
        "answer": best_document,
        "relevance_score": round(
            float(best_score),
            4
        ),
        "retrieved_documents": len(documents),
        "guardrail_triggered": False
    }


# ==================================================
# 4. MARKET CONTEXT ENDPOINT
# ==================================================
@app.get("/market-context")
def get_market_context():

    try:

        # --------------------------------------------------
        # Step 1: Fetch market news
        # --------------------------------------------------

        articles = fetch_market_news()


        # --------------------------------------------------
        # Step 2: Classify news
        # --------------------------------------------------

        classified_articles = []

        for article in articles:

            if not isinstance(article, dict):
                continue

            title = article.get("title") or ""
            description = article.get("description") or ""

            if not title:
                continue

            classification = classify_article(
                title,
                description
            )

            classified_article = {

                **article,

                "sector":
                classification["sector"],

                "confidence":
                classification["confidence"]
            }

            classified_articles.append(
                classified_article
            )


        # --------------------------------------------------
        # Step 3: Sector sentiment
        # --------------------------------------------------

        sector_sentiment = calculate_sector_sentiment(
            classified_articles
        )


        # --------------------------------------------------
        # Step 4: Corporate events
        # --------------------------------------------------

        corporate_events = extract_corporate_events(
            classified_articles
        )


        # --------------------------------------------------
        # Step 5: Get NIFTY 50 movement
        # --------------------------------------------------

        nifty_change = get_nifty_change()


        # --------------------------------------------------
        # Step 6: Create market context
        # --------------------------------------------------

        context = create_market_context(

            news_count=len(
                articles
            ),

            sector_sentiment=
            sector_sentiment,

            nifty_change=
            nifty_change,

            corporate_events=
            corporate_events
        )


        return {

            "market_context":
            context

        }


    except Exception as e:

        raise HTTPException(

            status_code=500,

            detail=(
                "Market context creation failed: "
                f"{str(e)}"
            )
        )


# ==================================================
# 5. FETCH MARKET NEWS ENDPOINT
# ==================================================

@app.get("/news")
def get_market_news():

    try:

        articles = fetch_market_news()

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"News ingestion failed: {str(e)}"
        )

    return {

        "status": "success",

        "articles_count": len(
            articles
        ),

        "articles": articles
    }


# ==================================================
# 6. CLASSIFY SINGLE NEWS ARTICLE
# ==================================================

@app.post("/news/classify")
def classify_news(request: NewsRequest):

    title = request.title.strip()
    description = request.description.strip()

    # --------------------------------------------------
    # Validate input
    # --------------------------------------------------

    if not title:

        raise HTTPException(
            status_code=400,
            detail="News title is required."
        )

    # --------------------------------------------------
    # Classify article
    # --------------------------------------------------

    try:

        result = classify_article(
            title,
            description
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"News classification failed: {str(e)}"
        )

    return {

        "title": title,

        "description": description,

        "sector": result["sector"],

        "confidence": result["confidence"]
    }


# ==================================================
# 7. FETCH + CLASSIFY ALL MARKET NEWS
# ==================================================

@app.get("/news/classified")
def get_classified_news():

    # --------------------------------------------------
    # Step 1: Fetch news
    # --------------------------------------------------

    try:

        articles = fetch_market_news()

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"News ingestion failed: {str(e)}"
        )

    # --------------------------------------------------
    # Step 2: Classify each article
    # --------------------------------------------------

    classified_articles = []

    for article in articles:

        if not isinstance(article, dict):
            continue

        title = article.get(
            "title"
        ) or ""

        description = article.get(
            "description"
        ) or ""

        # Skip articles without title

        if not title:
            continue

        try:

            classification = classify_article(
                title,
                description
            )

            classified_article = {

                "title": title,

                "description": description,

                "source": article.get(
                    "source"
                ),

                "published_at": article.get(
                    "published_at"
                ),

                "url": article.get(
                    "url"
                ),

                "sector": classification[
                    "sector"
                ],

                "confidence": classification[
                    "confidence"
                ]
            }

            classified_articles.append(
                classified_article
            )

        except Exception as e:

            print(
                f"Classification failed for: {title}"
            )

            continue

    # --------------------------------------------------
    # Step 3: Return results
    # --------------------------------------------------

    return {

        "status": "success",

        "articles_fetched": len(
            articles
        ),

        "articles_classified": len(
            classified_articles
        ),

        "articles": classified_articles
    }


# ==================================================
# RUN WITH:
#
# uvicorn main:app --reload
#
# ==================================================