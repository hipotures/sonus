# Enable Artifact Registry API
resource "google_project_service" "artifactregistry" {
  service = "artifactregistry.googleapis.com"
  disable_on_destroy = false
}

# Create the Docker repository
resource "google_artifact_registry_repository" "sonus" {
  provider = google-beta
  project  = var.project_id
  location = var.region
  
  repository_id = var.repository_id
  description   = var.repository_description
  format        = "DOCKER"
  
  labels = var.labels

  depends_on = [google_project_service.artifactregistry]
}

# Grant the service account access to the repository
resource "google_artifact_registry_repository_iam_member" "service_account_access" {
  provider   = google-beta
  project    = var.project_id
  location   = var.region
  repository = google_artifact_registry_repository.sonus.name
  role       = "roles/artifactregistry.writer"
  member     = "serviceAccount:${var.service_account_email}"
}

# Grant Cloud Build service account access to the repository
resource "google_artifact_registry_repository_iam_member" "cloudbuild_access" {
  provider   = google-beta
  project    = var.project_id
  location   = var.region
  repository = google_artifact_registry_repository.sonus.name
  role       = "roles/artifactregistry.writer"
  member     = "serviceAccount:${var.project_number}@cloudbuild.gserviceaccount.com"
}

# Configure Docker authentication for Artifact Registry
resource "null_resource" "docker_auth" {
  provisioner "local-exec" {
    command = "gcloud auth configure-docker ${var.region}-docker.pkg.dev"
  }

  depends_on = [google_artifact_registry_repository.sonus]
}
