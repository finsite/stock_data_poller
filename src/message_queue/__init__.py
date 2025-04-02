"""The module provides the QueueSender class for handling message delivery
to either RabbitMQ or SQS queues.

Classes:
    QueueSender: Manages sending data to RabbitMQ or SQS queues and offers
                 methods for message dispatch to the appropriate queue.

Attributes:
    queue_type (str): Specifies the type of queue to use ('rabbitmq' or 'sqs').
    rabbitmq_host (str): The RabbitMQ server hostname.
    rabbitmq_exchange (str): The RabbitMQ exchange name.
    rabbitmq_routing_key (str): The routing key for RabbitMQ messages.
    sqs_queue_url (str): The URL of the SQS queue.

Methods:
    send_message: Sends a message to the configured queue.

"""

from src.message_queue.queue_sender import QueueSender

__all__ = ["QueueSender"]
