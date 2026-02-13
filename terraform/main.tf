# Get project information
data "google_project" "project" {
  project_id = var.project_id
}

# Configure required providers
terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 6.0"
    }
    time = {
      source  = "hashicorp/time"
      version = "~> 0.10.0"
    }
  }
}

# Enable required APIs
resource "google_project_service" "required_apis" {
  for_each = toset([
    "cloudbuild.googleapis.com",
    "drive.googleapis.com",
    "pubsub.googleapis.com",
    "secretmanager.googleapis.com"
  ])
  
  service = each.key
  disable_on_destroy = false
}

# Wait for service accounts to be created
resource "time_sleep" "wait_for_apis" {
  depends_on = [google_project_service.required_apis]
  create_duration = "30s"
}

# Create storage buckets and configure access
module "storage" {
  source = "./modules/storage"

  project_id            = var.project_id
  region               = var.region
  cloudbuild_sa_email  = "${data.google_project.project.number}@cloudbuild.gserviceaccount.com"
  service_account_email = google_service_account.transcription_sa.email
  labels               = var.labels

  depends_on = [
    google_service_account.transcription_sa,
    time_sleep.wait_for_apis
  ]
}

# Create source code repository
module "source_repo" {
  source = "./modules/source-repo"

  project_id           = var.project_id
  project_number       = data.google_project.project.number
  region              = var.region
  repo_name           = var.repository_name
  initial_version     = var.activator_version
  service_account_email = google_service_account.transcription_sa.email

  depends_on = [
    google_service_account.transcription_sa,
    time_sleep.wait_for_apis
  ]
}

# Create Artifact Registry repository
module "artifact_registry" {
  source = "./modules/artifact-registry"

  project_id              = var.project_id
  project_number          = data.google_project.project.number
  region                 = var.region
  repository_id          = var.artifact_repository_name
  repository_description = "Container registry for Sonus application"
  service_account_email  = google_service_account.transcription_sa.email
  labels                = var.labels

  depends_on = [
    google_service_account.transcription_sa,
    time_sleep.wait_for_apis
  ]
}

# Configure Cloud Build
module "cloud_build" {
  source                      = "./modules/cloud-build"
  project_id                  = var.project_id
  project_number             = data.google_project.project.number
  region                     = var.region
  repository_id              = module.source_repo.repository_id
  repository_name            = module.source_repo.repository_name
  artifact_registry_location = var.region
  artifact_registry_repository = module.artifact_registry.repository_name
  service_account_email      = google_service_account.transcription_sa.email
  initial_version           = var.activator_version
  trigger_name             = var.build_trigger_name
  transcriber_trigger_name = var.transcriber_trigger_name
  transcriber_repository_name = var.transcriber_repository_name
  branch_pattern          = var.build_branch_pattern
  labels                  = var.labels

  depends_on = [
    module.source_repo.init_repo_id,
    module.artifact_registry,
  ]
}

# Create Pub/Sub topic and subscription
module "pubsub" {
  source = "./modules/pubsub"

  project_id = var.project_id
  region     = var.region

  depends_on = [
    time_sleep.wait_for_apis
  ]
}

# Create Cloud Run job for activator
module "cloud_run_activator" {
  source = "./modules/cloud-run"

  project_id            = var.project_id
  region               = var.region
  service_account_email = google_service_account.transcription_sa.email
  image                = "${module.artifact_registry.image_path}/activator:${var.activator_version}"
  debug_mode           = var.debug_mode
  audio_extensions     = var.audio_extensions
  video_extensions     = var.video_extensions
  job_name             = "activator"
  schedule             = "11 * * * *"  # Every hour at minute 11
  labels               = var.labels

  depends_on = [
    module.cloud_build
  ]
}

  # Create Cloud Run job for transcriber
module "cloud_run_transcriber" {
  source = "./modules/cloud-run"

  project_id            = var.project_id
  region               = var.region
  service_account_email = google_service_account.transcription_sa.email
  image                = "${module.artifact_registry.image_path}/transcriber:${var.transcriber_version}"
  debug_mode           = var.debug_mode
  job_name             = "transcriber"
  schedule             = "23 */1 * * *"
  labels               = var.labels
  
  # Specific requirements for transcriber
  cpu                  = "8000m"         # 8 CPU
  memory               = "32Gi"          # 32 GiB
  execution_timeout    = "21600s"        # 6 hours
  max_retries          = 0               # No retries, as we handle retries through activator

  # Volume configuration
  enable_memory_volume = true
  memory_volume_size   = "1Gi"
  enable_gcs_volume    = true
  gcs_bucket_name      = "sonus-whisperx-models"

  # Secret configuration
  hf_token_secret      = "hf-token"      # Name of the secret containing HF token

  depends_on = [
    module.cloud_build,
    module.storage,
    module.secrets
  ]
}

# Create secrets
module "secrets" {
  source = "./modules/secrets"

  project_id = var.project_id
  region     = var.region
  labels     = var.labels

  depends_on = [
    time_sleep.wait_for_apis
  ]
}
