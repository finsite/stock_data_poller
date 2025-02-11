import time
import threading
from app.utils.setup_logger import setup_logger

logger = setup_logger(__name__)


class RateLimiter:
    """
    A rate limiter based on the token bucket algorithm.
    Allows a specified number of requests within a time window.
    """

    def __init__(self, max_requests: int, time_window: float):
        """
        Initialize the RateLimiter.

        Args:
            max_requests (int): Maximum number of requests allowed.
            time_window (float): Time window in seconds.
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.tokens = max_requests
        self.lock = threading.Lock()
        self.last_check = time.time()

    def acquire(self, context="RateLimiter"):
        """
        Acquire permission to proceed with a request.
        Blocks if the rate limit is exceeded.

        Args:
            context (str): Optional context for logging (e.g., poller type).
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
