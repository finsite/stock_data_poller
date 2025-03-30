"""Test suite for pollers.

Contains fixtures and tests for pollers. Each poller is tested for successful and
timeout scenarios.

Fixtures:
- mock_queue_sender: A fixture to mock the QueueSender's send_message method.
- mock_env: A fixture to provide shared mock environment variables for all pollers.
- poller_fixture: A fixture to provide each poller class and the correct patch path
  for request_with_timeout.

Tests:
- test_poller_success: Test successful poller behavior with mocked API response.
- test_poller_timeout: Test poller handles timeout exceptions gracefully.
"""

import os
from unittest.mock import MagicMock, patch

import pytest
from requests.exceptions import Timeout

from src.pollers.alphavantage_poller import AlphaVantagePoller
from src.pollers.finnhub_poller import FinnhubPoller
from src.pollers.iex_poller import IEXPoller
from src.pollers.polygon_poller import PolygonPoller
from src.pollers.quandl_poller import QuandlPoller
from src.pollers.yfinance_poller import YFinancePoller
from src.utils.setup_logger import setup_logger

# Initialize logger
logger = setup_logger(__name__)

# Dictionary of available pollers and their corresponding patch paths
POLLERS = {
    "alphavantage": (
        AlphaVantagePoller,
        "src.pollers.alphavantage_poller.request_with_timeout",
    ),
    "finnhub": (FinnhubPoller, "src.pollers.finnhub_poller.request_with_timeout"),
    "iex": (IEXPoller, "src.pollers.iex_poller.request_with_timeout"),
    "polygon": (PolygonPoller, "src.pollers.polygon_poller.request_with_timeout"),
    "quandl": (QuandlPoller, "src.pollers.quandl_poller.request_with_timeout"),
    "yfinance": (YFinancePoller, "src.pollers.yfinance_poller.request_with_timeout"),
}


@pytest.fixture
def mock_queue_sender():
    """Fixture to mock the QueueSender's send_message method."""
    mock_sender = MagicMock()
    mock_sender.send_message.return_value = None
    return mock_sender


@pytest.fixture(autouse=True)
def mock_env(monkeypatch):
    """Fixture to provide shared mock environment variables for all pollers."""
    # Set mock environment variables for message queue and API authentication
    monkeypatch.setenv("QUEUE_TYPE", "rabbitmq")
    monkeypatch.setenv("RABBITMQ_HOST", "localhost")
    monkeypatch.setenv("RABBITMQ_EXCHANGE", "stock_data_exchange")
    monkeypatch.setenv("RABBITMQ_ROUTING_KEY", "stock_data")
    monkeypatch.setenv(
        "SQS_QUEUE_URL", "https://sqs.us-east-1.amazonaws.com/123456789012/test-queue"
    )
    monkeypatch.setenv("VAULT_TOKEN", "test-token")


@pytest.fixture(params=POLLERS.keys())
def poller_fixture(request):
    """Fixture to provide each poller class and the correct patch path for
    request_with_timeout.
    """
    poller_key = request.param
    poller_class, patch_path = POLLERS[poller_key]

    # Map poller keys to their respective API key environment variables
    api_keys = {
        "alphavantage": "ALPHA_VANTAGE_API_KEY",
        "finnhub": "FINNHUB_API_KEY",
        "iex": "IEX_API_KEY",
        "polygon": "POLYGON_API_KEY",
        "quandl": "QUANDL_API_KEY",
        "yfinance": None,
    }
    api_key_env_var = api_keys[poller_key]
    api_key = os.getenv(api_key_env_var, "test_api_key") if api_key_env_var else None

    # Instantiate poller with or without api_key
    poller_instance = poller_class(api_key=api_key) if api_key else poller_class()
    return poller_instance, patch_path


def _expected_payload_structure(message: dict):
    """Validate that message has the expected structure."""
    # Ensure required top-level keys are present
    required_keys = ["symbol", "timestamp", "price", "source"]
    for key in required_keys:
        if key not in message:
            pytest.fail(f"Missing top-level key: {key}")

    # Check that 'data' key is a dictionary
    if not isinstance(message.get("data"), dict):
        pytest.fail("'data' key must be a dictionary")

    # Verify presence of required fields within 'data'
    for field in ["open", "high", "low", "close", "volume"]:
        if field not in message["data"]:
            pytest.fail(f"Missing field in data: {field}")


def _mock_success_response():
    """Return a mock successful API response."""
    return {
        "Time Series (5min)": {
            "2024-12-01 10:00:00": {
                "1. open": "150.00",
                "2. high": "155.00",
                "3. low": "149.00",
                "4. close": "152.00",
                "5. volume": "1000",
            }
        }
    }


def test_poller_success(poller_fixture, mock_queue_sender):
    """Test successful poller behavior with mocked API response."""
    poller, patch_path = poller_fixture

    with patch(patch_path, return_value=_mock_success_response()) as mock_request:
        # Assign the mocked send_to_queue method
        poller.send_to_queue = mock_queue_sender.send_message
        poller.poll(["AAPL"])

        # Validate that the request and message sending were successful
        mock_request.assert_called()
        mock_queue_sender.send_message.assert_called_once()
        args, kwargs = mock_queue_sender.send_message.call_args
        _expected_payload_structure(kwargs["message"])


def test_poller_timeout(poller_fixture, mock_queue_sender):
    """Test poller handles timeout exceptions gracefully."""
    poller, patch_path = poller_fixture

    with patch(patch_path, side_effect=Timeout):
        # Assign the mocked send_to_queue method
        poller.send_to_queue = mock_queue_sender.send_message
        poller.poll(["AAPL"])

        # Ensure that no message is sent when a timeout occurs
        mock_queue_sender.send_message.assert_not_called()
