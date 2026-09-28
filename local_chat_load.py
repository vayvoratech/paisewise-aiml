import asyncio
import json
import time
from statistics import median

import httpx

BASE_URL = "http://127.0.0.1:8000"
CHAT_PATH = "/ai/chat"  # Change this if your chat route uses a different path.
REQUEST_COUNT = 5
CONCURRENCY = 1


async def main():
    semaphore = asyncio.Semaphore(CONCURRENCY)
    results = []

    async with httpx.AsyncClient(
        base_url=BASE_URL,
        timeout=60,
        limits=httpx.Limits(
            max_connections=CONCURRENCY,
            max_keepalive_connections=CONCURRENCY,
        ),
    ) as client:

        async def send_request(index: int):
            payload = {
                "userId": "local-load-test",
                "sessionId": f"local-load-session-{index}",
                "message": f"Explain diversification in simple terms. Request {index}.",
            }

            async with semaphore:
                started = time.perf_counter()
                try:
                    response = await client.post(CHAT_PATH, json=payload)
                    elapsed_ms = (time.perf_counter() - started) * 1000
                    results.append({
                        "status": response.status_code,
                        "elapsed_ms": round(elapsed_ms, 2),
                        "error": None if response.is_success else response.text[:300],
                    })
                except Exception as exc:
                    elapsed_ms = (time.perf_counter() - started) * 1000
                    results.append({
                        "status": None,
                        "elapsed_ms": round(elapsed_ms, 2),
                        "error": str(exc)[:300],
                    })

        overall_started = time.perf_counter()
        await asyncio.gather(*(send_request(i) for i in range(REQUEST_COUNT)))
        overall_ms = (time.perf_counter() - overall_started) * 1000

    latencies = sorted(item["elapsed_ms"] for item in results)
    successful = sum(
        item["status"] is not None and 200 <= item["status"] < 300
        for item in results
    )

    report = {
        "base_url": BASE_URL,
        "chat_path": CHAT_PATH,
        "requests": REQUEST_COUNT,
        "concurrency": CONCURRENCY,
        "successful_requests": successful,
        "failed_requests": REQUEST_COUNT - successful,
        "median_latency_ms": round(median(latencies), 2) if latencies else None,
        "p95_latency_ms": (
            round(latencies[min(len(latencies) - 1, int(len(latencies) * 0.95))], 2)
            if latencies else None
        ),
        "total_time_ms": round(overall_ms, 2),
        "results": results,
    }

    print(json.dumps(report, indent=2))


asyncio.run(main())