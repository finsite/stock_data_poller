from unittest.mock import patch
from requests.exceptions import Timeout
from src.pollers.alphavantage_poller import AlphaVantagePoller


@patch("src.pollers.alphavantage_poller.AlphaVantagePoller.send_to_queue")
@patch("src.utils.request_with_timeout")
def test_alphavantage_poller_success(mock_request_with_timeout, mock_send_to_queue):
    """Test AlphaVantagePoller fetches and processes data successfully."""
    # Mocking the API response with valid data
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

    # Initializing the poller and executing the poll method
    poller = AlphaVantagePoller()
    poller.poll(["AAPL"])

    # Verifying that the data is sent to the queue as expected
    mock_send_to_queue.assert_called_once_with(
        {
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
        }
    )


@patch("src.pollers.alphavantage_poller.AlphaVantagePoller.send_to_queue")
@patch("src.utils.request_with_timeout")
def test_alphavantage_poller_invalid_symbol(mock_request_with_timeout, mock_send_to_queue):
    """Test AlphaVantagePoller handles invalid symbols."""
    # Mocking the API response with an error message for invalid symbols
    mock_request_with_timeout.return_value = {"Error Message": "Invalid API call."}

    # Initializing the poller and executing the poll method
    poller = AlphaVantagePoller()
    poller.poll(["INVALID"])

    # Verifying that no data is sent to the queue
    mock_send_to_queue.assert_not_called()


@patch("src.pollers.alphavantage_poller.AlphaVantagePoller.send_to_queue")
@patch("src.utils.request_with_timeout")
def test_alphavantage_poller_timeout(mock_request_with_timeout, mock_send_to_queue):
    """Test AlphaVantagePoller handles API timeouts."""
    # Simulating a timeout exception for the API request
    mock_request_with_timeout.side_effect = Timeout("API request timed out.")

    # Initializing the poller and executing the poll method
    poller = AlphaVantagePoller()
    poller.poll(["AAPL"])

    # Verifying that no data is sent to the queue due to timeout
    mock_send_to_queue.assert_not_called()


@patch("src.pollers.alphavantage_poller.AlphaVantagePoller.send_to_queue")
@patch("src.utils.request_with_timeout")
def test_alphavantage_poller_network_error(mock_request_with_timeout, mock_send_to_queue):
    """Test AlphaVantagePoller handles network errors."""
    # Simulating a network error during the API request
    mock_request_with_timeout.side_effect = Exception("Network error")

    # Initializing the poller and executing the poll method
    poller = AlphaVantagePoller()
    poller.poll(["AAPL"])

    # Verifying that no data is sent to the queue due to network error
    mock_send_to_queue.assert_not_called()


@patch("src.pollers.alphavantage_poller.AlphaVantagePoller.send_to_queue")
@patch("src.utils.request_with_timeout")
def test_alphavantage_poller_empty_data(mock_request_with_timeout, mock_send_to_queue):
    """Test AlphaVantagePoller handles empty data response."""
    # Mocking the API response with empty data
    mock_request_with_timeout.return_value = {"Time Series (5min)": {}}

    # Initializing the poller and executing the poll method
    poller = AlphaVantagePoller()
    poller.poll(["AAPL"])

    # Verifying that no data is sent to the queue due to empty data
    mock_send_to_queue.assert_not_called()
