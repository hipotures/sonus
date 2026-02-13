# Changelog

## [0.0.24] - 2025-02-25
### Changed
- Centralized configuration management:
  - Added config.py for centralized environment variables and constants
  - Moved all environment variables to config.py with proper defaults
  - Added GENERATED_EXTENSIONS and GENERATED_EXTENSIONS_TUPLE constants
  - Added helper functions for getting supported extensions and Pub/Sub config
- Improved file status checking:
  - Optimized Drive API queries by combining file checks
  - Added better status messages for different file types
  - Used constants for file extensions to ensure consistency

## [0.0.23] - 2025-02-24
### Changed
- Improved logging configuration:
  - Removed custom TRACE level in favor of standard logging levels
  - Added environment detection (local vs Cloud Run) using K_SERVICE
  - Configured proper console handler for local development
  - Simplified logging by using direct logger calls
  - Fixed double logging issues

## [0.0.22] - 2025-02-24
### Changed
- Updated logging levels: most logs moved to DEBUG level, keeping only Pub/Sub initialization and message content at INFO level

## [0.0.21] - 2025-02-24
### Added
- Added SERVICE_ACCOUNT_EMAIL environment variable for service account identification
### Changed
- Made PUBSUB_CONFIG configurable through Terraform variables

## [0.0.20] - 2025-02-23
### Fixed
- Fixed Cloud Build configuration by removing duplicate 'update' command
- Added .gitignore and removed __pycache__ files

## [0.0.19] - 2025-02-23
### Changed
- Added .err file checking in check_transcription_exists
- Updated logging to show when .err file is found
- Improved file status checking to handle all file types (.txt, .tmp, .err)

## [0.0.17] - 2025-02-21
### Changed
- Updated Drive API permissions query to get file owner instead of first permission
- Changed logging message to "File owned by" for clarity
- Modified scan_folder to iterate through permissions to find owner role

## [0.0.16] - 2025-02-21
### Added
- Added shared_by information to Pub/Sub messages
- Added detailed logging for Pub/Sub message publishing

## [0.0.15] - 2025-02-21
### Added
- Added detailed logging for Pub/Sub operations
- Added error handling and debug information for message publishing

## [0.0.14] - 2025-02-21
### Changed
- Updated Cloud Build configuration to use TAG_NAME for image versioning
- Fixed Cloud Run job version tagging

## [0.0.13] - 2025-02-21
### Added
- Integrated Pub/Sub support in activator.
- Added Terraform module for Pub/Sub with proper labels.
- Updated activator code to publish JSON messages for each media file without existing transcription.
- Updated requirements with Pub/Sub dependencies.

## [0.0.12] - 2025-02-21
### Added
- Uniwersalny system uwierzytelniania działający zarówno w Cloud Run jak i lokalnie
- Dodano dokumentację uruchamiania lokalnego w README.md
- Dodano obsługę zmiennej środowiskowej GOOGLE_APPLICATION_CREDENTIALS

## [0.0.11] - 2025-02-21
### Changed
- Zaktualizowano wersję Pythona do 3.11

## [0.0.10] - 2025-02-21
### Changed
- Uproszczono konfigurację Cloud Build do używania SHORT_SHA

## [0.0.9] - 2025-02-21
### Fixed
- Poprawiono sposób wersjonowania w Cloud Build

## [0.0.8] - 2025-02-21
### Changed
- Zmieniono sposób wersjonowania w Cloud Build na używanie wersji z taga Git

## [0.0.7] - 2025-02-21
### Changed
- Zmieniono sposób uwierzytelniania do Google Drive API na używanie domyślnych poświadczeń środowiska Cloud Run

## [0.0.6] - 2025-02-21
### Fixed
- Poprawiono sposób uwierzytelniania do Google Drive API
- Dodano brakujące zależności do Google API Client

## [0.0.5] - 2025-02-21
### Added
- Dodano uprawnienie iam.serviceAccountUser dla service account
- Poprawiono automatyczną aktualizację Cloud Run job

## [0.0.4] - 2025-02-21
### Added
- Dodano uprawnienie run.developer dla service account
- Poprawiono automatyczną aktualizację Cloud Run job po zbudowaniu nowej wersji

## [0.0.3] - 2025-02-21
### Added
- Automatyczna aktualizacja Cloud Run job po zbudowaniu nowej wersji
- Skanowanie folderów Google Drive w poszukiwaniu plików audio/video
- Sprawdzanie istnienia plików transkrypcji
- Logowanie znalezionych plików i statusu transkrypcji

### Changed
- Konfiguracja Cloud Build trigger na reagowanie na tagi
