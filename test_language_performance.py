import statistics
import time

import pytest
import requests


BASE_URL = "http://127.0.0.1:8000"


def measure_request(
    method,
    endpoint,
    payload,
    runs=5
):
    times = []
    statuses = []

    for i in range(runs):

        start = time.perf_counter()

        response = requests.request(
            method,
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

    # -------------------------------------------------
    # Skip when FastAPI server is not running
    # -------------------------------------------------

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
    # TEST 1: ENGLISH / ASK
    # =================================================

    print("\nTesting /ask - English")

    english_ask = measure_request(
        method="POST",
        endpoint="/ask",
        payload={
            "question": "What is a mutual fund?",
            "language": "en"
        },
        runs=5
    )

    print_result(
        "English /ask",
        english_ask
    )

    # =================================================
    # TEST 2: TELUGU / ASK
    # =================================================

    print("\nTesting /ask - Telugu")

    telugu_ask = measure_request(
        method="POST",
        endpoint="/ask",
        payload={
            "question": "What is a mutual fund?",
            "language": "te"
        },
        runs=5
    )

    print_result(
        "Telugu /ask",
        telugu_ask
    )

    # =================================================
    # TEST 3: ENGLISH CONVERSATION
    # =================================================

    print("\nTesting /ai/conversation - English")

    english_conversation = measure_request(
        method="POST",
        endpoint="/ai/conversation",
        payload={
            "conversation_id": "PERF_EN",
            "message": "What is a mutual fund?",
            "language": "en"
        },
        runs=5
    )

    print_result(
        "English Conversation",
        english_conversation
    )

    # =================================================
    # TEST 4: TELUGU CONVERSATION
    # =================================================

    print("\nTesting /ai/conversation - Telugu")

    telugu_conversation = measure_request(
        method="POST",
        endpoint="/ai/conversation",
        payload={
            "conversation_id": "PERF_TE",
            "message": "What is a mutual fund?",
            "language": "te"
        },
        runs=5
    )

    print_result(
        "Telugu Conversation",
        telugu_conversation
    )

    # =================================================
    # VALIDATE HTTP RESPONSES
    # =================================================

    assert all(
        status < 500
        for status in english_ask["statuses"]
    )

    assert all(
        status < 500
        for status in telugu_ask["statuses"]
    )

    assert all(
        status < 500
        for status in english_conversation["statuses"]
    )

    assert all(
        status < 500
        for status in telugu_conversation["statuses"]
    )

    # =================================================
    # COMPARISON
    # =================================================

    ask_difference = (
        telugu_ask["average"]
        - english_ask["average"]
    )

    conversation_difference = (
        telugu_conversation["average"]
        - english_conversation["average"]
    )

    print("\n")
    print("=" * 60)
    print("PERFORMANCE COMPARISON")
    print("=" * 60)

    print(
        f"\nEnglish /ask average: "
        f"{english_ask['average']:.3f}s"
    )

    print(
        f"Telugu /ask average: "
        f"{telugu_ask['average']:.3f}s"
    )

    print(
        f"/ask difference: "
        f"{ask_difference:.3f}s"
    )

    print(
        f"\nEnglish conversation average: "
        f"{english_conversation['average']:.3f}s"
    )

    print(
        f"Telugu conversation average: "
        f"{telugu_conversation['average']:.3f}s"
    )

    print(
        f"Conversation difference: "
        f"{conversation_difference:.3f}s"
    )

    print("\n")
    print("=" * 60)
    print("TEST COMPLETED")
    print("=" * 60)