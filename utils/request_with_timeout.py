import logging
import requests
from typing import Optional

logger = logging.getLogger("poller")

class RequestError(Exception):
    """Custom exception for handling request-related errors."""
    pass

def request_with_timeout(url: str, timeout: int = 10) -> Optional[dict]:
    """
    Request data from a URL with a timeout and handle errors appropriately.

    Args:
        url (str): The URL to request data from.
        timeout (int): The time in seconds to wait for the request to complete.

    Returns:
        Optional[dict]: The JSON response from the request, or None if the request fails.
    """
    if not url:
        logger.error("URL cannot be empty.")
        raise RequestError("URL cannot be empty.")

    try:
        # Perform the GET request
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Check Content-Type header
        content_type = response.headers.get("Content-Type", "")
        if "application/json" not in content_type:
            logger.error(f"Expected JSON response from {url}, but got {content_type}.")
            raise RequestError(f"Expected JSON response from {url}, but got {content_type}.")

        # Parse and return JSON data
        try:
            json_response = response.json()
        except ValueError:
            logger.error(f"Error decoding JSON response from {url}.")
            raise RequestError(f"Error decoding JSON from {url}")

        if not json_response:
            logger.warning(f"Received empty JSON response from {url}.")
            return None

        return json_response

    except requests.exceptions.Timeout:
        logger.error(f"Timeout occurred while requesting {url}.")
        raise RequestError(f"Timeout occurred while requesting {url}")
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error occurred while requesting {url}: {e}")
        raise RequestError(f"HTTP error occurred: {str(e)}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Request exception occurred while requesting {url}: {e}")
        raise RequestError(f"Request exception: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error while requesting {url}: {e}")
        raise RequestError(f"Unexpected error: {str(e)}")
