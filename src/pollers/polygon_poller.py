# """
# Poller for fetching stock quotes from Polygon.io API.

# The poller fetches the previous close data for the given symbols from Polygon.io API and
# sends it to the message queue.

# The poller enforces a rate limit of 5 requests per minute, per symbol.
# """

# from typing import Any

# from src.config import get_polygon_api_key, get_rate_limit, get_polygon_fill_rate_limit
# from src.pollers.base_poller import BasePoller
# from src.utils.rate_limit import RateLimiter
# from src.utils.request_with_timeout import request_with_timeout
# from src.utils.retry_request import retry_request
# from src.utils.setup_logger import setup_logger
# from src.utils.track_polling_metrics import track_polling_metrics
# from src.utils.track_request_metrics import track_request_metrics
# from src.utils.validate_data import validate_data

# # Logger setup
# logger = setup_logger(__name__)


# class PolygonPoller(BasePoller):
#     """Poller for fetching stock quotes from Polygon.io API."""

#     def __init__(self):
#         """
#         Initializes the PolygonPoller.

#         Raises
#         ------
#             ValueError: If POLYGON_API_KEY is not set.
#         """
#         super().__init__()

#         self.api_key = get_polygon_api_key()
#         if not self.api_key:
#             raise ValueError("Missing POLYGON_API_KEY.")
#         self.rate_limiter = RateLimiter(max_requests=get_polygon_fill_rate_limit(), time_window=60)
#         self.rate_limiter = RateLimiter(max_requests=get_rate_limit(), time_window=60)

#     def poll(self, symbols: list[str]) -> None:
#         """Polls data for the specified symbols from Polygon.io API."""
#         for symbol in symbols:
#             try:
#                 self._enforce_rate_limit()
#                 data = self._fetch_data(symbol)

#                 if not data or "results" not in data:
#                     self._handle_failure(symbol, "Missing results in API response.")
#                     continue

#                 payload = self._process_data(symbol, data)

#                 if not validate_data(payload):
#                     self._handle_failure(symbol, "Validation failed.")
#                     continue

#                 track_polling_metrics("Polygon", [symbol])
#                 track_request_metrics(symbol, 30, 5)

#                 self.send_to_queue(payload)
#                 self._handle_success(symbol)

#             except Exception as e:
#                 self._handle_failure(symbol, str(e))

#     def _enforce_rate_limit(self) -> None:
#         """Enforces the rate limit using the RateLimiter class."""
#         self.rate_limiter.acquire(context="Polygon")

#     def _fetch_data(self, symbol: str) -> dict[str, Any]:
#         """Fetches stock data for the given symbol from Polygon.io API."""

#         def request_func():
#             """Makes a GET request to the Polygon.io API to fetch the previous close
#             data for the given symbol."""
#             url = (
#                 f"https://api.polygon.io/v2/aggs/ticker/{symbol}/prev?"
#                 f"adjusted=true&apiKey={self.api_key}"
#             )
#             return request_with_timeout("GET", url)

#         return retry_request(request_func)

#     def _process_data(self, symbol: str, data: dict[str, Any]) -> dict[str, Any]:
#         """Processes the raw data into the payload format."""
#         results = data["results"][0]  # Only one result for "previous close"

#         return {
#             "symbol": symbol,
#             "timestamp": results.get("t"),
#             "price": float(results.get("c", 0.0)),
#             "source": "Polygon",
#             "data": {
#                 "open": float(results.get("o", 0.0)),
#                 "high": float(results.get("h", 0.0)),
#                 "low": float(results.get("l", 0.0)),
#                 "close": float(results.get("c", 0.0)),
#                 "volume": int(results.get("v", 0)),
#             },
#         }

#     def _handle_success(self, symbol: str) -> None:
#         """Tracks success metrics for polling and requests."""
#         track_polling_metrics("Polygon", [symbol])
#         track_request_metrics(symbol, 30, 5)

