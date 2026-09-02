# Paisewise AI/ML Platform

Paisewise is a financial AI platform that helps users understand their portfolio, discover suitable mutual funds, learn financial terms, practice paper trading, and detect suspicious activity.

The platform combines a FastAPI backend, AI services, machine learning components, PostgreSQL, Redis, Kafka, MLflow, and Airflow.

## Main AI-Service Flow

```text
Java / Spring Boot
        ↓
      JSON
        ↓
   FastAPI AI Service
        ↓
Validation and preprocessing
        ↓
Gemini / ML models / Business logic
        ↓
Response validation and fallback
        ↓
      JSON
```

The AI service receives structured JSON, validates the input, processes the required data, runs the required AI or ML logic, and returns a structured JSON response.

## Main Features


### Portfolio Insights

The portfolio service combines user details, holdings, market information, and recent news to generate personalized portfolio insights.

It also supports language-based responses and stores generated insights for later use.

### Mutual Fund Recommendations

The recommendation service uses user information and mutual fund data to provide suitable fund recommendations.

Recommendation runs and user clicks are tracked so recommendation performance can be measured.

### Financial Jargon

The jargon service explains financial terms in a simple way.

Terms are stored in the database and Redis is used for faster repeated access.

### Paper Trade Coach

The paper trading feature allows users to practice trading without using real money.

The AI coach can provide feedback based on the paper-trading activity and user input.

### Fraud Detection

The fraud system collects login and transaction-related events and checks them using different signals.

It includes device tracking, login-location tracking, rule-based checks, real-time risk calculation, and machine-learning based fraud detection.

Kafka is used for event-based fraud processing.

### Feature Store

User information is converted into useful features and stored in the `user_features` table.

The feature pipeline also supports feature refresh and monitoring.

### Learning and Personalisation

The learning service uses user progress and previous activity to support personalised learning.

It can adjust learning content based on the user's progress and difficulty level.

### Market and News Data

The platform uses market data and financial news as part of portfolio and recommendation workflows.

Market symbols can be configured through environment variables.

### Caching

Redis is used for frequently requested data and AI-related responses.

Caching helps reduce repeated processing and improves response time.

## Data and Scheduled Pipelines


Airflow is used to automate background data and AI workflows.

The feature store pipeline updates user features from the main user data.

The portfolio insight pipeline follows this flow:

```text
Users with holdings
        ↓
Market data
        ↓
Recent news
        ↓
AI service
        ↓
Portfolio insight
        ↓
PostgreSQL
```

The pipeline can process multiple users and stores the generated portfolio insights in PostgreSQL.

## MLflow


MLflow is used to track the portfolio insight generation process.

The `Portfolio Insight` experiment stores useful information such as user ID, language, risk profile, prompt details, response details, execution time, and generated artifacts.

MLflow helps compare runs and understand AI-service performance.

## Environment


Create a local `.env` file and keep it out of Git:

```env
DATABASE_URL=postgresql+psycopg2://...
DB_HOST=localhost
DB_PORT=5432
DB_NAME=financial_ai
DB_USER=postgres
DB_PASSWORD=...

GEMINI_API_KEY=...
GEMINI_MODEL=gemini-3.6-flash

ALPHA_VANTAGE_API_KEY=...
NEWS_API_KEY=...

AI_SERVICE_URL=http://127.0.0.1:8000/ai/portfolio-insight
SLACK_WEBHOOK=...

MARKET_SYMBOLS=NIFTY50,SENSEX,BANKNIFTY

SHARED_SECRET=...
AI_AUTH_ALLOW_LOCAL=false

SENTRY_DSN=

REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_SSL=false

KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_ORDERS_TOPIC=orders.created
KAFKA_CONSUMER_GROUP=fraud-event-collector
KAFKA_USERNAME=...
KAFKA_PASSWORD=...

MLFLOW_TRACKING_URI=http://127.0.0.1:5000
ENABLE_LLM_WARMING=false
```

## Technologies


* Python
* FastAPI
* PostgreSQL
* SQLAlchemy
* Redis
* Apache Kafka
* Apache Airflow
* MLflow
* Gemini
* Pandas
* Scikit-learn
* Joblib
* Sentry
* Pytest

## Setup


Create and activate a virtual environment:

```bash
python3 -m venv .venv_new
source .venv_new/bin/activate
```

Install the project dependencies:

```bash
pip install -r requirements.txt
```

Create the PostgreSQL database and configure the `.env` file with the required values.

## Run API


Start the FastAPI application using:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

The API can then be tested through Swagger.

## Run MLflow


Start the MLflow tracking server:

```bash
mlflow server --host 0.0.0.0 --port 5000
```

## Run Airflow

Airflow is used for scheduled and background pipelines.

Start the Airflow API server and scheduler according to the local Airflow setup.

The main pipelines can be checked from the Airflow UI.

## Testing

The project includes automated tests for API services, recommendations, fraud detection, paper trading, feature processing, and other platform components.

Run the complete test suite with:

```bash
pytest -q
```

The current test suite passes all 90 tests.

## API and Pipeline Testing


API endpoints can be tested using Swagger or Postman with both valid and invalid JSON inputs.

The Airflow pipelines can be checked from the Airflow UI by running the required DAGs and verifying each task.

MLflow runs can be checked from the MLflow UI to verify that experiments, parameters, metrics, and artifacts are being recorded.

## Project Goal


The main goal of Paisewise is to provide a complete financial AI platform where backend services, AI services, machine learning, data pipelines, and monitoring work together.

The platform is designed to take financial user data, process it through the required services, generate useful AI or ML results, and store the required information for future use.
