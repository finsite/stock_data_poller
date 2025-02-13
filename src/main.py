import time
from poller_factory import PollerFactory
from utils.rate_limit import RateLimiter
from utils.setup_logger import setup_logger
from utils import (
    validate_environment_variables,
    track_request_metrics,
    track_polling_metrics,
)
from message_queue.queue_sender import QueueSender
from config import (  # ✅ Importing updated config with Vault integration
    POLLER_TYPE,
    SYMBOLS,
    RABBITMQ_HOST,
    RABBITMQ_EXCHANGE,
    RABBITMQ_ROUTING_KEY,
    POLL_INTERVAL,
    REQUEST_TIMEOUT,
    MAX_RETRIES,
    RETRY_DELAY,
    LOG_LEVEL,
    RATE_LIMIT,
)

# Set up logging
logger = setup_logger(__name__)

# Validate required environment variables (already loaded via Vault)
required_env_vars = ["POLLER_TYPE", "SYMBOLS"]
validate_environment_variables(required_env_vars)

# Initialize RateLimiter
rate_limiter = RateLimiter(max_requests=RATE_LIMIT, time_window=1)

# ✅ Initialize the queue sender (Only RabbitMQ exchange)
queue_sender = QueueSender(
    rabbitmq_host=RABBITMQ_HOST,
    rabbitmq_exchange=RABBITMQ_EXCHANGE,
    rabbitmq_routing_key=RABBITMQ_ROUTING_KEY,
)

# Initialize the PollerFactory and create the poller
poller_factory = PollerFactory()
poller = poller_factory.create_poller()

def main():
    """
    Main polling loop.
    Polls data for configured symbols and sends the results to a queue.
    """
    try:
        logger.info(f"Starting {POLLER_TYPE} Poller...")
        logger.info(f"Polling every {POLL_INTERVAL} seconds with exchange `{RABBITMQ_EXCHANGE}`")

        while True:
            symbols = get_symbols_to_poll()
            logger.info(f"Polling for symbols: {symbols}")

            # Track polling metrics
            track_polling_metrics(POLLER_TYPE, symbols)

            # Poll and send data for each symbol
            for symbol in symbols:
                rate_limiter.acquire(context=f"{POLLER_TYPE} - {symbol}")
                try:
                    logger.info(f"Polling data for {symbol}")
                    track_request_metrics(symbol, REQUEST_TIMEOUT, MAX_RETRIES)
                    data = poller.poll([symbol])  # Assuming poller handles a single symbol
                    queue_sender.send(data)  # ✅ No more queue selection; always using RabbitMQ exchange
                except Exception as e:
                    logger.error(f"Error polling {symbol}: {e}")
                    logger.info(f"Retrying {symbol} after {RETRY_DELAY} seconds...")
                    time.sleep(RETRY_DELAY)  # ✅ Applying retry delay before retrying

            time.sleep(POLL_INTERVAL)

    except KeyboardInterrupt:
        logger.info("Polling stopped by user.")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        logger.info("Shutting down...")
        queue_sender.close()

def get_symbols_to_poll():
    """
    Get the list of stock symbols to poll.
    """
    return SYMBOLS.split(",")

if __name__ == "__main__":
    main()
