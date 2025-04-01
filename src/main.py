# """Main application entry point.

# This script polls stock data from the IEX Cloud API and sends the data to a
# RabbitMQ or SQS queue. It uses environment variables to configure its behavior.

# Environment Variables:
# - POLLER_TYPE: The type of poller to use (e.g., "iex", "polygon", etc.).
# - SYMBOLS: A comma-separated list of stock symbols to poll.
# - POLL_INTERVAL: The time in seconds to wait between polling runs.
# - REQUEST_TIMEOUT: The maximum time in seconds to wait for an API response.
# - MAX_RETRIES: The maximum number of retry attempts for a failed request.
# - RATE_LIMIT: The maximum number of requests per second.
# - RETRY_DELAY: The time in seconds to wait before retrying a failed request.
# - RABBITMQ_HOST: The RabbitMQ server hostname.
# - RABBITMQ_EXCHANGE: The RabbitMQ exchange name.
# - RABBITMQ_ROUTING_KEY: The routing key for RabbitMQ messages.
# """

# import logging
# import time

# # from src.config import (
# #     LOG_LEVEL,
# #     MAX_RETRIES,
# #     POLL_INTERVAL,
# #     POLLER_TYPE,
# #     RABBITMQ_EXCHANGE,
# #     RABBITMQ_HOST,
# #     RABBITMQ_ROUTING_KEY,
# #     RATE_LIMIT,
# #     REQUEST_TIMEOUT,
# #     RETRY_DELAY,
# #     SYMBOLS,
# # )
# from src.config import (
#     get_log_level,
#     get_max_retries,
#     get_poll_interval,
#     get_poller_type,
#     get_rabbitmq_exchange,
#     get_rabbitmq_host,
#     get_rabbitmq_routing_key,
#     get_rate_limit,
#     get_request_timeout,
#     get_retry_delay,
#     get_symbols,
# )

# from src.message_queue.queue_sender import QueueSender
# from src.poller_factory import PollerFactory
# from src.utils import (
#     track_polling_metrics,
#     track_request_metrics,
#     validate_environment_variables,
# )
# from src.utils.rate_limit import RateLimiter
# from src.utils.setup_logger import setup_logger

# # Mapping of log level strings to logging module constants
# LOG_LEVEL_MAP = {
#     "debug": logging.DEBUG,
#     "info": logging.INFO,
#     "warning": logging.WARNING,
#     "error": logging.ERROR,
#     "critical": logging.CRITICAL,
# }

# # Set up logging with the specified log level
# logger = setup_logger(__name__, level=LOG_LEVEL_MAP.get(LOG_LEVEL.lower(), logging.INFO))

# # Validate required environment variables
# validate_environment_variables(["POLLER_TYPE", "SYMBOLS"])

# # Initialize a rate limiter for API requests
# rate_limiter = RateLimiter(max_requests=RATE_LIMIT, time_window=1)

# # Initialize the queue sender for message delivery
# queue_sender = QueueSender(
#     rabbitmq_host=RABBITMQ_HOST,
#     rabbitmq_exchange=RABBITMQ_EXCHANGE,
#     rabbitmq_routing_key=RABBITMQ_ROUTING_KEY,
# )

# # Initialize the poller factory and create the appropriate poller
# poller_factory = PollerFactory()
# poller = poller_factory.create_poller()


# def main():
#     """Run the main polling loop to collect and send stock data."""
#     try:
#         logger.info(f"Starting {POLLER_TYPE} Poller...")
#         logger.info(f"Polling every {POLL_INTERVAL} seconds with exchange `{RABBITMQ_EXCHANGE}`")

#         while True:
#             symbols = get_symbols_to_poll()
#             logger.info(f"Polling for symbols: {symbols}")

#             # Track polling metrics
#             track_polling_metrics(POLLER_TYPE, symbols)

#             # Poll and send data for each symbol
#             for symbol in symbols:
#                 rate_limiter.acquire(context=f"{POLLER_TYPE} - {symbol}")
#                 try:
#                     logger.info(f"Polling data for {symbol}")
#                     track_request_metrics(symbol, REQUEST_TIMEOUT, MAX_RETRIES)
#                     data = poller.poll([symbol])
#                     queue_sender.send(data)
#                 except Exception as e:
#                     logger.error(f"Error polling {symbol}: {e}")
#                     logger.info(f"Retrying {symbol} after {RETRY_DELAY} seconds...")
#                     time.sleep(RETRY_DELAY)

#             time.sleep(POLL_INTERVAL)

#     except KeyboardInterrupt:
#         logger.info("Polling stopped by user.")
#     except Exception as e:
#         logger.error(f"Unexpected error: {e}")
#     finally:
#         logger.info("Shutting down...")
#         queue_sender.close()


# def get_symbols_to_poll():
#     """Return the list of stock symbols to poll, split from a comma-separated string."""
#     return SYMBOLS.split(",")


