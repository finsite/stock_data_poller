"""
This module initializes the main application package.

The app package is structured as follows:
- pollers: Handles data polling from various APIs (e.g., AlphaVantage, YFinance).
- queue: Manages queue logic for RabbitMQ and SQS.
- utils: Provides utility functions for logging, environment validation, rate-limiting, etc.

Exports:
- Pollers: BasePoller, AlphaVantagePoller, FinnhubPoller, IEXPoller, PolygonPoller, QuandlPoller, YFinancePoller
- Queue: QueueSender
- Utilities: setup_logger, validate_environment_variables, rate_limit, retry_request,
  request_with_timeout, track_polling_metrics, track_request_metrics, validate_data
"""

# Import pollers
from .pollers import (
    AlphaVantagePoller,
    BasePoller,
    FinnhubPoller,
    IEXPoller,
    PolygonPoller,
    QuandlPoller,
    YFinancePoller,
)

# Import queue logic
#from .queue import QueueSender
from .queue.queue_sender import QueueSender

# Import utilities
from .utils import (
    setup_logger,
    validate_environment_variables,
    rate_limit,
    retry_request,
    request_with_timeout,
    track_polling_metrics,
    track_request_metrics,
    validate_data,
)

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

# Package-level logger setup
import logging

logger = setup_logger(name="app")
logger.info("Application package initialized.")
