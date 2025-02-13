"""
This module initializes the main application package.

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

# ✅ Import pollers (from `pollers/`)
from .pollers.alphavantage_poller import AlphaVantagePoller
from .pollers.base_poller import BasePoller
from .pollers.finnhub_poller import FinnhubPoller
from .pollers.iex_poller import IEXPoller
from .pollers.polygon_poller import PolygonPoller
from .pollers.quandl_poller import QuandlPoller
from .pollers.yfinance_poller import YFinancePoller

# ✅ Import queue logic
from .message_queue.queue_sender import QueueSender

# ✅ Import utilities (from `utils/`)
from .utils.rate_limit import RateLimiter
from .utils.request_with_timeout import request_with_timeout
from .utils.retry_request import retry_request
from .utils.setup_logger import setup_logger
from .utils.track_polling_metrics import track_polling_metrics
from .utils.track_request_metrics import track_request_metrics
from .utils.validate_data import validate_data
from .utils.validate_environment_variables import validate_environment_variables

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
import logging

logger = setup_logger(name="app")
logger.info("Application package initialized.")
