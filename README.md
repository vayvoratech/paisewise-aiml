# PaiseWise RAG API

A Retrieval-Augmented Generation (RAG) based financial education API for **PaiseWise**.

The project combines a financial knowledge base, vector search, document embeddings, re-ranking, financial guardrails, market context, market-news ingestion, sector classification, sentiment analysis, portfolio analysis, churn prediction, and automated ML model retraining into a FastAPI application.

---

# 1. Project Overview

PaiseWise is designed to provide **general financial education** using information stored in a curated knowledge base.

The system is designed to explain financial concepts such as:

* Mutual funds
* SIP
* NAV
* Expense ratio
* Equity
* Debt funds
* Hybrid funds
* Diversification
* Risk
* KYC
* Demat accounts
* SEBI
* AMFI
* Inflation
* Compound interest
* Liquidity
* Saving vs investing

The application also contains supporting AI/ML features for:

* Market context
* Market-news ingestion
* Sector classification
* Sentiment analysis
* Portfolio diversification
* Portfolio risk
* Portfolio drawdown
* Portfolio correlation
* Portfolio health
* Churn prediction
* Automated churn model retraining
* Fund recommendation model retraining

---

# 2. Main RAG Flow

The main financial education flow is:

```text
User Question
      ↓
FastAPI
      ↓
Pydantic Validation
      ↓
Guardrail Check
      ↓
Question Embedding
      ↓
ChromaDB Retrieval
      ↓
Top 10 Documents
      ↓
Re-ranking
      ↓
Best Relevant Document
      ↓
Relevance Check
      ↓
Answer
```

The purpose of each step is:

```text
FastAPI
    → Receives the user's question

Pydantic
    → Validates the request

Guardrails
    → Prevents personalized financial advice

Embeddings
    → Converts the question into a vector

ChromaDB
    → Finds similar knowledge-base documents

Re-ranker
    → Reorders retrieved documents based on relevance

Relevance Check
    → Prevents unrelated content from being returned

Response
    → Returns the educational answer
```

---

# 3. Market News Flow

The market-news pipeline is:

```text
NewsAPI
   ↓
News Ingestion
   ↓
Market News Articles
   ↓
Zero-Shot Sector Classification
   ↓
Sector + Confidence
   ↓
Sentiment Analysis
   ↓
Sector Sentiment
   ↓
Market Context
```

---

# 4. Technologies Used

The project uses:

* Python
* FastAPI
* Uvicorn
* Pydantic
* ChromaDB
* Sentence Transformers
* Hugging Face Transformers
* NewsAPI
* Requests
* VADER Sentiment
* XGBoost
* Pandas
* NumPy
* Scikit-learn
* Python-dotenv
* MLflow
* Git
* GitHub

---

# 5. Python Version

The current development environment uses:

```text
Python 3.13
```

Check your Python version:

```powershell
python --version
```

---

# 6. Project Structure

The project is organized as follows:

```text
paiseWise-rag/
│
├── src/
│   │
│   ├── __init__.py
│   ├── main.py
│   │
│   ├── embeddings.py
│   ├── reranker.py
│   ├── guardrails.py
│   │
│   ├── news_ingestion.py
│   ├── news_classifier.py
│   ├── sentiment_analyser.py
│   ├── sector_sentiment.py
│   ├── corporate_events.py
│   ├── market_context.py
│   ├── market_data.py
│   │
│   ├── ingest_document.py
│   ├── chunking.py
│   ├── retrieval_test.py
│   ├── evaluate_retrieval.py
│   ├── check_database.py
│   │
│   ├── test_api_guardrails.py
│   ├── test_embedding.py
│   ├── test_hindi.py
│   ├── test_reranker.py
│   └── test_churn_predictions.py
│
├── data/
│   │
│   ├── lessons/
│   ├── jargon/
│   │
│   ├── churn/
│   │   ├── churn_training_dataset.csv
│   │   └── models/
│   │       ├── churn_model.pkl
│   │       └── new_churn_model.pkl
│   │
│   └── funds/
│       ├── fund_performance.csv
│       └── models/
│           ├── fund_recommendation_model.pkl
│           └── new_fund_recommendation_model.pkl
│
├── chroma_db/
│
├── requirements.txt
├── .env
├── .gitignore
└── README.md
```

### Important

The file:

```text
src/__init__.py
```

makes `src` a Python package.

Because of this, the project uses package-style imports such as:

```python
from .embeddings import create_embedding
```

and the FastAPI application should be started from the **project root** using:

```powershell
uvicorn src.main:app --reload
```

---

# 7. Clone the Repository

Open PowerShell.

Clone the repository:

```powershell
git clone <YOUR_REPOSITORY_URL>
```

Move into the project:

```powershell
cd paiseWise-rag
```

Check the current branch:

```powershell
git branch
```

If a specific branch is required:

```powershell
git checkout <YOUR_BRANCH_NAME>
```

---

# 8. Create Virtual Environment

Create the virtual environment:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\Activate.ps1
```

After activation, you should see:

```text
(.venv) PS C:\...\paiseWise-rag>
```

---

# 9. Upgrade pip

Run:

```powershell
python -m pip install --upgrade pip
```

---

# 10. Install Dependencies

If `requirements.txt` is available:

```powershell
pip install -r requirements.txt
```

If you need to install the packages manually:

```powershell
pip install fastapi uvicorn chromadb sentence-transformers transformers requests pydantic vaderSentiment xgboost pandas numpy scikit-learn python-dotenv mlflow
```

---

# 11. Verify the Environment

Check Python:

```powershell
python --version
```

Check FastAPI:

```powershell
python -c "import fastapi; print('FastAPI OK')"
```

Check ChromaDB:

```powershell
python -c "import chromadb; print('ChromaDB OK')"
```

Check Sentence Transformers:

```powershell
python -c "from sentence_transformers import SentenceTransformer; print('Sentence Transformers OK')"
```

Check Transformers:

```powershell
python -c "from transformers import pipeline; print('Transformers OK')"
```

Check XGBoost:

```powershell
python -c "import xgboost; print('XGBoost OK')"
```

Check MLflow:

```powershell
python -c "import mlflow; print('MLflow OK')"
```

---

# 12. Environment Variables

The news pipeline requires a NewsAPI key.

The code reads:

```python
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
```

You can create a `.env` file if the project uses `python-dotenv`:

```text
NEWS_API_KEY=YOUR_NEWS_API_KEY
```

Do not commit the real API key to GitHub.

For PowerShell, you can temporarily set it using:

```powershell
$env:NEWS_API_KEY="YOUR_NEWS_API_KEY"
```

Verify:

```powershell
echo $env:NEWS_API_KEY
```

---

# 13. Knowledge Base

The PaiseWise knowledge base contains financial education content including:

* 30 lesson contents
* 200 financial jargon definitions
* PaiseWise FAQs
* SEBI financial education content
* Mutual fund category explanations

The data is stored under:

```text
data/
├── lessons/
└── jargon/
```

Example:

```text
data/
├── lessons/
│   ├── lesson_01.txt
│   ├── lesson_02.txt
│   └── ...
│
└── jargon/
    ├── sip.txt
    ├── nav.txt
    ├── expense_ratio.txt
    └── ...
