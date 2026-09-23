import time
import requests
import statistics

BASE_URL = "http://127.0.0.1:8000"

tests = [
    {
        "name": "GET /v1/health",
        "method": "GET",
        "url": "/v1/health",
    },
    {
        "name": "GET /v1/",
        "method": "GET",
        "url": "/v1/",
    },
    {
        "name": "GET /v1/market-context",
        "method": "GET",
        "url": "/v1/market-context",
    },
    {
        "name": "GET /v1/news",
        "method": "GET",
        "url": "/v1/news",
    },
    {
        "name": "GET /v1/news/classified",
        "method": "GET",
        "url": "/v1/news/classified",
    },
    {
        "name": "GET /v1/ai/experiments",
        "method": "GET",
        "url": "/v1/ai/experiments",
    },
    {
        "name": "GET /v1/ai/features",
        "method": "GET",
        "url": "/v1/ai/features",
    },
    {
        "name": "GET /v1/ai/languages",
        "method": "GET",
        "url": "/v1/ai/languages",
    },
    {
        "name": "GET /v1/ai/languages/en/fallback",
        "method": "GET",
        "url": "/v1/ai/languages/en/fallback",
    },
    {
        "name": "GET /v1/ai/personalise/U001/learning-dna",
        "method": "GET",
        "url": "/v1/ai/personalise/U001/learning-dna",
    },
    {
        "name": "GET /v1/ai/personalise/U001/notification-time",
        "method": "GET",
        "url": "/v1/ai/personalise/U001/notification-time",
    },
    {
        "name": "GET /v1/ai/personalise/U001/streak-recovery",
        "method": "GET",
        "url": "/v1/ai/personalise/U001/streak-recovery",
    },
    {
        "name": "GET /v1/ai/personalise/U001/daily-lesson",
        "method": "GET",
        "url": "/v1/ai/personalise/U001/daily-lesson",
    },
    {
        "name": "GET /v1/ai/personalise/U001/home",
        "method": "GET",
        "url": "/v1/ai/personalise/U001/home",
    },
]


def test_endpoint(test):
    times = []
    errors = []

    # Warm-up request
    try:
        requests.request(
            test["method"],
            BASE_URL + test["url"],
            timeout=60
        )
    except Exception:
        pass

    # Five measurements
    for _ in range(5):
        try:
            start = time.perf_counter()

            response = requests.request(
                test["method"],
                BASE_URL + test["url"],
                timeout=60
            )

            elapsed = (time.perf_counter() - start) * 1000

            if response.status_code < 400:
                times.append(elapsed)
            else:
                errors.append(response.status_code)

        except Exception as exc:
            errors.append(str(exc))

    if times:
        return {
            "endpoint": test["name"],
            "requests": len(times),
            "average_ms": round(statistics.mean(times), 2),
            "min_ms": round(min(times), 2),
            "max_ms": round(max(times), 2),
            "errors": len(errors),
        }

    return {
        "endpoint": test["name"],
        "requests": 0,
        "average_ms": None,
        "min_ms": None,
        "max_ms": None,
        "errors": len(errors),
    }


print("=" * 90)
print("PaiseWise AI Service - API Performance Baseline")
print("=" * 90)

results = []

for test in tests:
    print(f"\nTesting: {test['name']}")

    result = test_endpoint(test)
    results.append(result)

    print(
        f"Average: {result['average_ms']} ms | "
        f"Min: {result['min_ms']} ms | "
        f"Max: {result['max_ms']} ms | "
        f"Errors: {result['errors']}"
    )


print("\n")
print("=" * 90)
print("FINAL PERFORMANCE BASELINE")
print("=" * 90)

for result in results:
    print(
        f"{result['endpoint']:<55} "
        f"Avg={str(result['average_ms']):>8} ms | "
        f"Min={str(result['min_ms']):>8} ms | "
        f"Max={str(result['max_ms']):>8} ms | "
        f"Errors={result['errors']}"
    )

print("=" * 90)