# """QueueSender class for message delivery to RabbitMQ or SQS.

# This class provides an interface for dispatching messages to either a RabbitMQ or an SQS
# queue. It supports configuration for both RabbitMQ and SQS, allowing users to select
# between them based on their needs.

# The class also includes methods for closing connections to the configured queue to ensure
# resource cleanup.

# Imports
# -------
# - json: Provides JSON serialization and deserialization.
# - boto3: AWS SDK for Python, used for interacting with SQS.
# - pika: Python client for RabbitMQ, used for interacting with RabbitMQ.
# - typing: Provides type hints for better code clarity and static analysis.
# - setup_logger: Function to set up the logger for logging messages.
# """

# import json
# import boto3
# import pika

# from typing import Dict, Any, Optional
# from src.utils.setup_logger import setup_logger

# # Set up logger
# logger = setup_logger(__name__)


# class QueueSender:
#     """A class for sending messages to a RabbitMQ or SQS queue.

#     The class provides an interface for sending messages to a RabbitMQ or SQS queue. It
#     supports both RabbitMQ and SQS, and it can be configured to use either one or the
#     other.

#     The class also provides methods for closing the connection to the queue.
#     """

#     def __init__(
#         self,
#         queue_type: str,
#         rabbitmq_host: str = None,
#         rabbitmq_exchange: str = None,
#         rabbitmq_routing_key: str = None,
#         sqs_queue_url: str = None,
#     ) -> None:
#         """Initializes the QueueSender for RabbitMQ or SQS.

#         Args:
#         ----
#             queue_type (str): Specifies the type of queue system, either "rabbitmq" or "sqs".
#             rabbitmq_host (Optional[str]): RabbitMQ host. Defaults to None.
#             rabbitmq_exchange (Optional[str]): RabbitMQ exchange name. Defaults to None.
#             rabbitmq_routing_key (Optional[str]): RabbitMQ routing key. Defaults to None.
#             sqs_queue_url (Optional[str]): AWS SQS queue URL. Defaults to None.

#         Raises:
#         ------
#             ValueError: If the queue type is invalid or unsupported.

#         """
#         self.queue_type: str = queue_type.lower()
#         self.rabbitmq_host: Optional[str] = rabbitmq_host
#         self.rabbitmq_exchange: Optional[str] = rabbitmq_exchange
#         self.rabbitmq_routing_key: Optional[str] = rabbitmq_routing_key
#         self.sqs_queue_url: Optional[str] = sqs_queue_url

#         if self.queue_type == "rabbitmq":
#             try:
#                 self.connection: pika.BlockingConnection = pika.BlockingConnection(
#                     pika.ConnectionParameters(host=self.rabbitmq_host)
#                 )
#                 self.channel: pika.adapters.blocking_connection.BlockingChannel = self.connection.channel()
#                 self.channel.exchange_declare(
#                     exchange=self.rabbitmq_exchange, exchange_type="direct"
#                 )
#                 logger.info(f"Connected to RabbitMQ on {self.rabbitmq_host}")
#             except Exception as e:
#                 logger.error(f"Failed to connect to RabbitMQ: {e}")
#                 raise

#         elif self.queue_type == "sqs":
#             try:
#                 self.sqs: boto3.client = boto3.client("sqs")
#                 logger.info("SQS client initialized.")
#             except Exception as e:
#                 logger.error(f"Failed to initialize SQS client: {e}")
#                 raise

#         else:
#             raise ValueError(f"Unsupported queue type: {self.queue_type}")

#     def send_message(self, data: Dict[str, Any]) -> None:
#         """Sends a message to the configured queue.

#         This method will determine the queue type and delegate the message
#         sending to the appropriate method. It handles exceptions and logs
#         errors if message sending fails.

#         Args:
#         ----
#             data (Dict[str, Any]): The message payload as a dictionary.

#         Raises:
#         ------
#             Exception: If the message could not be sent to the queue.

#         Returns:
#         -------
#             None: This method does not return a value.

