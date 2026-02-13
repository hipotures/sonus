#!/usr/bin/env python3
from transcriber import process_file
import os
import sys

# Dodaj ścieżkę do PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.abspath(os.path.join(
    current_dir, '..', 'sonus-transcriber', 'src'))
sys.path.insert(0, src_path)

# Ustaw ścieżki dla modeli i transkrypcji
os.environ["MODELS_DIR"] = "/tmp/sonus/models"
os.environ["TRANSCRIPTIONS_DIR"] = "/tmp/sonus/transcriptions"
os.environ["HF_TOKEN"] = "hf_...."

# Upewnij się, że katalogi istnieją
os.makedirs(os.environ["MODELS_DIR"], exist_ok=True)
os.makedirs(os.environ["TRANSCRIPTIONS_DIR"], exist_ok=True)

# Importuj po ustawieniu zmiennych środowiskowych


def main():
    # Ścieżka do przykładowego pliku audio
    audio_file = os.path.join(current_dir, "sample_audio_2_persons.mp3")

    try:
        # Wykonaj transkrypcję
        transcription = process_file(audio_file, os.path.basename(audio_file))
        print(transcription)

    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
