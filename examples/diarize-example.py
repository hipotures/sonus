import os
from pyannote.audio import Pipeline
import torch

# Ustaw token Hugging Face
os.environ["HF_TOKEN"] = "hf_....."

# Sprawdź dostępność CUDA
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# Ścieżka do pliku audio (względem katalogu głównego projektu)
AUDIO_PATH = os.path.join(os.path.dirname(
    __file__), "sample_audio_2_persons.mp3")
OUTPUT_PATH = os.path.join(os.path.dirname(
    __file__), "sample_audio_2_persons.rttm")


def main():
    # Inicjalizacja pipeline'u
    try:
        pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization-3.1",
            use_auth_token=True  # Automatycznie użyje HF_TOKEN
        )

        # Ustaw urządzenie (CPU/GPU)
        pipeline.to(device)

        print(f"Processing file: {AUDIO_PATH}")

        # Uruchom diaryzację
        diarization = pipeline(AUDIO_PATH)

        # Zapisz wynik w formacie RTTM
        with open(OUTPUT_PATH, "w") as rttm:
            diarization.write_rttm(rttm)

        print(f"Results saved to: {OUTPUT_PATH}")

        # Wyświetl wyniki
        print("\nDiarization results:")
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            print(f"[{turn.start:.1f}s -> {turn.end:.1f}s] {speaker}")

    except Exception as e:
        print(f"Error during diarization: {str(e)}")
        print("\nMake sure to:")
        print("1. Set HF_TOKEN environment variable with your Hugging Face token")
        print("2. Accept terms for the model at: https://huggingface.co/pyannote/speaker-diarization-3.1")
        print("3. Accept terms for the model at: https://huggingface.co/pyannote/segmentation-3.0")


if __name__ == "__main__":
    main()
