from unittest.mock import patch, MagicMock
from app.pollers.iex_poller import IEXPoller
from requests.exceptions import Timeout


@patch("app.utils.request_with_timeout")
def test_iex_poller_success(mock_request_with_timeout, mock_queue_sender):
    """Test IEXPoller fetches and processes data successfully."""
    mock_request_with_timeout.return_value = {
        "symbol": "AAPL",
        "latestUpdate": 1682468986000,
        "latestPrice": 150.25,
        "open": 149.00,
        "high": 151.50,
        "low": 148.00,
        "volume": 2000000,
    }

    poller = IEXPoller(api_key="fake_api_key")
    poller.send_to_queue = mock_queue_sender.send_message

    poller.poll(["AAPL"])

    mock_queue_sender.send_message.assert_called_once_with({
        "symbol": "AAPL",
        "timestamp": 1682468986000,
        "price": 150.25,
        "source": "IEX",
        "data": {
            "open": 149.00,
            "high": 151.50,
            "low": 148.00,
            "close": 150.25,
            "volume": 2000000,
        },
    })


@patch("app.utils.request_with_timeout")
def test_iex_poller_invalid_symbol(mock_request_with_timeout, mock_queue_sender):
    """Test IEXPoller handles invalid symbols."""
    mock_request_with_timeout.return_value = {"Error Message": "Invalid symbol"}

    poller = IEXPoller(api_key="fake_api_key")
    poller.send_to_queue = mock_queue_sender.send_message

    poller.poll(["INVALID"])

    mock_queue_sender.send_message.assert_not_called()


@patch("app.utils.request_with_timeout")
def test_iex_poller_empty_response(mock_request_with_timeout, mock_queue_sender):
    """Test IEXPoller handles an empty API response."""
    mock_request_with_timeout.return_value = {}

    poller = IEXPoller(api_key="fake_api_key")
    poller.send_to_queue = mock_queue_sender.send_message

    poller.poll(["AAPL"])

    mock_queue_sender.send_message.assert_not_called()


@patch("app.utils.request_with_timeout")
def test_iex_poller_timeout(mock_request_with_timeout, mock_queue_sender):
    """Test IEXPoller handles API timeouts."""
    mock_request_with_timeout.side_effect = Timeout("API request timed out.")

    poller = IEXPoller(api_key="fake_api_key")
    poller.send_to_queue = mock_queue_sender.send_message

    poller.poll(["AAPL"])

    mock_queue_sender.send_message.assert_not_called()
