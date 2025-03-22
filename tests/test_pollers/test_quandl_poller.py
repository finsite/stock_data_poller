# from unittest.mock import patch
# from requests.exceptions import Timeout
# from src.pollers.quandl_poller import QuandlPoller


# @patch("src.utils.request_with_timeout")
# def test_quandl_poller_success(mock_request_with_timeout, mock_queue_sender):
#     """Test QuandlPoller fetches and processes data successfully."""
#     mock_request_with_timeout.return_value = {
#         "dataset": {
#             "dataset_code": "AAPL",
#             "data": [["2024-12-01", 150, 155, 145, 152, 1000]],
#         }
#     }

#     poller = QuandlPoller(api_key="fake_api_key")
#     poller.send_to_queue = mock_queue_sender.send_message

#     poller.poll(["AAPL"])

#     mock_queue_sender.send_message.assert_called_once_with(
#         {
#             "symbol": "AAPL",
#             "timestamp": "2024-12-01",
#             "price": 152.00,
#             "source": "Quandl",
#             "data": {
#                 "open": 150.00,
#                 "high": 155.00,
#                 "low": 145.00,
#                 "close": 152.00,
#                 "volume": 1000,
#             },
#         }
#     )


# @patch("src.utils.request_with_timeout")
# def test_quandl_poller_invalid_symbol(mock_request_with_timeout, mock_queue_sender):
#     """Test QuandlPoller handles invalid symbols."""
#     mock_request_with_timeout.return_value = {"Error Message": "Invalid symbol"}

#     poller = QuandlPoller(api_key="fake_api_key")
#     poller.send_to_queue = mock_queue_sender.send_message

#     poller.poll(["INVALID"])

#     mock_queue_sender.send_message.assert_not_called()


# @patch("src.utils.request_with_timeout")
# def test_quandl_poller_timeout(mock_request_with_timeout, mock_queue_sender):
#     """Test QuandlPoller handles API timeouts."""
#     mock_request_with_timeout.side_effect = Timeout("API request timed out.")

#     poller = QuandlPoller(api_key="fake_api_key")
#     poller.send_to_queue = mock_queue_sender.send_message

#     poller.poll(["AAPL"])

#     mock_queue_sender.send_message.assert_not_called()


# @patch("src.utils.request_with_timeout")
# def test_quandl_poller_empty_response(mock_request_with_timeout, mock_queue_sender):
#     """Test QuandlPoller handles an empty API response."""
#     mock_request_with_timeout.return_value = {}

#     poller = QuandlPoller(api_key="fake_api_key")
#     poller.send_to_queue = mock_queue_sender.send_message

#     poller.poll(["AAPL"])

#     mock_queue_sender.send_message.assert_not_called()


# @patch("src.utils.request_with_timeout")
# def test_quandl_poller_missing_field(mock_request_with_timeout, mock_queue_sender):
#     """Test QuandlPoller handles missing fields in the response."""
#     # Simulating missing 'data' field
#     mock_request_with_timeout.return_value = {
#         "dataset": {
#             "dataset_code": "AAPL",
#         }
#     }

#     poller = QuandlPoller(api_key="fake_api_key")
#     poller.send_to_queue = mock_queue_sender.send_message

#     poller.poll(["AAPL"])

#     mock_queue_sender.send_message.assert_not_called()


# @patch("src.utils.request_with_timeout")
# def test_quandl_poller_invalid_data_format(
#     mock_request_with_timeout, mock_queue_sender
# ):
#     """Test QuandlPoller handles invalid data format in the response."""
#     # Simulating invalid data format (string instead of a list of lists)
#     mock_request_with_timeout.return_value = {
#         "dataset": {"dataset_code": "AAPL", "data": "Invalid data format"}
#     }

#     poller = QuandlPoller(api_key="fake_api_key")
#     poller.send_to_queue = mock_queue_sender.send_message

#     poller.poll(["AAPL"])

#     mock_queue_sender.send_message.assert_not_called()
from unittest.mock import patch
from requests.exceptions import Timeout
from src.pollers.quandl_poller import QuandlPoller


@patch("src.pollers.quandl_poller.QuandlPoller.send_to_queue")
@patch("src.utils.request_with_timeout")
def test_quandl_poller_success(mock_request_with_timeout, mock_send_to_queue):
    """Test QuandlPoller fetches and processes data successfully."""
    mock_request_with_timeout.return_value = {
        "dataset": {
            "data": [
                ["2024-12-01", 150.0, 155.0, 149.0, 152.0, 1000]
            ]
        }
    }

    poller = QuandlPoller()
    poller.poll(["AAPL"])

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
    mock_request_with_timeout.return_value = {
        "quandl_error": {"code": "QECx02", "message": "Unknown or unavailable dataset"}
    }

    poller = QuandlPoller()
    poller.poll(["INVALID"])

    mock_send_to_queue.assert_not_called()


@patch("src.pollers.quandl_poller.QuandlPoller.send_to_queue")
@patch("src.utils.request_with_timeout")
def test_quandl_poller_empty_response(mock_request_with_timeout, mock_send_to_queue):
    """Test QuandlPoller handles an empty API response."""
    mock_request_with_timeout.return_value = {}

    poller = QuandlPoller()
    poller.poll(["AAPL"])

    mock_send_to_queue.assert_not_called()


@patch("src.pollers.quandl_poller.QuandlPoller.send_to_queue")
@patch("src.utils.request_with_timeout")
def test_quandl_poller_timeout(mock_request_with_timeout, mock_send_to_queue):
    """Test QuandlPoller handles API timeouts."""
    mock_request_with_timeout.side_effect = Timeout("Request timed out")

    poller = QuandlPoller()
    poller.poll(["AAPL"])

    mock_send_to_queue.assert_not_called()


@patch("src.pollers.quandl_poller.QuandlPoller.send_to_queue")
@patch("src.utils.request_with_timeout")
def test_quandl_poller_missing_dataset(mock_request_with_timeout, mock_send_to_queue):
    """Test QuandlPoller handles missing dataset field in response."""
    mock_request_with_timeout.return_value = {
        "meta": {"info": "no dataset"}
    }

    poller = QuandlPoller()
    poller.poll(["AAPL"])

    mock_send_to_queue.assert_not_called()


@patch("src.pollers.quandl_poller.QuandlPoller.send_to_queue")
@patch("src.utils.request_with_timeout")
def test_quandl_poller_invalid_data_format(mock_request_with_timeout, mock_send_to_queue):
    """Test QuandlPoller handles unexpected data format."""
    mock_request_with_timeout.return_value = "Unexpected response"

    poller = QuandlPoller()
    poller.poll(["AAPL"])

    mock_send_to_queue.assert_not_called()
