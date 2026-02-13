# Testy jednostkowe do zaimplementowania

## Storage Clients

### LocalStorageClient ✅
- [x] test_file_exists_returns_true_for_existing_file
- [x] test_file_exists_returns_false_for_nonexistent_file
- [x] test_download_file_copies_file_to_work_dir
- [x] test_download_file_raises_error_for_nonexistent_file
- [x] test_upload_text_file_creates_file_in_correct_location
- [x] test_delete_file_removes_file
- [x] test_delete_file_handles_nonexistent_file

### DriveStorageClient ✅
- [x] test_file_exists_returns_true_for_existing_file
- [x] test_file_exists_returns_false_for_nonexistent_file
- [x] test_download_file_saves_to_work_dir
- [x] test_upload_text_file_creates_file_in_drive
- [x] test_delete_file_removes_file
- [x] test_delete_file_handles_nonexistent_file

## Transcriber

### Obsługa błędów ✅
- [x] test_unsupported_file_extension_creates_err_file
- [x] test_nonexistent_file_creates_err_file
- [x] test_file_access_error_creates_err_file
- [x] test_existing_txt_file_skips_processing
- [x] test_existing_json_file_skips_processing
- [x] test_existing_tmp_file_skips_processing
- [x] test_existing_err_file_skips_processing

### Obsługa plików ⏳
- [ ] test_creates_tmp_file_before_processing
- [ ] test_deletes_tmp_file_after_success
- [ ] test_deletes_tmp_file_after_error
- [ ] test_creates_txt_and_json_files_after_success

### Pub/Sub ✅
- [x] test_pubsub_message_missing_filename
- [x] test_pubsub_message_missing_filepath
- [x] test_pubsub_message_invalid_json
- [x] test_pubsub_message_acknowledges_on_success
- [x] test_pubsub_message_no_acknowledge_on_error

### Konfiguracja Pub/Sub ✅
- [x] test_pubsub_config_default_uses_test_queue
- [x] test_pubsub_config_custom_queue
- [x] test_pubsub_config_production_queue
- [x] test_pubsub_config_invalid_format
- [x] test_pubsub_config_missing_separator
- [x] test_pubsub_config_empty_values

### WhisperX ⏳
- [ ] test_transcription_result_format
- [ ] test_transcription_with_diarization
- [ ] test_transcription_without_diarization
- [ ] test_transcription_handles_ffprobe_error
- [ ] test_transcription_handles_whisperx_error

## Integracyjne

### Pełny proces ✅
- [x] test_full_process_mp3_file
- [x] test_full_process_wav_file
- [x] test_full_process_video_file
- [x] test_full_process_unsupported_file
- [x] test_full_process_nonexistent_file

### Storage ✅
- [x] test_local_to_local_file_copy
- [x] test_drive_to_local_file_download
- [x] test_local_to_drive_file_upload

## Mockowanie ✅
- [x] Google Drive API
- [x] WhisperX
- [x] FFprobe
- [x] Pub/Sub
- [x] Storage Clients

## Fixtures ✅
- [x] Przykładowe pliki audio/video
- [x] Przykładowe transkrypcje
- [x] Przykładowe pliki .err
- [x] Przykładowe wiadomości Pub/Sub
- [x] Przykładowe odpowiedzi API

## Konfiguracja testów ✅
- [x] Skonfigurować pytest.ini
- [x] Skonfigurować coverage
- [x] Skonfigurować tox dla różnych wersji Pythona
- [x] Dodać GitHub Actions dla CI/CD

## Testy zmiennych środowiskowych

### Main ⏳
- [ ] test_missing_debug_env_var_defaults_to_false
- [ ] test_invalid_debug_env_var_defaults_to_false
- [ ] test_missing_gpu_env_var_defaults_to_false
- [ ] test_invalid_gpu_env_var_defaults_to_false
- [ ] test_missing_project_id_env_var_raises_error
- [ ] test_empty_project_id_env_var_raises_error
- [ ] test_missing_models_dir_env_var_raises_error
- [ ] test_empty_models_dir_env_var_raises_error
- [ ] test_missing_transcriptions_dir_env_var_raises_error
- [ ] test_empty_transcriptions_dir_env_var_raises_error
- [ ] test_missing_pubsub_config_env_var_uses_test_queue
- [ ] test_empty_pubsub_config_env_var_uses_test_queue
- [ ] test_invalid_pubsub_config_format_raises_error
- [ ] test_missing_hf_token_env_var_raises_error
- [ ] test_empty_hf_token_env_var_raises_error

## Następne kroki

1. Dokończyć implementację testów WhisperX:
   - Przygotować mocki dla modeli
   - Dodać testy dla różnych konfiguracji
   - Przetestować obsługę błędów

2. Rozszerzyć testy integracyjne:
   - Dodać więcej scenariuszy testowych
   - Przetestować edge cases
   - Dodać testy wydajnościowe

3. Poprawić konfigurację CI/CD:
   - Skonfigurować GitHub Actions
   - Dodać automatyczne generowanie raportów
   - Skonfigurować badges w README.md

4. Dodać testy dla nowych funkcjonalności:
   - Obsługa plików tymczasowych (.tmp)
   - Generowanie plików wynikowych (.txt, .json)
   - Obsługa błędów WhisperX
   - Konfiguracja diaryzacji

5. Poprawić dokumentację testów ✅:
   - [x] Dodać przykłady użycia w README.md
   - [x] Zaktualizować CHANGELOG.md
   - [x] Dodać sekcję troubleshooting
   - [x] Opisać proces debugowania testów
   - [x] Dodać instrukcje uruchamiania testów z parametrami
   - [x] Dodać opis formatu parametrów testowych
   - [x] Zaktualizować listę aktualnych testów
