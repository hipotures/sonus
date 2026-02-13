import os
import logging
import json
import datetime
import google.auth
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.cloud import pubsub_v1
from .config import (
    DEBUG,
    IS_CLOUD_RUN,
    PROJECT_ID,
    SERVICE_ACCOUNT_EMAIL,
    GENERATED_EXTENSIONS,
    GENERATED_EXTENSIONS_TUPLE,
    get_supported_extensions,
    get_pubsub_config
)

# Get logger
logger = logging.getLogger('activator')
# Prevent propagation to root logger to avoid duplicate logs
logger.propagate = False
logger.setLevel(logging.DEBUG if DEBUG else logging.INFO)

# Configure logging based on environment
if not IS_CLOUD_RUN:  # Running locally
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)
# When running in Cloud Run, use default handler which integrates with Cloud Logging


def get_credentials(scopes):
    """
    Universal credentials retrieval that works for both Cloud Run and local development.

    Args:
        scopes: List of OAuth scopes required for the API

    Returns:
        google.auth.credentials.Credentials: The obtained credentials

    Raises:
        Exception: If no valid credentials could be obtained
    """
    try:
        # First try to get default credentials (works in Cloud Run)
        credentials, _ = google.auth.default(scopes=scopes)
        logger.debug("Successfully obtained default credentials")
        return credentials
    except Exception as e:
        logger.error(f"Could not get default credentials: {e}")

        # Try to get credentials from service account file
        service_account_file = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        if service_account_file and os.path.exists(service_account_file):
            try:
                credentials = service_account.Credentials.from_service_account_file(
                    service_account_file,
                    scopes=scopes
                )
                logger.debug(
                    f"Successfully obtained credentials from {service_account_file}")
                return credentials
            except Exception as e:
                logger.error(
                    f"Error loading service account credentials: {e}")
                raise Exception("Failed to load service account credentials")
        else:
            logger.error(
                "No credentials available - ensure GOOGLE_APPLICATION_CREDENTIALS is set for local development")
            raise Exception("No credentials available")


class DriveScanner:
    def __init__(self):
        self.project_id = PROJECT_ID
        self.service_account = SERVICE_ACCOUNT_EMAIL
        self.supported_audio, self.supported_video = get_supported_extensions()

        # Initialize Google Drive API client using universal credentials method
        credentials = get_credentials(
            ['https://www.googleapis.com/auth/drive.readonly'])
        self.drive_service = build(
            'drive', 'v3', credentials=credentials, cache_discovery=False)
        logger.debug("Successfully initialized Drive API client")

        # Get PubSub config
        pubsub_config = get_pubsub_config()
        topic_name = pubsub_config['topic']

        # Initialize Pub/Sub publisher
        try:
            self.publisher = pubsub_v1.PublisherClient()
            self.topic_path = self.publisher.topic_path(
                self.project_id, topic_name)
            logger.info(
                f"Successfully initialized Pub/Sub Publisher for topic: {topic_name}")
        except Exception as e:
            logger.error(f"Failed to initialize Pub/Sub publisher: {e}")
            self.publisher = None

    def is_supported_media(self, file_name):
        extension = file_name.lower().split(
            '.')[-1] if '.' in file_name else ''
        return extension in self.supported_audio or extension in self.supported_video

    def check_transcription_exists(self, folder_id, file_name):
        base_name = os.path.splitext(file_name)[0]
        file_names = [f"{base_name}{ext}" for ext in GENERATED_EXTENSIONS]
        file_names_query = " or ".join(f"name = '{name}'" for name in file_names)

        try:
            # Search for generated files in the same folder
            results = self.drive_service.files().list(
                q=f"({file_names_query}) and '{folder_id}' in parents and trashed = false",
                spaces='drive',
                fields='files(id, name)'
            ).execute()

            files = results.get('files', [])
            if files:
                for file in files:
                    if file['name'].endswith(GENERATED_EXTENSIONS_TUPLE):
                        status = {
                            '.txt': "Found transcription file",
                            '.tmp': "Found temporary file - transcription in progress",
                            '.err': "Found error file - unsupported format"
                        }
                        ext = os.path.splitext(file['name'])[1]
                        logger.debug(f"{status.get(ext, 'Found file')}: {file['name']}")
                return True
            return False
        except HttpError as error:
            logger.error(f"Error checking transcription: {error}")
            return False

    def publish_to_pubsub(self, file_info, folder, shared_by=None):
        try:
            if not self.publisher:
                logger.error("Pub/Sub publisher is not initialized.")
                return

            logger.info(
                f"Found file for transcription, user: {shared_by}, file: {file_info.get('name')}")
            message = {
                "file_id": file_info.get("id"),
                "file_name": file_info.get("name"),
                # Use folder ID instead of file ID
                "file_path": f"drive://{folder.get('id')}",
                "shared_by": shared_by,
                "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
                "operation": "konwersja"
            }
            logger.debug(f"Message content: {json.dumps(message, indent=2)}")

            logger.debug(f"Publishing to topic: {self.topic_path}")
            message_json = json.dumps(message).encode("utf-8")
            future = self.publisher.publish(self.topic_path, message_json)
            message_id = future.result()
            logger.debug(
                f"Successfully published message to Pub/Sub: {message_id}")
        except Exception as e:
            logger.error(f"Error publishing message to Pub/Sub: {str(e)}")
            raise

    def scan_shared_folders(self):
        try:
            # List folders shared with service account
            results = self.drive_service.files().list(
                q=f"mimeType = 'application/vnd.google-apps.folder' and '{self.service_account}' in readers and trashed = false",
                spaces='drive',
                fields='files(id, name)'
            ).execute()

            folders = results.get('files', [])
            for folder in folders:
                logger.debug(
                    f"Scanning folder: {folder.get('name')} ({folder.get('id')})")
                self.scan_folder(folder)

        except HttpError as error:
            logger.error(f"Error scanning folders: {error}")

    def scan_folder(self, folder):
        try:
            # List all files in the folder
            results = self.drive_service.files().list(
                q=f"'{folder['id']}' in parents and trashed = false",
                spaces='drive',
                fields='files(id, name, mimeType, permissions(emailAddress, role))'
            ).execute()

            files = results.get('files', [])
            for file in files:
                if self.is_supported_media(file['name']):
                    permissions = file.get('permissions', [])
                    shared_by = None
                    # Find the owner in permissions list
                    for permission in permissions:
                        if permission.get('role') == 'owner':
                            shared_by = permission.get('emailAddress')
                            break
                    logger.debug(
                        f"Found media file in '{folder.get('name')}': {file.get('name')} ({file.get('id')})")
                    if shared_by:
                        logger.debug(f"File owned by: {shared_by}")
                    # Check if transcription exists
                    exists = self.check_transcription_exists(
                        folder['id'], file['name'])
                    status = "exists (skipping)" if exists else "missing (needs processing)"
                    logger.debug(f"Transcription for {file['name']}: {status}")
                    if not exists:
                        self.publish_to_pubsub(file, folder, shared_by)

        except HttpError as error:
            logger.error(
                f"Error scanning folder {folder['name']}: {error}")


def main():
    scanner = DriveScanner()
    scanner.scan_shared_folders()


if __name__ == '__main__':
    main()
