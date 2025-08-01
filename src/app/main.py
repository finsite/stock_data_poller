# """Main application entry point.

# Polls stock data and sends it to RabbitMQ or SQS.
# """

# import logging
# import time
# from typing import Any

# from app.config import (
#     get_log_level,
#     get_polling_interval,  # ✅ Correct name
#     get_poller_type,
#     get_rate_limit,
#     get_retry_delay,
#     get_symbols,
# )

# from app.message_queue.queue_sender import QueueSender
# from app.poller_factory import PollerFactory
# from app.utils import validate_environment_variables
# from app.utils.rate_limit import RateLimiter
# from app.utils.setup_logger import setup_logger

# # Mapping of log level strings to logging module constants
# LOG_LEVEL_MAP = {
#     "debug": logging.DEBUG,
#     "info": logging.INFO,
#     "warning": logging.WARNING,
#     "error": logging.ERROR,
#     "critical": logging.CRITICAL,
# }


# def main() -> None:
#     """Run the main polling loop to collect and send stock data."""
#     validate_environment_variables(["POLLER_TYPE", "SYMBOLS"])

#     # Load config
#     log_level = get_log_level()
#     poll_interval = get_polling_interval()
#     poller_type = get_poller_type()
#     rate_limit = get_rate_limit()
#     retry_delay = get_retry_delay()

#     # Setup logger
#     logger = setup_logger(
#         __name__, level=LOG_LEVEL_MAP.get(log_level.lower(), logging.INFO)
#     )

#     # Initialize
#     rate_limiter = RateLimiter(max_requests=rate_limit, time_window=1)
#     queue_sender = QueueSender()  # <-- Updated here
#     poller_factory = PollerFactory()
#     poller = poller_factory.create_poller()

#     try:
#         logger.info(f"Starting {poller_type} Poller...")
#         logger.info(f"Polling every {poll_interval} seconds")

#         while True:
#             symbols: list[str] = get_symbols()
#             logger.info(f"Polling for symbols: {symbols}")

#             for symbol in symbols:
#                 rate_limiter.acquire(context=f"{poller_type} - {symbol}")
#                 try:
#                     logger.info(f"Polling data for {symbol}")
#                     data: Any = poller.poll([symbol])
#                     queue_sender.send_message(data)
#                 except Exception as e:
#                     logger.error(f"Error polling {symbol}: {e}")
#                     logger.info(f"Retrying {symbol} after {retry_delay} seconds...")
#                     time.sleep(retry_delay)

#             time.sleep(poll_interval)

#     except KeyboardInterrupt:
#         logger.info("Polling stopped by user.")
#     except Exception as e:
#         logger.error(f"Unexpected error: {e}")
#     finally:
#         logger.info("Shutting down...")
#         queue_sender.close()


# if __name__ == "__main__":
#     main()
"""Main application entry point.

Polls stock data and sends it to RabbitMQ or SQS.
"""

import logging
import time
from typing import Any

from app.config import (
    get_log_level,
    get_polling_interval,
    get_poller_type,
    get_rate_limit,
    get_retry_delay,
    get_symbols,
    get_dry_run_mode,
    get_queue_type,
    get_structured_logging,
)
from app.message_queue.queue_sender import QueueSender
from app.poller_factory import PollerFactory
from app.utils import validate_environment_variables
from app.utils.rate_limit import RateLimiter
from app.utils.setup_logger import setup_logger

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
    poll_interval = get_polling_interval()
    poller_type = get_poller_type()
    rate_limit = get_rate_limit()
    retry_delay = get_retry_delay()
    dry_run = get_dry_run_mode()
    queue_type = get_queue_type()
    structured_logging = get_structured_logging()

    # Setup logger
    logger = setup_logger(__name__, level=LOG_LEVEL_MAP.get(log_level.lower(), logging.INFO))

    # Readiness logs
    logger.info(
        "🔧 Poller initialized",
        extra=(
            {
                "poller_type": poller_type,
                "poll_interval": poll_interval,
                "rate_limit": rate_limit,
                "queue_type": queue_type,
                "dry_run": dry_run,
                "structured": structured_logging,
            }
            if structured_logging
            else None
        ),
    )

    rate_limiter = RateLimiter(max_requests=rate_limit, time_window=1)
    queue_sender = QueueSender()
    poller = PollerFactory().create_poller()

    try:
        logger.info(f"📡 Starting {poller_type} poller...")
        logger.info(f"Polling every {poll_interval} seconds")

        while True:
            symbols: list[str] = get_symbols()
            logger.debug(f"Fetched symbols: {symbols}")

            for symbol in symbols:
                rate_limiter.acquire(context=f"{poller_type}:{symbol}")

                try:
                    logger.info(f"🔍 Polling data for {symbol}")
                    data: Any = poller.poll([symbol])

                    if dry_run:
                        logger.info(f"[DRY_RUN] Would send data for {symbol}")
                    else:
                        queue_sender.send_message(data)

                except Exception as e:
                    logger.error(f"❌ Error polling {symbol}: {e}")
                    logger.info(f"⏳ Retrying {symbol} after {retry_delay} seconds...")
                    time.sleep(retry_delay)

            time.sleep(poll_interval)

    except KeyboardInterrupt:
        logger.info("⛔ Polling stopped by user.")
    except Exception as e:
        logger.error(f"🔥 Unexpected error: {e}")
    finally:
        logger.info("🧹 Shutting down poller.")
        queue_sender.close()


if __name__ == "__main__":
    main()
