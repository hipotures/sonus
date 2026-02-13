#!/usr/bin/env python3
import os
import sys
import json
import whisperx
import torch
from datetime import datetime

# Ustaw liczbę wątków dla PyTorch
torch.set_num_threads(16)

# Dodaj ścieżkę do PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.abspath(os.path.join(
    current_dir, '..', 'sonus-transcriber', 'src'))
sys.path.insert(0, src_path)

# Ustaw ścieżki dla modeli i wyników
os.environ["MODELS_DIR"] = "/tmp/sonus/models"
os.environ["HF_TOKEN"] = "hf_..."
RESULTS_DIR = os.path.join(current_dir, "tuning_results")
os.makedirs(RESULTS_DIR, exist_ok=True)

# Parametry do przetestowania
TEST_CONFIGS = [
    {
        "name": "test01",
        "description": "Baseline - domyślne parametry",
        "params": {
            "batch_size": 16,
            "compute_type": "float32",
            "chunk_size": 30,
            "language": "pl"
        }
    },
    {
        "name": "test02",
        "description": "Większy batch_size",
        "params": {
            "batch_size": 32,
            "compute_type": "float32",
            "chunk_size": 30,
            "language": "pl"
        }
    },
    {
        "name": "test03",
        "description": "Mniejszy chunk_size",
        "params": {
            "batch_size": 16,
            "compute_type": "float32",
            "chunk_size": 15,
            "language": "pl"
        }
    },
    {
        "name": "test04",
        "description": "Średni chunk_size",
        "params": {
            "batch_size": 16,
            "compute_type": "float32",
            "chunk_size": 25,
            "language": "pl"
        }
    },
    {
        "name": "test05",
        "description": "Mały batch_size, średni chunk_size",
        "params": {
            "batch_size": 8,
            "compute_type": "float32",
            "chunk_size": 25,
            "language": "pl"
        }
    },
    {
        "name": "test06",
        "description": "Duży batch_size, mały chunk_size",
        "params": {
            "batch_size": 32,
            "compute_type": "float32",
            "chunk_size": 15,
            "language": "pl"
        }
    },
    {
        "name": "test07",
        "description": "Bardzo duży batch_size",
        "params": {
            "batch_size": 64,
            "compute_type": "float32",
            "chunk_size": 20,
            "language": "pl"
        }
    },
    {
        "name": "test08",
        "description": "Bardzo mały chunk_size",
        "params": {
            "batch_size": 16,
            "compute_type": "float32",
            "chunk_size": 10,
            "language": "pl"
        }
    },
    {
        "name": "test09",
        "description": "Średni batch_size i chunk_size",
        "params": {
            "batch_size": 24,
            "compute_type": "float32",
            "chunk_size": 20,
            "language": "pl"
        }
    },
    {
        "name": "test10",
        "description": "Duży batch_size, średni chunk_size",
        "params": {
            "batch_size": 48,
            "compute_type": "float32",
            "chunk_size": 25,
            "language": "pl"
        }
    }
]


def run_transcription_test(config, audio_path):
    """Wykonaj test transkrypcji z danymi parametrami."""
    print(f"\n{'='*80}")
    print(f"Uruchamiam test: {config['name']} - {config['description']}")
    print(f"Parametry: {json.dumps(config['params'], indent=2)}")

    # Przygotuj ścieżki plików wynikowych
    base_path = os.path.join(RESULTS_DIR, config['name'])
    params_file = f"{base_path}_params.json"
    transcript_file = f"{base_path}_transcript.txt"

    # Zapisz parametry testu
    test_info = {
        "name": config['name'],
        "description": config['description'],
        "parameters": config['params'],
        "timestamp": datetime.now().isoformat(),
        "audio_file": os.path.basename(audio_path)
    }

    with open(params_file, 'w', encoding='utf-8') as f:
        json.dump(test_info, f, indent=2, ensure_ascii=False)

    try:
        # Sprawdź dostępność CUDA
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {device}")

        # Załaduj model
        model = whisperx.load_model(
            "large-v2",
            device=device,
            compute_type=config['params']['compute_type'],
            download_root=os.environ["MODELS_DIR"],
            language=config['params']['language']
        )

        # Wykonaj transkrypcję
        audio = whisperx.load_audio(audio_path)
        result = model.transcribe(
            audio=audio,
            batch_size=config['params']['batch_size'],
            chunk_size=config['params']['chunk_size']
        )

        # Zapisz wyniki transkrypcji
        with open(transcript_file, 'w', encoding='utf-8') as f:
            for segment in result["segments"]:
                timestamp = f"[{segment['start']:.3f} --> {segment['end']:.3f}]"
                f.write(f"Transcript: {timestamp}  {segment['text']}\n")

        print(f"Test {config['name']} zakończony. Wyniki zapisane w:")
        print(f"- Parametry: {params_file}")
        print(f"- Transkrypcja: {transcript_file}")

    except Exception as e:
        print(f"Błąd podczas testu {config['name']}: {str(e)}")
        # Zapisz informację o błędzie
        with open(transcript_file, 'w', encoding='utf-8') as f:
            f.write(f"ERROR: {str(e)}\n")


def main():
    # Ścieżka do przykładowego pliku audio
    audio_file = os.path.join(current_dir, "sample_audio_2_persons.mp3")

    print(f"Rozpoczynam testy transkrypcji dla pliku: {audio_file}")
    print(f"Wyniki będą zapisywane w katalogu: {RESULTS_DIR}")

    # Wykonaj testy dla każdej konfiguracji
    for config in TEST_CONFIGS:
        run_transcription_test(config, audio_file)

    print("\nWszystkie testy zakończone. Sprawdź wyniki w katalogu tuning_results/")


if __name__ == "__main__":
    main()
