"""
Configuration module for the stock poller.

The module provides functions for retrieving configuration values from environment
variables or Vault secrets.
"""

import logging
import os

import hvac

_VAULT_CONFIG: dict | None = None


def load_vault_secrets() -> dict[str, str]:
    """
    Fetch secrets from HashiCorp Vault and return a dictionary of secrets.

    Parameters
    ----------
        None

    Returns
    -------
        dict[str, str]: A dictionary of secrets, or an empty dictionary if the Vault
            secrets cannot be loaded.
    """
    # Get the Vault address from the environment variable
    VAULT_ADDR: str = os.getenv("VAULT_ADDR", "http://vault:8200")
    # Get the Vault token from the environment variable
    VAULT_TOKEN: str | None = os.getenv("VAULT_TOKEN")

    logger = logging.getLogger(__name__)

    if not VAULT_TOKEN:
        # If the VAULT_TOKEN is not set, log a warning and return an empty dictionary
        logger.warning("VAULT_TOKEN not set. Skipping Vault secret load.")
        return {}

    try:
        # Create a Vault client with the given VAULT_ADDR and VAULT_TOKEN
        client = hvac.Client(url=VAULT_ADDR, token=VAULT_TOKEN)

        # Check if the client is authenticated
        if not client.is_authenticated():
            logger.warning("Vault authentication failed.")
            return {}

        # Read the secrets from Vault
        secrets: dict[str, str] = client.secrets.kv.v2.read_secret_version(path="poller")["data"][
            "data"
        ]
        # Log a success message
        logger.info("Successfully loaded secrets from Vault.")
        # Return the secrets
        return secrets

    except Exception as e:
        # Log a warning if the Vault is not available or if there is an error
        logger.warning(f"Vault not available or failed: {e}")
        # Return an empty dictionary
        return {}


def get_vault_config() -> dict[str, str]:
    """
    Lazy-load and cache Vault secrets.

    If the Vault configuration has not been loaded yet, load it from Vault
    and cache it in the `_VAULT_CONFIG` variable. If it has been loaded,
    return the cached configuration.

    This function is used to avoid loading the Vault configuration multiple
    times, which can be useful if the configuration is used in multiple places
    in the code.

    Returns
    -------
    dict[str, str]
        A dictionary of Vault secrets.
    """
    global _VAULT_CONFIG
    if _VAULT_CONFIG is None:
        # Load secrets from Vault and cache them
        _VAULT_CONFIG = load_vault_secrets()
    return _VAULT_CONFIG


def get_config_value(key: str, default: str | None = None) -> str | None:
    """
    Retrieve a configuration value from Vault, environment, or default.

    This function attempts to get the specified configuration value by first
    checking the Vault secrets. If the key is not found in Vault, it checks
    the environment variables. If the key is also not found in the environment,
    it returns the provided default value.

    Parameters
    ----------
    key : str
        The key to look up in Vault and environment variables.
    default : Optional[str], optional
        The default value to return if the key is not found in Vault or
        environment variables. Defaults to None.

    Returns
    -------
    str | None
        The configuration value for the given key, or the default if not found.
    """
    # Attempt to retrieve the value from Vault secrets
    vault_config = get_vault_config()

    # Retrieve the value from Vault, or fall back to the environment variable
    return vault_config.get(key, os.getenv(key, default))


# --- Getter functions below ---


def get_symbols() -> list[str]:
    """
    Get the list of symbols from the configuration.

    The function returns a list of stock symbols to poll, either from the
    Vault secrets or the environment variable SYMBOLS.

    Returns
    -------
    list[str]
        A list of stock symbols to poll.
    """
    return get_config_value("SYMBOLS", "AAPL,GOOG,MSFT").split(",")


def get_poller_type() -> str:
    """
    Get the type of poller from the configuration.

    The function returns the type of poller to use, either from the
    Vault secrets or the environment variable POLLER_TYPE.

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

    The function fetches the type of message queue to be used,
    either from the Vault secrets or the environment variable
    QUEUE_TYPE. Defaults to 'rabbitmq' if not specified.

    Returns
    -------
    str
        The type of queue to be used.
    """
    return get_config_value("QUEUE_TYPE", "rabbitmq")


def get_rabbitmq_host() -> str:
    """
    Get the RabbitMQ host from the configuration.

    The function returns the RabbitMQ host, either from the Vault secrets
    or the environment variable RABBITMQ_HOST. If not specified, it defaults
    to "localhost".

    Returns
    -------
    str
        The RabbitMQ host.
    """
    return get_config_value("RABBITMQ_HOST", "localhost")


