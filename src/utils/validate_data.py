import logging
from typing import Any

# Initialize the logger
logger = logging.getLogger(__name__)


def validate_data(data: dict[str, Any]) -> bool:
    """Validates the data to ensure it conforms to the required schema.

    Parameters
    ----------
        data (Dict[str, Any]): The data to validate.

    Returns
    -------
        bool: True if data is valid, False otherwise.

    """
    # Define the required keys for validation
    required_keys = {"symbol", "price", "volume", "timestamp"}

    # Check if the input is a dictionary
    if not isinstance(data, dict):
        logger.error("Invalid data type. Expected a dictionary.")
        return False

    # Check if all required keys are present in the data
    missing_keys = required_keys - data.keys()
    if missing_keys:
        logger.error(f"Missing required keys in data: {missing_keys}")
        return False

    # Validate individual fields using helper functions
    if not _validate_symbol(data["symbol"]):
        return False
    if not _validate_price(data["price"]):
        return False
    if not _validate_volume(data["volume"]):
        return False
    return _validate_timestamp(data["timestamp"])


def _validate_symbol(symbol: Any) -> bool:
    """Validates the 'symbol' field to ensure it is a string of alphabetical characters.

    Parameters
    ----------
        symbol (Any): The value of the 'symbol' field.

    Returns
    -------
        bool: True if valid, False otherwise.

    """
    if not isinstance(symbol, str) or not symbol.isalpha():
        logger.error(f"Invalid symbol format: {symbol}")
        return False
    return True


def _validate_price(price: Any) -> bool:
    """Validates the 'price' field to ensure it is a non-negative number.

    Parameters
    ----------
        price (Any): The value of the 'price' field.

    Returns
    -------
        bool: True if valid, False otherwise.

    """
    if not isinstance(price, (int, float)) or price < 0:
        logger.error(f"Invalid price: {price}")
        return False
    return True


def _validate_volume(volume: Any) -> bool:
    """Validates the 'volume' field to ensure it is a non-negative integer.

    Parameters
    ----------
        volume (Any): The value of the 'volume' field.

    Returns
    -------
        bool: True if valid, False otherwise.

    """
    if not isinstance(volume, int) or volume < 0:
        logger.error(f"Invalid volume: {volume}")
        return False
    return True


def _validate_timestamp(timestamp: Any) -> bool:
    """Validates the 'timestamp' field to ensure it is a string.

    Parameters
    ----------
        timestamp (Any): The value of the 'timestamp' field.

    Returns
    -------
        bool: True if valid, False otherwise.

    """
    if not isinstance(timestamp, str):
        logger.error(f"Invalid timestamp format: {timestamp}")
        return False
    return True
