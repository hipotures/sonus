import os
import json
from google.cloud import pubsub_v1
from google.cloud import storage
from google.oauth2 import service_account
from googleapiclient.discovery import build


def scan_drive_folders():
    """
    Scans Google Drive folders shared with the service account for audio/video files.
    Uses environment variables:
    - AUDIO_EXTENSIONS: comma-separated list of audio extensions (default: mp3,wav,m4a,flac)
    - VIDEO_EXTENSIONS: comma-separated list of video extensions (default: mp4,mov,avi,mkv)
    - DEBUG: if True, prints debug information (default: False)
    """
    # Get environment variables
    audio_exts = set(os.environ.get(
        "AUDIO_EXTENSIONS", "mp3,wav,m4a,flac").lower().split(','))
    video_exts = set(os.environ.get(
        "VIDEO_EXTENSIONS", "mp4,mov,avi,mkv").lower().split(','))
    debug = os.environ.get("DEBUG", "False").lower() in ("true", "1", "yes")

    # Initialize Drive API client
    credentials = service_account.Credentials.default()
    service = build('drive', 'v3', credentials=credentials)

    found_files = []
    page_token = None

    try:
        while True:
            # Get list of all accessible files
            response = service.files().list(
                q="trashed = false",  # Skip files in trash
                spaces='drive',
                fields='nextPageToken, files(id, name, mimeType, parents)',
                pageToken=page_token
            ).execute()

            for file in response.get('files', []):
                file_name = file.get('name', '')
                file_ext = file_name.split(
                    '.')[-1].lower() if '.' in file_name else ''

                if debug:
                    print(f"Found file: {file_name} (ID: {file.get('id')})")

                # Check file extension
                if file_ext in audio_exts:
                    file_type = "audio"
                elif file_ext in video_exts:
                    file_type = "video"
                else:
                    continue  # Skip files with unsupported extensions

                # Get full folder path
                folder_path = get_folder_path(service, file.get('parents', []))

                found_files.append({
                    'id': file.get('id'),
                    'name': file_name,
                    'type': file_type,
                    'folder_path': folder_path
                })

            page_token = response.get('nextPageToken')
            if not page_token:
                break

    except Exception as e:
        if debug:
            print(f"Error scanning Drive folders: {str(e)}")
        raise

    if debug:
        print(f"\nTotal files found: {len(found_files)}")
        for file in found_files:
            print(f"- {file['folder_path']}/{file['name']} ({file['type']})")

    return found_files


def get_folder_path(service, parent_ids, path=""):
    """Recursively builds the folder path."""
    if not parent_ids:
        return path

    try:
        parent = service.files().get(
            fileId=parent_ids[0],
            fields='name, parents'
        ).execute()

        new_path = f"{parent['name']}/{path}" if path else parent['name']
        return get_folder_path(service, parent.get('parents', []), new_path)
    except Exception:
        return path


def needs_transcription(file):
    """
    Determines if the file needs transcription by checking if a transcription
    file already exists in the same folder.
    """
    transcription_name = f"{file['name']}.txt"
    try:
        # Initialize Drive API client
        credentials = service_account.Credentials.default()
        service = build('drive', 'v3', credentials=credentials)

        # Search for transcription file in the same folder
        response = service.files().list(
            q=f"name = '{transcription_name}' and trashed = false",
            spaces='drive',
            fields='files(id, name)'
        ).execute()

        # If no transcription file exists, transcription is needed
        return len(response.get('files', [])) == 0
    except Exception:
        # In case of error, assume transcription is needed
        return True


def publish_transcription_task(file_info):
    """
    Publishes a transcription task to Pub/Sub.
    """
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(
        os.getenv("PROJECT_ID"), "transcription-tasks")

    # Publish the task with the file information as JSON
    future = publisher.publish(
        topic_path, data=json.dumps(file_info).encode("utf-8"))
    return future.result()


def main():
    """
    Main function that scans for files and publishes transcription tasks.
    """
    files = scan_drive_folders()
    for file in files:
        if needs_transcription(file):
            result = publish_transcription_task(file)
            print(f"Published task for {file['name']}, result: {result}")


if __name__ == "__main__":
    main()