```

---

# 14. Document Chunking

Large documents are divided into smaller chunks before being inserted into ChromaDB.

Current strategy:

```text
Chunk Size : 200 words
Overlap    : 50 words
```

The process is:

```text
Original Document
       ↓
Chunk 1 → 200 words
       ↓
50-word overlap
       ↓
Chunk 2 → 200 words
       ↓
50-word overlap
       ↓
Chunk 3 → 200 words
```

The overlap helps preserve context between consecutive chunks.

---

# 15. Embedding Model

The actual PaiseWise project uses:

```text
paraphrase-multilingual-MiniLM-L12-v2
```

from Sentence Transformers.

This model is useful because the project also tests multilingual questions, including Hindi.

The embedding flow is:

```text
Document
    ↓
Text
    ↓
Sentence Transformer
    ↓
Vector Embedding
    ↓
ChromaDB
```

The same embedding model is used when converting a user's question into a vector.

---

# 16. Lazy Model Loading

The embedding model is loaded only when it is actually needed.

The project uses lazy loading so that simply importing the module does not immediately load the large ML model.

Conceptually:

```text
Python imports embeddings.py
        ↓
Model is NOT loaded yet
        ↓
create_embedding() is called
        ↓
Model is loaded
        ↓
Embedding is generated
```

This is important for test collection and application startup stability.

---

# 17. ChromaDB

ChromaDB is used as the local vector database.

Database:

```text
chroma_db/
```

Collection:

```text
paisewise_knowledge_base
```

The collection stores:

```text
Document
Embedding
Metadata
Chunk ID
```

---

# 18. Check ChromaDB

From the project root, run:

```powershell
python src/check_database.py
```

This checks the local ChromaDB database.

Expected type of output:

```text
ChromaDB connected successfully.
ChromaDB path: ...
Documents available: ...
```

The current development database has contained approximately:

```text
290 documents
```

The exact number can change when documents are added or re-ingested.

---

# 19. Ingest Documents

From the project root:

```powershell
python src/ingest_document.py
```

The ingestion process is:

```text
Lesson / Jargon File
       ↓
Read Document
       ↓
Chunk Text
       ↓
Create Embedding
       ↓
Generate Unique Chunk ID
       ↓
Store in ChromaDB
```

---

# 20. Test Retrieval

Run:

```powershell
python src/retrieval_test.py
```

The retrieval test checks questions such as:

```text
What is a mutual fund?
What is SIP?
What is NAV?
What is an expense ratio?
What is diversification?
What is equity?
```

The process is:

```text
Question
   ↓
Question Embedding
   ↓
ChromaDB
   ↓
Top Matching Documents
   ↓
Similarity Distance
```

---

# 21. Understanding ChromaDB Distance

ChromaDB returns a distance value for retrieved documents.

Generally:

```text
Lower distance
      ↓
More similar
```

Example:

```text
Question: What is SIP?

Result 1 → Distance: 0.43
Result 2 → Distance: 0.82
Result 3 → Distance: 1.10
```

Result 1 is more similar than Result 2 and Result 3.

---

# 22. Re-ranking

Initial retrieval returns the top documents from ChromaDB.

The PaiseWise flow is:

```text
Question
    ↓
ChromaDB
    ↓
Top 10 Documents
    ↓
Re-ranker
    ↓
Ranked Documents
    ↓
Best Relevant Document
```

The re-ranker evaluates the relationship between:

```text
Question
+
Retrieved Document
```

A higher relevance score generally means the document is more relevant.

---

# 23. Test Re-ranking

Run:

```powershell
python src/test_reranker.py
```

The test:

1. Connects to ChromaDB.
2. Gets the PaiseWise collection.
3. Creates an embedding for:

```text
What is SIP?
```

4. Retrieves up to 10 documents.
5. Sends them to the re-ranker.
6. Displays the ranked results.

---

# 24. Retrieval Evaluation

Run:

```powershell
python src/evaluate_retrieval.py
```

This helps evaluate retrieval quality.

It can identify problems such as:

```text
Question
   ↓
Wrong document retrieved
```

or:

```text
Different questions
       ↓
Same document repeatedly retrieved
```

The evaluation is useful for improving the knowledge base and retrieval process.

---

# 25. Hindi Retrieval Testing

The project includes Hindi retrieval testing.

Example questions include:

```text
म्यूचुअल फंड क्या है?
SIP कैसे काम करता है?
NAV का मतलब क्या है?
एक्सपेंस रेशियो क्या होता है?
इक्विटी फंड क्या है?
डेट फंड क्या होता है?
KYC क्या है?
SEBI क्या है?
डाइवर्सिफिकेशन क्यों जरूरी है?
```

Run:

```powershell
pytest -q src/test_hindi.py
```

The test:

```text
Hindi Question
      ↓
Multilingual Embedding
      ↓
ChromaDB
      ↓
Top 3 Results
      ↓
Retrieved Content
```

---

# 26. Guardrails

PaiseWise is designed for **financial education**, not personalized financial advice.

The guardrail should block questions such as:

```text
Which stock should I buy?
Should I sell this stock?
Which mutual fund should I buy?
Which SIP is best for me?
Where should I invest my money?
```

Educational questions can be answered:

```text
What is SIP?
What is NAV?
What is a mutual fund?
What is diversification?
What is an expense ratio?
```

---

# 27. Guardrail Testing

Run:

```powershell
pytest -q src/test_api_guardrails.py
```

The guardrail test checks a set of financial-advice questions.

The project target is:

```text
95% or higher deflection rate
```

The current test has demonstrated:

```text
Total questions : 16
Blocked         : 16
Not blocked     : 0

