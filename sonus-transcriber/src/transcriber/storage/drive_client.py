import os
import io
from typing import Dict, Any, List
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
from ..config import GENERATED_EXTENSIONS, GENERATED_EXTENSIONS_TUPLE, get_extensions_with_dot
from .base_client import StorageClient


class DriveStorageClient(StorageClient):
    """Client for handling Google Drive operations."""

    def __init__(self, logger):
        super().__init__(logger)
        self._create_service()
        
        # Get supported extensions with dot prefix from config
        self.audio_extensions_with_dot, self.video_extensions_with_dot = get_extensions_with_dot()

    def _create_service(self) -> None:
        """Create a new Drive service instance."""
        self.service = build('drive', 'v3', cache_discovery=False)

    @staticmethod
    def get_scheme() -> str:
        return "drive"

    def check_files_status(self, file_info: Dict[str, Any]) -> Dict[str, bool]:
        """Check status of all related files in Google Drive.

        Args:
            file_info: Dictionary containing file information.

        Returns:
            dict: Dictionary with file status for source and generated files
        """
        try:
            folder_id = file_info['file_path'].replace('drive://', '')
            base_name = os.path.splitext(file_info['file_name'])[0]

            # Search for all files starting with base_name
            query = f"'{folder_id}' in parents and name contains '{base_name}' and trashed = false"
            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name)',
                supportsAllDrives=True,
                includeItemsFromAllDrives=True
            ).execute()

            # Get list of all files
            file_names = [file['name'] for file in results.get('files', [])]
            files_dict = {file['name']: file for file in results.get('files', [])}
            
            # Check generated files first
            found_extensions = []
            not_found_extensions = []
            
            # Check generated files
            for ext in GENERATED_EXTENSIONS:
                test_filename = f"{base_name}{ext}"
                if test_filename in file_names:
                    found_extensions.append(ext)
                else:
                    not_found_extensions.append(ext)
            
            # Check media files - only add to found_extensions if they exist
            for ext in self.audio_extensions_with_dot + self.video_extensions_with_dot:
                test_filename = f"{base_name}{ext}"
                if test_filename in file_names:
                    found_extensions.append(ext)
            
            # Log summary in a single line
            self.logger.debug(
                f"File {base_name}, found: {', '.join(found_extensions) if found_extensions else 'none'} not_found: {', '.join(not_found_extensions) if not_found_extensions else 'none'}")
            
            # Return status for each file type
            return {
                'source': any(file['id'] == file_info['file_id'] and file['name'] == file_info['file_name'] 
                            for file in results.get('files', [])) if not file_info['file_name'].endswith(GENERATED_EXTENSIONS_TUPLE) else False,
                'txt': f"{base_name}.txt" in file_names,
                'tmp': f"{base_name}.tmp" in file_names,
                'err': f"{base_name}.err" in file_names,
                'files': files_dict
            }

        except Exception as e:
            self.logger.error(
                f"Error checking files status: {str(e)}")
            return {
                'source': False,
                'txt': False,
                'tmp': False,
                'err': False,
                'files': {}
            }

    def file_exists(self, file_info: Dict[str, Any]) -> bool:
        """Check if a file exists in Google Drive.

        Args:
            file_info: Dictionary containing file information.
                      If file_id is provided, checks by ID.
                      Otherwise, searches by name in the folder.

        Returns:
            bool: True if file exists, False otherwise
        """
        try:
            folder_id = file_info['file_path'].replace('drive://', '')
            base_name = os.path.splitext(file_info['file_name'])[0]
            file_name = file_info['file_name']

            # Search for all files starting with base_name
            query = f"'{folder_id}' in parents and name = '{file_name}' and trashed = false"
            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name)',
                supportsAllDrives=True,
                includeItemsFromAllDrives=True
            ).execute()

            # For source file, check if it exists with correct ID and name
            if not file_name.endswith(GENERATED_EXTENSIONS_TUPLE):
                for file in results.get('files', []):
                    if file['id'] == file_info['file_id'] and file['name'] == file_name:
                        return True
                return False

            # For generated files, check if file with exact name exists
            return bool(results.get('files', []))

        except Exception as e:
            self.logger.error(
                f"Error checking file existence: {str(e)}")
            return False

    def download_file(self, file_info: Dict[str, Any], local_path: str) -> str:
        """Download a file from Google Drive to local storage."""
        try:
            # Ensure the target directory exists
            os.makedirs(os.path.dirname(local_path), exist_ok=True)

            # First check if file exists in correct folder
            if not self.file_exists(file_info):
                raise FileNotFoundError(
                    f"File {file_info['file_name']} not found in folder")

            # Use file_id from file_info
            request = self.service.files().get_media(
                fileId=file_info['file_id'])

            # Download the file
            fh = io.FileIO(local_path, 'wb')
            downloader = MediaIoBaseDownload(fh, request)
            done = False

            while done is False:
                status, done = downloader.next_chunk()
                if status:
                    self.logger.debug(
                        f"Download progress: {int(status.progress() * 100)}%")

            return local_path

        except Exception as e:
            error_msg = f"Error downloading file from Drive: {str(e)}"
            self.logger.error(error_msg)
            raise Exception(error_msg) from e

    def upload_text_file(self, file_info: Dict[str, Any], file_name: str, content: str) -> None:
        """Upload a text file to Google Drive with retries."""
        max_retries = 3
        retry_delay = 5  # seconds

        for attempt in range(max_retries):
            try:
                # Refresh service connection before upload
                if attempt > 0:
                    self.logger.debug(
                        f"Refreshing Drive service connection (attempt {attempt + 1})")
                    self._create_service()

                # Get folder ID from file_path (remove drive:// prefix)
                folder_id = file_info['file_path'].replace('drive://', '')

                file_metadata = {
                    'name': file_name,
                    'parents': [folder_id]
                }

                # Create file content in memory
                content_stream = io.BytesIO(content.encode('utf-8'))

                # Configure chunked upload
                media = MediaIoBaseUpload(
                    content_stream,
                    mimetype='text/plain',
                    resumable=True,
                    chunksize=1024*1024  # 1MB chunks
                )

                # Create the file upload request
                request = self.service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields='id'
                )

                # Upload the file in chunks
                response = None
                while response is None:
                    try:
                        status, response = request.next_chunk()
                        if status:
                            self.logger.debug(
                                f"Upload progress: {int(status.progress() * 100)}%")
                    except Exception as e:
                        if attempt == max_retries - 1:  # Last attempt
                            raise
                        self.logger.warning(
                            f"Chunk upload failed: {str(e)}")
                        import time
                        time.sleep(retry_delay)
                        break  # Break inner loop to retry with new service connection

                if response:  # Upload completed successfully
                    self.logger.debug(
                        f"File {file_name} uploaded to Google Drive with ID: {response.get('id')}")
                    return

            except Exception as e:
                if attempt == max_retries - 1:  # Last attempt
                    self.logger.error(
                        f"Error uploading file to Drive: {str(e)}")
                    raise
                self.logger.warning(
                    f"Upload attempt {attempt + 1} failed: {str(e)}")
                import time
                time.sleep(retry_delay)

    def delete_file(self, file_info: Dict[str, Any], file_name: str) -> None:
        """Delete a file from Google Drive."""
        try:
            # Get folder ID from file_path (remove drive:// prefix)
            folder_id = file_info['file_path'].replace('drive://', '')

            # Find file by name in the folder
            response = self.service.files().list(
                q=f"name = '{file_name}' and '{folder_id}' in parents and trashed = false",
                spaces='drive',
                fields='files(id, name)'
            ).execute()

            files = response.get('files', [])
            if files:
                # Delete the file
                self.service.files().delete(
                    fileId=files[0]['id']
                ).execute()

        except Exception as e:
            error_msg = f"Error deleting file from Drive: {str(e)}"
            self.logger.error(error_msg)
            raise Exception(error_msg) from e
