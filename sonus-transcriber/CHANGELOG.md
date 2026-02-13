# Changelog

All notable changes to the sonus-transcriber service will be documented in this file.

## [0.0.44] - 2025-03-02

### Changed

- Increased Cloud Run job resources for better performance:
  - CPU: 8 cores (8000m), increased from 6 cores
  - Memory: 32GB (32Gi), increased from 24GB

## [0.0.43] - 2025-02-25

### Changed

- Improved WhisperX transcription output:
  - Disabled verbose output by setting verbose=False
  - Enabled progress display with print_progress=True
  - Reduced log noise by removing detailed transcription output
  - Optimized logging to show only essential information

## [0.0.42] - 2025-02-25

### Changed

- Removed old drive_client.py file:
  - Removed unused file from src/transcriber/drive_client.py
  - Fixed potential logger configuration issues
  - Consolidated Google Drive operations in storage/drive_client.py
  - Ensured consistent logger usage across codebase

## [0.0.41] - 2025-02-25

### Changed

- Improved file status logging in Google Drive:
  - Centralized environment variables management in config.py
  - Added check_files_status method to reduce API calls
  - Optimized file status checking to use one API call instead of multiple
  - Improved log readability by showing only relevant file extensions:
    * Shows found files (both generated and media files that exist)
    * Shows only missing generated files (.txt, .tmp, .err)
    * Example: "File example, found: .tmp, .mp3 not_found: .txt, .err"
  - Removed redundant file extension checks to reduce log noise

## [0.0.40] - 2025-02-24

### Changed

- Improved Pub/Sub message handling:
  - Added 5-second wait and retry for message polling
  - Optimized message polling with immediate return option
  - Properly closing Pub/Sub client to prevent resource leaks
  - Improved error handling for Pub/Sub operations
- Standardized logging to match activator component:
  - Set logger.propagate = False to prevent duplicate logs
  - Consistent log levels across components
  - INFO level for operational status messages
  - DEBUG level for detailed information

## [0.0.39] - 2025-02-24

### Changed

- Improved logging configuration:
  - Added environment detection (local vs Cloud Run) using K_SERVICE
  - Configured proper console handler for local development
  - Integrated with Google Cloud Logging in Cloud Run
  - Simplified logging by using direct logger calls
  - Changed warning logs to error level for better visibility
  - Fixed double logging issues  

## [0.0.38] - 2025-02-24

### Added

- Enhanced test suite for unsupported file extensions:
  - Added test_transcription_with_unsupported_file to test handling of .pdf and .jpg files
  - Added proper file extension validation in tests
  - Added verification of error messages and .err file creation
  - Added test documentation in UNIT_TEST.md

### Changed

- Updated test documentation:
  - Added actual test names and descriptions
  - Added proper test running instructions with environment variables
  - Added test parameter format explanation
  - Updated test coverage information

### Fixed

- Fixed unsupported file extension test:
  - Now properly testing file extension validation
  - Fixed error message verification
  - Added proper cleanup after tests

## [0.0.37] - 2025-02-23

### Fixed

- Fixed Google Drive file upload error:
  - Now correctly getting parent folder ID from source file
  - Fixed "The specified parent is not a folder" error
  - Updated file_exists and delete_file methods to use correct folder ID

## [0.0.36] - 2025-02-23

### Changed

- Added subscription name to "No messages found" log message:
  - Now shows which queue is being checked (test or production)
  - Added PUBSUB_CONFIG environment variable in Cloud Run job for production queue
  - Local development continues to use test queue by default

## [0.0.35] - 2025-02-23

### Changed

- Remove test stage from Cloud Build:
  - Remove test dependencies installation
  - Remove pytest execution in cloud
  - Remove test artifacts configuration
  - Keep only container build and deployment stages
  - Tests are now run locally before pushing changes

## [0.0.34] - 2025-02-23

### Added

- Complete test infrastructure setup:
  - Added pytest.ini with test discovery and reporting settings
  - Added .coveragerc for coverage configuration
  - Added GitHub Actions workflow for CI/CD
  - Added setup.cfg for code style tools
  - Added tox.ini for multi-environment testing
  - Added requirements-test.txt with test dependencies
