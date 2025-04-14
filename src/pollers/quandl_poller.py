"""
The module provides a poller class for fetching stock data using the Quandl (now Nasdaq
Data Link) API.

The poller class is QuandlPoller and it inherits the BasePoller class. The poller class
fetches stock data from the Quandl API using the request_with_timeout function. It also
enforces a rate limit using the RateLimiter class.
"""

from typing import Any

from src.config import get_quandl_api_key, get_quandl_fill_rate_limit
from src.pollers.base_poller import BasePoller
from src.utils.rate_limit import RateLimiter
from src.utils.request_with_timeout import request_with_timeout
from src.utils.retry_request import retry_request
from src.utils.setup_logger import setup_logger
from src.utils.track_polling_metrics import track_polling_metrics
from src.utils.track_request_metrics import track_request_metrics
from src.utils.validate_data import validate_data

# ✅ Logger setup
logger = setup_logger(__name__)


class QuandlPoller(BasePoller):
    """Poller for fetching stock data from the Quandl (now Nasdaq Data Link) API."""

    def __init__(self):
        """
        Initializes the QuandlPoller.

        Raises
        ------
            ValueError: If QUANDL_API_KEY is not set.
        """
        super().__init__()

        self.api_key = get_quandl_api_key()
        if not self.api_key:
            raise ValueError("❌ Missing QUANDL_API_KEY.")

        self.rate_limiter = RateLimiter(
            max_requests=get_quandl_fill_rate_limit(),
            time_window=60,
        )

    def poll(self, symbols: list[str]) -> None:
        """
        Polls data for the specified symbols from Quandl API.

        Args:
        ----
            symbols (list[str]): List of stock symbols to poll.
        """
        for symbol in symbols:
            try:
                self._enforce_rate_limit()
                data = self._fetch_data(symbol)

                if not data or "dataset" not in data:
                    self._handle_failure(symbol, "Missing dataset in response.")
                    continue

                payload = self._process_data(symbol, data)

                if not validate_data(payload):
                    self._handle_failure(symbol, "Validation failed.")
                    continue

                # Track metrics for successful polling and request
                track_request_metrics(symbol, 30, 5)

                self.send_to_queue(payload)
                self._handle_success(symbol)

            except Exception as e:
                self._handle_failure(symbol, str(e))

    def _enforce_rate_limit(self) -> None:
        """
        Enforces the rate limit using the RateLimiter class.

        The rate limit is set to 5 requests per minute. If the rate limit is
        exceeded, the function will block until the limit is replenished.
        """
        self.rate_limiter.acquire(context="Quandl")

    def _fetch_data(self, symbol: str) -> dict[str, Any]:
        """
        Fetches stock data for the given symbol from Quandl API.

        Args:
        ----
            symbol (str): Stock symbol to fetch data for.

        Returns:
        -------
            dict[str, Any]: Fetched data in the format returned by the Quandl API.
        """

        def request_func():
            url = (
                f"https://data.nasdaq.com/api/v3/datasets/WIKI/{symbol}.json"
                f"?api_key={self.api_key}"
            )
            return request_with_timeout("GET", url)

        return retry_request(request_func)

    def _process_data(self, symbol: str, data: dict[str, Any]) -> dict[str, Any]:
        """
        Processes the raw data from Quandl API into the payload format.

        Args:
        ----
            symbol (str): Stock symbol.
            data (dict[str, Any]): Raw data from Quandl API.

        Returns:
        -------
            dict[str, Any]: Processed data in the payload format.
        """
        dataset = data["dataset"]
        latest_row = dataset["data"][0]
        columns = dataset["column_names"]
        col_index = {col: idx for idx, col in enumerate(columns)}

        return {
            "symbol": symbol,
            "timestamp": latest_row[col_index["Date"]],
            "price": float(latest_row[col_index["Close"]]),
            "source": "Quandl",
            "data": {
                "open": float(latest_row[col_index["Open"]]),
                "high": float(latest_row[col_index["High"]]),
                "low": float(latest_row[col_index["Low"]]),
                "close": float(latest_row[col_index["Close"]]),
                "volume": int(latest_row[col_index["Volume"]]),
            },
        }

    # def _handle_success(self, symbol: str) -> None:
    #     """Tracks success metrics for polling and requests."""
    #     track_polling_metrics("Quandl", [symbol])
    #     track_request_metrics(symbol, 30, 5)

    # def _handle_failure(self, symbol: str, error: str) -> None:
    #     """
    #     Tracks failure metrics for polling and logs error.

    #     Args:
    #     ----
    #         symbol (str): Stock symbol.
    #         error (str): Error message.
    #     """
    #     track_polling_metrics("Quandl", [symbol])
    #     track_request_metrics(symbol, 30, 5, success=False)
    #     logger.error(f"Quandl polling error for {symbol}: {error}")
    def _handle_success(self, symbol: str) -> None:
        """
        Tracks success metrics for polling and requests.

        Parameters:
        -----------
        symbol : str
            The symbol for which polling was performed.

        Returns:
        --------
        None
        """
        # Track polling metrics indicating a successful polling operation
        track_polling_metrics("success", "Quandl", symbol)
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
        # Track polling metrics indicating a failed polling operation
        track_polling_metrics("failure", "Quandl", symbol)
        # Track request metrics with fixed response time and failed status
        track_request_metrics(symbol, 30, 5, success=False)
        # Log the error message for debugging purposes
        logger.error(f"Quandl polling error for {symbol}: {error}")
