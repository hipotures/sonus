# Enable required APIs
resource "google_project_service" "apis" {
  for_each = toset([
    "cloudbuild.googleapis.com",
    "sourcerepo.googleapis.com"
  ])
  
  service = each.key
  disable_on_destroy = false
}

# Create a bucket for build artifacts
resource "google_storage_bucket" "build_artifacts" {
  name     = "sonus-build-artifacts"
  location = var.region
  
  uniform_bucket_level_access = true
  force_destroy = true
  
  labels = var.labels

  lifecycle_rule {
    condition {
      age = 30  # days
    }
    action {
      type = "Delete"
    }
  }
}

# Create the Cloud Build trigger for activator
resource "google_cloudbuild_trigger" "activator_build" {
  name        = var.trigger_name
  description = "Trigger for building the activator service"
  location    = var.region
  filename    = "cloudbuild.yaml"

  trigger_template {
    project_id = var.project_id
    repo_name = var.repository_name
    tag_name = "v*"
  }

  service_account = "projects/${var.project_id}/serviceAccounts/${var.service_account_email}"  # Full service account path

  substitutions = {
    _VERSION  = var.initial_version
    _REGISTRY = "${var.artifact_registry_location}-docker.pkg.dev/${var.project_id}/${var.artifact_registry_repository}"
    _REGION   = var.region
  }

  depends_on = [
    google_project_service.apis,
    google_storage_bucket.build_artifacts,
  ]
}

# Create the Cloud Build trigger for transcriber
resource "google_cloudbuild_trigger" "transcriber_build" {
  name        = var.transcriber_trigger_name
  description = "Trigger for building the transcriber service"
  location    = var.region
  filename    = "cloudbuild.yaml"

  trigger_template {
    project_id = var.project_id
    repo_name = var.transcriber_repository_name
    tag_name = "v*"
  }

  service_account = "projects/${var.project_id}/serviceAccounts/${var.service_account_email}"  # Full service account path

  substitutions = {
    _VERSION  = var.initial_version
    _REGISTRY = "${var.artifact_registry_location}-docker.pkg.dev/${var.project_id}/${var.artifact_registry_repository}"
    _REGION   = var.region
  }

  depends_on = [
    google_project_service.apis,
    google_storage_bucket.build_artifacts,
  ]
}

# Grant Cloud Build service account access to Artifact Registry
resource "google_project_iam_member" "cloudbuild_artifactregistry" {
  project = var.project_id
  role    = "roles/artifactregistry.writer"
  member  = "serviceAccount:${var.project_number}@cloudbuild.gserviceaccount.com"
}

# Grant Cloud Build service account access to Cloud Storage
resource "google_project_iam_member" "cloudbuild_storage" {
  project = var.project_id
  role    = "roles/storage.admin"
  member  = "serviceAccount:${var.project_number}@cloudbuild.gserviceaccount.com"
}

# Grant Cloud Build service account access to run services
resource "google_project_iam_member" "cloudbuild_run" {
  project = var.project_id
  role    = "roles/run.admin"
  member  = "serviceAccount:${var.project_number}@cloudbuild.gserviceaccount.com"
}

# Grant Cloud Build service account access to use service accounts
resource "google_project_iam_member" "cloudbuild_serviceaccount" {
  project = var.project_id
  role    = "roles/iam.serviceAccountUser"
  member  = "serviceAccount:${var.project_number}@cloudbuild.gserviceaccount.com"
}
