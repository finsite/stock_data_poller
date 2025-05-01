# """
# Configuration module for the stock poller.

# The module provides functions for retrieving configuration values from environment
# variables or Vault secrets.
# """

# import os
# from typing import Optional

# from app.utils.vault_client import load_vault_secrets

# # Load and cache Vault secrets from centralized Vault client
# _vault_config: dict[str, str] = load_vault_secrets()


# def get_config_value(key: str, default: Optional[str] = None) -> Optional[str]:
#     """
#     Retrieve a configuration value from Vault, environment, or default.

#     Parameters:
#         key (str): The key for the configuration value to retrieve.
#         default (Optional[str], optional): The default value to return if the key is not found. Defaults to None.

#     Returns:
#         Optional[str]: The retrieved configuration value, or the default if not found.
#     """
#     # Attempt to get the value from Vault secrets first
#     # If not found, fall back to environment variable
#     # If still not found, use the provided default
#     return _vault_config.get(key, os.getenv(key, default))


# def get_symbols() -> list[str]:
#     """
#     Retrieve the list of stock symbols from the configuration.

#     Returns
#     -------
#     list[str]
#         A list of stock symbols to poll.

#     Notes
#     -----
#     The symbols are retrieved as a comma-separated string from the configuration
#     and split into a list. If not found, defaults to 'AAPL', 'GOOG', and 'MSFT'.
#     """
#     # Get the comma-separated string of symbols from configuration
#     symbols_str: str = get_config_value("SYMBOLS", "AAPL,GOOG,MSFT")
#     # Split the string by commas to form a list of symbols
#     symbols_list: list[str] = symbols_str.split(",")
#     return symbols_list


# def get_poller_type() -> str:
#     """
#     Retrieve the type of poller from the configuration.

#     The type of poller to use is determined by the 'POLLER_TYPE' environment
#     variable. If not set, defaults to 'yfinance'.

#     Returns
#     -------
#     str
#         One of 'yfinance', 'iex', 'finnhub', 'polygon', 'alpha_vantage', or 'quandl'.
#     """
#     return get_config_value("POLLER_TYPE", "yfinance")  # type: str


# def get_poller_fill_rate_limit() -> int:
#     """
#     Retrieve the poller fill rate limit from the configuration.

#     The fill rate limit determines the maximum number of requests per minute
#     that the poller will make to the API. If not set, defaults to 0, meaning no
#     limit.

#     Returns
#     -------
#     int
#         The maximum number of requests per minute, or 0 if no limit.
#     """
#     # Get the fill rate limit from the configuration
#     # If not set, defaults to 0, meaning no limit
#     return int(get_config_value("POLLER_FILL_RATE_LIMIT", 0))  # type: int


# def get_queue_type() -> str:
#     """
#     Retrieve the queue type from the configuration.

#     The queue type is determined by the 'QUEUE_TYPE' environment variable. If not
#     set, defaults to 'rabbitmq'.

#     Returns
#     -------
#     str
#         One of 'rabbitmq' or 'sqs'.
#     """
#     return get_config_value("QUEUE_TYPE", "rabbitmq")


# def get_rabbitmq_host() -> str:
#     """
#     Retrieves the RabbitMQ host from the configuration.

#     The RabbitMQ host is determined by the 'RABBITMQ_HOST' environment variable.
#     If not set, defaults to 'localhost'.

#     Returns
#     -------
#     str
#         The RabbitMQ host.
#     """
#     return get_config_value("RABBITMQ_HOST", "localhost")  # type: str


# def get_rabbitmq_port() -> int:
#     """
#     Retrieve the RabbitMQ port from the configuration.

#     The RabbitMQ port is specified by the 'RABBITMQ_PORT' environment variable.
#     If not set, it defaults to 5672.

#     Returns
#     -------
#     int
#         The RabbitMQ port number.
#     """
#     return int(get_config_value("RABBITMQ_PORT", 5672))


# def get_rabbitmq_exchange() -> str:
#     """
#     Retrieves the RabbitMQ exchange name from the configuration.

#     Returns
#     -------
#     exchange_name: str
#         The RabbitMQ exchange name.

