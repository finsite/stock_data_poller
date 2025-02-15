from typing import List, Dict, Any
import os
import json
import pika
import boto3

from pollers.base_poller import BasePoller
from utils.retry_request import retry_request
from utils.validate_data import validate_data
from utils.track_polling_metrics import track_polling_metrics
from utils.track_request_metrics import track_request_metrics
from utils.request_with_timeout import request_with_timeout
from utils.validate_environment_variables import validate_environment_variables
from utils.rate_limit import RateLimiter
from utils.setup_logger import setup_logger
from config import (
    RATE_LIMIT, FINNHUB_API_KEY, QUEUE_TYPE,
    RABBITMQ_HOST, RABBITMQ_EXCHANGE, RABBITMQ_ROUTING_KEY, SQS_QUEUE_URL
)

# Initialize logger
logger = setup_logger(__name__)

class FinnhubPoller(BasePoller):
    """
    Poller for fetching stock quotes from Finnhub API.
    """

    def __init__(self):
        """
        Initializes the FinnhubPoller.
        """
        super().__init__()

        # Validate required environment variables
        validate_environment_variables([
            "QUEUE_TYPE", "FINNHUB_API_KEY", "RABBITMQ_HOST", "RABBITMQ_EXCHANGE", "RABBITMQ_ROUTING_KEY"
        ])

        # Use FINNHUB_API_KEY from config
        self.api_key = FINNHUB_API_KEY

        # Use RATE_LIMIT from config instead of hardcoding
        self.rate_limiter = RateLimiter(max_requests=RATE_LIMIT, time_window=60)

    def poll(self, symbols: List[str]) -> None:
        """
        Polls data for the specified symbols from Finnhub.

        Args:
            symbols (List[str]): List of stock symbols to poll.
        """
        for symbol in symbols:
            try:
                self._enforce_rate_limit()
                data = self._fetch_data(symbol)

                if not data or "c" not in data:
                    self._handle_failure(f"No data or missing price for symbol: {symbol}")
                    continue

                payload = self._process_data(symbol, data)

                if not validate_data(payload):
                    self._handle_failure(f"Validation failed for symbol: {symbol}")
                    continue

                # Track polling & request metrics
                track_polling_metrics("Finnhub", [symbol])
                track_request_metrics(symbol, 30, 5)

                self.send_to_queue(payload)
                self._handle_success()

            except Exception as e:
                self._handle_failure(str(e))

    def _enforce_rate_limit(self) -> None:
        """
        Enforces the rate limit using the RateLimiter class.
        """
        self.rate_limiter.acquire(context="Finnhub")

    def _fetch_data(self, symbol: str) -> Dict[str, Any]:
        """
        Fetches stock data for the given symbol from Finnhub.

        Args:
            symbol (str): The stock symbol to fetch data for.

        Returns:
            Dict[str, Any]: The JSON response from Finnhub API.
        """
        try:
            def request_func():
                url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={self.api_key}"
                return request_with_timeout("GET", url)

            return retry_request(request_func)
        except Exception as e:
            self._handle_failure(f"Error fetching data for {symbol}: {e}")
            return {}

    def _process_data(self, symbol: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processes the raw data into the payload format.

        Args:
            symbol (str): The stock symbol.
            data (Dict[str, Any]): The raw data from Finnhub.

        Returns:
            Dict[str, Any]: The processed payload.
        """
        return {
            "symbol": symbol,
            "timestamp": None,  # Finnhub does not provide timestamps in quotes
            "price": float(data["c"]),
            "source": "Finnhub",
            "data": {
                "current": float(data["c"]),
                "high": float(data["h"]),
                "low": float(data["l"]),
                "open": float(data["o"]),
                "previous_close": float(data["pc"]),
            },
        }

    def send_to_queue(self, payload: Dict[str, Any]) -> None:
        """
        Sends the payload to the appropriate queue system (RabbitMQ or SQS).
        """
        if QUEUE_TYPE == "rabbitmq":
            self.send_to_rabbitmq(payload)
        elif QUEUE_TYPE == "sqs":
            self.send_to_sqs(payload)
        else:
            raise ValueError(f"Unsupported QUEUE_TYPE: {QUEUE_TYPE}")

    def send_to_rabbitmq(self, payload: Dict[str, Any]) -> None:
        """
        Sends the payload to a RabbitMQ exchange.
        """
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
            channel = connection.channel()
            channel.exchange_declare(exchange=RABBITMQ_EXCHANGE, exchange_type='direct')

            message_body = json.dumps(payload)
            channel.basic_publish(
                exchange=RABBITMQ_EXCHANGE,
                routing_key=RABBITMQ_ROUTING_KEY,
                body=message_body
            )
            logger.info(f"Sent data to RabbitMQ exchange {RABBITMQ_EXCHANGE} with routing key {RABBITMQ_ROUTING_KEY}")
            connection.close()
        except Exception as e:
            logger.error(f"Error sending data to RabbitMQ: {str(e)}")

    def send_to_sqs(self, payload: Dict[str, Any]) -> None:
        """
        Sends the payload to an SQS queue.
        """
        try:
            sqs = boto3.client('sqs')
            if not SQS_QUEUE_URL:
                raise ValueError("SQS_QUEUE_URL is not set in environment variables.")

            message_body = json.dumps(payload)
            sqs.send_message(QueueUrl=SQS_QUEUE_URL, MessageBody=message_body)
            logger.info(f"Sent data to SQS queue: {SQS_QUEUE_URL}")
        except Exception as e:
            logger.error(f"Error sending data to SQS: {str(e)}")

    def _handle_success(self) -> None:
        """
        Tracks success metrics for polling and requests.
        """
        track_polling_metrics("success")
        track_request_metrics("success", source="Finnhub")

    def _handle_failure(self, error: str) -> None:
        """
        Tracks failure metrics for polling and requests.

        Args:
            error (str): Error message or reason for failure.
        """
        track_polling_metrics("failure", error=error)
        track_request_metrics("failure", source="Finnhub")
        logger.error(f"Polling error: {error}")
