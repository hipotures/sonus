#!/usr/bin/env python3
from transcriber.main import WhisperXTranscriber, ActivityLogger
import os
import sys

# Dodaj ścieżkę do PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.abspath(os.path.join(
    current_dir, '..', 'sonus-transcriber', 'src'))
sys.path.insert(0, src_path)

# Importuj po dodaniu ścieżki do PYTHONPATH

# Ustaw ścieżki dla modeli i transkrypcji
os.environ["MODELS_DIR"] = "/tmp/sonus/models"
os.environ["TRANSCRIPTIONS_DIR"] = "/tmp/sonus/transcriptions"
os.environ["HF_TOKEN"] = "hf_....."

# Upewnij się, że katalogi istnieją
os.makedirs(os.environ["MODELS_DIR"], exist_ok=True)
os.makedirs(os.environ["TRANSCRIPTIONS_DIR"], exist_ok=True)


def main():
    # Inicjalizacja loggera i transcribera
    logger = ActivityLogger()
    transcriber = WhisperXTranscriber(logger)

    # Ścieżka do przykładowego pliku audio
    audio_file = os.path.join(current_dir, "sample_audio_2_persons.mp3")

    try:
        # Wykonaj transkrypcję z pełną funkcjonalnością:
        # - Model: large-v2
        # - Compute type: float32 dla lepszej kompatybilności
        # - Batch size: 16 (GPU) lub 4 (CPU)
        # - Chunk size: 10 dla lepszej segmentacji
        # - Język: wymuszony polski
        # - Diaryzacja: minimum 2 mówców
        # - Alignment: precyzyjne mapowanie tekstu na ścieżkę audio
        transcription = transcriber.transcribe(
            audio_file, os.path.basename(audio_file))

        # Wyniki zostały zapisane w:
        # - /tmp/sonus/transcriptions/sample_audio_2_persons.txt (transkrypcja z oznaczeniem mówców)
        # - /tmp/sonus/transcriptions/sample_audio_2_persons.json (pełne wyniki z czasami i metadanymi)
        print("\nTranscription result:")
        print(transcription)

        # Wyświetl informacje o lokalizacji plików wynikowych
        txt_path = os.path.join(os.environ["TRANSCRIPTIONS_DIR"],
                                os.path.splitext(os.path.basename(audio_file))[0] + ".txt")
        json_path = os.path.join(os.environ["TRANSCRIPTIONS_DIR"],
                                 os.path.splitext(os.path.basename(audio_file))[0] + ".json")

        print("\nOutput files:")
        print(f"Text file (with speaker labels): {txt_path}")
        print(f"JSON file (with timestamps and metadata): {json_path}")

    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
