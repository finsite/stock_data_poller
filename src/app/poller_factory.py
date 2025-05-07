# """Factory class for creating pollers dynamically based on POLLER_TYPE."""

# import os

# from app.pollers.alphavantage_poller import AlphaVantagePoller
# from app.pollers.finnhub_poller import FinnhubPoller
# from app.pollers.iex_poller import IEXPoller
# from app.pollers.polygon_poller import PolygonPoller
# from app.pollers.quandl_poller import QuandlPoller
# from app.pollers.yfinance_poller import YFinancePoller
# from app.utils.setup_logger import setup_logger
# from app.utils.validate_environment_variables import validate_environment_variables

# logger = setup_logger(__name__)


# class PollerFactory:
#     """
#     Factory class for creating pollers dynamically based on POLLER_TYPE.

#     Validates only the required API key for the selected poller, except for `yfinance`.
#     """

#     def __init__(self) -> None:
#         """Initializes the PollerFactory and validates the required API key for the
#         selected poller."""
#         self.poller_type: str = os.getenv("POLLER_TYPE", "").lower()

#         valid_pollers = {
#             "iex": "IEX_API_KEY",
#             "finnhub": "FINNHUB_API_KEY",
#             "polygon": "POLYGON_API_KEY",
#             "alpha_vantage": "ALPHA_VANTAGE_API_KEY",
#             "quandl": "QUANDL_API_KEY",
#             # No API key needed for yfinance
#             "yfinance": None,
#         }

#         if self.poller_type not in valid_pollers:
#             logger.error(f"Invalid POLLER_TYPE: {self.poller_type}")
#             raise ValueError(
#                 "POLLER_TYPE must be one of: 'iex', 'finnhub', 'polygon', "
#                 "'alpha_vantage', 'yfinance', or 'quandl'."
#             )

#         # Only validate the API key if one is required
#         required_key = valid_pollers[self.poller_type]
#         if required_key:
#             validate_environment_variables(["POLLER_TYPE", required_key])
#         else:
#             validate_environment_variables(["POLLER_TYPE"])

#     def create_poller(self):
#         """
#         Creates an instance of the poller based on POLLER_TYPE.

#         Returns
#         -------
#         BasePoller
#             An instance of the poller class.
#         """
#         if self.poller_type == "iex":
#             logger.info("Using IEX Poller.")
#             return IEXPoller(os.getenv("IEX_API_KEY", ""))

#         if self.poller_type == "finnhub":
#             logger.info("Using Finnhub Poller.")
#             return FinnhubPoller(os.getenv("FINNHUB_API_KEY", ""))

#         if self.poller_type == "polygon":
#             logger.info("Using Polygon Poller.")
#             return PolygonPoller(os.getenv("POLYGON_API_KEY", ""))

#         if self.poller_type == "alpha_vantage":
#             logger.info("Using Alpha Vantage Poller.")
#             return AlphaVantagePoller(os.getenv("ALPHA_VANTAGE_API_KEY", ""))

#         if self.poller_type == "quandl":
#             logger.info("Using Quandl Poller.")
#             return QuandlPoller(os.getenv("QUANDL_API_KEY", ""))

#         if self.poller_type == "yfinance":
#             logger.info("Using YFinance Poller.")
#             return YFinancePoller()

#         raise ValueError(f"Unsupported POLLER_TYPE: {self.poller_type}")
"""Factory class for creating pollers dynamically based on POLLER_TYPE."""

import os

from app.pollers.alphavantage_poller import AlphaVantagePoller
from app.pollers.finnhub_poller import FinnhubPoller
from app.pollers.iex_poller import IEXPoller
from app.pollers.polygon_poller import PolygonPoller
from app.pollers.quandl_poller import QuandlPoller
from app.pollers.yfinance_poller import YFinancePoller
from app.utils.setup_logger import setup_logger
from app.utils.validate_environment_variables import validate_environment_variables

logger = setup_logger(__name__)


class PollerFactory:
    """Factory class for creating pollers dynamically based on POLLER_TYPE.

    Validates only the required API key for the selected poller, except for `yfinance`.

    Args:

    Returns:

    """

    def __init__(self) -> None:
        """Initializes the PollerFactory and validates the required API key for the
        selected poller.
        """
        self.poller_type: str = os.getenv("POLLER_TYPE", "").lower()

        valid_pollers = {
            "iex": "IEX_API_KEY",
            "finnhub": "FINNHUB_API_KEY",
            "polygon": "POLYGON_API_KEY",
            "alpha_vantage": "ALPHA_VANTAGE_API_KEY",
            "quandl": "QUANDL_API_KEY",
            "yfinance": None,  # No API key required
        }

        if self.poller_type not in valid_pollers:
            logger.error(f"Invalid POLLER_TYPE: {self.poller_type}")
            raise ValueError(
                "POLLER_TYPE must be one of: 'iex', 'finnhub', 'polygon', "
                "'alpha_vantage', 'quandl', or 'yfinance'."
            )

        required_key = valid_pollers[self.poller_type]
        keys_to_validate = ["POLLER_TYPE"] + ([required_key] if required_key else [])
        validate_environment_variables(keys_to_validate)

    def create_poller(self):
        """Creates an instance of the poller based on POLLER_TYPE."""
        if self.poller_type == "iex":
            logger.info("Using IEX Poller.")
            return IEXPoller()

        if self.poller_type == "finnhub":
            logger.info("Using Finnhub Poller.")
            return FinnhubPoller()

        if self.poller_type == "polygon":
            logger.info("Using Polygon Poller.")
            return PolygonPoller()

        if self.poller_type == "alpha_vantage":
            logger.info("Using Alpha Vantage Poller.")
            return AlphaVantagePoller()

        if self.poller_type == "quandl":
            logger.info("Using Quandl Poller.")
            return QuandlPoller()

        if self.poller_type == "yfinance":
            logger.info("Using YFinance Poller.")
            return YFinancePoller()

        raise ValueError(f"Unsupported POLLER_TYPE: {self.poller_type}")
