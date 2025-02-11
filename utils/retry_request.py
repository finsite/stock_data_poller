# import time
# import typing


# def retry_request(
#     func: typing.Callable[[], typing.Any],
#     *,
#     max_retries: int = 3,
#     delay_seconds: int = 5
# ) -> typing.Any:
#     """
#     Retries a given function if it raises an exception.

#     Args:
#         func: The function to be retried.
#         max_retries: The maximum number of retry attempts. Defaults to 3.
#         delay_seconds: The delay in seconds between retries. Defaults to 5.

#     Returns:
#         The result of the function if successful.

#     Raises:
#         ValueError: If the function to be retried is None.
#         Exception: The last exception encountered if all retries fail.
#     """
#     if func is None:
#         raise ValueError("The function to be retried cannot be None")

#     for attempt in range(max_retries):
#         try:
#             return func()
#         except Exception as exception:
#             if attempt < max_retries - 1:
#                 time.sleep(delay_seconds)
#             else:
#                 raise exception from None
import time
import logging
from typing import Callable, Any, Optional

# Initialize logger
logger = logging.getLogger("poller")


def retry_request(
    func: Callable[[], Any],
    *,
    max_retries: int = 3,
    delay_seconds: int = 5
) -> Optional[Any]:
    """
    Retries a given function if it raises an exception.

    Args:
        func (Callable[[], Any]): The function to be retried.
        max_retries (int): The maximum number of retry attempts. Defaults to 3.
        delay_seconds (int): The delay in seconds between retries. Defaults to 5.

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
            return func()
        except Exception as exception:
            last_exception = exception
            logger.warning(
                f"Attempt {attempt} failed with error: {exception}. "
                f"{'Retrying...' if attempt < max_retries else 'No more retries.'}"
            )
            if attempt < max_retries:
                time.sleep(delay_seconds)

    logger.error(f"All {max_retries} attempts failed. Last error: {last_exception}")
    raise last_exception
