from unittest.mock import patch
from app.pollers.quandl_poller import QuandlPoller
from requests.exceptions import Timeout


@patch("app.utils.request_with_timeout")
def test_quandl_poller_success(mock_request_with_timeout, mock_queue_sender):
    """Test QuandlPoller fetches and processes data successfully."""
    mock_request_with_timeout.return_value = {
        "dataset": {
            "dataset_code": "AAPL",
            "data": [["2024-12-01", 150, 155, 145, 152, 1000]],
        }
    }

    poller = QuandlPoller(api_key="fake_api_key")
    poller.send_to_queue = mock_queue_sender.send_message

    poller.poll(["AAPL"])

    mock_queue_sender.send_message.assert_called_once_with({
        "symbol": "AAPL",
        "timestamp": "2024-12-01",
        "price": 152.00,
        "source": "Quandl",
        "data": {
            "open": 150.00,
            "high": 155.00,
            "low": 145.00,
            "close": 152.00,
            "volume": 1000,
        },
    })


@patch("app.utils.request_with_timeout")
def test_quandl_poller_invalid_symbol(mock_request_with_timeout, mock_queue_sender):
    """Test QuandlPoller handles invalid symbols."""
    mock_request_with_timeout.return_value = {"Error Message": "Invalid symbol"}

    poller = QuandlPoller(api_key="fake_api_key")
    poller.send_to_queue = mock_queue_sender.send_message

    poller.poll(["INVALID"])

    mock_queue_sender.send_message.assert_not_called()


@patch("app.utils.request_with_timeout")
def test_quandl_poller_timeout(mock_request_with_timeout, mock_queue_sender):
    """Test QuandlPoller handles API timeouts."""
    mock_request_with_timeout.side_effect = Timeout("API request timed out.")

    poller = QuandlPoller(api_key="fake_api_key")
    poller.send_to_queue = mock_queue_sender.send_message

    poller.poll(["AAPL"])

    mock_queue_sender.send_message.assert_not_called()
