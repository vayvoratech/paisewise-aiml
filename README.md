# PaiseWise RAG API

A Retrieval-Augmented Generation (RAG) based financial education API for **PaiseWise**.

The project combines a financial knowledge base, vector search, document embeddings, re-ranking, guardrails, market context, and market-news ingestion/classification into a FastAPI application.

---

## 1. Project Overview

The PaiseWise RAG system is designed to answer general financial education questions using information stored in a knowledge base.

The main flow is:

```text
User Question
      ↓
FastAPI
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

The market-news flow is:

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
Market Context
```

---

# 2. Technologies Used

* Python
* FastAPI
* Uvicorn
* ChromaDB
* Sentence Transformers
* Hugging Face Transformers
* NewsAPI
* Requests
* Pydantic
* VADER Sentiment
* XGBoost
* Git/GitHub

---

# 3. Knowledge Base

The PaiseWise knowledge base contains financial education information such as:

* 30 lesson contents
* 200 financial jargon definitions
* PaiseWise product FAQs
* SEBI-approved financial education content
* Mutual fund category explanations

The documents are converted into chunks before being stored in ChromaDB.

### Chunking Strategy

```text
Chunk Size  : 200 words
Overlap     : 50 words
```

The overlap helps preserve context between consecutive chunks.

---

# 4. Project Structure

Recommended project structure:

```text
paiseWise-rag/
│
├── src/
│   │
│   ├── main.py
│   ├── embeddings.py
│   ├── reranker.py
│   ├── guardrails.py
│   ├── market_context.py
│   ├── news_ingestion.py
│   ├── news_classifier.py
│   ├── ingest_document.py
│   ├── chunking.py
│   ├── retrieval_test.py
│   ├── evaluate_retrieval.py
│   └── check_database.py
│
├── data/
│   ├── lessons/
│   └── jargon/
│
├── chroma_db/
│
├── requirements.txt
├── .env
└── README.md
```

---

# 5. Start From Scratch

## Step 1: Clone the Repository

Open PowerShell or Command Prompt.

```powershell
git clone <YOUR_REPOSITORY_URL>
```

Move into the project:

```powershell
cd paiseWise-rag
```

If you are using a specific branch:

```powershell
git checkout <YOUR_BRANCH_NAME>
```

---

# 6. Create Python Virtual Environment

Create a virtual environment:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\activate
```

After activation, you should see something similar to:

```text
(.venv) PS C:\Users\...\paiseWise-rag>
```

---

# 7. Upgrade pip

```powershell
python -m pip install --upgrade pip
```

---

# 8. Install Required Packages

Install the main dependencies:

```powershell
pip install fastapi uvicorn chromadb sentence-transformers transformers requests pydantic vaderSentiment xgboost pandas numpy scikit-learn python-dotenv
```

If a `requirements.txt` file is available:

```powershell
pip install -r requirements.txt
```

---

# 9. Verify Python Environment

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

---

# 10. Prepare the Data

Place lesson files inside:

```text
data/lessons/
```

Place jargon files inside:

```text
data/jargon/
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

# 11. Document Chunking

The document ingestion process divides large documents into smaller chunks.

Current strategy:

```text
200 words per chunk
50 words overlap
```

Example:

```text
Original Document
       ↓
Chunk 1 → 200 words
       ↓
Chunk 2 → 200 words
       ↓
Chunk 3 → 200 words
```

The 50-word overlap helps prevent important information from being lost between chunks.

---

# 12. Generate Embeddings

The project uses:

```text
all-MiniLM-L6-v2
```

from Sentence Transformers.

The process is:

```text
Document
   ↓
Text
   ↓
Sentence Transformer
   ↓
Vector Embedding
```

The same embedding model is used to convert user questions into vectors.

---

# 13. ChromaDB Setup

The project uses ChromaDB as the local vector database.

Database path:

```text
../chroma_db
```

Collection name:

```text
paisewise_knowledge_base
```

The collection stores:

```text
Document
Embedding
Metadata
ID
```

---

# 14. Ingest Documents

From the `src` directory:

```powershell
cd src
```

Run the document ingestion script according to the current project implementation.

Example:

```powershell
python ingest_document.py
```

The ingestion process is:

```text
Lesson/Jargon File
       ↓
Read Document
       ↓
Chunk Text
       ↓
Create Embedding
       ↓
Generate Chunk ID
       ↓
Store in ChromaDB
```

