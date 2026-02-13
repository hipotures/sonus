#!/usr/bin/env python3
from src.transcriber.whisperx_transcriber import WhisperXTranscriber
from src.transcriber.storage import StorageClientFactory
from src.transcriber.logger import ActivityLogger
import os
import sys
import time
import json
from datetime import datetime

# Dodaj ścieżkę do PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.abspath(os.path.join(
    current_dir, '..', 'sonus-transcriber', 'src'))
sys.path.insert(0, src_path)


# Ustaw ścieżki dla modeli i transkrypcji
os.environ["MODELS_DIR"] = "/tmp/sonus/models"
os.environ["WORK_DIR"] = "/tmp/sonus/work"
os.environ["HF_TOKEN"] = "hf_..."
os.environ["DEBUG"] = "true"

# Upewnij się, że katalogi istnieją
os.makedirs(os.environ["MODELS_DIR"], exist_ok=True)
os.makedirs(os.environ["WORK_DIR"], exist_ok=True)


def main():
    # Inicjalizacja
    logger = ActivityLogger()

    # Ścieżka do przykładowego pliku audio
    audio_file = os.path.join(current_dir, "sample_audio_2_persons.mp3")
    file_name = os.path.basename(audio_file)
    base_name = os.path.splitext(file_name)[0]

    try:
        # Symulacja danych z Pub/Sub
        file_info = {
            "file_id": None,
            "file_name": file_name,
            "file_path": f"file://{os.path.dirname(audio_file)}",
            "shared_by": "local",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "operation": "konwersja"
        }

        # Utwórz storage client
        storage_client = StorageClientFactory.create_client(file_info, logger)

        # Utwórz plik .tmp
        tmp_content = f"Transcription in progress, started at {time.strftime('%Y%m%d %H:%M:%S')}"
        logger.logger.info(f"Creating .tmp file: {base_name}.tmp")
        storage_client.upload_text_file(
            file_info, f"{base_name}.tmp", tmp_content)

        # Wykonaj transkrypcję
        logger.logger.info("Starting transcription...")
        transcriber = WhisperXTranscriber(logger)
        result = transcriber.transcribe(audio_file, file_name)

        # Zapisz wyniki
        storage_client.upload_text_file(
            file_info, f"{base_name}.txt", result['text'])
        storage_client.upload_text_file(
            file_info, f"{base_name}.json",
            json.dumps(result['json'], indent=2, ensure_ascii=False))

        # Usuń plik .tmp
        storage_client.delete_file(file_info, f"{base_name}.tmp")

        # Wyświetl wynik
        print("\nTranscription completed successfully!")
        print(f"Files created in {os.path.dirname(audio_file)}:")
        print(f"- {base_name}.txt")
        print(f"- {base_name}.json")

    except Exception as e:
        logger.logger.error(f"Error: {str(e)}")
        # Usuń plik .tmp w przypadku błędu
        try:
            storage_client.delete_file(file_info, f"{base_name}.tmp")
        except:
            pass
        sys.exit(1)


if __name__ == "__main__":
    main()
