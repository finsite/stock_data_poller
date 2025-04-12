"""
Base class for pollers that handles dynamic queue configuration and message sending.

This class provides a way to dynamically configure the queue based on environment
variables and provides a common interface for sending messages to the queue.

The class also provides methods for connecting to RabbitMQ and sending messages to the
queue.
"""

import json
from typing import Any

import pika

from src.config import (
    get_queue_type,  # Type of queue system, either "rabbitmq" or "sqs".
)
from src.config import get_rabbitmq_exchange  # RabbitMQ exchange name.
from src.config import get_rabbitmq_host  # RabbitMQ host.
from src.config import get_rabbitmq_routing_key  # RabbitMQ routing key.
from src.config import get_rate_limit  # Rate limit for API requests.
from src.config import get_sqs_queue_url  # AWS SQS queue URL.
from src.message_queue.queue_sender import (
    QueueSender,  # Class for sending messages to the queue.
)
from src.utils.rate_limit import RateLimiter  # Class for rate limiting API requests.
from src.utils.setup_logger import setup_logger  # Function for setting up the logger.
from src.utils.validate_environment_variables import (  # Function for validating environment variables.
    validate_environment_variables,
)

# Initialize logger
logger = setup_logger(__name__)


class BasePoller:
    """Base class for pollers that handles dynamic queue configuration and message
    sending."""

    def __init__(self) -> None:
        """
        Initializes the BasePoller with dynamic queue configuration based on environment
        variables.

        This method first validates the required environment variables for both RabbitMQ
        and SQS. Then, it initializes the QueueSender based on the environment variable
        QUEUE_TYPE, which can either be "rabbitmq" or "sqs". Finally, it also initializes
        the Rate Limiter to enforce the API rate limits.

        Raises
        ------
            ValueError: If the queue type is invalid.
        """
        # Validate required environment variables for both RabbitMQ and SQS
        required_env_vars: list[str] = [
            "QUEUE_TYPE",
            "RABBITMQ_HOST",
            "RABBITMQ_EXCHANGE",
            "RABBITMQ_ROUTING_KEY",
        ]
        validate_environment_variables(required_env_vars)

        self.queue_type: str = get_queue_type().lower()
        if self.queue_type not in {"rabbitmq", "sqs"}:
            logger.error("QUEUE_TYPE must be either 'sqs' or 'rabbitmq'.")
            raise ValueError("QUEUE_TYPE must be either 'sqs' or 'rabbitmq'.")

        # Initialize QueueSender based on the queue type
        self.queue_sender: QueueSender = QueueSender(
            queue_type=self.queue_type,
            rabbitmq_host=get_rabbitmq_host(),
            rabbitmq_exchange=get_rabbitmq_exchange(),
            rabbitmq_routing_key=get_rabbitmq_routing_key(),
            sqs_queue_url=get_sqs_queue_url(),
        )

        # Initialize Rate Limiter (Apply API Rate Limits)
        self.rate_limiter: RateLimiter = RateLimiter(max_requests=get_rate_limit(), time_window=60)

        # RabbitMQ-specific attributes (if RabbitMQ is used)
        self.connection: pika.BlockingConnection | None = None
        self.channel: pika.adapters.blocking_connection.BlockingChannel | None = None

    def connect_to_rabbitmq(self) -> None:
        """
        Establishes a connection to RabbitMQ and opens a channel for message publishing.

        This method will first check if the connection is closed or not. If it is,
        it will establish a new connection to RabbitMQ and open a new channel for
        message publishing. If the connection is already open, it will simply return
        without doing anything.

        Args:
            None

        Returns:
            None

        Raises:
        ------
            Exception: If the connection to RabbitMQ fails.
        """
        try:
            if not self.connection or self.connection.is_closed:
                self.connection = pika.BlockingConnection(
                    pika.ConnectionParameters(host=get_rabbitmq_host())
                )
                self.channel = self.connection.channel()
                self.channel.exchange_declare(
                    exchange=get_rabbitmq_exchange(), exchange_type="direct"
                )
                logger.info("Connected to RabbitMQ successfully.")
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            raise

    def send_to_queue(self, payload: dict[str, Any]) -> None:
        """
        Sends the processed payload to the configured queue (SQS or RabbitMQ).

        This method will first acquire a slot in the rate limiter and then send the message
        to the queue. If the queue type is RabbitMQ, it will connect to RabbitMQ and
        publish the message to the queue. If the queue type is SQS, it will use the
        QueueSender instance to send the message to the queue.

        Args:
        ----
            payload (Dict[str, Any]): The payload to be sent to the queue.

        Returns:
        -------
            None
        """
        try:
            # Acquire a slot in the rate limiter
            self.rate_limiter.acquire(context="QueueSender")

            # Send the message to the queue
            if self.queue_type == "rabbitmq":
                # Connect to RabbitMQ and publish the message to the queue
                self._send_to_rabbitmq(payload)
            else:
                # Use the QueueSender instance to send the message to the queue
                self._send_to_sqs(payload)
        except Exception as e:
            logger.error(f"Failed to send message to {self.queue_type} queue: {e}")
            raise

    def _send_to_rabbitmq(self, payload: dict[str, Any]) -> None:
        """
        Publishes the message to a RabbitMQ queue.

        This method will connect to RabbitMQ, declare a queue, and publish the message
        to the queue. If there is an error while sending the message, it will catch the
        exception and log the error.

        Args:
            payload (Dict[str, Any]): The message to be sent to the RabbitMQ queue.

        Returns:
            None

        Raises:
            Exception: If there is an error while sending the message to RabbitMQ.
        """
        try:
            self.connect_to_rabbitmq()

            # Declare a queue to store the messages
            queue_name = get_rabbitmq_exchange()
            self.channel.queue_declare(queue=queue_name, durable=True)

            # Publish the message to the queue
            self.channel.basic_publish(
                # Set the exchange and routing key
                exchange=get_rabbitmq_exchange(),
                routing_key=get_rabbitmq_routing_key(),
                # Set the message body
                body=json.dumps(payload),
                # Set the properties of the message
                properties=pika.BasicProperties(delivery_mode=2),  # Persistent messages
            )

            logger.info(f"Message successfully sent to RabbitMQ queue: {queue_name}.")
        except Exception as e:
            logger.error(f"Error while sending message to RabbitMQ: {e}")
            raise

    def _send_to_sqs(self, payload: dict[str, Any]) -> None:
        """
        Sends the message to the SQS queue using the QueueSender.

        This method delegates the task of sending the message to the SQS queue
        to the QueueSender instance. It logs the success or failure of the operation.

        Args:
            payload (Dict[str, Any]): The message payload to be sent to the SQS queue.

        Raises:
            Exception: If there is an error while sending the message to SQS.
        """
        try:
            # Send the message using QueueSender
            self.queue_sender.send_message(payload)  # type: ignore
            # Log successful message sending
            logger.info("Message successfully sent to SQS queue.")
        except Exception as e:
            # Log error if message sending fails
            logger.error(f"Error while sending message to SQS: {e}")
            raise

    def close_connection(self) -> None:
        """
        Closes the RabbitMQ connection if it exists.

        This method is used to clean up the resources used by the RabbitMQ connection.
        It is called when the object is no longer needed. It will close the connection
        if it exists and is open.

        Args:
            None

        Returns:
            None
        """
        if self.queue_type == "rabbitmq" and self.connection:
            try:
                # Close the connection if it exists and is open
                self.connection.close()
                logger.info("RabbitMQ connection closed.")
            except Exception as e:
                # Log an error if there is a problem while closing the connection
                logger.error(f"Failed to close RabbitMQ connection: {e}")
                raise
