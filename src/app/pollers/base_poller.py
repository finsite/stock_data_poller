# from typing import Any

# from app.config import (
#     get_queue_type,
#     get_rabbitmq_exchange,
#     get_rabbitmq_host,
#     get_rabbitmq_routing_key,
#     get_rabbitmq_vhost,
#     get_rate_limit,
#     get_sqs_queue_url,
# )
# from app.message_queue.queue_sender import QueueSender
# from app.utils.rate_limit import RateLimiter
# from app.utils.setup_logger import setup_logger

# logger = setup_logger(__name__)


# class BasePoller:
#     """Base class for pollers that handles dynamic queue configuration and message
#     sending."""

#     def __init__(self) -> None:
#         """Initializes the BasePoller with dynamic queue configuration and rate
#         limiting."""
#         self.queue_type = get_queue_type().lower()
#         if self.queue_type not in {"rabbitmq", "sqs"}:
#             raise ValueError("QUEUE_TYPE must be either 'sqs' or 'rabbitmq'.")

#         self.queue_sender = QueueSender(
#             queue_type=self.queue_type,
#             rabbitmq_host=get_rabbitmq_host(),
#             rabbitmq_exchange=get_rabbitmq_exchange(),
#             rabbitmq_routing_key=get_rabbitmq_routing_key(),
#             rabbitmq_vhost=get_rabbitmq_vhost(),
#             sqs_queue_url=get_sqs_queue_url(),
#         )

#         self.rate_limiter = RateLimiter(max_requests=get_rate_limit(), time_window=60)

#     def send_to_queue(self, payload: dict[str, Any]) -> None:
#         """Sends the processed payload to the configured queue (SQS or RabbitMQ)."""
#         try:
#             self.rate_limiter.acquire(context="QueueSender")
#             self.queue_sender.send_message(payload)
#             logger.info(f"Message successfully sent to {self.queue_type.upper()}.")
#         except Exception as e:
#             logger.error(f"Failed to send message to {self.queue_type.upper()}: {e}")
#             raise

#     def close_connection(self) -> None:
#         """Closes the queue connection if necessary."""
#         try:
#             self.queue_sender.close()
#         except Exception as e:
#             logger.error(f"Error closing queue connection: {e}")

#     def flush(self) -> None:
#         """Flush any buffered data in the underlying queue sender."""
#         try:
#             self.queue_sender.flush()
#         except Exception as e:
#             logger.error(f"Error during flush: {e}")

#     def health_check(self) -> bool:
#         """Check the health status of the queue sender connection."""
#         try:
#             return self.queue_sender.health_check()
#         except Exception as e:
#             logger.error(f"Health check failed: {e}")
#             return False
from typing import Any

from app.config import get_queue_type, get_rate_limit
from app.message_queue.queue_sender import QueueSender
from app.utils.rate_limit import RateLimiter
from app.utils.setup_logger import setup_logger

logger = setup_logger(__name__)


class BasePoller:
    """Base class for pollers that handles queue configuration and message sending."""

    def __init__(self) -> None:
        """Initializes the BasePoller with queue sender and rate limiter."""
        self.queue_type = get_queue_type().lower()
        if self.queue_type not in {"rabbitmq", "sqs"}:
            raise ValueError("QUEUE_TYPE must be either 'sqs' or 'rabbitmq'.")

        self.queue_sender = QueueSender()
        self.rate_limiter = RateLimiter(max_requests=get_rate_limit(), time_window=60)

    def send_to_queue(self, payload: dict[str, Any]) -> None:
        """Sends the processed payload to the configured queue (SQS or RabbitMQ).

        Args:
        ----
          payload: dict[str:
          Any]:
          payload: dict[str:
          payload: dict[str:
          payload: dict[str:
          payload: dict[str:
          payload: dict[str:

        Returns:
        -------

        """
        try:
            self.rate_limiter.acquire(context="QueueSender")
            self.queue_sender.send_message(payload)
            logger.info(f"Message successfully sent to {self.queue_type.upper()}.")
        except Exception as e:
            logger.error(f"Failed to send message to {self.queue_type.upper()}: {e}")
            raise

    def close_connection(self) -> None:
        """Closes the queue connection if necessary."""
        try:
            self.queue_sender.close()
        except Exception as e:
            logger.error(f"Error closing queue connection: {e}")

    def flush(self) -> None:
        """Flush any buffered data in the underlying queue sender."""
        try:
            self.queue_sender.flush()
        except Exception as e:
            logger.error(f"Error during flush: {e}")

    def health_check(self) -> bool:
        """Check the health status of the queue sender connection."""
        try:
            return self.queue_sender.health_check()
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
