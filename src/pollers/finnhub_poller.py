from typing import Any

from src.config import get_finnhub_api_key, get_rate_limit
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

    Attributes:
        api_key (str): The API key to access the Finnhub API.
        rate_limiter (RateLimiter): The rate limiter to manage the request rate.
    """

    def __init__(self):
        """
        Initializes the FinnhubPoller.

        Raises:
            ValueError: If the FINNHUB_API_KEY environment variable is not set.
        """
        super().__init__()

        # Validate Finnhub-specific environment
        self.api_key = get_finnhub_api_key()
        if not self.api_key:
            raise ValueError("Missing FINNHUB_API_KEY environment variable.")

        self.rate_limiter = RateLimiter(max_requests=get_rate_limit(), time_window=60)

    def poll(self, symbols: list[str]) -> None:
        """
        Polls data for the specified symbols from Finnhub.

        Args:
            symbols (list[str]): The list of symbols to poll.
        """
        for symbol in symbols:
            try:
                self._enforce_rate_limit()
                data = self._fetch_data(symbol)

                if not data or "c" not in data:
                    self._handle_failure(symbol, "No data or missing current price.")
                    continue

                payload = self._process_data(symbol, data)

                if not validate_data(payload):
                    self._handle_failure(symbol, "Validation failed.")
                    continue

                # Track metrics for polling and requests
                track_polling_metrics("Finnhub", [symbol])
                track_request_metrics(symbol, 30, 5)

                self.send_to_queue(payload)
                self._handle_success(symbol)

            except Exception as e:
                self._handle_failure(symbol, str(e))

    def _enforce_rate_limit(self) -> None:
        """
        Enforces the rate limit using the RateLimiter class.
        """
        self.rate_limiter.acquire(context="Finnhub")

    def _fetch_data(self, symbol: str) -> dict[str, Any]:
        """
        Fetches stock data for the given symbol from Finnhub.

        Args:
            symbol (str): The symbol to fetch data for.

        Returns:
            dict[str, Any]: The fetched data in the format of a dictionary.
        """
        def request_func():
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
            dict[str, Any]: The processed data in the format of a dictionary.
        """
        return {
            "symbol": symbol,
            "timestamp": None,  # Finnhub does not provide timestamps in quotes
            "price": float(data["c"]),
            "source": "Finnhub",
            "data": {
                "current": float(data["c"]),
                "high": float(data["h"]),
                "low": float(data["l"]),
                "open": float(data["o"]),
                "previous_close": float(data["pc"]),
            },
        }

    def _handle_success(self, symbol: str) -> None:
        """
        Tracks success metrics for polling and requests.

        Args:
            symbol (str): The symbol to track metrics for.
        """
        track_polling_metrics("Finnhub", [symbol])
        track_request_metrics(symbol, 30, 5)

    def _handle_failure(self, symbol: str, error: str) -> None:
        """
        Tracks failure metrics for polling and requests.

        Args:
            symbol (str): The symbol to track metrics for.
            error (str): The error message to log.
        """
        track_polling_metrics("Finnhub", [symbol])
        track_request_metrics(symbol, 30, 5, success=False)
        logger.error(f"Polling error for {symbol}: {error}")

