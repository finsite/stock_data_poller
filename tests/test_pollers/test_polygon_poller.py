from unittest.mock import patch
from app.pollers.polygon_poller import PolygonPoller
from requests.exceptions import Timeout


@patch("app.utils.request_with_timeout")
def test_polygon_poller_success(mock_request_with_timeout, mock_queue_sender):
    """Test PolygonPoller fetches and processes data successfully."""
    mock_request_with_timeout.return_value = {
        "symbol": "AAPL",
        "last": {"price": 152.5, "timestamp": 1682468986000, "size": 100, "exchange": 11},
        "status": "success",
    }

    poller = PolygonPoller(api_key="fake_api_key")
    poller.send_to_queue = mock_queue_sender.send_message

    poller.poll(["AAPL"])

    mock_queue_sender.send_message.assert_called_once_with({
        "symbol": "AAPL",
        "timestamp": 1682468986000,
        "price": 152.5,
        "source": "Polygon",
        "data": {
            "size": 100,
            "exchange": 11,
        },
    })


@patch("app.utils.request_with_timeout")
def test_polygon_poller_invalid_symbol(mock_request_with_timeout, mock_queue_sender):
    """Test PolygonPoller handles invalid symbols."""
    mock_request_with_timeout.return_value = {"status": "error", "message": "Invalid symbol"}

    poller = PolygonPoller(api_key="fake_api_key")
    poller.send_to_queue = mock_queue_sender.send_message

    poller.poll(["INVALID"])

    mock_queue_sender.send_message.assert_not_called()


@patch("app.utils.request_with_timeout")
def test_polygon_poller_empty_response(mock_request_with_timeout, mock_queue_sender):
    """Test PolygonPoller handles an empty API response."""
    mock_request_with_timeout.return_value = {}

    poller = PolygonPoller(api_key="fake_api_key")
    poller.send_to_queue = mock_queue_sender.send_message

    poller.poll(["AAPL"])

    mock_queue_sender.send_message.assert_not_called()


@patch("app.utils.request_with_timeout")
def test_polygon_poller_timeout(mock_request_with_timeout, mock_queue_sender):
    """Test PolygonPoller handles API timeouts."""
    mock_request_with_timeout.side_effect = Timeout("API request timed out.")

    poller = PolygonPoller(api_key="fake_api_key")
    poller.send_to_queue = mock_queue_sender.send_message

    poller.poll(["AAPL"])

    mock_queue_sender.send_message.assert_not_called()
