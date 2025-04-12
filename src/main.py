"""
Main application entry point.

Polls stock data and sends it to RabbitMQ or SQS.
"""

import logging
import time
from typing import Any

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


def main() -> None:
    """Run the main polling loop to collect and send stock data."""
    validate_environment_variables(["POLLER_TYPE", "SYMBOLS"])

    # Load config
    log_level = get_log_level()
    max_retries = get_max_retries()
    poll_interval = get_poll_interval()
    poller_type = get_poller_type()
    rabbitmq_host = get_rabbitmq_host()
    rabbitmq_exchange = get_rabbitmq_exchange()
    rabbitmq_routing_key = get_rabbitmq_routing_key()
    rate_limit = get_rate_limit()
    request_timeout = get_request_timeout()
    retry_delay = get_retry_delay()

    # Setup logger
    logger = setup_logger(__name__, level=LOG_LEVEL_MAP.get(log_level.lower(), logging.INFO))

    # Initialize
    rate_limiter = RateLimiter(max_requests=rate_limit, time_window=1)
    queue_sender = QueueSender(
        rabbitmq_host=rabbitmq_host,
        rabbitmq_exchange=rabbitmq_exchange,
        rabbitmq_routing_key=rabbitmq_routing_key,
    )
    poller_factory = PollerFactory()
    poller = poller_factory.create_poller()

    try:
        logger.info(f"Starting {poller_type} Poller...")
        logger.info(f"Polling every {poll_interval} seconds with exchange `{rabbitmq_exchange}`")

        while True:
            symbols: list[str] = get_symbols()
            logger.info(f"Polling for symbols: {symbols}")

            track_polling_metrics(poller_type, symbols)

            for symbol in symbols:
                rate_limiter.acquire(context=f"{poller_type} - {symbol}")
                try:
                    logger.info(f"Polling data for {symbol}")
                    track_request_metrics(symbol, request_timeout, max_retries)
                    data: Any = poller.poll([symbol])
                    queue_sender.send(data)
                except Exception as e:
                    logger.error(f"Error polling {symbol}: {e}")
                    logger.info(f"Retrying {symbol} after {retry_delay} seconds...")
                    time.sleep(retry_delay)

            time.sleep(poll_interval)

    except KeyboardInterrupt:
        logger.info("Polling stopped by user.")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        logger.info("Shutting down...")
        queue_sender.close()


if __name__ == "__main__":
    main()
