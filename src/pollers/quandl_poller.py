from typing import List, Dict, Any
from src.pollers.base_poller import BasePoller
from src.utils.request_with_timeout import request_with_timeout
from src.utils.retry_request import retry_request
from src.utils.track_polling_metrics import track_polling_metrics
from src.utils.track_request_metrics import track_request_metrics
from src.utils.validate_data import validate_data
from src.utils.validate_environment_variables import validate_environment_variables


class QuandlPoller(BasePoller):
    """
    Poller for fetching stock data from Quandl API.
    """

    def __init__(self, api_key: str):
        """
        Initializes the QuandlPoller.

        Args:
            api_key (str): API key for accessing Quandl API.
        """
        super().__init__()
        validate_environment_variables(["SQS_QUEUE_URL", "QUANDL_API_KEY"])
        self.api_key = api_key

    def poll(self, symbols: List[str]) -> None:
        """
        Polls data for the specified symbols from Quandl.

        Args:
            symbols (List[str]): List of stock symbols to poll.
        """
        for symbol in symbols:
            try:
                # Fetch data from Quandl API
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
        Fetches stock data for the given symbol from Quandl.

        Args:
            symbol (str): The stock symbol to fetch data for.

        Returns:
            Dict[str, Any]: The JSON response from Quandl API.
        """
        try:
            def request_func():
                url = (
                    f"https://www.quandl.com/api/v3/datasets/WIKI/{symbol}.json?"
                    f"api_key={self.api_key}"
                )
                return request_with_timeout("GET", url)

            data = retry_request(request_func)

            if "dataset" not in data:
                track_request_metrics("failure", source="Quandl")
                return None

            return data
        except Exception as e:
            self._handle_failure(f"Error fetching data for {symbol}: {e}")
            return None

    def _process_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processes the raw data into the payload format.

        Args:
            data (Dict[str, Any]): The raw data from Quandl API.

        Returns:
            Dict[str, Any]: The processed payload.
        """
        dataset = data["dataset"]
        latest_data = dataset["data"][0]

        return {
            "symbol": dataset["dataset_code"],
            "timestamp": latest_data[0],
            "price": float(latest_data[4]),
            "source": "Quandl",
            "data": {
                "open": float(latest_data[1]),
                "high": float(latest_data[2]),
                "low": float(latest_data[3]),
                "close": float(latest_data[4]),
                "volume": int(latest_data[5]),
            },
        }

    def _handle_success(self) -> None:
        """
        Tracks success metrics for polling and requests.
        """
        track_polling_metrics("success")
        track_request_metrics("success", source="Quandl")

    def _handle_failure(self, error: str) -> None:
        """
        Tracks failure metrics for polling and requests.

        Args:
            error (str): Error message or reason for failure.
        """
        track_polling_metrics("failure", error=error)
        track_request_metrics("failure", source="Quandl")
