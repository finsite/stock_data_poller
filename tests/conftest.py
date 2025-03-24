import os
import pytest
from unittest.mock import patch, MagicMock
from requests.exceptions import Timeout

from src.pollers.alphavantage_poller import AlphaVantagePoller
from src.pollers.finnhub_poller import FinnhubPoller
from src.pollers.iex_poller import IEXPoller
from src.pollers.polygon_poller import PolygonPoller
from src.pollers.quandl_poller import QuandlPoller
from src.pollers.yfinance_poller import YFinancePoller

from src.utils.setup_logger import setup_logger

logger = setup_logger(__name__)

# ✅ Available pollers and their import path for patching
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
    monkeypatch.setenv("QUEUE_TYPE", "rabbitmq")
    monkeypatch.setenv("RABBITMQ_HOST", "localhost")
    monkeypatch.setenv("RABBITMQ_EXCHANGE", "stock_data_exchange")
    monkeypatch.setenv("RABBITMQ_ROUTING_KEY", "stock_data")
    monkeypatch.setenv(
        "SQS_QUEUE_URL", "https://sqs.us-east-1.amazonaws.com/123456789012/test-queue"
    )
    # ✅ Added to prevent import error from src/config.py
    monkeypatch.setenv("VAULT_TOKEN", "test-token")


@pytest.fixture(params=POLLERS.keys())
def poller_fixture(request):
    """Fixture to provide each poller class and the correct patch path for request_with_timeout."""
    poller_key = request.param
    poller_class, patch_path = POLLERS[poller_key]

    # Set fake API key if needed
    api_keys = {
        "alphavantage": "ALPHA_VANTAGE_API_KEY",
        "finnhub": "FINNHUB_API_KEY",
        "iex": "IEX_API_KEY",
        "polygon": "POLYGON_API_KEY",
        "quandl": "QUANDL_API_KEY",
        "yfinance": None,  # No API key required
    }
    api_key_env_var = api_keys[poller_key]
    api_key = os.getenv(api_key_env_var, "test_api_key") if api_key_env_var else None

    poller_instance = poller_class(api_key=api_key) if api_key else poller_class()
    return poller_instance, patch_path


def _expected_payload_structure(message: dict):
    """Validate that message has the expected structure."""
    assert "symbol" in message
    assert "timestamp" in message
    assert "price" in message
    assert "source" in message
    assert isinstance(message["data"], dict)
    for field in ["open", "high", "low", "close", "volume"]:
        assert field in message["data"]


def _mock_success_response():
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
        poller.send_to_queue = mock_queue_sender.send_message
        poller.poll(["AAPL"])

        mock_request.assert_called()
        mock_queue_sender.send_message.assert_called_once()
        args, kwargs = mock_queue_sender.send_message.call_args
        _expected_payload_structure(kwargs["message"])


def test_poller_timeout(poller_fixture, mock_queue_sender):
    """Test poller handles timeout exceptions gracefully."""
    poller, patch_path = poller_fixture

    with patch(patch_path, side_effect=Timeout):
        poller.send_to_queue = mock_queue_sender.send_message
        poller.poll(["AAPL"])

        mock_queue_sender.send_message.assert_not_called()
