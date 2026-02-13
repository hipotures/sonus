# Unit Tests Documentation

## Overview

The test suite is designed to verify all critical components of the transcription system:
- File handling (local and Google Drive)
- Message processing (Pub/Sub)
- Error handling
- Configuration management
- Full transcription flow

## Test Structure

### 1. Main Component Tests (`test_main.py`)

Tests error handling and basic operations:

#### Error Handling
- `test_unsupported_file_extension_creates_err_file`: Verifies that attempting to process an unsupported file type (e.g., .pdf) creates a .err file with proper error message
- `test_nonexistent_file_creates_err_file`: Checks that attempting to process a nonexistent file creates a .err file
- `test_existing_txt_file_skips_processing`: Verifies that existing .txt files are not reprocessed
- `test_existing_tmp_file_skips_processing`: Ensures that files currently being processed (with .tmp) are skipped
- `test_existing_err_file_skips_processing`: Confirms that files with previous errors (.err) are not reprocessed

### 2. Storage Tests

#### Local Storage (`test_local_storage.py`)
- `test_file_exists_returns_true_for_existing_file`: Verifies file existence checking
- `test_file_exists_returns_false_for_nonexistent_file`: Tests nonexistent file handling
- `test_download_file_copies_file_to_work_dir`: Checks file copying to work directory
- `test_download_file_raises_error_for_nonexistent_file`: Verifies error handling for missing files
- `test_upload_text_file_creates_file_in_correct_location`: Tests text file creation with proper permissions
- `test_delete_file_removes_file`: Verifies file deletion
- `test_delete_file_handles_nonexistent_file`: Tests graceful handling of deleting nonexistent files
- Integration tests:
  - `test_local_transcription_with_existing_txt`: Tests handling of existing transcriptions
  - `test_local_transcription_with_existing_tmp`: Tests handling of in-progress transcriptions
  - `test_local_transcription_with_existing_err`: Tests handling of failed transcriptions
  - `test_local_transcription_with_unsupported_file`: Tests handling of unsupported file types

#### Google Drive Storage (`test_drive_storage.py`)
- `test_file_exists_returns_true`: Tests file existence verification in Drive
- `test_file_exists_returns_false`: Tests nonexistent file handling in Drive
- Integration tests:
  - `test_drive_transcription`: Tests complete transcription flow
  - `test_drive_transcription_with_existing_txt`: Tests handling of existing transcriptions
  - `test_drive_transcription_with_existing_tmp`: Tests handling of in-progress transcriptions
  - `test_drive_transcription_with_existing_err`: Tests handling of failed transcriptions
  - `test_drive_transcription_with_unsupported_file`: Tests handling of unsupported file types (.pdf, .jpg)

### 3. Configuration Tests (`test_config.py`)

Tests environment variable handling:
- `test_default_config`: Verifies default configuration (test queue)
- `test_production_config`: Tests production queue configuration
- `test_custom_config`: Tests custom queue configuration
- `test_invalid_config_format`: Verifies error handling for invalid config format
- `test_empty_config_values`: Tests error handling for empty config values

### 4. Integration Tests

#### Full Process Integration (`test_transcriber_integration.py`)
Base class for storage-specific integration tests:
- `test_transcription_process`: Tests complete transcription flow
- `test_transcription_with_existing_file`: Tests handling of existing files
- `test_transcription_with_existing_txt`: Tests handling of existing transcriptions
- `test_transcription_with_existing_tmp`: Tests handling of in-progress transcriptions
- `test_transcription_with_existing_err`: Tests handling of failed transcriptions
- `test_transcription_with_unsupported_file`: Tests handling of unsupported file types

## Running Tests

### Basic Test Run
```bash
cd sonus-transcriber && \
mkdir -p /tmp/sonus/models && \
PUBSUB_CONFIG="sonus-pubsub-topic-test|sonus-transcriber-sub-test" \
DEBUG=true \
GPU=false \
PROJECT_ID=example-project-id \
MODELS_DIR=/tmp/sonus/models \
WORK_DIR=/tmp/sonus/transcriptions \
HF_TOKEN=hf_dummy \
python -m pytest
```

### Running Specific Tests
```bash
# Run single test file
python -m pytest tests/test_main.py -v

# Run specific test with parameters
python -m pytest "tests/test_drive_storage.py::test_drive_transcription_with_unsupported_file[.pdf-drive_test_30s]" -v
```

Format parametrów testu:
- `[extension-config_name]`, np:
  - `.pdf-drive_test_30s` - test z rozszerzeniem .pdf dla konfiguracji drive_test_30s
  - `.jpg-drive_test_30s` - test z rozszerzeniem .jpg dla konfiguracji drive_test_30s

### Test Coverage
```bash
# Run tests with coverage report
python -m pytest --cov=src/transcriber tests/
```

## Test Environment

### Setup
- Uses pytest fixtures for common objects
- Mocks external services where appropriate
- Creates temporary directories for file operations
- Cleans up after tests

### Key Fixtures
- `logger`: ActivityLogger instance
- `pubsub_reader`: PubSubReader with mocked components
- `storage_client`: Storage client instances
- `test_dir`: Temporary directory for file operations
- `test_audio_file`: Sample audio file for transcription tests

## Running Tests

### Basic Test Run
```bash
cd sonus-transcriber
python -m pytest
```

### Running Specific Tests
```bash
# Run single test file
python -m pytest tests/test_main.py

# Run with verbose output
python -m pytest -v

# Run specific test
python -m pytest tests/test_main.py::test_nonexistent_file_creates_err_file
```

### Test Coverage
```bash
# Run tests with coverage report
python -m pytest --cov=src/transcriber tests/
```

## Mocking Strategy

### External Services
- Google Drive API: Mock service responses and file operations
- Pub/Sub: Mock message publishing and receiving
- WhisperX: Mock transcription process for basic tests
- Storage: Mock file operations for isolation

### File Operations
- Use temporary directories for file tests
- Clean up after each test
- Mock file system operations when appropriate

### Error Conditions
- Simulate API errors
- Test timeout scenarios
- Test network issues
- Test invalid file formats

## Best Practices

### Test Organization
- Group related tests in classes
- Use descriptive test names
- Follow AAA pattern (Arrange, Act, Assert)
- Keep tests focused and atomic

### Fixtures
- Use fixtures for common setup
- Clean up resources after tests
- Share fixtures across test modules
- Keep fixtures simple and focused

### Assertions
- Use specific assertions
- Check both positive and negative cases
- Verify error messages and codes
- Test edge cases and boundaries

## Continuous Integration

### GitHub Actions
- Run tests on pull requests
- Generate coverage reports
- Check code style (flake8)
- Verify dependencies

### Cloud Build
- Run tests during build
- Generate test reports
- Store artifacts
- Update coverage badges

## Test Data

### Sample Files
- Use small audio files for tests
- Include various formats (mp3, wav, etc.)
- Test both valid and invalid files
- Include files with multiple speakers

### Mock Data
- Use realistic but minimal data
- Follow production data formats
- Include edge cases
- Test Unicode handling

## Debugging Tests

### Common Issues
- Pytest fixture scope issues
- Mocking complexities
- Resource cleanup
- Timing-dependent tests

### Solutions
- Use pytest -vv for verbose output
- Check fixture teardown
- Use pytest.mark.skip for WIP
- Add debug logging when needed
