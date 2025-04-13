# """
# Poller for fetching stock data from AlphaVantage API.

# The AlphaVantagePoller class fetches the daily data for the given symbols from the
# AlphaVantage API and sends it to the message queue.

# The poller enforces a rate limit of 5 requests per minute, per symbol.
# """

# from typing import Any

# from src.config import get_alpha_vantage_api_key  # AlphaVantage API key
# from src.config import get_queue_type  # Message queue type (RabbitMQ or SQS)
# from src.config import (
#     get_rabbitmq_exchange,  # RabbitMQ exchange name (if RabbitMQ is used)
# )
# from src.config import (
#     get_rabbitmq_host,  # RabbitMQ server hostname (if RabbitMQ is used)
# )
# from src.config import (
#     get_rabbitmq_routing_key,  # RabbitMQ routing key (if RabbitMQ is used)
# )
# from src.config import get_rate_limit  # Maximum number of requests per second
# from src.config import get_alpha_vantage_fill_rate_limit
# from src.config import get_sqs_queue_url  # SQS queue URL (if SQS is used)
# from src.message_queue.queue_sender import QueueSender  # Message queue sender
# from src.pollers.base_poller import BasePoller  # Base poller class
# from src.utils.rate_limit import RateLimiter  # Rate limiter class
# from src.utils.request_with_timeout import request_with_timeout  # Request with timeout
# from src.utils.retry_request import retry_request  # Retry request
# from src.utils.setup_logger import setup_logger  # Logger setup
# from src.utils.track_polling_metrics import (
#     track_polling_metrics,  # Track polling metrics
# )
# from src.utils.track_request_metrics import (
#     track_request_metrics,  # Track request metrics
# )
# from src.utils.validate_data import validate_data  # Validate data

# logger = setup_logger(__name__)


# class AlphaVantagePoller(BasePoller):
#     """Poller for fetching stock data from AlphaVantage API."""

#     def __init__(self) -> None:
#         """
#         Initializes the AlphaVantagePoller.

#         The class takes the following environment variables:

#         - ALPHA_VANTAGE_API_KEY: str, The AlphaVantage API key.
#         - QUEUE_TYPE: str, The message queue type (RabbitMQ or SQS).
#         - RABBITMQ_HOST: str, The RabbitMQ server hostname (if RabbitMQ is used).
#         - RABBITMQ_EXCHANGE: str, The RabbitMQ exchange name (if RabbitMQ is used).
#         - RABBITMQ_ROUTING_KEY: str, The RabbitMQ routing key (if RabbitMQ is used).
#         - SQS_QUEUE_URL: str, The SQS queue URL (if SQS is used).
#         """
#         super().__init__()

#         # Get the AlphaVantage API key
#         self.api_key: str = get_alpha_vantage_api_key()
#         if not self.api_key:
#             raise ValueError("Missing ALPHA_VANTAGE_API_KEY.")

#         self.rate_limiter = RateLimiter(max_requests=get_alpha_vantage_fill_rate_limit(), time_window=60)
#         # Initialize rate limiter with configured limit
#         self.rate_limiter: RateLimiter = RateLimiter(max_requests=get_rate_limit(), time_window=60)

#         # Initialize queue sender with configured queue
#         self.queue_sender: QueueSender = QueueSender(
#             queue_type=get_queue_type(),
#             rabbitmq_host=get_rabbitmq_host(),
#             rabbitmq_exchange=get_rabbitmq_exchange(),
#             rabbitmq_routing_key=get_rabbitmq_routing_key(),
#             sqs_queue_url=get_sqs_queue_url(),
#         )

#     def poll(self, symbols: list[str]) -> None:
#         """
#         Polls data for the specified symbols from AlphaVantage API.

#         Args:
#             symbols (list[str]): The list of symbols to poll.

#         Returns:
#             None
#         """
#         for symbol in symbols:
#             try:
#                 # Enforce rate limit
#                 self._enforce_rate_limit()
#                 # Fetch data from AlphaVantage API
#                 data: dict[str, Any] = self._fetch_data(symbol)

#                 if "Error Message" in data:
#                     # Handle failure if the API returns an error message
#                     self._handle_failure(
#                         symbol, f"Error from AlphaVantage: {data['Error Message']}"
#                     )
#                     continue

#                 # Process data into payload
#                 payload: dict[str, Any] = self._process_data(symbol, data)

