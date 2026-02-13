import whisperx
import os
from typing import Optional


def debug_transcribe(
    audio_path: str,
    model_name: str = "base",
    device: str = "cpu",
    compute_type: str = "float32",
    language: Optional[str] = None,
) -> dict:
    """
    Debug function to transcribe a single audio file using WhisperX.

    Args:
        audio_path: Path to the audio file
        model_name: WhisperX model name (default: "base")
        device: Device to run on (default: "cpu")
        compute_type: Compute type (default: "float32")
        language: Language code (default: None for auto-detection)

    Returns:
        dict: Transcription result
    """
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    models_dir = "/tmp/sonus/models"
    os.makedirs(models_dir, exist_ok=True)
    os.environ["MODELS_DIR"] = models_dir

    try:
        model = whisperx.load_model(
            model_name, device=device, compute_type=compute_type)
    except Exception as e:
        raise ValueError(f"Failed to load model {model_name}: {str(e)}")

    result = model.transcribe(audio_path, language=language)
    return result
