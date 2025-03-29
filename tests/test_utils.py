# import os
from unittest.mock import patch

import pytest
import requests

from src.utils.request_with_timeout import request_with_timeout
from src.utils.validate_environment_variables import validate_environment_variables


def test_validate_environment_variables():
    """Test that validate_environment_variables passes when the required
    environment variable is set.
    """
    os.environ["TEST_VAR"] = "value"
    validate_environment_variables(["TEST_VAR"])
    del os.environ["TEST_VAR"]


def test_validate_environment_variables_missing():
    """Test that validate_environment_variables raises an EnvironmentError when
    the required environment variable is missing.
    """
    with pytest.raises(EnvironmentError):
        validate_environment_variables(["MISSING_VAR"])


@patch("requests.get")
def test_request_with_timeout(mock_get):
    """Test that request_with_timeout correctly processes a valid response."""
    mock_get.return_value.json.return_value = {"key": "value"}

    response = request_with_timeout("http://fake-url.com")

    if response != {"key": "value"}:
        pytest.fail(f"Expected {{'key': 'value'}}, got {response}")

    mock_get.assert_called_once()


@patch("requests.get")
def test_request_with_timeout_failure(mock_get):
    """Test that request_with_timeout raises a Timeout exception when the
    request times out.
    """
    mock_get.side_effect = requests.exceptions.Timeout

    with pytest.raises(requests.exceptions.Timeout):
        request_with_timeout("http://fake-url.com")

    mock_get.assert_called_once()


@patch("requests.get")
def test_request_with_timeout_network_error(mock_get):
    """Test that request_with_timeout raises a ConnectionError when the request
    fails due to network issues.
    """
    mock_get.side_effect = requests.exceptions.ConnectionError

    with pytest.raises(requests.exceptions.ConnectionError):
        request_with_timeout("http://fake-url.com")

    mock_get.assert_called_once()