Deflection rate : 100%
```

---

# 28. Multilingual and Red-Team Testing

The project also includes:

* Hindi testing
* Adversarial questions
* Financial advice questions
* Educational questions
* Guardrail testing

The broader testing objective is:

```text
Advice Questions
       ↓
Deflect

Educational Questions
       ↓
Answer

Hindi Questions
       ↓
Retrieve Correct Knowledge

Adversarial Questions
       ↓
Remain Safe
```

---

# 29. FastAPI Application

The main FastAPI file is:

```text
src/main.py
```

The API connects the main PaiseWise components:

```text
FastAPI
   ↓
Guardrails
   ↓
Embeddings
   ↓
ChromaDB
   ↓
Retrieval
   ↓
Re-ranking
   ↓
Relevance Check
   ↓
Response
```

---

# 30. IMPORTANT: Start FastAPI Correctly

Because `src` is a Python package and `main.py` uses relative imports, **run Uvicorn from the project root**.

Make sure your terminal is here:

```text
C:\Users\...\paiseWise-rag
```

Then run:

```powershell
uvicorn src.main:app --reload
```

You should see something similar to:

```text
Uvicorn running on http://127.0.0.1:8000
```

---

# 31. Do NOT Start It This Way

Do not use:

```powershell
cd src
uvicorn main:app --reload
```

with the current package structure.

This causes:

```text
ImportError:
attempted relative import with no known parent package
```

because `main.py` contains imports such as:

```python
from .news_classifier import classify_article
```

---

# 32. Correct FastAPI Commands

From the project root:

### Development

```powershell
uvicorn src.main:app --reload
```

### Specific host and port

```powershell
uvicorn src.main:app --host 127.0.0.1 --port 8000
```

### Host + port + reload

```powershell
uvicorn src.main:app --host 127.0.0.1 --port 8000 --reload
```

### Port 8080

```powershell
uvicorn src.main:app --host 127.0.0.1 --port 8080 --reload
```

---

# 33. Swagger UI

After starting FastAPI, open:

```text
http://127.0.0.1:8000/docs
```

FastAPI automatically provides Swagger UI.

Swagger can be used to:

* View endpoints
* View request schemas
* View response schemas
* Send test requests
* Check API responses

---

# 34. Home Endpoint

Endpoint:

```text
GET /
```

URL:

```text
http://127.0.0.1:8000/
```

Expected response:

```json
{
    "message": "PaiseWise RAG API is running"
}
```

---

# 35. Health Endpoint

Endpoint:

```text
GET /health
```

URL:

```text
http://127.0.0.1:8000/health
```

The health endpoint can be used to verify:

```text
API status
ChromaDB connection
Collection
Document count
```

---

# 36. Ask Question Endpoint

Endpoint:

```text
POST /ask
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

Example request:

```json
{
    "question": "What is SIP?"
}
```

---

# 37. `/ask` Internal Flow

When the user asks:

```text
What is SIP?
```

the API performs:

```text
1. Receive Question
        ↓
2. Validate Request
        ↓
3. Guardrail Check
        ↓
4. Create Question Embedding
        ↓
5. Search ChromaDB
        ↓
6. Retrieve Top 10 Documents
        ↓
7. Re-rank Documents
        ↓
8. Select Best Result
        ↓
9. Check Relevance
        ↓
10. Return Educational Answer
```

---

# 38. Financial Advice Guardrail Flow

When the user asks:

```text
Which stock should I buy today?
```

the flow becomes:

```text
Question
   ↓
Guardrail
   ↓
Financial Advice Detected
   ↓
Block / Deflect
   ↓
Educational Safety Response
```

The system should not provide a personalized buy/sell recommendation.

---

# 39. Relevance Threshold

The current API uses:

```python
RELEVANCE_THRESHOLD = 0.25
```

The threshold is used to prevent unrelated documents from being returned as answers.

Conceptually:

```text
Retrieved Result
      ↓
Relevance Check
      ↓
Above Threshold?
   /          \
 YES           NO
  ↓             ↓
Answer       No relevant
             information
```

If the result is not relevant enough, the API can return a response indicating that relevant information was not found in the PaiseWise knowledge base.

---

# 40. Market Context

The market-context feature combines information from different market sources.

The flow is:

```text
Market Data
     +
Market News
     +
Sector Sentiment
     +
Corporate Events
     ↓
Market Context
```

Endpoint:

```text
GET /market-context
```

---

# 41. Market Data

The market data module provides market/index information such as NIFTY movement.

Conceptually:

```text
Market Data
    ↓
NIFTY Change
    ↓
Market Context
```

Example:

```text
NIFTY Change: +0.75%
```

The actual value depends on the available market-data implementation.

---

# 42. News Ingestion

The project uses NewsAPI to retrieve market-related news.

The search query is:

```text
NSE OR BSE OR NIFTY OR Sensex
```

The ingestion process retrieves information such as:

* Article title
* Description
* Source
* Published date
* URL

---

# 43. Test News Ingestion

Set the API key first:

```powershell
$env:NEWS_API_KEY="YOUR_NEWS_API_KEY"
```

Then run from the project root:

```powershell
python src/news_ingestion.py
```

The flow is:

```text
NewsAPI
   ↓
API Request
   ↓
Market Articles
   ↓
Article Information
```

---

# 44. News Endpoint

Endpoint:

```text
GET /news
```

The endpoint calls:

```python
fetch_market_news()
```

from:

```text
news_ingestion.py
```

The endpoint returns market-related news.

---

# 45. Sector Classification

The news classifier uses Hugging Face zero-shot classification.

The classifier assigns a sector to each article.

Candidate sectors include:

```text
IT
Banking
Pharma
Auto
Energy
FMCG
Metals
Telecom
Financial Services
Market Index
Other
```

The classification flow is:

```text
News Article
      ↓
Title + Description
      ↓
Zero-Shot Classifier
      ↓
Compare Candidate Sectors
      ↓
Highest Score
      ↓
Sector + Confidence
```