#                 if not validate_data(payload):
#                     # Handle failure if the data does not pass validation
#                     self._handle_failure(symbol, f"Validation failed for symbol: {symbol}")
#                     continue

#                 # Track metrics
#                 track_polling_metrics("AlphaVantage", [symbol])
#                 track_request_metrics(symbol, 30, 5)

#                 # Send payload to message queue
#                 self.queue_sender.send_message(payload)
#                 # Handle success
#                 self._handle_success(symbol)

#             except Exception as e:
#                 # Handle failure if an unexpected exception is raised
#                 self._handle_failure(symbol, str(e))

#     def _enforce_rate_limit(self) -> None:
#         """
#         Enforces the rate limit using the RateLimiter class.

#         The function acquires a token from the rate limiter and blocks until the
#         token is available. This ensures that the maximum number of requests per
#         minute is not exceeded.

#         Args:
#             None

#         Returns:
#             None
#         """
#         # Acquire a token from the rate limiter and block until the token is available
#         self.rate_limiter.acquire(context="AlphaVantage")  # type: ignore

#     def _fetch_data(self, symbol: str) -> dict[str, Any]:
#         """
#         Fetches data for the given symbol from AlphaVantage API.

#         The function makes a GET request to the AlphaVantage API and fetches the
#         intraday time series data for the given symbol. The request is made with a
#         timeout and the result is returned as a dictionary.

#         Args:
#             symbol (str): The symbol for which data is to be fetched.

#         Returns:
#             dict[str, Any]: The fetched data as a dictionary.
#         """

#         def request_func() -> dict[str, Any]:
#             """
#             Makes a GET request to the AlphaVantage API to fetch the intraday time
#             series data for the given symbol.

#             The request is made with the following parameters:
#             - function: TIME_SERIES_INTRADAY
#             - symbol: The symbol for which data is to be fetched (str)
#             - interval: 5min
#             - apikey: The AlphaVantage API key (str)

#             The function returns the fetched data as a dictionary (dict[str, Any]).

#             Returns:
#                 dict[str, Any]: The fetched data as a dictionary.
#             """
#             url = (
#                 f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY"
#                 f"&symbol={symbol}&interval=5min&apikey={self.api_key}"
#             )
#             return request_with_timeout(url)

#         return retry_request(request_func)

#     def _process_data(self, symbol: str, data: dict[str, Any]) -> dict[str, Any]:
#         """
#         Processes the latest time series data into a payload.

#         Parameters
#         ----------
#         symbol: str
#             The symbol for which polling was performed.
#         data: dict[str, Any]
#             The time series data from AlphaVantage.

#         Returns
#         -------
#         dict[str, Any]:
#             The processed payload dictionary.
#         """
#         time_series: dict[str, dict[str, str]] = data.get("Time Series (5min)")
#         if not time_series:
#             raise ValueError(f"No 'Time Series (5min)' data found for symbol: {symbol}")

#         # Determine the latest time in the time series
#         latest_time: str = max(time_series.keys())
#         latest_data: dict[str, str] = time_series[latest_time]

#         # Process the latest time series data into a payload
#         return {
#             "symbol": symbol,
#             "timestamp": latest_time,
#             "price": float(latest_data["4. close"]),
#             "source": "AlphaVantage",
#             "data": {
#                 "open": float(latest_data["1. open"]),
#                 "high": float(latest_data["2. high"]),
#                 "low": float(latest_data["3. low"]),
#                 "close": float(latest_data["4. close"]),
#                 "volume": int(latest_data["5. volume"]),
#             },
#         }

#     def _handle_success(self, symbol: str) -> None:
#         """
#         Tracks success metrics for polling and requests.

#         Metrics tracked include the source of the data (AlphaVantage) and the symbol
#         for which polling was performed.

#         Args:
#             symbol (str): The symbol for which polling was performed.

#         Returns:
#             None
#         """
#         # Track success metrics for polling and requests
#         track_polling_metrics("AlphaVantage", [symbol])
#         track_request_metrics(symbol, 30, 5)

#     def _handle_failure(self, symbol: str, error: str) -> None:
#         """
#         Tracks failure metrics for polling and requests.

#         Metrics tracked include the source of the data (AlphaVantage) and the symbol
#         for which polling was performed. The error message is also logged.

