import os
import time
import psutil
import gc
import json
import whisperx


def get_models_dir():
    return os.environ.get("MODELS_DIR", "/models")


class WhisperXTranscriber:
    def __init__(self, logger):
        self.logger = logger
        self.is_debug_enabled = os.environ.get(
            'DEBUG', 'False').lower() == 'true'
        self.use_gpu = os.environ.get("GPU", "false").lower() == "true"
        self.device = "cuda" if self.use_gpu else "cpu"
        self.compute_type = "float16" if self.use_gpu else "float32"
        self.model_name = "large-v2"  # Zawsze używamy large-v2
        self.language = os.environ.get("LANGUAGE", "pl")  # Domyślnie polski
        self.model = None
        self.duration = None
        self.file_size_mib = None

    def load_model(self):
        """Load WhisperX model from mounted GCS path."""
        try:
            self.logger.debug(
                f"Loading model {self.model_name} on {self.device}")
            self.logger.debug(
                f"Using compute type: {self.compute_type}")
            self.logger.debug(f"Using language: {self.language}")
            self.logger.debug(
                f"Loading model with parameters: model_name={self.model_name}, device={self.device}, compute_type={self.compute_type}")
            try:
                # Najpierw próbujemy załadować lokalnie
                self.model = whisperx.load_model(
                    whisper_arch=self.model_name,
                    device=self.device,
                    compute_type=self.compute_type,
                    download_root=get_models_dir(),
                    local_files_only=True,
                    language=self.language,  # Używamy języka ze zmiennej środowiskowej
                    threads=8  # Ustawiamy 8 wątków CPU
                )
            except Exception as e:
                if self.is_debug_enabled:
                    self.logger.warning(
                        f"Could not load model locally: {str(e)}")
                    self.logger.debug("Downloading model...")
                # Jeśli nie ma lokalnie, pobieramy
                self.model = whisperx.load_model(
                    whisper_arch=self.model_name,
                    device=self.device,
                    compute_type=self.compute_type,
                    download_root=get_models_dir(),
                    local_files_only=False,
                    language=self.language,  # Używamy języka ze zmiennej środowiskowej
                    threads=8  # Ustawiamy 8 wątków CPU
                )
            self.logger.debug("Model loaded successfully")
        except Exception as e:
            self.logger.error(f"Error loading model: {str(e)}")
            raise

    def transcribe(self, audio_path, original_filename):
        """Transcribe audio file using WhisperX."""
        try:
            if self.model is None:
                self.load_model()

            start_time = time.time()
            initial_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB

            file_info = f"{os.path.basename(audio_path)}, {self.duration} seconds, {self.file_size_mib} MiB"
            self.logger.info(f"Starting transcription: {file_info}")

            self.logger.debug(
                f"Initial memory usage: {initial_memory:.2f} MB")

            audio = whisperx.load_audio(audio_path)
            try:
                # 1. Transkrypcja podstawowa z parametrami z test08
                result = self.model.transcribe(
                    audio=audio,
                    batch_size=16,  # Optymalny batch_size z test08
                    chunk_size=10,  # Mniejszy chunk_size z test08 dla lepszej segmentacji
                    language=self.language,  # Używamy języka ze zmiennej środowiskowej
                    task="transcribe",
                    verbose=False,  # Wyłączamy verbose output
                    print_progress=True  # Pokazujemy postęp transkrypcji
                )

                if not isinstance(result, dict) or "segments" not in result:
                    raise ValueError(
                        f"Unexpected transcription result format: {type(result)}")

                if not result["segments"]:
                    self.logger.info(
                        "No speech detected in the audio file")
                    return ""

                # 2. Alignment
                self.logger.debug("Starting alignment...")
                model_a, metadata = whisperx.load_align_model(
                    language_code=result["language"],
                    device=self.device
                )
                aligned_result = whisperx.align(
                    result["segments"],
                    model_a,
                    metadata,
                    audio,
                    self.device,
                    return_char_alignments=False
                )
                result["segments"] = aligned_result["segments"]
                self.logger.debug("Alignment completed")

                # Zwolnij pamięć po alignmencie
                gc.collect()
                del model_a

                # 3. Diaryzacja (opcjonalna)
                diarize_segments = None  # Inicjalizacja przed try/except
                try:
                    self.logger.debug("Starting diarization...")
                    diarize_model = whisperx.DiarizationPipeline(
                        use_auth_token=True,  # Użyje tokena ze zmiennej środowiskowej HF_TOKEN
                        device=self.device
                    )
                    diarize_segments = diarize_model(
                        audio,
                        min_speakers=2  # Minimum 2 speakers
                    )
                    self.logger.debug("Diarization completed")

                    # 4. Przypisanie mówców do segmentów
                    diarized_result = whisperx.assign_word_speakers(
                        diarize_segments, result)
                    if isinstance(diarized_result, list):
                        result["segments"] = diarized_result
                    self.logger.debug("Speaker assignment completed")

                    # Zwolnij pamięć po diaryzacji
                    gc.collect()
                    del diarize_model

                except Exception as e:
                    self.logger.debug(
                        f"Diarization failed: {str(e)}. Continuing without speaker diarization.")
                    # Kontynuuj bez diaryzacji

                # 5. Przygotowanie tekstu i metadanych
                current_speaker = None
                transcription_lines = []

                for segment in result["segments"]:
                    speaker = segment.get('speaker', 'unknown')
                    text = segment['text'].strip()

                    # Jeśli zmienił się mówca, dodaj pustą linię
                    if current_speaker is not None and current_speaker != speaker:
                        transcription_lines.append("")

                    transcription_lines.append(f"[Speaker {speaker}] {text}")
                    current_speaker = speaker

                transcription_text = "\n".join(transcription_lines)
            except Exception as e:
                self.logger.error(
                    f"Error during transcription steps: {str(e)}")
                raise
            text_size_kb = len(transcription_text.encode('utf-8')) / 1024

            # 6. Przygotuj dane do zapisu
            json_content = {
                "segments": result["segments"],
                "diarization": [],
                "language": self.language,
                "duration": self.duration,
                "file_size_mib": self.file_size_mib
            }

            if diarize_segments is not None:
                # Konwertuj DataFrame na listę słowników
                segments_dict = diarize_segments.to_dict('records')
                for segment in segments_dict:
                    json_content["diarization"].append({
                        "start": float(segment.get('start', 0)),
                        "end": float(segment.get('end', 0)),
                        "speaker": segment.get('speaker', 'UNKNOWN')
                    })

            # Calculate and log performance metrics
            end_time = time.time()
            duration_seconds = end_time - start_time
            duration_minutes = duration_seconds / 60
            final_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
            memory_diff = final_memory - initial_memory

            # Log completion info
            self.logger.info(
                f"Transcription: text size: {text_size_kb:.2f} KiB, completed in {duration_minutes:.2f} minutes")

            if self.is_debug_enabled:
                self.logger.debug(
                    f"Memory usage change: {memory_diff:.2f} MB")

            return {
                'text': transcription_text,
                'json': json_content
            }

        except Exception as e:
            self.logger.error(f"Error during transcription: {str(e)}")
            raise
