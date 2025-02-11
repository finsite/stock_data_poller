from unittest.mock import patch
from app.pollers.finnhub_poller import FinnhubPoller
from requests.exceptions import Timeout


@patch("app.utils.request_with_timeout")
def test_finnhub_poller_success(mock_request_with_timeout, mock_queue_sender):
    """Test FinnhubPoller fetches and processes data successfully."""
    mock_request_with_timeout.return_value = {
        "c": 150.25,
        "h": 151.00,
        "l": 149.00,
        "o": 150.00,
        "pc": 149.50,
    }

    poller = FinnhubPoller(api_key="fake_api_key")
    poller.send_to_queue = mock_queue_sender.send_message

    poller.poll(["AAPL"])

    mock_queue_sender.send_message.assert_called_once_with({
        "symbol": "AAPL",
        "timestamp": None,
        "price": 150.25,
        "source": "Finnhub",
        "data": {
            "current": 150.25,
            "high": 151.00,
            "low": 149.00,
            "open": 150.00,
            "previous_close": 149.50,
        },
    })


@patch("app.utils.request_with_timeout")
def test_finnhub_poller_invalid_symbol(mock_request_with_timeout, mock_queue_sender):
    """Test FinnhubPoller handles invalid symbols."""
    mock_request_with_timeout.return_value = {"Error Message": "Invalid symbol"}

    poller = FinnhubPoller(api_key="fake_api_key")
    poller.send_to_queue = mock_queue_sender.send_message

    poller.poll(["INVALID"])

    mock_queue_sender.send_message.assert_not_called()


@patch("app.utils.request_with_timeout")
def test_finnhub_poller_timeout(mock_request_with_timeout, mock_queue_sender):
    """Test FinnhubPoller handles API timeouts."""
    mock_request_with_timeout.side_effect = Timeout("API request timed out.")

    poller = FinnhubPoller(api_key="fake_api_key")
    poller.send_to_queue = mock_queue_sender.send_message

    poller.poll(["AAPL"])

    mock_queue_sender.send_message.assert_not_called()
