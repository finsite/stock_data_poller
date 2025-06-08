"""Repository-specific configuration.

Delegates to shared config for common settings and defines any custom logic needed
by this repository (e.g., symbol lists, indicator types).
"""

import os
from app.config_shared import (
    get_environment,
    get_poller_name,
    get_poller_type,
    get_polling_interval,
    get_batch_size,
    get_rate_limit,
    get_output_mode,
    get_log_level,
    get_queue_type,
    get_rabbitmq_host,
    get_rabbitmq_port,
    get_rabbitmq_vhost,
    get_rabbitmq_user,
    get_rabbitmq_password,
    get_rabbitmq_exchange,
    get_rabbitmq_routing_key,
    get_rabbitmq_queue,
    get_dlq_name,
    get_sqs_queue_url,
    get_sqs_region,
    get_config_value,
    get_config_bool,
)


def get_symbols() -> list[str]:
    """Return a list of symbols to fetch data for, from comma-separated string."""
    symbols = os.getenv("SYMBOLS", "AAPL,MSFT,GOOG")
    return [s.strip() for s in symbols.split(",") if s.strip()]


def get_retry_delay() -> int:
    """Delay in seconds before retrying failed polling attempts."""
    return int(get_config_value("RETRY_DELAY", "5"))
