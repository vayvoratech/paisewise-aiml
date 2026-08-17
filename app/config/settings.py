import os

from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

GEMINI_MODEL = os.getenv("GEMINI_MODEL")

ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")

NEWS_API_KEY = os.getenv("NEWS_API_KEY")

SLACK_WEBHOOK = os.getenv("SLACK_WEBHOOK")

AI_SERVICE_URL = os.getenv("AI_SERVICE_URL")

DATABASE_URL = os.getenv("DATABASE_URL")
