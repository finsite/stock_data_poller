# Tests for the YFinancePoller class
from unittest.mock import patch

from src.pollers.yfinance_poller import YFinancePoller


@patch("src.pollers.yfinance_poller.YFinancePoller.send_to_queue")
@patch("yfinance.Ticker")
def test_yfinance_poller_success(mock_ticker, mock_send_to_queue):
    """Test YFinancePoller fetches and processes data successfully."""
    mock_data = {
        "Open": 150.0,
        "High": 155.0,
        "Low": 149.0,
        "Close": 152.0,
        "Volume": 1000,
    }

    # Mimic latest row with .name for timestamp
    mock_history = type(
        "MockHistory",
        (),
        {
            "iloc": [
                type(
                    "LatestRow",
                    (),
                    {
                        "name": "2024-12-01",
                        "__getitem__": lambda self, key: mock_data[key],
                    },
                )
            ]
        },
    )

    mock_ticker.return_value.history.return_value = mock_history

    poller = YFinancePoller()
    poller.poll(["AAPL"])

    mock_send_to_queue.assert_called_once_with(
        {
            "symbol": "AAPL",
            "timestamp": "2024-12-01",
            "price": 152.0,
            "source": "YFinance",
            "data": {
                "open": 150.0,
                "high": 155.0,
                "low": 149.0,
                "close": 152.0,
                "volume": 1000,
            },
        }
    )


@patch("src.pollers.yfinance_poller.YFinancePoller.send_to_queue")
@patch("yfinance.Ticker")
def test_yfinance_poller_empty_data(mock_ticker, mock_send_to_queue):
    """Test YFinancePoller handles empty history data."""
    mock_ticker.return_value.history.return_value = []

    poller = YFinancePoller()
    poller.poll(["AAPL"])

    # Assert that send_message is not called when the response is empty
    mock_send_to_queue.assert_not_called()


@patch("src.pollers.yfinance_poller.YFinancePoller.send_to_queue")
@patch("yfinance.Ticker")
def test_yfinance_poller_exception(mock_ticker, mock_send_to_queue):
    """Test YFinancePoller handles unexpected errors."""
    mock_ticker.side_effect = Exception("Unexpected error")

    poller = YFinancePoller()
    poller.poll(["AAPL"])

    # Assert that send_message is not called in case of an exception
    mock_send_to_queue.assert_not_called()


@patch("src.pollers.yfinance_poller.YFinancePoller.send_to_queue")
@patch("yfinance.Ticker")
def test_yfinance_poller_invalid_symbol(mock_ticker, mock_send_to_queue):
    """Test YFinancePoller handles invalid symbols with empty data."""

    class MockHistory:
        def __bool__(self):
            return False  # Simulate empty DataFrame

    mock_ticker.return_value.history.return_value = MockHistory()

    poller = YFinancePoller()
    poller.poll(["INVALID"])

    # Assert that send_message is not called for an invalid symbol
    mock_send_to_queue.assert_not_called()