#         """
#         try:
#             # Check the queue type and call the corresponding method
#             if self.queue_type == "rabbitmq":
#                 # Send message to RabbitMQ
#                 self._send_to_rabbitmq(data)  # type: ignore
#             elif self.queue_type == "sqs":
#                 # Send message to SQS
#                 self._send_to_sqs(data)  # type: ignore
#         except Exception as e:
#             # Log error if message sending fails
#             logger.error(f"Failed to send message: {e}")
#             raise

#     def _send_to_rabbitmq(self, data: Dict[str, Any]) -> None:
#         """Sends a message to a RabbitMQ queue.

#         This method takes a dictionary of data and serializes it into a JSON
#         string. It then publishes the message to the RabbitMQ exchange
#         specified in the configuration, using the routing key specified in
#         the configuration.

#         Args:
#         ----
#             data (Dict[str, Any]): The message payload to be sent, as a dictionary.

#         Raises:
#         ------
#             Exception: If there is an error while sending the message.

#         """
#         try:
#             # Convert the data dictionary to a JSON string
#             message_body: str = json.dumps(data)

#             # Publish the message to RabbitMQ
#             self.channel.basic_publish(
#                 exchange=self.rabbitmq_exchange,  # Exchange to publish to
#                 routing_key=self.rabbitmq_routing_key,  # Routing key for the message
#                 body=message_body,  # The message body
#                 properties=pika.BasicProperties(
#                     delivery_mode=2,  # Persistent messages
#                 ),
#             )

#             # Log a message indicating that the message has been sent
#             logger.info(
#                 f"Message sent to RabbitMQ exchange `{self.rabbitmq_exchange}` with routing key `{self.rabbitmq_routing_key}`"
#             )
#         except Exception as e:
#             # Log an error if there is an issue while sending the message
#             logger.error(f"Error sending to RabbitMQ: {e}")
#             raise

#     def _send_to_sqs(self, data: Dict[str, Any]) -> None:
#         """Sends a message to an SQS queue.

#         Args:
#         ----
#             data (Dict[str, Any]): The message payload to be sent, as a dictionary.

#         Raises:
#         ------
#             ValueError: If the SQS queue URL is not set.
#             Exception: If there is an error while sending the message.

#         Returns:
#         -------
#             None

#         """
#         try:
#             # Check if the SQS queue URL is set
#             if not self.sqs_queue_url:
#                 raise ValueError("SQS_QUEUE_URL is not configured.")

#             # Convert the data dictionary to a JSON string
#             message_body = json.dumps(data)

#             # Send the message to the SQS queue
#             self.sqs.send_message(QueueUrl=self.sqs_queue_url, MessageBody=message_body)

#             # Log a message indicating that the message has been sent
#             logger.info(f"Message sent to SQS queue: {self.sqs_queue_url}")
#         except Exception as e:
#             # Log an error if there is an issue while sending the message
#             logger.error(f"Error sending to SQS: {e}")
#             raise

#     def close(self) -> None:
#         """Closes the RabbitMQ connection if open.

#         This method is used to clean up resources when the object is no longer
#         needed. It closes the RabbitMQ connection if it is open.

#         Args:
#         ----
#             None

#         Returns:
#         -------
#             None

#         Raises:
#         ------
#             Exception: If there is an error while closing the connection.

#         """
#         # Check if the queue type is RabbitMQ
#         if self.queue_type == "rabbitmq":
#             try:
#                 # If the connection exists and is open, close it
#                 if self.connection and self.connection.is_open:
#                     self.connection.close()
#                     # Log successful closure of the connection
#                     logger.info("RabbitMQ connection closed.")
#             except Exception as e:
#                 # Log an error if closing the connection fails
#                 logger.error(f"Failed to close RabbitMQ connection: {e}")
#                 raise
# """
# QueueSender module for message delivery to RabbitMQ or AWS SQS.

# This module defines the QueueSender class, which sends messages to a configured
# RabbitMQ or Amazon SQS queue and supports proper connection cleanup.
# """

# import json
# import boto3
# import pika
# import logging

# from typing import Dict, Any, Optional
# from tenacity import (
#     retry,
#     stop_after_attempt,
#     wait_exponential,
#     retry_if_exception_type,
#     before_log,
# )