---

# 46. Example Sector Classification

Example:

```text
Article:

TCS reports strong quarterly growth
```

The classifier may produce:

```text
Sector:
IT

Confidence:
0.xx
```

The actual confidence depends on the model output.

---

# 47. Test News Classifier

Run:

```powershell
python src/news_classifier.py
```

The first execution may take longer because the Hugging Face model may need to be downloaded.

---

# 48. Classify News API

Endpoint:

```text
POST /news/classify
```

Example request:

```json
{
    "title": "TCS reports strong quarterly growth",
    "description": "The IT company reported improved revenue."
}
```

Example response structure:

```json
{
    "title": "TCS reports strong quarterly growth",
    "description": "The IT company reported improved revenue.",
    "sector": "IT",
    "confidence": 0.XX
}
```

---

# 49. Classified News Endpoint

Endpoint:

```text
GET /news/classified
```

Complete flow:

```text
GET /news/classified
        ↓
fetch_market_news()
        ↓
NewsAPI
        ↓
Market Articles
        ↓
classify_article()
        ↓
Sector Classification
        ↓
Confidence
        ↓
Sentiment
        ↓
Response
```

The response can contain:

```text
Title
Description
Source
Published At
URL
Sector
Confidence
```

depending on the current API implementation.

---

# 50. Sentiment Analysis

The project includes sentiment analysis using VADER sentiment analysis.

News can be classified into:

```text
Positive
Negative
Neutral
```

The flow is:

```text
News Article
      ↓
Sentiment Analyzer
      ↓
Sentiment Score
      ↓
Positive / Negative / Neutral
```

---

# 51. Sector Sentiment

Sector sentiment aggregates sentiment across news articles belonging to the same sector.

Example:

```text
IT
   ↓
Positive News
Positive News
Neutral News
   ↓
Overall IT Sentiment
```

Example output:

```text
IT          → Positive
Banking     → Neutral
Pharma      → Positive
Auto        → Negative
```

---

# 52. Corporate Events

The market-context pipeline can also extract major corporate events from market information.

Conceptually:

```text
Market News
     ↓
Corporate Event Detection
     ↓
Major Events
     ↓
Market Context
```

---

# 53. Complete Market Context Flow

```text
             Market Data
                 │
                 ▼
           NIFTY Movement
                 │
                 │
NewsAPI ──→ News Articles
                 │
                 ▼
          Sector Classification
                 │
                 ▼
          Sentiment Analysis
                 │
                 ▼
           Sector Sentiment
                 │
                 ▼
          Corporate Events
                 │
                 ▼
          Market Context
```

---

# 54. Portfolio Analysis

The portfolio analysis module evaluates a portfolio from different perspectives.

Main areas include:

```text
Diversification
Risk
Drawdown
Correlation
Portfolio Health
```

Overall flow:

```text
Portfolio Holdings
       ↓
Portfolio Analysis
       ↓
Diversification
       ↓
Risk
       ↓
Drawdown
       ↓
Correlation
       ↓
Portfolio Health
```

---

# 55. Portfolio Diversification

The diversification analysis checks:

```text
Sector Concentration
Single Stock Concentration
Overall Diversification
```

The module generates a diversification score from:

```text
0 – 100
```

Example:

```text
Diversification Score: 78/100
```

Run:

```powershell
python src/Portfolio_Diversification.py
```

---

# 56. Portfolio Analysis

Run:

```powershell
python src/portfolio_analyser.py
```

The analysis considers:

```text
Portfolio Holdings
Sector Exposure
Stock Concentration
Portfolio Distribution
```

---

# 57. Portfolio Risk Assessment

Run:

```powershell
python src/risk_assessment.py
```

The risk module evaluates portfolio risk and compares it with the NIFTY 50 benchmark where supported by the implementation.

Flow:

```text
Portfolio
    ↓
Risk Calculation
    ↓
NIFTY 50 Comparison
    ↓
Risk Result
```

---

# 58. Portfolio Drawdown

Run:

```powershell
python src/Portfolio_Drawdown_Calculator.py
```

Maximum drawdown measures the largest decline from a previous portfolio peak.

Flow:

```text
Portfolio Values
      ↓
Find Peak
      ↓
Find Lowest Value After Peak
      ↓
Calculate Drawdown
```

Example:

```text
Highest Portfolio Value: 123343.54
Lowest Value: 96428.78
Maximum Drawdown: 21.82%
```

---

# 59. Portfolio Correlation Matrix

Run:

```powershell
python src/portfolio_correlation_matrix.py
```

Correlation shows how assets move in relation to each other.

General interpretation:

```text
-1 → Opposite movement
 0 → Little or no relationship
+1 → Similar movement
```

The analysis can identify:

* Highly correlated assets
* Less correlated assets
* Possible concentration
* Diversification opportunities

---

# 60. Portfolio Health Report

Run:

```powershell
python src/portfolio_health_report.py
```

The health report combines:

```text
Diversification
       +
Risk
       +
Performance
       +
Drawdown
       +
Correlation
       ↓
Portfolio Health Report
```

---

# 61. Portfolio API

If portfolio endpoints are enabled in the current `main.py`, they can be tested through:

```text
http://127.0.0.1:8000/docs
```

For example, a diversification request can contain holdings similar to:

```json
{
    "holdings": [
        {
            "stock": "TCS",
            "sector": "IT",
            "amount": 40000,
            "market_cap": "Large"
        }
    ]
}
```

Always use the request schema displayed by the current Swagger documentation.

---

# 62. Churn Prediction

The churn prediction system identifies users who may stop using PaiseWise.

Current churn definition:

```text
User with 0 app opens
for 14 consecutive days
        ↓
Churned User
```

The overall flow is:

```text
User Activity
      ↓
Feature Engineering
      ↓
XGBoost Classifier
      ↓
Churn Prediction
      ↓
High-Risk Users
```

---

# 63. Churn Features

The model uses the following Day-7 engagement features:

```text
d7_lesson_count
d7_quiz_count
d7_paper_trade_count
d7_streak_days
d7_xp_earned
d7_notification_open_rate
onboarding_goal_set
kyc_completed_d7
first_paper_trade_d7
```

