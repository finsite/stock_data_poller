# import time
# import os
# import json
# import pika
# import boto3
# from typing import List, Dict, Any
# from pollers.base_poller import BasePoller
# from utils.request_with_timeout import request_with_timeout
# from utils.retry_request import retry_request
# from utils.track_polling_metrics import track_polling_metrics  # ✅ Added
# from utils.track_request_metrics import track_request_metrics  # ✅ Added
# from utils.validate_data import validate_data
# from utils.validate_environment_variables import validate_environment_variables
# from utils.rate_limit import RateLimiter
# from utils.setup_logger import setup_logger
# from config import (
#     RATE_LIMIT, ALPHA_VANTAGE_API_KEY, QUEUE_TYPE,
#     RABBITMQ_HOST, RABBITMQ_EXCHANGE, RABBITMQ_ROUTING_KEY, SQS_QUEUE_URL
# )

# logger = setup_logger(__name__)


# class AlphaVantagePoller(BasePoller):
#     """
#     Poller for AlphaVantage API.
#     """

#     def __init__(self):
#         super().__init__()

#         # ✅ Use ALPHA_VANTAGE_API_KEY from config (Vault)
#         self.api_key = ALPHA_VANTAGE_API_KEY

#         # ✅ Use RATE_LIMIT from config instead of hardcoding
#         self.rate_limiter = RateLimiter(max_requests=RATE_LIMIT, time_window=60)

#     def poll(self, symbols: List[str]) -> None:
#         """
#         Polls data for the specified symbols from AlphaVantage.
#         """
#         for symbol in symbols:
#             try:
#                 self._enforce_rate_limit()
#                 data = self._fetch_data(symbol)

#                 if "Error Message" in data:
#                     self._handle_failure("Error Message from AlphaVantage")
#                     continue

#                 payload = self._process_data(symbol, data)

#                 if not validate_data(payload):
#                     self._handle_failure(f"Validation failed for symbol: {symbol}")
#                     continue

#                 # ✅ Track polling & request metrics
#                 track_polling_metrics("AlphaVantage", [symbol])
#                 track_request_metrics(symbol, 30, 5)

#                 self.send_to_queue(payload)
#                 self._handle_success()

#             except Exception as e:
#                 self._handle_failure(str(e))

#     def _enforce_rate_limit(self) -> None:
#         """
#         Enforces the rate limit using the RateLimiter class.
#         """
#         self.rate_limiter.acquire(context="AlphaVantage")

#     def _fetch_data(self, symbol: str) -> Dict[str, Any]:
#         """
#         Fetches data for the given symbol from AlphaVantage.
#         """
#         def request_func():
#             url = (
#                 f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY"
#                 f"&symbol={symbol}&interval=5min&apikey={self.api_key}"
#             )
#             return request_with_timeout(url)

#         return retry_request(request_func)

#     def _process_data(self, symbol: str, data: Dict[str, Any]) -> Dict[str, Any]:
#         """
#         Processes the latest time series data into a payload.
#         """
#         time_series = data.get("Time Series (5min)")
#         if not time_series:
#             raise ValueError(f"No 'Time Series (5min)' data found for symbol: {symbol}")

#         latest_time = max(time_series.keys())
#         latest_data = time_series[latest_time]

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

#     def send_to_queue(self, payload: Dict[str, Any]) -> None:
#         """
#         Sends the payload to the appropriate queue system (RabbitMQ or SQS).
#         """
#         if QUEUE_TYPE == "rabbitmq":
#             self.send_to_rabbitmq(payload)
#         elif QUEUE_TYPE == "sqs":
#             self.send_to_sqs(payload)
#         else:
#             raise ValueError(f"Unsupported QUEUE_TYPE: {QUEUE_TYPE}")

#     def send_to_rabbitmq(self, payload: Dict[str, Any]) -> None:
#         """
#         Sends the payload to a RabbitMQ exchange.
#         """
#         try:
#             connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
#             channel = connection.channel()
#             channel.exchange_declare(exchange=RABBITMQ_EXCHANGE, exchange_type='direct')

#             message_body = json.dumps(payload)
#             channel.basic_publish(
#                 exchange=RABBITMQ_EXCHANGE,
#                 routing_key=RABBITMQ_ROUTING_KEY,
#                 body=message_body
#             )
#             logger.info(f"Sent data to RabbitMQ exchange {RABBITMQ_EXCHANGE} with routing key {RABBITMQ_ROUTING_KEY}")
#             connection.close()
#         except Exception as e:
#             logger.error(f"Error sending data to RabbitMQ: {str(e)}")

