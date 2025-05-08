"""
The module provides a poller class for fetching stock data using the Finnhub API.

The module uses the following libraries:
- app.config: To get the rate limit for the poller and the Finnhub API key.
- app.pollers.base_poller: To inherit the base poller functionality.
- app.utils.rate_limit: To enforce the rate limit using the RateLimiter class.
- app.utils.request_with_timeout: To make HTTP requests with a timeout.
- app.utils.retry_request: To retry operations with exponential backoff.
- app.utils.setup_logger: To set up the logger for the module.
- app.utils.track_polling_metrics: To track metrics for polling operations.
- app.utils.track_request_metrics: To track metrics for individual API requests.
- app.utils.validate_data: To validate the fetched data against the required schema.
"""

import time
from typing import Any

from app.config import get_finnhub_api_key, get_finnhub_fill_rate_limit
from app.pollers.base_poller import BasePoller
from app.utils.rate_limit import RateLimiter
from app.utils.request_with_timeout import request_with_timeout
from app.utils.retry_request import retry_request
from app.utils.setup_logger import setup_logger
from app.utils.track_polling_metrics import track_polling_metrics
from app.utils.track_request_metrics import track_request_metrics
from app.utils.validate_data import validate_data

# Initialize logger
logger = setup_logger(__name__)


class FinnhubPoller(BasePoller):
    """Poller for fetching stock quotes from Finnhub API."""

    def __init__(self) -> None:
        """
        Initializes the FinnhubPoller with necessary configurations.

        Raises
        ------
        ValueError
            If the FINNHUB_API_KEY environment variable is not set.
        """
        super().__init__()

        # Retrieve and validate the Finnhub API key
        self.api_key: str = get_finnhub_api_key()
        if not self.api_key:
            raise ValueError(
                "Missing FINNHUB_API_KEY environment variable. "
                "FinnhubPoller cannot be used without an API key."
            )

        # Initialize the rate limiter with the configured fill rate limit
        self.rate_limiter: RateLimiter = RateLimiter(
            max_requests=get_finnhub_fill_rate_limit(), time_window=60
        )

    def poll(self, symbols: list[str]) -> None:
        """
        Polls data for the specified symbols from Finnhub.

        Args:
        ----
            symbols (list[str]): The list of symbols to poll.

        Returns:
        -------
            None: This function does not return a value.

        Args:
          symbols: list[str]:

        Returns:

        Args:
          symbols: list[str]:

        Returns:

        Args:
          symbols: list[str]:

        Returns:

        Args:
          symbols: list[str]:

        Returns:
        """
        for symbol in symbols:
            try:
                self._enforce_rate_limit()
                data: dict[str, Any] = self._fetch_data(symbol)

                if not data or "c" not in data:
                    self._handle_failure(symbol, "No data or missing current price.")
                    continue

                payload: dict[str, Any] = self._process_data(symbol, data)

                if not validate_data(payload):
                    self._handle_failure(symbol, "Validation failed.")
                    continue

                self.send_to_queue(payload)
                self._handle_success(symbol)

            except Exception as e:
                self._handle_failure(symbol, str(e))

    def _enforce_rate_limit(self) -> None:
        """
        Enforces the rate limit using the RateLimiter class.

        This function acquires permission to proceed with a request. If the rate limit
        is exceeded, the function will block until the limit is replenished.

        Args:
        ----
            None

        Returns:
        -------
            None

        Args:

        Returns:

        Args:

        Returns:

        Args:

        Returns:

        Args:

        Returns:
        """
        self.rate_limiter.acquire(context="Finnhub")

    def _fetch_data(self, symbol: str) -> dict[str, Any]:
        """
        Fetches stock data for the given symbol from Finnhub using the quote endpoint.

        Args:
          symbol: str:
          symbol: str:
          symbol: str:
          symbol: str:

        Returns:
          The fetched data.:
        """

        def request_func():
            """"""
            url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={self.api_key}"
            return request_with_timeout(url, timeout=30)

        data = retry_request(request_func)
        if data is None:
            raise ValueError(f"Finnhub API returned no data for symbol: {symbol}")
        return data

    def _process_data(self, symbol: str, data: dict[str, Any]) -> dict[str, Any]:
        """
        Processes the raw data into the payload format.

        Args:
        ----
            symbol (str): The symbol to process data for.
            data (dict[str, Any]): The raw data to process.

        Returns:
        -------
            dict[str, Any]: The processed payload.

        Args:
          symbol: str:
          data: dict[str:
          Any]:

        Returns:

        Args:
          symbol: str:
          data: dict[str:
          Any]:

        Returns:

        Args:
          symbol: str:
          data: dict[str:
          Any]:

        Returns:

        Args:
          symbol: str:
          data: dict[str:
          Any]:

        Returns:
        """
        return {
            "symbol": symbol,  # str
            "timestamp": int(time.time()),  # Time of polling (not actual market update time)
            "price": float(data["c"]),  # float
            "source": "Finnhub",  # str
            "data": {  # dict[str, float]
                "current": float(data["c"]),  # float
                "high": float(data["h"]),  # float
                "low": float(data["l"]),  # float
                "open": float(data["o"]),  # float
                "previous_close": float(data["pc"]),  # float
            },
        }

    def _handle_success(self, symbol: str) -> None:
        """
        Tracks success metrics for polling and requests.

        Args:
        ----
            symbol (str): The stock symbol that was successfully polled.

        Metrics tracked include the source of the data (Finnhub) and the symbol
        for which polling was performed.

        Returns:
        -------
            None

        Args:
          symbol: str:

        Returns:

        Args:
          symbol: str:

        Returns:

        Args:
          symbol: str:

        Returns:

        Args:
          symbol: str:

        Returns:
        """
        # Track polling metrics indicating a successful polling operation
        track_polling_metrics("success", "Finnhub", symbol)

        # Track request metrics with fixed response time and success status
        track_request_metrics(symbol, 30, 5)

    def _handle_failure(self, symbol: str, error: str) -> None:
        """
        Tracks failure metrics for polling and logs the error.

        Args:
        ----
            symbol (str): The stock symbol for which polling failed.
            error (str): The error message describing the failure.

        Returns:
        -------
            None

        Args:
          symbol: str:
          error: str:

        Returns:

        Args:
          symbol: str:
          error: str:

        Returns:

        Args:
          symbol: str:
          error: str:

        Returns:

        Args:
          symbol: str:
          error: str:

        Returns:
        """
        # Log the error message for debugging purposes
        logger.error(f"Finnhub polling error for {symbol}: {error}")

        # Track polling metrics indicating a failed polling operation
        track_polling_metrics("failure", "Finnhub", symbol)

        # Track request metrics with fixed response time and failed status
        track_request_metrics(symbol, 30, 5, success=False)
