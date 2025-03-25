import logging
from typing import Literal

# Initialize logger
logger = logging.getLogger("poller")


def track_polling_metrics(
    status: Literal["success", "failure"], source: str, symbol: str
) -> None:
    """Tracks metrics for polling operations.

    Args:
        status (Literal["success", "failure"]): The status of the operation ('success' or 'failure').
        source (str): The source of the polling data (e.g., 'yfinance', 'finnhub').
        symbol (str): The symbol for which polling was performed.

    Raises:
        ValueError: If the status is not 'success' or 'failure'.

    """
    # Validate status
    if status not in {"success", "failure"}:
        raise ValueError("Invalid status. Must be 'success' or 'failure'.")

    # Log the result
    message = f"Polling {status} for symbol '{symbol}' from source '{source}'."
    if status == "success":
        logger.info(message)
    else:
        logger.error(message)