- Comprehensive test suite implementation:
  - Storage client tests (local and Drive)
  - Pub/Sub configuration tests
  - Error handling tests
  - Integration tests with test queue
  - Full process tests with sample files

### Changed

- Updated test dependencies to match production environment:
  - Added security testing tools (bandit and safety)
  - Added type stubs matching installed package versions
  - Updated types-requests to 2.32.3
  - Updated types-urllib3 to 2.3.0
  - Added development tools (ipython, ipdb)
- Improved test documentation:
  - Added detailed test descriptions in UNIT_TEST.md
  - Added CI/CD workflow documentation
  - Added code style configuration guide
  - Added coverage reporting setup guide
  - Updated test coverage information in README.md
  - Added test status tracking in TODO.md

### Fixed

- Fixed test environment configuration
- Fixed code style settings
- Fixed coverage reporting paths
- Fixed test fixtures cleanup
- Fixed mock implementations for Drive API
- Fixed Pub/Sub test queue configuration

## [0.0.33] - 2025-02-23

### Changed

- Changed "No messages found" log level from debug to info
- Added .gitignore and removed __pycache__ files

## [0.0.32] - 2025-02-23

### Changed

- Added .err file checking in file status verification
- Improved file extension validation logic
- Updated error handling for unsupported file types
- Added detailed logging for .err file creation

## [0.0.31] - 2025-02-23

### Added

- Added file metadata collection:
  - File duration using ffprobe (in seconds)
  - File size measurement (in MiB)
- Added enhanced file info logging:
  - File size displayed immediately after download
  - File duration displayed after ffprobe analysis
  - Added file metadata to JSON output

### Changed

- Changed file size unit from MB to MiB in:
  - JSON output metadata
  - Log messages
  - Internal variable names
- Disabled specific warning messages:
  - Added warnings.filterwarnings for pyannote.audio version mismatch
  - Added warnings.filterwarnings for torch version mismatch
  - Added warnings.filterwarnings("ignore") to suppress unnecessary warnings
  - Cleaner output without PyTorch and other library warnings
- Optimized CPU performance:
  - Added threads=8 parameter to WhisperX model loading
  - Optimized CPU thread utilization for faster transcription
- Improved logging:
  - Simplified non-debug output to show only essential information
  - Added shared_by info to transcription start and completion messages
  - Removed verbose debug output (alignment details, diarization segments)
  - Added verbose transcription progress in debug mode
  - Removed folder ID from file save confirmation

### Fixed

- Fixed memory management:
  - Changed order of gc.collect() and del operations to match WhisperX example
  - Now calling gc.collect() before del for better memory cleanup
- Fixed file locking mechanism:
  - Changed folder_id calculation to properly get parent folder ID from Google Drive API
  - Now using proper folder ID for .tmp file creation instead of file ID

## [0.0.30] - 2025-02-21

### Fixed

- Fixed file locking mechanism:
  - Fixed folder_id calculation for .tmp files on Google Drive
  - Now using file's ID as folder ID to ensure correct lock file placement

## [0.0.29] - 2025-02-21

### Changed

- Bump version to 0.0.29: Updated changelog and tagged release.

## [0.0.28] - 2025-02-21

### Changed

- Changed Cloud Build configuration to use latest tag for Cloud Run job updates
- Ensures Cloud Run always uses the most recent build regardless of tag version

## [0.0.27] - 2025-02-21

### Changed

- Increased Cloud Run job resources for better performance:
  - CPU: 6 cores (6000m)
  - Memory: 24GB (24Gi)
  - Optimized for parallel processing of large audio files

## [0.0.26] - 2025-02-21

### Added

- Added file locking mechanism:
  - Creating .tmp file before starting transcription
  - Acknowledging Pub/Sub message only after .tmp file creation
  - Automatic .tmp file cleanup after transcription or on error
  - Added timestamp information in .tmp file content

## [0.0.25] - 2025-02-21

### Fixed

- Fixed WhisperX model loading by using positional argument instead of named argument
- Fixed output path logging to show both txt and json file paths

## [0.0.24] - 2025-02-21

### Added

- Added full WhisperX pipeline with diarization and alignment:
  - Added alignment step for better word timing
  - Added speaker diarization with minimum 2 speakers
  - Added saving full results in JSON format
  - Added speaker labels in text output [Speaker X]
  - Added HF_TOKEN secret configuration

