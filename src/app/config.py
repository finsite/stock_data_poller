"""Configuration module for the stock poller.

Provides typed getter functions to retrieve configuration values from HashiCorp Vault,
environment variables, or defaults — in that order.
"""

import os

from app.utils.vault_client import VaultClient

# Initialize and cache Vault client
_vault = VaultClient()


def get_config_value(key: str, default: str | None = None) -> str:
    """Retrieve a configuration value from Vault, environment variable, or default."""
    val = _vault.get(key, os.getenv(key))
    if val is None:
        if default is not None:
            return str(default)
        raise ValueError(f"❌ Missing required config for key: {key}")
    return str(val)


# --------------------------------------------------------------------------
# 🔧 General Configuration
# --------------------------------------------------------------------------


def get_log_level() -> str:
    return get_config_value("LOG_LEVEL", "info")


def get_log_dir() -> str:
    return get_config_value("LOG_DIR", "/app/logs")


def get_data_source() -> str:
    return get_config_value("DATA_SOURCE", "yahoo_rapidapi")


def get_symbols() -> list[str]:
    return get_config_value("SYMBOLS", "AAPL,GOOG,MSFT").split(",")


def get_poll_interval() -> int:
    return int(get_config_value("POLL_INTERVAL", "60"))


def get_poll_timeout() -> int:
    return int(get_config_value("POLL_TIMEOUT", "30"))


def get_request_timeout() -> int:
    return int(get_config_value("REQUEST_TIMEOUT", "30"))


# --------------------------------------------------------------------------
# 🔁 Retry & Backfill
# --------------------------------------------------------------------------


def get_max_retries() -> int:
    return int(get_config_value("MAX_RETRIES", "3"))


def get_retry_delay() -> int:
    return int(get_config_value("RETRY_DELAY", "5"))


def is_retry_enabled() -> bool:
    return get_config_value("ENABLE_RETRY", "true") == "true"


def is_backfill_enabled() -> bool:
    return get_config_value("ENABLE_BACKFILL", "false") == "true"


# --------------------------------------------------------------------------
# 🧪 Logging Flags
# --------------------------------------------------------------------------


def is_logging_enabled() -> bool:
    return get_config_value("ENABLE_LOGGING", "true") == "true"


def is_cloud_logging_enabled() -> bool:
    return get_config_value("CLOUD_LOGGING_ENABLED", "false") == "true"


# --------------------------------------------------------------------------
# 📊 Poller Configuration
# --------------------------------------------------------------------------


def get_poller_type() -> str:
    return get_config_value("POLLER_TYPE", "yfinance")


def get_poller_fill_rate_limit() -> int:
    return int(get_config_value("POLLER_FILL_RATE_LIMIT", get_config_value("RATE_LIMIT", "0")))


def get_yfinance_fill_rate_limit() -> int:
    return int(get_config_value("YFINANCE_FILL_RATE_LIMIT", str(get_poller_fill_rate_limit())))


def get_iex_fill_rate_limit() -> int:
    return int(get_config_value("IEX_FILL_RATE_LIMIT", str(get_poller_fill_rate_limit())))


def get_finnhub_fill_rate_limit() -> int:
    return int(get_config_value("FINNHUB_FILL_RATE_LIMIT", str(get_poller_fill_rate_limit())))


def get_polygon_fill_rate_limit() -> int:
    return int(get_config_value("POLYGON_FILL_RATE_LIMIT", str(get_poller_fill_rate_limit())))


def get_alpha_vantage_fill_rate_limit() -> int:
    return int(get_config_value("ALPHA_VANTAGE_FILL_RATE_LIMIT", str(get_poller_fill_rate_limit())))


def get_quandl_fill_rate_limit() -> int:
    return int(get_config_value("QUANDL_FILL_RATE_LIMIT", str(get_poller_fill_rate_limit())))


def get_intrinio_fill_rate_limit() -> int:
    return int(get_config_value("INTRINIO_FILL_RATE_LIMIT", str(get_poller_fill_rate_limit())))


def get_rapidapi_fill_rate_limit() -> int:
    return int(get_config_value("RAPIDAPI_FILL_RATE_LIMIT", str(get_poller_fill_rate_limit())))


