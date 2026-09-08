from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import chromadb
import joblib
import pandas as pd
import time


# --------------------------------------------------
# Existing PaiseWise modules
# --------------------------------------------------
from news_classifier import classify_article

from embeddings import create_embedding
from reranker import rerank_results
from guardrails import is_guardrail_question
from market_context import create_market_context

from news_ingestion import fetch_market_news
from news_classifier import classify_article
from sector_sentiment import calculate_sector_sentiment
from corporate_events import extract_corporate_events
from market_data import get_nifty_change
from typing import List


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
# Load Churn Model
# ==================================================

CHURN_MODEL_PATH = "../data/churn/models/new_churn_model.pkl"

try:
    churn_model = joblib.load(CHURN_MODEL_PATH)
    print("Churn model loaded successfully.")

except Exception as e:
    churn_model = None
    print(f"Warning: Churn model could not be loaded: {e}")
    
# Market context cache
market_context_cache = None
market_context_cache_time = 0

MARKET_CONTEXT_CACHE_SECONDS = 15 * 60

# ==================================================
# Request Models
# ==================================================

class QuestionRequest(BaseModel):
    question: str


class NewsRequest(BaseModel):
    title: str
    description: str = ""


class ChurnRequest(BaseModel):
    d7_lesson_count: int
    d7_quiz_count: int
    d7_paper_trade_count: int
    d7_streak_days: int
    d7_xp_earned: int
    d7_notification_open_rate: float
    onboarding_goal_set: bool
    kyc_completed_d7: bool
    first_paper_trade_d7: bool

class PortfolioHolding(BaseModel):
    stock: str
    sector: str
    amount: float
    market_cap: str = "Large"


class PortfolioRequest(BaseModel):
    holdings: List[PortfolioHolding]
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
# 3. PORTFOLIO DIVERSIFICATION ENDPOINT
# ==================================================

@app.post("/portfolio/diversification")
def portfolio_diversification(request: PortfolioRequest):

    # --------------------------------------------------
    # Step 1: Get holdings from request
    # --------------------------------------------------

    holdings = [
        holding.model_dump()
        for holding in request.holdings
    ]

    # --------------------------------------------------
    # Step 2: Check whether holdings were provided
    # --------------------------------------------------

    if not holdings:
        raise HTTPException(
            status_code=400,
            detail="Portfolio holdings are required."
        )

    # --------------------------------------------------
    # Step 3: Calculate total portfolio value
    # --------------------------------------------------

    total_value = sum(
        holding["amount"]
        for holding in holdings
    )

    if total_value <= 0:
        raise HTTPException(
            status_code=400,
            detail="Portfolio amount must be greater than zero."
        )

    # --------------------------------------------------
    # Step 4: Calculate sector concentration
    # --------------------------------------------------

    sector_values = {}

    for holding in holdings:

        sector = holding["sector"]

        sector_values[sector] = (
            sector_values.get(sector, 0)
            + holding["amount"]
        )

    sector_concentration = {
        sector: round(
            (amount / total_value) * 100,
            2
        )
        for sector, amount in sector_values.items()
    }

    # --------------------------------------------------
    # Step 5: Calculate single-stock concentration
    # --------------------------------------------------

    stock_concentration = {}

    for holding in holdings:

        stock = holding["stock"]

        # If the same stock appears more than once,
        # combine its amount.

        stock_concentration[stock] = (
            stock_concentration.get(stock, 0)
            + holding["amount"]
        )

    stock_concentration = {
        stock: round(
            (amount / total_value) * 100,
            2
        )
        for stock, amount in stock_concentration.items()
    }

    # --------------------------------------------------
    # Step 6: Calculate sector diversification score
    # --------------------------------------------------

    sector_weights = [
        amount / total_value
        for amount in sector_values.values()
    ]

    largest_sector_weight = max(sector_weights)

    sector_score = (
        1 - largest_sector_weight
    ) * 100

    # --------------------------------------------------
    # Step 7: Calculate market-cap distribution
    # --------------------------------------------------

    market_cap_values = {}

    for holding in holdings:

        market_cap = holding["market_cap"]

        market_cap_values[market_cap] = (
            market_cap_values.get(market_cap, 0)
            + holding["amount"]
        )

    market_cap_weights = [
        amount / total_value
        for amount in market_cap_values.values()
    ]

    largest_market_cap_weight = max(
        market_cap_weights
    )

    market_cap_score = (
        1 - largest_market_cap_weight
    ) * 100

    # --------------------------------------------------
    # Step 8: Overall diversification score
    # --------------------------------------------------

    diversification_score = (
        sector_score + market_cap_score
    ) / 2

    # --------------------------------------------------
    # Step 9: Return result
    # --------------------------------------------------

    return {
        "total_portfolio_value": round(
            total_value,
            2
        ),

        "sector_concentration": (
            sector_concentration
        ),

        "stock_concentration": (
            stock_concentration
        ),

        "diversification_score": round(
            diversification_score,
            2
        )
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
                "sector": classification["sector"],
                "confidence": classification["confidence"]
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
# 8. CHURN PREDICTION ENDPOINT
# ==================================================

@app.post("/churn/predict")
def predict_churn(request: ChurnRequest):

    # --------------------------------------------------
    # Check model
    # --------------------------------------------------

    if churn_model is None:
        raise HTTPException(
            status_code=500,
            detail="Churn model is not loaded."
        )

    # --------------------------------------------------
    # Prepare input data
    # --------------------------------------------------

    input_data = pd.DataFrame([{

        "d7_lesson_count":
            request.d7_lesson_count,

        "d7_quiz_count":
            request.d7_quiz_count,

        "d7_paper_trade_count":
            request.d7_paper_trade_count,

        "d7_streak_days":
            request.d7_streak_days,

        "d7_xp_earned":
            request.d7_xp_earned,

        "d7_notification_open_rate":
            request.d7_notification_open_rate,

        "onboarding_goal_set":
            int(request.onboarding_goal_set),

        "kyc_completed_d7":
            int(request.kyc_completed_d7),

        "first_paper_trade_d7":
            int(request.first_paper_trade_d7)
    }])

    # --------------------------------------------------
    # DEBUG - Check API input
    # --------------------------------------------------

    print("\n" + "=" * 60)
    print("CHURN PREDICTION REQUEST")
    print("=" * 60)

    print("\nInput received:")
    print(input_data)

    # --------------------------------------------------
    # Predict churn probability
    # --------------------------------------------------

    try:

        probabilities = churn_model.predict_proba(
            input_data
        )

        print("\nModel probabilities:")
        print(probabilities)

        churn_probability = probabilities[0][1]

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Churn prediction failed: {str(e)}"
        )

    # --------------------------------------------------
    # Determine risk level
    # --------------------------------------------------

    if churn_probability >= 0.70:

        risk_level = "High"

    elif churn_probability >= 0.40:

        risk_level = "Medium"

    else:

        risk_level = "Low"

    print(f"\nChurn probability: {churn_probability:.4f}")
    print(f"Risk level: {risk_level}")
    print("=" * 60)

    # --------------------------------------------------
    # Return prediction
    # --------------------------------------------------

    return {

        "churn_probability":
            round(
                float(churn_probability),
                4
            ),

        "risk_level":
            risk_level
    }
