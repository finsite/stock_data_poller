# import pytest
# from unittest.mock import MagicMock

# @pytest.fixture
# def mock_queue_sender():
#     """Fixture to mock the QueueSender."""
#     mock_sender = MagicMock()

#     # Mocking the send_message method to return a mock response
#     mock_sender.send_message.return_value = None  # Modify as needed (e.g., to return a fake message ID)
    
#     # If you need to mock other methods like send_to_queue, add them here
#     mock_sender.send_to_queue.return_value = None  # Modify as needed

#     return mock_sender
import pytest
from unittest.mock import patch, MagicMock
from requests.exceptions import Timeout
from src.pollers.alphavantage_poller import AlphaVantagePoller

# Fixture to mock the QueueSender
@pytest.fixture
def mock_queue_sender():
    """Fixture to mock the QueueSender."""
    mock_sender = MagicMock()
    # Mocking the send_message method to return a mock response
    mock_sender.send_message.return_value = None  # Modify as needed
    return mock_sender

# Test function for successful data fetch and processing
@patch("src.utils.request_with_timeout")
def test_alphavantage_poller_success(mock_request_with_timeout, mock_queue_sender, monkeypatch):
    """Test AlphaVantagePoller fetches and processes data successfully."""
    # Set required environment variables
    monkeypatch.setenv("QUEUE_TYPE", "your_queue_type")
    monkeypatch.setenv("RABBITMQ_HOST", "your_rabbitmq_host")
    monkeypatch.setenv("RABBITMQ_EXCHANGE", "your_rabbitmq_exchange")
    monkeypatch.setenv("RABBITMQ_ROUTING_KEY", "your_rabbitmq_routing_key")
    monkeypatch.setenv("SQS_QUEUE_URL", "your_sqs_queue_url")

    # Mock API response
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

    # Initialize poller
    poller = AlphaVantagePoller(api_key="fake_api_key")
    poller.send_to_queue = mock_queue_sender.send_message

    # Execute poller
    poller.poll(["AAPL"])

    # Assert that send_message was called with the expected data
    mock_queue_sender.send_message.assert_called_once_with({
        "symbol": "AAPL",
        "timestamp": "2024-12-01 10:00:00",
        "price": 152.00,
        "source": "AlphaVantage",
        "data": {
            "open": 150.00,
            "high": 155.00,
            "low": 149.00,
            "close": 152.00,
            "volume": 1000,
        },
    })

# Additional test functions (e.g., for invalid symbols, timeouts, etc.) would follow a similar structure,
# including the use of monkeypatch to set environment variables and the mock_queue_sender fixture.
