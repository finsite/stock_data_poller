from unittest.mock import patch
from app.pollers.alphavantage_poller import AlphaVantagePoller
from requests.exceptions import Timeout


@patch("app.utils.request_with_timeout")
def test_alphavantage_poller_success(mock_request_with_timeout, mock_queue_sender):
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

    poller = AlphaVantagePoller(api_key="fake_api_key")
    poller.send_to_queue = mock_queue_sender.send_message

    poller.poll(["AAPL"])

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


@patch("app.utils.request_with_timeout")
def test_alphavantage_poller_invalid_symbol(mock_request_with_timeout, mock_queue_sender):
    """Test AlphaVantagePoller handles invalid symbols."""
    mock_request_with_timeout.return_value = {"Error Message": "Invalid API call."}

    poller = AlphaVantagePoller(api_key="fake_api_key")
    poller.send_to_queue = mock_queue_sender.send_message

    poller.poll(["INVALID"])

    mock_queue_sender.send_message.assert_not_called()


@patch("app.utils.request_with_timeout")
def test_alphavantage_poller_timeout(mock_request_with_timeout, mock_queue_sender):
    """Test AlphaVantagePoller handles API timeouts."""
    mock_request_with_timeout.side_effect = Timeout("API request timed out.")

    poller = AlphaVantagePoller(api_key="fake_api_key")
    poller.send_to_queue = mock_queue_sender.send_message

    poller.poll(["AAPL"])

    mock_queue_sender.send_message.assert_not_called()