# from src.utils.setup_logger import setup_logger

# logger = setup_logger(__name__)


# class QueueSender:
#     """
#     A class for sending messages to a RabbitMQ or SQS queue.

#     Supports configuration for either queue type. Handles message serialization,
#     dispatch, and optional connection cleanup for RabbitMQ.
#     """

#     def __init__(
#         self,
#         queue_type: str,
#         rabbitmq_host: Optional[str] = None,
#         rabbitmq_exchange: Optional[str] = None,
#         rabbitmq_routing_key: Optional[str] = None,
#         sqs_queue_url: Optional[str] = None,
#     ) -> None:
#         """
#         Initialize the QueueSender for RabbitMQ or SQS.

#         Args:
#             queue_type (str): Either "rabbitmq" or "sqs".
#             rabbitmq_host (Optional[str]): RabbitMQ host, if applicable.
#             rabbitmq_exchange (Optional[str]): RabbitMQ exchange name.
#             rabbitmq_routing_key (Optional[str]): RabbitMQ routing key.
#             sqs_queue_url (Optional[str]): AWS SQS queue URL.

#         Raises:
#             ValueError: If the queue_type is unsupported.
#             Exception: If connection to the specified queue fails.
#         """
#         self.queue_type = queue_type.lower()
#         self.rabbitmq_host = rabbitmq_host
#         self.rabbitmq_exchange = rabbitmq_exchange
#         self.rabbitmq_routing_key = rabbitmq_routing_key
#         self.sqs_queue_url = sqs_queue_url

#         if self.queue_type == "rabbitmq":
#             try:
#                 self.connection = pika.BlockingConnection(
#                     pika.ConnectionParameters(host=self.rabbitmq_host)
#                 )
#                 self.channel = self.connection.channel()
#                 self.channel.exchange_declare(
#                     exchange=self.rabbitmq_exchange, exchange_type="direct"
#                 )
#                 logger.info(f"Connected to RabbitMQ on {self.rabbitmq_host}")
#             except Exception as e:
#                 logger.error(f"Failed to connect to RabbitMQ: {e}")
#                 raise

#         elif self.queue_type == "sqs":
#             try:
#                 self.sqs = boto3.client("sqs")
#                 logger.info("SQS client initialized.")
#             except Exception as e:
#                 logger.error(f"Failed to initialize SQS client: {e}")
#                 raise

#         else:
#             raise ValueError(f"Unsupported queue type: {self.queue_type}")

#     def send_message(self, data: Dict[str, Any]) -> None:
#         """
#         Send a message to the configured queue.

#         Args:
#             data (Dict[str, Any]): Message payload.

#         Raises:
#             Exception: If message delivery fails.
#         """
#         try:
#             if self.queue_type == "rabbitmq":
#                 self._send_to_rabbitmq(data)
#             elif self.queue_type == "sqs":
#                 self._send_to_sqs(data)
#         except Exception as e:
#             logger.error(f"Failed to send message: {e}")
#             raise

#     @retry(
#         stop=stop_after_attempt(3),
#         wait=wait_exponential(multiplier=1, min=1, max=10),
#         retry=retry_if_exception_type(Exception),
#         before=before_log(logger, logging.WARNING),
#         reraise=True,
#     )
#     def _send_to_rabbitmq(self, data: Dict[str, Any]) -> None:
#         """
#         Send a message to RabbitMQ (with retry).

#         Args:
#             data (Dict[str, Any]): Message payload.

#         Raises:
#             Exception: If sending fails.
#         """
#         message_body = json.dumps(data)
#         self.channel.basic_publish(
#             exchange=self.rabbitmq_exchange,
#             routing_key=self.rabbitmq_routing_key,
#             body=message_body,
#             properties=pika.BasicProperties(delivery_mode=2),
#         )
#         logger.info(
#             f"Message sent to RabbitMQ exchange `{self.rabbitmq_exchange}` "
#             f"with routing key `{self.rabbitmq_routing_key}`"
#         )

