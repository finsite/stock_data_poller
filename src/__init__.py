"""This module initializes the main application package.

The app package is structured as follows:
- pollers: Handles data polling from various APIs (e.g., AlphaVantage, YFinance).
- message_queue: Manages queue logic for RabbitMQ and SQS.
- utils: Provides utility functions for logging, environment validation, rate-limiting, etc.

Exports:
- Pollers: BasePoller, AlphaVantagePoller, FinnhubPoller, IEXPoller, PolygonPoller, QuandlPoller, YFinancePoller
- Queue: QueueSender
- Utilities: setup_logger, validate_environment_variables, rate_limit, retry_request,
  request_with_timeout, track_polling_metrics, track_request_metrics, validate_data
"""

# ✅ Import queue logic
from src.message_queue.queue_sender import QueueSender

# ✅ Import pollers (from `pollers/`)
from src.pollers.alphavantage_poller import AlphaVantagePoller
from src.pollers.base_poller import BasePoller
from src.pollers.finnhub_poller import FinnhubPoller
from src.pollers.iex_poller import IEXPoller
from src.pollers.polygon_poller import PolygonPoller
from src.pollers.quandl_poller import QuandlPoller
from src.pollers.yfinance_poller import YFinancePoller

# ✅ Import utilities (from `utils/`)
from src.utils.rate_limit import RateLimiter
from src.utils.request_with_timeout import request_with_timeout
from src.utils.retry_request import retry_request
from src.utils.setup_logger import setup_logger
from src.utils.track_polling_metrics import track_polling_metrics
from src.utils.track_request_metrics import track_request_metrics
from src.utils.validate_data import validate_data
from src.utils.validate_environment_variables import validate_environment_variables

__all__ = [
    "AlphaVantagePoller",
    "BasePoller",
    "FinnhubPoller",
    "IEXPoller",
    "PolygonPoller",
    "QuandlPoller",
    "YFinancePoller",
    "QueueSender",
    "setup_logger",
    "validate_environment_variables",
    "RateLimiter",
    "retry_request",
    "request_with_timeout",
    "track_polling_metrics",
    "track_request_metrics",
    "validate_data",
]

# ✅ Package-level logger setup (moved after imports to prevent circular imports)
# import logging

logger = setup_logger(name="app")
logger.info("Application package initialized.")
