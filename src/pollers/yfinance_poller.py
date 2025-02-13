from typing import List, Dict, Any
from pollers.base_poller import BasePoller
from utils.retry_request import retry_request
from utils.track_polling_metrics import track_polling_metrics
from utils.track_request_metrics import track_request_metrics
from utils.validate_data import validate_data
from utils.validate_environment_variables import validate_environment_variables
import yfinance as yf
import os


class YFinancePoller(BasePoller):
    """
    Poller for fetching stock data from Yahoo Finance (yfinance).
    """

    def __init__(self):
        """
        Initializes the YFinancePoller.
        """
        super().__init__()
        # Validate environment variables needed for the queue system
        validate_environment_variables(["QUEUE_TYPE", "RABBITMQ_HOST", "RABBITMQ_EXCHANGE", "RABBITMQ_ROUTING_KEY", "SQS_QUEUE_URL"])

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

                # Send payload to the appropriate queue (RabbitMQ or SQS)
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
