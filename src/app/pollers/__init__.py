"""Initialize the stock polling logic for the application.

Pollers included:
- BasePoller: Abstract base class for all pollers, providing common functionality.
- IEXPoller: Fetches stock data from the IEX Cloud API.
- PolygonPoller: Fetches stock data from the Polygon.io API.
- YFinancePoller: Fetches stock data from Yahoo Finance (yfinance).
- AlphaVantagePoller: Fetches stock data from the Alpha Vantage API.
- FinnhubPoller: Fetches stock data from the Finnhub API.
- QuandlPoller: Fetches stock data from the Quandl API.

Note:
----
    This module imports and exports poller classes for use across the application
    and sets up the package-level logger.

"""

import logging

from app.pollers.alphavantage_poller import AlphaVantagePoller
from app.pollers.base_poller import BasePoller
from app.pollers.finnhub_poller import FinnhubPoller
from app.pollers.iex_poller import IEXPoller
from app.pollers.polygon_poller import PolygonPoller
from app.pollers.quandl_poller import QuandlPoller
from app.pollers.yfinance_poller import YFinancePoller
from app.utils.setup_logger import setup_logger

__all__ = [
    "BasePoller",
    "IEXPoller",
    "PolygonPoller",
    "YFinancePoller",
    "AlphaVantagePoller",
    "FinnhubPoller",
    "QuandlPoller",
]

# Configure package-level logger
logger: logging.Logger = setup_logger(name="pollers")