These features represent early user engagement.

---

# 64. Churn Dataset

Run:

```powershell
python src/churn_data.py
```

The dataset contains user activity and churn information.

Target:

```text
churned
```

Target values:

```text
0 = Retained
1 = Churned
```

---

# 65. Train Churn Model

Run:

```powershell
python src/churn_training.py
```

Model:

```text
XGBoost Classifier
```

Training flow:

```text
Churn Dataset
      ↓
Feature Preparation
      ↓
Training
      ↓
XGBoost
      ↓
Model
```

---

# 66. Churn Validation

Run:

```powershell
python src/churn_validation.py
```

The validation process compares:

```text
Current Model
       vs
New Model
```

Metrics include:

```text
Accuracy
Precision
Recall
F1 Score
```

The F1 score is used for model comparison.

---

# 67. Automated Churn Retraining

Run:

```powershell
python src/churn_retraining_pipeline.py
```

Flow:

```text
Latest Churn Data
       ↓
Filter Training Data
       ↓
Train New XGBoost Model
       ↓
Holdout Validation
       ↓
Calculate Metrics
       ↓
Compare Current vs New
       ↓
Improvement > 2%?
      /       \
    YES        NO
     ↓          ↓
 Deploy       Keep Current
 New Model       Model
     \           /
      ↓         ↓
       MLflow
```

---

# 68. Churn Deployment Rule

The new churn model is deployed only if its performance improves by more than the required threshold.

Conceptually:

```text
New F1 - Current F1 > 2%
```

If:

```text
Improvement > 2%
```

then:

```text
DEPLOY_NEW_MODEL
```

Otherwise:

```text
KEEP_CURRENT_MODEL
```

Example:

```text
Current F1 : 100.00%
New F1     : 100.00%
Improvement: 0.00%

Decision   : KEEP_CURRENT_MODEL
```

This demonstrates that the deployment safeguard prevents an equal or weaker model from replacing the current model.

---

# 69. Churn MLflow Tracking

Experiment:

```text
PaiseWise-Churn-Retraining
```

MLflow can track:

```text
Accuracy
Precision
Recall
F1 Score
Current Model F1
New Model F1
Improvement
Deployment Decision
Model Artifact
```

---

# 70. Churn Monthly Schedule

Production schedule:

```text
Frequency : Monthly
Day       : 1st day of every month
Time      : 3:00 AM
```

Scheduler:

```text
src/churn_scheduler.py
```

Test:

```powershell
python src/churn_scheduler.py
```

If the scheduler supports:

```python
TEST_MODE = True
```

the pipeline can be executed immediately for testing.

For the actual schedule:

```python
TEST_MODE = False
```

---

# 71. Fund Recommendation Retraining

PaiseWise also contains an automated fund recommendation retraining workflow.

The process uses fund-performance information to calculate scores and rank funds.

Flow:

```text
Fund Performance Data
        ↓
Dynamic Scoring Weights
        ↓
Fund Scores
        ↓
Fund Ranking
        ↓
Validation
        ↓
Compare Current vs New
        ↓
Deployment Decision
```

---

# 72. Fund Scoring Factors

The fund scoring pipeline considers factors such as:

```text
1-Year Return
3-Year Return
Risk Score
Consistency Score
```

---

# 73. Dynamic Fund Weights

The scoring pipeline dynamically calculates the importance of different factors based on the available dataset.

Example:

```text
Return Weight      : 71.31%
Risk Weight        : 10.53%
Consistency Weight : 18.16%

Total              : 100%
```

The actual weights can change when the underlying dataset changes.

---

# 74. Fund Score

Conceptually:

```text
Fund Score =
    Return Score × Return Weight
  + Risk Score × Risk Weight
  + Consistency Score × Consistency Weight
```

Funds are then ranked according to the final score.

---

# 75. Fund Recommendation Example

An example ranking may look like:

```text
1. HDFC Mid-Cap Opportunities Fund
2. Kotak Emerging Equity Fund
3. Quant Flexi Cap Fund
4. Parag Parikh Flexi Cap Fund
5. Axis Midcap Fund
```

These rankings are based on the project's test/demo dataset and should **not** be interpreted as live investment recommendations.

---

# 76. Fund Retraining Pipeline

Run the fund retraining pipeline using the actual filename present in `src`.

If the project contains:

```text
fund_retraining_pipeline.py
```

run:

```powershell
python src/fund_retraining_pipeline.py
```

The pipeline performs:

```text
Load Fund Data
      ↓
Calculate Weights
      ↓
Calculate Fund Scores
      ↓
Generate Ranking
      ↓
Validate
      ↓
Compare Models
      ↓
Deploy if Better
```

---

# 77. Fund Deployment Rule

The new fund model is deployed only if the required improvement is achieved.

Conceptually:

```text
New Score - Current Score > 2%
```

Otherwise:

```text
KEEP_CURRENT_MODEL
```

Example:

```text
Current Score : 41.67%
New Score     : 41.67%
Improvement   : 0.00%

Decision      : KEEP_CURRENT_MODEL
```

---

# 78. Fund MLflow Tracking

Experiment:

```text
PaiseWise-Fund-Retraining
```

Metrics can include:

```text
return_weight
risk_weight
consistency_weight
current_score
new_score
improvement
```

Parameters can include:

```text
model_type
retraining_frequency
retraining_day
retraining_time
evaluation_metric
deployment_threshold
deployment_decision
```

The generated model artifact can be stored as:

```text
new_fund_recommendation_model.pkl
```

---

# 79. Fund Weekly Schedule

Production schedule:

```text
Frequency : Weekly
Day       : Sunday
Time      : 2:00 AM
```

Scheduler:

```text
src/fund_scheduler.py
```

Run:

```powershell
python src/fund_scheduler.py
```

If supported:

```python
TEST_MODE = True
```

can be used for immediate testing.

For production:

```python
TEST_MODE = False
```

---

# 80. MLflow UI

Start MLflow:

```powershell
mlflow ui --backend-store-uri sqlite:///C:/Users/Malinirani/Desktop/paiseWise-rag/src/mlflow.db
```

MLflow will display a local URL in the terminal.

Open that URL in your browser.

The main experiments are:

```text
PaiseWise-Churn-Retraining
PaiseWise-Fund-Retraining
```

