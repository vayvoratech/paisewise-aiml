"""
Local Task 14 load test:
100 synthetic users × 9 AI API endpoints = 900 requests.

Gemini calls: 0
PostgreSQL required: no
Redis required: no

Run from the project root:
    .\proj\Scripts\python.exe task14_all_features_loadtest.py
"""

from __future__ import annotations

import asyncio
import importlib
import json
import math
import os
import random
import statistics
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from typing import Any

# Select the existing local mock-provider app before importing it.
os.environ["APP_ENV"] = "staging"
os.environ["TASK14_LOADTEST"] = "1"

import httpx

from task14_loadtest_main import app


def load_module(name: str) -> Any:
    return importlib.import_module(name)


# Import route modules so the test can replace their service boundaries.
chat_routes = load_module("app.api.routes.chat")
fraud_routes = load_module("app.api.routes.fraud")
fund_routes = load_module("app.api.routes.fund_recommendation")
market_routes = load_module("app.api.routes.market_context")
portfolio_routes = load_module("app.api.routes.portfolio_analytics")
sector_routes = load_module("app.api.routes.sector_news")
stock_news_routes = load_module("app.api.routes.stock_news")
discovery_routes = load_module("app.api.routes.stock_discovery")


# Chat uses a fixed local response. No Gemini request is made.
class FakeChatService:
    async def process_chat(self, request: Any) -> Any:
        from app.schemas.chat import ChatResponse

        return ChatResponse(
            status="success",
            responseId=str(uuid.uuid4()),
            message="Mock chat response for local load testing.",
            category="general",
        )


chat_routes.get_chat_service = FakeChatService


# Fraud route and decision logic run with a deterministic fake model and order.
class FakeFraudModel:
    def predict_proba(self, features: Any) -> list[list[float]]:
        return [[0.85, 0.15]]


class FakeFraudOrderRepository:
    def get_order_by_id(self, order_id: str) -> dict[str, Any]:
        return {
            "id": order_id,
            "user_id": "synthetic-load-user",
            "symbol": "NSE:RELIANCE",
            "side": "BUY",
            "shares": 10,
            "price_per_share": 2500.0,
            "total_amount": 25000.0,
            "order_type": "MARKET",
            "xp_earned": 0,
            "created_at": None,
        }


fraud_routes.FraudOrderRepository = FakeFraudOrderRepository
fraud_routes.fraud_runtime.get_runtime = lambda: SimpleNamespace(
    model=FakeFraudModel()
)


# Stub service boundaries that otherwise access user data or external systems.
class FakeFundRecommendationService:
    def recommend(
        self,
        *,
        user_id: str,
        goal: str | None = None,
        level: str | None = None,
    ) -> Any:
        from app.schemas.fund_recommendation import (
            FundRecommendationResponse,
        )

        return FundRecommendationResponse(
            userId=user_id,
            recommendations=[],
            trendingAmongLearners=[],
        )


fund_routes.FundRecommendationService = FakeFundRecommendationService


class FakeMarketContextService:
    async def get_market_context(self) -> Any:
        from app.schemas.market_context import MarketContextResponse

        return MarketContextResponse(
            asOf=datetime.now(timezone.utc).isoformat(),
            indices=[],
            news=[],
        )


market_routes.MarketContextService = FakeMarketContextService
portfolio_routes.MarketContextService = FakeMarketContextService


class FakePortfolioAnalyticsService:
    def calculate(self, *, user_id: str) -> Any:
        from app.schemas.portfolio_analytics import (
            HoldingAnalytics,
            PortfolioAnalyticsResponse,
        )

        holding = HoldingAnalytics(
            symbol="NSE:RELIANCE",
            shares=1,
            avg_price=100.0,
            current_price=105.0,
            invested_value=100.0,
            current_value=105.0,
            pnl=5.0,
            pnl_percentage=5.0,
        )

        return PortfolioAnalyticsResponse(
            userId=user_id,
            holdingsCount=1,
            totalInvested=100.0,
            currentValue=105.0,
            totalPnl=5.0,
            pnlPercentage=5.0,
            holdings=[holding],
        )


