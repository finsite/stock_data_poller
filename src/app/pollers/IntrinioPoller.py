from typing import Any

import requests

from app.config import get_intrinio_fill_rate_limit, get_intrinio_key
from app.pollers.base_poller import BasePoller
from app.utils.rate_limit import RateLimiter
from app.utils.setup_logger import setup_logger
from app.utils.track_polling_metrics import track_polling_metrics
from app.utils.track_request_metrics import track_request_metrics
from app.utils.validate_data import validate_data
from app.utils.validate_environment_variables import validate_environment_variables

logger = setup_logger(__name__)


class IntrinioPoller(BasePoller):
    """Poller using Intrinio's historical prices endpoint."""

    def __init__(self, symbols: list[str]) -> None:
        super().__init__()
        self.symbols = symbols

        validate_environment_variables(["QUEUE_TYPE", "INTRINIO_API_KEY"])

        self.rate_limiter = RateLimiter(max_requests=get_intrinio_fill_rate_limit(), time_window=60)

        self.base_url = "https://api.intrinio.com/securities/{symbol}/prices"
        self.auth = (get_intrinio_key(), "")  # Intrinio uses basic auth with API key as username

    def poll(self) -> list[dict[str, Any]]:
        """ """
        results = []
        for symbol in self.symbols:
            try:
                self.rate_limiter.acquire("Intrinio")

                url = self.base_url.format(symbol=symbol)
                response = requests.get(
                    url,
                    auth=self.auth,
                    params={
                        "page_size": 1,
                        "sort_order": "desc",
                        "frequency": "daily",
                    },
                    timeout=10,
                )
                response.raise_for_status()
                data = response.json()

                prices = data.get("stock_prices", [])
                if not prices:
                    raise ValueError("No price data returned")

                payload = self._process_data(symbol, prices[0])
                if not validate_data(payload):
                    raise ValueError("Validation failed")

                results.append(payload)
                self._handle_success(symbol)
            except Exception as e:
                self._handle_failure(symbol, str(e))

        return results

    def _process_data(self, symbol: str, price: dict[str, Any]) -> dict[str, Any]:
        """Args:
          symbol: str:
          price: dict[str:
          Any]:
          symbol: str:
          price: dict[str:
          symbol: str:
          price: dict[str:
          symbol: str:
          price: dict[str:
          symbol: str:
          price: dict[str:
          symbol: str:
          price: dict[str:

        :param symbol: str:
        :param price: dict[str:
        :param Any: param symbol: str:
        :param price: dict[str:
        :param Any: param symbol: str:
        :param price: dict[str:
        :param Any: 
        :param symbol: 
        :type symbol: str :
        :param price: 
        :type price: dict[str :
        :param Any]: 
        :param symbol: 
        :type symbol: str :
        :param price: 
        :type price: dict[str :
        :param symbol: str: 
        :param price: dict[str: 

        
        """
        return {
            "symbol": symbol,
            "timestamp": price["date"],
            "price": float(price["close"]),
            "source": "Intrinio",
            "data": {
                "open": float(price["open"]),
                "high": float(price["high"]),
                "low": float(price["low"]),
                "close": float(price["close"]),
                "volume": int(price.get("volume", 0)),
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

        :param symbol: str:
        :param symbol: str:
        :param symbol: str:
        :param symbol: 
        :type symbol: str :
        :param symbol: 
        :type symbol: str :
        :param symbol: str: 

        
        """
        track_polling_metrics("success", "Intrinio", symbol)
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

        :param symbol: str:
        :param error: str:
        :param symbol: str:
        :param error: str:
        :param symbol: str:
        :param error: str:
        :param symbol: 
        :type symbol: str :
        :param error: 
        :type error: str :
        :param symbol: 
        :type symbol: str :
        :param error: 
        :type error: str :
        :param symbol: str: 
        :param error: str: 

        
        """
        track_polling_metrics("failure", "Intrinio", symbol)
        track_request_metrics(symbol, 30, 5, success=False)
        logger.error(f"Intrinio polling error for {symbol}: {error}")
