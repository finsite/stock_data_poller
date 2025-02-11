import time
from typing import List, Dict, Any

from src.pollers.base_poller import BasePoller
from src.utils.rate_limit import rate_limit
from src.utils.request_with_timeout import request_with_timeout
from src.utils.retry_request import retry_request
from src.utils.track_polling_metrics import track_polling_metrics
from src.utils.track_request_metrics import track_request_metrics
from src.utils.validate_data import validate_data
from src.utils.validate_environment_variables import validate_environment_variables


class AlphaVantagePoller(BasePoller):
    """
    Poller for AlphaVantage API.
    """

    def __init__(self, api_key: str):
        super().__init__()
        validate_environment_variables(["SQS_QUEUE_URL", "ALPHAVANTAGE_API_KEY"])
        self.api_key = api_key
        self.last_request_time = 0
        self.rate_limit_interval = 60  # AlphaVantage allows 5 requests per minute

    def poll(self, symbols: List[str]) -> None:
        """
        Polls data for the specified symbols from AlphaVantage.

        Args:
            symbols (List[str]): List of stock symbols to poll.
        """
        for symbol in symbols:
            try:
                self._enforce_rate_limit()

                # Fetch data from AlphaVantage
                data = self._fetch_data(symbol)
                if "Error Message" in data:
                    self._handle_failure("Error Message from AlphaVantage")
                    continue

                # Process and validate the latest time series data
                payload = self._process_data(symbol, data)
                if not validate_data(payload):
                    self._handle_failure(f"Validation failed for symbol: {symbol}")
                    continue

                # Send payload to the queue
                self.send_to_queue(payload)

                # Track success metrics
                self._handle_success()

            except Exception as e:
                self._handle_failure(str(e))

    def _enforce_rate_limit(self) -> None:
        """
        Enforces the rate limit for API requests.
        """
        rate_limit(self.last_request_time, self.rate_limit_interval)
        self.last_request_time = time.time()

    def _fetch_data(self, symbol: str) -> Dict[str, Any]:
        """
        Fetches data for the given symbol from AlphaVantage.

        Args:
            symbol (str): The stock symbol to fetch data for.

        Returns:
            Dict[str, Any]: The JSON response from AlphaVantage.
        """
        def request_func():
            url = (
                f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY"
                f"&symbol={symbol}&interval=5min&apikey={self.api_key}"
            )
            return request_with_timeout("GET", url)

        return retry_request(request_func)

    def _process_data(self, symbol: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processes the latest time series data into a payload.

        Args:
            symbol (str): The stock symbol.
            data (Dict[str, Any]): The raw time series data.

        Returns:
            Dict[str, Any]: The processed payload.
        """
        time_series = data["Time Series (5min)"]
        latest_time = max(time_series.keys())
        latest_data = time_series[latest_time]

        payload = {
            "symbol": symbol,
            "timestamp": latest_time,
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
        return payload

    def _handle_success(self) -> None:
        """
        Tracks success metrics for polling and requests.
        """
        track_polling_metrics("success")
        track_request_metrics("success", source="AlphaVantage")

    def _handle_failure(self, error: str) -> None:
        """
        Tracks failure metrics for polling and requests.

        Args:
            error (str): Error message or reason for failure.
        """
        track_polling_metrics("failure", error=error)
        track_request_metrics("failure", source="AlphaVantage")
