import logging
from typing import Literal

# Initialize logger
logger = logging.getLogger("poller")


def track_request_metrics(
    status: Literal["success", "failure"], endpoint: str, response_time: float, error_message: str = ""
) -> None:
    """
    Tracks metrics for individual API requests.

    Args:
        status (Literal["success", "failure"]): The status of the request ('success' or 'failure').
        endpoint (str): The API endpoint that was accessed.
        response_time (float): The time taken for the API request in seconds.
        error_message (str): Optional error message for failed requests.

    Raises:
        ValueError: If the status is not 'success' or 'failure'.
    """
    # Validate status
    if status not in {"success", "failure"}:
        logger.error(f"Invalid status '{status}' for endpoint '{endpoint}'. Must be 'success' or 'failure'.")
        raise ValueError(f"Invalid status '{status}'. Must be 'success' or 'failure'.")

    # Construct log message
    if status == "success":
        message = f"Request to {endpoint} completed successfully in {response_time:.2f} seconds."
    else:
        # Include error message for failures if available
        message = f"Request to {endpoint} failed after {response_time:.2f} seconds."
        if error_message:
            message += f" Error: {error_message}"

    # Log the message
    if status == "success":
        logger.info(message)
    else:
        logger.error(message)