def get_rabbitmq_exchange() -> str:
    """
    Retrieve the RabbitMQ exchange name from the configuration.

    The function fetches the RabbitMQ exchange name either from Vault
    secrets or from the environment variable RABBITMQ_EXCHANGE. If neither
    is set, it defaults to 'stock_data_exchange'.

    Returns
    -------
    str
        The RabbitMQ exchange name.
    """
    return get_config_value("RABBITMQ_EXCHANGE", "stock_data_exchange")


def get_rabbitmq_routing_key() -> str:
    """
    Get the RabbitMQ routing key from the configuration.

    The function fetches the RabbitMQ routing key either from Vault
    secrets or from the environment variable RABBITMQ_ROUTING_KEY. If
    neither is set, it defaults to 'stock_data'.

    Returns
    -------
    str
        The RabbitMQ routing key.
    """
    # Fetch the RabbitMQ routing key, defaulting to 'stock_data'
    return get_config_value("RABBITMQ_ROUTING_KEY", "stock_data")


def get_rabbitmq_vhost() -> str:
    """
    Get the RabbitMQ virtual host from the configuration.

    This function retrieves the RabbitMQ virtual host from Vault secrets
    or the environment variable RABBITMQ_VHOST. If neither is set, it
    raises an error to avoid falling back to an inaccessible default.

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

    The function fetches the SQS queue URL either from Vault secrets or
    from the environment variable SQS_QUEUE_URL. If neither is set, it
    defaults to an empty string.

    Returns
    -------
    str
        The SQS queue URL.
    """
    return get_config_value("SQS_QUEUE_URL", "")


def get_poll_interval() -> int:
    """
    Get the poll interval from the configuration.

    The function fetches the poll interval from Vault secrets or the
    environment variable POLL_INTERVAL. If neither is set, it defaults
    to 60 seconds.

    Returns
    -------
    int
        The poll interval in seconds.
    """
    return int(get_config_value("POLL_INTERVAL", 60))


def get_request_timeout() -> int:
    """
    Get the request timeout from the configuration.

    The function fetches the request timeout from Vault secrets or the
    environment variable REQUEST_TIMEOUT. If neither is set, it defaults
    to 30 seconds.

    Returns
    -------
    int
        The request timeout in seconds.
    """
    return int(get_config_value("REQUEST_TIMEOUT", 30))


def get_max_retries() -> int:
    """
    Get the maximum number of retries from the configuration.

    The function fetches the maximum number of retries from Vault secrets or
    the environment variable MAX_RETRIES. If neither is set, it defaults to
    3.

    Returns
    -------
    int
        The maximum number of retries.
    """
    return int(get_config_value("MAX_RETRIES", 3))


def get_retry_delay() -> int:
    """
    Retrieve the retry delay from the configuration.

    The function fetches the retry delay from the configuration,
    either from Vault secrets or the environment variable RETRY_DELAY.
    If neither is set, it defaults to 5 seconds.

    Returns
    -------
    int
        The retry delay in seconds.
    """
    # Fetch the retry delay from configuration, defaulting to 5 seconds
    return int(get_config_value("RETRY_DELAY", 5))


def get_poll_timeout() -> int:
    """
    Get the poll timeout from the configuration.

    The function fetches the poll timeout from Vault secrets or the
    environment variable POLL_TIMEOUT. If neither is set, it defaults
    to 30 seconds.

    Returns
    -------
    int
        The poll timeout in seconds.
    """
    return int(get_config_value("POLL_TIMEOUT", 30))


def get_log_level() -> str:
    """
    Get the log level from the configuration.

    The function fetches the log level from the configuration, either from Vault
    secrets or the environment variable LOG_LEVEL. If neither is set, it defaults
    to "info".

    Returns
    -------
    str
        The log level.
    """
    return get_config_value("LOG_LEVEL", "info")


def is_logging_enabled() -> bool:
    """
    Check if logging is enabled from the configuration.

    The function checks the environment variable ENABLE_LOGGING and
    returns True if it is set to "true", and False otherwise.

    Returns
    -------
    bool
        True if logging is enabled, False otherwise.
    """
    return get_config_value("ENABLE_LOGGING", "true") == "true"


def is_cloud_logging_enabled() -> bool:
    """
    Check if cloud logging is enabled from the configuration.

    The function checks the configuration for the 'CLOUD_LOGGING_ENABLED'
    key to determine if cloud logging should be enabled. It defaults to
    'false' if the key is not present.

    Parameters
    ----------
    None

    Returns
    -------
    bool
        True if cloud logging is enabled, False otherwise.
    """
    # Retrieve the cloud logging enabled status from the configuration
    return get_config_value("CLOUD_LOGGING_ENABLED", "false") == "true"


