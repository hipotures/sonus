# Create the service account
resource "google_service_account" "transcription_sa" {
  account_id   = var.service_account_name
  display_name = var.service_account_display_name
  description  = "Service account for Sonus transcription services"
}

# Grant necessary roles to the service account
resource "google_project_iam_member" "sa_roles" {
  for_each = toset([
    "roles/run.invoker",              # Invoke Cloud Run services
    "roles/run.developer",            # Update Cloud Run jobs
    "roles/iam.serviceAccountUser",   # Use service accounts
    "roles/storage.objectViewer",     # Read from Cloud Storage
    "roles/storage.objectCreator",    # Create objects in Cloud Storage
    "roles/pubsub.publisher",         # Publish to Pub/Sub
    "roles/pubsub.subscriber",        # Subscribe to Pub/Sub topics
    "roles/source.reader",            # Read from Source Repositories
    "roles/artifactregistry.reader",  # Pull images from Artifact Registry
    "roles/logging.logWriter",        # Write logs
    "roles/monitoring.metricWriter",  # Write metrics
    "roles/cloudtrace.agent",         # Write traces
    "roles/viewer",                   # View project resources
    "roles/secretmanager.secretAccessor" # Access secrets
  ])

  project = var.project_id
  role    = each.key
  member  = "serviceAccount:${google_service_account.transcription_sa.email}"
}

# Grant the service account permission to be used by Cloud Run
resource "google_service_account_iam_member" "cloud_run_service_account_user" {
  service_account_id = google_service_account.transcription_sa.name
  role               = "roles/iam.serviceAccountUser"
  member             = "serviceAccount:${data.google_project.project.number}@cloudbuild.gserviceaccount.com"
  depends_on         = [google_project_service.required_apis]
}

# Create a service account key
resource "google_service_account_key" "sa_key" {
  service_account_id = google_service_account.transcription_sa.name
  private_key_type   = "TYPE_GOOGLE_CREDENTIALS_FILE"
  public_key_type    = "TYPE_X509_PEM_FILE"
}
