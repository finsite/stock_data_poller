# # import os
# # import hvac
# # from src.utils.validate_environment_variables import validate_environment_variables

# # # ✅ Runtime-secret cache
# # _VAULT_CONFIG = None


# # def load_vault_secrets():
# #     """Fetch secrets from HashiCorp Vault and return a dictionary."""
# #     VAULT_ADDR = os.getenv("VAULT_ADDR", "http://vault:8200")
# #     VAULT_TOKEN = os.getenv("VAULT_TOKEN")

# #     if not VAULT_TOKEN:
# #         raise ValueError("❌ Missing VAULT_TOKEN. Ensure it's set in the environment.")

# #     try:
# #         client = hvac.Client(url=VAULT_ADDR, token=VAULT_TOKEN)

# #         if not client.is_authenticated():
# #             raise ValueError("❌ Vault authentication failed!")

# #         vault_secrets = client.secrets.kv.v2.read_secret_version(path="poller")["data"]["data"]
# #         print("✅ Successfully loaded secrets from Vault.")
# #         return vault_secrets

# #     except Exception as e:
# #         print(f"⚠️ Warning: Failed to fetch secrets from Vault: {e}")
# #         return {}


# # def get_vault_config():
# #     """Load and cache Vault config only when needed."""
# #     global _VAULT_CONFIG
# #     if _VAULT_CONFIG is None:
# #         _VAULT_CONFIG = load_vault_secrets()
# #     return _VAULT_CONFIG


# # # ✅ Validate required environment variables
# # validate_environment_variables(["POLLER_TYPE", "QUEUE_TYPE", "RABBITMQ_HOST"])

# # # ✅ Convenience getter for secrets or env vars
# # def get_config_value(key, default=None):
# #     return get_vault_config().get(key, os.getenv(key, default))


# # # ✅ Core configuration values
# # SYMBOLS = get_config_value("SYMBOLS", "AAPL,GOOG,MSFT")
# # POLLER_TYPE = get_config_value("POLLER_TYPE", "yfinance")
# # QUEUE_TYPE = get_config_value("QUEUE_TYPE", "rabbitmq")

# # RABBITMQ_HOST = get_config_value("RABBITMQ_HOST", "localhost")
# # RABBITMQ_EXCHANGE = get_config_value("RABBITMQ_EXCHANGE", "stock_data_exchange")
# # RABBITMQ_ROUTING_KEY = get_config_value("RABBITMQ_ROUTING_KEY", "stock_data")

# # SQS_QUEUE_URL = get_config_value("SQS_QUEUE_URL", "")

# # POLL_INTERVAL = int(get_config_value("POLL_INTERVAL", 60))
# # REQUEST_TIMEOUT = int(get_config_value("REQUEST_TIMEOUT", 30))
# # MAX_RETRIES = int(get_config_value("MAX_RETRIES", 3))
# # RETRY_DELAY = int(get_config_value("RETRY_DELAY", 5))
# # LOG_LEVEL = get_config_value("LOG_LEVEL", "info")
# # RATE_LIMIT = int(get_config_value("RATE_LIMIT", 5))

# # # ✅ API Keys
# # POLYGON_API_KEY = get_config_value("POLYGON_API_KEY", "")
# # FINNHUB_API_KEY = get_config_value("FINNHUB_API_KEY", "")
# # ALPHA_VANTAGE_API_KEY = get_config_value("ALPHA_VANTAGE_API_KEY", "")
# # YFINANCE_API_KEY = get_config_value("YFINANCE_API_KEY", "")
# # IEX_API_KEY = get_config_value("IEX_API_KEY", "")
# # QUANDL_API_KEY = get_config_value("QUANDL_API_KEY", "")

# # # ✅ API Rate Limits
# # FINNHUB_FILL_RATE_LIMIT = int(get_config_value("FINNHUB_FILL_RATE_LIMIT", 100))
# # POLYGON_FILL_RATE_LIMIT = int(get_config_value("POLYGON_FILL_RATE_LIMIT", 100))
# # ALPHA_VANTAGE_FILL_RATE_LIMIT = int(get_config_value("ALPHA_VANTAGE_FILL_RATE_LIMIT", 100))
# # YFINANCE_FILL_RATE_LIMIT = int(get_config_value("YFINANCE_FILL_RATE_LIMIT", 100))
# # IEX_FILL_RATE_LIMIT = int(get_config_value("IEX_FILL_RATE_LIMIT", 100))
# # QUANDL_FILL_RATE_LIMIT = int(get_config_value("QUANDL_FILL_RATE_LIMIT", 100))

