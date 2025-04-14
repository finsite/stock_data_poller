"""
Poller for fetching stock quotes from Polygon.io API.

The poller fetches the previous close data for the given symbols from Polygon.io API and
sends it to the message queue.

The poller enforces a rate limit of 5 requests per minute, per symbol.
"""

from typing import Any

from src.config import get_polygon_api_key, get_polygon_fill_rate_limit
from src.pollers.base_poller import BasePoller
from src.utils.rate_limit import RateLimiter
from src.utils.request_with_timeout import request_with_timeout
from src.utils.retry_request import retry_request
from src.utils.setup_logger import setup_logger
from src.utils.track_polling_metrics import track_polling_metrics
from src.utils.track_request_metrics import track_request_metrics
from src.utils.validate_data import validate_data

# Logger setup
logger = setup_logger(__name__)


class PolygonPoller(BasePoller):
    """Poller for fetching stock quotes from Polygon.io API."""

    def __init__(self):
        """
        Initializes the PolygonPoller.

        The method fetches the API key from the environment variable POLYGON_API_KEY
        and initializes the rate limiter with the configured fill rate limit.

        Raises
        ------
            ValueError: If POLYGON_API_KEY is not set.
        """
        super().__init__()

        # Fetch the API key from the environment variable
        self.api_key = get_polygon_api_key()
        if not self.api_key:
            raise ValueError("Missing POLYGON_API_KEY.")

        # Initialize the rate limiter with the configured fill rate limit
        self.rate_limiter = RateLimiter(
            max_requests=get_polygon_fill_rate_limit(),
            time_window=60,
        )

    def poll(self, symbols: list[str]) -> None:
        """
        Polls data for the specified symbols from Polygon.io API.

        This method fetches the previous close data for the given symbols from
        Polygon.io API and sends it to the message queue.

        Args:
        ----
            symbols (list[str]): List of stock symbols to poll.

        Raises:
        ------
            Exception: If any error occurs during polling.
        """
        for symbol in symbols:
            try:
                # Enforce rate limit for the symbol
                self._enforce_rate_limit()

                # Fetch data from Polygon.io API
                data = self._fetch_data(symbol)

                # Check if data is valid
                if not data or "results" not in data:
                    self._handle_failure(
                        symbol, "Missing results in API response. Please check the API response."
                    )
                    continue

                # Process the data
                payload = self._process_data(symbol, data)

                # Validate the processed data
                if not validate_data(payload):
                    self._handle_failure(symbol, "Validation failed. Please check the data.")
                    continue

                # Track metrics for successful polling and request
                track_request_metrics(symbol, 30, 5)

                # Send the processed data to the message queue
                self.send_to_queue(payload)
                self._handle_success(symbol)

            except Exception as e:
                # Handle any exceptions and track the failure
                self._handle_failure(symbol, str(e))

    def _enforce_rate_limit(self) -> None:
        """
        Enforces the rate limit using the RateLimiter class.

        The rate limiter is configured to allow a maximum of 5 requests per minute per
        symbol.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        # Acquire permission to proceed with the request
        # If the rate limit is exceeded, the call will block until the limit
        # is replenished
        self.rate_limiter.acquire(context="Polygon")

    def _fetch_data(self, symbol: str) -> dict[str, Any]:
        """
        Fetches stock data for the given symbol from Polygon.io API.

        The API endpoint is the "previous close" endpoint which returns the
        latest available data for the given symbol.

        The API key is obtained from the environment variable
        POLYGON_API_KEY.

        If the request fails, the retry_request function is used to retry the
        request up to 3 times with a 5 second delay between retries.

        Returns
        -------
            dict[str, Any]: The fetched data in JSON format.
        """

        # Define the request function
        def request_func():
            """
            Makes a GET request to the Polygon.io API to fetch the previous close data
            for the given symbol.

            Returns
            -------
                dict[str, Any]: The JSON response from the API.
            """
            # Construct the URL with the API key
            url = (
                f"https://api.polygon.io/v2/aggs/ticker/{symbol}/prev?"
                f"adjusted=true&apiKey={self.api_key}"
            )
            # Make the request with a timeout
            return request_with_timeout("GET", url)

        # Retry the request up to 3 times with a 5 second delay between retries
        return retry_request(request_func)

    def _process_data(self, symbol: str, data: dict[str, Any]) -> dict[str, Any]:
        """
        Processes the raw data from Polygon.io API into the payload format.

        The raw data is a dictionary containing the results of the API call,
        which is a list of dictionaries. This method processes the first result
        in the list and returns the processed data in the payload format.

        The payload format is a dictionary with the following keys:

        * symbol (str): The stock symbol for which the data was fetched.
        * timestamp (int): The timestamp for which the data was fetched, in
          seconds since the epoch.
        * price (float): The price of the stock at the given timestamp.
        * source (str): The source of the data, which is "Polygon" for this
          poller.
        * data (dict): A dictionary containing the following keys:

          * open (float): The opening price of the stock at the given timestamp.
          * high (float): The highest price of the stock at the given timestamp.
          * low (float): The lowest price of the stock at the given timestamp.
          * close (float): The closing price of the stock at the given timestamp.
          * volume (int): The volume of the stock at the given timestamp.

        Args:
            symbol (str): The stock symbol for which the data was fetched.
            data (dict[str, Any]): The raw data from the API call.

        Returns:
            dict[str, Any]: The processed data in the payload format.
        """
        results = data["results"][0]  # Only one result for "previous close"

        return {
            "symbol": symbol,  # str
            "timestamp": int(results.get("t", 0) / 1000),  # int
            "price": float(results.get("c", 0.0) / 100),  # float
            "source": "Polygon",  # str
            "data": {
                "open": float(results.get("o", 0.0) / 100),  # float
                "high": float(results.get("h", 0.0) / 100),  # float
                "low": float(results.get("l", 0.0) / 100),  # float
                "close": float(results.get("c", 0.0) / 100),  # float
                "volume": int(results.get("v", 0)),  # int
            },
        }

    # def _handle_success(self, symbol: str) -> None:
    #     """
    #     Tracks success metrics for polling and requests.

    #     Metrics tracked include the source of the data (Polygon) and the symbol
    #     for which polling was performed.

    #     Args:
    #     ----
    #         symbol (str): The symbol for which polling was performed.

    #     Returns:
    #     -------
    #         None
    #     """
    #     # Track success metrics for polling and requests
    #     # Polygon is the source of the data for this poller
    #     track_polling_metrics("Polygon", [symbol])  # type: ignore
    #     # 30 requests per minute, 5 minute window
    #     track_request_metrics(symbol, 30, 5)  # type: ignore

    # def _handle_failure(self, symbol: str, error: str) -> None:
    #     """
    #     Tracks failure metrics for polling and requests.

    #     Metrics tracked include the source of the data (Polygon) and the symbol
    #     for which polling was performed. The error message is also logged.

    #     Args:
    #     ----
    #         symbol (str): The symbol for which polling was performed.
    #         error (str): The error message.

    #     Returns:
    #     -------
    #         None
    #     """
    #     # Track failure metrics for polling and requests
    #     track_polling_metrics("Polygon", [symbol])  # type: ignore
    #     # 30 requests per minute, 5 minute window, but failed
    #     track_request_metrics(symbol, 30, 5, success=False)  # type: ignore
    #     logger.error(f"Polygon polling error for {symbol}: {error}")
    def _handle_success(self, symbol: str) -> None:
        """
        Tracks success metrics for polling and requests.

        This function is called when the poller successfully fetches data for the given symbol.
        It tracks success metrics for polling and requests, including the source of the data
        (Polygon) and the symbol for which polling was performed.

        Parameters:
        symbol (str): The symbol for which polling was performed.

        Returns:
        -------
        None
        """
        # Track success metrics for polling and requests
        track_polling_metrics("success", "Polygon", symbol)
        # 30 requests per minute, 5 minute window
        track_request_metrics(symbol, 30, 5)

    def _handle_failure(self, symbol: str, error: str) -> None:
        """
        Tracks failure metrics for polling and requests.

        Metrics tracked include the source of the data (Polygon) and the symbol
        for which polling was performed. The error message is also logged.

        Parameters:
        symbol (str): The symbol for which polling was performed.
        error (str): The error message describing the failure.

        Returns:
        -------
        None
        """
        # Track failure metrics for polling and requests
        track_polling_metrics("failure", "Polygon", symbol)
        # 30 requests per minute, 5 minute window, but failed
        track_request_metrics(symbol, 30, 5, success=False)
        # Log the error message for debugging purposes
        logger.error(f"Polygon polling error for {symbol}: {error}")
