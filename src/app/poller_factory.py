"""Factory class for creating pollers dynamically based on POLLER_TYPE."""

import os

from app.pollers.alphavantage_poller import AlphaVantagePoller
from app.pollers.FinnazonPoller import FinnazonPoller
from app.pollers.finnhub_poller import FinnhubPoller
from app.pollers.iex_poller import IEXPoller
from app.pollers.IntrinioPoller import IntrinioPoller
from app.pollers.polygon_poller import PolygonPoller
from app.pollers.quandl_poller import QuandlPoller
from app.pollers.YahooRapidAPIPoller import YahooRapidAPIPoller
from app.pollers.yfinance_poller import YFinancePoller
from app.utils.setup_logger import setup_logger
from app.utils.validate_environment_variables import validate_environment_variables

logger = setup_logger(__name__)


class PollerFactory:
    """Creates the appropriate poller instance based on the POLLER_TYPE environment variable.

    Validates the required API key for the chosen poller, if applicable.
    """

    def __init__(self) -> None:
        self.poller_type: str = os.getenv("POLLER_TYPE", "").lower()

        self.valid_pollers = {
            "iex": ("IEX_API_KEY", IEXPoller),
            "finnhub": ("FINNHUB_API_KEY", FinnhubPoller),
            "polygon": ("POLYGON_API_KEY", PolygonPoller),
            "alpha_vantage": ("ALPHA_VANTAGE_API_KEY", AlphaVantagePoller),
            "quandl": ("QUANDL_API_KEY", QuandlPoller),
            "yfinance": (None, YFinancePoller),
            "finnazon": ("FINNAZON_API_KEY", FinnazonPoller),
            "intrinio": ("INTRINIO_API_KEY", IntrinioPoller),
            "yahoo_rapidapi": ("YAHOO_RAPIDAPI_KEY", YahooRapidAPIPoller),
        }

        if self.poller_type not in self.valid_pollers:
            logger.error("❌ Invalid POLLER_TYPE: %s", self.poller_type)
            raise ValueError(
                "POLLER_TYPE must be one of: " + ", ".join(f"'{k}'" for k in self.valid_pollers)
            )

        required_key, _ = self.valid_pollers[self.poller_type]
        keys_to_validate = ["POLLER_TYPE"] + ([required_key] if required_key else [])
        validate_environment_variables(keys_to_validate)

    def create_poller(self):
        """Creates and returns a poller instance for the configured POLLER_TYPE."""
        _, poller_class = self.valid_pollers[self.poller_type]
        logger.info(f"📡 Using poller: {poller_class.__name__}")
        return poller_class()