# # # ✅ AWS Config
# # AWS_ACCESS_KEY_ID = get_config_value("AWS_ACCESS_KEY_ID", "")
# # AWS_SECRET_ACCESS_KEY = get_config_value("AWS_SECRET_ACCESS_KEY", "")
# # AWS_REGION = get_config_value("AWS_REGION", "us-east-1")

# # # ✅ Feature Toggles
# # ENABLE_LOGGING = get_config_value("ENABLE_LOGGING", "true") == "true"
# # CLOUD_LOGGING_ENABLED = get_config_value("CLOUD_LOGGING_ENABLED", "false") == "true"
# # ENABLE_RETRY = get_config_value("ENABLE_RETRY", "true") == "true"
# # ENABLE_BACKFILL = get_config_value("ENABLE_BACKFILL", "false") == "true"

# # # ✅ Misc
# # POLL_TIMEOUT = int(get_config_value("POLL_TIMEOUT", 30))
# # MAX_API_CALLS_PER_MIN = int(get_config_value("MAX_API_CALLS_PER_MIN", 1000))
# import os
# import hvac
# from src.utils.validate_environment_variables import validate_environment_variables

# # ✅ Cache the secrets so Vault is only queried once
# _VAULT_CONFIG = None


# def load_vault_secrets():
#     """Fetch secrets from HashiCorp Vault and return a dictionary."""
#     VAULT_ADDR = os.getenv("VAULT_ADDR", "http://vault:8200")
#     VAULT_TOKEN = os.getenv("VAULT_TOKEN")

#     if not VAULT_TOKEN:
#         raise ValueError("❌ Missing VAULT_TOKEN. Ensure it's set in the environment.")

#     try:
#         client = hvac.Client(url=VAULT_ADDR, token=VAULT_TOKEN)
#         if not client.is_authenticated():
#             raise ValueError("❌ Vault authentication failed!")

#         vault_secrets = client.secrets.kv.v2.read_secret_version(path="poller")["data"]["data"]
#         print("✅ Successfully loaded secrets from Vault.")
#         return vault_secrets

#     except Exception as e:
#         print(f"⚠️ Warning: Failed to fetch secrets from Vault: {e}")
#         return {}


# def get_vault_config():
#     """Lazy-load Vault secrets."""
#     global _VAULT_CONFIG
#     if _VAULT_CONFIG is None:
#         _VAULT_CONFIG = load_vault_secrets()
#     return _VAULT_CONFIG


# def get_config_value(key, default=None):
#     """Get value from Vault if available, otherwise fallback to env/default."""
#     return get_vault_config().get(key, os.getenv(key, default))


# # ✅ Runtime validation (call manually in main entrypoints only)
# def validate_required_env():
#     """Validate required environment variables."""
#     validate_environment_variables(["POLLER_TYPE", "QUEUE_TYPE", "RABBITMQ_HOST"])


# # ✅ Core Configuration
# SYMBOLS = get_config_value("SYMBOLS", "AAPL,GOOG,MSFT")
# POLLER_TYPE = get_config_value("POLLER_TYPE", "yfinance")
# QUEUE_TYPE = get_config_value("QUEUE_TYPE", "rabbitmq")

# # ✅ RabbitMQ
# RABBITMQ_HOST = get_config_value("RABBITMQ_HOST", "localhost")
# RABBITMQ_EXCHANGE = get_config_value("RABBITMQ_EXCHANGE", "stock_data_exchange")
# RABBITMQ_ROUTING_KEY = get_config_value("RABBITMQ_ROUTING_KEY", "stock_data")

# # ✅ SQS
# SQS_QUEUE_URL = get_config_value("SQS_QUEUE_URL", "")

