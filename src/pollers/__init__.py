"""This module initializes the stock polling logic for the application.

Pollers included:
- BasePoller: Abstract base class for all pollers, providing common functionality.
- IEXPoller: Fetches stock data from the IEX Cloud API.
- PolygonPoller: Fetches stock data from the Polygon.io API.
- YFinancePoller: Fetches stock data from Yahoo Finance (yfinance).
- AlphaVantagePoller: Fetches stock data from the Alpha Vantage API.
- FinnhubPoller: Fetches stock data from the Finnhub API.
- QuandlPoller: Fetches stock data from the Quandl API.

Note: This module is responsible for importing and exporting the necessary poller
classes and functions. It also sets up the package-level logger.
"""

# Import the concrete poller classes
from src.pollers.alphavantage_poller import AlphaVantagePoller

# Import the base poller class
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
# Import the logger setup function from the utils module
from src.utils.setup_logger import setup_logger

# Initialize the logger for the pollers package
logger = setup_logger(name="pollers")
