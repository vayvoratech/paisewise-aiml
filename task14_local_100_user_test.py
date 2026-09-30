import asyncio
import json
import math
import time
import uuid
from statistics import median

import httpx


BASE_URL = "http://127.0.0.1:8000"
CHAT_PATH = "/ai/chat"
USER_COUNT = 100
CONCURRENCY = 5
EXPECTED_MOCK_TEXT = "Diversification spreads investments across different assets"


async def main() -> None:
    semaphore = asyncio.Semaphore(CONCURRENCY)
    results: list[dict] = []

    async with httpx.AsyncClient(
        timeout=60,
        limits=httpx.Limits(
            max_connections=CONCURRENCY,
            max_keepalive_connections=CONCURRENCY,
        ),
    ) as client:

        async def send_request() -> dict:
            user_id = f"task14-synthetic-{uuid.uuid4().hex}"
            session_id = f"task14-session-{uuid.uuid4().hex}"

            async with semaphore:
                started = time.perf_counter()

                try:
                    response = await client.post(
                        f"{BASE_URL}{CHAT_PATH}",
                        json={
                            "userId": user_id,
                            "sessionId": session_id,
                            "message": "Explain diversification in simple terms.",
                        },
                    )

                    elapsed_ms = (time.perf_counter() - started) * 1000

                    try:
                        body = response.json()
                    except ValueError:
                        body = {}

                    return {
                        "status": response.status_code,
                        "elapsed_ms": round(elapsed_ms, 2),
                        "mock_response_confirmed": (
                            EXPECTED_MOCK_TEXT
                            in str(body.get("message", ""))
                        ),
                        "error": (
                            None
                            if response.is_success
                            else response.text[:200]
                        ),
                    }

                except Exception as exc:
                    elapsed_ms = (time.perf_counter() - started) * 1000
                    return {
                        "status": None,
                        "elapsed_ms": round(elapsed_ms, 2),
                        "mock_response_confirmed": False,
                        "error": str(exc)[:200],
                    }

        overall_started = time.perf_counter()

        results = await asyncio.gather(
            *(send_request() for _ in range(USER_COUNT))
        )

        total_ms = (time.perf_counter() - overall_started) * 1000

    latencies = sorted(row["elapsed_ms"] for row in results)
    successful = sum(
        row["status"] is not None
        and 200 <= row["status"] < 300
        for row in results
    )
    p95_index = max(0, math.ceil(0.95 * len(latencies)) - 1)

    report = {
        "base_url": BASE_URL,
        "synthetic_users": USER_COUNT,
        "requests": USER_COUNT,
        "maximum_concurrency": CONCURRENCY,
        "successful_requests": successful,
        "failed_requests": USER_COUNT - successful,
        "mock_responses_confirmed": sum(
            row["mock_response_confirmed"] for row in results
        ),
        "median_latency_ms": round(median(latencies), 2),
        "p95_latency_ms": round(latencies[p95_index], 2),
        "total_time_ms": round(total_ms, 2),
        "errors": [
            row for row in results if row["error"] is not None
        ][:10],
    }

    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    asyncio.run(main())