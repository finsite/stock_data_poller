# Import necessary libraries
import os
from unittest.mock import patch

import pytest
import requests

# Import functions to be tested
from src.utils.request_with_timeout import request_with_timeout
from src.utils.validate_environment_variables import validate_environment_variables


def test_validate_environment_variables():
    """
    Test validate_environment_variables with environment variable set.

    This test ensures that the validate_environment_variables function passes without
    errors when the required environment variable is set.
    """
    # Set a test environment variable
    os.environ["TEST_VAR"] = "value"

    # Validate that the environment variable is set
    validate_environment_variables(["TEST_VAR"])

    # Clean up by deleting the test environment variable
    del os.environ["TEST_VAR"]


def test_validate_environment_variables_missing():
    """
    Test validate_environment_variables with missing environment variable.

    This test checks that the validate_environment_variables function raises an
    EnvironmentError when the required environment variable is missing.
    """
    # Expect an EnvironmentError to be raised for a missing variable
    with pytest.raises(EnvironmentError):
        validate_environment_variables(["MISSING_VAR"])


@patch("requests.get")
def test_request_with_timeout(mock_get):
    """
    Test request_with_timeout with a valid response.

    This test verifies that the request_with_timeout function correctly processes a
    valid JSON response from a mocked GET request.
    """
    # Mock a successful JSON response
    mock_get.return_value.json.return_value = {"key": "value"}

    # Call the function being tested
    response = request_with_timeout("http://fake-url.com")

    # Assert that the response matches the expected value
    if response != {"key": "value"}:
        pytest.fail(f"Expected {{'key': 'value'}}, got {response}")

    # Ensure that the GET request was called once
    mock_get.assert_called_once()


@patch("requests.get")
def test_request_with_timeout_failure(mock_get):
    """
    Test request_with_timeout with a timeout exception.

    This test ensures that the request_with_timeout function raises a Timeout exception
    when the GET request times out.
    """
    # Mock a timeout exception
    mock_get.side_effect = requests.exceptions.Timeout

    # Expect a Timeout exception to be raised
    with pytest.raises(requests.exceptions.Timeout):
        request_with_timeout("http://fake-url.com")

    # Ensure that the GET request was called once
    mock_get.assert_called_once()


@patch("requests.get")
def test_request_with_timeout_network_error(mock_get):
    """
    Test request_with_timeout with a network error.

    This test verifies that the request_with_timeout function raises a ConnectionError
    when the GET request fails due to network issues.
    """
    # Mock a connection error
    mock_get.side_effect = requests.exceptions.ConnectionError

    # Expect a ConnectionError to be raised
    with pytest.raises(requests.exceptions.ConnectionError):
        request_with_timeout("http://fake-url.com")

    # Ensure that the GET request was called once
    mock_get.assert_called_once()
