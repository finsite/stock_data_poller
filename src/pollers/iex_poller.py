from typing import List, Dict, Any

from src.pollers.base_poller import BasePoller
from src.utils.retry_request import retry_request
from src.utils.validate_data import validate_data
from src.utils.track_polling_metrics import track_polling_metrics
from src.utils.track_request_metrics import track_request_metrics
from src.utils.request_with_timeout import request_with_timeout
from src.utils.validate_environment_variables import validate_environment_variables


class IEXPoller(BasePoller):
    """
    Poller for fetching stock quotes from the IEX Cloud API.
    """

    def __init__(self, api_key: str):
        """
        Initializes the IEXPoller.

        Args:
            api_key (str): API key for accessing the IEX Cloud API.
        """
        super().__init__()
        validate_environment_variables(["SQS_QUEUE_URL", "IEX_API_KEY"])
        self.api_key = api_key

    def poll(self, symbols: List[str]) -> None:
        """
        Polls data for the specified symbols from IEX Cloud API.

        Args:
            symbols (List[str]): List of stock symbols to poll.
        """
        for symbol in symbols:
            try:
                # Fetch data from IEX Cloud API
                data = self._fetch_data(symbol)
                if not data:
                    continue

                # Process and validate the payload
                payload = self._process_data(data)
                if not validate_data(payload):
                    self._handle_failure(f"Validation failed for symbol: {symbol}")
                    continue

                # Send payload to the queue
                self.send_to_queue(payload)

                # Track success metrics
                self._handle_success()

            except Exception as e:
                self._handle_failure(str(e))

    def _fetch_data(self, symbol: str) -> Dict[str, Any]:
        """
        Fetches stock data for the given symbol from IEX Cloud API.

        Args:
            symbol (str): The stock symbol to fetch data for.

        Returns:
            Dict[str, Any]: The JSON response from IEX Cloud API.
        """
        try:
            def request_func():
                url = f"https://cloud.iexapis.com/stable/stock/{symbol}/quote?token={self.api_key}"
                return request_with_timeout("GET", url)

            data = retry_request(request_func)

            if not data:
                track_request_metrics("failure", source="IEX")
                return None

            return data
        except Exception as e:
            self._handle_failure(f"Error fetching data for {symbol}: {e}")
            return None

    def _process_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processes the raw data into the payload format.

        Args:
            data (Dict[str, Any]): The raw data from IEX Cloud API.

        Returns:
            Dict[str, Any]: The processed payload.
        """
        return {
            "symbol": data["symbol"],
            "timestamp": data["latestUpdate"],
            "price": float(data["latestPrice"]),
            "source": "IEX",
            "data": {
                "open": float(data.get("open", 0)),  # Default to 0 if not provided
                "high": float(data.get("high", 0)),
                "low": float(data.get("low", 0)),
                "close": float(data["latestPrice"]),
                "volume": int(data.get("volume", 0)),  # Default to 0 if not provided
            },
        }

    def _handle_success(self) -> None:
        """
        Tracks success metrics for polling and requests.
        """
        track_polling_metrics("success")
        track_request_metrics("success", source="IEX")

    def _handle_failure(self, error: str) -> None:
        """
        Tracks failure metrics for polling and requests.

        Args:
            error (str): Error message or reason for failure.
        """
        track_polling_metrics("failure", error=error)
        track_request_metrics("failure", source="IEX")