# # ✅ Timing
# POLL_INTERVAL = int(get_config_value("POLL_INTERVAL", 60))
# REQUEST_TIMEOUT = int(get_config_value("REQUEST_TIMEOUT", 30))
# MAX_RETRIES = int(get_config_value("MAX_RETRIES", 3))
# RETRY_DELAY = int(get_config_value("RETRY_DELAY", 5))
# POLL_TIMEOUT = int(get_config_value("POLL_TIMEOUT", 30))

# # ✅ Logging
# LOG_LEVEL = get_config_value("LOG_LEVEL", "info")
# ENABLE_LOGGING = get_config_value("ENABLE_LOGGING", "true") == "true"
# CLOUD_LOGGING_ENABLED = get_config_value("CLOUD_LOGGING_ENABLED", "false") == "true"

# # ✅ Retry & Backfill
# ENABLE_RETRY = get_config_value("ENABLE_RETRY", "true") == "true"
# ENABLE_BACKFILL = get_config_value("ENABLE_BACKFILL", "false") == "true"

# # ✅ Rate Limits
# RATE_LIMIT = int(get_config_value("RATE_LIMIT", 5))
# MAX_API_CALLS_PER_MIN = int(get_config_value("MAX_API_CALLS_PER_MIN", 1000))

# # ✅ API Keys
# POLYGON_API_KEY = get_config_value("POLYGON_API_KEY", "")
# FINNHUB_API_KEY = get_config_value("FINNHUB_API_KEY", "")
# ALPHA_VANTAGE_API_KEY = get_config_value("ALPHA_VANTAGE_API_KEY", "")
# YFINANCE_API_KEY = get_config_value("YFINANCE_API_KEY", "")
# IEX_API_KEY = get_config_value("IEX_API_KEY", "")
# QUANDL_API_KEY = get_config_value("QUANDL_API_KEY", "")

# # ✅ API-specific fill rate limits
# FINNHUB_FILL_RATE_LIMIT = int(get_config_value("FINNHUB_FILL_RATE_LIMIT", 100))
# POLYGON_FILL_RATE_LIMIT = int(get_config_value("POLYGON_FILL_RATE_LIMIT", 100))
# ALPHA_VANTAGE_FILL_RATE_LIMIT = int(get_config_value("ALPHA_VANTAGE_FILL_RATE_LIMIT", 100))
# YFINANCE_FILL_RATE_LIMIT = int(get_config_value("YFINANCE_FILL_RATE_LIMIT", 100))
# IEX_FILL_RATE_LIMIT = int(get_config_value("IEX_FILL_RATE_LIMIT", 100))
# QUANDL_FILL_RATE_LIMIT = int(get_config_value("QUANDL_FILL_RATE_LIMIT", 100))

# # ✅ AWS
# AWS_ACCESS_KEY_ID = get_config_value("AWS_ACCESS_KEY_ID", "")
# AWS_SECRET_ACCESS_KEY = get_config_value("AWS_SECRET_ACCESS_KEY", "")
# AWS_REGION = get_config_value("AWS_REGION", "us-east-1")
import os
import hvac
from src.utils.validate_environment_variables import validate_environment_variables

# ✅ Secret cache for runtime use
_VAULT_CONFIG = None


def load_vault_secrets():
    """Fetch secrets from HashiCorp Vault and return a dictionary."""
    VAULT_ADDR = os.getenv("VAULT_ADDR", "http://vault:8200")
    VAULT_TOKEN = os.getenv("VAULT_TOKEN")

    if not VAULT_TOKEN:
        raise ValueError("❌ Missing VAULT_TOKEN. Ensure it's set in the environment.")

    try:
        client = hvac.Client(url=VAULT_ADDR, token=VAULT_TOKEN)

        if not client.is_authenticated():
            raise ValueError("❌ Vault authentication failed!")

        secrets = client.secrets.kv.v2.read_secret_version(path="poller")["data"][
            "data"
        ]
        print("✅ Successfully loaded secrets from Vault.")
        return secrets

    except Exception as e:
        print(f"⚠️ Warning: Failed to fetch secrets from Vault: {e}")
        return {}


