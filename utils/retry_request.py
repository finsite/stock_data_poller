import time
import logging
from typing import Callable, Any, Optional

# Initialize logger
logger = logging.getLogger("poller")

def retry_request(
    func: Callable[[], Any],
    *,
    max_retries: int = 3,
    delay_seconds: int = 5,
    backoff_factor: float = 2.0  # Optional: exponential backoff
) -> Optional[Any]:
    """
    Retries a given function if it raises an exception.

    Args:
        func (Callable[[], Any]): The function to be retried.
        max_retries (int): The maximum number of retry attempts. Defaults to 3.
        delay_seconds (int): The delay in seconds between retries. Defaults to 5.
        backoff_factor (float): The factor by which the delay is multiplied for each retry. Defaults to 2.0 (exponential backoff).

    Returns:
        Optional[Any]: The result of the function if successful, or None if all retries fail.

    Raises:
        ValueError: If the function to be retried is None.
        Exception: The last exception encountered if all retries fail.
    """
    if func is None:
        raise ValueError("The function to be retried cannot be None")

    last_exception = None

    for attempt in range(1, max_retries + 1):
        try:
            logger.debug(f"Attempt {attempt} of {max_retries}.")
            result = func()  # Attempt to call the function
            logger.info(f"Attempt {attempt} succeeded.")
            return result  # Return the result if the function succeeds
        except Exception as exception:
            last_exception = exception
            logger.warning(
                f"Attempt {attempt} failed with error: {exception}. "
                f"{'Retrying...' if attempt < max_retries else 'No more retries.'}"
            )
            if attempt < max_retries:
                # Exponential backoff
                time.sleep(delay_seconds * (backoff_factor ** (attempt - 1)))

    logger.error(f"All {max_retries} attempts failed. Last error: {last_exception}")
    raise last_exception  # Raise the last encountered exception after all retries
