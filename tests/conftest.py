import pytest
import os
from unittest.mock import patch, MagicMock
from requests.exceptions import Timeout
from src.pollers.alphavantage_poller import AlphaVantagePoller
from src.pollers.finnhub_poller import FinnhubPoller
from src.pollers.iex_poller import IEXPoller
from src.pollers.polygon_poller import PolygonPoller
from src.pollers.quandl_poller import QuandlPoller
from src.pollers.yfinance_poller import YFinancePoller

from src.message_queue.queue_sender import QueueSender
from src.utils.validate_environment_variables import validate_environment_variables
from src.utils.setup_logger import setup_logger

# ✅ Set up logger
logger = setup_logger(__name__)

# ✅ List of available pollers
POLLERS = {
    "alphavantage": AlphaVantagePoller,
    "finnhub": FinnhubPoller,
    "iex": IEXPoller,
    "polygon": PolygonPoller,
    "quandl": QuandlPoller,
    "yfinance": YFinancePoller,
}

# ✅ Fixture to mock the QueueSender
@pytest.fixture
def mock_queue_sender():
    """Fixture to mock the QueueSender."""
    mock_sender = MagicMock()
    mock_sender.send_message.return_value = None  # Modify as needed
    return mock_sender

# ✅ Fixture for setting environment variables
@pytest.fixture(autouse=True)
def mock_env(monkeypatch):
    """Mock environment variables required for all pollers."""
    monkeypatch.setenv("QUEUE_TYPE", "rabbitmq")
    monkeypatch.setenv("RABBITMQ_HOST", "localhost")
    monkeypatch.setenv("RABBITMQ_EXCHANGE", "stock_data_exchange")
    monkeypatch.setenv("RABBITMQ_ROUTING_KEY", "stock_data")
    monkeypatch.setenv("SQS_QUEUE_URL", "https://sqs.us-east-1.amazonaws.com/123456789012/test-queue")

# ✅ Fixture to create a poller instance dynamically
@pytest.fixture(params=POLLERS.keys())
def poller_instance(request):
    """Fixture to instantiate each poller dynamically."""
    poller_class = POLLERS[request.param]
    
    # Provide necessary API key based on the poller
    api_keys = {
        "alphavantage": "ALPHA_VANTAGE_API_KEY",
        "finnhub": "FINNHUB_API_KEY",
        "iex": "IEX_API_KEY",
        "polygon": "POLYGON_API_KEY",
        "quandl": "QUANDL_API_KEY",
        "yfinance": None,  # Yahoo Finance does not require an API key
    }
    
    api_key_env_var = api_keys[request.param]
    api_key = os.getenv(api_key_env_var, "test_api_key") if api_key_env_var else None

    return poller_class(api_key=api_key) if api_key else poller_class()

# ✅ Test function for successful polling
@patch("utils.request_with_timeout")
def test_poller_success(mock_request_with_timeout, mock_queue_sender, poller_instance):
    """Test all pollers fetch and process data successfully."""
    
    # ✅ Mock API response (format varies by poller)
    mock_request_with_timeout.return_value = {
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

    # ✅ Inject the mocked queue sender
    poller_instance.send_to_queue = mock_queue_sender.send_message

    # ✅ Execute poller
    poller_instance.poll(["AAPL"])

    # ✅ Ensure queue sender was called at least once
    mock_queue_sender.send_message.assert_called()

# ✅ Test function for handling timeouts
@patch("utils.request_with_timeout", side_effect=Timeout)
def test_poller_timeout(mock_request_with_timeout, mock_queue_sender, poller_instance):
    """Test all pollers gracefully handle request timeouts."""
    
    # ✅ Inject the mocked queue sender
    poller_instance.send_to_queue = mock_queue_sender.send_message

    # ✅ Run poller (should not throw an error)
    poller_instance.poll(["AAPL"])

    # ✅ Ensure queue sender was never called due to failure
    mock_queue_sender.send_message.assert_not_called()
