# Tests for PolygonPoller

from unittest.mock import patch

from requests.exceptions import Timeout

from src.app.pollers.polygon_poller import PolygonPoller


@patch("src.app.pollers.polygon_poller.PolygonPoller.send_to_queue")
@patch("src.app.utils.request_with_timeout")
def test_polygon_poller_success(mock_request_with_timeout, mock_send_to_queue):
    """Test PolygonPoller fetches and processes data successfully."""
    # Simulate a successful API response
    mock_request_with_timeout.return_value = {
        "symbol": "AAPL",
        "last": {
            "price": 152.5,
            "timestamp": 1682468986000,
            "size": 100,
            "exchange": 11,
        },
        "status": "success",
    }

    # Create a PolygonPoller instance
    poller = PolygonPoller()

    # Call the poll method with a valid symbol
    poller.poll(["AAPL"])

    # Assert that the send_to_queue method is called with the expected arguments
    mock_send_to_queue.assert_called_once_with(
        {
            "symbol": "AAPL",
            "timestamp": 1682468986000,
            "price": 152.5,
            "source": "Polygon",
            "data": {
                "size": 100,
                "exchange": 11,
            },
        }
    )


@patch("src.app.pollers.polygon_poller.PolygonPoller.send_to_queue")
@patch("src.app.utils.request_with_timeout")
def test_polygon_poller_invalid_symbol(mock_request_with_timeout, mock_send_to_queue):
    """Test PolygonPoller handles invalid symbols."""
    # Simulate an invalid symbol
    mock_request_with_timeout.return_value = {
        "status": "error",
        "message": "Invalid symbol",
    }

    # Create a PolygonPoller instance
    poller = PolygonPoller()

    # Call the poll method with an invalid symbol
    poller.poll(["INVALID"])

    # Assert that the send_to_queue method is not called
    mock_send_to_queue.assert_not_called()


@patch("src.app.pollers.polygon_poller.PolygonPoller.send_to_queue")
@patch("src.app.utils.request_with_timeout")
def test_polygon_poller_empty_response(mock_request_with_timeout, mock_send_to_queue):
    """Test PolygonPoller handles an empty API response."""
    # Simulate an empty API response
    mock_request_with_timeout.return_value = {}

    # Create a PolygonPoller instance
    poller = PolygonPoller()

    # Call the poll method with a valid symbol
    poller.poll(["AAPL"])

    # Assert that the send_to_queue method is not called
    mock_send_to_queue.assert_not_called()


@patch("src.app.pollers.polygon_poller.PolygonPoller.send_to_queue")
@patch("src.app.utils.request_with_timeout")
def test_polygon_poller_timeout(mock_request_with_timeout, mock_send_to_queue):
    """Test PolygonPoller handles API timeouts."""
    # Simulate an API timeout
    mock_request_with_timeout.side_effect = Timeout("API request timed out.")

    # Create a PolygonPoller instance
    poller = PolygonPoller()

    # Call the poll method with a valid symbol
    poller.poll(["AAPL"])

    # Assert that the send_to_queue method is not called
    mock_send_to_queue.assert_not_called()


@patch("src.app.pollers.polygon_poller.PolygonPoller.send_to_queue")
@patch("src.app.utils.request_with_timeout")
def test_polygon_poller_missing_field(mock_request_with_timeout, mock_send_to_queue):
    """Test PolygonPoller handles missing fields in the response."""
    # Simulate a missing 'last' field
    mock_request_with_timeout.return_value = {
        "symbol": "AAPL",
        "status": "success",
    }

    # Create a PolygonPoller instance
    poller = PolygonPoller()

    # Call the poll method with a valid symbol
    poller.poll(["AAPL"])

    # Assert that the send_to_queue method is not called
    mock_send_to_queue.assert_not_called()


@patch("src.app.pollers.polygon_poller.PolygonPoller.send_to_queue")
@patch("src.app.utils.request_with_timeout")
def test_polygon_poller_invalid_data_format(mock_request_with_timeout, mock_send_to_queue):
    """Test PolygonPoller handles unexpected data formats."""
    # Simulate an invalid data format
    mock_request_with_timeout.return_value = "Invalid data format"

    # Create a PolygonPoller instance
    poller = PolygonPoller()

    # Call the poll method with a valid symbol
    poller.poll(["AAPL"])

    # Assert that the send_to_queue method is not called
    mock_send_to_queue.assert_not_called()
