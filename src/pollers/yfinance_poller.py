from typing import Any

import yfinance as yf

from src.config import get_rate_limit
from src.pollers.base_poller import BasePoller
from src.utils.rate_limit import RateLimiter
from src.utils.setup_logger import setup_logger
from src.utils.track_polling_metrics import track_polling_metrics
from src.utils.track_request_metrics import track_request_metrics
from src.utils.validate_data import validate_data
from src.utils.validate_environment_variables import validate_environment_variables

# Logger setup for YFinancePoller
logger = setup_logger(__name__)


class YFinancePoller(BasePoller):

    """Poller for fetching stock data using Yahoo Finance (yfinance)."""

    def __init__(self):
        """Initializes the YFinancePoller with rate limiting and environment
        validation.
        """
        super().__init__()

        # Validate required environment variables
        validate_environment_variables(["QUEUE_TYPE"])

        # Initialize rate limiter
        self.rate_limiter = RateLimiter(max_requests=get_rate_limit(), time_window=60)

    def poll(self, symbols: list[str]) -> None:
        """Polls data for the specified symbols using yfinance."""
        for symbol in symbols:
            try:
                self._enforce_rate_limit()  # Enforce rate limit
                data = self._fetch_data(symbol)  # Fetch data

                if data is None:
                    self._handle_failure(symbol, "No data returned from yfinance.")
                    continue

                payload = self._process_data(symbol, data)  # Process data

                if not validate_data(payload):
                    self._handle_failure(symbol, "Validation failed.")
                    continue

                # Track polling and request metrics
                track_polling_metrics("YFinance", [symbol])
                track_request_metrics(symbol, 30, 5)

                self.send_to_queue(payload)  # Send to queue
                self._handle_success(symbol)  # Handle success

            except Exception as e:
                self._handle_failure(symbol, str(e))  # Handle failure

    def _enforce_rate_limit(self) -> None:
        """Enforces the rate limit using the RateLimiter class."""
        self.rate_limiter.acquire(context="YFinance")

    def _fetch_data(self, symbol: str) -> Any:
        """Fetches recent intraday stock data for the given symbol using
        yfinance.
        """
        ticker = yf.Ticker(symbol)
        data = ticker.history(period="1d", interval="5m")

        if data.empty:
            return None

        return data

    def _process_data(self, symbol: str, data: Any) -> dict[str, Any]:
        """Processes the latest row of yfinance data into the standard payload
        format.
        """
        latest_data = data.iloc[-1]
        timestamp = latest_data.name.isoformat()

        return {
            "symbol": symbol,
            "timestamp": timestamp,
            "price": float(latest_data["Close"]),
            "source": "YFinance",
            "data": {
                "open": float(latest_data["Open"]),
                "high": float(latest_data["High"]),
                "low": float(latest_data["Low"]),
                "close": float(latest_data["Close"]),
                "volume": int(latest_data["Volume"]),
            },
        }

    def _handle_success(self, symbol: str) -> None:
        """Tracks success metrics for polling and requests."""
        track_polling_metrics("success", [symbol])
        track_request_metrics(symbol, 30, 5)

    def _handle_failure(self, symbol: str, error: str) -> None:
        """Tracks failure metrics for polling and logs error."""
        track_polling_metrics("failure", [symbol])
        track_request_metrics(symbol, 30, 5, success=False)
        logger.error(f"YFinance polling error for {symbol}: {error}")
