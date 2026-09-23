import time

from circuit_breaker import CircuitBreaker


def main():
    print("=" * 60)
    print("PaiseWise Circuit Breaker Test")
    print("=" * 60)

    breaker = CircuitBreaker(
        error_threshold=0.10,
        window_size=20,
        recovery_timeout=2
    )

    print("\n1. Initial state")
    print(breaker.get_status())

    # First 8 successful calls
    for _ in range(8):
        breaker.allow_request()
        breaker.record_success()

    print("\n2. After 8 successful calls")
    print(breaker.get_status())

    # Two failures
    breaker.allow_request()
    breaker.record_failure()

    breaker.allow_request()
    breaker.record_failure()

    print("\n3. After 2 failures")
    print(breaker.get_status())

    # Circuit should now be OPEN
    print("\n4. Can request while OPEN?")
    print("Allowed:", breaker.allow_request())

    # Wait for recovery
    print("\n5. Waiting 2 seconds for recovery...")
    time.sleep(2.5)

    print("\n6. State after recovery timeout")
    print(breaker.get_status())

    # HALF_OPEN should allow one request
    print("\n7. HALF_OPEN trial request")
    print("Allowed:", breaker.allow_request())

    # Successful trial
    breaker.record_success()

    print("\n8. After successful trial")
    print(breaker.get_status())

    print("\n" + "=" * 60)
    print("Circuit breaker test completed")
    print("=" * 60)


if __name__ == "__main__":
    main()