#     Notes
#     -----
#     If the 'RABBITMQ_EXCHANGE' is not set in the environment, it defaults to 'stock_data_exchange'.
#     """
#     # Retrieve the RabbitMQ exchange name from environment or use default if not set
#     return get_config_value("RABBITMQ_EXCHANGE", "stock_data_exchange")


# def get_rabbitmq_routing_key() -> str:
#     """
#     Retrieves the RabbitMQ routing key from the configuration.

#     The routing key specifies which queue(s) a message should be routed to.
#     The default routing key is 'stock_data' if not specified.

#     Returns
#     -------
#     str
#         The RabbitMQ routing key.
#     """
#     return get_config_value("RABBITMQ_ROUTING_KEY", "stock_data")


# def get_rabbitmq_vhost() -> str:
#     """
#     Retrieve the RabbitMQ virtual host from the configuration.

#     Returns
#     -------
#     str
#         The RabbitMQ virtual host.

#     Raises
#     ------
#     ValueError
#         If the RabbitMQ virtual host is not configured.

#     Notes
#     -----
#     Ensure that the 'RABBITMQ_VHOST' environment variable is set to avoid
#     connection issues with RabbitMQ.
#     """
#     vhost: str = get_config_value("RABBITMQ_VHOST")

#     if not vhost:
#         raise ValueError("❌ Missing required config: RABBITMQ_VHOST must be set.")

#     return vhost


# def get_sqs_queue_url() -> str:
#     """
#     Retrieves the SQS queue URL from the configuration.

#     Returns
#     -------
#     str
#         The SQS queue URL. Returns an empty string if not configured.

#     Notes
#     -----
#     Ensure that the 'SQS_QUEUE_URL' environment variable is set to avoid
#     issues with SQS message delivery.
#     """
#     return get_config_value("SQS_QUEUE_URL", "")


# def get_poll_interval() -> int:
#     """
#     Get the poll interval from the configuration.

#     The poll interval is the time (in seconds) that the poller waits between
#     subsequent polls. The default value is 60 seconds.

#     Returns
#     -------
#     int
#         The poll interval in seconds.
#     """
#     return int(get_config_value("POLL_INTERVAL", 60))


# def get_request_timeout() -> int:
#     """
#     Get the request timeout from the configuration.

#     The request timeout is the time (in seconds) that the poller waits for
#     a response from the API. The default value is 30 seconds.

#     Returns
#     -------
#     int
#         The request timeout in seconds.
#     """
#     return int(get_config_value("REQUEST_TIMEOUT", 30))


# def get_max_retries() -> int:
#     """
#     Get the maximum number of retries from the configuration.

#     This value is used by the :py:func:`retry_request` decorator to determine
#     the maximum number of times to retry a failed API request.

#     Returns
#     -------
#     max_retries: int
#         The maximum number of retries.
#     """
#     return int(get_config_value("MAX_RETRIES", "3"))


# def get_retry_delay() -> int:
#     """
#     Retrieves the retry delay from the configuration.

#     The retry delay is the time (in seconds) that the poller waits before retrying
#     a failed API request.

#     Returns
#     -------
#     int
#         The retry delay in seconds. The default value is 5 seconds.
#     """
#     return int(get_config_value("RETRY_DELAY", 5))


# def get_poll_timeout() -> int:
#     """
#     Retrieves the poll timeout from the configuration.

#     The poll timeout is the time (in seconds) that the poller waits for a response
#     from the API after sending a request. If the API does not respond within
#     this time window, the poller will retry the request.

#     Returns
#     -------
#     int
#         The poll timeout in seconds. The default value is 30 seconds.
#     """
#     return int(get_config_value("POLL_TIMEOUT", 30))


# def get_log_level() -> str:
#     """
#     Retrieves the log level from the configuration.

#     The log level determines the severity of logs that are output by the application.
#     Common log levels include "debug", "info", "warning", "error", and "critical".

#     Returns
#     -------
#     log_level: str
#         The configured log level. Defaults to "info" if not set.
#     """
#     return get_config_value("LOG_LEVEL", "info")


# def is_logging_enabled() -> bool:
#     """
#     Determine if logging is enabled based on the configuration.

#     This function retrieves the 'ENABLE_LOGGING' configuration value and checks
#     if it is set to 'true'.

#     Parameters
#     ----------
#     None

