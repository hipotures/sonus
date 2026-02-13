from typing import Dict, Any, Type
from .base_client import StorageClient
from .local_client import LocalStorageClient
from .drive_client import DriveStorageClient


class StorageClientFactory:
    """Factory for creating storage clients based on URI scheme."""

    _clients: Dict[str, Type[StorageClient]] = {
        "file": LocalStorageClient,
        "drive": DriveStorageClient,
        # Future: Add more clients here
        # "gs": GCSStorageClient,
        # "s3": S3StorageClient,
    }

    @classmethod
    def create_client(cls, file_info: Dict[str, Any], logger) -> StorageClient:
        """Create appropriate storage client for given file info.

        Args:
            file_info: Dictionary containing file information
            logger: Logger instance to use

        Returns:
            StorageClient: Appropriate storage client instance

        Raises:
            ValueError: If no client can handle the given file info
        """
        if not file_info.get('file_path'):
            raise ValueError("file_path is required in file_info")

        # Extract scheme from file_path
        scheme = file_info['file_path'].split(
            '://')[0] if '://' in file_info['file_path'] else ''

        # Find client that can handle this scheme
        for client_class in cls._clients.values():
            if client_class.get_scheme() == scheme:
                return client_class(logger)

        raise ValueError(f"No storage client available for scheme: {scheme}")

    @classmethod
    def register_client(cls, client_class: Type[StorageClient]) -> None:
        """Register a new storage client class.

        Args:
            client_class: Storage client class to register
        """
        scheme = client_class.get_scheme()
        cls._clients[scheme] = client_class
