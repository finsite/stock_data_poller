"""Tests for FinnhubPoller.
"""

@patch("src.pollers.finnhub_poller.FinnhubPoller.send_to_queue")
@patch("src.utils.request_with_timeout")
def test_finnhub_poller_success(mock_request_with_timeout, mock_send_to_queue):
    """Test FinnhubPoller fetches and processes data successfully.
    """
    mock_request_with_timeout.return_value = {
        "c": 150.25,
        "h": 151.00,
        "l": 149.00,
        "o": 150.00,
        "pc": 149.50,
    }

    poller = FinnhubPoller()
    poller.poll(["AAPL"])

    mock_send_to_queue.assert_called_once_with(
        {
            "symbol": "AAPL",
            "timestamp": None,
            "price": 150.25,
            "source": "Finnhub",
            "data": {
                "current": 150.25,
                "high": 151.00,
                "low": 149.00,
                "open": 150.00,
                "previous_close": 149.50,
            },
        }
    )


@patch("src.pollers.finnhub_poller.FinnhubPoller.send_to_queue")
@patch("src.utils.request_with_timeout")
def test_finnhub_poller_invalid_symbol(mock_request_with_timeout, mock_send_to_queue):
    """Test FinnhubPoller handles invalid symbols.
    """
    mock_request_with_timeout.return_value = {"Error Message": "Invalid symbol"}

    poller = FinnhubPoller()
    poller.poll(["INVALID"])

    mock_send_to_queue.assert_not_called()


@patch("src.pollers.finnhub_poller.FinnhubPoller.send_to_queue")
@patch("src.utils.request_with_timeout")
def test_finnhub_poller_timeout(mock_request_with_timeout, mock_send_to_queue):
    """Test FinnhubPoller handles API timeouts.
    """
    mock_request_with_timeout.side_effect = Timeout("API request timed out.")

    poller = FinnhubPoller()
    poller.poll(["AAPL"])

    mock_send_to_queue.assert_not_called()


@patch("src.pollers.finnhub_poller.FinnhubPoller.send_to_queue")
@patch("src.utils.request_with_timeout")
def test_finnhub_poller_network_error(mock_request_with_timeout, mock_send_to_queue):
    """Test FinnhubPoller handles network errors.
    """
    mock_request_with_timeout.side_effect = Exception("Network error")

    poller = FinnhubPoller()
    poller.poll(["AAPL"])

    mock_send_to_queue.assert_not_called()


@patch("src.pollers.finnhub_poller.FinnhubPoller.send_to_queue")
@patch("src.utils.request_with_timeout")
def test_finnhub_poller_empty_data(mock_request_with_timeout, mock_send_to_queue):
    """Test FinnhubPoller handles empty data response.
    """
    mock_request_with_timeout.return_value = {}

    poller = FinnhubPoller()
    poller.poll(["AAPL"])

    mock_send_to_queue.assert_not_called()
