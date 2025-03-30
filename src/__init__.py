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

# Import queue logic
from src.message_queue.queue_sender import QueueSender

# Import pollers (from `pollers/`)
from src.pollers.alphavantage_poller import AlphaVantagePoller
from src.pollers.base_poller import BasePoller
from src.pollers.finnhub_poller import FinnhubPoller
from src.pollers.iex_poller import IEXPoller
from src.pollers.polygon_poller import PolygonPoller
from src.pollers.quandl_poller import QuandlPoller
from src.pollers.yfinance_poller import YFinancePoller

# Import utilities (from `utils/`)
from src.utils import (
    rate_limit,
    request_with_timeout,
    retry_request,
    setup_logger,
    track_polling_metrics,
    track_request_metrics,
    validate_data,
    validate_environment_variables,
)

# Define the public API of the module
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
    "rate_limit",
    "retry_request",
    "request_with_timeout",
    "track_polling_metrics",
    "track_request_metrics",
    "validate_data",
]
