"""Poller for fetching stock data from AlphaVantage API.

The AlphaVantagePoller class fetches the daily data for the given symbols from the
AlphaVantage API and sends it to the message queue.

The poller enforces a rate limit of 5 requests per minute, per symbol.
"""

from typing import Any

from src.config import get_alpha_vantage_api_key  # AlphaVantage API key
from src.config import get_queue_type  # Message queue type (RabbitMQ or SQS)
from src.config import (
    get_rabbitmq_exchange,  # RabbitMQ exchange name (if RabbitMQ is used)
)
from src.config import (
    get_rabbitmq_host,  # RabbitMQ server hostname (if RabbitMQ is used)
)
from src.config import (
    get_rabbitmq_routing_key,  # RabbitMQ routing key (if RabbitMQ is used)
)
from src.config import get_rate_limit  # Maximum number of requests per second
from src.config import get_sqs_queue_url  # SQS queue URL (if SQS is used)
from src.message_queue.queue_sender import QueueSender  # Message queue sender
from src.pollers.base_poller import BasePoller  # Base poller class
from src.utils.rate_limit import RateLimiter  # Rate limiter class
from src.utils.request_with_timeout import request_with_timeout  # Request with timeout
from src.utils.retry_request import retry_request  # Retry request
from src.utils.setup_logger import setup_logger  # Logger setup
from src.utils.track_polling_metrics import (
    track_polling_metrics,  # Track polling metrics
)
from src.utils.track_request_metrics import (
    track_request_metrics,  # Track request metrics
)
from src.utils.validate_data import validate_data  # Validate data

logger = setup_logger(__name__)


class AlphaVantagePoller(BasePoller):
    """Poller for fetching stock data from AlphaVantage API."""

    def __init__(self):
        """Initializes the AlphaVantagePoller."""
        super().__init__()

        self.api_key = get_alpha_vantage_api_key()
        if not self.api_key:
            raise ValueError("Missing ALPHA_VANTAGE_API_KEY.")

        self.rate_limiter = RateLimiter(max_requests=get_rate_limit(), time_window=60)

        self.queue_sender = QueueSender(
            queue_type=get_queue_type(),
            rabbitmq_host=get_rabbitmq_host(),
            rabbitmq_exchange=get_rabbitmq_exchange(),
            rabbitmq_routing_key=get_rabbitmq_routing_key(),
            sqs_queue_url=get_sqs_queue_url(),
        )

    def poll(self, symbols: list[str]) -> None:
        """Polls data for the specified symbols from AlphaVantage API."""
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
                    self._handle_failure(symbol, f"Validation failed for symbol: {symbol}")
                    continue

                track_polling_metrics("AlphaVantage", [symbol])
                track_request_metrics(symbol, 30, 5)

                self.queue_sender.send_message(payload)
                self._handle_success(symbol)

            except Exception as e:
                self._handle_failure(symbol, str(e))

    def _enforce_rate_limit(self) -> None:
        """Enforces the rate limit using the RateLimiter class."""
        self.rate_limiter.acquire(context="AlphaVantage")

    def _fetch_data(self, symbol: str) -> dict[str, Any]:
        """Fetches data for the given symbol from AlphaVantage API."""

        def request_func():
            url = (
                f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY"
                f"&symbol={symbol}&interval=5min&apikey={self.api_key}"
            )
            return request_with_timeout(url)

        return retry_request(request_func)

    def _process_data(self, symbol: str, data: dict[str, Any]) -> dict[str, Any]:
        """Processes the latest time series data into a payload."""
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
        """Tracks failure metrics for polling and requests."""
        logger.error(f"AlphaVantage poll failed for {symbol}: {error}")
        track_polling_metrics("AlphaVantage", [symbol])
        track_request_metrics(symbol, 30, 5, success=False)
