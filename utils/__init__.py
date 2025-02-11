# """
# This module initializes the utilities package for the application.
# """

# from .retry_request import retry_request
# from .validate_data import validate_data
# from .track_polling_metrics import track_polling_metrics
# from .track_request_metrics import track_request_metrics
# from .request_with_timeout import request_with_timeout
# from .validate_environment_variables import validate_environment_variables
# from .setup_logger import setup_logger

# __all__ = [
#     "retry_request",
#     "validate_data",
#     "track_polling_metrics",
#     "track_request_metrics",
#     "request_with_timeout",
#     "validate_environment_variables",
#     "setup_logger",
# ]
"""
This module initializes the utilities package for the application.

Utilities included:
- retry_request: Function for retrying operations with exponential backoff.
- validate_data: Validates the structure and content of data.
- track_polling_metrics: Tracks polling metrics for success and failure.
- track_request_metrics: Tracks metrics for individual API requests.
- request_with_timeout: Makes HTTP requests with a timeout.
- validate_environment_variables: Validates required environment variables.
- setup_logger: Configures logging for the application.
"""

from .retry_request import retry_request
from .validate_data import validate_data
from .track_polling_metrics import track_polling_metrics
from .track_request_metrics import track_request_metrics
from .request_with_timeout import request_with_timeout
from .validate_environment_variables import validate_environment_variables
from .setup_logger import setup_logger

__all__ = [
    "retry_request",
    "validate_data",
    "track_polling_metrics",
    "track_request_metrics",
    "request_with_timeout",
    "validate_environment_variables",
    "setup_logger",
]

# Initialize package-level logger
logger = setup_logger(name="utils")
