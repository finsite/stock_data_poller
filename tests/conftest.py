import pytest
from unittest.mock import MagicMock

@pytest.fixture
def mock_queue_sender():
    """Fixture to mock the QueueSender."""
    mock_sender = MagicMock()

    # Mocking the send_message method to return a mock response
    mock_sender.send_message.return_value = None  # Modify as needed (e.g., to return a fake message ID)
    
    # If you need to mock other methods like send_to_queue, add them here
    mock_sender.send_to_queue.return_value = None  # Modify as needed

    return mock_sender

