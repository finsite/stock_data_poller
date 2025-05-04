# """
# Configuration module for the stock poller.

# Provides typed getter functions to retrieve configuration values from HashiCorp Vault,
# environment variables, or defaults — in that order.
# """

# import os

# from app.utils.vault_client import load_vault_secrets

# # Load and cache Vault secrets from centralized Vault client
# _vault_config: dict[str, str] = load_vault_secrets()


# def get_config_value(key: str, default: str | None = None) -> str | None:
#     """
#     Retrieve a configuration value from Vault, environment variable, or default.

#     Parameters
#     ----------
#     key : str
#         The configuration key to retrieve.
#     default : Optional[str]
#         The fallback value if neither Vault nor environment contain the key.

#     Returns
#     -------
#     Optional[str]
#         The configuration value as a string, or None.
#     """
#     return _vault_config.get(key, os.getenv(key, default))


# # ------------------------------------------------------------------------------
# # 🔧 General Configuration
# # ------------------------------------------------------------------------------


# def get_log_level() -> str:
#     """
#     Get the configured log level.

#     Returns
#     -------
#     str
#         One of "debug", "info", "warning", "error", or "critical". Default is "info".
#     """
#     return get_config_value("LOG_LEVEL", "info")


# def get_log_dir() -> str:
#     """
#     Get the path to the logging directory.

#     Returns
#     -------
#     str
#         Log directory path. Default is "/app/logs".
#     """
#     return get_config_value("LOG_DIR", "/app/logs")


# def get_data_source() -> str:
#     """
#     Get the data source used in the current run.

#     Returns
#     -------
#     str
#         Data source identifier. Default is "yahoo_rapidapi".
#     """
#     return get_config_value("DATA_SOURCE", "yahoo_rapidapi")


# def get_symbols() -> list[str]:
#     """
#     Get the list of stock symbols to poll.

#     Returns
#     -------
#     list[str]
#         List of symbols from the "SYMBOLS" config. Defaults to ["AAPL", "GOOG", "MSFT"].
#     """
#     symbols_str: str = get_config_value("SYMBOLS", "AAPL,GOOG,MSFT")
#     return symbols_str.split(",")


# def get_poll_interval() -> int:
#     """
#     Get the polling interval in seconds.

#     Returns
#     -------
#     int
#         Time between polls. Default is 60.
#     """
#     return int(get_config_value("POLL_INTERVAL", 60))


# def get_poll_timeout() -> int:
#     """
#     Get the timeout for polling.

#     Returns
#     -------
#     int
#         Timeout duration in seconds. Default is 30.
#     """
#     return int(get_config_value("POLL_TIMEOUT", 30))


# def get_request_timeout() -> int:
#     """
#     Get the HTTP request timeout for API calls.

#     Returns
#     -------
#     int
#         Timeout duration in seconds. Default is 30.
#     """
#     return int(get_config_value("REQUEST_TIMEOUT", 30))


# # ------------------------------------------------------------------------------
# # 🔁 Retry & Backfill
# # ------------------------------------------------------------------------------


# def get_max_retries() -> int:
#     """
#     Get the number of times to retry failed API requests.

#     Returns
#     -------
#     int
#         Maximum retries. Default is 3.
#     """
#     return int(get_config_value("MAX_RETRIES", 3))


# def get_retry_delay() -> int:
#     """
#     Get the delay between retries in seconds.

#     Returns
#     -------
#     int
#         Delay duration. Default is 5.
#     """
#     return int(get_config_value("RETRY_DELAY", 5))


# def is_retry_enabled() -> bool:
#     """
#     Determine if retry is enabled.

#     Returns
#     -------
#     bool
#         True if enabled, else False.
#     """
#     return get_config_value("ENABLE_RETRY", "true") == "true"


# def is_backfill_enabled() -> bool:
#     """
#     Determine if backfill is enabled.

#     Returns
#     -------
#     bool
#         True if enabled, else False.
#     """
#     return get_config_value("ENABLE_BACKFILL", "false") == "true"


# # ------------------------------------------------------------------------------
# # 🧪 Logging Flags
# # ------------------------------------------------------------------------------


# def is_logging_enabled() -> bool:
#     """
#     Check if logging is enabled.

#     Returns
#     -------
#     bool
#         True if enabled, else False.
#     """
#     return get_config_value("ENABLE_LOGGING", "true") == "true"


# def is_cloud_logging_enabled() -> bool:
#     """
#     Check if cloud logging is enabled.

#     Returns
#     -------
#     bool
#         True if enabled, else False.
#     """
#     return get_config_value("CLOUD_LOGGING_ENABLED", "false") == "true"