def get_finnazon_fill_rate_limit() -> int:
    return int(get_config_value("FINNAZON_FILL_RATE_LIMIT", str(get_poller_fill_rate_limit())))


# --------------------------------------------------------------------------
# 🔐 API Keys
# --------------------------------------------------------------------------


def get_yfinance_key() -> str:
    return get_config_value("YFINANCE_API_KEY", "")


def get_iex_api_key() -> str:
    return get_config_value("IEX_API_KEY", "")


def get_finnhub_api_key() -> str:
    return get_config_value("FINNHUB_API_KEY", "")


def get_polygon_api_key() -> str:
    return get_config_value("POLYGON_API_KEY", "")


def get_alpha_vantage_api_key() -> str:
    return get_config_value("ALPHA_VANTAGE_API_KEY", "")


def get_quandl_api_key() -> str:
    return get_config_value("QUANDL_API_KEY", "")


def get_intrinio_key() -> str:
    return get_config_value("INTRINIO_API_KEY", "")


def get_rapidapi_key() -> str:
    return get_config_value("RAPIDAPI_KEY", "")


def get_finnazon_key() -> str:
    return get_config_value("FINNAZON_API_KEY", "")


# --------------------------------------------------------------------------
# 📬 Queue Configuration
# --------------------------------------------------------------------------


def get_queue_type() -> str:
    return get_config_value("QUEUE_TYPE", "rabbitmq")


def get_rabbitmq_host() -> str:
    return get_config_value("RABBITMQ_HOST", "localhost")


def get_rabbitmq_port() -> int:
    return int(get_config_value("RABBITMQ_PORT", "5672"))


def get_rabbitmq_exchange() -> str:
    return get_config_value("RABBITMQ_EXCHANGE", "stock_data_exchange")


def get_rabbitmq_routing_key() -> str:
    return get_config_value("RABBITMQ_ROUTING_KEY", "stock_data")


def get_rabbitmq_vhost() -> str:
    vhost = get_config_value("RABBITMQ_VHOST")
    if not vhost:
        raise ValueError("❌ Missing required config: RABBITMQ_VHOST must be set.")
    return vhost


def get_rabbitmq_user() -> str:
    return get_config_value("RABBITMQ_USER", "")


def get_rabbitmq_password() -> str:
    return get_config_value("RABBITMQ_PASS", "")


def get_sqs_queue_url() -> str:
    """Retrieve the SQS queue URL from the configuration.

    Returns
    -------
    str
        The URL of the SQS queue. An empty string is returned if not configured.

    """
    return get_config_value("SQS_QUEUE_URL", "")


def get_sqs_region() -> str:
    """Retrieve the SQS region configuration value.

    Returns
    -------
    str
        The region where the SQS queue is located. Defaults to "us-east-1" if the
        configuration value is not set.

    """
    return get_config_value("SQS_REGION", "us-east-1")


def get_rapidapi_host() -> str:
    """Retrieve the RapidAPI host configuration value.

    Returns
    -------
    str
        The hostname of the RapidAPI service. Defaults to
        "apidojo-yahoo-finance-v1.p.rapidapi.com" if the configuration value is
        not set.

    """
    return get_config_value("RAPIDAPI_HOST", "apidojo-yahoo-finance-v1.p.rapidapi.com")


def get_polling_interval() -> int:
    """Retrieve the polling interval configuration value.

    Returns
    -------
    int
        The polling interval in seconds. Defaults to 60 seconds if the
        environment variable POLLING_INTERVAL is not set.

    """
    return int(get_config_value("POLLING_INTERVAL", "60"))


def get_rate_limit() -> int:
    """Returns the rate limit for the API in requests per second.

    If the environment variable RATE_LIMIT is set, its value is used.
    Otherwise, 0 is returned, meaning no rate limit is enforced.
    """
    return int(get_config_value("RATE_LIMIT", "0"))


def get_batch_size() -> int:
    """Retrieve the batch size configuration value.

    Returns
    -------
    int
        The batch size for polling or sending messages. Defaults to 10 if the
        environment variable BATCH_SIZE is not set.

    """
    return int(get_config_value("BATCH_SIZE", "10"))
