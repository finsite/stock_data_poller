import logging
from typing import Literal

# Initialize logger for tracking request metrics
logger = logging.getLogger("poller")


def track_request_metrics(
    status: Literal["success", "failure"], endpoint: str, response_time: float
) -> None:
    """Tracks metrics for individual API requests.

    Args:
    ----
        status (Literal["success", "failure"]): The status of the request ('success' or 'failure').
        endpoint (str): The API endpoint that was accessed.
        response_time (float): The time taken for the API request in seconds.

    Raises:
    ------
        ValueError: If the status is not 'success' or 'failure'.

    """
    # Validate status to ensure it is either 'success' or 'failure'
    if status not in {"success", "failure"}:
        raise ValueError("Invalid status. Must be 'success' or 'failure'.")

    # Construct log message based on the status
    message = (
        f"Request to {endpoint} completed successfully in {response_time:.2f} seconds."
        if status == "success"
        else f"Request to {endpoint} failed after {response_time:.2f} seconds."
    )

    # Log the message with appropriate log level
    if status == "success":
        logger.info(message)  # Log info for successful requests
    else:
        logger.error(message)  # Log error for failed requests
