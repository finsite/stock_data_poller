"""
Poller for fetching stock data from AlphaVantage API.

The AlphaVantagePoller class fetches the daily data for the given symbols from the
AlphaVantage API and sends it to the message queue.

The poller enforces a per-minute rate limit using the configured environment or Vault
value.
"""

from datetime import datetime
from typing import Any

from src.config import get_alpha_vantage_api_key, get_alpha_vantage_fill_rate_limit
from src.pollers.base_poller import BasePoller
from src.utils.rate_limit import RateLimiter
from src.utils.request_with_timeout import request_with_timeout
from src.utils.retry_request import retry_request
from src.utils.setup_logger import setup_logger
from src.utils.track_polling_metrics import track_polling_metrics
from src.utils.track_request_metrics import track_request_metrics
from src.utils.validate_data import validate_data

logger = setup_logger(__name__)


class AlphaVantagePoller(BasePoller):
    """Poller for fetching stock data from AlphaVantage API."""

    def __init__(self) -> None:
        """
        Initializes the AlphaVantagePoller with rate limit and API key.

        Raises
        ------
        ValueError
            If the ALPHA_VANTAGE_API_KEY environment variable is not set.
        """
        super().__init__()

        # Validate required environment variable
        self.api_key: str = get_alpha_vantage_api_key()
        if not self.api_key:
            raise ValueError("Missing ALPHA_VANTAGE_API_KEY.")

        # Initialize rate limiter
        self.rate_limiter = RateLimiter(
            max_requests=get_alpha_vantage_fill_rate_limit(), time_window=60
        )

    def poll(self, symbols: list[str]) -> None:
        """
        Polls data for the specified symbols from AlphaVantage API.

        Args:
        ----
            symbols (list[str]): The list of stock symbols to poll.

        Returns:
        -------
            None: This function does not return a value.
        """
        for symbol in symbols:
            try:
                self._enforce_rate_limit()
                data = self._fetch_data(symbol)

                if "Error Message" in data:
                    self._handle_failure(
                        symbol, f"Error from AlphaVantage: {data['Error Message']}"
                    )
                    continue

                payload = self._process_data(symbol, data)

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

        Acquires permission to proceed with a request. Blocks if the rate limit is
        exceeded.

        Args:
            None

        Returns:
            None
        """
        self.rate_limiter.acquire(context="AlphaVantage")

    def _fetch_data(self, symbol: str) -> dict[str, Any]:
        """
        Fetches data for the given symbol from AlphaVantage API.

        Args:
        ----
            symbol (str): The stock symbol.

        Returns:
        -------
            dict[str, Any]: The fetched data from AlphaVantage.
        """

        def request_func() -> dict[str, Any]:
            url = (
                "https://www.alphavantage.co/query"
                f"?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=5min&apikey={self.api_key}"
            )
            return request_with_timeout(url)

        return retry_request(request_func)

    def _process_data(self, symbol: str, data: dict[str, Any]) -> dict[str, Any]:
        """
        Processes the latest time series data into a standardized payload.

        Args:
        ----
            symbol (str): Stock symbol.
            data (dict[str, Any]): Raw data from AlphaVantage.

        Returns:
        -------
            dict[str, Any]: Transformed payload.
        """
        time_series = data.get("Time Series (5min)")
        if not time_series:
            raise ValueError(f"No 'Time Series (5min)' data found for symbol: {symbol}")

        latest_time = max(time_series.keys())
        latest_data = time_series[latest_time]

        return {
            "symbol": symbol,
            "timestamp": int(datetime.fromisoformat(latest_time).timestamp()),
            "price": float(latest_data["4. close"]),
            "source": "AlphaVantage",
            "data": {
                "open": float(latest_data["1. open"]),
                "high": float(latest_data["2. high"]),
                "low": float(latest_data["3. low"]),
                "close": float(latest_data["4. close"]),
                "volume": int(latest_data["5. volume"]),
            },
        }

    def _handle_success(self, symbol: str) -> None:
        """
        Tracks success metrics for polling and requests.

        Parameters:
        symbol (str): The stock symbol that was successfully polled.

        Returns:
        None
        """
        # Track polling metrics indicating a successful polling operation
        track_polling_metrics("success", "AlphaVantage", symbol)

        # Track request metrics with fixed response time and status
        track_request_metrics(symbol, 30, 5)

    def _handle_failure(self, symbol: str, error: str) -> None:
        """
        Tracks failure metrics and logs the error.

        This method is called when the poller fails to fetch data for a given
        symbol. It logs the error and tracks the failure metrics.

        Parameters:
        symbol (str): The stock symbol for which polling failed.
        error (str): The error message describing the failure.
        """
        # Log the error for debugging purposes
        logger.error(f"AlphaVantage poll failed for {symbol}: {error}")

        # Track polling metrics indicating a failed polling operation
        track_polling_metrics("failure", "AlphaVantage", symbol)

        # Track request metrics with fixed response time and failed status
        track_request_metrics(symbol, 30, 5, success=False)
