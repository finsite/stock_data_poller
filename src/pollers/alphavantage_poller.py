import time
import os
import json
import pika
import boto3
from typing import List, Dict, Any
from pollers.base_poller import BasePoller
from utils.request_with_timeout import request_with_timeout
from utils.retry_request import retry_request
from utils.track_polling_metrics import track_polling_metrics
from utils.track_request_metrics import track_request_metrics
from utils.validate_data import validate_data
from utils.validate_environment_variables import validate_environment_variables
from utils.rate_limit import RateLimiter  # Corrected import
from utils.setup_logger import setup_logger

logger = setup_logger(__name__)


class AlphaVantagePoller(BasePoller):
    """
    Poller for AlphaVantage API.
    """

    def __init__(self, api_key: str):
        super().__init__()

        # Validate environment variables
        validate_environment_variables([
            "QUEUE_TYPE", "ALPHAVANTAGE_API_KEY", "RABBITMQ_HOST",
            "RABBITMQ_EXCHANGE", "RABBITMQ_ROUTING_KEY", "SQS_QUEUE_URL"
        ])

        self.api_key = api_key
        self.rate_limiter = RateLimiter(max_requests=5, time_window=60)  # Fixed rate limiter

    def poll(self, symbols: List[str]) -> None:
        """
        Polls data for the specified symbols from AlphaVantage.
        """
        for symbol in symbols:
            try:
                self._enforce_rate_limit()
                data = self._fetch_data(symbol)
                if "Error Message" in data:
                    self._handle_failure("Error Message from AlphaVantage")
                    continue

                payload = self._process_data(symbol, data)
                if not validate_data(payload):
                    self._handle_failure(f"Validation failed for symbol: {symbol}")
                    continue

                self.send_to_queue(payload)
                self._handle_success()

            except Exception as e:
                self._handle_failure(str(e))

    def _enforce_rate_limit(self) -> None:
        """
        Enforces the rate limit using the RateLimiter class.
        """
        self.rate_limiter.acquire(context="AlphaVantage")

    def _fetch_data(self, symbol: str) -> Dict[str, Any]:
        """
        Fetches data for the given symbol from AlphaVantage.
        """
        def request_func():
            url = (
                f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY"
                f"&symbol={symbol}&interval=5min&apikey={self.api_key}"
            )
            return request_with_timeout(url)

        return retry_request(request_func)

    def _process_data(self, symbol: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processes the latest time series data into a payload.
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

    def send_to_queue(self, payload: Dict[str, Any]) -> None:
        """
        Sends the payload to the appropriate queue system (RabbitMQ or SQS).
        """
        queue_type = os.getenv("QUEUE_TYPE", "rabbitmq")
        if queue_type == "rabbitmq":
            self.send_to_rabbitmq(payload)
        elif queue_type == "sqs":
            self.send_to_sqs(payload)
        else:
            raise ValueError(f"Unsupported QUEUE_TYPE: {queue_type}")

    def send_to_rabbitmq(self, payload: Dict[str, Any]) -> None:
        """
        Sends the payload to a RabbitMQ exchange.
        """
        try:
            rabbitmq_host = os.getenv("RABBITMQ_HOST", "localhost")
            rabbitmq_exchange = os.getenv("RABBITMQ_EXCHANGE", "stock_data_exchange")
            rabbitmq_routing_key = os.getenv("RABBITMQ_ROUTING_KEY", "stock_data")

            connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
            channel = connection.channel()
            channel.exchange_declare(exchange=rabbitmq_exchange, exchange_type='direct')
            
            message_body = json.dumps(payload)
            channel.basic_publish(
                exchange=rabbitmq_exchange,
                routing_key=rabbitmq_routing_key,
                body=message_body
            )
            logger.info(f"Sent data to RabbitMQ exchange {rabbitmq_exchange} with routing key {rabbitmq_routing_key}")
            connection.close()
        except Exception as e:
            logger.error(f"Error sending data to RabbitMQ: {str(e)}")

    def send_to_sqs(self, payload: Dict[str, Any]) -> None:
        """
        Sends the payload to an SQS queue.
        """
        try:
            sqs = boto3.client('sqs')
            sqs_queue_url = os.getenv("SQS_QUEUE_URL")
            if not sqs_queue_url:
                raise ValueError("SQS_QUEUE_URL is not set in environment variables.")

            message_body = json.dumps(payload)
            sqs.send_message(QueueUrl=sqs_queue_url, MessageBody=message_body)
            logger.info(f"Sent data to SQS queue: {sqs_queue_url}")
        except Exception as e:
            logger.error(f"Error sending data to SQS: {str(e)}")