---

# 81. Automated Deployment Architecture

Both ML models follow the same basic safety mechanism:

```text
             New Model
                 ↓
          Model Validation
                 ↓
       Compare With Current
                 ↓
        Improvement > 2%?
            /        \
          YES         NO
           ↓           ↓
      Deploy New    Keep Current
         Model          Model
           \           /
             ↓       ↓
                MLflow
```

This prevents a weaker model from automatically replacing the existing model.

---

# 82. Testing With Pytest

The project uses pytest for automated testing.

The mentor/team requested the command:

```powershell
pytest -q
```

Run it from the **project root**:

```powershell
cd paiseWise-rag
```

Activate the environment:

```powershell
.venv\Scripts\Activate.ps1
```

Then:

```powershell
pytest -q
```

---

# 83. Important Pytest Package Structure

Because `src` contains:

```text
src/__init__.py
```

test files inside `src` should use package-relative imports where appropriate.

Correct:

```python
from .embeddings import create_embedding
```

Correct:

```python
from .reranker import rerank_results
```

For importing the FastAPI application:

```python
from src.main import app
```

Avoid:

```python
from embeddings import create_embedding
```

when pytest is running from the project root.

---

# 84. Embedding Test

The embedding test should contain an actual pytest test function.

Example:

```python
from .embeddings import create_embedding


def test_embedding():
    text = "What is a mutual fund?"

    embedding = create_embedding(text)

    assert embedding is not None
    assert len(embedding) > 0

    print("\nEmbedding created successfully.")
    print("Embedding length:", len(embedding))
```

Run individually:

```powershell
pytest -q src/test_embedding.py
```

---

# 85. Hindi Test

Run:

```powershell
pytest -q src/test_hindi.py
```

This verifies:

```text
Hindi Question
      ↓
Multilingual Embedding
      ↓
ChromaDB
      ↓
Retrieved Documents
```

---

# 86. Reranker Test

Run:

```powershell
pytest -q src/test_reranker.py
```

This verifies:

```text
Question
    ↓
Embedding
    ↓
ChromaDB
    ↓
Top 10
    ↓
Reranker
    ↓
Ranked Results
```

---

# 87. Guardrail Test

Run:

```powershell
pytest -q src/test_api_guardrails.py
```

Expected target:

```text
Guardrail deflection rate >= 95%
```

---

# 88. Full Test Suite

The final command is:

```powershell
pytest -q
```

Run this from:

```text
paiseWise-rag/
```

not from:

```text
paiseWise-rag/src/
```

Correct:

```text
C:\Users\...\paiseWise-rag>
pytest -q
```

---

# 89. If Pytest Reports Import Errors

If you see:

```text
ModuleNotFoundError: No module named 'embeddings'
```

check that the test uses:

```python
from .embeddings import create_embedding
```

instead of:

```python
from embeddings import create_embedding
```

Also make sure:

```text
src/__init__.py
```

exists.

---

# 90. If Uvicorn Reports Relative Import Error

If you see:

```text
ImportError:
attempted relative import with no known parent package
```

you are probably starting the application incorrectly.

Do:

```powershell
cd C:\Users\...\paiseWise-rag
```

then:

```powershell
uvicorn src.main:app --reload
```

Do not use:

```powershell
cd src
uvicorn main:app
```

---

# 91. If ChromaDB Is Empty

Check the database:

```powershell
python src/check_database.py
```

If the collection is empty, run the ingestion process:

```powershell
python src/ingest_document.py
```

Then check again:

```powershell
python src/check_database.py
```

---

# 92. If Pandas Is Missing

If you see:

```text
ModuleNotFoundError: No module named 'pandas'
```

install:

```powershell
pip install pandas
```

or reinstall all requirements:

```powershell
pip install -r requirements.txt
```

---

# 93. If Sentence Transformers Is Missing

Install:

```powershell
pip install sentence-transformers
```

Test:

```powershell
python -c "from sentence_transformers import SentenceTransformer; print('Sentence Transformers OK')"
```

---

# 94. If XGBoost Is Missing

Install:

```powershell
pip install xgboost
```

Test:

```powershell
python -c "import xgboost; print('XGBoost OK')"
```

---

# 95. If NewsAPI Key Is Missing

If you see:

```text
NEWS_API_KEY environment variable is not set.
```

set:

```powershell
$env:NEWS_API_KEY="YOUR_NEWS_API_KEY"
```

Then run:

```powershell
python src/news_ingestion.py
```

---

# 96. Hugging Face Warnings

The first model download may produce warnings related to:

```text
Hugging Face Hub
```

An unauthenticated Hugging Face environment can still download publicly available models, although rate limits may apply.

A Hugging Face token can be configured if required by your environment.

---

# 97. Pytest Warnings

You may see warnings such as:

```text
StarletteDeprecationWarning
```

or:

```text
BPE deprecation warning
```

Warnings are different from test failures.

For example:

```text
5 passed, 2 warnings
```

means:

```text
Tests passed successfully.
Warnings are present but did not fail the tests.
```

---

# 98. Windows / ML Model Stability

The project uses ML libraries such as:

```text
PyTorch
Transformers
Sentence Transformers
```

These libraries can load native components.

For this reason:

* Avoid loading models unnecessarily during module import.
* Keep embedding model loading lazy.
* Keep expensive ML calls inside test functions.
* Avoid executing model inference directly at test-module import time.

For example, avoid:

```python
embedding = create_embedding("What is SIP?")
```

at the top level of a pytest file.

Instead use:

```python
def test_embedding():
    embedding = create_embedding("What is SIP?")
```

---

# 99. Complete API Endpoint List

The main API currently exposes the following endpoints:

```text
GET  /
GET  /health
POST /ask
GET  /market-context
GET  /news
POST /news/classify
GET  /news/classified
```

Portfolio-related endpoints may also be available depending on the current `src/main.py`.

Always use:

```text
http://127.0.0.1:8000/docs
```

as the source of truth for the currently registered endpoints.

---

# 100. Complete API Architecture

