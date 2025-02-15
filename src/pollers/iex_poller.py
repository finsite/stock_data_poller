# from typing import List, Dict, Any
# import os
# import json  # ✅ Explicitly importing JSON
# import pika
# import boto3

# from pollers.base_poller import BasePoller
# from utils.retry_request import retry_request
# from utils.validate_data import validate_data
# from utils.track_polling_metrics import track_polling_metrics
# from utils.track_request_metrics import track_request_metrics
# from utils.request_with_timeout import request_with_timeout
# from utils.validate_environment_variables import validate_environment_variables
# from utils.rate_limit import RateLimiter  # ✅ Added RateLimiter

# # ✅ Initialize RateLimiter (Throttle requests)
# RATE_LIMIT = int(os.getenv("IEX_FILL_RATE_LIMIT", 100))
# rate_limiter = RateLimiter(max_requests=RATE_LIMIT, time_window=60)


# class IEXPoller(BasePoller):
#     """
#     Poller for fetching stock quotes from the IEX Cloud API.
#     """

#     def __init__(self, api_key: str):
#         """
#         Initializes the IEXPoller.

#         Args:
#             api_key (str): API key for accessing the IEX Cloud API.
#         """
#         super().__init__()

#         # Validate required environment variables
#         validate_environment_variables(["QUEUE_TYPE", "IEX_API_KEY", "RABBITMQ_HOST", "RABBITMQ_EXCHANGE", "RABBITMQ_ROUTING_KEY"])

#         self.api_key = api_key

#     def poll(self, symbols: List[str]) -> None:
#         """
#         Polls data for the specified symbols from IEX Cloud API.

#         Args:
#             symbols (List[str]): List of stock symbols to poll.
#         """
#         for symbol in symbols:
#             try:
#                 rate_limiter.acquire(context=f"IEX - {symbol}")  # ✅ Apply rate limiting
                
#                 # Fetch data from IEX Cloud API
#                 data = self._fetch_data(symbol)
#                 if not data:
#                     continue

#                 # Process and validate the payload
#                 payload = self._process_data(data)
#                 if not validate_data(payload):
#                     self._handle_failure(f"Validation failed for symbol: {symbol}")
#                     continue

#                 # Send payload to the queue (RabbitMQ or SQS)
#                 self.send_to_queue(payload)

#                 # Track success metrics
#                 self._handle_success()

#             except Exception as e:
#                 self._handle_failure(str(e))

#     def _fetch_data(self, symbol: str) -> Dict[str, Any]:
#         """
#         Fetches stock data for the given symbol from IEX Cloud API.

#         Args:
#             symbol (str): The stock symbol to fetch data for.

#         Returns:
#             Dict[str, Any]: The JSON response from IEX Cloud API.
#         """
#         try:
#             def request_func():
#                 url = f"https://cloud.iexapis.com/stable/stock/{symbol}/quote?token={self.api_key}"
#                 return request_with_timeout("GET", url)

#             data = retry_request(request_func)

#             if not data or "latestPrice" not in data:
#                 track_request_metrics("failure", source="IEX")
#                 return None

#             return data
#         except Exception as e:
#             self._handle_failure(f"Error fetching data for {symbol}: {e}")
#             return None

#     def _process_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
#         """
#         Processes the raw data into the payload format.

#         Args:
#             data (Dict[str, Any]): The raw data from IEX Cloud API.

#         Returns:
#             Dict[str, Any]: The processed payload.
#         """
#         return {
#             "symbol": data.get("symbol", "N/A"),
#             "timestamp": data.get("latestUpdate", None),
#             "price": float(data.get("latestPrice", 0.0)),
#             "source": "IEX",
#             "data": {
#                 "open": float(data.get("open", 0.0)),  # Default to 0 if not provided
#                 "high": float(data.get("high", 0.0)),
#                 "low": float(data.get("low", 0.0)),
#                 "close": float(data.get("latestPrice", 0.0)),
#                 "volume": int(data.get("volume", 0)),  # Default to 0 if not provided
#             },
#         }

#     def _handle_success(self) -> None:
#         """
#         Tracks success metrics for polling and requests.
#         """
#         track_polling_metrics("success")
#         track_request_metrics("success", source="IEX")

#     def _handle_failure(self, error: str) -> None:
#         """
#         Tracks failure metrics for polling and requests.

#         Args:
#             error (str): Error message or reason for failure.
#         """
#         track_polling_metrics("failure", error=error)
#         track_request_metrics("failure", source="IEX")

#     def send_to_queue(self, payload: Dict[str, Any]) -> None:
#         """
#         Sends the payload to the appropriate queue system (RabbitMQ or SQS).
#         """
#         queue_type = os.getenv("QUEUE_TYPE", "rabbitmq")

#         if queue_type == "rabbitmq":
#             self.send_to_rabbitmq(payload)
#         elif queue_type == "sqs":
#             self.send_to_sqs(payload)
#         else:
#             raise ValueError(f"Unsupported QUEUE_TYPE: {queue_type}")

