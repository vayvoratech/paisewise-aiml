from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import statistics
import time
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlparse
from urllib.request import Request, urlopen
from uuid import uuid4


def post_json(url: str, payload: dict, timeout: float) -> tuple[int, dict]:
    body = json.dumps(payload).encode("utf-8")
    request = Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urlopen(request, timeout=timeout) as response:
            response_body = response.read()
            data = json.loads(response_body) if response_body else {}
            return response.status, data
    except HTTPError as exc:
        response_body = exc.read()
        try:
            data = json.loads(response_body) if response_body else {}
        except json.JSONDecodeError:
            data = {"error": response_body.decode("utf-8", errors="replace")}
        return exc.code, data


def post_stream(
    url: str,
    payload: dict,
    timeout: float,
) -> dict:
    body = json.dumps(payload).encode("utf-8")
    request = Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    start = time.perf_counter()

    try:
        with urlopen(request, timeout=timeout) as response:
            first_byte = response.read(1)
            first_byte_ms = (time.perf_counter() - start) * 1000
            remaining = response.read()

            return {
                "status": response.status,
                "first_byte_ms": first_byte_ms if first_byte else None,
                "total_ms": (time.perf_counter() - start) * 1000,
                "response_bytes": len(first_byte) + len(remaining),
                "error": None,
            }
    except HTTPError as exc:
        return {
            "status": exc.code,
            "first_byte_ms": None,
            "total_ms": (time.perf_counter() - start) * 1000,
            "response_bytes": 0,
            "error": exc.read().decode("utf-8", errors="replace"),
        }
    except (TimeoutError, URLError, OSError) as exc:
        return {
            "status": None,
            "first_byte_ms": None,
            "total_ms": (time.perf_counter() - start) * 1000,
            "response_bytes": 0,
            "error": str(exc),
        }


def send_chat(
    base_url: str,
    user_id: str,
    message: str,
    timeout: float,
    index: int,
) -> dict:
    payload = {
        "userId": user_id,
        "sessionId": f"task13-load-{index}-{uuid4()}",
        "message": message,
    }

    start = time.perf_counter()

    try:
        status_code, data = post_json(
            f"{base_url}/ai/chat",
            payload,
            timeout,
        )
        return {
            "status": status_code,
            "total_ms": (time.perf_counter() - start) * 1000,
            "error": data.get("detail") or data.get("error"),
        }
    except Exception as exc:
        return {
            "status": None,
            "total_ms": (time.perf_counter() - start) * 1000,
            "error": str(exc),
        }


def poll_job(
    base_url: str,
    user_id: str,
    message: str,
    timeout: float,
    poll_timeout: float,
) -> dict:
    payload = {
        "userId": user_id,
        "sessionId": f"task13-job-{uuid4()}",
        "message": message,
    }

    status_code, accepted = post_json(
        f"{base_url}/ai/chat/jobs",
        payload,
        timeout,
    )

    job_id = accepted.get("job_id")
    if status_code != 202 or not job_id:
        return {
            "status": "submit_failed",
            "http_status": status_code,
            "details": accepted,
        }

    deadline = time.monotonic() + poll_timeout
    job_url = f"{base_url}/ai/chat/jobs/{quote(job_id)}"

    while time.monotonic() < deadline:
        try:
            with urlopen(job_url, timeout=timeout) as response:
                data = json.loads(response.read())

            if data.get("status") in {"completed", "failed"}:
                return {
                    "status": data.get("status"),
                    "job_id": job_id,
                    "result": data.get("result"),
                    "error": data.get("error"),
                }

        except (HTTPError, TimeoutError, URLError, OSError) as exc:
            return {
                "status": "poll_failed",
                "job_id": job_id,
                "error": str(exc),
            }

        time.sleep(0.5)

    return {
        "status": "poll_timeout",
        "job_id": job_id,
    }


def percentile(values: list[float], percentage: float) -> float | None:
    if not values:
        return None

    ordered = sorted(values)
    index = round((percentage / 100) * (len(ordered) - 1))
    return ordered[index]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Measure Task 13 chat performance."
    )
    parser.add_argument(
        "--url",
        default="http://127.0.0.1:8000",
        help="Load balancer base URL.",
    )
    parser.add_argument("--requests", type=int, default=20)
    parser.add_argument("--concurrency", type=int, default=2)
    parser.add_argument("--timeout", type=float, default=180)
    parser.add_argument("--job-timeout", type=float, default=240)
    parser.add_argument(
        "--include-job",
        action="store_true",
        help="Submit one queued job and poll until it finishes.",
    )
    args = parser.parse_args()

    parsed_url = urlparse(args.url)
    if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
        parser.error("--url must be a valid HTTP or HTTPS URL")

    base_url = args.url.rstrip("/")
    user_id = os.getenv("CHAT_TEST_USER_ID", "task13-load-test-user")
    message = os.getenv("CHAT_TEST_MESSAGE")

    if not message:
        parser.error(
            "Set CHAT_TEST_MESSAGE to a suitable test question before running."
        )

    if args.requests < 1 or args.concurrency < 1:
        parser.error("--requests and --concurrency must be at least 1")

    # Measure streaming separately so the first-byte latency is visible.
    stream_payload = {
        "userId": user_id,
        "sessionId": f"task13-stream-{uuid4()}",
        "message": message,
    }
    stream_result = post_stream(
        f"{base_url}/ai/chat/stream",
        stream_payload,
        args.timeout,
    )

    # Send ordinary chat requests concurrently.
    with concurrent.futures.ThreadPoolExecutor(
        max_workers=args.concurrency
    ) as executor:
        futures = [
            executor.submit(
                send_chat,
                base_url,
                user_id,
                message,
                args.timeout,
                index,
            )
            for index in range(args.requests)
        ]
        chat_results = [future.result() for future in futures]

    chat_times = [
        result["total_ms"]
        for result in chat_results
        if result["status"] == 200
    ]
    successful_chats = sum(
        result["status"] == 200
        for result in chat_results
    )

    report = {
        "base_url": base_url,
        "chat_requests": args.requests,
        "concurrency": args.concurrency,
        "successful_chat_requests": successful_chats,
        "chat_p95_ms": percentile(chat_times, 95),
        "stream": stream_result,
        "stream_under_1_second": (
            stream_result["first_byte_ms"] is not None
            and stream_result["first_byte_ms"] < 1000
        ),
    }

    if args.include_job:
        report["queued_job"] = poll_job(
            base_url,
            user_id,
            message,
            args.timeout,
            args.job_timeout,
        )

    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())