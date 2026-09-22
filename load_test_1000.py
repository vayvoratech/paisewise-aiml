import asyncio
import time
import statistics

import aiohttp


# ============================================================
# PaiseWise 1,000 Concurrent User Load Test
# ============================================================

BASE_URL = "http://127.0.0.1:8000"

# Total simulated users
TOTAL_USERS = 1000

# Maximum requests running at the same time
MAX_CONCURRENT = 100

# Endpoint used for the load test
ENDPOINT = "/health"

# Individual request timeout
REQUEST_TIMEOUT = 30


async def make_request(
    session,
    semaphore,
    user_number
):
    """
    Simulate one user making one API request.
    """

    async with semaphore:

        start_time = time.perf_counter()

        try:
            async with session.get(
                f"{BASE_URL}{ENDPOINT}"
            ) as response:

                await response.read()

                elapsed = (
                    time.perf_counter() - start_time
                ) * 1000

                return {
                    "user": user_number,
                    "status": response.status,
                    "response_time_ms": elapsed,
                    "success": 200 <= response.status < 300
                }

        except Exception as e:

            elapsed = (
                time.perf_counter() - start_time
            ) * 1000

            return {
                "user": user_number,
                "status": None,
                "response_time_ms": elapsed,
                "success": False,
                "error": str(e)
            }


async def run_load_test():

    print("=" * 70)
    print("PaiseWise 1,000 Concurrent User Load Test")
    print("=" * 70)

    print(f"Target endpoint : {BASE_URL}{ENDPOINT}")
    print(f"Total users     : {TOTAL_USERS}")
    print(f"Concurrency     : {MAX_CONCURRENT}")
    print()

    timeout = aiohttp.ClientTimeout(
        total=REQUEST_TIMEOUT
    )

    connector = aiohttp.TCPConnector(
        limit=MAX_CONCURRENT,
        limit_per_host=MAX_CONCURRENT,
        ttl_dns_cache=300
    )

    semaphore = asyncio.Semaphore(
        MAX_CONCURRENT
    )

    start_time = time.perf_counter()

    async with aiohttp.ClientSession(
        timeout=timeout,
        connector=connector
    ) as session:

        tasks = [
            make_request(
                session,
                semaphore,
                user_number
            )
            for user_number in range(
                1,
                TOTAL_USERS + 1
            )
        ]

        results = await asyncio.gather(
            *tasks
        )

    total_time = (
        time.perf_counter() - start_time
    )

    successful = [
        result
        for result in results
        if result["success"]
    ]

    failed = [
        result
        for result in results
        if not result["success"]
    ]

    response_times = [
        result["response_time_ms"]
        for result in results
    ]

    error_rate = (
        len(failed) / TOTAL_USERS
    ) * 100

    requests_per_second = (
        TOTAL_USERS / total_time
    )

    print()
    print("=" * 70)
    print("LOAD TEST RESULTS")
    print("=" * 70)

    print(f"Total requests       : {TOTAL_USERS}")
    print(f"Successful requests  : {len(successful)}")
    print(f"Failed requests      : {len(failed)}")
    print(f"Error rate           : {error_rate:.2f}%")
    print(f"Total test time      : {total_time:.2f} seconds")
    print(f"Requests/second      : {requests_per_second:.2f}")

    if response_times:

        print(
            f"Average response     : "
            f"{statistics.mean(response_times):.2f} ms"
        )

        print(
            f"Minimum response     : "
            f"{min(response_times):.2f} ms"
        )

        print(
            f"Maximum response     : "
            f"{max(response_times):.2f} ms"
        )

    print()
    print("=" * 70)

    if error_rate < 5:
        print("RESULT: PASS")
        print("Error rate is below the 5% requirement.")
    else:
        print("RESULT: FAIL")
        print("Error rate is 5% or higher.")

    print("=" * 70)

    if failed:

        print()
        print("Sample failures:")

        for result in failed[:10]:

            print(
                f"User {result['user']}: "
                f"{result.get('error', 'HTTP error')}"
            )


if __name__ == "__main__":

    asyncio.run(
        run_load_test()
    )