#     def _handle_failure(self, symbol: str, error: str) -> None:
#         """Tracks failure metrics for polling and requests."""
#         track_polling_metrics("Polygon", [symbol])
#         track_request_metrics(symbol, 30, 5, success=False)
#         logger.error(f"Polygon polling error for {symbol}: {error}")
"""Poller for fetching stock quotes from Polygon.io API.

The poller fetches the previous close data for the given symbols from Polygon.io API and
sends it to the message queue.

The poller enforces a rate limit of 5 requests per minute, per symbol.
"""

from typing import Any

from src.config import get_polygon_api_key, get_polygon_fill_rate_limit
from src.pollers.base_poller import BasePoller
from src.utils.rate_limit import RateLimiter
from src.utils.request_with_timeout import request_with_timeout
from src.utils.retry_request import retry_request
from src.utils.setup_logger import setup_logger
from src.utils.track_polling_metrics import track_polling_metrics
from src.utils.track_request_metrics import track_request_metrics
from src.utils.validate_data import validate_data

# Logger setup
logger = setup_logger(__name__)


class PolygonPoller(BasePoller):
    """Poller for fetching stock quotes from Polygon.io API."""

    def __init__(self):
        """Initializes the PolygonPoller.

        Raises
        ------
            ValueError: If POLYGON_API_KEY is not set.

        """
        super().__init__()

        self.api_key = get_polygon_api_key()
        if not self.api_key:
            raise ValueError("Missing POLYGON_API_KEY.")

        self.rate_limiter = RateLimiter(
            max_requests=get_polygon_fill_rate_limit(),
            time_window=60,
        )

    def poll(self, symbols: list[str]) -> None:
        """Polls data for the specified symbols from Polygon.io API."""
        for symbol in symbols:
            try:
                self._enforce_rate_limit()
                data = self._fetch_data(symbol)

                if not data or "results" not in data:
                    self._handle_failure(symbol, "Missing results in API response.")
                    continue

                payload = self._process_data(symbol, data)

                if not validate_data(payload):
                    self._handle_failure(symbol, "Validation failed.")
                    continue

                track_polling_metrics("Polygon", [symbol])
                track_request_metrics(symbol, 30, 5)

                self.send_to_queue(payload)
                self._handle_success(symbol)

            except Exception as e:
                self._handle_failure(symbol, str(e))

    def _enforce_rate_limit(self) -> None:
        """Enforces the rate limit using the RateLimiter class."""
        self.rate_limiter.acquire(context="Polygon")

    def _fetch_data(self, symbol: str) -> dict[str, Any]:
        """Fetches stock data for the given symbol from Polygon.io API."""

        def request_func():
            url = (
                f"https://api.polygon.io/v2/aggs/ticker/{symbol}/prev?"
                f"adjusted=true&apiKey={self.api_key}"
            )
            return request_with_timeout("GET", url)

        return retry_request(request_func)

    def _process_data(self, symbol: str, data: dict[str, Any]) -> dict[str, Any]:
        """Processes the raw data into the payload format."""
        results = data["results"][0]  # Only one result for "previous close"

        return {
            "symbol": symbol,
            "timestamp": results.get("t"),
            "price": float(results.get("c", 0.0)),
            "source": "Polygon",
            "data": {
                "open": float(results.get("o", 0.0)),
                "high": float(results.get("h", 0.0)),
                "low": float(results.get("l", 0.0)),
                "close": float(results.get("c", 0.0)),
                "volume": int(results.get("v", 0)),
            },
        }

    def _handle_success(self, symbol: str) -> None:
        """Tracks success metrics for polling and requests."""
        track_polling_metrics("Polygon", [symbol])
        track_request_metrics(symbol, 30, 5)

    def _handle_failure(self, symbol: str, error: str) -> None:
        """Tracks failure metrics for polling and requests."""
        track_polling_metrics("Polygon", [symbol])
        track_request_metrics(symbol, 30, 5, success=False)
        logger.error(f"Polygon polling error for {symbol}: {error}")