#     Returns
#     -------
#     bool
#         True if logging is enabled; otherwise, False.
#     """
#     # Retrieve the logging enabled status from the configuration
#     return get_config_value("ENABLE_LOGGING", "true") == "true"


# def is_cloud_logging_enabled() -> bool:
#     """
#     Check if cloud logging is enabled from the configuration.

#     Parameters
#     ----------
#     None

#     Returns
#     -------
#     bool
#         True if cloud logging is enabled, False otherwise.
#     """
#     # Retrieve the cloud logging enabled status from the configuration
#     return get_config_value("CLOUD_LOGGING_ENABLED", "false") == "true"


# def is_retry_enabled() -> bool:
#     """
#     Determine if retry is enabled based on the configuration.

#     This function retrieves the 'ENABLE_RETRY' configuration value and checks
#     if it is set to 'true'.

#     Returns
#     -------
#     bool
#         True if retry is enabled; otherwise, False.
#     """
#     return get_config_value("ENABLE_RETRY", "true") == "true"


# def is_backfill_enabled() -> bool:
#     """
#     Check if backfill is enabled from the configuration.

#     Parameters
#     ----------
#     None

#     Returns
#     -------
#     bool
#         True if backfill is enabled; otherwise, False.
#     """
#     return get_config_value("ENABLE_BACKFILL", "false") == "true"

# def get_data_source() -> str:
#     """
#     Returns the data source to use for the current run.

#     Parameters
#     ----------
#     None

#     Returns
#     -------
#     str
#         The data source to use. The default value is "yahoo_rapidapi" if the
#         "DATA_SOURCE" environment variable is not set.
#     """
#     return os.getenv("DATA_SOURCE", "yahoo_rapidapi")

# def get_rapidapi_key() -> str:
#     """
#     Retrieves the RapidAPI key from the environment variables.

#     Returns
#     -------
#     str
#         The RapidAPI key as a string.

#     Notes
#     -----
#     The RapidAPI key is retrieved from the 'RAPIDAPI_KEY' environment variable.
#     If not found, an empty string is returned.
#     """
#     return os.getenv("RAPIDAPI_KEY", "")

# def get_finnazon_key() -> str:
#     """
#     Retrieves the FinnaZon API key from the environment variables.

#     Returns
#     -------
#     key: str
#         The FinnaZon API key as a string.

#     Notes
#     -----
#     The FinnaZon API key is retrieved from the 'FINNAZON_API_KEY' environment
#     variable. If not found, an empty string is returned.
#     """
#     key: str = os.getenv("FINNAZON_API_KEY", "")
#     return key

# def get_intrinio_key() -> str:
#     """
#     Retrieves the Intrinio API key from the environment variables.

#     Returns
#     -------
#     str
#         The Intrinio API key as a string.

#     Notes
#     -----
#     The Intrinio API key is retrieved from the 'INTRINIO_API_KEY' environment
#     variable. If not found, an empty string is returned.
#     """
#     return os.getenv("INTRINIO_API_KEY", "")
"""
Configuration module for the stock poller.

Provides typed getter functions to retrieve configuration values from HashiCorp Vault,
environment variables, or defaults — in that order.
"""

import os

from app.utils.vault_client import load_vault_secrets

# Load and cache Vault secrets from centralized Vault client
_vault_config: dict[str, str] = load_vault_secrets()


def get_config_value(key: str, default: str | None = None) -> str | None:
    """
    Retrieve a configuration value from Vault, environment variable, or default.

    Parameters
    ----------
    key : str
        The configuration key to retrieve.
    default : Optional[str]
        The fallback value if neither Vault nor environment contain the key.

    Returns
    -------
    Optional[str]
        The configuration value as a string, or None.
    """
    return _vault_config.get(key, os.getenv(key, default))


# ------------------------------------------------------------------------------
# 🔧 General Configuration
# ------------------------------------------------------------------------------


def get_log_level() -> str:
    """
    Get the configured log level.

    Returns
    -------
    str
        One of "debug", "info", "warning", "error", or "critical". Default is "info".
    """
    return get_config_value("LOG_LEVEL", "info")


def get_log_dir() -> str:
    """
    Get the path to the logging directory.

    Returns
    -------
    str
        Log directory path. Default is "/app/logs".
    """
    return get_config_value("LOG_DIR", "/app/logs")