def is_retry_enabled() -> bool:
    """
    Check if retry is enabled from the configuration.

    The function checks the configuration for the 'ENABLE_RETRY' key to
    determine if retry should be enabled. It defaults to 'true' if the key is
    not present.

    Returns
    -------
    bool
        True if retry is enabled, False otherwise.

    Parameters
    ----------
    None

    Returns
    -------
    bool
        True if retry is enabled, False otherwise.
    """
    return get_config_value("ENABLE_RETRY", "true") == "true"


def is_backfill_enabled() -> bool:
    """
    Check if backfill is enabled from the configuration.

    The function checks the configuration for the 'ENABLE_BACKFILL' key
    to determine if backfill should be enabled. It defaults to 'false' if
    the key is not present.

    Parameters
    ----------
    None

    Returns
    -------
    bool
        True if backfill is enabled, False otherwise.
    """
    # Retrieve the backfill enabled status from the configuration
    return get_config_value("ENABLE_BACKFILL", "false") == "true"


def get_rate_limit() -> int:
    """
    Get the rate limit from the configuration.

    The function fetches the rate limit from the configuration,
    either from Vault secrets or the environment variable RATE_LIMIT.
    If neither is set, it defaults to 5.

    Returns
    -------
    int: The rate limit.
    """
    return int(get_config_value("RATE_LIMIT", 5))


def get_max_api_calls_per_min() -> int:
    """
    Retrieve the maximum number of API calls per minute from the configuration.

    The function fetches the maximum API calls per minute setting
    from the configuration, either from Vault secrets or the environment
    variable MAX_API_CALLS_PER_MIN. If neither is set, it defaults
    to 1000.

    Returns
    -------
    int
        The maximum number of API calls per minute.
    """
    # Fetch the maximum API calls per minute, defaulting to 1000
    return int(get_config_value("MAX_API_CALLS_PER_MIN", 1000))


# --- API Keys ---


def get_polygon_api_key() -> str:
    """
    Get the Polygon API key from the configuration.

    The function fetches the Polygon API key from the configuration,
    either from Vault secrets or the environment variable POLYGON_API_KEY.
    If neither is set, it defaults to an empty string.

    Returns
    -------
    str
        The Polygon API key.
    """
    return get_config_value("POLYGON_API_KEY", "")


def get_finnhub_api_key() -> str:
    """
    Retrieve the Finnhub API key from the configuration.

    The function fetches the Finnhub API key from the configuration,
    either from Vault secrets or the environment variable FINNHUB_API_KEY.
    If neither is set, it defaults to an empty string.

    Returns
    -------
    str
        The Finnhub API key.
    """
    return get_config_value("FINNHUB_API_KEY", "")


def get_alpha_vantage_api_key() -> str:
    """
    Retrieve the Alpha Vantage API key from the configuration.

    The function fetches the Alpha Vantage API key from the configuration,
    either from Vault secrets or the environment variable ALPHA_VANTAGE_API_KEY.
    If neither is set, it defaults to an empty string.

    Returns
    -------
    str
        The Alpha Vantage API key.
    """
    # Fetch the Alpha Vantage API key from the configuration
    return get_config_value("ALPHA_VANTAGE_API_KEY", "")


def get_yfinance_api_key() -> str:
    """
    Retrieve the Yahoo Finance API key from the configuration.

    The function fetches the Yahoo Finance API key from the configuration,
    either from Vault secrets or the environment variable YFINANCE_API_KEY.
    If neither is set, it defaults to an empty string.

    Returns
    -------
    str
        The Yahoo Finance API key as a string.
    """
    # Fetch the Yahoo Finance API key from the configuration
    return get_config_value("YFINANCE_API_KEY", "")


def get_iex_api_key() -> str:
    """
    Retrieves the IEX Cloud API key from the configuration.

    The function fetches the IEX Cloud API key from the configuration,
    either from Vault secrets or the environment variable IEX_API_KEY.
    If neither is set, it defaults to an empty string.

    The IEX Cloud API is a financial data API that provides data on equities, options, and
    forex. It is used in the IEXPoller to fetch the latest prices of the specified symbols.

    Returns
    -------
    str
        The IEX Cloud API key as a string.
    """
    return get_config_value("IEX_API_KEY", "")


def get_quandl_api_key() -> str:
    """
    Retrieve the Quandl API key from the configuration.

    The function fetches the Quandl API key from the configuration,
    either from Vault secrets or the environment variable QUANDL_API_KEY.
    If neither is set, it defaults to an empty string.

    Returns
    -------
    str:
        The Quandl API key.
    """
    # Fetch the Quandl API key from the configuration
    return get_config_value("QUANDL_API_KEY", "")


