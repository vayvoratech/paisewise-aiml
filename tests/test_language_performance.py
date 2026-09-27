import statistics
import time

import pytest
import requests


BASE_URL = "http://127.0.0.1:8000"


def measure_request(
    endpoint,
    payload,
    runs=5
):
    times = []
    statuses = []

    for i in range(runs):

        start = time.perf_counter()

        response = requests.post(
            f"{BASE_URL}{endpoint}",
            json=payload,
            timeout=120
        )

        end = time.perf_counter()

        elapsed = end - start

        times.append(elapsed)
        statuses.append(response.status_code)

        print(
            f"Run {i + 1}: "
            f"{elapsed:.3f} seconds "
            f"| Status: {response.status_code}"
        )

    return {
        "average": statistics.mean(times),
        "minimum": min(times),
        "maximum": max(times),
        "statuses": statuses
    }


def print_result(name, result):

    print("\n" + "=" * 60)
    print(name)
    print("=" * 60)

    print(
        f"Average: {result['average']:.3f} seconds"
    )

    print(
        f"Minimum: {result['minimum']:.3f} seconds"
    )

    print(
        f"Maximum: {result['maximum']:.3f} seconds"
    )

    print(
        f"Statuses: {result['statuses']}"
    )


def server_is_running():

    try:
        response = requests.get(
            f"{BASE_URL}/health",
            timeout=3
        )

        return response.status_code < 500

    except requests.RequestException:

        return False


@pytest.mark.integration
def test_multi_language_performance():

    if not server_is_running():

        pytest.skip(
            "FastAPI server is not running at "
            f"{BASE_URL}"
        )

    print("\n")
    print("=" * 60)
    print("PAISEWISE MULTI-LANGUAGE PERFORMANCE TEST")
    print("=" * 60)

    # =================================================
    # TEST 1: ENGLISH / AI CHAT
    # =================================================

    print("\nTesting /ai/chat - English")

    english_chat = measure_request(
        endpoint="/ai/chat",
        payload={
            "userId": "PERF_EN_USER",
            "sessionId": "PERF_EN",
            "message": "What is a mutual fund?"
        },
        runs=5
    )

    print_result(
        "English /ai/chat",
        english_chat
    )

    # =================================================
    # TEST 2: TELUGU / AI CHAT
    # =================================================

    print("\nTesting /ai/chat - Telugu")

    telugu_chat = measure_request(
        endpoint="/ai/chat",
        payload={
            "userId": "PERF_TE_USER",
            "sessionId": "PERF_TE",
            "message": "మ్యూచువల్ ఫండ్ అంటే ఏమిటి?"
        },
        runs=5
    )

    print_result(
        "Telugu /ai/chat",
        telugu_chat
    )

    # =================================================
    # VALIDATE HTTP RESPONSES
    # =================================================

    assert all(
        200 <= status < 300
        for status in english_chat["statuses"]
    )

    assert all(
        200 <= status < 300
        for status in telugu_chat["statuses"]
    )

    # =================================================
    # PERFORMANCE COMPARISON
    # =================================================

    difference = (
        telugu_chat["average"]
        - english_chat["average"]
    )

    print("\n")
    print("=" * 60)
    print("PERFORMANCE COMPARISON")
    print("=" * 60)

    print(
        f"\nEnglish /ai/chat average: "
        f"{english_chat['average']:.3f}s"
    )

    print(
        f"Telugu /ai/chat average: "
        f"{telugu_chat['average']:.3f}s"
    )

    print(
        f"Telugu - English difference: "
        f"{difference:.3f}s"
    )

    print("\n")
    print("=" * 60)
    print("TEST COMPLETED")
    print("=" * 60)
