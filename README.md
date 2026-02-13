# Sonus - Automated Transcription System

Sonus is a scalable, cloud-native automated transcription and diarization system built on Google Cloud Platform (GCP). It utilizes **WhisperX** to provide high-accuracy speech-to-text conversion with speaker identification (diarization).

## 🚀 Features

*   **High Accuracy:** Uses OpenAI's Whisper model via WhisperX for state-of-the-art recognition.
*   **Speaker Diarization:** Automatically identifies and separates different speakers.
*   **Scalable Architecture:** Built on GCP Cloud Run Jobs to handle variable workloads cost-effectively.
*   **Event-Driven:** Uses Pub/Sub for asynchronous task processing.
*   **Infrastructure as Code:** Fully managed via Terraform/OpenTofu.
*   **Format Support:** Handles various audio (mp3, wav, m4a, flac) and video (mp4, mov, avi, mkv) formats.

## 🏗 Architecture

The system consists of two main components:

1.  **Activator:** A scheduled job that scans sources (e.g., Google Drive) for new files and publishes tasks to Pub/Sub.
2.  **Transcriber:** A worker job triggered by Pub/Sub messages that processes the audio/video files using WhisperX and saves the results.

```mermaid
graph LR
    Source[Source (e.g., Drive)] --> Activator[Activator (Cloud Run)]
    Activator --> Topic[Pub/Sub Topic]
    Topic --> Transcriber[Transcriber (Cloud Run)]
    Transcriber --> Storage[Storage (Output)]
```

## 📂 Project Structure

*   `sonus-activator/`: Source code for the trigger service.
*   `sonus-transcriber/`: Source code for the WhisperX processing service.
*   `terraform/`: Infrastructure configuration (Terraform/OpenTofu).
*   `docs/`: Detailed technical documentation.
*   `examples/`: Sample scripts and files for testing.

## 🛠️ Prerequisites

*   **Google Cloud Platform Account**
*   **Terraform** or **OpenTofu**
*   **Docker**
*   **Python 3.11+**
*   **GCP CLI (`gcloud`)**

## 📦 Installation & Deployment

### 1. Configuration
Navigate to the `terraform/` directory and configure your variables. You can create a `terraform.tfvars` file:

```hcl
project_id = "your-gcp-project-id"
region     = "your-preferred-region" # e.g., europe-west1
```

### 2. Infrastructure Deployment
Initialize and apply the Terraform configuration:

```bash
cd terraform
tofu init
tofu apply
```

This will create:
*   Artifact Registry repositories
*   Cloud Run Jobs (Activator & Transcriber)
*   Cloud Storage Buckets
*   Pub/Sub Topics and Subscriptions
*   Service Accounts and IAM roles

### 3. Service Deployment
Build and push the Docker images for both services:

```bash
# Example for Activator
cd sonus-activator
gcloud builds submit --tag REGION-docker.pkg.dev/PROJECT_ID/sonus/activator:latest .

# Example for Transcriber
cd sonus-transcriber
gcloud builds submit --tag REGION-docker.pkg.dev/PROJECT_ID/sonus/transcriber:latest .
```

## 💻 Local Development

### Setup
1.  Create a virtual environment:
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```
2.  Install dependencies:
    ```bash
    pip install -r sonus-activator/requirements.txt
    pip install -r sonus-transcriber/requirements.txt
    ```

### Running Tests
The project uses `pytest`.

```bash
# Run Activator tests
pytest sonus-activator/tests

# Run Transcriber tests
pytest sonus-transcriber/tests
```

## 📄 Documentation

For a detailed deep-dive into the setup, configuration variables, and troubleshooting, please refer to the **[StepByStep Guide](docs/StepByStep.md)**.

## ⚖️ License

CC0 1.0 Universal (Public Domain)
