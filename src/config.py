import os
import hvac
from utils.validate_environment_variables import validate_environment_variables  # ✅ RESTORED

def load_vault_secrets():
    """Fetch secrets from HashiCorp Vault and return a dictionary."""
    VAULT_ADDR = os.getenv("VAULT_ADDR", "http://vault:8200")
    VAULT_TOKEN = os.getenv("VAULT_TOKEN")

    if not VAULT_TOKEN:
        raise ValueError("❌ Missing VAULT_TOKEN. Ensure it's set in the environment.")

    try:
        # Connect to Vault
        client = hvac.Client(url=VAULT_ADDR, token=VAULT_TOKEN)

        # Authenticate
        if not client.is_authenticated():
            raise ValueError("❌ Vault authentication failed!")

        # Fetch secrets from Vault
        vault_secrets = client.secrets.kv.v2.read_secret_version(path="poller")["data"]["data"]

        print("✅ Successfully loaded secrets from Vault.")
        return vault_secrets

    except Exception as e:
        print(f"⚠️ Warning: Failed to fetch secrets from Vault: {e}")
        return {}

# ✅ Load Vault secrets at runtime
VAULT_CONFIG = load_vault_secrets()

# ✅ Validate required environment variables
validate_environment_variables(["POLLER_TYPE", "QUEUE_TYPE", "RABBITMQ_HOST"])  # ✅ RESTORED VALIDATION

# ✅ Default Stock Symbols (Ensures it always has values)
SYMBOLS = VAULT_CONFIG.get("SYMBOLS", os.getenv("SYMBOLS", "AAPL,GOOG,MSFT"))

# ✅ Default Poller Type (Now set to `yfinance` by default)
POLLER_TYPE = VAULT_CONFIG.get("POLLER_TYPE", os.getenv("POLLER_TYPE", "yfinance"))
QUEUE_TYPE = VAULT_CONFIG.get("QUEUE_TYPE", os.getenv("QUEUE_TYPE", "rabbitmq"))

# ✅ RabbitMQ Exchange Configuration
RABBITMQ_HOST = VAULT_CONFIG.get("RABBITMQ_HOST", os.getenv("RABBITMQ_HOST", "localhost"))
RABBITMQ_EXCHANGE = VAULT_CONFIG.get("RABBITMQ_EXCHANGE", os.getenv("RABBITMQ_EXCHANGE", "stock_data_exchange"))
RABBITMQ_ROUTING_KEY = VAULT_CONFIG.get("RABBITMQ_ROUTING_KEY", os.getenv("RABBITMQ_ROUTING_KEY", "stock_data"))

# ✅ FIXED: Added missing `SQS_QUEUE_URL`
SQS_QUEUE_URL = VAULT_CONFIG.get("SQS_QUEUE_URL", os.getenv("SQS_QUEUE_URL", ""))

# ✅ Polling & API Request Configurations
POLL_INTERVAL = int(VAULT_CONFIG.get("POLL_INTERVAL", os.getenv("POLL_INTERVAL", 60)))
REQUEST_TIMEOUT = int(VAULT_CONFIG.get("REQUEST_TIMEOUT", os.getenv("REQUEST_TIMEOUT", 30)))
MAX_RETRIES = int(VAULT_CONFIG.get("MAX_RETRIES", os.getenv("MAX_RETRIES", 3)))
RETRY_DELAY = int(VAULT_CONFIG.get("RETRY_DELAY", os.getenv("RETRY_DELAY", 5)))
LOG_LEVEL = VAULT_CONFIG.get("LOG_LEVEL", os.getenv("LOG_LEVEL", "info"))

# ✅ Added `RATE_LIMIT`
RATE_LIMIT = int(VAULT_CONFIG.get("RATE_LIMIT", os.getenv("RATE_LIMIT", 5)))

