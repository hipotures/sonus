#!/usr/bin/env python3
from src.transcriber.storage import StorageClientFactory
from src.transcriber.logger import ActivityLogger
import os
import sys
import json
import time
from datetime import datetime

# Dodaj ścieżkę do PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.abspath(os.path.join(
    current_dir, '..', 'sonus-transcriber', 'src'))
sys.path.insert(0, src_path)


# Ustaw ścieżki dla modeli i transkrypcji
os.environ["MODELS_DIR"] = "/tmp/sonus/models"
os.environ["WORK_DIR"] = "/tmp/sonus/work"
os.environ["DEBUG"] = "true"

# Upewnij się, że katalogi istnieją
os.makedirs(os.environ["MODELS_DIR"], exist_ok=True)
os.makedirs(os.environ["WORK_DIR"], exist_ok=True)

# Lista testowych rozszerzeń
AUDIO_EXTENSIONS = ['mp3', 'wav', 'm4a', 'flac']
VIDEO_EXTENSIONS = ['mp4', 'mov', 'avi', 'mkv']
UNSUPPORTED_EXTENSIONS = ['pdf', 'doc', 'txt', 'jpg']


def test_extension(logger, extension: str, supported: bool = True):
    """Test obsługi pojedynczego rozszerzenia."""
    print(f"\nTesting .{extension} extension...")

    # Symulacja danych z Pub/Sub
    file_info = {
        "file_id": None,
        "file_name": f"test_file.{extension}",
        "file_path": f"file://{os.getcwd()}/examples",
        "shared_by": "local",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "operation": "konwersja"
    }

    # Utwórz storage client
    storage_client = StorageClientFactory.create_client(file_info, logger)
    base_name = f"test_file"

    if supported:
        # Symulacja transkrypcji
        transcription = "This is a test transcription."
        metadata = {
            "duration": 60,
            "file_size_mib": 1.5,
            "language": "pl"
        }

        # Zapisz pliki
        storage_client.upload_text_file(
            file_info, f"{base_name}.txt", transcription)
        storage_client.upload_text_file(
            file_info, f"{base_name}.json",
            json.dumps(metadata, indent=2, ensure_ascii=False))

        print(f"Created test files for .{extension}:")
        print(f"- {base_name}.txt")
        print(f"- {base_name}.json")
    else:
        # Utwórz plik .err dla nieobsługiwanych formatów
        supported_formats = (
            f"Audio files: {', '.join(AUDIO_EXTENSIONS)}\n"
            f"Video files: {', '.join(VIDEO_EXTENSIONS)}"
        )
        error_message = (
            f"Unsupported media type.\n\n"
            f"The following media types are supported:\n{supported_formats}"
        )
        storage_client.upload_text_file(
            file_info, f"{base_name}.err", error_message)
        print(f"Created .err file for unsupported extension .{extension}")


def main():
    logger = ActivityLogger()

    print("Testing supported audio extensions...")
    for ext in AUDIO_EXTENSIONS:
        test_extension(logger, ext)

    print("\nTesting supported video extensions...")
    for ext in VIDEO_EXTENSIONS:
        test_extension(logger, ext)

    print("\nTesting unsupported extensions...")
    for ext in UNSUPPORTED_EXTENSIONS:
        test_extension(logger, ext, supported=False)


if __name__ == "__main__":
    main()
