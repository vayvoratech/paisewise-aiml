import os
import sentry_sdk
from dotenv import load_dotenv
from fastapi import FastAPI
from routes import jargon
from routes import portfolio
from routes import features
from services.cache_warming import warm_cache
from routes import fund_recommend
from services.fund_catalogue import load_catalogue
from services.catalogue_scheduler import start_catalogue_scheduler
load_dotenv()

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    traces_sample_rate=1.0,
)

app = FastAPI()
@app.on_event("startup")
async def startup_event():

    warm_cache()

    load_catalogue()

    start_catalogue_scheduler()
app.include_router(jargon.router)
app.include_router(portfolio.router)
app.include_router(features.router)
app.include_router(fund_recommend.router)
@app.get("/")
def health_check():
    return {"status": "AI service running"}