#     def send_to_rabbitmq(self, payload: Dict[str, Any]) -> None:
#         """
#         Sends the payload to a RabbitMQ exchange.
#         """
#         try:
#             rabbitmq_host = os.getenv("RABBITMQ_HOST", "localhost")
#             rabbitmq_exchange = os.getenv("RABBITMQ_EXCHANGE", "stock_data_exchange")
#             rabbitmq_routing_key = os.getenv("RABBITMQ_ROUTING_KEY", "stock_data")

#             # ✅ Reuse the connection
#             if not hasattr(self, "connection") or self.connection.is_closed:
#                 self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
#                 self.channel = self.connection.channel()
#                 self.channel.exchange_declare(exchange=rabbitmq_exchange, exchange_type='direct')

#             # Publish the message to RabbitMQ exchange
#             message_body = json.dumps(payload)
#             self.channel.basic_publish(
#                 exchange=rabbitmq_exchange,
#                 routing_key=rabbitmq_routing_key,
#                 body=message_body
#             )
#             print(f"✅ Sent data to RabbitMQ exchange `{rabbitmq_exchange}` with routing key `{rabbitmq_routing_key}`")

#         except Exception as e:
#             print(f"❌ Error sending data to RabbitMQ: {str(e)}")

#     def send_to_sqs(self, payload: Dict[str, Any]) -> None:
#         """
#         Sends the payload to an SQS queue.
#         """
#         try:
#             sqs = boto3.client('sqs')
#             sqs_queue_url = os.getenv("SQS_QUEUE_URL")

#             if not sqs_queue_url:
#                 raise ValueError("❌ SQS_QUEUE_URL is not set in environment variables.")

#             # Send the message to SQS
#             message_body = json.dumps(payload)
#             sqs.send_message(QueueUrl=sqs_queue_url, MessageBody=message_body)
#             print(f"✅ Sent data to SQS queue: {sqs_queue_url}")

#         except Exception as e:
#             print(f"❌ Error sending data to SQS: {str(e)}")
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
    RATE_LIMIT, IEX_API_KEY, QUEUE_TYPE,
    RABBITMQ_HOST, RABBITMQ_EXCHANGE, RABBITMQ_ROUTING_KEY, SQS_QUEUE_URL
)

# Initialize logger
logger = setup_logger(__name__)

class IEXPoller(BasePoller):
    """
    Poller for fetching stock quotes from the IEX Cloud API.
    """

    def __init__(self):
        """
        Initializes the IEXPoller.
        """
        super().__init__()

        # Validate required environment variables
        validate_environment_variables([
            "QUEUE_TYPE", "IEX_API_KEY", "RABBITMQ_HOST", "RABBITMQ_EXCHANGE", "RABBITMQ_ROUTING_KEY"
        ])

        # Use IEX_API_KEY from config
        self.api_key = IEX_API_KEY

        # Use RATE_LIMIT from config instead of hardcoding
        self.rate_limiter = RateLimiter(max_requests=RATE_LIMIT, time_window=60)

    def poll(self, symbols: List[str]) -> None:
        """
        Polls data for the specified symbols from IEX Cloud API.

        Args:
            symbols (List[str]): List of stock symbols to poll.
        """
        for symbol in symbols:
            try:
                self._enforce_rate_limit()
                data = self._fetch_data(symbol)

                if not data or "latestPrice" not in data:
                    self._handle_failure(f"No data or missing price for symbol: {symbol}")
                    continue

                payload = self._process_data(symbol, data)

                if not validate_data(payload):
                    self._handle_failure(f"Validation failed for symbol: {symbol}")
                    continue

                # Track polling & request metrics
                track_polling_metrics("IEX", [symbol])
                track_request_metrics(symbol, 30, 5)

                self.send_to_queue(payload)
                self._handle_success()

            except Exception as e:
                self._handle_failure(str(e))

    def _enforce_rate_limit(self) -> None:
        """
        Enforces the rate limit using the RateLimiter class.
        """
        self.rate_limiter.acquire(context="IEX")

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

            return retry_request(request_func)
        except Exception as e:
            self._handle_failure(f"Error fetching data for {symbol}: {e}")
            return {}

    def _process_data(self, symbol: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processes the raw data into the payload format.

        Args:
            symbol (str): The stock symbol.
            data (Dict[str, Any]): The raw data from IEX Cloud API.

        Returns:
            Dict[str, Any]: The processed payload.
        """
        return {
            "symbol": data.get("symbol", "N/A"),
            "timestamp": data.get("latestUpdate", None),
            "price": float(data.get("latestPrice", 0.0)),
            "source": "IEX",
            "data": {
                "open": float(data.get("open", 0.0)),  # Default to 0 if not provided
                "high": float(data.get("high", 0.0)),
                "low": float(data.get("low", 0.0)),
                "close": float(data.get("latestPrice", 0.0)),
                "volume": int(data.get("volume", 0)),  # Default to 0 if not provided
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
        track_request_metrics("success", source="IEX")

    def _handle_failure(self, error: str) -> None:
        """
        Tracks failure metrics for polling and requests.

        Args:
            error (str): Error message or reason for failure.
        """
        track_polling_metrics("failure", error=error)
        track_request_metrics("failure", source="IEX")
        logger.error(f"Polling error: {error}")
