from typing import Any

import requests

from app.config_shared import get_finnazon_fill_rate_limit, get_finnazon_key
from app.pollers.base_poller import BasePoller
from app.utils.rate_limit import RateLimiter
from app.utils.setup_logger import setup_logger
from app.utils.track_polling_metrics import track_polling_metrics
from app.utils.track_request_metrics import track_request_metrics
from app.utils.validate_data import validate_data
from app.utils.validate_environment_variables import validate_environment_variables

logger = setup_logger(__name__)


class FinnazonPoller(BasePoller):
    """Poller using Finazon's OHLCV endpoint."""

    def __init__(self, symbols: list[str]) -> None:
        super().__init__()
        self.symbols = symbols

        validate_environment_variables(["QUEUE_TYPE", "FINNAZON_API_KEY"])

        self.rate_limiter = RateLimiter(max_requests=get_finnazon_fill_rate_limit(), time_window=60)

        self.base_url = "https://api.finazon.com/api/v1/quotes/historical"
        self.headers = {
            "Authorization": f"Bearer {get_finnazon_key()}",
            "Accept": "application/json",
        }

    def poll(self) -> list[dict[str, Any]]:
        """ """
        results = []
        for symbol in self.symbols:
            try:
                self.rate_limiter.acquire("Finnazon")

                response = requests.get(
                    self.base_url,
                    headers=self.headers,
                    params={
                        "symbols": symbol,
                        "limit": 1,
                        "interval": "1d",
                        "sort": "desc",
                    },
                    timeout=10,
                )
                response.raise_for_status()
                data = response.json()

                quotes = data.get("quotes", [])
                if not quotes:
                    raise ValueError("No quote data returned")

                payload = self._process_data(symbol, quotes[0])
                if not validate_data(payload):
                    raise ValueError("Validation failed")

                results.append(payload)
                self._handle_success(symbol)
            except Exception as e:
                self._handle_failure(symbol, str(e))

        return results

    def _process_data(self, symbol: str, quote: dict[str, Any]) -> dict[str, Any]:
        """Args:
          symbol: str:
          quote: dict[str:
          Any]:
          symbol: str:
          quote: dict[str:
          symbol: str:
          quote: dict[str:
          symbol: str:
          quote: dict[str:
          symbol: str:
          quote: dict[str:
          symbol: str:
          quote: dict[str:

        :param symbol: str:
        :param quote: dict[str:
        :param Any: param symbol: str:
        :param quote: dict[str:
        :param Any: param symbol: str:
        :param quote: dict[str:
        :param Any: param symbol:
        :param quote: type quote: dict[str :
        :param Any: param symbol:
        :param quote: type quote: dict[str :
        :param symbol: str:
        :param quote: dict[str:
        :param symbol: str:
        :param quote: dict[str:
        :param Any: param symbol: str:
        :param quote: dict[str:
        :param Any:
        :param symbol: str:
        :param quote: dict[str:
        :param Any]:

        """
        return {
            "symbol": symbol,
            "timestamp": quote["date"],
            "price": float(quote["close"]),
            "source": "Finnazon",
            "data": {
                "open": float(quote["open"]),
                "high": float(quote["high"]),
                "low": float(quote["low"]),
                "close": float(quote["close"]),
                "volume": int(quote["volume"]),
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
        :param symbol: type symbol: str :
        :param symbol: type symbol: str :
        :param symbol: str:
        :param symbol: str:
        :param symbol: str:
        :param symbol: str:

        """
        track_polling_metrics("success", "Finnazon", symbol)
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
        :param symbol: str:
        :param error: str:

        """
        track_polling_metrics("failure", "Finnazon", symbol)
        track_request_metrics(symbol, 30, 5, success=False)
        logger.error(f"Finnazon polling error for {symbol}: {error}")
