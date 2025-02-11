from unittest.mock import patch
from app.utils.validate_environment_variables import validate_environment_variables
from app.utils.request_with_timeout import request_with_timeout


def test_validate_environment_variables():
    import os
    os.environ["TEST_VAR"] = "value"

    validate_environment_variables(["TEST_VAR"])


def test_validate_environment_variables_missing():
    import pytest
    with pytest.raises(EnvironmentError):
        validate_environment_variables(["MISSING_VAR"])


@patch("requests.get")
def test_request_with_timeout(mock_get):
    mock_get.return_value.json.return_value = {"key": "value"}
    response = request_with_timeout("http://fake-url.com")

    assert response == {"key": "value"}
    mock_get.assert_called_once()
