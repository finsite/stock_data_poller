from unittest.mock import patch

from requests.exceptions import Timeout

from src.pollers.quandl_poller import QuandlPoller


@patch("src.pollers.quandl_poller.QuandlPoller.send_to_queue")
@patch("src.utils.request_with_timeout")
def test_quandl_poller_success(mock_request_with_timeout, mock_send_to_queue):
    """Test QuandlPoller fetches and processes data successfully."""
    # Mocking a successful API response
    mock_request_with_timeout.return_value = {
        "dataset": {"data": [["2024-12-01", 150.0, 155.0, 149.0, 152.0, 1000]]}
    }

    poller = QuandlPoller()  # Instantiate the QuandlPoller
    poller.poll(["AAPL"])  # Poll for the symbol "AAPL"

    # Validate the message sent to the queue
    mock_send_to_queue.assert_called_once_with(
        {
            "symbol": "AAPL",
            "timestamp": "2024-12-01",
            "price": 152.0,
            "source": "Quandl",
            "data": {
                "open": 150.0,
                "high": 155.0,
                "low": 149.0,
                "close": 152.0,
                "volume": 1000,
            },
        }
    )


@patch("src.pollers.quandl_poller.QuandlPoller.send_to_queue")
@patch("src.utils.request_with_timeout")
def test_quandl_poller_invalid_symbol(mock_request_with_timeout, mock_send_to_queue):
    """Test QuandlPoller handles invalid symbols."""
    # Mocking an invalid symbol response
    mock_request_with_timeout.return_value = {
        "quandl_error": {"code": "QECx02", "message": "Unknown or unavailable dataset"}
    }

    poller = QuandlPoller()
    poller.poll(["INVALID"])  # Poll with an invalid symbol

    # Ensure no message is sent to the queue
    mock_send_to_queue.assert_not_called()


@patch("src.pollers.quandl_poller.QuandlPoller.send_to_queue")
@patch("src.utils.request_with_timeout")
def test_quandl_poller_empty_response(mock_request_with_timeout, mock_send_to_queue):
    """Test QuandlPoller handles an empty API response."""
    # Mocking an empty response
    mock_request_with_timeout.return_value = {}

    poller = QuandlPoller()
    poller.poll(["AAPL"])

    # Ensure no message is sent to the queue
    mock_send_to_queue.assert_not_called()


@patch("src.pollers.quandl_poller.QuandlPoller.send_to_queue")
@patch("src.utils.request_with_timeout")
def test_quandl_poller_timeout(mock_request_with_timeout, mock_send_to_queue):
    """Test QuandlPoller handles API timeouts."""
    # Simulate a timeout exception
    mock_request_with_timeout.side_effect = Timeout("Request timed out")

    poller = QuandlPoller()
    poller.poll(["AAPL"])

    # Ensure no message is sent due to timeout
    mock_send_to_queue.assert_not_called()


@patch("src.pollers.quandl_poller.QuandlPoller.send_to_queue")
@patch("src.utils.request_with_timeout")
def test_quandl_poller_missing_dataset(mock_request_with_timeout, mock_send_to_queue):
    """Test QuandlPoller handles missing dataset field in response."""
    # Mocking a response with missing dataset field
    mock_request_with_timeout.return_value = {"meta": {"info": "no dataset"}}

    poller = QuandlPoller()
    poller.poll(["AAPL"])

    # Ensure no message is sent due to missing field
    mock_send_to_queue.assert_not_called()


@patch("src.pollers.quandl_poller.QuandlPoller.send_to_queue")
@patch("src.utils.request_with_timeout")
def test_quandl_poller_invalid_data_format(mock_request_with_timeout, mock_send_to_queue):
    """Test QuandlPoller handles unexpected data format."""
    # Simulating an invalid data format response
    mock_request_with_timeout.return_value = "Unexpected response"

    poller = QuandlPoller()
    poller.poll(["AAPL"])

    # Ensure no message is sent due to invalid format
    mock_send_to_queue.assert_not_called()
