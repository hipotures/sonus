import os
import shutil
from typing import Dict, Any
from .base_client import StorageClient


class LocalStorageClient(StorageClient):
    """Client for handling local file system operations."""

    @staticmethod
    def get_scheme() -> str:
        return "file"

    def file_exists(self, file_info: Dict[str, Any]) -> bool:
        """Check if a file exists in local storage.

        Args:
            file_info: Dictionary containing file information

        Returns:
            bool: True if file exists, False otherwise
        """
        try:
            file_path = file_info['file_path'].replace('file://', '')
            full_path = os.path.join(file_path, file_info['file_name'])
            return os.path.exists(full_path)
        except Exception as e:
            self.logger.debug(
                f"Error checking file existence: {str(e)}")
            return False

    def _get_full_path(self, file_info: Dict[str, Any]) -> str:
        """Get full local path from file info.

        Args:
            file_info: Dictionary containing file information

        Returns:
            str: Full local path
        """
        # Remove 'file://' prefix and join with filename
        base_path = file_info['file_path'].replace('file://', '')
        return os.path.join(base_path, file_info['file_name'])

    def download_file(self, file_info: Dict[str, Any], local_path: str) -> str:
        """For local files, just return the path or copy if needed."""
        try:
            src_path = self._get_full_path(file_info)

            # If source and destination are the same, just return the path
            if os.path.abspath(src_path) == os.path.abspath(local_path):
                return local_path

            # Otherwise, copy the file
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            shutil.copy2(src_path, local_path)
            self.logger.debug(f"Copied {src_path} to {local_path}")
            return local_path

        except Exception as e:
            self.logger.error(f"Error accessing local file: {str(e)}")
            raise

    def upload_text_file(self, file_info: Dict[str, Any], file_name: str, content: str) -> None:
        """Save text file to local filesystem."""
        try:
            # Get directory path from file_info
            dir_path = file_info['file_path'].replace('file://', '')
            os.makedirs(dir_path, exist_ok=True)

            # Create full path and save file
            full_path = os.path.join(dir_path, file_name)
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.logger.debug(f"Saved text file to {full_path}")

        except Exception as e:
            self.logger.error(f"Error saving local file: {str(e)}")
            raise

    def delete_file(self, file_info: Dict[str, Any], file_name: str) -> None:
        """Delete local file."""
        try:
            full_path = os.path.join(
                file_info['file_path'].replace('file://', ''),
                file_name
            )
            if os.path.exists(full_path):
                os.remove(full_path)
                self.logger.debug(f"Deleted file {full_path}")
            else:
                self.logger.warning(f"File not found: {full_path}")

        except Exception as e:
            self.logger.error(f"Error deleting local file: {str(e)}")
            raise
