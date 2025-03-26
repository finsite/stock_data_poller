# from unittest.mock import patch
# from requests.exceptions import Timeout
# from src.pollers.polygon_poller import PolygonPoller


# @patch("src.utils.request_with_timeout")
# def test_polygon_poller_success(mock_request_with_timeout, mock_queue_sender):
#     """Test PolygonPoller fetches and processes data successfully."""
#     mock_request_with_timeout.return_value = {
#         "symbol": "AAPL",
#         "last": {
#             "price": 152.5,
#             "timestamp": 1682468986000,
#             "size": 100,
#             "exchange": 11,
#         },
#         "status": "success",
#     }

#     poller = PolygonPoller(api_key="fake_api_key")
#     poller.send_to_queue = mock_queue_sender.send_message

#     poller.poll(["AAPL"])

#     mock_queue_sender.send_message.assert_called_once_with(
#         {
#             "symbol": "AAPL",
#             "timestamp": 1682468986000,
#             "price": 152.5,
#             "source": "Polygon",
#             "data": {
#                 "size": 100,
#                 "exchange": 11,
#             },
#         }
#     )


# @patch("src.utils.request_with_timeout")
# def test_polygon_poller_invalid_symbol(mock_request_with_timeout, mock_queue_sender):
#     """Test PolygonPoller handles invalid symbols."""
#     mock_request_with_timeout.return_value = {
#         "status": "error",
#         "message": "Invalid symbol",
#     }

#     poller = PolygonPoller(api_key="fake_api_key")
#     poller.send_to_queue = mock_queue_sender.send_message

#     poller.poll(["INVALID"])

#     # Assert that send_message is not called for invalid symbol
#     mock_queue_sender.send_message.assert_not_called()


# @patch("src.utils.request_with_timeout")
# def test_polygon_poller_empty_response(mock_request_with_timeout, mock_queue_sender):
#     """Test PolygonPoller handles an empty API response."""
#     mock_request_with_timeout.return_value = {}

#     poller = PolygonPoller(api_key="fake_api_key")
#     poller.send_to_queue = mock_queue_sender.send_message

#     poller.poll(["AAPL"])

#     # Assert that send_message is not called when API response is empty
#     mock_queue_sender.send_message.assert_not_called()


# @patch("src.utils.request_with_timeout")
# def test_polygon_poller_timeout(mock_request_with_timeout, mock_queue_sender):
#     """Test PolygonPoller handles API timeouts."""
#     mock_request_with_timeout.side_effect = Timeout("API request timed out.")

#     poller = PolygonPoller(api_key="fake_api_key")
#     poller.send_to_queue = mock_queue_sender.send_message

#     poller.poll(["AAPL"])

#     # Assert that send_message is not called in case of timeout
#     mock_queue_sender.send_message.assert_not_called()


# @patch("src.utils.request_with_timeout")
# def test_polygon_poller_missing_field(mock_request_with_timeout, mock_queue_sender):
#     """Test PolygonPoller handles missing fields in the response."""
#     # Simulating a missing 'last' field
#     mock_request_with_timeout.return_value = {
#         "symbol": "AAPL",
#         "status": "success",
#     }

#     poller = PolygonPoller(api_key="fake_api_key")
#     poller.send_to_queue = mock_queue_sender.send_message

#     poller.poll(["AAPL"])

#     # Assert that send_message is not called because 'last' field is missing
#     mock_queue_sender.send_message.assert_not_called()


# @patch("src.utils.request_with_timeout")
# def test_polygon_poller_invalid_data_format(
#     mock_request_with_timeout, mock_queue_sender
# ):
#     """Test PolygonPoller handles unexpected data formats."""
#     # Simulating an invalid data format (string instead of dict)
#     mock_request_with_timeout.return_value = "Invalid data format"

#     poller = PolygonPoller(api_key="fake_api_key")
#     poller.send_to_queue = mock_queue_sender.send_message

#     poller.poll(["AAPL"])

#     # Assert that send_message is not called because of invalid format
#     mock_queue_sender.send_message.assert_not_called()
from unittest.mock import patch

from requests.exceptions import Timeout

from src.pollers.polygon_poller import PolygonPoller


@patch("src.pollers.polygon_poller.PolygonPoller.send_to_queue")
@patch("src.utils.request_with_timeout")
def test_polygon_poller_success(mock_request_with_timeout, mock_send_to_queue):
    """Test PolygonPoller fetches and processes data successfully."""
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

    poller = PolygonPoller()
    poller.poll(["AAPL"])

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


@patch("src.pollers.polygon_poller.PolygonPoller.send_to_queue")
@patch("src.utils.request_with_timeout")
def test_polygon_poller_invalid_symbol(mock_request_with_timeout, mock_send_to_queue):
    """Test PolygonPoller handles invalid symbols."""
    mock_request_with_timeout.return_value = {
        "status": "error",
        "message": "Invalid symbol",
    }

    poller = PolygonPoller()
    poller.poll(["INVALID"])

    mock_send_to_queue.assert_not_called()


@patch("src.pollers.polygon_poller.PolygonPoller.send_to_queue")
@patch("src.utils.request_with_timeout")
def test_polygon_poller_empty_response(mock_request_with_timeout, mock_send_to_queue):
    """Test PolygonPoller handles an empty API response."""
    mock_request_with_timeout.return_value = {}

    poller = PolygonPoller()
    poller.poll(["AAPL"])

    mock_send_to_queue.assert_not_called()


@patch("src.pollers.polygon_poller.PolygonPoller.send_to_queue")
@patch("src.utils.request_with_timeout")
def test_polygon_poller_timeout(mock_request_with_timeout, mock_send_to_queue):
    """Test PolygonPoller handles API timeouts."""
    mock_request_with_timeout.side_effect = Timeout("API request timed out.")

    poller = PolygonPoller()
    poller.poll(["AAPL"])

    mock_send_to_queue.assert_not_called()


@patch("src.pollers.polygon_poller.PolygonPoller.send_to_queue")
@patch("src.utils.request_with_timeout")
def test_polygon_poller_missing_field(mock_request_with_timeout, mock_send_to_queue):
    """Test PolygonPoller handles missing fields in the response."""
    mock_request_with_timeout.return_value = {
        "symbol": "AAPL",
        "status": "success",
    }

    poller = PolygonPoller()
    poller.poll(["AAPL"])

    mock_send_to_queue.assert_not_called()


@patch("src.pollers.polygon_poller.PolygonPoller.send_to_queue")
@patch("src.utils.request_with_timeout")
def test_polygon_poller_invalid_data_format(mock_request_with_timeout, mock_send_to_queue):
    """Test PolygonPoller handles unexpected data formats."""
    mock_request_with_timeout.return_value = "Invalid data format"

    poller = PolygonPoller()
    poller.poll(["AAPL"])

    mock_send_to_queue.assert_not_called()