```text
                         PaiseWise
                            │
                            ▼
                       FastAPI API
                            │
          ┌─────────────────┼─────────────────┐
          │                 │                 │
          ▼                 ▼                 ▼
       RAG Flow        Market Context     Portfolio
          │                 │                 │
          ▼                 ▼                 ▼
     Guardrails          Market Data     Diversification
          │                 │                 │
          ▼                 ▼                 ▼
     Embeddings         NewsAPI          Risk
          │                 │                 │
          ▼                 ▼                 ▼
      ChromaDB        Classification     Drawdown
          │                 │                 │
          ▼                 ▼                 ▼
     Top 10 Docs       Sentiment         Correlation
          │                 │                 │
          ▼                 ▼                 ▼
      Re-ranker       Sector Sentiment   Health Report
          │                 │
          ▼                 ▼
    Best Document      Market Context
          │
          ▼
       Answer
```

---

# 101. Complete ML Architecture

```text
                    PaiseWise ML
                         │
             ┌───────────┴───────────┐
             │                       │
             ▼                       ▼
        Churn Model            Fund Model
             │                       │
             ▼                       ▼
        User Activity        Fund Performance
             │                       │
             ▼                       ▼
      Feature Engineering       Scoring
             │                       │
             ▼                       ▼
          XGBoost              Fund Ranking
             │                       │
             ▼                       ▼
         Validation             Validation
             │                       │
             └───────────┬───────────┘
                         ▼
                    MLflow
                         │
                         ▼
                Deployment Decision
```

---

# 102. Automated Retraining Overview

## Churn

```text
Monthly
   ↓
1st Day
   ↓
3:00 AM
   ↓
Latest Churn Data
   ↓
Training
   ↓
Validation
   ↓
F1 Comparison
   ↓
Deploy if >2% improvement
```

## Fund Recommendation

```text
Weekly
   ↓
Sunday
   ↓
2:00 AM
   ↓
Latest Fund Data
   ↓
Dynamic Weights
   ↓
Fund Scoring
   ↓
Validation
   ↓
Score Comparison
   ↓
Deploy if >2% improvement
```

---

# 103. Git Workflow

Check the current branch:

```powershell
git branch
```

Check changed files:

```powershell
git status
```

Add changes:

```powershell
git add .
```

Commit:

```powershell
git commit -m "Update PaiseWise RAG API"
```

Push:

```powershell
git push
```

---

# 104. Security

Never commit secrets to GitHub.

Do not write:

```python
NEWS_API_KEY = "actual-secret-key"
```

inside the source code.

Use:

```text
NEWS_API_KEY
```

as an environment variable.

Recommended `.gitignore`:

```text
.venv/
.env
__pycache__/
*.pyc
chroma_db/
*.db
```

Depending on project requirements, model files and datasets may or may not be committed to Git.

---

# 105. Quick Start – Existing Project

If the repository is already cloned, dependencies are installed, and ChromaDB is already populated:

```powershell
cd C:\Users\Malinirani\Desktop\paiseWise-rag

.venv\Scripts\Activate.ps1

pytest -q
```

If tests pass, start the API:

```powershell
uvicorn src.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

---

# 106. Quick Start – Fresh Installation

For a new machine:

```powershell
git clone <YOUR_REPOSITORY_URL>

cd paiseWise-rag

python -m venv .venv

.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip

pip install -r requirements.txt
```

Prepare the environment variable:

```powershell
$env:NEWS_API_KEY="YOUR_NEWS_API_KEY"
```

Check the database:

```powershell
python src/check_database.py
```

If the database is empty:

```powershell
python src/ingest_document.py
```

Run tests:

```powershell
pytest -q
```

Start the API:

```powershell
uvicorn src.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

---

# 107. Recommended Daily Development Workflow

Start from the project root:

```powershell
cd C:\Users\Malinirani\Desktop\paiseWise-rag
```

Activate the environment:

```powershell
.venv\Scripts\Activate.ps1
```

Run the complete test suite:

```powershell
pytest -q
```

If needed, check ChromaDB:

```powershell
python src/check_database.py
```

Run individual tests when debugging:

```powershell
pytest -q src/test_embedding.py
```

```powershell
pytest -q src/test_hindi.py
```

```powershell
pytest -q src/test_reranker.py
```

```powershell
pytest -q src/test_api_guardrails.py
```

Then start FastAPI:

```powershell
uvicorn src.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

---

# 108. Recommended Verification Order

For a complete local verification:

```text
1. Activate virtual environment
          ↓
2. Check dependencies
          ↓
3. Check ChromaDB
          ↓
4. Run pytest
          ↓
5. Test retrieval
          ↓
6. Test reranking
          ↓
7. Test guardrails
          ↓
8. Test Hindi retrieval
          ↓
9. Test portfolio modules
          ↓
10. Test churn pipeline
          ↓
11. Test fund pipeline
          ↓
12. Start FastAPI
          ↓
13. Open Swagger
          ↓
14. Test API endpoints
```

Commands:

```powershell
cd C:\Users\Malinirani\Desktop\paiseWise-rag

.venv\Scripts\Activate.ps1

python src/check_database.py

pytest -q

python src/retrieval_test.py

python src/test_reranker.py

pytest -q src/test_api_guardrails.py

pytest -q src/test_hindi.py

python src/Portfolio_Diversification.py

python src/portfolio_analyser.py

python src/risk_assessment.py

python src/Portfolio_Drawdown_Calculator.py

python src/portfolio_correlation_matrix.py

python src/portfolio_health_report.py

python src/churn_data.py

python src/churn_training.py

python src/churn_validation.py

python src/churn_retraining_pipeline.py

python src/fund_retraining_pipeline.py

