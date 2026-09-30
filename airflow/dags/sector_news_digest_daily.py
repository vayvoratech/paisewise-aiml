import asyncio
import sys
from datetime import datetime
from pathlib import Path

from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator # type: ignore

from app.repositories.stocks_repository import StocksRepository
from app.services.news_cache_service import NewsCacheService
from app.services.sector_metadata_provider import SectorMetadataProvider
from app.services.sector_news_digest_service import (
    SectorNewsDigestService,
)


sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[2]),
)


def generate_daily_sector_news_digest() -> None:
    stocks_repository = StocksRepository()
    sector_metadata_provider = SectorMetadataProvider()
    digest_service = SectorNewsDigestService()

    stocks = stocks_repository.get_stocks()

    sectors: set[str] = set()

    for stock in stocks:
        symbol = str(stock.get("symbol") or "").strip()

        if not symbol:
            continue

        sector_info = (
            sector_metadata_provider.get_sector(symbol)
        )

        if sector_info is None:
            continue

        sector = sector_info.sector.strip()

        if sector:
            sectors.add(sector)

    if not sectors:
        return

    digests = asyncio.run(
        digest_service.generate(
            sectors=sorted(sectors),
        )
    )

    for sector, digest in digests.items():
        cache_key = (
            f"sector-news-digest:{sector.lower()}"
        )

        NewsCacheService.set(
            cache_key,
            digest,
        )


with DAG(
    dag_id="sector_news_digest_daily",
    start_date=datetime(2026, 9, 11),
    schedule="0 9 * * *",
    catchup=False,
    tags=[
        "paisewise",
        "task6",
        "sector-news",
    ],
) as dag:

    generate_digest = PythonOperator(
        task_id="generate_daily_sector_news_digest",
        python_callable=(
            generate_daily_sector_news_digest
        ),
    )