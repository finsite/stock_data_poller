# Tests for the IEXPoller class

from unittest.mock import patch

from requests.exceptions import Timeout

from src.app.pollers.iex_poller import IEXPoller


@patch("src.app.pollers.iex_poller.IEXPoller.send_to_queue")
@patch("src.app.utils.request_with_timeout")
def test_iex_poller_success(mock_request_with_timeout, mock_send_to_queue):
    """Test IEXPoller fetches and processes data successfully."""
    # Mock the API response with sample data
    mock_request_with_timeout.return_value = {
        "symbol": "AAPL",
        "latestUpdate": 1682468986000,
        "latestPrice": 150.25,
        "open": 149.00,
        "high": 151.50,
        "low": 148.00,
        "volume": 2000000,
    }

    # Initialize the poller and run the poll method
    poller = IEXPoller()
    poller.poll(["AAPL"])

    # Verify that the data is sent to the queue as expected
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


@patch("src.app.pollers.iex_poller.IEXPoller.send_to_queue")
@patch("src.app.utils.request_with_timeout")
def test_iex_poller_invalid_symbol(mock_request_with_timeout, mock_send_to_queue):
    """Test IEXPoller handles invalid symbols."""
    # Mock the API response with an error message
    mock_request_with_timeout.return_value = {"Error Message": "Invalid symbol"}

    # Initialize the poller and run the poll method
    poller = IEXPoller()
    poller.poll(["INVALID"])

    # Verify that no message is sent to the queue for invalid symbols
    mock_send_to_queue.assert_not_called()


@patch("src.app.pollers.iex_poller.IEXPoller.send_to_queue")
@patch("src.app.utils.request_with_timeout")
def test_iex_poller_empty_response(mock_request_with_timeout, mock_send_to_queue):
    """Test IEXPoller handles an empty API response."""
    # Mock the API response with an empty dictionary
    mock_request_with_timeout.return_value = {}

    # Initialize the poller and run the poll method
    poller = IEXPoller()
    poller.poll(["AAPL"])

    # Verify that no message is sent to the queue for an empty response
    mock_send_to_queue.assert_not_called()


@patch("src.app.pollers.iex_poller.IEXPoller.send_to_queue")
@patch("src.app.utils.request_with_timeout")
def test_iex_poller_timeout(mock_request_with_timeout, mock_send_to_queue):
    """Test IEXPoller handles API timeouts."""
    # Simulate a timeout exception
    mock_request_with_timeout.side_effect = Timeout("API request timed out.")

    # Initialize the poller and run the poll method
    poller = IEXPoller()
    poller.poll(["AAPL"])

    # Verify that no message is sent to the queue in case of a timeout
    mock_send_to_queue.assert_not_called()


@patch("src.app.pollers.iex_poller.IEXPoller.send_to_queue")
@patch("src.app.utils.request_with_timeout")
def test_iex_poller_missing_field(mock_request_with_timeout, mock_send_to_queue):
    """Test IEXPoller handles missing fields in the response."""
    # Mock the API response with missing fields
    mock_request_with_timeout.return_value = {
        "symbol": "AAPL",
        "latestUpdate": 1682468986000,
        "open": 149.00,
        "high": 151.50,
        "low": 148.00,
        "volume": 2000000,
    }

    # Initialize the poller and run the poll method
    poller = IEXPoller()
    poller.poll(["AAPL"])

    # Verify that no message is sent to the queue for missing fields
    mock_send_to_queue.assert_not_called()


@patch("src.app.pollers.iex_poller.IEXPoller.send_to_queue")
@patch("src.app.utils.request_with_timeout")
def test_iex_poller_invalid_data_format(mock_request_with_timeout, mock_send_to_queue):
    """Test IEXPoller handles unexpected data formats."""
    # Mock the API response with an invalid data format
    mock_request_with_timeout.return_value = "Invalid data format"

    # Initialize the poller and run the poll method
    poller = IEXPoller()
    poller.poll(["AAPL"])

    # Verify that no message is sent to the queue for invalid data formats
    mock_send_to_queue.assert_not_called()
