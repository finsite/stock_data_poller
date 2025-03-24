from unittest.mock import patch
from requests.exceptions import Timeout
from src.pollers.alphavantage_poller import AlphaVantagePoller


@patch("src.pollers.alphavantage_poller.AlphaVantagePoller.send_to_queue")
@patch("src.utils.request_with_timeout")
def test_alphavantage_poller_success(mock_request_with_timeout, mock_send_to_queue):
    """Test AlphaVantagePoller fetches and processes data successfully."""
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

    poller = AlphaVantagePoller()
    poller.poll(["AAPL"])

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
def test_alphavantage_poller_invalid_symbol(
    mock_request_with_timeout, mock_send_to_queue
):
    """Test AlphaVantagePoller handles invalid symbols."""
    mock_request_with_timeout.return_value = {"Error Message": "Invalid API call."}

    poller = AlphaVantagePoller()
    poller.poll(["INVALID"])

    mock_send_to_queue.assert_not_called()


@patch("src.pollers.alphavantage_poller.AlphaVantagePoller.send_to_queue")
@patch("src.utils.request_with_timeout")
def test_alphavantage_poller_timeout(mock_request_with_timeout, mock_send_to_queue):
    """Test AlphaVantagePoller handles API timeouts."""
    mock_request_with_timeout.side_effect = Timeout("API request timed out.")

    poller = AlphaVantagePoller()
    poller.poll(["AAPL"])

    mock_send_to_queue.assert_not_called()


@patch("src.pollers.alphavantage_poller.AlphaVantagePoller.send_to_queue")
@patch("src.utils.request_with_timeout")
def test_alphavantage_poller_network_error(
    mock_request_with_timeout, mock_send_to_queue
):
    """Test AlphaVantagePoller handles network errors."""
    mock_request_with_timeout.side_effect = Exception("Network error")

    poller = AlphaVantagePoller()
    poller.poll(["AAPL"])

    mock_send_to_queue.assert_not_called()


@patch("src.pollers.alphavantage_poller.AlphaVantagePoller.send_to_queue")
@patch("src.utils.request_with_timeout")
def test_alphavantage_poller_empty_data(mock_request_with_timeout, mock_send_to_queue):
    """Test AlphaVantagePoller handles empty data response."""
    mock_request_with_timeout.return_value = {"Time Series (5min)": {}}

    poller = AlphaVantagePoller()
    poller.poll(["AAPL"])

    mock_send_to_queue.assert_not_called()
