"""Factory class for creating pollers dynamically based on POLLER_TYPE."""

import os

from src.pollers.alphavantage_poller import AlphaVantagePoller
from src.pollers.finnhub_poller import FinnhubPoller
from src.pollers.iex_poller import IEXPoller
from src.pollers.polygon_poller import PolygonPoller
from src.pollers.quandl_poller import QuandlPoller
from src.pollers.yfinance_poller import YFinancePoller
from src.utils.setup_logger import setup_logger
from src.utils.validate_environment_variables import validate_environment_variables

# Initialize logger
logger = setup_logger(__name__)


class PollerFactory:
    """Factory class for creating pollers dynamically based on POLLER_TYPE.

    Attributes
    ----------
    required_env_vars : List[str]
        List of required environment variables to validate.
    poller_type : str
        Type of poller to create, as specified in the POLLER_TYPE environment variable.

    """

    def __init__(self):
        """Initializes the PollerFactory, validating the required environment variables
        and determining the appropriate poller class based on the configuration.
        """
        # Define required environment variables for validation
        self.required_env_vars = [
            "POLLER_TYPE",
            "IEX_API_KEY",
            "FINNHUB_API_KEY",
            "POLYGON_API_KEY",
            "ALPHA_VANTAGE_API_KEY",
            "YFINANCE_API_KEY",
            "QUANDL_API_KEY",
        ]

        # Validate environment variables
        validate_environment_variables(self.required_env_vars)

        # Fetch poller configuration from environment variables
        self.poller_type = os.getenv("POLLER_TYPE", "").lower()

        # Validate POLLER_TYPE
        if self.poller_type not in {
            "iex",
            "finnhub",
            "polygon",
            "alpha_vantage",
            "yfinance",
            "quandl",
        }:
            logger.error(f"Invalid POLLER_TYPE: {self.poller_type}")
            raise ValueError(
                "POLLER_TYPE must be one of: 'iex', 'finnhub', 'polygon', "
                "'alpha_vantage', 'yfinance', or 'quandl'."
            )

    def create_poller(self):
        """Creates an instance of the poller based on the specified POLLER_TYPE.

        Returns
        -------
        BasePoller
            An instance of the appropriate poller class.

        Raises
        ------
        ValueError
            If the POLLER_TYPE is invalid or if the required API key is missing.

        """
        if self.poller_type == "iex":
            api_key = os.getenv("IEX_API_KEY")
            if not api_key:
                raise ValueError("Missing API key for IEX Poller. Set IEX_API_KEY.")
            logger.info("Using IEX Poller.")
            return IEXPoller(api_key)

        elif self.poller_type == "finnhub":
            api_key = os.getenv("FINNHUB_API_KEY")
            if not api_key:
                raise ValueError("Missing API key for Finnhub Poller. Set FINNHUB_API_KEY.")
            logger.info("Using Finnhub Poller.")
            return FinnhubPoller(api_key)

        elif self.poller_type == "polygon":
            api_key = os.getenv("POLYGON_API_KEY")
            if not api_key:
                raise ValueError("Missing API key for Polygon Poller. Set POLYGON_API_KEY.")
            logger.info("Using Polygon Poller.")
            return PolygonPoller(api_key)

        elif self.poller_type == "alpha_vantage":
            api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
            if not api_key:
                raise ValueError(
                    "Missing API key for Alpha Vantage Poller. Set ALPHA_VANTAGE_API_KEY."
                )
            logger.info("Using Alpha Vantage Poller.")
            return AlphaVantagePoller(api_key)

        elif self.poller_type == "yfinance":
            api_key = os.getenv("YFINANCE_API_KEY")
            if not api_key:
                raise ValueError("Missing API key for YFinance Poller. Set YFINANCE_API_KEY.")
            logger.info("Using YFinance Poller.")
            return YFinancePoller(api_key)

        elif self.poller_type == "quandl":
            api_key = os.getenv("QUANDL_API_KEY")
            if not api_key:
                raise ValueError("Missing API key for Quandl Poller. Set QUANDL_API_KEY.")
            logger.info("Using Quandl Poller.")
            return QuandlPoller(api_key)

        else:
            logger.error(f"Unsupported POLLER_TYPE: {self.poller_type}")
            raise ValueError(f"Unsupported POLLER_TYPE: {self.poller_type}")
