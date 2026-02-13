import json
from unittest.mock import patch, MagicMock
import pytest
from activator.main import publish_transcription_task


def test_publish_transcription_task_success(mock_pubsub_client):
    """Test successful message publishing"""
    with patch('google.cloud.pubsub_v1.PublisherClient',
               return_value=mock_pubsub_client):
        file_info = {
            'id': '123',
            'name': 'test.mp3',
            'type': 'audio',
            'folder_path': 'Test Folder'
        }
        result = publish_transcription_task(file_info)

        # Verify result
        assert result == 'message_id_123'

        # Verify the message was published correctly
        mock_pubsub_client.publish.assert_called_once()
        args = mock_pubsub_client.publish.call_args

        # Verify topic path
        assert mock_pubsub_client.topic_path.called
        assert 'transcription-tasks' in mock_pubsub_client.topic_path.call_args[0]

        # Verify message data
        published_data = json.loads(args[0][1]['data'].decode('utf-8'))
        assert published_data == file_info


def test_publish_transcription_task_error(mock_pubsub_client):
    """Test error handling during publishing"""
    # Mock publish error
    future = MagicMock()
    future.result.side_effect = Exception("Publish Error")
    mock_pubsub_client.publish.return_value = future

    with patch('google.cloud.pubsub_v1.PublisherClient',
               return_value=mock_pubsub_client):
        with pytest.raises(Exception) as exc_info:
            publish_transcription_task({'name': 'test.mp3'})
        assert "Publish Error" in str(exc_info.value)


def test_publish_transcription_task_invalid_json(mock_pubsub_client):
    """Test handling of non-JSON-serializable data"""
    with patch('google.cloud.pubsub_v1.PublisherClient',
               return_value=mock_pubsub_client):
        # Create a dict with non-serializable object
        file_info = {
            'name': 'test.mp3',
            'invalid': object()  # object() is not JSON serializable
        }

        with pytest.raises(TypeError):
            publish_transcription_task(file_info)


def test_publish_transcription_task_empty_data(mock_pubsub_client):
    """Test publishing with empty data"""
    with patch('google.cloud.pubsub_v1.PublisherClient',
               return_value=mock_pubsub_client):
        # Test with empty dict
        result = publish_transcription_task({})
        assert result == 'message_id_123'

        # Verify empty dict was properly serialized
        published_data = json.loads(
            mock_pubsub_client.publish.call_args[0][1]['data'].decode('utf-8'))
        assert published_data == {}
