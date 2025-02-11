from unittest.mock import patch
from app.pollers.yfinance_poller import YFinancePoller
from requests.exceptions import Timeout


@patch("yfinance.Ticker")
def test_yfinance_poller_success(mock_ticker, mock_queue_sender):
    """Test YFinancePoller fetches and processes data successfully."""
    mock_ticker.return_value.history.return_value = {
        "Open": [100],
        "High": [110],
        "Low": [95],
        "Close": [105],
        "Volume": [1000],
    }

    poller = YFinancePoller()
    poller.send_to_queue = mock_queue_sender.send_message

    poller.poll(["AAPL"])

    mock_queue_sender.send_message.assert_called_once()


@patch("yfinance.Ticker")
def test_yfinance_poller_invalid_symbol(mock_ticker, mock_queue_sender):
    """Test YFinancePoller handles invalid symbols."""
    mock_ticker.return_value.history.return_value = {}

    poller = YFinancePoller()
    poller.send_to_queue = mock_queue_sender.send_message

    poller.poll(["INVALID"])

    mock_queue_sender.send_message.assert_not_called()


@patch("yfinance.Ticker")
def test_yfinance_poller_timeout(mock_ticker, mock_queue_sender):
    """Test YFinancePoller handles API timeouts."""
    mock_ticker.side_effect = Timeout("API request timed out.")

    poller = YFinancePoller()
    poller.send_to_queue = mock_queue_sender.send_message

    poller.poll(["AAPL"])

    mock_queue_sender.send_message.assert_not_called()
