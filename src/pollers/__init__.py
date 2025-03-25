"""This module initializes the stock polling logic for the application.

Pollers included:
- BasePoller: Abstract base class for all pollers, providing common functionality.
- IEXPoller: Fetches stock data from the IEX Cloud API.
- PolygonPoller: Fetches stock data from the Polygon.io API.
- YFinancePoller: Fetches stock data from Yahoo Finance (yfinance).
- AlphaVantagePoller: Fetches stock data from the Alpha Vantage API.
- FinnhubPoller: Fetches stock data from the Finnhub API.
- QuandlPoller: Fetches stock data from the Quandl API.
"""

from src.pollers.alphavantage_poller import AlphaVantagePoller
from src.pollers.base_poller import BasePoller
from src.pollers.finnhub_poller import FinnhubPoller
from src.pollers.iex_poller import IEXPoller
from src.pollers.polygon_poller import PolygonPoller
from src.pollers.quandl_poller import QuandlPoller
from src.pollers.yfinance_poller import YFinancePoller

__all__ = [
    "BasePoller",
    "IEXPoller",
    "PolygonPoller",
    "YFinancePoller",
    "AlphaVantagePoller",
    "FinnhubPoller",
    "QuandlPoller",
]

# Package-level logger setup
# import logging
from src.utils.setup_logger import setup_logger

logger = setup_logger(name="pollers")
