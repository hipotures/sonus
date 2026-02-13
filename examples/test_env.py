from transcriber.main import MODELS_DIR, WORK_DIR
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
    f"WORK_DIR = {os.environ.get('WORK_DIR', 'nie ustawione')}")

# Ustaw zmienne środowiskowe
os.environ["MODELS_DIR"] = "/tmp/sonus/models"
os.environ["WORK_DIR"] = "/tmp/sonus/work"

print("\nPo ustawieniu:")
print(f"MODELS_DIR = {os.environ.get('MODELS_DIR', 'nie ustawione')}")
print(
    f"WORK_DIR = {os.environ.get('WORK_DIR', 'nie ustawione')}")

# Importuj moduł

print("\nW zaimportowanym module:")
print(f"MODELS_DIR = {MODELS_DIR}")
print(f"WORK_DIR = {WORK_DIR}")