# if __name__ == "__main__":
#     main()
"""Main application entry point.

This script polls stock data from the IEX Cloud API and sends the data to a
RabbitMQ or SQS queue. It uses environment variables or Vault to configure its behavior.

Environment Variables:
- POLLER_TYPE: The type of poller to use (e.g., "iex", "polygon", etc.).
- SYMBOLS: A comma-separated list of stock symbols to poll.
- POLL_INTERVAL: The time in seconds to wait between polling runs.
- REQUEST_TIMEOUT: The maximum time in seconds to wait for an API response.
- MAX_RETRIES: The maximum number of retry attempts for a failed request.
- RATE_LIMIT: The maximum number of requests per second.
- RETRY_DELAY: The time in seconds to wait before retrying a failed request.
- RABBITMQ_HOST: The RabbitMQ server hostname.
- RABBITMQ_EXCHANGE: The RabbitMQ exchange name.
- RABBITMQ_ROUTING_KEY: The routing key for RabbitMQ messages.
"""

import logging
import time

from src.config import (
    get_log_level,
    get_max_retries,
    get_poll_interval,
    get_poller_type,
    get_rabbitmq_exchange,
    get_rabbitmq_host,
    get_rabbitmq_routing_key,
    get_rate_limit,
    get_request_timeout,
    get_retry_delay,
    get_symbols,
)
from src.message_queue.queue_sender import QueueSender
from src.poller_factory import PollerFactory
from src.utils import (
    track_polling_metrics,
    track_request_metrics,
    validate_environment_variables,
)
from src.utils.rate_limit import RateLimiter
from src.utils.setup_logger import setup_logger

# Mapping of log level strings to logging module constants
LOG_LEVEL_MAP = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
}

# Load configuration values using getter functions
LOG_LEVEL = get_log_level()
MAX_RETRIES = get_max_retries()
POLL_INTERVAL = get_poll_interval()
POLLER_TYPE = get_poller_type()
RABBITMQ_HOST = get_rabbitmq_host()
RABBITMQ_EXCHANGE = get_rabbitmq_exchange()
RABBITMQ_ROUTING_KEY = get_rabbitmq_routing_key()
RATE_LIMIT = get_rate_limit()
REQUEST_TIMEOUT = get_request_timeout()
RETRY_DELAY = get_retry_delay()

# Set up logging with the specified log level
logger = setup_logger(__name__, level=LOG_LEVEL_MAP.get(LOG_LEVEL.lower(), logging.INFO))

# Validate required environment variables
validate_environment_variables(["POLLER_TYPE", "SYMBOLS"])

# Initialize a rate limiter for API requests
rate_limiter = RateLimiter(max_requests=RATE_LIMIT, time_window=1)

# Initialize the queue sender for message delivery
queue_sender = QueueSender(
    rabbitmq_host=RABBITMQ_HOST,
    rabbitmq_exchange=RABBITMQ_EXCHANGE,
    rabbitmq_routing_key=RABBITMQ_ROUTING_KEY,
)

# Initialize the poller factory and create the appropriate poller
poller_factory = PollerFactory()
poller = poller_factory.create_poller()


def main() -> None:
    """Run the main polling loop to collect and send stock data.

    This function starts a while loop that continues until the program is
    interrupted with a KeyboardInterrupt (e.g., Ctrl+C). It polls the specified
    API for each symbol in the SYMBOLS environment variable, and sends the data to
    the message queue using the QueueSender.

    If an exception is raised during polling, the error is logged and the program
    waits for the specified retry delay before retrying the poll for the symbol.

    Returns:
        None

    """
    try:
        logger.info(f"Starting {POLLER_TYPE} Poller...")
        logger.info(f"Polling every {POLL_INTERVAL} seconds with exchange `{RABBITMQ_EXCHANGE}`")

        while True:
            symbols: list[str] = get_symbols()
            logger.info(f"Polling for symbols: {symbols}")

            # Track polling metrics
            track_polling_metrics(POLLER_TYPE, symbols)

            # Poll and send data for each symbol
            for symbol in symbols:
                rate_limiter.acquire(context=f"{POLLER_TYPE} - {symbol}")
                try:
                    logger.info(f"Polling data for {symbol}")
                    track_request_metrics(symbol, REQUEST_TIMEOUT, MAX_RETRIES)
                    data: Any = poller.poll([symbol])
                    queue_sender.send(data)
                except Exception as e:
                    logger.error(f"Error polling {symbol}: {e}")
                    logger.info(f"Retrying {symbol} after {RETRY_DELAY} seconds...")
                    time.sleep(RETRY_DELAY)

            time.sleep(POLL_INTERVAL)

    except KeyboardInterrupt:
        logger.info("Polling stopped by user.")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        logger.info("Shutting down...")
        queue_sender.close()


if __name__ == "__main__":
    main()
