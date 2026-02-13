import os
from unittest.mock import patch, MagicMock
import pytest
from activator.main import scan_drive_folders


def test_scan_drive_folders_file_filtering(mock_drive_service, monkeypatch):
    """Test file filtering based on extensions"""
    # Mock build function to return our mock service
    with patch('googleapiclient.discovery.build', return_value=mock_drive_service):
        # Test with default extensions
        files = scan_drive_folders()

        # Should find one audio (mp3) and one video (mp4) file
        assert len(files) == 2
        assert any(f['name'] == 'test.mp3' and f['type']
                   == 'audio' for f in files)
        assert any(f['name'] == 'test.mp4' and f['type']
                   == 'video' for f in files)

        # Test with custom extensions
        monkeypatch.setenv('AUDIO_EXTENSIONS', 'wav')
        monkeypatch.setenv('VIDEO_EXTENSIONS', 'avi')

        # Should find no files with these extensions
        files = scan_drive_folders()
        assert len(files) == 0


def test_scan_drive_folders_debug_mode(mock_drive_service, capsys):
    """Test debug output"""
    # Mock build function to return our mock service
    with patch('googleapiclient.discovery.build', return_value=mock_drive_service):
        # Test without debug
        os.environ['DEBUG'] = 'False'
        scan_drive_folders()
        captured = capsys.readouterr()
        assert not captured.out  # No output without debug

        # Test with debug
        os.environ['DEBUG'] = 'True'
        scan_drive_folders()
        captured = capsys.readouterr()
        assert 'Found file: test.mp3' in captured.out
        assert 'Found file: test.mp4' in captured.out
        assert 'Total files found:' in captured.out


def test_scan_drive_folders_pagination(mock_drive_service):
    """Test handling of paginated results"""
    # Modify mock to return paginated results
    first_page = {
        'files': [
            {'id': '1', 'name': 'test1.mp3', 'parents': ['folder1']},
        ],
        'nextPageToken': 'token123'
    }
    second_page = {
        'files': [
            {'id': '2', 'name': 'test2.mp4', 'parents': ['folder1']},
        ]
    }

    mock_list = MagicMock()
    mock_list.execute.side_effect = [first_page, second_page]
    mock_drive_service.files.return_value.list.return_value = mock_list

    with patch('googleapiclient.discovery.build', return_value=mock_drive_service):
        files = scan_drive_folders()

        assert len(files) == 2
        assert any(f['name'] == 'test1.mp3' for f in files)
        assert any(f['name'] == 'test2.mp4' for f in files)

        # Verify pagination was handled
        calls = mock_drive_service.files.return_value.list.call_args_list
        assert len(calls) == 2
        assert calls[1][1]['pageToken'] == 'token123'


def test_scan_drive_folders_error_handling(mock_drive_service):
    """Test error handling during scanning"""
    # Mock service to raise an exception
    mock_drive_service.files.return_value.list.return_value.execute.side_effect = Exception(
        "API Error")

    with patch('googleapiclient.discovery.build', return_value=mock_drive_service):
        with pytest.raises(Exception) as exc_info:
            scan_drive_folders()
        assert "API Error" in str(exc_info.value)


def test_scan_drive_folders_empty_response(mock_drive_service):
    """Test handling of empty response from API"""
    # Mock empty response
    mock_drive_service.files.return_value.list.return_value.execute.return_value = {
        'files': []}

    with patch('googleapiclient.discovery.build', return_value=mock_drive_service):
        files = scan_drive_folders()
        assert len(files) == 0
