"""Poller class for fetching stock data using Yahoo Finance (yfinance)."""

from typing import Any

import yfinance as yf

from app.config import get_yfinance_fill_rate_limit
from app.pollers.base_poller import BasePoller
from app.utils.rate_limit import RateLimiter
from app.utils.setup_logger import setup_logger
from app.utils.track_polling_metrics import track_polling_metrics
from app.utils.track_request_metrics import track_request_metrics
from app.utils.validate_data import validate_data
from app.utils.validate_environment_variables import validate_environment_variables

# Logger setup for YFinancePoller
logger = setup_logger(__name__)


class YFinancePoller(BasePoller):
    """Poller for fetching stock data using Yahoo Finance (yfinance)."""

    def __init__(self) -> None:
        """Initializes the YFinancePoller with rate limiting and environment
        validation.
        """
        super().__init__()

        # Ensure required environment variables are present
        validate_environment_variables(["QUEUE_TYPE"])

        # Initialize poller-specific rate limiter
        self.rate_limiter = RateLimiter(
            max_requests=get_yfinance_fill_rate_limit(),
            time_window=60,
        )

    def poll(self, symbols: list[str]) -> None:
        """Polls data for the specified symbols using yfinance.
        
        Args:
        ----
          symbols(list[str]): The stock symbols to fetch data for.
          symbols: list[str]:
          symbols: list[str]:
          symbols: list[str]:
          symbols: list[str]:
          symbols: list[str]:
          symbols: list[str]:

        :param symbols: list[str]:
        :param symbols: list[str]:
        :param symbols: list[str]:
        :param symbols: type symbols: list[str] :
        :param symbols: type symbols: list[str] :
        :param symbols: list[str]:
        :param symbols: list[str]:
        :param symbols: list[str]: 

        """
        for symbol in symbols:
            try:
                self._enforce_rate_limit()
                data = self._fetch_data(symbol)

                if data is None:
                    self._handle_failure(symbol, "No data returned from yfinance.")
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
        """Enforces the rate limit using the RateLimiter class."""
        self.rate_limiter.acquire(context="YFinance")

    def _fetch_data(self, symbol: str) -> Any:
        """Fetches recent intraday stock data for the given symbol using yfinance.
        
        Args:
        ----
            symbol (str): The stock symbol to fetch.

        :param symbol: str:
        :param symbol: str:
        :param symbol: str:
        :param symbol: type symbol: str :
        :param symbol: type symbol: str :
        :param symbol: str:
        :param symbol: str:
        :param symbol: str: 

        """
        ticker = yf.Ticker(symbol)
        data = ticker.history(period="1d", interval="5m")

        return None if data.empty else data

    def _process_data(self, symbol: str, data: Any) -> dict[str, Any]:
        """Processes the latest row of yfinance data into the standard payload format.
        
        Args:
        ----
            symbol (str): The stock symbol.
            data (Any): Raw data from yfinance.

        :param symbol: str:
        :param data: Any:
        :param symbol: str:
        :param data: Any:
        :param symbol: str:
        :param data: Any:
        :param symbol: type symbol: str :
        :param data: type data: Any :
        :param symbol: type symbol: str :
        :param data: type data: Any :
        :param symbol: str:
        :param data: Any:
        :param symbol: str:
        :param data: Any:
        :param symbol: str: 
        :param data: Any: 

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
        """Tracks success metrics for polling and requests.
        
        Args:
        ----
          symbol(str): The stock symbol.
          symbol: str:
          symbol: str:
          symbol: str:
          symbol: str:
          symbol: str:
          symbol: str:

        :param symbol: str:
        :param symbol: str:
        :param symbol: str:
        :param symbol: type symbol: str :
        :param symbol: type symbol: str :
        :param symbol: str:
        :param symbol: str:
        :param symbol: str: 

        """
        track_polling_metrics("success", "YFinance", symbol)
        track_request_metrics(symbol, 30, 5)

    def _handle_failure(self, symbol: str, error: str) -> None:
        """Tracks failure metrics and logs the error.
        
        Args:
        ----
          symbol(str): The stock symbol.
          error(str): The error message.
          symbol: str:
          error: str:
          symbol: str:
          error: str:
          symbol: str:
          error: str:
          symbol: str:
          error: str:
          symbol: str:
          error: str:
          symbol: str:
          error: str:

        :param symbol: str:
        :param error: str:
        :param symbol: str:
        :param error: str:
        :param symbol: str:
        :param error: str:
        :param symbol: type symbol: str :
        :param error: type error: str :
        :param symbol: type symbol: str :
        :param error: type error: str :
        :param symbol: str:
        :param error: str:
        :param symbol: str:
        :param error: str:
        :param symbol: str: 
        :param error: str: 

        """
        track_polling_metrics("failure", "YFinance", symbol)
        track_request_metrics(symbol, 30, 5, success=False)
        logger.error(f"YFinance polling error for {symbol}: {error}")
