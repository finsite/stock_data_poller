"""
Configuration module for the stock poller.

The module provides functions for retrieving configuration values from environment
variables or Vault secrets.
"""

import os
from typing import Optional

from app.utils.vault_client import load_vault_secrets

# Load and cache Vault secrets from centralized Vault client
_vault_config: dict[str, str] = load_vault_secrets()


def get_config_value(key: str, default: str | None = None) -> str | None:
    """
    Retrieve a configuration value from Vault, environment, or default.

    Returns
    -------
    str | None
        The configuration value, or the default if not found.
    """
    return _vault_config.get(key, os.getenv(key, default))


def get_symbols() -> list[str]:
    """
    Get the list of symbols from the configuration.

    Returns
    -------
    list[str]
        A list of stock symbols to poll.
    """
    return get_config_value("SYMBOLS", "AAPL,GOOG,MSFT").split(",")


def get_poller_type() -> str:
    """
    Get the type of poller from the configuration.

    Returns
    -------
    str
        The type of poller to use. Can be one of 'yfinance', 'iex',
        'finnhub', 'polygon', 'alpha_vantage', or 'quandl'.
    """
    return get_config_value("POLLER_TYPE", "yfinance")


def get_queue_type() -> str:
    """
    Retrieve the queue type from the configuration.

    Returns
    -------
    str
        The type of queue to be used.
    """
    return get_config_value("QUEUE_TYPE", "rabbitmq")


def get_rabbitmq_host() -> str:
    """
    Get the RabbitMQ host from the configuration.

    Returns
    -------
    str
        The RabbitMQ host.
    """
    return get_config_value("RABBITMQ_HOST", "localhost")


def get_rabbitmq_exchange() -> str:
    """
    Retrieve the RabbitMQ exchange name from the configuration.

    Returns
    -------
    str
        The RabbitMQ exchange name.
    """
    return get_config_value("RABBITMQ_EXCHANGE", "stock_data_exchange")


def get_rabbitmq_routing_key() -> str:
    """
    Get the RabbitMQ routing key from the configuration.

    Returns
    -------
    str
        The RabbitMQ routing key.
    """
    return get_config_value("RABBITMQ_ROUTING_KEY", "stock_data")


def get_rabbitmq_vhost() -> str:
    """
    Get the RabbitMQ virtual host from the configuration.

    Returns
    -------
    str
        The RabbitMQ virtual host.

    Raises
    ------
    ValueError
        If the RabbitMQ virtual host is not configured.
    """
    vhost = get_config_value("RABBITMQ_VHOST")
    if not vhost:
        raise ValueError("❌ Missing required config: RABBITMQ_VHOST must be set.")
    return vhost


def get_sqs_queue_url() -> str:
    """
    Get the SQS queue URL from the configuration.

    Returns
    -------
    str
        The SQS queue URL.
    """
    return get_config_value("SQS_QUEUE_URL", "")


def get_poll_interval() -> int:
    """
    Get the poll interval from the configuration.

    Returns
    -------
    int
        The poll interval in seconds.
    """
    return int(get_config_value("POLL_INTERVAL", "60"))


def get_request_timeout() -> int:
    """
    Get the request timeout from the configuration.

    Returns
    -------
    int
        The request timeout in seconds.
    """
    return int(get_config_value("REQUEST_TIMEOUT", "30"))


def get_max_retries() -> int:
    """
    Get the maximum number of retries from the configuration.

    Returns
    -------
    int
        The maximum number of retries.
    """
    return int(get_config_value("MAX_RETRIES", "3"))


def get_retry_delay() -> int:
    """
    Retrieve the retry delay from the configuration.

    Returns
    -------
    int
        The retry delay in seconds.
    """
    return int(get_config_value("RETRY_DELAY", "5"))


def get_poll_timeout() -> int:
    """
    Get the poll timeout from the configuration.

    Returns
    -------
    int
        The poll timeout in seconds.
    """
    return int(get_config_value("POLL_TIMEOUT", "30"))


def get_log_level() -> str:
    """
    Get the log level from the configuration.

    Returns
    -------
    str
        The log level.
    """
    return get_config_value("LOG_LEVEL", "info")


def is_logging_enabled() -> bool:
    """
    Check if logging is enabled from the configuration.

    Returns
    -------
    bool
        True if logging is enabled, False otherwise.
    """
    return get_config_value("ENABLE_LOGGING", "true") == "true"


def is_cloud_logging_enabled() -> bool:
    """
    Check if cloud logging is enabled from the configuration.

    Returns
    -------
    bool
        True if cloud logging is enabled, False otherwise.
    """
    return get_config_value("CLOUD_LOGGING_ENABLED", "false") == "true"


def is_retry_enabled() -> bool:
    """
    Check if retry is enabled from the configuration.

    Returns
    -------
    bool
        True if retry is enabled, False otherwise.
    """
    return get_config_value("ENABLE_RETRY", "true") == "true"


def is_backfill_enabled() -> bool:
    """
    Check if backfill is enabled from the configuration.

    Returns
    -------
    bool
        True if backfill is enabled, False otherwise.
    """
    return get_config_value("ENABLE_BACKFILL", "false") == "true"
