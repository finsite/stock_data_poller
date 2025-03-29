"""
A class for sending messages to a RabbitMQ or SQS queue.

The class provides an interface for sending messages to a RabbitMQ or SQS queue.
It supports both RabbitMQ and SQS, and it can be configured to use either one
or the other.

The class also provides methods for closing the connection to the queue.
"""

import json
import boto3
import pika

from src.utils.setup_logger import setup_logger

# Set up logger
logger = setup_logger(__name__)


class QueueSender:
    """
    A class for sending messages to a RabbitMQ or SQS queue.

    The class provides an interface for sending messages to a RabbitMQ or SQS queue.
    It supports both RabbitMQ and SQS, and it can be configured to use either one
    or the other.

    The class also provides methods for closing the connection to the queue.
    """

    def __init__(
        self,
        queue_type: str,
        rabbitmq_host: str = None,
        rabbitmq_exchange: str = None,
        rabbitmq_routing_key: str = None,
        sqs_queue_url: str = None,
    ):
        """
        Initializes the QueueSender for RabbitMQ or SQS.

        Args:
        ----
            queue_type (str): Type of queue system, either "rabbitmq" or "sqs".
            rabbitmq_host (str): RabbitMQ host.
            rabbitmq_exchange (str): RabbitMQ exchange name.
            rabbitmq_routing_key (str): RabbitMQ routing key.
            sqs_queue_url (str): AWS SQS queue URL.
        """
        self.queue_type = queue_type.lower()
        self.rabbitmq_host = rabbitmq_host
        self.rabbitmq_exchange = rabbitmq_exchange
        self.rabbitmq_routing_key = rabbitmq_routing_key
        self.sqs_queue_url = sqs_queue_url

        if self.queue_type == "rabbitmq":
            try:
                self.connection = pika.BlockingConnection(
                    pika.ConnectionParameters(host=self.rabbitmq_host)
                )
                self.channel = self.connection.channel()
                self.channel.exchange_declare(
                    exchange=self.rabbitmq_exchange, exchange_type="direct"
                )
                logger.info(f"Connected to RabbitMQ on {self.rabbitmq_host}")
            except Exception as e:
                logger.error(f"Failed to connect to RabbitMQ: {e}")
                raise

        elif self.queue_type == "sqs":
            try:
                self.sqs = boto3.client("sqs")
                logger.info("SQS client initialized.")
            except Exception as e:
                logger.error(f"Failed to initialize SQS client: {e}")
                raise

        else:
            raise ValueError(f"Unsupported queue type: {self.queue_type}")

    def send_message(self, data: dict):
        """
        Sends a message to the configured queue.

        Args:
        ----
            data (dict): The message payload.
        """
        try:
            if self.queue_type == "rabbitmq":
                self._send_to_rabbitmq(data)
            elif self.queue_type == "sqs":
                self._send_to_sqs(data)
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            raise

    def _send_to_rabbitmq(self, data: dict):
        """
        Sends a message to a RabbitMQ queue.

        Args:
        ----
            data (dict): The message payload.
        """
        try:
            message_body = json.dumps(data)
            self.channel.basic_publish(
                exchange=self.rabbitmq_exchange,
                routing_key=self.rabbitmq_routing_key,
                body=message_body,
            )
            logger.info(
                f"Message sent to RabbitMQ exchange `{self.rabbitmq_exchange}` with routing key `{self.rabbitmq_routing_key}`"
            )
        except Exception as e:
            logger.error(f"Error sending to RabbitMQ: {e}")
            raise

    def _send_to_sqs(self, data: dict):
        """
        Sends a message to an SQS queue.

        Args:
        ----
            data (dict): The message payload.
        """
        try:
            if not self.sqs_queue_url:
                raise ValueError("SQS_QUEUE_URL is not configured.")
            message_body = json.dumps(data)
            self.sqs.send_message(QueueUrl=self.sqs_queue_url, MessageBody=message_body)
            logger.info(f"Message sent to SQS queue: {self.sqs_queue_url}")
        except Exception as e:
            logger.error(f"Error sending to SQS: {e}")
            raise

    def close(self):
        """
        Closes the RabbitMQ connection if open.
        """
        if self.queue_type == "rabbitmq":
            try:
                if self.connection and self.connection.is_open:
                    self.connection.close()
                    logger.info("RabbitMQ connection closed.")
            except Exception as e:
                logger.error(f"Failed to close RabbitMQ connection: {e}")