# # ------------------------------------------------------------------------------
# # 📊 Poller Configuration
# # ------------------------------------------------------------------------------


# def get_poller_type() -> str:
#     """
#     Get the poller type (e.g. "yfinance").

#     Returns
#     -------
#     str
#         Poller type identifier.
#     """
#     return get_config_value("POLLER_TYPE", "yfinance")


# def get_poller_fill_rate_limit() -> int:
#     """
#     Get the base API fill rate limit.

#     Returns
#     -------
#     int
#         Requests per minute. Defaults to value of "RATE_LIMIT" or 0.
#     """
#     return int(get_config_value("POLLER_FILL_RATE_LIMIT", get_config_value("RATE_LIMIT", 0)))


# def get_yfinance_fill_rate_limit() -> int:
#     """YFinance specific rate limit."""
#     return int(get_config_value("YFINANCE_FILL_RATE_LIMIT", get_poller_fill_rate_limit()))


# def get_iex_fill_rate_limit() -> int:
#     """IEX specific rate limit."""
#     return int(get_config_value("IEX_FILL_RATE_LIMIT", get_poller_fill_rate_limit()))


# def get_finnhub_fill_rate_limit() -> int:
#     """Finnhub specific rate limit."""
#     return int(get_config_value("FINNHUB_FILL_RATE_LIMIT", get_poller_fill_rate_limit()))


# def get_polygon_fill_rate_limit() -> int:
#     """Polygon specific rate limit."""
#     return int(get_config_value("POLYGON_FILL_RATE_LIMIT", get_poller_fill_rate_limit()))


# def get_alpha_vantage_fill_rate_limit() -> int:
#     """Alpha Vantage specific rate limit."""
#     return int(get_config_value("ALPHA_VANTAGE_FILL_RATE_LIMIT", get_poller_fill_rate_limit()))


# def get_quandl_fill_rate_limit() -> int:
#     """Quandl specific rate limit."""
#     return int(get_config_value("QUANDL_FILL_RATE_LIMIT", get_poller_fill_rate_limit()))


# def get_intrinio_fill_rate_limit() -> int:
#     """Intrinio specific rate limit."""
#     return int(get_config_value("INTRINIO_FILL_RATE_LIMIT", get_poller_fill_rate_limit()))


# def get_rapidapi_fill_rate_limit() -> int:
#     """RapidAPI specific rate limit."""
#     return int(get_config_value("RAPIDAPI_FILL_RATE_LIMIT", get_poller_fill_rate_limit()))


# def get_finnazon_fill_rate_limit() -> int:
#     """Finnazon specific rate limit."""
#     return int(get_config_value("FINNAZON_FILL_RATE_LIMIT", get_poller_fill_rate_limit()))


# # ------------------------------------------------------------------------------
# # 🔐 API Keys
# # ------------------------------------------------------------------------------


# def get_yfinance_key() -> str:
#     """YFinance API key."""
#     return get_config_value("YFINANCE_API_KEY", "")


# def get_iex_api_key() -> str:
#     """IEX API key."""
#     return get_config_value("IEX_API_KEY", "")


# def get_finnhub_api_key() -> str:
#     """Finnhub API key."""
#     return get_config_value("FINNHUB_API_KEY", "")


# def get_polygon_api_key() -> str:
#     """Polygon API key."""
#     return get_config_value("POLYGON_API_KEY", "")


# def get_alpha_vantage_api_key() -> str:
#     """Alpha Vantage API key."""
#     return get_config_value("ALPHA_VANTAGE_API_KEY", "")


# def get_quandl_api_key() -> str:
#     """Quandl API key."""
#     return get_config_value("QUANDL_API_KEY", "")


# def get_intrinio_key() -> str:
#     """Intrinio API key."""
#     return get_config_value("INTRINIO_API_KEY", "")


# def get_rapidapi_key() -> str:
#     """RapidAPI key."""
#     return get_config_value("RAPIDAPI_KEY", "")


# def get_finnazon_key() -> str:
#     """Finnazon API key."""
#     return get_config_value("FINNAZON_API_KEY", "")


# # ------------------------------------------------------------------------------
# # 📬 Queue Configuration
# # ------------------------------------------------------------------------------


# def get_queue_type() -> str:
#     """
#     Get the messaging queue type.

#     Returns
#     -------
#     str
#         Either "rabbitmq" or "sqs".
#     """
#     return get_config_value("QUEUE_TYPE", "rabbitmq")


# # -- RabbitMQ


# def get_rabbitmq_host() -> str:
#     """RabbitMQ host name or IP."""
#     return get_config_value("RABBITMQ_HOST", "localhost")