uvicorn src.main:app --reload
```

Then:

```text
http://127.0.0.1:8000/docs
```

---

# 109. Important Command Difference

Because the project now uses `src` as a Python package, remember this rule:

### Pytest

Run from project root:

```powershell
pytest -q
```

### FastAPI

Run from project root:

```powershell
uvicorn src.main:app --reload
```

### Python scripts

Run from project root using the `src/` path:

```powershell
python src/check_database.py
```

```powershell
python src/retrieval_test.py
```

```powershell
python src/ingest_document.py
```

This avoids the relative-import problems caused by treating `src` as a standalone directory.

---

# 110. Troubleshooting Summary

| Problem                                                  | Solution                                       |
| -------------------------------------------------------- | ---------------------------------------------- |
| `No module named embeddings`                             | Use `from .embeddings import create_embedding` |
| `attempted relative import with no known parent package` | Run `uvicorn src.main:app` from project root   |
| ChromaDB empty                                           | Run `python src/ingest_document.py`            |
| Pandas missing                                           | `pip install pandas`                           |
| Sentence Transformers missing                            | `pip install sentence-transformers`            |
| XGBoost missing                                          | `pip install xgboost`                          |
| NewsAPI key missing                                      | Set `NEWS_API_KEY`                             |
| Pytest model crash                                       | Keep model calls inside test functions         |
| FastAPI not starting                                     | Check `uvicorn src.main:app --reload`          |
| Swagger unavailable                                      | Start FastAPI and open `/docs`                 |
| MLflow unavailable                                       | Start `mlflow ui`                              |

---

# 111. Final Project Checklist

Before considering the project ready:

```text
[ ] Repository cloned
[ ] Correct branch selected
[ ] Virtual environment created
[ ] Virtual environment activated
[ ] Dependencies installed
[ ] Python version verified
[ ] src/__init__.py exists
[ ] Knowledge-base data available
[ ] ChromaDB populated
[ ] Embedding model working
[ ] Retrieval tested
[ ] Re-ranking tested
[ ] Guardrails tested
[ ] Hindi retrieval tested
[ ] Red-team testing completed
[ ] FastAPI starts successfully
[ ] Swagger UI accessible
[ ] Market context working
[ ] News ingestion working
[ ] News classification working
[ ] Sentiment analysis working
[ ] Sector sentiment working
[ ] Portfolio diversification tested
[ ] Portfolio analysis tested
[ ] Risk assessment tested
[ ] Drawdown tested
[ ] Correlation tested
[ ] Portfolio health tested
[ ] Churn model trained
[ ] Churn validation completed
[ ] Churn retraining tested
[ ] MLflow tracking available
[ ] Churn scheduler configured
[ ] Fund scoring tested
[ ] Fund retraining tested
[ ] Fund validation completed
[ ] Fund scheduler configured
[ ] Secrets excluded from Git
[ ] pytest -q passes
[ ] Git changes committed
[ ] Git changes pushed
```

---

# 112. Final End-to-End Architecture

```text
                         PAiseWise
                            │
                            ▼
                       FastAPI API
                            │
       ┌────────────────────┼────────────────────┐
       │                    │                    │
       ▼                    ▼                    ▼
   RAG Assistant       Market Intelligence   Portfolio
       │                    │                    │
       ▼                    ▼                    ▼
  Guardrails            NewsAPI             Holdings
       │                    │                    │
       ▼                    ▼                    ▼
  Embeddings          News Ingestion       Diversification
       │                    │                    │
       ▼                    ▼                    ▼
   ChromaDB          Sector Classification     Risk
       │                    │                    │
       ▼                    ▼                    ▼
 Top 10 Retrieval     Sentiment Analysis     Drawdown
       │                    │                    │
       ▼                    ▼                    ▼
   Re-ranking         Sector Sentiment       Correlation
       │                    │                    │
       ▼                    ▼                    ▼
 Relevance Check       Market Context      Health Report
       │
       ▼
 Educational Answer


                     PaiseWise ML
                          │
             ┌────────────┴────────────┐
             ▼                         ▼
        Churn Model              Fund Model
             │                         │
             ▼                         ▼
       XGBoost Model             Fund Scoring
             │                         │
             ▼                         ▼
       Validation                Validation
             │                         │
             └────────────┬────────────┘
                          ▼
                       MLflow
                          │
                          ▼
                  Model Comparison
                          │
                   ┌──────┴──────┐
                   ▼             ▼
              >2% Better      Not Better
                   │             │
                   ▼             ▼
             Deploy New     Keep Current
```

---

# 113. Final Commands to Remember

### Activate environment

```powershell
.venv\Scripts\Activate.ps1
```

### Run all tests

```powershell
pytest -q
```

### Check ChromaDB

```powershell
python src/check_database.py
```

### Ingest documents

```powershell
python src/ingest_document.py
```

### Test retrieval

```powershell
python src/retrieval_test.py
```

### Test reranking

```powershell
pytest -q src/test_reranker.py
```

### Test Hindi retrieval

```powershell
pytest -q src/test_hindi.py
```

### Test guardrails

```powershell
pytest -q src/test_api_guardrails.py
```

### Start FastAPI

```powershell
uvicorn src.main:app --reload
```

### Open Swagger

```text
http://127.0.0.1:8000/docs
```

### Start MLflow

```powershell
mlflow ui --backend-store-uri sqlite:///C:/Users/Malinirani/Desktop/paiseWise-rag/src/mlflow.db
```

---

# 114. Summary

PaiseWise is a financial education platform built around a RAG architecture.

The core RAG pipeline is:

```text
Question
   ↓
Guardrail
   ↓
Embedding
   ↓
ChromaDB
   ↓
Top 10 Retrieval
   ↓
Re-ranking
   ↓
Relevance Check
   ↓
Educational Answer
```

The market intelligence pipeline is:

```text
NewsAPI
   ↓
News Ingestion
   ↓
Sector Classification
   ↓
Sentiment Analysis
   ↓
Sector Sentiment
   ↓
Market Context
```

The portfolio pipeline is:

```text
Portfolio
   ↓
Diversification
   ↓
Risk
   ↓
Drawdown
   ↓
Correlation
   ↓
Portfolio Health
```

The churn ML pipeline is:

```text
User Activity
   ↓
Feature Engineering
   ↓
XGBoost
   ↓
Validation
   ↓
MLflow
   ↓
Monthly Retraining
   ↓
Deploy if Better
```

The fund retraining pipeline is:

```text
Fund Performance
   ↓
Dynamic Weights
   ↓
Fund Scoring
   ↓
Ranking
   ↓
Validation
   ↓
MLflow
   ↓
Weekly Retraining
   ↓
Deploy if Better
```

The main development commands are:

```powershell
cd C:\Users\Malinirani\Desktop\paiseWise-rag

.venv\Scripts\Activate.ps1

pytest -q

uvicorn src.main:app --reload
```

Then open:

```text
http://127.0.0.1:8000/docs
```

This is the recommended starting point for running and testing the complete PaiseWise application.