---

# 15. Check ChromaDB

Run:

```powershell
python check_database.py
```

This checks whether documents have been successfully stored.

Expected type of output:

```text
Collection: paisewise_knowledge_base
Document count: ...
```

---

# 16. Test Basic Retrieval

Run:

```powershell
python retrieval_test.py
```

This tests multiple financial questions against the vector database.

Example questions:

```text
What is a mutual fund?
What is SIP?
What is NAV?
What is an expense ratio?
What is diversification?
What is equity?
```

The retrieval system returns the most similar chunks.

---

# 17. Understanding ChromaDB Distance

ChromaDB retrieval returns a distance value.

Generally:

```text
Lower distance = More similar
Higher distance = Less similar
```

Example:

```text
Question: What is SIP?

Result 1 distance: 0.43
Result 2 distance: 0.82
Result 3 distance: 1.10
```

Result 1 is more similar than Result 2 and Result 3.

---

# 18. Re-ranking

Initial retrieval gets the top 10 documents.

```text
Question
   ↓
ChromaDB
   ↓
Top 10 documents
   ↓
Re-ranker
   ↓
Best relevant document
```

The re-ranker calculates relevance using the question and retrieved document.

Run the re-ranker test:

```powershell
python test_reranker.py
```

The re-ranker score is interpreted differently from ChromaDB distance:

```text
Higher relevance score = More relevant
```

---

# 19. Retrieval Evaluation

Run:

```powershell
python evaluate_retrieval.py
```

This is used to evaluate whether the correct content is being retrieved for test questions.

The evaluation helps identify issues such as:

```text
Correct question
      ↓
Wrong document retrieved
```

or:

```text
Different questions
      ↓
Same document repeatedly retrieved
```

---

# 20. Guardrails

The PaiseWise assistant is intended for financial education and should not provide personalized investment recommendations.

The guardrail checks questions such as:

```text
Which stock should I buy?
Should I sell this stock?
Which mutual fund is best for me?
Should I invest in this SIP?
```

These questions should be deflected.

Educational questions such as:

```text
What is SIP?
What is NAV?
What is a mutual fund?
What is diversification?
```

can be answered.

---

# 21. FastAPI Application

The main API file is:

```text
src/main.py
```

It connects:

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
Reranker
   ↓
Answer
```

---

# 22. Start FastAPI With Uvicorn

Make sure you are inside the `src` directory:

```powershell
cd src
```

Run:

```powershell
uvicorn main:app --reload
```

You should see:

```text
Uvicorn running on http://127.0.0.1:8000
```

---

# 23. Run Uvicorn With Host and Port

To expose the API on a specific host and port:

```powershell
uvicorn main:app --host 0.0.0.0 --port 8000
```

For local development:

```powershell
uvicorn main:app --host 127.0.0.1 --port 8000
```

With auto reload:

```powershell
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

---

# 24. Open Swagger API Documentation

After starting Uvicorn, open:

```text
http://127.0.0.1:8000/docs
```

FastAPI automatically provides Swagger UI.

You can test all API endpoints from the browser.

---

# 25. Home Endpoint

Endpoint:

```text
GET /
```

Open:

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

# 26. Health Endpoint

Endpoint:

```text
GET /health
```

Open:

```text
http://127.0.0.1:8000/health
```

It checks:

```text
API status
ChromaDB connection
Collection name
Document count
```

---

# 27. Ask Question API

Endpoint:

```text
POST /ask
```

Use Swagger:

```text
http://127.0.0.1:8000/docs
```

Select:

```text
POST /ask
```

Click:

```text
Try it out
```

Enter:

```json
{
    "question": "What is SIP?"
}
```

Click:

```text
Execute
```

---

# 28. `/ask` Internal Flow

When the user asks:

```text
What is SIP?
```

the API performs:

```text
1. Receive question
        ↓
2. Check empty input
        ↓
3. Guardrail check
        ↓
4. Create embedding
        ↓
5. Search ChromaDB
        ↓
6. Retrieve top 10
        ↓
7. Re-rank documents
        ↓
8. Select best document
        ↓
9. Check relevance threshold
        ↓
10. Return answer
```

---

# 29. Relevance Threshold

The current API uses:

```python
RELEVANCE_THRESHOLD = 0.25
```

