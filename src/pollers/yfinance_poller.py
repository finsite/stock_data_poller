from typing import List, Dict, Any
from src.pollers.base_poller import BasePoller
from src.utils.retry_request import retry_request
from src.utils.track_polling_metrics import track_polling_metrics
from src.utils.track_request_metrics import track_request_metrics
from src.utils.validate_data import validate_data
from src.utils.validate_environment_variables import validate_environment_variables
import yfinance as yf


class YFinancePoller(BasePoller):
    """
    Poller for fetching stock data from Yahoo Finance (yfinance).
    """

    def __init__(self):
        """
        Initializes the YFinancePoller.
        """
        super().__init__()
        validate_environment_variables(["SQS_QUEUE_URL"])  # Ensure required variables are set

    def poll(self, symbols: List[str]) -> None:
        """
        Polls data for the specified symbols from Yahoo Finance.

        Args:
            symbols (List[str]): List of stock symbols to poll.
        """
        for symbol in symbols:
            try:
                # Fetch data using yfinance
                latest_data = self._fetch_data(symbol)
                if not latest_data:
                    continue

                # Process and validate the payload
                payload = self._process_data(symbol, latest_data)
                if not validate_data(payload):
                    self._handle_failure(f"Validation failed for symbol: {symbol}")
                    continue

                # Send payload to the queue
                self.send_to_queue(payload)

                # Track success metrics
                self._handle_success()

            except Exception as e:
                self._handle_failure(str(e))

    def _fetch_data(self, symbol: str) -> Any:
        """
        Fetches the latest stock data for the given symbol using yfinance.

        Args:
            symbol (str): The stock symbol to fetch data for.

        Returns:
            Any: The latest row of historical stock data.
        """
        try:
            def fetch_data_func():
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="1d")
                if hist.empty:
                    raise ValueError(f"No data found for symbol: {symbol}")
                return hist.iloc[-1]

            return retry_request(fetch_data_func)
        except Exception as e:
            self._handle_failure(f"Error fetching data for {symbol}: {e}")
            return None

    def _process_data(self, symbol: str, latest_data: Any) -> Dict[str, Any]:
        """
        Processes the raw data into the payload format.

        Args:
            symbol (str): The stock symbol.
            latest_data (Any): The latest row of historical stock data.

        Returns:
            Dict[str, Any]: The processed payload.
        """
        return {
            "symbol": symbol,
            "timestamp": latest_data.name.isoformat(),
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

    def _handle_success(self) -> None:
        """
        Tracks success metrics for polling and requests.
        """
        track_polling_metrics("success")
        track_request_metrics("success", source="YFinance")

    def _handle_failure(self, error: str) -> None:
        """
        Tracks failure metrics for polling and requests.

        Args:
            error (str): Error message or reason for failure.
        """
        track_polling_metrics("failure", error=error)
        track_request_metrics("failure", source="YFinance")