# --- API Rate Limits ---
def get_alpha_vantage_fill_rate_limit() -> int:
    """
    Get the Alpha Vantage fill rate limit from the configuration.

    The function fetches the Alpha Vantage fill rate limit from the configuration,
    either from Vault secrets or the environment variable
    ALPHA_VANTAGE_FILL_RATE_LIMIT. If neither is set, it defaults to the
    configured rate limit.

    Returns
    -------
    int
        The Alpha Vantage fill rate limit as an integer.
    """
    return int(get_config_value("ALPHA_VANTAGE_FILL_RATE_LIMIT", str(get_rate_limit())))


def get_iex_fill_rate_limit() -> int:
    """
    Get the IEX fill rate limit from the configuration.

    The function fetches the IEX fill rate limit from the configuration,
    either from Vault secrets or the environment variable IEX_FILL_RATE_LIMIT.
    If neither is set, it defaults to the configured rate limit.

    Returns
    -------
    int
        The IEX fill rate limit as an integer.
    """
    return int(get_config_value("IEX_FILL_RATE_LIMIT", str(get_rate_limit())))


def get_finnhub_fill_rate_limit() -> int:
    """
    Get the Finnhub fill rate limit from the configuration.

    The function fetches the Finnhub fill rate limit from the configuration,
    either from Vault secrets or the environment variable FINNHUB_FILL_RATE_LIMIT.
    If neither is set, it defaults to the configured rate limit.

    Returns
    -------
    int
        The Finnhub fill rate limit as an integer.
    """
    return int(get_config_value("FINNHUB_FILL_RATE_LIMIT", str(get_rate_limit())))


def get_polygon_fill_rate_limit() -> int:
    """
    Get the Polygon fill rate limit from the configuration.

    The function fetches the Polygon fill rate limit from the configuration,
    either from Vault secrets or the environment variable POLYGON_FILL_RATE_LIMIT.
    If neither is set, it defaults to the configured rate limit.

    Returns
    -------
    int
        The Polygon fill rate limit as an integer.
    """
    # Fetch the fill rate limit from the configuration with a default fallback
    return int(get_config_value("POLYGON_FILL_RATE_LIMIT", str(get_rate_limit())))


def get_quandl_fill_rate_limit() -> int:
    """
    Get the Quandl fill rate limit from the configuration.

    The function fetches the Quandl fill rate limit from the configuration,
    either from Vault secrets or the environment variable QUANDL_FILL_RATE_LIMIT.
    If neither is set, it defaults to the configured rate limit.

    Returns
    -------
    int
        The Quandl fill rate limit as an integer.
    """
    return int(get_config_value("QUANDL_FILL_RATE_LIMIT", str(get_rate_limit())))


def get_yfinance_fill_rate_limit() -> int:
    """
    Get the Yahoo Finance fill rate limit from the configuration.

    The function fetches the Yahoo Finance fill rate limit from the configuration,
    either from Vault secrets or the environment variable YFINANCE_FILL_RATE_LIMIT.
    If neither is set, it defaults to the configured rate limit.

    Returns
    -------
    int
        The Yahoo Finance fill rate limit as an integer.
    """
    # Fetch the fill rate limit from the configuration with a default fallback
    return int(get_config_value("YFINANCE_FILL_RATE_LIMIT", str(get_rate_limit())))


# --- AWS ---


def get_aws_access_key_id() -> str:
    """
    Get the AWS access key ID from the configuration.

    The function retrieves the AWS access key ID from the configuration.

    Returns
    -------
    str
        The AWS access key ID.
    """
    return get_config_value("AWS_ACCESS_KEY_ID", "")


def get_aws_secret_access_key() -> str:
    """
    Retrieve the AWS secret access key from the configuration.

    The function fetches the AWS secret access key from the configuration,
    either from Vault secrets or the environment variable AWS_SECRET_ACCESS_KEY.
    If neither is set, it defaults to an empty string.

    Parameters
    ----------
    None

    Returns
    -------
    str
        The AWS secret access key.
    """
    # Fetch the AWS secret access key from the configuration
    return get_config_value("AWS_SECRET_ACCESS_KEY", "")


def get_aws_region() -> str:
    """
    Get the AWS region from the configuration.

    The function retrieves the AWS region from the configuration.
    The region is used to determine the correct endpoint for AWS services.

    The region is fetched from the configuration with a default of 'us-east-1' if
    no region is specified.

    Parameters
    ----------
    None

    Returns
    -------
    str
        The AWS region.
    """
    # Fetch the AWS region from the configuration with a default of 'us-east-1'
    return get_config_value("AWS_REGION", "us-east-1")
