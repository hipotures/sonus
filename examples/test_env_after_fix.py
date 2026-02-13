from transcriber.main import get_models_dir, get_transcriptions_dir
import os
import sys

# Dodaj ścieżkę do PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.abspath(os.path.join(
    current_dir, '..', 'sonus-transcriber', 'src'))
sys.path.insert(0, src_path)

print("Przed importem:")
print(f"MODELS_DIR = {os.environ.get('MODELS_DIR', 'nie ustawione')}")
print(
    f"TRANSCRIPTIONS_DIR = {os.environ.get('TRANSCRIPTIONS_DIR', 'nie ustawione')}")

# Ustaw zmienne środowiskowe
os.environ["MODELS_DIR"] = "/tmp/sonus/models"
os.environ["TRANSCRIPTIONS_DIR"] = "/tmp/sonus/transcriptions"

print("\nPo ustawieniu:")
print(f"MODELS_DIR = {os.environ.get('MODELS_DIR', 'nie ustawione')}")
print(
    f"TRANSCRIPTIONS_DIR = {os.environ.get('TRANSCRIPTIONS_DIR', 'nie ustawione')}")

# Importuj moduł

print("\nW zaimportowanym module:")
print(f"MODELS_DIR = {get_models_dir()}")
print(f"TRANSCRIPTIONS_DIR = {get_transcriptions_dir()}")
