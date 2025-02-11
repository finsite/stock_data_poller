# import logging

# import requests

# logger = logging.getLogger("poller")


# def request_with_timeout(url: str, timeout: int = 10) -> dict:
#     """
#     Request data from a URL with a timeout.

#     Args:
#         url (str): The URL to request data from.
#         timeout (int): The time in seconds to wait for the request to complete.

#     Returns:
#         dict: The JSON response from the request, or None if the request fails.
#     """
#     if not url:
#         logger.error("URL cannot be empty.")
#         return None

#     try:
#         response = requests.get(url, timeout=timeout)
#         response.raise_for_status()

#         if not response:
#             logger.error("No response received from the request.")
#             return None

#         if response.headers.get("Content-Type") != "application/json":
#             logger.error(
#                 f"Expected JSON response from {url}, but got {response.headers.get('Content-Type')}"
#             )
#             return None

#         json_response = response.json()

#         if not json_response:
#             logger.error("No JSON response received from the request.")
#             return None

#         return json_response
#     except requests.exceptions.Timeout:
#         logger.error(f"Timeout occurred while requesting {url}.")
#     except requests.exceptions.RequestException as e:
#         logger.error(f"Request error: {e}")
#     return None
import logging
import requests
from typing import Optional

logger = logging.getLogger("poller")


def request_with_timeout(url: str, timeout: int = 10) -> Optional[dict]:
    """
    Request data from a URL with a timeout.

    Args:
        url (str): The URL to request data from.
        timeout (int): The time in seconds to wait for the request to complete.

    Returns:
        Optional[dict]: The JSON response from the request, or None if the request fails.
    """
    if not url:
        logger.error("URL cannot be empty.")
        return None

    try:
        # Perform the GET request
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Check Content-Type header
        content_type = response.headers.get("Content-Type", "")
        if "application/json" not in content_type:
            logger.error(f"Expected JSON response from {url}, but got {content_type}.")
            return None

        # Parse and return JSON data
        json_response = response.json()
        if not json_response:
            logger.error("Received empty JSON response.")
            return None

        return json_response

    except requests.exceptions.Timeout:
        logger.error(f"Timeout occurred while requesting {url}.")
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error occurred while requesting {url}: {e}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Request exception occurred: {e}")
    except ValueError as e:
        logger.error(f"Error decoding JSON response from {url}: {e}")
    return None
