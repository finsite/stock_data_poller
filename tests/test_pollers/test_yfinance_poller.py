
from unittest.mock import patch
from requests.exceptions import Timeout
from src.pollers.yfinance_poller import YFinancePoller


@patch("yfinance.Ticker")
def test_yfinance_poller_success(mock_ticker, mock_queue_sender):
    """Test YFinancePoller fetches and processes data successfully."""
    # Mocking the return value of the yfinance history function
    mock_ticker.return_value.history.return_value = {
        "Open": [100],
        "High": [110],
        "Low": [95],
        "Close": [105],
        "Volume": [1000],
    }

    poller = YFinancePoller()
    poller.send_to_queue = mock_queue_sender.send_message

    # Run the poller for the symbol "AAPL"
    poller.poll(["AAPL"])

    # Assert that send_message is called once
    mock_queue_sender.send_message.assert_called_once_with({
        "symbol": "AAPL",
        "timestamp": "2024-12-01T10:00:00",  # Adjust the timestamp based on your needs
        "price": 105.00,
        "source": "YFinance",
        "data": {
            "open": 100.00,
            "high": 110.00,
            "low": 95.00,
            "close": 105.00,
            "volume": 1000,
        },
    })


@patch("yfinance.Ticker")
def test_yfinance_poller_invalid_symbol(mock_ticker, mock_queue_sender):
    """Test YFinancePoller handles invalid symbols."""
    # Mocking an invalid response (empty data)
    mock_ticker.return_value.history.return_value = {}

    poller = YFinancePoller()
    poller.send_to_queue = mock_queue_sender.send_message

    # Polling for an invalid symbol
    poller.poll(["INVALID"])

    # Assert that send_message is not called for an invalid symbol
    mock_queue_sender.send_message.assert_not_called()


@patch("yfinance.Ticker")
def test_yfinance_poller_timeout(mock_ticker, mock_queue_sender):
    """Test YFinancePoller handles API timeouts."""
    # Mocking a timeout error
    mock_ticker.side_effect = Timeout("API request timed out.")

    poller = YFinancePoller()
    poller.send_to_queue = mock_queue_sender.send_message

    # Polling for a symbol when there's a timeout
    poller.poll(["AAPL"])

    # Assert that send_message is not called in case of timeout
    mock_queue_sender.send_message.assert_not_called()


@patch("yfinance.Ticker")
def test_yfinance_poller_empty_response(mock_ticker, mock_queue_sender):
    """Test YFinancePoller handles empty data response."""
    # Mocking an empty response
    mock_ticker.return_value.history.return_value = {}

    poller = YFinancePoller()
    poller.send_to_queue = mock_queue_sender.send_message

    # Polling for a symbol when the response is empty
    poller.poll(["AAPL"])

    # Assert that send_message is not called when the response is empty
    mock_queue_sender.send_message.assert_not_called()


@patch("yfinance.Ticker")
def test_yfinance_poller_invalid_data_format(mock_ticker, mock_queue_sender):
    """Test YFinancePoller handles invalid data format."""
    # Mocking an invalid data format (string instead of a dict or list)
    mock_ticker.return_value.history.return_value = "Invalid data format"

    poller = YFinancePoller()
    poller.send_to_queue = mock_queue_sender.send_message

    # Polling for a symbol with invalid data format
    poller.poll(["AAPL"])

    # Assert that send_message is not called because of invalid data format
    mock_queue_sender.send_message.assert_not_called()

