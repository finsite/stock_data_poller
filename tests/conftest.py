import pytest
from unittest.mock import MagicMock

@pytest.fixture
def mock_queue_sender():
    """Fixture to mock the QueueSender."""
    mock_sender = MagicMock()
    return mock_sender
