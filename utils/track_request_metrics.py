# import logging


# def track_request_metrics(status: str, endpoint: str, response_time: float) -> None:
#     """
#     Tracks metrics for individual API requests.

#     Args:
#         status (str): The status of the request ('success' or 'failure').
#         endpoint (str): The API endpoint that was accessed.
#         response_time (float): The time taken for the API request in seconds.

#     Raises:
#         ValueError: If the status is not 'success' or 'failure'.
#     """
#     if status not in {"success", "failure"}:
#         raise ValueError("Invalid status. Must be 'success' or 'failure'.")

#     if status == "success":
#         logging.info(
#             "Request to %s completed successfully in %.2f seconds.",
#             endpoint,
#             response_time,
#         )
#     else:
#         logging.error(
#             "Request to %s failed after %.2f seconds.", endpoint, response_time
#         )
import logging
from typing import Literal

# Initialize logger
logger = logging.getLogger("poller")


def track_request_metrics(
    status: Literal["success", "failure"], endpoint: str, response_time: float
) -> None:
    """
    Tracks metrics for individual API requests.

    Args:
        status (Literal["success", "failure"]): The status of the request ('success' or 'failure').
        endpoint (str): The API endpoint that was accessed.
        response_time (float): The time taken for the API request in seconds.

    Raises:
        ValueError: If the status is not 'success' or 'failure'.
    """
    # Validate status
    if status not in {"success", "failure"}:
        raise ValueError("Invalid status. Must be 'success' or 'failure'.")

    # Construct log message
    message = (
        f"Request to {endpoint} completed successfully in {response_time:.2f} seconds."
        if status == "success"
        else f"Request to {endpoint} failed after {response_time:.2f} seconds."
    )

    # Log the message
    if status == "success":
        logger.info(message)
    else:
        logger.error(message)