#     @retry(
#         stop=stop_after_attempt(3),
#         wait=wait_exponential(multiplier=1, min=1, max=10),
#         retry=retry_if_exception_type(Exception),
#         before=before_log(logger, logging.WARNING),
#         reraise=True,
#     )
#     def _send_to_sqs(self, data: Dict[str, Any]) -> None:
#         """
#         Send a message to AWS SQS (with retry).

#         Args:
#             data (Dict[str, Any]): Message payload.

#         Raises:
#             ValueError: If the queue URL is missing.
#             Exception: If sending fails.
#         """
#         if not self.sqs_queue_url:
#             raise ValueError("SQS_QUEUE_URL is not configured.")

#         message_body = json.dumps(data)
#         self.sqs.send_message(QueueUrl=self.sqs_queue_url, MessageBody=message_body)
#         logger.info(f"Message sent to SQS queue: {self.sqs_queue_url}")

#     def close(self) -> None:
#         """
#         Close the RabbitMQ connection if it exists and is open.

#         Raises:
#             Exception: If closing fails.
#         """
#         if self.queue_type == "rabbitmq":
#             try:
#                 if self.connection and self.connection.is_open:
#                     self.connection.close()
#                     logger.info("RabbitMQ connection closed.")
#             except Exception as e:
#                 logger.error(f"Failed to close RabbitMQ connection: {e}")
#                 raise
"""
QueueSender module for message delivery to RabbitMQ or AWS SQS.

This module defines the QueueSender class, which sends messages to a configured RabbitMQ
or Amazon SQS queue and supports proper connection cleanup.
"""

import json
import logging
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
        sqs_queue_url: str | None = None,
    ) -> None:
        """
        Initialize the QueueSender for RabbitMQ or SQS.

        Args:
            queue_type (str): Either "rabbitmq" or "sqs".
            rabbitmq_host (Optional[str]): RabbitMQ host, if applicable.
            rabbitmq_exchange (Optional[str]): RabbitMQ exchange name.
            rabbitmq_routing_key (Optional[str]): RabbitMQ routing key.
            sqs_queue_url (Optional[str]): AWS SQS queue URL.

        Raises:
            ValueError: If the queue_type is unsupported.
        """
        self.queue_type = queue_type.lower()
        self.rabbitmq_host = rabbitmq_host
        self.rabbitmq_exchange = rabbitmq_exchange
        self.rabbitmq_routing_key = rabbitmq_routing_key
        self.sqs_queue_url = sqs_queue_url

        if self.queue_type == "rabbitmq":
            self._init_rabbitmq()
        elif self.queue_type == "sqs":
            self._init_sqs()
        else:
            raise ValueError(f"Unsupported queue type: {self.queue_type}")

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
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=self.rabbitmq_host)
            )
            self.channel = self.connection.channel()
            self.channel.exchange_declare(exchange=self.rabbitmq_exchange, exchange_type="direct")
            logger.info(f"Connected to RabbitMQ on {self.rabbitmq_host}")
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
        """
        Send a message to the configured queue.

        Args:
            data (Dict[str, Any]): Message payload.

        Raises:
            Exception: If message delivery fails.
        """
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
        """
        Send a message to RabbitMQ (with retry).

        Args:
            data (Dict[str, Any]): Message payload.

        Raises:
            Exception: If sending fails.
        """
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
        """
        Send a message to AWS SQS (with retry).

        Args:
            data (Dict[str, Any]): Message payload.

        Raises:
            ValueError: If the queue URL is missing.
            Exception: If sending fails.
        """
        if not self.sqs_queue_url:
            raise ValueError("SQS_QUEUE_URL is not configured.")

        message_body = json.dumps(data)
        self.sqs.send_message(QueueUrl=self.sqs_queue_url, MessageBody=message_body)
        logger.info(f"Message sent to SQS queue: {self.sqs_queue_url}")

    def close(self) -> None:
        """
        Close the RabbitMQ connection if it exists and is open.

        Raises:
            Exception: If closing fails.
        """
        if self.queue_type == "rabbitmq":
            try:
                if self.connection and self.connection.is_open:
                    self.connection.close()
                    logger.info("RabbitMQ connection closed.")
            except Exception as e:
                logger.error(f"Failed to close RabbitMQ connection: {e}")
                raise
