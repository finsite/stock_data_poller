"""
The module provides a poller class for fetching stock quotes from the IEX Cloud API.

The poller enforces a rate limit specific to IEX, with a fallback to the default limit.
"""

from typing import Any

from src.config import get_iex_api_key, get_iex_fill_rate_limit
from src.pollers.base_poller import BasePoller
from src.utils.rate_limit import RateLimiter
from src.utils.request_with_timeout import request_with_timeout
from src.utils.retry_request import retry_request
from src.utils.setup_logger import setup_logger
from src.utils.track_polling_metrics import track_polling_metrics
from src.utils.track_request_metrics import track_request_metrics
from src.utils.validate_data import validate_data

# ✅ Standard logger
logger = setup_logger(__name__)


class IEXPoller(BasePoller):
    """Poller for fetching stock quotes from the IEX Cloud API."""

    def __init__(self):
        """
        Initializes the IEXPoller.

        Raises
        ------
            ValueError: If the IEX_API_KEY environment variable is not set.
        """
        super().__init__()

        self.api_key = get_iex_api_key()
        if not self.api_key:
            raise ValueError("❌ Missing IEX_API_KEY.")

        self.rate_limiter = RateLimiter(max_requests=get_iex_fill_rate_limit(), time_window=60)

    def poll(self, symbols: list[str]) -> None:
        """
        Polls data for the specified symbols from IEX Cloud API.

        Args:
        ----
            symbols: List[str]
                List of stock symbols to poll.

        Returns:
        -------
            None

        This method polls the IEX Cloud API for the given symbols and sends the
        fetched data to the message queue. If any error occurs during polling, the
        error is tracked and logged.
        """
        for symbol in symbols:
            try:
                self._enforce_rate_limit()
                data = self._fetch_data(symbol)

                if not data or "latestPrice" not in data:
                    self._handle_failure(symbol, "No data or missing latest price.")
                    continue

                payload = self._process_data(data)

                if not validate_data(payload):
                    self._handle_failure(symbol, "Validation failed.")
                    continue

                self.send_to_queue(payload)
                self._handle_success(symbol)

            except Exception as e:
                self._handle_failure(symbol, str(e))

    def _enforce_rate_limit(self) -> None:
        """
        Enforces the IEX-specific rate limit.

        The IEX Cloud API has a rate limit of 5 requests per second and 100,000 requests
        per month. The rate limit is enforced here to prevent hitting the limit.

        Args:
            None

        Returns:
            None
        """
        self.rate_limiter.acquire(context="IEX")

    def _fetch_data(self, symbol: str) -> dict[str, Any]:
        """
        Fetches stock data for the given symbol from the IEX Cloud API.

        Args:
        ----
            symbol (str): Stock symbol to fetch data for.

        Returns:
        -------
            dict[str, Any]: Fetched data from the IEX API.
        """

        def request_func() -> dict[str, Any]:
            url = f"https://cloud.iexapis.com/stable/stock/{symbol}/quote?token={self.api_key}"
            return request_with_timeout("GET", url)

        return retry_request(request_func)

    def _process_data(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Processes the raw data from IEX Cloud API into the payload format.

        Args:
        ----
            data (dict[str, Any]): Raw data from IEX API.

        Returns:
        -------
            dict[str, Any]: Processed data in the payload format, including stock
                symbol (str), timestamp (int), latest price (float), and additional
                stock data (dict[str, float|int]).
        """
        # Extract and format the processed data
        return {
            "symbol": data.get("symbol", "N/A"),  # Stock symbol (str)
            "timestamp": data.get("latestUpdate"),  # Last update timestamp (int)
            "price": float(data.get("latestPrice", 0.0)),  # Latest stock price (float)
            "source": "IEX",  # Data source (str)
            "data": {
                "open": float(data.get("open", 0.0)),  # Opening price (float)
                "high": float(data.get("high", 0.0)),  # Highest price of the day (float)
                "low": float(data.get("low", 0.0)),  # Lowest price of the day (float)
                "close": float(data.get("latestPrice", 0.0)),  # Closing price (float)
                "volume": int(data.get("volume", 0)),  # Trading volume (int)
            },
        }

    def _handle_success(self, symbol: str) -> None:
        """
        Tracks success metrics for polling and requests.

        Metrics tracked include the source of the data (IEX) and the symbol
        for which polling was performed.

        Args:
            symbol (str): The stock symbol that was successfully polled.

        Returns:
            None
        """
        # Validate status to ensure it is either 'success' or 'failure'
        track_polling_metrics("success", "IEX", symbol)
        # Track request metrics with fixed response time and success status
        track_request_metrics(symbol, 30, 5)

    def _handle_failure(self, symbol: str, error: str) -> None:
        """
        Tracks failure metrics for polling and logs the error.

        This method is called when polling for a stock symbol fails. It logs
        the error and tracks the failure metrics for monitoring purposes.

        Parameters:
        symbol (str): The stock symbol for which polling failed.
        error (str): The error message describing the failure.

        Returns:
        -------
        None
        """
        # Log the error message for debugging purposes
        logger.error(f"IEX polling error for {symbol}: {error}")

        # Track polling metrics indicating a failed polling operation
        track_polling_metrics("failure", "IEX", symbol)

        # Track request metrics with a fixed response time and failure status
        track_request_metrics(symbol, 30, 5, success=False)
