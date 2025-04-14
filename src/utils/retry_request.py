"""
The module provides a decorator for retrying a function if it raises an exception.

The decorator `retry_request` retries a given function if it raises an exception.
It waits for a specified delay in seconds between retries, and attempts up to
a maximum number of times. If the function still raises an exception after the
maximum number of retries, it raises that exception.
"""

import time
from collections.abc import Callable
from typing import Any

from src.utils.setup_logger import setup_logger

# Set up logger for this module
logger = setup_logger(__name__)


def retry_request(
    func: Callable[[], Any], *, max_retries: int = 3, delay_seconds: int = 5
) -> Any | None:
    """
    Retries a given function if it raises an exception.

    Args:
    ----
        func (Callable[[], Any]): The function to be retried.
        max_retries (int): The maximum number of retry attempts. Defaults to 3.
        delay_seconds (int): The delay in seconds between retries. Defaults to 5.

    Returns:
    -------
        Optional[Any]: The result of the function if successful, or None if all retries fail.

    Raises:
    ------
        ValueError: If the function to be retried is None.
        Exception: The last exception encountered if all retries fail.
    """
    # Validate the function to be retried
    if func is None:
        raise ValueError("The function to be retried cannot be None")

    last_exception = None  # To store the last exception encountered

    # Attempt to execute the function up to max_retries times
    for attempt in range(1, max_retries + 1):
        try:
            logger.debug(f"Attempt {attempt} of {max_retries}.")
            return func()  # Call the function and return its result if successful
        except Exception as exception:
            last_exception = exception  # Store the exception
            logger.warning(
                f"Attempt {attempt} failed with error: {exception}. "
                f"{'Retrying...' if attempt < max_retries else 'No more retries.'}"
            )
            # Delay before retrying, if more retries are available
            if attempt < max_retries:
                time.sleep(delay_seconds)

    # Log the final failure and raise the last exception encountered
    logger.error(f"All {max_retries} attempts failed. Last error: {last_exception}")
    raise last_exception
