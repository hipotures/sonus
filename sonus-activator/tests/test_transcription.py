from unittest.mock import patch, MagicMock
import pytest
from activator.main import needs_transcription


def test_needs_transcription_no_existing(mock_drive_service):
    """Test when no transcription file exists"""
    # Mock empty response (no transcription file found)
    mock_drive_service.files.return_value.list.return_value.execute.return_value = {
        'files': []
    }

    with patch('googleapiclient.discovery.build', return_value=mock_drive_service):
        file_info = {
            'name': 'test.mp3',
            'folder_path': 'Test Folder'
        }
        assert needs_transcription(file_info) is True


def test_needs_transcription_existing(mock_drive_service):
    """Test when transcription file exists"""
    # Mock response with existing transcription file
    mock_drive_service.files.return_value.list.return_value.execute.return_value = {
        'files': [
            {'id': '1', 'name': 'test.mp3.txt'}
        ]
    }

    with patch('googleapiclient.discovery.build', return_value=mock_drive_service):
        file_info = {
            'name': 'test.mp3',
            'folder_path': 'Test Folder'
        }
        assert needs_transcription(file_info) is False


def test_needs_transcription_api_error(mock_drive_service):
    """Test error handling during transcription check"""
    # Mock API error
    mock_drive_service.files.return_value.list.return_value.execute.side_effect = Exception(
        "API Error")

    with patch('googleapiclient.discovery.build', return_value=mock_drive_service):
        file_info = {
            'name': 'test.mp3',
            'folder_path': 'Test Folder'
        }
        # Should return True when error occurs (assume transcription needed)
        assert needs_transcription(file_info) is True


def test_needs_transcription_special_characters(mock_drive_service):
    """Test handling of filenames with special characters"""
    mock_drive_service.files.return_value.list.return_value.execute.return_value = {
        'files': []
    }

    with patch('googleapiclient.discovery.build', return_value=mock_drive_service):
        file_info = {
            'name': 'test file (2024) [HD].mp3',
            'folder_path': 'Test Folder'
        }
        assert needs_transcription(file_info) is True

        # Verify the query was properly escaped
        query = mock_drive_service.files.return_value.list.call_args[1]['q']
        assert "name = 'test file (2024) [HD].mp3.txt'" in query


def test_needs_transcription_empty_filename(mock_drive_service):
    """Test handling of empty or invalid filenames"""
    with patch('googleapiclient.discovery.build', return_value=mock_drive_service):
        file_info = {
            'name': '',
            'folder_path': 'Test Folder'
        }
        # Should handle empty filename gracefully
        assert needs_transcription(file_info) is True

        file_info = {
            'folder_path': 'Test Folder'
            # Missing name field
        }
        # Should handle missing filename gracefully
        assert needs_transcription(file_info) is True