# def get_rabbitmq_port() -> int:
#     """RabbitMQ port number."""
#     return int(get_config_value("RABBITMQ_PORT", 5672))


# def get_rabbitmq_exchange() -> str:
#     """RabbitMQ exchange name."""
#     return get_config_value("RABBITMQ_EXCHANGE", "stock_data_exchange")


# def get_rabbitmq_routing_key() -> str:
#     """RabbitMQ routing key for publishing."""
#     return get_config_value("RABBITMQ_ROUTING_KEY", "stock_data")


# def get_rabbitmq_vhost() -> str:
#     """
#     Get the RabbitMQ virtual host.

#     Returns
#     -------
#     str
#         Virtual host name.

#     Raises
#     ------
#     ValueError
#         If not configured.
#     """
#     vhost: str | None = get_config_value("RABBITMQ_VHOST")
#     if not vhost:
#         raise ValueError("❌ Missing required config: RABBITMQ_VHOST must be set.")
#     return vhost


# def get_rabbitmq_user() -> str:
#     """RabbitMQ username."""
#     return get_config_value("RABBITMQ_USER", "")


# def get_rabbitmq_password() -> str:
#     """RabbitMQ password."""
#     return get_config_value("RABBITMQ_PASS", "")


# # -- AWS SQS


# def get_sqs_queue_url() -> str:
#     """SQS queue URL."""
#     return get_config_value("SQS_QUEUE_URL", "")

# def get_rate_limit() -> int:
#     """
#     Get the general rate limit if a poller-specific one isn't set.

#     Returns
#     -------
#     int
#         Default max requests per minute. Defaults to 0 (no limit).
#     """
#     return int(get_config_value("RATE_LIMIT", 0))
"""
Configuration module for the stock poller.

Provides typed getter functions to retrieve configuration values from HashiCorp Vault,
environment variables, or defaults — in that order.
"""

import os

from app.utils.vault_client import load_vault_secrets

# Load and cache Vault secrets from centralized Vault client
_vault_config: dict[str, str] = load_vault_secrets()


def get_config_value(key: str, default: str | None = None) -> str:
    """
    Retrieve a configuration value from Vault, environment variable, or default.

    Args:
      key(str): The configuration key to retrieve.
      default(Optional[str]): The fallback value if neither Vault nor environment contain the key.
      key: str:
      default: str | None:  (Default value = None)

    Returns:
      str: The configuration value as a string.
    """
    val = _vault_config.get(key, os.getenv(key))
    if val is None:
        if default is not None:
            return str(default)
        raise ValueError(f"Missing required config for key: {key}")
    return val


# --------------------------------------------------------------------------
# 🔧 General Configuration
# --------------------------------------------------------------------------


def get_log_level() -> str:
    """"""
    return get_config_value("LOG_LEVEL", "info")


def get_log_dir() -> str:
    """"""
    return get_config_value("LOG_DIR", "/app/logs")


def get_data_source() -> str:
    """"""
    return get_config_value("DATA_SOURCE", "yahoo_rapidapi")


def get_symbols() -> list[str]:
    """"""
    return get_config_value("SYMBOLS", "AAPL,GOOG,MSFT").split(",")


def get_poll_interval() -> int:
    """"""
    return int(get_config_value("POLL_INTERVAL", "60"))


def get_poll_timeout() -> int:
    """"""
    return int(get_config_value("POLL_TIMEOUT", "30"))


def get_request_timeout() -> int:
    """"""
    return int(get_config_value("REQUEST_TIMEOUT", "30"))


# --------------------------------------------------------------------------
# 🔁 Retry & Backfill
# --------------------------------------------------------------------------


def get_max_retries() -> int:
    """"""
    return int(get_config_value("MAX_RETRIES", "3"))


def get_retry_delay() -> int:
    """"""
    return int(get_config_value("RETRY_DELAY", "5"))


def is_retry_enabled() -> bool:
    """"""
    return get_config_value("ENABLE_RETRY", "true") == "true"


def is_backfill_enabled() -> bool:
    """"""
    return get_config_value("ENABLE_BACKFILL", "false") == "true"


# --------------------------------------------------------------------------
# 🧪 Logging Flags
# --------------------------------------------------------------------------


def is_logging_enabled() -> bool:
    """"""
    return get_config_value("ENABLE_LOGGING", "true") == "true"


def is_cloud_logging_enabled() -> bool:
    """"""
    return get_config_value("CLOUD_LOGGING_ENABLED", "false") == "true"


# --------------------------------------------------------------------------
# 📊 Poller Configuration
# --------------------------------------------------------------------------


def get_poller_type() -> str:
    """"""
    return get_config_value("POLLER_TYPE", "yfinance")