#     def send_to_sqs(self, payload: Dict[str, Any]) -> None:
#         """
#         Sends the payload to an SQS queue.
#         """
#         try:
#             sqs = boto3.client('sqs')
#             if not SQS_QUEUE_URL:
#                 raise ValueError("SQS_QUEUE_URL is not set in environment variables.")

#             message_body = json.dumps(payload)
#             sqs.send_message(QueueUrl=SQS_QUEUE_URL, MessageBody=message_body)
#             logger.info(f"Sent data to SQS queue: {SQS_QUEUE_URL}")
#         except Exception as e:
#             logger.error(f"Error sending data to SQS: {str(e)}")
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
from utils.rate_limit import RateLimiter
from utils.setup_logger import setup_logger
from message_queue.queue_sender import QueueSender  # ✅ Matches other pollers
from config import (
    RATE_LIMIT, ALPHA_VANTAGE_API_KEY, QUEUE_TYPE, RABBITMQ_HOST,
    RABBITMQ_EXCHANGE, RABBITMQ_ROUTING_KEY, SQS_QUEUE_URL
)

# ✅ Standard logging setup
logger = setup_logger(__name__)


class AlphaVantagePoller(BasePoller):
    """
    Poller for AlphaVantage API.
    """

    def __init__(self):
        super().__init__()

        # ✅ Validate environment variables (matches other pollers)
        validate_environment_variables([
            "QUEUE_TYPE",
            "ALPHA_VANTAGE_API_KEY",
            "RABBITMQ_HOST",
            "RABBITMQ_EXCHANGE",
            "RABBITMQ_ROUTING_KEY",
            "SQS_QUEUE_URL"
        ])

        self.api_key = ALPHA_VANTAGE_API_KEY
        self.rate_limiter = RateLimiter(max_requests=RATE_LIMIT, time_window=60)

        # ✅ Use the `QueueSender` like the other pollers
        self.queue_sender = QueueSender(
            queue_type=QUEUE_TYPE,
            rabbitmq_host=RABBITMQ_HOST,
            rabbitmq_exchange=RABBITMQ_EXCHANGE,
            rabbitmq_routing_key=RABBITMQ_ROUTING_KEY,
            sqs_queue_url=SQS_QUEUE_URL
        )

    def poll(self, symbols: List[str]) -> None:
        """
        Polls data for the specified symbols from AlphaVantage.
        """
        for symbol in symbols:
            try:
                self._enforce_rate_limit()
                data = self._fetch_data(symbol)

                if "Error Message" in data:
                    self._handle_failure(f"Error from AlphaVantage: {data['Error Message']}")
                    continue

                payload = self._process_data(symbol, data)

                if not validate_data(payload):
                    self._handle_failure(f"Validation failed for symbol: {symbol}")
                    continue

                # ✅ Track polling & request metrics (standardized)
                track_polling_metrics("AlphaVantage", [symbol])
                track_request_metrics(symbol, 30, 5)

                self.queue_sender.send_message(payload)  # ✅ Matches other pollers
                self._handle_success()

            except Exception as e:
                self._handle_failure(str(e))

    def _enforce_rate_limit(self) -> None:
        """Enforces the rate limit using the RateLimiter class."""
        self.rate_limiter.acquire(context="AlphaVantage")

    def _fetch_data(self, symbol: str) -> Dict[str, Any]:
        """Fetches data for the given symbol from AlphaVantage."""
        def request_func():
            url = (
                f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY"
                f"&symbol={symbol}&interval=5min&apikey={self.api_key}"
            )
            return request_with_timeout(url)

        return retry_request(request_func)

    def _process_data(self, symbol: str, data: Dict[str, Any]) -> Dict[str, Any]:
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

    def _handle_success(self) -> None:
        """Tracks success metrics for polling and requests."""
        track_polling_metrics("success")
        track_request_metrics("success", source="AlphaVantage")

    def _handle_failure(self, error: str) -> None:
        """Tracks failure metrics for polling and requests."""
        track_polling_metrics("failure", error=error)
        track_request_metrics("failure", source="AlphaVantage")
