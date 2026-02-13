from abc import ABC, abstractmethod
from typing import Optional, Dict, Any


class StorageClient(ABC):
    """Abstract base class for storage clients."""

    def __init__(self, logger):
        """Initialize storage client.

        Args:
            logger: Logger instance to use
        """
        self.logger = logger

    @abstractmethod
    def file_exists(self, file_info: Dict[str, Any]) -> bool:
        """Check if a file exists.

        Args:
            file_info: Dictionary containing file information

        Returns:
            bool: True if file exists, False otherwise
        """
        pass

    @abstractmethod
    def download_file(self, file_info: Dict[str, Any], local_path: str) -> str:
        """Download a file to local storage.

        Args:
            file_info: Dictionary containing file information:
                - file_id: Optional ID of the file (may be null for local files)
                - file_name: Name of the file
                - file_path: URI-style path (e.g., file://, drive://, gs://)
                - shared_by: Who shared/owns the file
                - timestamp: When the operation was requested
                - operation: Type of operation (e.g., "konwersja")
            local_path: Where to save the file locally

        Returns:
            str: Path to the downloaded file

        Raises:
            Exception: If download fails
        """
        pass

    @abstractmethod
    def upload_text_file(self, file_info: Dict[str, Any], file_name: str, content: str) -> None:
        """Upload a text file.

        Args:
            file_info: Dictionary containing file information (same as download_file)
            file_name: Name of the file to create
            content: Text content to upload

        Raises:
            Exception: If upload fails
        """
        pass

    @abstractmethod
    def delete_file(self, file_info: Dict[str, Any], file_name: str) -> None:
        """Delete a file.

        Args:
            file_info: Dictionary containing file information (same as download_file)
            file_name: Name of the file to delete

        Raises:
            Exception: If deletion fails
        """
        pass

    @staticmethod
    def get_scheme() -> str:
        """Get the URI scheme this client handles (e.g., 'file', 'drive', 'gs').

        Returns:
            str: The URI scheme
        """
        pass

    @classmethod
    def can_handle(cls, file_info: Dict[str, Any]) -> bool:
        """Check if this client can handle the given file info.

        Args:
            file_info: Dictionary containing file information

        Returns:
            bool: True if this client can handle the file, False otherwise
        """
        if not file_info.get('file_path'):
            return False
        scheme = file_info['file_path'].split(
            '://')[0] if '://' in file_info['file_path'] else ''
        return scheme == cls.get_scheme()
