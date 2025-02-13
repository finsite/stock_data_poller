from typing import List, Dict, Any
import os

from pollers.base_poller import BasePoller
from utils.retry_request import retry_request
from utils.validate_data import validate_data
from utils.track_polling_metrics import track_polling_metrics
from utils.track_request_metrics import track_request_metrics
from utils.request_with_timeout import request_with_timeout
from utils.validate_environment_variables import validate_environment_variables


class PolygonPoller(BasePoller):
    """
    Poller for fetching stock data from Polygon.io.
    """

    def __init__(self, api_key: str):
        """
        Initializes the PolygonPoller.

        Args:
            api_key (str): API key for accessing Polygon.io API.
        """
        super().__init__()

        # Validate environment variables for both RabbitMQ and SQS
        validate_environment_variables([
            "QUEUE_TYPE",
            "POLYGON_API_KEY",
            "RABBITMQ_HOST",
            "RABBITMQ_EXCHANGE",
            "RABBITMQ_ROUTING_KEY",
            "SQS_QUEUE_URL"
        ])

        self.api_key = api_key

    def poll(self, symbols: List[str]) -> None:
        """
        Polls data for the specified symbols from Polygon.io.

        Args:
            symbols (List[str]): List of stock symbols to poll.
        """
        for symbol in symbols:
            try:
                # Fetch data from Polygon API
                data = self._fetch_data(symbol)
                if not data:
                    continue

                # Process and validate the payload
                payload = self._process_data(data)
                if not validate_data(payload):
                    self._handle_failure(f"Validation failed for symbol: {symbol}")
                    continue

                # Send payload to the queue (RabbitMQ or SQS)
                self.send_to_queue(payload)

                # Track success metrics
                self._handle_success()

            except Exception as e:
                self._handle_failure(str(e))

    def _fetch_data(self, symbol: str) -> Dict[str, Any]:
        """
        Fetches stock data for the given symbol from Polygon.io.

        Args:
            symbol (str): The stock symbol to fetch data for.

        Returns:
            Dict[str, Any]: The JSON response from Polygon.io.
        """
        try:
            def request_func():
                url = f"https://api.polygon.io/v1/last/stocks/{symbol}?apiKey={self.api_key}"
                return request_with_timeout("GET", url)

            data = retry_request(request_func)

            if "status" not in data or data["status"] != "success":
                track_request_metrics("failure", source="Polygon")
                return None

            return data
        except Exception as e:
            self._handle_failure(f"Error fetching data for {symbol}: {e}")
            return None

    def _process_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processes the raw data into the payload format.

        Args:
            data (Dict[str, Any]): The raw data from Polygon.io.

        Returns:
            Dict[str, Any]: The processed payload.
        """
        return {
            "symbol": data["symbol"],
            "timestamp": data["last"]["timestamp"],
            "price": float(data["last"]["price"]),
            "source": "Polygon",
            "data": {
                "size": data["last"]["size"],
                "exchange": data["last"]["exchange"],
            },
        }

    def _handle_success(self) -> None:
        """
        Tracks success metrics for polling and requests.
        """
        track_polling_metrics("success")
        track_request_metrics("success", source="Polygon")

    def _handle_failure(self, error: str) -> None:
        """
        Tracks failure metrics for polling and requests.

        Args:
            error (str): Error message or reason for failure.
        """
        track_polling_metrics("failure", error=error)
        track_request_metrics("failure", source="Polygon")

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
        import pika
        try:
            rabbitmq_host = os.getenv("RABBITMQ_HOST", "localhost")
            rabbitmq_exchange = os.getenv("RABBITMQ_EXCHANGE", "stock_data_exchange")
            rabbitmq_routing_key = os.getenv("RABBITMQ_ROUTING_KEY", "stock_data")

            # Establish RabbitMQ connection and declare exchange
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
            channel = connection.channel()
            channel.exchange_declare(exchange=rabbitmq_exchange, exchange_type='direct')

            # Publish the message to RabbitMQ exchange
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
        import boto3
        try:
            sqs = boto3.client('sqs')
            sqs_queue_url = os.getenv("SQS_QUEUE_URL")

            if not sqs_queue_url:
                raise ValueError("SQS_QUEUE_URL is not set in environment variables.")

            # Send the message to SQS
            message_body = json.dumps(payload)
            sqs.send_message(QueueUrl=sqs_queue_url, MessageBody=message_body)
            logger.info(f"Sent data to SQS queue: {sqs_queue_url}")

        except Exception as e:
            logger.error(f"Error sending data to SQS: {str(e)}")
