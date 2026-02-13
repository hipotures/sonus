import os
import sys
import json
import time
import logging
import argparse

logging.getLogger("speechbrain").setLevel(logging.WARNING)

from .config import DEBUG, IS_CLOUD_RUN
from .pubsub.client import PubSubClient
from .pubsub.message_handler import PubSubMessageHandler
from .transcription.processor import FileProcessor
from .transcription.file_validator import FileValidator
from .storage import StorageClientFactory

# Set up logging
logger = logging.getLogger('transcriber')
logger.propagate = False  # Prevent propagation to root logger to avoid duplicate logs
logger.setLevel(logging.DEBUG if DEBUG else logging.INFO)

# Configure logging based on environment
if not IS_CLOUD_RUN:  # Running locally
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)
# When running in Cloud Run, use default handler which integrates with Cloud Logging


def process_pubsub():
    """Process messages from Pub/Sub."""
    client = PubSubClient()
    handler = PubSubMessageHandler()
    
    try:
        logger.info(f"Starting to pull messages from Pub/Sub")
        messages = client.pull_message(max_messages=1, wait_timeout=5)
        
        if not messages:
            logger.info("No messages found in the subscription")
            return
        
        # Process only the first message
        received_message = messages[0]
        
        # Acknowledge message immediately
        client.acknowledge_message(received_message.ack_id)
        
        # Process the message
        success = handler.handle_message(received_message)
        if not success:
            sys.exit(1)  # Signal error to Cloud Run
            
    except Exception as e:
        logger.error(f"Error in Pub/Sub processing: {str(e)}")
        sys.exit(1)  # Signal error to Cloud Run
    finally:
        client.close()


def process_local_file(file_path):
    """Process a local file.
    
    Args:
        file_path: Path to the local file
    """
    validator = FileValidator()
    processor = FileProcessor()
    
    file_path = os.path.abspath(file_path)
    file_info = {
        'file_id': None,
        'file_name': os.path.basename(file_path),
        'file_path': f"file://{os.path.dirname(file_path)}",
        'shared_by': 'local',
        'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
        'operation': 'konwersja'
    }
    
    logger.debug(f"Processing local file: {file_info}")
    
    # Create storage client
    storage_client = StorageClientFactory.create_client(file_info, logger)
    
    # Check file extension
    if not validator.is_supported_extension(file_info['file_name']):
        error_message = validator.get_supported_formats_message()
        base_filename = os.path.splitext(file_info['file_name'])[0]
        storage_client.upload_text_file(
            file_info, f"{base_filename}.err", error_message)
        logger.error(
            f"Unsupported file extension for {file_info['file_name']}. Created .err file.")
        return
    
    result = processor.process(file_info)
    if result:
        print("\nTranscription result:")
        print(result['text'])


def process_test_config(config_name):
    """Process file from test configuration.
    
    Args:
        config_name: Name of the configuration in test_config.json
    """
    processor = FileProcessor()
    
    try:
        # Load test configuration
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        config_path = os.path.join(
            project_root, 'tests', 'test_config.json')
        logger.debug(f"Loading config from: {config_path}")
        
        with open(config_path) as f:
            test_config = json.load(f)
        
        # Get specified configuration
        if config_name not in test_config['configs']:
            logger.error(f"Configuration '{config_name}' not found in test_config.json")
            sys.exit(1)
        
        config = test_config['configs'][config_name]
        file_info = config['file']
        logger.debug(f"Processing file from config '{config_name}': {file_info}")
        
        processor.process(file_info)
        
    except Exception as e:
        logger.error(f"Error processing test configuration: {str(e)}")
        sys.exit(1)


def process_json_message(json_data):
    """Process file from JSON message.
    
    Args:
        json_data: JSON string with file information
    """
    processor = FileProcessor()
    
    try:
        file_info = json.loads(json_data)
        processor.process(file_info)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON message: {str(e)}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error processing JSON message: {str(e)}")
        sys.exit(1)


def main():
    """Entry point for processing."""
    parser = argparse.ArgumentParser(
        description='Transcribe audio/video files')
    parser.add_argument(
        '--file', help='Path to audio/video file to transcribe')
    parser.add_argument(
        '--pubsub-message-json', help='JSON message with file information')
    parser.add_argument(
        '--pubsub-message-config', help='Name of configuration from test_config.json, e.g. drive_test_30s')
    parser.add_argument(
        '--pubsub-message', help='DEPRECATED: Use --pubsub-message-json instead', dest='pubsub_message_json')
    parser.add_argument('--pubsub', action='store_true',
                        help='Listen for Pub/Sub messages')
    args = parser.parse_args()
    
    try:
        if args.pubsub_message_json:
            process_json_message(args.pubsub_message_json)
        elif args.pubsub_message_config:
            process_test_config(args.pubsub_message_config)
        elif args.file:
            process_local_file(args.file)
        elif args.pubsub:
            process_pubsub()
        else:
            # Default to Pub/Sub processing for backward compatibility
            process_pubsub()
    except Exception as e:
        logger.error(f"Unhandled error in main: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()
