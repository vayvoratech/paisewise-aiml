import time
from collections import deque


class CircuitBreakerOpen(Exception):
    """Raised when the circuit breaker is open."""
    pass


class CircuitBreaker:
    """
    Circuit breaker for LLM API calls.

    Behavior:
    - Tracks recent LLM calls and failures.
    - Opens when error rate is > 10%.
    - When open, LLM calls are blocked for 5 minutes.
    - After 5 minutes, allows one trial request.
    - Successful trial closes the circuit.
    - Failed trial opens the circuit again.
    """

    def __init__(
        self,
        error_threshold=0.10,
        window_size=20,
        recovery_timeout=300
    ):
        self.error_threshold = error_threshold
        self.window_size = window_size
        self.recovery_timeout = recovery_timeout

        # Stores True for failure, False for success
        self.results = deque(maxlen=window_size)

        self.state = "CLOSED"
        self.opened_at = None

        self.half_open_trial = False

    def _error_rate(self):
        """Calculate current error rate."""
        if not self.results:
            return 0.0

        failures = sum(1 for result in self.results if result)

        return failures / len(self.results)

    def _check_recovery(self):
        """
        If circuit has been open for 5 minutes,
        move it to HALF_OPEN.
        """

        if self.state != "OPEN":
            return

        if self.opened_at is None:
            return

        elapsed = time.time() - self.opened_at

        if elapsed >= self.recovery_timeout:
            self.state = "HALF_OPEN"
            self.half_open_trial = False

    def allow_request(self):
        """
        Decide whether an LLM request can be made.
        """

        self._check_recovery()

        if self.state == "CLOSED":
            return True

        if self.state == "OPEN":
            return False

        if self.state == "HALF_OPEN":
            # Only allow one trial request
            if not self.half_open_trial:
                self.half_open_trial = True
                return True

            return False

        return False

    def record_success(self):
        """Record a successful LLM call."""

        self.results.append(False)

        if self.state == "HALF_OPEN":
            self.state = "CLOSED"
            self.opened_at = None
            self.half_open_trial = False

            # Start fresh after successful recovery
            self.results.clear()

    def record_failure(self):
        """Record a failed LLM call."""

        self.results.append(True)

        if self.state == "HALF_OPEN":
            self.state = "OPEN"
            self.opened_at = time.time()
            self.half_open_trial = False
            return

        # Wait until enough calls exist before calculating
        # the error rate.
        if len(self.results) < 10:
            return

        error_rate = self._error_rate()

        if error_rate > self.error_threshold:
            self.state = "OPEN"
            self.opened_at = time.time()
            self.half_open_trial = False

    def get_status(self):
        """Return current circuit breaker status."""

        self._check_recovery()

        return {
            "state": self.state,
            "error_rate": round(self._error_rate(), 4),
            "total_calls": len(self.results),
            "failed_calls": sum(1 for result in self.results if result),
            "recovery_timeout_seconds": self.recovery_timeout
        }