def get_vault_config():
    """Lazy-load and cache Vault secrets."""
    global _VAULT_CONFIG
    if _VAULT_CONFIG is None:
        _VAULT_CONFIG = load_vault_secrets()
    return _VAULT_CONFIG


def get_config_value(key, default=None):
    """Get value from Vault if available, else from environment or default."""
    return get_vault_config().get(key, os.getenv(key, default))


# ✅ Call manually in runtime entrypoint (not at import time)
def validate_required_env():
    validate_environment_variables(["POLLER_TYPE", "QUEUE_TYPE", "RABBITMQ_HOST"])


# --- Getter functions below ---


def get_symbols():
    return get_config_value("SYMBOLS", "AAPL,GOOG,MSFT")


def get_poller_type():
    return get_config_value("POLLER_TYPE", "yfinance")


def get_queue_type():
    return get_config_value("QUEUE_TYPE", "rabbitmq")


def get_rabbitmq_host():
    return get_config_value("RABBITMQ_HOST", "localhost")


def get_rabbitmq_exchange():
    return get_config_value("RABBITMQ_EXCHANGE", "stock_data_exchange")


def get_rabbitmq_routing_key():
    return get_config_value("RABBITMQ_ROUTING_KEY", "stock_data")


def get_sqs_queue_url():
    return get_config_value("SQS_QUEUE_URL", "")


def get_poll_interval():
    return int(get_config_value("POLL_INTERVAL", 60))


def get_request_timeout():
    return int(get_config_value("REQUEST_TIMEOUT", 30))


def get_max_retries():
    return int(get_config_value("MAX_RETRIES", 3))


def get_retry_delay():
    return int(get_config_value("RETRY_DELAY", 5))


def get_poll_timeout():
    return int(get_config_value("POLL_TIMEOUT", 30))


def get_log_level():
    return get_config_value("LOG_LEVEL", "info")


def is_logging_enabled():
    return get_config_value("ENABLE_LOGGING", "true") == "true"


def is_cloud_logging_enabled():
    return get_config_value("CLOUD_LOGGING_ENABLED", "false") == "true"


def is_retry_enabled():
    return get_config_value("ENABLE_RETRY", "true") == "true"


def is_backfill_enabled():
    return get_config_value("ENABLE_BACKFILL", "false") == "true"


def get_rate_limit():
    return int(get_config_value("RATE_LIMIT", 5))


def get_max_api_calls_per_min():
    return int(get_config_value("MAX_API_CALLS_PER_MIN", 1000))


# --- API Keys ---


def get_polygon_api_key():
    return get_config_value("POLYGON_API_KEY", "")


def get_finnhub_api_key():
    return get_config_value("FINNHUB_API_KEY", "")


def get_alpha_vantage_api_key():
    return get_config_value("ALPHA_VANTAGE_API_KEY", "")


def get_yfinance_api_key():
    return get_config_value("YFINANCE_API_KEY", "")


def get_iex_api_key():
    return get_config_value("IEX_API_KEY", "")


def get_quandl_api_key():
    return get_config_value("QUANDL_API_KEY", "")


# --- API Rate Limits ---


def get_polygon_fill_rate_limit():
    return int(get_config_value("POLYGON_FILL_RATE_LIMIT", 100))


def get_finnhub_fill_rate_limit():
    return int(get_config_value("FINNHUB_FILL_RATE_LIMIT", 100))


def get_alpha_vantage_fill_rate_limit():
    return int(get_config_value("ALPHA_VANTAGE_FILL_RATE_LIMIT", 100))


def get_yfinance_fill_rate_limit():
    return int(get_config_value("YFINANCE_FILL_RATE_LIMIT", 100))


def get_iex_fill_rate_limit():
    return int(get_config_value("IEX_FILL_RATE_LIMIT", 100))


def get_quandl_fill_rate_limit():
    return int(get_config_value("QUANDL_FILL_RATE_LIMIT", 100))


# --- AWS ---


def get_aws_access_key_id():
    return get_config_value("AWS_ACCESS_KEY_ID", "")


def get_aws_secret_access_key():
    return get_config_value("AWS_SECRET_ACCESS_KEY", "")


def get_aws_region():
    return get_config_value("AWS_REGION", "us-east-1")
