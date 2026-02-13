"""Module for validating files before processing."""
import os
from ..config import get_supported_extensions

class FileValidator:
    """Validator for checking if files can be processed."""
    
    def __init__(self):
        """Initialize the file validator."""
        self.audio_extensions, self.video_extensions = get_supported_extensions()
    
    def is_supported_extension(self, filename):
        """Check if file has supported extension.
        
        Args:
            filename: Name of the file to check
            
        Returns:
            bool: True if extension is supported, False otherwise
        """
        ext = os.path.splitext(filename)[1].lower().lstrip('.')
        return ext in self.audio_extensions or ext in self.video_extensions
    
    def get_supported_formats_message(self):
        """Get a message describing supported file formats.
        
        Returns:
            str: Formatted message with supported formats
        """
        supported_formats = (
            f"Audio files: {', '.join(self.audio_extensions)}\n"
            f"Video files: {', '.join(self.video_extensions)}"
        )
        error_message = (
            f"Unsupported media type.\n\n"
            f"The following media types are supported:\n{supported_formats}"
        )
        return error_message
