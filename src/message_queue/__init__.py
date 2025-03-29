"""
This module initializes the queue-related functionalities for the
application.

The module provides the QueueSender class which handles sending data to
either RabbitMQ or SQS queues.

Classes:
    QueueSender: Handles sending data to either RabbitMQ or SQS queues.
                 The class provides methods for sending messages to the
                 respective queues.

"""

from src.message_queue.queue_sender import QueueSender


__all__ = ["QueueSender"]