#         Args:
#             symbol (str): The symbol for which polling was performed.
#             error (str): The error message.

#         Returns:
#             None
#         """
#         logger.error(f"AlphaVantage poll failed for {symbol}: {error}")
#         # Track failure metrics for polling and requests
#         track_polling_metrics("AlphaVantage", [symbol])
#         track_request_metrics(symbol, 30, 5, success=False)
"""Poller for fetching stock data from AlphaVantage API.

The AlphaVantagePoller class fetches the daily data for the given symbols from the
AlphaVantage API and sends it to the message queue.

The poller enforces a per-minute rate limit using the configured environment or Vault
value.
"""

from typing import Any

from src.config import get_alpha_vantage_api_key, get_alpha_vantage_fill_rate_limit
from src.pollers.base_poller import BasePoller
from src.utils.rate_limit import RateLimiter
from src.utils.request_with_timeout import request_with_timeout
from src.utils.retry_request import retry_request
from src.utils.setup_logger import setup_logger
from src.utils.track_polling_metrics import track_polling_metrics
from src.utils.track_request_metrics import track_request_metrics
from src.utils.validate_data import validate_data

logger = setup_logger(__name__)


class AlphaVantagePoller(BasePoller):
    """Poller for fetching stock data from AlphaVantage API."""

    def __init__(self) -> None:
        """Initializes the AlphaVantagePoller with rate limit and API key."""
        super().__init__()

        self.api_key: str = get_alpha_vantage_api_key()
        if not self.api_key:
            raise ValueError("Missing ALPHA_VANTAGE_API_KEY.")

        self.rate_limiter = RateLimiter(
            max_requests=get_alpha_vantage_fill_rate_limit(), time_window=60
        )

    def poll(self, symbols: list[str]) -> None:
        """Polls data for the specified symbols from AlphaVantage API.

        Args:
        ----
            symbols (list[str]): The list of symbols to poll.

        """
        for symbol in symbols:
            try:
                self._enforce_rate_limit()
                data = self._fetch_data(symbol)

                if "Error Message" in data:
                    self._handle_failure(
                        symbol, f"Error from AlphaVantage: {data['Error Message']}"
                    )
                    continue

                payload = self._process_data(symbol, data)

                if not validate_data(payload):
                    self._handle_failure(symbol, "Validation failed.")
                    continue

                track_polling_metrics("AlphaVantage", [symbol])
                track_request_metrics(symbol, 30, 5)

                self.send_to_queue(payload)
                self._handle_success(symbol)

            except Exception as e:
                self._handle_failure(symbol, str(e))

    def _enforce_rate_limit(self) -> None:
        """Enforces the rate limit using the RateLimiter class."""
        self.rate_limiter.acquire(context="AlphaVantage")

    def _fetch_data(self, symbol: str) -> dict[str, Any]:
        """Fetches data for the given symbol from AlphaVantage API.

        Args:
        ----
            symbol (str): The stock symbol.

        Returns:
        -------
            dict[str, Any]: The fetched data from AlphaVantage.

        """

        def request_func() -> dict[str, Any]:
            url = (
                "https://www.alphavantage.co/query"
                f"?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=5min&apikey={self.api_key}"
            )
            return request_with_timeout(url)

        return retry_request(request_func)

    def _process_data(self, symbol: str, data: dict[str, Any]) -> dict[str, Any]:
        """Processes the latest time series data into a standardized payload.

        Args:
        ----
            symbol (str): Stock symbol.
            data (dict[str, Any]): Raw data from AlphaVantage.

        Returns:
        -------
            dict[str, Any]: Transformed payload.

        """
        time_series = data.get("Time Series (5min)")
        if not time_series:
            raise ValueError(f"No 'Time Series (5min)' data found for symbol: {symbol}")

        latest_time = max(time_series.keys())
        latest_data = time_series[latest_time]

        return {
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

    def _handle_success(self, symbol: str) -> None:
        """Tracks success metrics for polling and requests."""
        track_polling_metrics("AlphaVantage", [symbol])
        track_request_metrics(symbol, 30, 5)

    def _handle_failure(self, symbol: str, error: str) -> None:
        """Tracks failure metrics and logs the error."""
        logger.error(f"AlphaVantage poll failed for {symbol}: {error}")
        track_polling_metrics("AlphaVantage", [symbol])
        track_request_metrics(symbol, 30, 5, success=False)
