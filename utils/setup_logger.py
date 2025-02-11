# import logging
# from typing import Optional


# def setup_logger(name: Optional[str] = None) -> logging.Logger:
#     """
#     Configure and return a logger for the application.

#     This logger logs messages to the console using a StreamHandler and a
#     specified format. The logging level is set to INFO.

#     Args:
#         name: The name of the logger to create. If not specified, a default
#             logger named "poller" is created.

#     Returns:
#         logging.Logger: Configured logger instance.
#     """
#     # Create a logger instance
#     logger = logging.getLogger(name or "poller")

#     # Set the logging level to INFO to capture all messages
#     logger.setLevel(logging.INFO)

#     # Create a StreamHandler to log messages to the console
#     handler = logging.StreamHandler()

#     # Define a format for the log messages
#     formatter = logging.Formatter(
#         "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
#     )

#     # Set the format for the StreamHandler
#     handler.setFormatter(formatter)

#     # Add the StreamHandler to the logger
#     logger.addHandler(handler)

#     # Return the configured logger
#     return logger


# # Create the logger instance
# logger = setup_logger()
import logging
from typing import Optional


def setup_logger(name: Optional[str] = None, level: int = logging.INFO) -> logging.Logger:
    """
    Configure and return a logger for the application.

    This logger logs messages to the console using a StreamHandler and a
    specified format. If the logger already exists, it simply returns the existing instance.

    Args:
        name (Optional[str]): The name of the logger to create. If not specified, a default
            logger named "poller" is created.
        level (int): The logging level to set. Defaults to INFO.

    Returns:
        logging.Logger: Configured logger instance.
    """
    # Determine the logger name
    logger_name = name or "poller"

    # Check if the logger already exists to avoid duplicate handlers
    logger = logging.getLogger(logger_name)
    if not logger.hasHandlers():
        # Set the logging level
        logger.setLevel(level)

        # Create a StreamHandler to log messages to the console
        handler = logging.StreamHandler()

        # Define a format for the log messages
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

        # Set the format for the StreamHandler
        handler.setFormatter(formatter)

        # Add the StreamHandler to the logger
        logger.addHandler(handler)

    return logger


# Create the logger instance
logger = setup_logger(level=logging.DEBUG)