class FakePortfolioHealthService:
    def __init__(self, llm_provider: Any = None) -> None:
        pass

    async def generate_report(
        self,
        *,
        analytics: Any,
        market_context: Any,
    ) -> str:
        return "Mock portfolio health report."


portfolio_routes.PortfolioAnalyticsService = FakePortfolioAnalyticsService
portfolio_routes.PortfolioHealthService = FakePortfolioHealthService


class FakeNewsCacheService:
    @staticmethod
    def get_news_cache(cache_key: str) -> None:
        return None

    @staticmethod
    def set_news_cache(**kwargs: Any) -> None:
        return None

    @staticmethod
    def is_newer_article_available(**kwargs: Any) -> bool:
        return True


sector_routes.NewsCacheService = FakeNewsCacheService
stock_news_routes.NewsCacheService = FakeNewsCacheService


class FakeSectorNewsService:
    async def get_news(self, *, sector: str, limit: int) -> list[Any]:
        return []


class FakeStockNewsService:
    async def get_news(self, *, symbol: str, limit: int) -> list[Any]:
        return []


class FakeStockDiscoveryService:
    async def discover(self, *, user_id: str) -> list[Any]:
        return []


sector_routes.SectorNewsService = FakeSectorNewsService
stock_news_routes.StockNewsService = FakeStockNewsService
discovery_routes.StockDiscoveryService = FakeStockDiscoveryService


FEATURES = (
    "chat",
    "churn_score",
    "fraud_score",
    "fund_recommendations",
    "market_context",
    "portfolio_analytics",
    "sector_news",
    "stock_news",
    "stock_discovery",
)


def make_user_requests(
    user_id: str,
) -> list[tuple[str, str, dict[str, Any]]]:
    order_id = str(uuid.uuid4())

    requests = [
        (
            "chat",
            "POST",
            {
                "path": "/ai/chat",
                "json": {
                    "userId": user_id,
                    "sessionId": f"task14-{user_id}",
                    "message": "Explain diversification briefly.",
                },
            },
        ),
        (
            "churn_score",
            "POST",
            {
                "path": "/ai/churn-score",
                "json": {
                    "userId": user_id,
                    "daysSinceLastActivity": 2,
                    "sessionCount7d": 5,
                    "completedJourneySteps": 2,
                    "totalJourneySteps": 5,
                    "daysSinceRegistration": 30,
                },
            },
        ),
        (
            "fraud_score",
            "POST",
            {
                "path": "/fraud/score",
                "json": {"order_id": order_id},
            },
        ),
        (
            "fund_recommendations",
            "POST",
            {
                "path": "/ai/fund-recommendations",
                "json": {
                    "userId": user_id,
                    "context": {
                        "goal": "long-term wealth",
                        "level": "2",
                    },
                },
            },
        ),
        (
            "market_context",
            "GET",
            {"path": "/ai/market-context"},
        ),
        (
            "portfolio_analytics",
            "GET",
            {"path": f"/ai/portfolio-analytics/{user_id}"},
        ),
        (
            "sector_news",
            "GET",
            {"path": "/ai/sector-news/Banking"},
        ),
        (
            "stock_news",
            "GET",
            {"path": "/ai/stock-news/NSE%3ARELIANCE"},
        ),
        (
            "stock_discovery",
            "GET",
            {"path": f"/ai/stock-discovery/{user_id}"},
        ),
    ]

    return requests


def percentile(values: list[float], pct: float) -> float | None:
    if not values:
        return None

    ordered = sorted(values)
    index = max(0, math.ceil(pct / 100 * len(ordered)) - 1)
    return round(ordered[index], 3)


