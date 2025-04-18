"""
The module provides a poller class for fetching stock data using the Finnhub API.

The module uses the following libraries:
- src.config: To get the rate limit for the poller and the Finnhub API key.
- src.pollers.base_poller: To inherit the base poller functionality.
- src.utils.rate_limit: To enforce the rate limit using the RateLimiter class.
- src.utils.request_with_timeout: To make HTTP requests with a timeout.
- src.utils.retry_request: To retry operations with exponential backoff.
- src.utils.setup_logger: To set up the logger for the module.
- src.utils.track_polling_metrics: To track metrics for polling operations.
- src.utils.track_request_metrics: To track metrics for individual API requests.
- src.utils.validate_data: To validate the fetched data against the required schema.
"""

import time
from typing import Any

from src.config import get_finnhub_api_key, get_finnhub_fill_rate_limit
from src.pollers.base_poller import BasePoller
from src.utils.rate_limit import RateLimiter
from src.utils.request_with_timeout import request_with_timeout
from src.utils.retry_request import retry_request
from src.utils.setup_logger import setup_logger
from src.utils.track_polling_metrics import track_polling_metrics
from src.utils.track_request_metrics import track_request_metrics
from src.utils.validate_data import validate_data

# Initialize logger
logger = setup_logger(__name__)


class FinnhubPoller(BasePoller):
    """
    Poller for fetching stock quotes from Finnhub API.

    Attributes
    ----------
    api_key : str
        The API key to access the Finnhub API.
    rate_limiter : RateLimiter
        The rate limiter to manage the request rate.
    """

    def __init__(self) -> None:
        """Initializes the FinnhubPoller with necessary configurations.

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
            None

        Returns:
            None
        """
        self.rate_limiter.acquire(context="Finnhub")

    def _fetch_data(self, symbol: str) -> dict[str, Any]:
        """
        Fetches stock data for the given symbol from Finnhub using the quote endpoint.

        The function makes a GET request to the Finnhub API with the symbol and API key.
        The response is expected to be a JSON object containing the current price,
        high, low, open, and previous close prices for the given symbol.

        Args:
        ----
            symbol (str): The symbol to fetch data for.

        Returns:
        -------
            dict[str, Any]: The fetched data.
        """

        def request_func() -> dict[str, Any]:
            """
            Makes a GET request to the Finnhub API to fetch the quote data.

            The request is made with the symbol and API key as query parameters.
            The response is expected to be a JSON object containing the quote data.

            Returns:
            -------
                dict[str, Any]: The fetched data.
            """
            url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={self.api_key}"
            return request_with_timeout("GET", url)

        return retry_request(request_func)

    def _process_data(self, symbol: str, data: dict[str, Any]) -> dict[str, Any]:
        """
        Processes the raw data into the payload format.

        Args:
            symbol (str): The symbol to process data for.
            data (dict[str, Any]): The raw data to process.

        Returns:
            dict[str, Any]: The processed payload.
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
            symbol (str): The stock symbol that was successfully polled.

        Metrics tracked include the source of the data (Finnhub) and the symbol
        for which polling was performed.

        Returns:
            None
        """
        # Track polling metrics indicating a successful polling operation
        track_polling_metrics("success", "Finnhub", symbol)

        # Track request metrics with fixed response time and success status
        track_request_metrics(symbol, 30, 5)

    def _handle_failure(self, symbol: str, error: str) -> None:
        """
        Tracks failure metrics for polling and logs the error.

        Args:
            symbol (str): The stock symbol for which polling failed.
            error (str): The error message describing the failure.

        Returns:
            None
        """
        # Log the error message for debugging purposes
        logger.error(f"Finnhub polling error for {symbol}: {error}")

        # Track polling metrics indicating a failed polling operation
        track_polling_metrics("failure", "Finnhub", symbol)

        # Track request metrics with fixed response time and failed status
        track_request_metrics(symbol, 30, 5, success=False)