## [0.0.23] - 2025-02-21

### Fixed

- Fixed model loading by using correct parameter name 'name' instead of 'model_name'

## [0.0.22] - 2025-02-21

### Fixed

- Added whisperx package to requirements.txt

## [0.0.21] - 2025-02-21

### Changed

- Removed initial_prompt parameter to avoid context bias
- Optimized transcription parameters:
  - Using silero VAD with optimized thresholds
  - Added max_line_width and max_line_count for better output formatting
  - Added beam_size=10 and patience=2.0 for better accuracy
  - Added length_penalty=1.5 for better sentence completion
  - Added threads=8 for optimal CPU utilization

## [0.0.20] - 2025-02-21

### Added

- Added WhisperX configuration parameters:
  - Using model_dir and model_cache_only for local model loading
  - Using silero VAD with optimized thresholds
  - Added max_line_width and max_line_count for better output formatting
  - Added verbose and print_progress for better logging
  - Configured no_speech_threshold for better silence detection
  - Set threads=8 for optimal CPU utilization

## [0.0.19] - 2025-02-21

### Added

- Added logging for empty transcription results:
  - Log message when no speech is detected in audio file
  - Save empty file instead of failing

## [0.0.18] - 2025-02-21

### Changed

- Updated dependencies to match official WhisperX requirements:
  - Added specific version of faster-whisper and ctranslate2
  - Added required dependencies: transformers, pandas, nltk
  - Organized requirements.txt into Google Cloud and WhisperX sections

## [0.0.17] - 2025-02-21

### Fixed

- Fixed transcription result handling:
  - Added proper segments handling from WhisperX output
  - Joining segments into complete transcription text
  - Added batch_size parameter (16 for GPU, 4 for CPU)

## [0.0.16] - 2025-02-21

### Fixed

- Improved logging configuration:
  - Disabled log propagation to root logger to prevent duplicates
  - Simplified log format by removing redundant timestamps
  - Cleaned up log output for better readability

## [0.0.15] - 2025-02-21

### Fixed

- Removed duplicate error logs by using only logger (no print statements)

## [0.0.14] - 2025-02-21

### Changed

- Improved error handling:
  - Job now fails with non-zero exit code on errors
  - Disabled message acknowledgment on errors to allow retries
  - Added proper error propagation to Cloud Run Job status
- Removed filesystem permissions diagnostics code

## [0.0.13] - 2025-02-21

### Fixed

- Added ffmpeg installation to Docker image to support audio file processing

## [0.0.11] - 2025-02-21

### Fixed

- Changed compute_type to float32 for CPU devices to fix compatibility issue

## [0.0.10] - 2025-02-21

### Fixed

- Improved error logging configuration:
  - Added separate handlers for stdout and stderr
  - Errors are now properly logged to stderr with ERROR severity
  - Added direct error printing to stderr for better visibility in Cloud Run logs

## [0.0.9] - 2025-02-21

### Added

- Implemented WhisperX transcription with CPU/GPU support
- Added model loading from mounted GCS path (/models)
- Added environment variable USE_GPU for device selection
- Added saving transcription results to /models directory
- Added performance monitoring:
  - Transcription duration tracking (in minutes and seconds)
  - Memory usage monitoring
  - Detected language logging
  - Text size measurement in KiB

## [0.0.8] - 2025-02-21

### Fixed

- Removed redundant file download logging

## [0.0.7] - 2025-02-21

### Added

- Implemented file download from Google Drive to memory volume
- Added DriveClient class for handling Google Drive operations
- Added support for temporary storage in /tmp/transcriptions

## [0.0.6] - 2025-02-21

### Fixed

- Fixed Pub/Sub message processing to correctly handle ReceivedMessage structure

## [0.0.5] - 2025-02-21

### Fixed

- Fixed Pub/Sub message acknowledgment using the correct API method

## [0.0.4] - 2025-02-21

### Changed

- Updated Pub/Sub subscription name to match infrastructure configuration

## [0.0.3] - 2025-02-21

### Added

- Initial Cloud Run job configuration
- Basic Pub/Sub message processing

## [0.0.2] - 2025-02-21

### Added

- Initial service setup
- Basic project structure
- Cloud Build configuration