async def run_load_test() -> dict[str, Any]:
    users = [str(uuid.uuid4()) for _ in range(100)]
    random.Random(14).shuffle(users)

    # Keep concurrency low for an i3 / 4 GB machine.
    semaphore = asyncio.Semaphore(5)
    results: list[dict[str, Any]] = []
    active_requests = 0
    max_active_requests = 0

    transport = httpx.ASGITransport(
        app=app,
        raise_app_exceptions=False,
    )

    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://task14-local.test",
        timeout=10.0,
    ) as client:

        async def send_one(
            user_id: str,
            feature: str,
            method: str,
            request: dict[str, Any],
        ) -> dict[str, Any]:
            nonlocal active_requests, max_active_requests

            async with semaphore:
                active_requests += 1
                max_active_requests = max(
                    max_active_requests,
                    active_requests,
                )
                started = time.perf_counter()

                try:
                    response = await client.request(
                        method,
                        request["path"],
                        json=request.get("json"),
                    )
                    elapsed_ms = (
                        time.perf_counter() - started
                    ) * 1000

                    return {
                        "user_id": user_id,
                        "feature": feature,
                        "status": response.status_code,
                        "elapsed_ms": round(elapsed_ms, 3),
                        "error": (
                            None
                            if response.is_success
                            else response.text[:300]
                        ),
                    }
                except Exception as exc:
                    elapsed_ms = (
                        time.perf_counter() - started
                    ) * 1000
                    return {
                        "user_id": user_id,
                        "feature": feature,
                        "status": None,
                        "elapsed_ms": round(elapsed_ms, 3),
                        "error": f"{type(exc).__name__}: {exc}",
                    }
                finally:
                    active_requests -= 1

        async def run_user(user_id: str) -> list[dict[str, Any]]:
            user_requests = make_user_requests(user_id)
            random.Random(user_id).shuffle(user_requests)

            return await asyncio.gather(
                *(
                    send_one(user_id, feature, method, request)
                    for feature, method, request in user_requests
                )
            )

        started_all = time.perf_counter()
        user_results = await asyncio.gather(
            *(run_user(user_id) for user_id in users)
        )
        total_time_ms = (
            time.perf_counter() - started_all
        ) * 1000

    for user_result in user_results:
        results.extend(user_result)

    successful = [
        result
        for result in results
        if result["status"] is not None
        and 200 <= result["status"] < 300
    ]
    failed = [
        result
        for result in results
        if result["status"] is None
        or not 200 <= result["status"] < 300
    ]
    latencies = [result["elapsed_ms"] for result in results]

    feature_results = {}

    for feature in FEATURES:
        feature_rows = [
            result
            for result in results
            if result["feature"] == feature
        ]
        feature_latencies = [
            result["elapsed_ms"]
            for result in feature_rows
        ]
        feature_successes = sum(
            result["status"] is not None
            and 200 <= result["status"] < 300
            for result in feature_rows
        )

        feature_results[feature] = {
            "requests": len(feature_rows),
            "successful": feature_successes,
            "failed": len(feature_rows) - feature_successes,
            "p95_ms": percentile(feature_latencies, 95),
        }

    return {
        "test": "task14_mocked_all_feature_local_load_test",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "data_classification": "synthetic_test_users",
        "execution": "in_process_local_fastapi",
        "simulated_users": len(users),
        "requests_per_user": len(FEATURES),
        "total_requests": len(results),
        "configured_max_concurrency": 5,
        "observed_max_concurrency": max_active_requests,
        "successful_requests": len(successful),
        "failed_requests": len(failed),
        "median_latency_ms": (
            round(statistics.median(latencies), 3)
            if latencies
            else None
        ),
        "p95_latency_ms": percentile(latencies, 95),
        "total_time_ms": round(total_time_ms, 3),
        "feature_results": feature_results,
        "gemini_calls": 0,
        "external_network_calls": 0,
        "redis_or_postgres_required": False,
        "limitations": [
            "External/model and persistence boundaries are mocked.",
            "This does not measure Gemini latency, model quality, "
            "database capacity, or network/server throughput.",
            "Churn and fraud calculation paths use synthetic inputs "
            "and a fixed fake fraud model.",
        ],
        "failure_samples": failed[:20],
    }


if __name__ == "__main__":
    report = asyncio.run(run_load_test())

    output_dir = Path("artifacts")
    output_dir.mkdir(exist_ok=True)

    report_path = output_dir / "task14_all_features_loadtest.json"
    report_path.write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )

    print(json.dumps(report, indent=2))
    print(f"\nReport saved to: {report_path}")