def get_data_source() -> str:
    """
    Get the data source used in the current run.

    Returns
    -------
    str
        Data source identifier. Default is "yahoo_rapidapi".
    """
    return get_config_value("DATA_SOURCE", "yahoo_rapidapi")


def get_symbols() -> list[str]:
    """
    Get the list of stock symbols to poll.

    Returns
    -------
    list[str]
        List of symbols from the "SYMBOLS" config. Defaults to ["AAPL", "GOOG", "MSFT"].
    """
    symbols_str: str = get_config_value("SYMBOLS", "AAPL,GOOG,MSFT")
    return symbols_str.split(",")


def get_poll_interval() -> int:
    """
    Get the polling interval in seconds.

    Returns
    -------
    int
        Time between polls. Default is 60.
    """
    return int(get_config_value("POLL_INTERVAL", 60))


def get_poll_timeout() -> int:
    """
    Get the timeout for polling.

    Returns
    -------
    int
        Timeout duration in seconds. Default is 30.
    """
    return int(get_config_value("POLL_TIMEOUT", 30))


def get_request_timeout() -> int:
    """
    Get the HTTP request timeout for API calls.

    Returns
    -------
    int
        Timeout duration in seconds. Default is 30.
    """
    return int(get_config_value("REQUEST_TIMEOUT", 30))


# ------------------------------------------------------------------------------
# 🔁 Retry & Backfill
# ------------------------------------------------------------------------------


def get_max_retries() -> int:
    """
    Get the number of times to retry failed API requests.

    Returns
    -------
    int
        Maximum retries. Default is 3.
    """
    return int(get_config_value("MAX_RETRIES", 3))


def get_retry_delay() -> int:
    """
    Get the delay between retries in seconds.

    Returns
    -------
    int
        Delay duration. Default is 5.
    """
    return int(get_config_value("RETRY_DELAY", 5))


def is_retry_enabled() -> bool:
    """
    Determine if retry is enabled.

    Returns
    -------
    bool
        True if enabled, else False.
    """
    return get_config_value("ENABLE_RETRY", "true") == "true"


def is_backfill_enabled() -> bool:
    """
    Determine if backfill is enabled.

    Returns
    -------
    bool
        True if enabled, else False.
    """
    return get_config_value("ENABLE_BACKFILL", "false") == "true"


# ------------------------------------------------------------------------------
# 🧪 Logging Flags
# ------------------------------------------------------------------------------


def is_logging_enabled() -> bool:
    """
    Check if logging is enabled.

    Returns
    -------
    bool
        True if enabled, else False.
    """
    return get_config_value("ENABLE_LOGGING", "true") == "true"


def is_cloud_logging_enabled() -> bool:
    """
    Check if cloud logging is enabled.

    Returns
    -------
    bool
        True if enabled, else False.
    """
    return get_config_value("CLOUD_LOGGING_ENABLED", "false") == "true"


# ------------------------------------------------------------------------------
# 📊 Poller Configuration
# ------------------------------------------------------------------------------


def get_poller_type() -> str:
    """
    Get the poller type (e.g. "yfinance").

    Returns
    -------
    str
        Poller type identifier.
    """
    return get_config_value("POLLER_TYPE", "yfinance")


def get_poller_fill_rate_limit() -> int:
    """
    Get the base API fill rate limit.

    Returns
    -------
    int
        Requests per minute. Defaults to value of "RATE_LIMIT" or 0.
    """
    return int(get_config_value("POLLER_FILL_RATE_LIMIT", get_config_value("RATE_LIMIT", 0)))


def get_yfinance_fill_rate_limit() -> int:
    """YFinance specific rate limit."""
    return int(get_config_value("YFINANCE_FILL_RATE_LIMIT", get_poller_fill_rate_limit()))


def get_iex_fill_rate_limit() -> int:
    """IEX specific rate limit."""
    return int(get_config_value("IEX_FILL_RATE_LIMIT", get_poller_fill_rate_limit()))


def get_finnhub_fill_rate_limit() -> int:
    """Finnhub specific rate limit."""
    return int(get_config_value("FINNHUB_FILL_RATE_LIMIT", get_poller_fill_rate_limit()))


def get_polygon_fill_rate_limit() -> int:
    """Polygon specific rate limit."""
    return int(get_config_value("POLYGON_FILL_RATE_LIMIT", get_poller_fill_rate_limit()))


