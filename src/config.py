# Secret cache for runtime use
_VAULT_CONFIG = None


def load_vault_secrets():
    """Fetch secrets from HashiCorp Vault and return a dictionary.

    Raises
    ------
        ValueError: If VAULT_TOKEN is not set in the environment.

    """
    VAULT_ADDR = os.getenv("VAULT_ADDR", "http://vault:8200")
    VAULT_TOKEN = os.getenv("VAULT_TOKEN")

    if not VAULT_TOKEN:
        raise ValueError("❌ Missing VAULT_TOKEN. Ensure it's set in the environment.")

    try:
        client = hvac.Client(url=VAULT_ADDR, token=VAULT_TOKEN)

        if not client.is_authenticated():
            raise ValueError("❌ Vault authentication failed!")

        secrets = client.secrets.kv.v2.read_secret_version(path="poller")["data"]["data"]
        print("✅ Successfully loaded secrets from Vault.")
        return secrets

    except Exception as e:
        print(f"⚠️ Warning: Failed to fetch secrets from Vault: {e}")
        return {}


def get_vault_config():
    """Lazy-load and cache Vault secrets.
    """
    global _VAULT_CONFIG
    if _VAULT_CONFIG is None:
        _VAULT_CONFIG = load_vault_secrets()
    return _VAULT_CONFIG


def get_config_value(key, default=None):
    """Get value from Vault if available, else from environment or default.
    """
    return get_vault_config().get(key, os.getenv(key, default))


# --- Getter functions below ---


def get_symbols():
    """Get the list of symbols from the configuration.
    """
    return get_config_value("SYMBOLS", "AAPL,GOOG,MSFT")


def get_poller_type():
    """Get the type of poller from the configuration.
    """
    return get_config_value("POLLER_TYPE", "yfinance")


def get_queue_type():
    """Get the type of queue from the configuration.
    """
    return get_config_value("QUEUE_TYPE", "rabbitmq")


def get_rabbitmq_host():
    """Get the RabbitMQ host from the configuration.
    """
    return get_config_value("RABBITMQ_HOST", "localhost")


def get_rabbitmq_exchange():
    """Get the RabbitMQ exchange from the configuration.
    """
    return get_config_value("RABBITMQ_EXCHANGE", "stock_data_exchange")


def get_rabbitmq_routing_key():
    """Get the RabbitMQ routing key from the configuration.
    """
    return get_config_value("RABBITMQ_ROUTING_KEY", "stock_data")


def get_sqs_queue_url():
    """Get the SQS queue URL from the configuration.
    """
    return get_config_value("SQS_QUEUE_URL", "")


def get_poll_interval():
    """Get the poll interval from the configuration.
    """
    return int(get_config_value("POLL_INTERVAL", 60))


def get_request_timeout():
    """Get the request timeout from the configuration.
    """
    return int(get_config_value("REQUEST_TIMEOUT", 30))


def get_max_retries():
    """Get the maximum number of retries from the configuration.
    """
    return int(get_config_value("MAX_RETRIES", 3))


def get_retry_delay():
    """Get the retry delay from the configuration.
    """
    return int(get_config_value("RETRY_DELAY", 5))


def get_poll_timeout():
    """Get the poll timeout from the configuration.
    """
    return int(get_config_value("POLL_TIMEOUT", 30))


def get_log_level():
    """Get the log level from the configuration.
    """
    return get_config_value("LOG_LEVEL", "info")


def is_logging_enabled():
    """Check if logging is enabled from the configuration.
    """
    return get_config_value("ENABLE_LOGGING", "true") == "true"


def is_cloud_logging_enabled():
    """Check if cloud logging is enabled from the configuration.
    """
    return get_config_value("CLOUD_LOGGING_ENABLED", "false") == "true"


def is_retry_enabled():
    """Check if retry is enabled from the configuration.
    """
    return get_config_value("ENABLE_RETRY", "true") == "true"


def is_backfill_enabled():
    """Check if backfill is enabled from the configuration.
    """
    return get_config_value("ENABLE_BACKFILL", "false") == "true"


def get_rate_limit():
    """Get the rate limit from the configuration.
    """
    return int(get_config_value("RATE_LIMIT", 5))


def get_max_api_calls_per_min():
    """Get the maximum number of API calls per minute from the configuration.
    """
    return int(get_config_value("MAX_API_CALLS_PER_MIN", 1000))


# --- API Keys ---


def get_polygon_api_key():
    """Get the Polygon API key from the configuration.
    """
    return get_config_value("POLYGON_API_KEY", "")


def get_finnhub_api_key():
    """Get the Finnhub API key from the configuration.
    """
    return get_config_value("FINNHUB_API_KEY", "")


def get_alpha_vantage_api_key():
    """Get the Alpha Vantage API key from the configuration.
    """
    return get_config_value("ALPHA_VANTAGE_API_KEY", "")


def get_yfinance_api_key():
    """Get the Yahoo Finance API key from the configuration.
    """
    return get_config_value("YFINANCE_API_KEY", "")


def get_iex_api_key():
    """Get the IEX API key from the configuration.
    """
    return get_config_value("IEX_API_KEY", "")


def get_quandl_api_key():
    """Get the Quandl API key from the configuration.
    """
    return get_config_value("QUANDL_API_KEY", "")


# --- API Rate Limits ---


def get_polygon_fill_rate_limit():
    """Get the Polygon fill rate limit from the configuration.
    """
    return int(get_config_value("POLYGON_FILL_RATE_LIMIT", 100))


def get_finnhub_fill_rate_limit():
    """Get the Finnhub fill rate limit from the configuration.
    """
    return int(get_config_value("FINNHUB_FILL_RATE_LIMIT", 100))


def get_alpha_vantage_fill_rate_limit():
    """Get the Alpha Vantage fill rate limit from the configuration.
    """
    return int(get_config_value("ALPHA_VANTAGE_FILL_RATE_LIMIT", 100))


def get_yfinance_fill_rate_limit():
    """Get the Yahoo Finance fill rate limit from the configuration.
    """
    return int(get_config_value("YFINANCE_FILL_RATE_LIMIT", 100))


def get_iex_fill_rate_limit():
    """Get the IEX fill rate limit from the configuration.
    """
    return int(get_config_value("IEX_FILL_RATE_LIMIT", 100))


def get_quandl_fill_rate_limit():
    """Get the Quandl fill rate limit from the configuration.
    """
    return int(get_config_value("QUANDL_FILL_RATE_LIMIT", 100))


# --- AWS ---


def get_aws_access_key_id():
    """Get the AWS access key ID from the configuration.
    """
    return get_config_value("AWS_ACCESS_KEY_ID", "")


def get_aws_secret_access_key():
    """Get the AWS secret access key from the configuration.
    """
    return get_config_value("AWS_SECRET_ACCESS_KEY", "")


def get_aws_region():
    """Get the AWS region from the configuration.
    """
    return get_config_value("AWS_REGION", "us-east-1")
