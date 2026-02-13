# Project Context: Sonus

## Overview
Sonus is an automated transcription and diarization pipeline deployed on Google Cloud Platform. It uses WhisperX for processing audio/video files.

## Core Components

### 1. Infrastructure (`terraform/`)
- **Tool:** OpenTofu / Terraform.
- **State:** Managed manually or via GCS backend (currently configured for `example-terraform-state`).
- **Key Resources:**
    - `google_cloud_run_v2_job`: For `activator` and `transcriber`.
    - `google_pubsub_topic`: For messaging queue.
    - `google_storage_bucket`: For logs, reports, and models.
- **Variables:** Defined in `terraform/variables.tf`. Default `project_id` is `example-project-id`.

### 2. Activator (`sonus-activator/`)
- **Role:** The "Producer".
- **Function:** Scans for files to process (e.g., from Google Drive) and pushes metadata messages to Pub/Sub.
- **Runtime:** Python 3.11, Cloud Run Job (Scheduled).

### 3. Transcriber (`sonus-transcriber/`)
- **Role:** The "Consumer" / Worker.
- **Function:** Pulls messages from Pub/Sub, downloads the audio/video, runs WhisperX (transcription + diarization), and uploads the result.
- **Runtime:** Python 3.11, Cloud Run Job (triggered or polled).
- **Libraries:** `whisperx`, `torch`, `google-cloud-pubsub`, `google-cloud-storage`.

## Development Guidelines

### Anonymization Rules
- **Project ID:** Always use `example-project-id` in code/docs.
- **Region:** Always use `REGION` or `example-region` in code/docs.
- **Domain:** Always use `example.com`.
- **Emails:** Use `user@example.com` or `sa-name@example-project-id.iam.gserviceaccount.com`.

### Testing
- **Framework:** `pytest`.
- **Location:** `tests/` folders in each service directory.
- **Commands:**
    ```bash
    pytest sonus-transcriber/tests
    pytest sonus-activator/tests
    ```

### Deployment Workflow
1.  **Infrastructure:** Update `.tf` files in `terraform/`, then `tofu apply`.
2.  **Code:** Update Python code, build Docker image via Cloud Build, push to Artifact Registry.
3.  **Update Jobs:** Update Cloud Run Jobs to use the new image tag (if not using `latest`).

## Key Files
- `docs/StepByStep.md`: The comprehensive manual for deployment and architecture.
- `terraform/variables.tf`: Main infrastructure configuration.
- `terraform/modules/cloud-run/main.tf`: Definition of the container runtime environment.

## Common Issues
- **GPU:** WhisperX benefits heavily from GPU. Current config might default to CPU for cost; ensure `torch` is compatible with the target runtime.
- **Timeouts:** Long audio files might exceed Cloud Run timeouts. Check `execution_timeout` in Terraform.
