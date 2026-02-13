"""Module for handling Pub/Sub messages."""
import json
import sys
import logging
from ..config import get_supported_extensions
from ..storage import StorageClientFactory

logger = logging.getLogger('transcriber')

class PubSubMessageHandler:
    """Handler for processing Pub/Sub messages."""
    
    def __init__(self):
        """Initialize the message handler."""
        self.audio_extensions, self.video_extensions = get_supported_extensions()
        self.file_processor = None  # Will be initialized when needed
    
    def is_supported_extension(self, filename):
        """Check if file has supported extension.
        
        Args:
            filename: Name of the file to check
            
        Returns:
            bool: True if extension is supported, False otherwise
        """
        ext = filename.lower().split('.')[-1] if '.' in filename else ''
        return ext in self.audio_extensions or ext in self.video_extensions
    
    def decode_message(self, pubsub_message):
        """Decode a Pub/Sub message.
        
        Args:
            pubsub_message: The Pub/Sub message to decode
            
        Returns:
            dict: The decoded message data
            
        Raises:
            ValueError: If message data is invalid
        """
        try:
            data = json.loads(pubsub_message.message.data.decode('utf-8'))
            logger.debug(f"Received message: {json.dumps(data, indent=2)}")
            
            # Validate required fields
            if not data.get('file_name') or not data.get('file_path'):
                raise ValueError("Missing file_name or file_path in message")
            
            return data
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in message: {str(e)}")
            raise ValueError(f"Invalid JSON format: {str(e)}")
    
    def handle_message(self, pubsub_message):
        """Process a Pub/Sub message.
        
        Args:
            pubsub_message: The Pub/Sub message to process
            
        Returns:
            bool: True if processing was successful, False otherwise
        """
        try:
            # Import FileProcessor here to avoid circular imports
            from ..transcription.processor import FileProcessor
            
            # Initialize FileProcessor if needed
            if self.file_processor is None:
                self.file_processor = FileProcessor()
            
            # Decode message
            file_info = self.decode_message(pubsub_message)
            
            # Create storage client
            storage_client = StorageClientFactory.create_client(file_info, logger)
            
            # Check file extension
            if not self.is_supported_extension(file_info['file_name']):
                # Create error file for unsupported extension
                self._create_unsupported_format_error(file_info, storage_client)
                return True  # Successfully handled as an unsupported format
            
            # Process the file
            result = self.file_processor.process(file_info)
            return True
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return False
    
    def _create_unsupported_format_error(self, file_info, storage_client):
        """Create an error file for unsupported format.
        
        Args:
            file_info: File information dict
            storage_client: Storage client to use for uploading
        """
        # Prepare supported formats message
        supported_formats = (
            f"Audio files: {', '.join(self.audio_extensions)}\n"
            f"Video files: {', '.join(self.video_extensions)}"
        )
        error_message = (
            f"Unsupported media type.\n\n"
            f"The following media types are supported:\n{supported_formats}"
        )
        
        # Create .err file
        base_filename = file_info['file_name'].rsplit('.', 1)[0]
        storage_client.upload_text_file(
            file_info, f"{base_filename}.err", error_message)
        logger.warning(
            f"Unsupported file extension for {file_info['file_name']}. Created .err file.")