If the best result has a score below the threshold, the API returns:

```text
I couldn't find relevant information
in the PaiseWise knowledge base.
```

This prevents unrelated content from being returned as an answer.

---

# 30. Market Context

Endpoint:

```text
GET /market-context
```

The market context module creates a summary using:

```text
News Count
Sector Sentiment
NIFTY Change
```

Example:

```text
News Count: 20

IT:
Positive

Banking:
Neutral

Pharma:
Positive

NIFTY:
+0.75%
```

The endpoint can be tested through:

```text
http://127.0.0.1:8000/docs
```

---

# 31. News Ingestion

The project uses NewsAPI to retrieve market-related news.

The news search query is:

```text
NSE OR BSE OR NIFTY OR Sensex
```

The ingestion process retrieves:

* Article title
* Description
* Source
* Published date
* URL

---

# 32. NewsAPI Key

The news ingestion module reads:

```python
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
```

Set the environment variable before running the news ingestion.

### PowerShell

```powershell
$env:NEWS_API_KEY="YOUR_NEWS_API_KEY"
```

Verify:

```powershell
echo $env:NEWS_API_KEY
```

Do not commit the API key to GitHub.

---

# 33. Run News Ingestion Directly

From `src`:

```powershell
python news_ingestion.py
```

Expected flow:

```text
============================================================
PaiseWise News Ingestion
============================================================

Articles fetched: 20

1. Article title
2. Article title
3. Article title
...
```

At the end:

```text
News ingestion completed successfully.
```

---

# 34. News Sector Classification

The project uses Hugging Face zero-shot classification.

Model:

```text
valhalla/distilbart-mnli-12-3
```

The classifier assigns a sector to each article.

Current sectors:

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

---

# 35. News Classification Flow

```text
News Article
      ↓
Title + Description
      ↓
Zero-Shot Classifier
      ↓
Compare Candidate Sectors
      ↓
Select Highest Score
      ↓
Sector + Confidence
```

Example:

```text
TCS reports strong quarterly growth
          ↓
Sector: IT
Confidence: 0.xx
```

---

# 36. Run News Classifier

Run:

```powershell
python news_classifier.py
```

The script loads the zero-shot classification model.

The first execution may take longer because the model needs to be downloaded.

---

# 37. News API Endpoint

The FastAPI application exposes:

```text
GET /news
```

This calls:

```python
fetch_market_news()
```

from:

```text
news_ingestion.py
```

It returns the latest market news.

---

# 38. Classify News Through API

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

Expected type of response:

```json
{
    "title": "TCS reports strong quarterly growth",
    "description": "The IT company reported improved revenue.",
    "sector": "IT",
    "confidence": 0.XX
}
```

---

# 39. Fetch and Classify All News

Endpoint:

```text
GET /news/classified
```

The complete flow is:

```text
GET /news/classified
        ↓
fetch_market_news()
        ↓
NewsAPI
        ↓
20 Articles
        ↓
classify_article()
        ↓
Sector Classification
        ↓
Confidence
        ↓
JSON Response
```

The response contains information such as:

```text
Title
Description
Source
Published At
URL
Sector
Confidence
```

---

# 40. Complete Project Architecture

```text
                         PaiseWise
                            │
                            ▼
                       FastAPI API
                            │
              ┌─────────────┴─────────────┐
              │                           │
           RAG Flow                   News Flow
              │                           │
              ▼                           ▼
         User Question                NewsAPI
              │                           │
              ▼                           ▼
         Guardrails                News Ingestion
              │                           │
              ▼                           ▼
         Embeddings               News Articles
              │                           │
              ▼                           ▼
          ChromaDB                 Sector Classifier
              │                           │
              ▼                           ▼
       Top 10 Retrieval             Sector + Score
              │                           │
              ▼                           │
          Re-ranker                       │
              │                           │
              ▼                           │
        Best Document                     │
              │                           │
              └──────────┬────────────────┘
                         ▼
                   Market Context
```

---

# 41. Complete Commands From Scratch

The basic development sequence is:

```powershell
git clone <YOUR_REPOSITORY_URL>

cd paiseWise-rag

python -m venv .venv

.venv\Scripts\activate

python -m pip install --upgrade pip

pip install -r requirements.txt

cd src

python ingest_document.py

python check_database.py

python retrieval_test.py

python test_reranker.py

python evaluate_retrieval.py

python news_ingestion.py

python news_classifier.py

uvicorn main:app --reload
```

