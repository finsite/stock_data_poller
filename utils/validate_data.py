import logging
from typing import Dict, Any

# Initialize the logger
logger = logging.getLogger(__name__)

def validate_data(data: Dict[str, Any]) -> bool:
    """
    Validates the data to ensure it conforms to the required schema.

    Parameters:
        data (Dict[str, Any]): The data to validate.

    Returns:
        bool: True if data is valid, False otherwise.
    """
    required_keys = {"symbol", "price", "volume", "timestamp"}

    # Check if the input is a dictionary
    if not isinstance(data, dict):
        logger.error(f"Invalid data type. Expected a dictionary, but got {type(data).__name__}.")
        return False

    # Check if all required keys are present
    missing_keys = required_keys - data.keys()
    if missing_keys:
        logger.error(f"Missing required keys in data: {missing_keys}.")
        return False

    # Validate individual fields
    if not _validate_symbol(data["symbol"]):
        return False
    if not _validate_price(data["price"]):
        return False
    if not _validate_volume(data["volume"]):
        return False
    if not _validate_timestamp(data["timestamp"]):
        return False

    return True


def _validate_symbol(symbol: Any) -> bool:
    """
    Validates the 'symbol' field.

    Parameters:
        symbol (Any): The value of the 'symbol' field.

    Returns:
        bool: True if valid, False otherwise.
    """
    if not isinstance(symbol, str) or not symbol.isalpha():
        logger.error(f"Invalid symbol format: {symbol}. Expected a string of alphabets only.")
        return False
    return True


def _validate_price(price: Any) -> bool:
    """
    Validates the 'price' field.

    Parameters:
        price (Any): The value of the 'price' field.

    Returns:
        bool: True if valid, False otherwise.
    """
    if not isinstance(price, (int, float)) or price < 0:
        logger.error(f"Invalid price: {price}. Expected a non-negative number.")
        return False
    return True


def _validate_volume(volume: Any) -> bool:
    """
    Validates the 'volume' field.

    Parameters:
        volume (Any): The value of the 'volume' field.

    Returns:
        bool: True if valid, False otherwise.
    """
    if not isinstance(volume, int) or volume < 0:
        logger.error(f"Invalid volume: {volume}. Expected a non-negative integer.")
        return False
    return True


def _validate_timestamp(timestamp: Any) -> bool:
    """
    Validates the 'timestamp' field.

    Parameters:
        timestamp (Any): The value of the 'timestamp' field.

    Returns:
        bool: True if valid, False otherwise.
    """
    if not isinstance(timestamp, str):
        logger.error(f"Invalid timestamp format: {timestamp}. Expected a string.")
        return False
    
    # Optionally, validate the timestamp format (e.g., ISO 8601)
    try:
        # If your timestamps are in ISO 8601 format
        from datetime import datetime
        datetime.fromisoformat(timestamp)
    except ValueError:
        logger.error(f"Invalid timestamp value: {timestamp}. Could not parse it as a valid ISO 8601 timestamp.")
        return False

    return True
