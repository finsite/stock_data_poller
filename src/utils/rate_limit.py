"""The module implements a rate limiter for API requests.

The `RateLimiter` class uses the token bucket algorithm to manage the request rate.
It is thread-safe and can be used to limit the request rate for a single API or
multiple APIs.

"""

import threading
import time

from src.utils.setup_logger import setup_logger

# Set up logger for this module
logger = setup_logger(__name__)

# Constants for the rate limiter
# The `RateLimiter` class uses these constants to manage request rates


class RateLimiter:
    """A rate limiter based on the token bucket algorithm.

    Allows a specified number of requests within a time window.
    """

    def __init__(self, max_requests: int, time_window: float) -> None:
        """Initialize the RateLimiter.

        The constructor takes in the maximum number of requests allowed within a
        specified time window and initializes the internal state of the rate
        limiter.

        Args:
        ----
            max_requests (int): Maximum number of requests allowed.
            time_window (float): Time window in seconds.

        """
        self._max_requests = max_requests
        self._time_window = time_window
        self._tokens = max_requests
        self._lock = threading.Lock()
        self._last_check = time.time()

    def acquire(self, context: str = "RateLimiter") -> None:
        """Acquire permission to proceed with a request. Blocks if the rate
        limit is exceeded.

        The function uses the token bucket algorithm to manage the request rate.
        It replenishes tokens based on the elapsed time since the last check and
        blocks if the rate limit is exceeded.

        Args:
        ----
            context (str, optional): Optional context for logging (e.g., poller type).
                Defaults to "RateLimiter".

        Returns:
        -------
            None

        """
        with self.lock:
            current_time = time.time()
            elapsed = current_time - self.last_check

            # Add tokens based on elapsed time
            tokens_to_add = elapsed * (self.max_requests / self.time_window)
            self.tokens = min(self.max_requests, self.tokens + tokens_to_add)
            self.last_check = current_time

            # Log token replenishment
            logger.debug(
                f"[{context}] Replenished {tokens_to_add:.2f} tokens. "
                f"Available tokens: {self.tokens:.2f}"
            )

            # Wait if no tokens are available
            if self.tokens < 1:
                sleep_time = (1 - self.tokens) * (self.time_window / self.max_requests)
                logger.info(
                    f"[{context}] Rate limit reached. Sleeping for {sleep_time:.2f} seconds."
                )
                time.sleep(sleep_time)
                self.tokens = 1  # Add one token after sleeping

            # Consume a token and log
            self.tokens -= 1
            logger.debug(f"[{context}] Consumed a token. Remaining tokens: {self.tokens:.2f}")
