import os
import pytest
import requests
from unittest.mock import patch
from src.utils.validate_environment_variables import validate_environment_variables
from src.utils.request_with_timeout import request_with_timeout


def test_validate_environment_variables():
    """
    Test that validate_environment_variables passes when the required environment variable is set.
    """
    os.environ["TEST_VAR"] = "value"  # Set the environment variable for testing
    validate_environment_variables(["TEST_VAR"])
    del os.environ["TEST_VAR"]  # Clean up the environment variable after the test


def test_validate_environment_variables_missing():
    """
    Test that validate_environment_variables raises an EnvironmentError when the required environment variable is missing.
    """
    with pytest.raises(EnvironmentError):
        validate_environment_variables(["MISSING_VAR"])


@patch("requests.get")
def test_request_with_timeout(mock_get):
    """
    Test that request_with_timeout correctly processes a valid response.
    """
    mock_get.return_value.json.return_value = {"key": "value"}  # Mock the JSON response
    response = request_with_timeout("http://fake-url.com")
    assert response == {"key": "value"}
    mock_get.assert_called_once()


@patch("requests.get")
def test_request_with_timeout_failure(mock_get):
    """
    Test that request_with_timeout raises a Timeout exception when the request times out.
    """
    mock_get.side_effect = requests.exceptions.Timeout  # Mock a timeout exception

    with pytest.raises(requests.exceptions.Timeout):
        request_with_timeout("http://fake-url.com")
    mock_get.assert_called_once()


@patch("requests.get")
def test_request_with_timeout_network_error(mock_get):
    """
    Test that request_with_timeout raises a ConnectionError when the request fails due to network issues.
    """
    mock_get.side_effect = (
        requests.exceptions.ConnectionError
    )  # Mock a connection error

    with pytest.raises(requests.exceptions.ConnectionError):
        request_with_timeout("http://fake-url.com")
    mock_get.assert_called_once()
