from typing import Any

import requests

from app.config import get_rapidapi_host, get_rapidapi_key, get_yfinance_fill_rate_limit
from app.pollers.base_poller import BasePoller
from app.utils.rate_limit import RateLimiter
from app.utils.setup_logger import setup_logger
from app.utils.track_polling_metrics import track_polling_metrics
from app.utils.track_request_metrics import track_request_metrics
from app.utils.validate_data import validate_data
from app.utils.validate_environment_variables import validate_environment_variables

# This module contains a poller class for Yahoo Finance using RapidAPI


logger = setup_logger(__name__)


class YahooRapidAPIPoller(BasePoller):
    """Poller using RapidAPI Yahoo Finance endpoint."""

    def __init__(self, symbols: list[str]) -> None:
        """Initializes the YahooRapidAPIPoller with rate limiting and environment
        validation.

        Args:
        ----
            symbols (list[str]): The stock symbols to poll.

        """
        super().__init__()
        self.symbols = symbols

        # Validate required environment variables
        validate_environment_variables(["QUEUE_TYPE", "RAPIDAPI_KEY", "RAPIDAPI_HOST"])

        # Initialize rate limiter
        self.rate_limiter = RateLimiter(max_requests=get_yfinance_fill_rate_limit(), time_window=60)

        # Set up the base URL and headers for the Yahoo Finance API call
        self.base_url = f"https://{get_rapidapi_host()}/stock/v2/get-summary"
        self.headers = {
            "x-rapidapi-key": get_rapidapi_key(),
            "x-rapidapi-host": get_rapidapi_host(),
        }

    def poll(self) -> list[dict[str, Any]]:
        """ """
        results = []
        for symbol in self.symbols:
            try:
                self.rate_limiter.acquire("YahooRapidAPI")

                response = requests.get(
                    self.base_url,
                    headers=self.headers,
                    params={"symbol": symbol},
                    timeout=10,
                )
                response.raise_for_status()
                data = response.json()

                price_info = data.get("price", {})
                if not price_info:
                    raise ValueError("No price data returned")

                payload = self._process_data(symbol, price_info)
                if not validate_data(payload):
                    raise ValueError("Validation failed")

                results.append(payload)
                self._handle_success(symbol)
            except Exception as e:
                self._handle_failure(symbol, str(e))

        return results

    def _process_data(self, symbol: str, price_info: dict[str, Any]) -> dict[str, Any]:
        """Processes the raw data from the Yahoo Finance API into a standardized payload
        format.

        Args:
        ----
            symbol (str): The stock symbol.
            price_info (dict[str, Any]): The raw data from the Yahoo Finance API.

        Parameters
        ----------
        symbol :
            str:
        price_info :
            dict[str:
        Any :
            param symbol: str:
        price_info :
            dict[str:
        Any :
            param symbol: str:
        price_info :
            dict[str:
        Any :

        symbol : str :

        price_info : dict[str :

        Any] :

        symbol: str :

        price_info: dict[str :


        Returns
        -------
        Args :

        ----
            symbol: str:
            price_info: dict[str:
            Any]:


        """
        return {
            "symbol": symbol,
            # The timestamp is the time of the latest market update.
            "timestamp": price_info.get("regularMarketTime"),
            # The price is the latest price of the stock.
            "price": float(price_info.get("regularMarketPrice", 0)),
            # The source is the name of the API.
            "source": "YahooRapidAPI",
            # The additional data fields are:
            # - open (float): The opening price of the stock.
            # - high (float): The highest price of the stock.
            # - low (float): The lowest price of the stock.
            # - close (float): The closing price of the stock.
            # - volume (int): The trading volume of the stock.
            "data": {
                "open": float(price_info.get("regularMarketOpen", 0)),
                "high": float(price_info.get("regularMarketDayHigh", 0)),
                "low": float(price_info.get("regularMarketDayLow", 0)),
                "close": float(price_info.get("regularMarketPreviousClose", 0)),
                "volume": int(price_info.get("regularMarketVolume", 0)),
            },
        }

    def _handle_success(self, symbol: str) -> None:
        """Args:
          symbol: str:
          symbol: str:
          symbol: str:
          symbol: str:
          symbol: str:
          symbol: str:

        Parameters
        ----------
        symbol :
            str:
        symbol :
            str:
        symbol :
            str:
        symbol : str :

        symbol: str :


        Returns
        -------


        """
        track_polling_metrics("success", "YahooRapidAPI", symbol)
        track_request_metrics(symbol, 30, 5)

    def _handle_failure(self, symbol: str, error: str) -> None:
        """Args:
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

        Parameters
        ----------
        symbol :
            str:
        error :
            str:
        symbol :
            str:
        error :
            str:
        symbol :
            str:
        error :
            str:
        symbol : str :

        error : str :

        symbol: str :

        error: str :


        Returns
        -------


        """
        track_polling_metrics("failure", "YahooRapidAPI", symbol)
        track_request_metrics(symbol, 30, 5, success=False)
        logger.error(f"YahooRapidAPI polling error for {symbol}: {error}")