Then open:

```text
http://127.0.0.1:8000/docs
```

---

# 42. Useful Uvicorn Commands

### Development

```powershell
uvicorn main:app --reload
```

### Specific Host and Port

```powershell
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Host + Port + Reload

```powershell
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Different Port

```powershell
uvicorn main:app --host 127.0.0.1 --port 8080 --reload
```

Then open:

```text
http://127.0.0.1:8080/docs
```

---

# 43. Troubleshooting

## ChromaDB not found

Check that the database exists at:

```text
../chroma_db
```

from the `src` directory.

Check:

```powershell
python check_database.py
```

---

## Sentence Transformers Error

Install:

```powershell
pip install sentence-transformers
```

Test:

```powershell
python -c "from sentence_transformers import SentenceTransformer; print('Sentence Transformers OK')"
```

---

## Pandas Error

If you see:

```text
ModuleNotFoundError: No module named 'pandas'
```

run:

```powershell
pip install pandas
```

---

## News API Key Error

If you see:

```text
NEWS_API_KEY environment variable is not set.
```

PowerShell:

```powershell
$env:NEWS_API_KEY="YOUR_NEWS_API_KEY"
```

Then run:

```powershell
python news_ingestion.py
```

---

## Hugging Face Warning

You may see a warning about unauthenticated requests to the Hugging Face Hub.

For development, the model can still be downloaded, but rate limits may be lower.

If your environment uses a Hugging Face token, configure it appropriately.

---

## Uvicorn Import Error

If you see:

```text
Error loading ASGI app
```

make sure you are inside the directory containing `main.py`.

For example:

```powershell
cd src
uvicorn main:app --reload
```

The command:

```text
main:app
```

means:

```text
main.py
   ↓
app = FastAPI(...)
```

---

# 44. Git Commands

Check status:

```powershell
git status
```

Add files:

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

Check branch:

```powershell
git branch
```

Switch branch:

```powershell
git checkout <BRANCH_NAME>
```

---

# 45. Development Workflow

For normal development, use this workflow:

```text
1. Activate environment
        ↓
2. Go to src
        ↓
3. Update code
        ↓
4. Test individual Python files
        ↓
5. Check ChromaDB
        ↓
6. Start FastAPI
        ↓
7. Open /docs
        ↓
8. Test API endpoints
```

Commands:

```powershell
.venv\Scripts\activate

cd src

python check_database.py

python retrieval_test.py

python test_reranker.py

python news_ingestion.py

python news_classifier.py

uvicorn main:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

---

# 46. Final API Endpoints

The current API provides:

```text
GET  /
GET  /health
POST /ask
GET  /market-context
GET  /news
POST /news/classify
GET  /news/classified
```

---

# 47. Final End-to-End Flow

### Financial Education

```text
User
 ↓
POST /ask
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
Relevance Threshold
 ↓
PaiseWise Answer
```

### Market News

```text
GET /news
 ↓
NewsAPI
 ↓
fetch_market_news()
 ↓
Market Articles
```

### News Classification

```text
GET /news/classified
 ↓
NewsAPI
 ↓
fetch_market_news()
 ↓
classify_article()
 ↓
Zero-Shot Classification
 ↓
Sector
 ↓
Confidence
 ↓
API Response
```

### Market Context

```text
Market News
     +
Sector Information
     +
Market/NIFTY Information
     ↓
create_market_context()
     ↓
Market Context
```

---

# 48. Important Security Notes

Do not commit API keys or secrets to GitHub.

Do not write:

```python
NEWS_API_KEY = "actual-secret-key"
```

inside the source code.

Use an environment variable:

```text
NEWS_API_KEY
```

and keep secret files such as `.env` out of Git.

Example `.gitignore`:

```text
.venv/
.env
__pycache__/
chroma_db/
*.pyc
```

---

# 49. Quick Start

If everything is already installed and the database is populated:

```powershell
cd paiseWise-rag

.venv\Scripts\activate

cd src

uvicorn main:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

Test:

```text
POST /ask
GET /market-context
GET /news
POST /news/classify
GET /news/classified
```

This starts the PaiseWise API from the existing ChromaDB knowledge base through the RAG and market-news pipeline.

