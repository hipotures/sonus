"""Module for processing audio/video files for transcription."""
import os
import json
import time
import subprocess
import logging
from ..config import WORK_DIR, GENERATED_EXTENSIONS_TUPLE
from ..storage import StorageClientFactory
from ..storage.drive_client import DriveStorageClient
from ..whisperx_transcriber import WhisperXTranscriber

logger = logging.getLogger('transcriber')

class FileProcessor:
    """Processor for audio/video file transcription."""
    
    def __init__(self):
        """Initialize the file processor."""
        pass
    
    def process(self, file_info):
        """Process a file for transcription.
        
        Args:
            file_info: Dictionary containing file information
            
        Returns:
            dict: The transcription result or None if processing was skipped
        """
        # Create appropriate storage client
        storage_client = StorageClientFactory.create_client(file_info, logger)
        
        # Set up local path for temporary processing
        os.makedirs(WORK_DIR, exist_ok=True)
        local_path = os.path.join(WORK_DIR, file_info['file_name'])
        
        try:
            # Check file status
            if not self._check_file_status(file_info, storage_client):
                # File cannot be processed (doesn't exist, already processed, etc.)
                return None
            
            # Get base filename for status files
            base_filename = os.path.splitext(file_info['file_name'])[0]
            
            # Create .tmp file to indicate processing
            tmp_content = f"Transcription in progress, started at {time.strftime('%Y%m%d %H%M%S')}"
            storage_client.upload_text_file(
                file_info, f"{base_filename}.tmp", tmp_content)
            
            # Download file
            try:
                local_path = storage_client.download_file(file_info, local_path)
            except Exception as e:
                error_message = f"Error accessing file: {str(e)}"
                storage_client.upload_text_file(
                    file_info, f"{base_filename}.err", error_message)
                logger.error(error_message)
                return None
                
            # Get file metadata
            file_metadata = self._extract_file_metadata(local_path)
            
            # Initialize WhisperX transcriber
            transcriber = WhisperXTranscriber(logger)
            transcriber.duration = file_metadata.get('duration')
            transcriber.file_size_mib = file_metadata.get('file_size_mib')
            
            # Perform transcription
            result = transcriber.transcribe(
                local_path, file_info['file_name'])
            
            # Save transcription files
            storage_client.upload_text_file(
                file_info, f"{base_filename}.txt", result['text'])
            storage_client.upload_text_file(
                file_info, f"{base_filename}.json",
                json.dumps(result['json'], indent=2, ensure_ascii=False))
            
            # Delete .tmp file
            storage_client.delete_file(file_info, f"{base_filename}.tmp")
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing file: {str(e)}")
            # Try to clean up temp file if it exists
            try:
                base_filename = os.path.splitext(file_info['file_name'])[0]
                error_message = f"Processing error: {str(e)}"
                storage_client.upload_text_file(
                    file_info, f"{base_filename}.err", error_message)
                storage_client.delete_file(file_info, f"{base_filename}.tmp")
            except:
                pass
            raise
    
    def _check_file_status(self, file_info, storage_client):
        """Check if file can be processed.
        
        Args:
            file_info: Dictionary containing file information
            storage_client: Storage client for the file
            
        Returns:
            bool: True if file can be processed, False otherwise
        """
        base_filename = os.path.splitext(file_info['file_name'])[0]
        
        # For Google Drive, check all files status at once
        if isinstance(storage_client, DriveStorageClient):
            files_status = storage_client.check_files_status(file_info)
            
            # Check if source file exists
            if not files_status['source']:
                error_message = f"File not found: {file_info['file_name']}"
                storage_client.upload_text_file(
                    file_info, f"{base_filename}.err", error_message)
                logger.error(error_message)
                return False
            
            # Check if transcription already exists
            if files_status['txt']:
                logger.debug(
                    f"Found existing transcription for {file_info['file_name']}. Skipping processing.")
                return False
            
            # Check if file is being processed
            if files_status['tmp']:
                logger.debug(
                    f"File {file_info['file_name']} is currently being processed. Skipping processing.")
                return False
            
            # Check if there was an error
            if files_status['err']:
                logger.debug(
                    f"Found error file for {file_info['file_name']}. Skipping processing.")
                return False
                
            return True
        else:
            # For other storage types, check files one by one
            # Check if source file exists
            if not storage_client.file_exists(file_info):
                error_message = f"File not found: {file_info['file_name']}"
                storage_client.upload_text_file(
                    file_info, f"{base_filename}.err", error_message)
                logger.error(error_message)
                return False
            
            # Check if transcription already exists
            txt_file_info = {**file_info, 'file_name': f"{base_filename}.txt"}
            if storage_client.file_exists(txt_file_info):
                logger.debug(
                    f"Found existing transcription for {file_info['file_name']}. Skipping processing.")
                return False
            
            # Check if file is being processed
            tmp_file_info = {**file_info, 'file_name': f"{base_filename}.tmp"}
            if storage_client.file_exists(tmp_file_info):
                logger.debug(
                    f"File {file_info['file_name']} is currently being processed. Skipping processing.")
                return False
            
            # Check if there was an error
            err_file_info = {**file_info, 'file_name': f"{base_filename}.err"}
            if storage_client.file_exists(err_file_info):
                logger.debug(
                    f"Found error file for {file_info['file_name']}. Skipping processing.")
                return False
            
            return True
    
    def _extract_file_metadata(self, file_path):
        """Extract metadata from audio/video file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            dict: Dictionary with file metadata
        """
        metadata = {}
        
        try:
            # Get duration using ffprobe
            duration_result = subprocess.run([
                'ffprobe',
                '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                file_path
            ], capture_output=True, text=True)
            
            metadata['duration'] = round(float(duration_result.stdout.strip()))
            metadata['file_size_mib'] = round(os.path.getsize(file_path) / (1024 * 1024), 2)
            
        except Exception as e:
            logger.error(f"Could not get file metadata: {str(e)}")
            metadata['duration'] = None
            metadata['file_size_mib'] = None
        
        return metadata
