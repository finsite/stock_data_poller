# Tests for the IEXPoller class

from unittest.mock import patch

from requests.exceptions import Timeout

from src.pollers.iex_poller import IEXPoller


@patch("src.pollers.iex_poller.IEXPoller.send_to_queue")
@patch("src.utils.request_with_timeout")
def test_iex_poller_success(mock_request_with_timeout, mock_send_to_queue):
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

    poller = IEXPoller()
    poller.poll(["AAPL"])

    mock_send_to_queue.assert_called_once_with(
        {
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
        }
    )


@patch("src.pollers.iex_poller.IEXPoller.send_to_queue")
@patch("src.utils.request_with_timeout")
def test_iex_poller_invalid_symbol(mock_request_with_timeout, mock_send_to_queue):
    """Test IEXPoller handles invalid symbols."""
    mock_request_with_timeout.return_value = {"Error Message": "Invalid symbol"}

    poller = IEXPoller()
    poller.poll(["INVALID"])

    mock_send_to_queue.assert_not_called()


@patch("src.pollers.iex_poller.IEXPoller.send_to_queue")
@patch("src.utils.request_with_timeout")
def test_iex_poller_empty_response(mock_request_with_timeout, mock_send_to_queue):
    """Test IEXPoller handles an empty API response."""
    mock_request_with_timeout.return_value = {}

    poller = IEXPoller()
    poller.poll(["AAPL"])

    mock_send_to_queue.assert_not_called()


@patch("src.pollers.iex_poller.IEXPoller.send_to_queue")
@patch("src.utils.request_with_timeout")
def test_iex_poller_timeout(mock_request_with_timeout, mock_send_to_queue):
    """Test IEXPoller handles API timeouts."""
    mock_request_with_timeout.side_effect = Timeout("API request timed out.")

    poller = IEXPoller()
    poller.poll(["AAPL"])

    mock_send_to_queue.assert_not_called()


@patch("src.pollers.iex_poller.IEXPoller.send_to_queue")
@patch("src.utils.request_with_timeout")
def test_iex_poller_missing_field(mock_request_with_timeout, mock_send_to_queue):
    """Test IEXPoller handles missing fields in the response."""
    mock_request_with_timeout.return_value = {
        "symbol": "AAPL",
        "latestUpdate": 1682468986000,
        "open": 149.00,
        "high": 151.50,
        "low": 148.00,
        "volume": 2000000,
    }

    poller = IEXPoller()
    poller.poll(["AAPL"])

    mock_send_to_queue.assert_not_called()


@patch("src.pollers.iex_poller.IEXPoller.send_to_queue")
@patch("src.utils.request_with_timeout")
def test_iex_poller_invalid_data_format(mock_request_with_timeout, mock_send_to_queue):
    """Test IEXPoller handles unexpected data formats."""
    mock_request_with_timeout.return_value = "Invalid data format"

    poller = IEXPoller()
    poller.poll(["AAPL"])

    mock_send_to_queue.assert_not_called()