def get_alpha_vantage_fill_rate_limit() -> int:
    """Alpha Vantage specific rate limit."""
    return int(get_config_value("ALPHA_VANTAGE_FILL_RATE_LIMIT", get_poller_fill_rate_limit()))


def get_quandl_fill_rate_limit() -> int:
    """Quandl specific rate limit."""
    return int(get_config_value("QUANDL_FILL_RATE_LIMIT", get_poller_fill_rate_limit()))


def get_intrinio_fill_rate_limit() -> int:
    """Intrinio specific rate limit."""
    return int(get_config_value("INTRINIO_FILL_RATE_LIMIT", get_poller_fill_rate_limit()))


def get_rapidapi_fill_rate_limit() -> int:
    """RapidAPI specific rate limit."""
    return int(get_config_value("RAPIDAPI_FILL_RATE_LIMIT", get_poller_fill_rate_limit()))


def get_finnazon_fill_rate_limit() -> int:
    """Finnazon specific rate limit."""
    return int(get_config_value("FINNAZON_FILL_RATE_LIMIT", get_poller_fill_rate_limit()))


# ------------------------------------------------------------------------------
# 🔐 API Keys
# ------------------------------------------------------------------------------


def get_yfinance_key() -> str:
    """YFinance API key."""
    return get_config_value("YFINANCE_API_KEY", "")


def get_iex_key() -> str:
    """IEX API key."""
    return get_config_value("IEX_API_KEY", "")


def get_finnhub_key() -> str:
    """Finnhub API key."""
    return get_config_value("FINNHUB_API_KEY", "")


def get_polygon_key() -> str:
    """Polygon API key."""
    return get_config_value("POLYGON_API_KEY", "")


def get_alpha_vantage_key() -> str:
    """Alpha Vantage API key."""
    return get_config_value("ALPHA_VANTAGE_API_KEY", "")


def get_quandl_key() -> str:
    """Quandl API key."""
    return get_config_value("QUANDL_API_KEY", "")


def get_intrinio_key() -> str:
    """Intrinio API key."""
    return get_config_value("INTRINIO_API_KEY", "")


def get_rapidapi_key() -> str:
    """RapidAPI key."""
    return get_config_value("RAPIDAPI_KEY", "")


def get_finnazon_key() -> str:
    """Finnazon API key."""
    return get_config_value("FINNAZON_API_KEY", "")


# ------------------------------------------------------------------------------
# 📬 Queue Configuration
# ------------------------------------------------------------------------------


def get_queue_type() -> str:
    """
    Get the messaging queue type.

    Returns
    -------
    str
        Either "rabbitmq" or "sqs".
    """
    return get_config_value("QUEUE_TYPE", "rabbitmq")


# -- RabbitMQ


def get_rabbitmq_host() -> str:
    """RabbitMQ host name or IP."""
    return get_config_value("RABBITMQ_HOST", "localhost")


def get_rabbitmq_port() -> int:
    """RabbitMQ port number."""
    return int(get_config_value("RABBITMQ_PORT", 5672))


def get_rabbitmq_exchange() -> str:
    """RabbitMQ exchange name."""
    return get_config_value("RABBITMQ_EXCHANGE", "stock_data_exchange")


def get_rabbitmq_routing_key() -> str:
    """RabbitMQ routing key for publishing."""
    return get_config_value("RABBITMQ_ROUTING_KEY", "stock_data")


def get_rabbitmq_vhost() -> str:
    """
    Get the RabbitMQ virtual host.

    Returns
    -------
    str
        Virtual host name.

    Raises
    ------
    ValueError
        If not configured.
    """
    vhost: str | None = get_config_value("RABBITMQ_VHOST")
    if not vhost:
        raise ValueError("❌ Missing required config: RABBITMQ_VHOST must be set.")
    return vhost


def get_rabbitmq_user() -> str:
    """RabbitMQ username."""
    return get_config_value("RABBITMQ_USER", "")


def get_rabbitmq_password() -> str:
    """RabbitMQ password."""
    return get_config_value("RABBITMQ_PASS", "")


# -- AWS SQS


def get_sqs_queue_url() -> str:
    """SQS queue URL."""
    return get_config_value("SQS_QUEUE_URL", "")
