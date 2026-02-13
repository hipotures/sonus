# Create GCS bucket for build logs
resource "google_storage_bucket" "build_logs" {
  name          = "sonus-build-logs"
  location      = var.region
  force_destroy = true

  uniform_bucket_level_access = true
  
  labels = var.labels
}

# Create GCS bucket for test reports
resource "google_storage_bucket" "test_reports" {
  name          = "sonus-test-reports"
  location      = var.region
  force_destroy = true

  uniform_bucket_level_access = true
  
  labels = var.labels
}

# Grant Cloud Build service account access to build logs bucket
resource "google_storage_bucket_iam_member" "cloudbuild_logs_access" {
  bucket = google_storage_bucket.build_logs.name
  role   = "roles/storage.objectViewer"
  member = "serviceAccount:${var.cloudbuild_sa_email}"
}

resource "google_storage_bucket_iam_member" "cloudbuild_logs_creator" {
  bucket = google_storage_bucket.build_logs.name
  role   = "roles/storage.objectCreator"
  member = "serviceAccount:${var.cloudbuild_sa_email}"
}

# Grant Cloud Build service account access to test reports bucket
resource "google_storage_bucket_iam_member" "cloudbuild_reports_access" {
  bucket = google_storage_bucket.test_reports.name
  role   = "roles/storage.objectViewer"
  member = "serviceAccount:${var.cloudbuild_sa_email}"
}

resource "google_storage_bucket_iam_member" "cloudbuild_reports_creator" {
  bucket = google_storage_bucket.test_reports.name
  role   = "roles/storage.objectCreator"
  member = "serviceAccount:${var.cloudbuild_sa_email}"
}

# Grant Sonus service account access to build logs bucket
resource "google_storage_bucket_iam_member" "sonus_logs_access" {
  bucket = google_storage_bucket.build_logs.name
  role   = "roles/storage.objectViewer"
  member = "serviceAccount:${var.service_account_email}"
}

resource "google_storage_bucket_iam_member" "sonus_logs_creator" {
  bucket = google_storage_bucket.build_logs.name
  role   = "roles/storage.objectCreator"
  member = "serviceAccount:${var.service_account_email}"
}

# Grant Sonus service account access to test reports bucket
resource "google_storage_bucket_iam_member" "sonus_reports_access" {
  bucket = google_storage_bucket.test_reports.name
  role   = "roles/storage.objectViewer"
  member = "serviceAccount:${var.service_account_email}"
}

resource "google_storage_bucket_iam_member" "sonus_reports_creator" {
  bucket = google_storage_bucket.test_reports.name
  role   = "roles/storage.objectCreator"
  member = "serviceAccount:${var.service_account_email}"
}

# Create GCS bucket for WhisperX models
resource "google_storage_bucket" "whisperx_models" {
  name          = "sonus-whisperx-models"
  location      = var.region
  force_destroy = true

  uniform_bucket_level_access = true
  
  labels = var.labels
}

# Grant Sonus service account access to WhisperX models bucket
resource "google_storage_bucket_iam_member" "sonus_whisperx_models_access" {
  bucket = google_storage_bucket.whisperx_models.name
  role   = "roles/storage.objectViewer"
  member = "serviceAccount:${var.service_account_email}"
}

resource "google_storage_bucket_iam_member" "sonus_whisperx_models_creator" {
  bucket = google_storage_bucket.whisperx_models.name
  role   = "roles/storage.objectCreator"
  member = "serviceAccount:${var.service_account_email}"
}

resource "google_storage_bucket_iam_member" "sonus_whisperx_models_writer" {
  bucket = google_storage_bucket.whisperx_models.name
  role   = "roles/storage.legacyBucketWriter"
  member = "serviceAccount:${var.service_account_email}"
}