def get_poller_fill_rate_limit() -> int:
    """"""
    return int(get_config_value("POLLER_FILL_RATE_LIMIT", get_config_value("RATE_LIMIT", "0")))


def get_yfinance_fill_rate_limit() -> int:
    """"""
    return int(get_config_value("YFINANCE_FILL_RATE_LIMIT", str(get_poller_fill_rate_limit())))


def get_iex_fill_rate_limit() -> int:
    """"""
    return int(get_config_value("IEX_FILL_RATE_LIMIT", str(get_poller_fill_rate_limit())))


def get_finnhub_fill_rate_limit() -> int:
    """"""
    return int(get_config_value("FINNHUB_FILL_RATE_LIMIT", str(get_poller_fill_rate_limit())))


def get_polygon_fill_rate_limit() -> int:
    """"""
    return int(get_config_value("POLYGON_FILL_RATE_LIMIT", str(get_poller_fill_rate_limit())))


def get_alpha_vantage_fill_rate_limit() -> int:
    """"""
    return int(get_config_value("ALPHA_VANTAGE_FILL_RATE_LIMIT", str(get_poller_fill_rate_limit())))


def get_quandl_fill_rate_limit() -> int:
    """"""
    return int(get_config_value("QUANDL_FILL_RATE_LIMIT", str(get_poller_fill_rate_limit())))


def get_intrinio_fill_rate_limit() -> int:
    """"""
    return int(get_config_value("INTRINIO_FILL_RATE_LIMIT", str(get_poller_fill_rate_limit())))


def get_rapidapi_fill_rate_limit() -> int:
    """"""
    return int(get_config_value("RAPIDAPI_FILL_RATE_LIMIT", str(get_poller_fill_rate_limit())))


def get_finnazon_fill_rate_limit() -> int:
    """"""
    return int(get_config_value("FINNAZON_FILL_RATE_LIMIT", str(get_poller_fill_rate_limit())))


# --------------------------------------------------------------------------
# 🔐 API Keys
# --------------------------------------------------------------------------


def get_yfinance_key() -> str:
    """"""
    return get_config_value("YFINANCE_API_KEY", "")


def get_iex_api_key() -> str:
    """"""
    return get_config_value("IEX_API_KEY", "")


def get_finnhub_api_key() -> str:
    """"""
    return get_config_value("FINNHUB_API_KEY", "")


def get_polygon_api_key() -> str:
    """"""
    return get_config_value("POLYGON_API_KEY", "")


def get_alpha_vantage_api_key() -> str:
    """"""
    return get_config_value("ALPHA_VANTAGE_API_KEY", "")


def get_quandl_api_key() -> str:
    """"""
    return get_config_value("QUANDL_API_KEY", "")


def get_intrinio_key() -> str:
    """"""
    return get_config_value("INTRINIO_API_KEY", "")


def get_rapidapi_key() -> str:
    """"""
    return get_config_value("RAPIDAPI_KEY", "")


def get_finnazon_key() -> str:
    """"""
    return get_config_value("FINNAZON_API_KEY", "")


# --------------------------------------------------------------------------
# 📬 Queue Configuration
# --------------------------------------------------------------------------


def get_queue_type() -> str:
    """"""
    return get_config_value("QUEUE_TYPE", "rabbitmq")


def get_rabbitmq_host() -> str:
    """"""
    return get_config_value("RABBITMQ_HOST", "localhost")


def get_rabbitmq_port() -> int:
    """"""
    return int(get_config_value("RABBITMQ_PORT", "5672"))


def get_rabbitmq_exchange() -> str:
    """"""
    return get_config_value("RABBITMQ_EXCHANGE", "stock_data_exchange")


def get_rabbitmq_routing_key() -> str:
    """"""
    return get_config_value("RABBITMQ_ROUTING_KEY", "stock_data")


def get_rabbitmq_vhost() -> str:
    """"""
    vhost = get_config_value("RABBITMQ_VHOST")
    if not vhost:
        raise ValueError("❌ Missing required config: RABBITMQ_VHOST must be set.")
    return vhost


def get_rabbitmq_user() -> str:
    """"""
    return get_config_value("RABBITMQ_USER", "")


def get_rabbitmq_password() -> str:
    """"""
    return get_config_value("RABBITMQ_PASS", "")


def get_sqs_queue_url() -> str:
    """"""
    return get_config_value("SQS_QUEUE_URL", "")


def get_rate_limit() -> int:
    """"""
    return int(get_config_value("RATE_LIMIT", "0"))


def get_rapidapi_host() -> str:
    """Get the RapidAPI host used in headers."""
    return get_config_value("RAPIDAPI_HOST", "apidojo-yahoo-finance-v1.p.rapidapi.com")
