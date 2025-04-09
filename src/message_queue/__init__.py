"""The module provides the QueueSender class for handling message delivery to either
RabbitMQ or SQS queues.

The QueueSender class encapsulates the logic for sending data to RabbitMQ or
SQS queues. It offers methods for message dispatch to the appropriate queue.

Attributes
----------
    queue_type (str): Specifies the type of queue to use ('rabbitmq' or 'sqs').
    rabbitmq_host (Optional[str]): The RabbitMQ server hostname. None if not using RabbitMQ.
    rabbitmq_exchange (Optional[str]): The RabbitMQ exchange name. None if not applicable.
    rabbitmq_routing_key (Optional[str]): The routing key for RabbitMQ messages. None if not applicable.
    sqs_queue_url (Optional[str]): The URL of the SQS queue. None if not using SQS.

Methods
-------
    send_message: Sends a message to the configured queue. Handles exceptions
                  and logs errors appropriately.

"""

from src.message_queue.queue_sender import QueueSender

__all__ = ["QueueSender"]
