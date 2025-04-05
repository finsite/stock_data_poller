"""QueueSender class for message delivery to RabbitMQ or SQS.

The class offers an interface for dispatching messages to either a RabbitMQ or SQS
queue. It is configurable to support both RabbitMQ and SQS systems, allowing selection
between them.

Additionally, this class includes methods for closing connections to the configured
queue.
"""

import json
import boto3
import pika

from typing import Dict, Any
from src.utils.setup_logger import setup_logger

# Set up logger
logger = setup_logger(__name__)


class QueueSender:
    """A class for sending messages to a RabbitMQ or SQS queue.

    The class provides an interface for sending messages to a RabbitMQ or SQS queue. It
    supports both RabbitMQ and SQS, and it can be configured to use either one or the
    other.

    The class also provides methods for closing the connection to the queue.
    """

    def __init__(
        self,
        queue_type: str,  # Type of queue system, either "rabbitmq" or "sqs".
        rabbitmq_host: str = None,  # RabbitMQ host.
        rabbitmq_exchange: str = None,  # RabbitMQ exchange name.
        rabbitmq_routing_key: str = None,  # RabbitMQ routing key.
        sqs_queue_url: str = None,  # AWS SQS queue URL.
    ) -> None:
        """Initializes the QueueSender for RabbitMQ or SQS.

        The QueueSender class is a utility for sending messages to either a RabbitMQ
        or an SQS queue. It supports both RabbitMQ and SQS, and it can be
        configured to use either one or the other.

        Args:
        ----
            queue_type (str): Type of queue system, either "rabbitmq" or "sqs".
            rabbitmq_host (str): RabbitMQ host. Defaults to None.
            rabbitmq_exchange (str): RabbitMQ exchange name. Defaults to None.
            rabbitmq_routing_key (str): RabbitMQ routing key. Defaults to None.
            sqs_queue_url (str): AWS SQS queue URL. Defaults to None.

        Raises:
        ------
            ValueError: If the queue type is invalid.

        """
        self.queue_type = queue_type.lower()
        self.rabbitmq_host = rabbitmq_host
        self.rabbitmq_exchange = rabbitmq_exchange
        self.rabbitmq_routing_key = rabbitmq_routing_key
        self.sqs_queue_url = sqs_queue_url

        if self.queue_type == "rabbitmq":
            try:
                # Establish a connection to RabbitMQ
                self.connection = pika.BlockingConnection(
                    pika.ConnectionParameters(host=self.rabbitmq_host)
                )
                self.channel = self.connection.channel()
                # Declare the RabbitMQ exchange
                self.channel.exchange_declare(
                    exchange=self.rabbitmq_exchange, exchange_type="direct"
                )
                logger.info(f"Connected to RabbitMQ on {self.rabbitmq_host}")
            except Exception as e:
                logger.error(f"Failed to connect to RabbitMQ: {e}")
                raise

        elif self.queue_type == "sqs":
            try:
                # Initialize the SQS client
                self.sqs = boto3.client("sqs")
                logger.info("SQS client initialized.")
            except Exception as e:
                logger.error(f"Failed to initialize SQS client: {e}")
                raise

        else:
            raise ValueError(f"Unsupported queue type: {self.queue_type}")

    def send_message(self, data: dict) -> None:
        """Sends a message to the configured queue.

        The method will first acquire a slot in the rate limiter and then send the message
        to the queue.

        Args:
        ----
            data (dict): The message payload.

        Raises:
        ------
            Exception: If the message could not be sent to the queue.

        """
        try:
            if self.queue_type == "rabbitmq":
                self._send_to_rabbitmq(data)  # type: ignore
            elif self.queue_type == "sqs":
                self._send_to_sqs(data)  # type: ignore
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            raise

    def _send_to_rabbitmq(self, data: dict) -> None:
        """Sends a message to a RabbitMQ queue.

        This method serializes the given data into JSON format and publishes
        it to a specified RabbitMQ exchange using the provided routing key.

        Args:
        ----
            data (dict): The message payload to be sent, as a dictionary.

        Raises:
        ------
            Exception: If there is an error while sending the message.

        """
        try:
            message_body: str = json.dumps(data)  # Convert the data dictionary to a JSON string

            self.channel.basic_publish(
                exchange=self.rabbitmq_exchange,  # Exchange to publish to
                routing_key=self.rabbitmq_routing_key,  # Routing key for the message
                body=message_body,  # The message body
            )

            logger.info(
                f"Message sent to RabbitMQ exchange `{self.rabbitmq_exchange}` with routing key `{self.rabbitmq_routing_key}`"
            )
        except Exception as e:
            logger.error(f"Error sending to RabbitMQ: {e}")
            raise

    def _send_to_sqs(self, data: Dict[str, Any]) -> None:
        """Sends a message to an SQS queue.

        Args:
        ----
            data (Dict[str, Any]): The message payload to be sent, as a dictionary.

        Raises:
        ------
            ValueError: If the SQS queue URL is not set.
            Exception: If there is an error while sending the message.

        """
        try:
            # Check if the SQS queue URL is set
            if not self.sqs_queue_url:
                raise ValueError("SQS_QUEUE_URL is not configured.")

            # Convert the data dictionary to a JSON string
            message_body = json.dumps(data)

            # Send the message to the SQS queue
            self.sqs.send_message(QueueUrl=self.sqs_queue_url, MessageBody=message_body)

            # Log a message indicating that the message has been sent
            logger.info(f"Message sent to SQS queue: {self.sqs_queue_url}")
        except Exception as e:
            # Log an error if there is an issue while sending the message
            logger.error(f"Error sending to SQS: {e}")
            raise

    def close(self) -> None:
        """Closes the RabbitMQ connection if open.

        This method is used to clean up resources when the object is no longer
        needed. It closes the RabbitMQ connection if it is open.

        Args:
        ----
            None

        Returns:
        -------
            None

        Raises:
        ------
            Exception: If there is an error while closing the connection.

        """
        if self.queue_type == "rabbitmq":
            try:
                if self.connection and self.connection.is_open:
                    self.connection.close()
                    logger.info("RabbitMQ connection closed.")
            except Exception as e:
                logger.error(f"Failed to close RabbitMQ connection: {e}")
                raise
