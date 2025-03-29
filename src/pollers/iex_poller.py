/*************  ✨ Codeium Command 🌟  *************/
"""
Poller for fetching stock quotes from the IEX Cloud API.
"""


from typing import Any, Dict, List
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
    """
    Poller for fetching stock quotes from the IEX Cloud API.
    """
    """Poller for fetching stock quotes from the IEX Cloud API."""

    def __init__(self):
        """
        Initializes the IEXPoller.

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

    def poll(self, symbols: List[str]) -> None:
        """
        Polls data for the specified symbols from IEX Cloud API.

        Args:
            symbols (List[str]): List of stock symbols to poll.
        """
    def poll(self, symbols: list[str]) -> None:
        """Polls data for the specified symbols from IEX Cloud API."""
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

                track_polling_metrics("IEX", [symbol])
                track_request_metrics(symbol, 30, 5)

                self.send_to_queue(payload)
                self._handle_success(symbol)

            except Exception as e:
                self._handle_failure(symbol, str(e))

    def _enforce_rate_limit(self) -> None:
        """
        Enforces the rate limit using the RateLimiter class.
        """
        """Enforces the rate limit using the RateLimiter class."""
        self.rate_limiter.acquire(context="IEX")

    def _fetch_data(self, symbol: str) -> Dict[str, Any]:
        """
        Fetches stock data for the given symbol from IEX Cloud API.
    def _fetch_data(self, symbol: str) -> dict[str, Any]:
        """Fetches stock data for the given symbol from IEX Cloud API."""

        Args:
            symbol (str): Stock symbol to fetch data for.

        Returns:
            Dict[str, Any]: Fetched data in the format returned by the IEX API.
        """
        def request_func():
            url = f"https://cloud.iexapis.com/stable/stock/{symbol}/quote?token={self.api_key}"
            return request_with_timeout("GET", url)

        return retry_request(request_func)

    def _process_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processes the raw data from IEX Cloud API into the payload
    def _process_data(self, data: dict[str, Any]) -> dict[str, Any]:
        """Processes the raw data from IEX Cloud API into the payload
        format.

        Args:
            data (Dict[str, Any]): Raw data from IEX API.

        Returns:
            Dict[str, Any]: Processed data in the payload format.
        """
        return {
            "symbol": data.get("symbol", "N/A"),
            "timestamp": data.get("latestUpdate"),
            "price": float(data.get("latestPrice", 0.0)),
            "source": "IEX",
            "data": {
                "open": float(data.get("open", 0.0)),
                "high": float(data.get("high", 0.0)),
                "low": float(data.get("low", 0.0)),
                "close": float(data.get("latestPrice", 0.0)),
                "volume": int(data.get("volume", 0)),
            },
        }

    def _handle_success(self, symbol: str) -> None:
        """
        Tracks success metrics for polling and requests.
        """
        """Tracks success metrics for polling and requests."""
        track_polling_metrics("IEX", [symbol])
        track_request_metrics(symbol, 30, 5)

    def _handle_failure(self, symbol: str, error: str) -> None:
        """
        Tracks failure metrics for polling and logs error.
        """
        """Tracks failure metrics for polling and logs error."""
        track_polling_metrics("IEX", [symbol])
        track_request_metrics(symbol, 30, 5, success=False)
        logger.error(f"Polling error for {symbol}: {error}")

/******  b3098d4c-ebd8-4a29-bafa-2b2039f3efe8  *******/