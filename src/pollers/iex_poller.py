"""Poller for fetching stock quotes from the IEX Cloud API."""

from typing import Any

from src.config import get_iex_api_key, get_rate_limit
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

    """Poller for fetching stock quotes from the IEX Cloud API."""

    def __init__(self):
        """Initializes the IEXPoller.

        Raises:
            ValueError: If the IEX_API_KEY environment variable is not set.

        """
        super().__init__()

        # Validate IEX-specific environment
        # ✅ Validate IEX-specific environment
        self.api_key = get_iex_api_key()
        if not self.api_key:
            raise ValueError("IEX_API_KEY environment variable is not set.")
            raise ValueError("❌ Missing IEX_API_KEY.")

        self.rate_limiter = RateLimiter(max_requests=get_rate_limit(), time_window=60)

    def poll(self, symbols: list[str]) -> None:
        """Polls data for the specified symbols from IEX Cloud API.

        This function iterates over the list of symbols and fetches the latest
        price from the IEX Cloud API. If the response is valid and contains the
        "latestPrice" key, the data is processed into a payload and sent to the
        message queue. If the response is invalid or contains missing data, an
        error is logged and the function continues to the next symbol.

        Args:
            symbols (List[str]): List of stock symbols to poll.

        """
        for symbol in symbols:
            try:
                # Enforce rate limit
                self._enforce_rate_limit()

                # Fetch data from IEX Cloud API
                data = self._fetch_data(symbol)

                if not data or "latestPrice" not in data:
                    # Handle failure
                    self._handle_failure(symbol, "No data or missing latest price.")
                    continue

                # Process data into payload
                payload = self._process_data(data)

                if not validate_data(payload):
                    # Handle failure
                    self._handle_failure(symbol, "Validation failed.")
                    continue

                # Track metrics
                track_polling_metrics("IEX", [symbol])
                track_request_metrics(symbol, 30, 5)

                # Send payload to queue
                self.send_to_queue(payload)

                # Handle success
                self._handle_success(symbol)

            except Exception as e:
                # Handle failure
                self._handle_failure(symbol, str(e))

    def _enforce_rate_limit(self) -> None:
        """Enforces the rate limit using the RateLimiter class to avoid exceeding the
        allowed number of requests per minute.
        """
        """Enforces the rate limit using the RateLimiter class to avoid exceeding the
        allowed number of requests per minute.

        The rate limiter is configured to allow a maximum of 5 requests per minute.
        """
        self.rate_limiter.acquire(context="IEX")

    def _fetch_data(self, symbol: str) -> dict[str, Any]:
        """Fetches stock data for the given symbol from the IEX Cloud API.

        Args:
            symbol (str): Stock symbol to fetch data for.

        Returns:
            Dict[str, Any]: Fetched data in the format returned by the IEX API.

        """

        def request_func():
            # Construct the API URL with the given symbol and API key
            url = f"https://cloud.iexapis.com/stable/stock/{symbol}/quote?token={self.api_key}"
            # Make a GET request to the IEX API with a timeout
            return request_with_timeout("GET", url)

        # Retry the request in case of failure
        return retry_request(request_func)

    def _process_data(self, data: dict[str, Any]) -> dict[str, Any]:
        """Processes the raw data from IEX Cloud API into the payload
        format.

        Args:
            data (Dict[str, Any]): Raw data from IEX API.

        Returns:
            Dict[str, Any]: Processed data in the payload format.

        """
        # Process the raw data into the payload format
        return {
            "symbol": data.get("symbol", "N/A"),  # Symbol
            "timestamp": data.get("latestUpdate"),  # Timestamp
            "price": float(data.get("latestPrice", 0.0)),  # Latest price
            "source": "IEX",  # Source
            "data": {
                "open": float(data.get("open", 0.0)),  # Open price
                "high": float(data.get("high", 0.0)),  # High price
                "low": float(data.get("low", 0.0)),  # Low price
                "close": float(data.get("latestPrice", 0.0)),  # Close price
                "volume": int(data.get("volume", 0)),  # Volume
            },
        }

    def _handle_success(self, symbol: str) -> None:
        """Tracks success metrics for polling and requests."""
        # Track success metrics for polling and requests
        track_polling_metrics("IEX", [symbol])
        track_request_metrics(symbol, 30, 5)

    def _handle_failure(self, symbol: str, error: str) -> None:
        """Tracks failure metrics for polling and logs error."""
        # Track failure metrics for polling and logs error
        track_polling_metrics("IEX", [symbol])
        track_request_metrics(symbol, 30, 5, success=False)
        logger.error(f"Polling error for {symbol}: {error}")
