from unittest.mock import patch, MagicMock
import pytest
from activator.main import get_folder_path


def test_get_folder_path_single_level(mock_drive_service):
    """Test path building for single level folder structure"""
    with patch('googleapiclient.discovery.build', return_value=mock_drive_service):
        # Test root level folder
        path = get_folder_path(mock_drive_service, ['folder1'])
        assert path == 'Test Folder'


def test_get_folder_path_nested(mock_drive_service):
    """Test path building for nested folders"""
    # Mock nested folder structure
    responses = {
        'folder1': {
            'id': 'folder1',
            'name': 'Level 1',
            'parents': ['folder2']
        },
        'folder2': {
            'id': 'folder2',
            'name': 'Level 2',
            'parents': ['folder3']
        },
        'folder3': {
            'id': 'folder3',
            'name': 'Level 3',
            'parents': []
        }
    }

    def mock_get_execute(file_id):
        return responses[file_id]

    mock_drive_service.files.return_value.get.return_value.execute.side_effect = mock_get_execute

    with patch('googleapiclient.discovery.build', return_value=mock_drive_service):
        path = get_folder_path(mock_drive_service, ['folder1'])
        assert path == 'Level 3/Level 2/Level 1'


def test_get_folder_path_no_parents():
    """Test path building when no parent IDs are provided"""
    mock_service = MagicMock()
    path = get_folder_path(mock_service, [])
    assert path == ""
    # Verify that no API calls were made
    mock_service.files.return_value.get.assert_not_called()


def test_get_folder_path_error_handling(mock_drive_service):
    """Test error handling in path building"""
    # Mock API error
    mock_drive_service.files.return_value.get.return_value.execute.side_effect = Exception(
        "API Error")

    with patch('googleapiclient.discovery.build', return_value=mock_drive_service):
        # Should return empty path on error
        path = get_folder_path(mock_drive_service, ['folder1'])
        assert path == ""


def test_get_folder_path_missing_parent(mock_drive_service):
    """Test handling of folders with missing parent information"""
    # Mock folder without parents field
    mock_drive_service.files.return_value.get.return_value.execute.return_value = {
        'id': 'folder1',
        'name': 'Test Folder'
        # No parents field
    }

    with patch('googleapiclient.discovery.build', return_value=mock_drive_service):
        path = get_folder_path(mock_drive_service, ['folder1'])
        assert path == "Test Folder"  # Should still return folder name
