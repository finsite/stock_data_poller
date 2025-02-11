import os
from typing import List
from app.utils.setup_logger import setup_logger

# Initialize logger
logger = setup_logger(__name__)

def validate_environment_variables(required_variables: List[str]) -> None:
    """
    Verify that all required environment variables are set.

    Args:
        required_variables (List[str]): A list of environment variables that are required for the script to run.

    Raises:
        EnvironmentError: If any of the environment variables are missing.
    """
    # Check that required_variables is a list of strings
    if not isinstance(required_variables, list) or not all(
        isinstance(var, str) for var in required_variables
    ):
        logger.error("required_variables must be a list of strings.")
        raise TypeError("required_variables must be a list of strings.")

    # Check for missing environment variables
    missing_variables = [
        variable for variable in required_variables if not os.getenv(variable)
    ]

    # Log and raise an error if any variables are missing
    if missing_variables:
        logger.error(
            f"Missing required environment variables: {', '.join(missing_variables)}"
        )
        raise EnvironmentError(
            f"Missing required environment variables: {', '.join(missing_variables)}"
        )

    # Log success if all variables are set
    logger.info("All required environment variables are set.")
