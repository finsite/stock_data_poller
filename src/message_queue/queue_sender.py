"""
QueueSender module for message delivery to RabbitMQ or AWS SQS.

This module defines the QueueSender class, which sends messages to a configured RabbitMQ
or Amazon SQS queue and supports proper connection cleanup.
"""

import json
import logging
import os
from typing import Any

import boto3
import pika
from botocore.exceptions import BotoCoreError, ClientError
from pika.exceptions import AMQPConnectionError
from tenacity import (
    before_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from src.utils.setup_logger import setup_logger

logger = setup_logger(__name__)


class QueueSender:
    """
    A class for sending messages to a RabbitMQ or SQS queue.

    Supports configuration for either queue type. Handles message serialization,
    dispatch, connection setup, and cleanup.
    """

    def __init__(
        self,
        queue_type: str,
        rabbitmq_host: str | None = None,
        rabbitmq_exchange: str | None = None,
        rabbitmq_routing_key: str | None = None,
        rabbitmq_vhost: str | None = "/",
        sqs_queue_url: str | None = None,
    ) -> None:
        """
        Initialize the QueueSender for RabbitMQ or SQS.

        Raises
        ------
        ValueError: If the queue_type is unsupported.
        EnvironmentError: If required environment variables are missing.
        """
        self.queue_type = queue_type.lower()
        self.rabbitmq_host = rabbitmq_host
        self.rabbitmq_exchange = rabbitmq_exchange
        self.rabbitmq_routing_key = rabbitmq_routing_key
        self.rabbitmq_vhost = rabbitmq_vhost
        self.sqs_queue_url = sqs_queue_url

        self._validate_required_vars()

        if self.queue_type == "rabbitmq":
            self._init_rabbitmq()
        elif self.queue_type == "sqs":
            self._init_sqs()
        else:
            raise ValueError(f"Unsupported queue type: {self.queue_type}")

    def _validate_required_vars(self) -> None:
        """Ensure all required environment variables are set for the configured queue."""
        if self.queue_type == "rabbitmq":
            missing = [
                var
                for var in [
                    "RABBITMQ_USER",
                    "RABBITMQ_PASS",
                    "RABBITMQ_HOST",
                    "RABBITMQ_EXCHANGE",
                    "RABBITMQ_ROUTING_KEY",
                ]
                if not os.getenv(var)
            ]
            if missing:
                raise OSError(
                    f"Missing required RabbitMQ environment variables: {', '.join(missing)}"
                )
        elif self.queue_type == "sqs":
            if not self.sqs_queue_url:
                raise OSError("Missing required SQS environment variable: SQS_QUEUE_URL")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type(AMQPConnectionError),
        before=before_log(logger, logging.WARNING),
        reraise=True,
    )
    def _init_rabbitmq(self) -> None:
        """Initialize RabbitMQ connection with retry."""
        try:
            logger.warning("🐇 Connecting to RabbitMQ with:")
            logger.warning(f"  host={self.rabbitmq_host}")
            logger.warning(f"  vhost={self.rabbitmq_vhost}")
            logger.warning(f"  exchange={self.rabbitmq_exchange}")
            logger.warning(f"  routing_key={self.rabbitmq_routing_key}")

            credentials = pika.PlainCredentials(
                username=os.getenv("RABBITMQ_USER"),
                password=os.getenv("RABBITMQ_PASS"),
            )

            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=self.rabbitmq_host,
                    virtual_host=self.rabbitmq_vhost,
                    credentials=credentials,
                )
            )
            self.channel = self.connection.channel()
            self.channel.exchange_declare(exchange=self.rabbitmq_exchange, exchange_type="direct")
            logger.info(f"✅ Connected to RabbitMQ on {self.rabbitmq_host}")
        except AMQPConnectionError as e:
            logger.warning(f"Retryable RabbitMQ connection error: {e}")
            raise
        except Exception as e:
            logger.error(f"Non-retryable RabbitMQ error: {e}")
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((BotoCoreError, ClientError)),
        before=before_log(logger, logging.WARNING),
        reraise=True,
    )
    def _init_sqs(self) -> None:
        """Initialize SQS client with retry."""
        try:
            self.sqs = boto3.client("sqs")
            logger.info("SQS client initialized.")
        except (BotoCoreError, ClientError) as e:
            logger.warning(f"Retryable SQS connection error: {e}")
            raise
        except Exception as e:
            logger.error(f"Non-retryable SQS error: {e}")
            raise

    def send_message(self, data: dict[str, Any]) -> None:
        """Send a message to the configured queue."""
        try:
            if self.queue_type == "rabbitmq":
                self._send_to_rabbitmq(data)
            elif self.queue_type == "sqs":
                self._send_to_sqs(data)
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type(Exception),
        before=before_log(logger, logging.WARNING),
        reraise=True,
    )
    def _send_to_rabbitmq(self, data: dict[str, Any]) -> None:
        """Send a message to RabbitMQ (with retry)."""
        message_body = json.dumps(data)
        self.channel.basic_publish(
            exchange=self.rabbitmq_exchange,
            routing_key=self.rabbitmq_routing_key,
            body=message_body,
            properties=pika.BasicProperties(delivery_mode=2),
        )
        logger.info(
            f"Message sent to RabbitMQ exchange `{self.rabbitmq_exchange}` "
            f"with routing key `{self.rabbitmq_routing_key}`"
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((BotoCoreError, ClientError)),
        before=before_log(logger, logging.WARNING),
        reraise=True,
    )
    def _send_to_sqs(self, data: dict[str, Any]) -> None:
        """Send a message to AWS SQS (with retry)."""
        if not self.sqs_queue_url:
            raise ValueError("SQS_QUEUE_URL is not configured.")

        message_body = json.dumps(data)
        self.sqs.send_message(QueueUrl=self.sqs_queue_url, MessageBody=message_body)
        logger.info(f"Message sent to SQS queue: {self.sqs_queue_url}")

    def close(self) -> None:
        """Close the RabbitMQ connection if it exists and is open."""
        if self.queue_type == "rabbitmq":
            try:
                if self.connection and self.connection.is_open:
                    self.connection.close()
                    logger.info("RabbitMQ connection closed.")
            except Exception as e:
                logger.error(f"Failed to close RabbitMQ connection: {e}")
                raise

    def flush(self) -> None:
        """
        Flush logic for future enhancements.

        This method currently performs no operations but can be extended to
        flush buffer or pending messages if batching is implemented in the future.
        """
        logger.info("Flush called - no operation performed.")

    def health_check(self) -> bool:
        """
        Check the health of the queue sender connection.

        Returns:
            bool: True if the connection is considered healthy, otherwise False.
        """
        if self.queue_type == "rabbitmq":
            return self.connection.is_open if hasattr(self, "connection") else False
        elif self.queue_type == "sqs":
            try:
                self.sqs.get_queue_attributes(
                    QueueUrl=self.sqs_queue_url,
                    AttributeNames=["QueueArn"],
                )
                return True
            except Exception as e:
                logger.warning(f"SQS health check failed: {e}")
                return False
        return False
