import pytest
from unittest.mock import MagicMock


@pytest.fixture
def mock_drive_service():
    """Mock for Google Drive service"""
    mock_service = MagicMock()

    # Mock files().list() method
    mock_list = MagicMock()
    mock_list.execute.return_value = {
        'files': [
            {'id': '1', 'name': 'test.mp3', 'parents': ['folder1']},
            {'id': '2', 'name': 'test.mp4', 'parents': ['folder1']},
            {'id': '3', 'name': 'test.txt', 'parents': ['folder1']},
        ]
    }
    mock_service.files.return_value.list.return_value = mock_list

    # Mock files().get() method
    mock_get = MagicMock()
    mock_get.execute.return_value = {
        'id': 'folder1',
        'name': 'Test Folder',
        'parents': []
    }
    mock_service.files.return_value.get.return_value = mock_get

    return mock_service


@pytest.fixture
def mock_pubsub_client():
    """Mock for Pub/Sub client"""
    mock_client = MagicMock()

    # Mock topic_path method
    mock_client.topic_path.return_value = 'projects/example-project-id/topics/transcription-tasks'

    # Mock publish method
    future = MagicMock()
    future.result.return_value = 'message_id_123'
    mock_client.publish.return_value = future

    return mock_client


@pytest.fixture
def mock_credentials():
    """Mock for Google credentials"""
    mock_creds = MagicMock()
    mock_creds.default.return_value = MagicMock()
    return mock_creds