# ✅ API Keys (All services)
POLYGON_API_KEY = VAULT_CONFIG.get("POLYGON_API_KEY", os.getenv("POLYGON_API_KEY", ""))
FINNHUB_API_KEY = VAULT_CONFIG.get("FINNHUB_API_KEY", os.getenv("FINNHUB_API_KEY", ""))
ALPHA_VANTAGE_API_KEY = VAULT_CONFIG.get("ALPHA_VANTAGE_API_KEY", os.getenv("ALPHA_VANTAGE_API_KEY", ""))
YFINANCE_API_KEY = VAULT_CONFIG.get("YFINANCE_API_KEY", os.getenv("YFINANCE_API_KEY", ""))
IEX_API_KEY = VAULT_CONFIG.get("IEX_API_KEY", os.getenv("IEX_API_KEY", ""))
QUANDL_API_KEY = VAULT_CONFIG.get("QUANDL_API_KEY", os.getenv("QUANDL_API_KEY", ""))

# ✅ API Rate Limits
FINNHUB_FILL_RATE_LIMIT = int(VAULT_CONFIG.get("FINNHUB_FILL_RATE_LIMIT", os.getenv("FINNHUB_FILL_RATE_LIMIT", 100)))
POLYGON_FILL_RATE_LIMIT = int(VAULT_CONFIG.get("POLYGON_FILL_RATE_LIMIT", os.getenv("POLYGON_FILL_RATE_LIMIT", 100)))
ALPHA_VANTAGE_FILL_RATE_LIMIT = int(VAULT_CONFIG.get("ALPHA_VANTAGE_FILL_RATE_LIMIT", os.getenv("ALPHA_VANTAGE_FILL_RATE_LIMIT", 100)))
YFINANCE_FILL_RATE_LIMIT = int(VAULT_CONFIG.get("YFINANCE_FILL_RATE_LIMIT", os.getenv("YFINANCE_FILL_RATE_LIMIT", 100)))
IEX_FILL_RATE_LIMIT = int(VAULT_CONFIG.get("IEX_FILL_RATE_LIMIT", os.getenv("IEX_FILL_RATE_LIMIT", 100)))
QUANDL_FILL_RATE_LIMIT = int(VAULT_CONFIG.get("QUANDL_FILL_RATE_LIMIT", os.getenv("QUANDL_FILL_RATE_LIMIT", 100)))

# ✅ AWS Config
AWS_ACCESS_KEY_ID = VAULT_CONFIG.get("AWS_ACCESS_KEY_ID", os.getenv("AWS_ACCESS_KEY_ID", ""))
AWS_SECRET_ACCESS_KEY = VAULT_CONFIG.get("AWS_SECRET_ACCESS_KEY", os.getenv("AWS_SECRET_ACCESS_KEY", ""))
AWS_REGION = VAULT_CONFIG.get("AWS_REGION", os.getenv("AWS_REGION", "us-east-1"))

# ✅ Enable Flags (Ensure boolean values are properly set)
ENABLE_LOGGING = VAULT_CONFIG.get("ENABLE_LOGGING", os.getenv("ENABLE_LOGGING", "true")) == "true"
CLOUD_LOGGING_ENABLED = VAULT_CONFIG.get("CLOUD_LOGGING_ENABLED", os.getenv("CLOUD_LOGGING_ENABLED", "false")) == "true"
ENABLE_RETRY = VAULT_CONFIG.get("ENABLE_RETRY", os.getenv("ENABLE_RETRY", "true")) == "true"
ENABLE_BACKFILL = VAULT_CONFIG.get("ENABLE_BACKFILL", os.getenv("ENABLE_BACKFILL", "false")) == "true"

# ✅ Other Configurations
POLL_TIMEOUT = int(VAULT_CONFIG.get("POLL_TIMEOUT", os.getenv("POLL_TIMEOUT", 30)))
MAX_API_CALLS_PER_MIN = int(VAULT_CONFIG.get("MAX_API_CALLS_PER_MIN", os.getenv("MAX_API_CALLS_PER_MIN", 1000)))
