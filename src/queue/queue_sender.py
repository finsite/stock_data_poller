import json
import os
import boto3
import pika
from src.utils.setup_logger import setup_logger

# Initialize logger
logger = setup_logger(__name__)


class QueueSender:
    """
    A class to send messages to either an SQS or RabbitMQ queue.
    """

    def __init__(self, queue_type: str, queue_url: str):
        """
        Initializes the QueueSender with the specified queue type (SQS or RabbitMQ) and queue URL.

        Args:
            queue_type (str): The type of the queue ('sqs' or 'rabbitmq').
            queue_url (str): The URL of the queue (for SQS or RabbitMQ).
        """
        self.queue_type = queue_type.lower()
        self.queue_url = queue_url

        if self.queue_type == "sqs":
            self.sqs_client = boto3.client("sqs")
            if not self.queue_url:
                logger.error("SQS_QUEUE_URL must be set for SQS queues.")
                raise ValueError("SQS_QUEUE_URL must be set for SQS queues.")
        elif self.queue_type == "rabbitmq":
            self.rabbitmq_host = os.getenv("RABBITMQ_HOST", "localhost")
            self.rabbitmq_vhost = os.getenv("RABBITMQ_DEFAULT_VHOST", "/")
            self.rabbitmq_user = os.getenv("RABBITMQ_DEFAULT_USER")
            self.rabbitmq_pass = os.getenv("RABBITMQ_DEFAULT_PASS")
            self.rabbitmq_connection = self._connect_to_rabbitmq()
        else:
            logger.error(f"Unsupported queue type: {self.queue_type}")
            raise ValueError("QUEUE_TYPE must be either 'sqs' or 'rabbitmq'.")

        logger.info(f"QueueSender initialized for {self.queue_type}.")

    def _connect_to_rabbitmq(self):
        """
        Establishes a connection to RabbitMQ using the provided connection parameters.
        """
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=self.rabbitmq_host,
                    virtual_host=self.rabbitmq_vhost,
                    credentials=pika.PlainCredentials(
                        self.rabbitmq_user, self.rabbitmq_pass
                    ),
                )
            )
            logger.info("RabbitMQ connection established.")
            return connection
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            raise

    def send(self, message: dict):
        """
        Sends a message to the configured queue.

        Args:
            message (dict): The message to send to the queue.

        Raises:
            Exception: If the message could not be sent.
        """
        if not isinstance(message, dict):
            logger.error("Message must be a dictionary.")
            raise ValueError("Message must be a dictionary.")

        if self.queue_type == "sqs":
            self._send_to_sqs(message)
        elif self.queue_type == "rabbitmq":
            self._send_to_rabbitmq(message)
        else:
            logger.error("Unsupported queue type. Please use 'sqs' or 'rabbitmq'.")
            raise ValueError("Unsupported queue type. Please use 'sqs' or 'rabbitmq'.")

    def _send_to_sqs(self, message: dict):
        """
        Sends a message to an SQS queue.

        Args:
            message (dict): The message to send to the queue.
        """
        try:
            response = self.sqs_client.send_message(
                QueueUrl=self.queue_url,
                MessageBody=json.dumps(message),
            )
            logger.info(
                f"Message sent to SQS queue. Message ID: {response['MessageId']}"
            )
        except Exception as e:
            logger.error(f"Failed to send message to SQS queue: {e}")
            raise

    def _send_to_rabbitmq(self, message: dict):
        """
        Sends a message to a RabbitMQ queue.

        Args:
            message (dict): The message to send to the queue.
        """
        try:
            channel = self.rabbitmq_connection.channel()
            queue_name = os.getenv("QUEUE_NAME", "default_queue")

            channel.queue_declare(queue=queue_name, durable=True)

            # Publish the message to the queue
            channel.basic_publish(
                exchange="",
                routing_key=queue_name,
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2  # Make the message persistent
                ),
            )
            logger.info(f"Message sent to RabbitMQ queue '{queue_name}'.")
        except Exception as e:
            logger.error(f"Failed to send message to RabbitMQ queue: {e}")
            raise

    def close(self):
        """
        Closes the connection to the queue (if applicable).
        """
        if self.queue_type == "rabbitmq":
            try:
                self.rabbitmq_connection.close()
                logger.info("RabbitMQ connection closed.")
            except Exception as e:
                logger.error(f"Failed to close RabbitMQ connection: {e}")
                raise
