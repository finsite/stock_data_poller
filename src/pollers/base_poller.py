"""Base class for pollers that handles dynamic queue configuration and message
sending.

This class provides a way to dynamically configure the queue based on
environment variables and provides a common interface for sending
messages to the queue.

The class also provides methods for connecting to RabbitMQ and sending
messages to the queue.
"""

import pika

from src.config import (
    get_queue_type,
    get_rabbitmq_exchange,
    get_rabbitmq_host,
    get_rabbitmq_routing_key,
    get_rate_limit,
    get_sqs_queue_url,
)
from src.message_queue.queue_sender import QueueSender
from src.utils.rate_limit import RateLimiter
from src.utils.setup_logger import setup_logger
from src.utils.validate_environment_variables import validate_environment_variables

# Initialize logger
logger = setup_logger(__name__)


class BasePoller:

    """Base class for pollers that handles dynamic queue configuration and
    message sending.
    """

    def __init__(self):
        """Initializes the BasePoller with dynamic queue configuration based on
        environment variables.

        Raises
        ------
            ValueError: If the queue type is invalid.

        """
        # Validate required environment variables for both RabbitMQ and SQS
        required_env_vars = [
            "QUEUE_TYPE",
            "RABBITMQ_HOST",
            "RABBITMQ_EXCHANGE",
            "RABBITMQ_ROUTING_KEY",
        ]
        validate_environment_variables(required_env_vars)

        self.queue_type = get_queue_type().lower()
        if self.queue_type not in {"rabbitmq", "sqs"}:
            logger.error("QUEUE_TYPE must be either 'sqs' or 'rabbitmq'.")
            raise ValueError("QUEUE_TYPE must be either 'sqs' or 'rabbitmq'.")

        # Initialize QueueSender based on the queue type
        self.queue_sender = QueueSender(
            queue_type=self.queue_type,
            rabbitmq_host=get_rabbitmq_host(),
            rabbitmq_exchange=get_rabbitmq_exchange(),
            rabbitmq_routing_key=get_rabbitmq_routing_key(),
            sqs_queue_url=get_sqs_queue_url(),
        )

        # Initialize Rate Limiter (Apply API Rate Limits)
        self.rate_limiter = RateLimiter(max_requests=get_rate_limit(), time_window=60)

        # RabbitMQ-specific attributes (if RabbitMQ is used)
        self.connection = None
        self.channel = None

    def connect_to_rabbitmq(self) -> None:
        """Establishes a connection to RabbitMQ and opens a channel for message
        publishing.
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

    def send_to_queue(self, payload: dict) -> None:
        """Sends the processed payload to the configured queue (SQS or
        RabbitMQ).

        This method will first acquire a slot in the rate limiter and then send the message
        to the queue.

        Args:
        ----
            payload (dict): The payload to be sent to the queue.

        """
        try:
            self.rate_limiter.acquire(context="QueueSender")
            if self.queue_type == "rabbitmq":
                self._send_to_rabbitmq(payload)
            else:
                self._send_to_sqs(payload)
        except Exception as e:
            logger.error(f"Failed to send message to {self.queue_type} queue: {e}")
            raise

    def _send_to_rabbitmq(self, payload: dict) -> None:
        """Publishes the message to a RabbitMQ queue."""
        try:
            self.connect_to_rabbitmq()

            queue_name = get_rabbitmq_exchange()
            self.channel.queue_declare(queue=queue_name, durable=True)
            self.channel.basic_publish(
                exchange=get_rabbitmq_exchange(),
                routing_key=get_rabbitmq_routing_key(),
                body=str(payload),
                properties=pika.BasicProperties(delivery_mode=2),  # Persistent messages
            )
            logger.info(f"Message successfully sent to RabbitMQ queue: {queue_name}.")
        except Exception as e:
            logger.error(f"Error while sending message to RabbitMQ: {e}")
            raise

    def _send_to_sqs(self, payload: dict) -> None:
        """Delegates sending the message to the SQS queue using QueueSender."""
        try:
            self.queue_sender.send_message(payload)
            logger.info("Message successfully sent to SQS queue.")
        except Exception as e:
            logger.error(f"Error while sending message to SQS: {e}")
            raise

    def close_connection(self) -> None:
        """Closes the RabbitMQ connection if it exists."""
        if self.queue_type == "rabbitmq" and self.connection:
            try:
                self.connection.close()
                logger.info("RabbitMQ connection closed.")
            except Exception as e:
                logger.error(f"Failed to close RabbitMQ connection: {e}")
                raise
