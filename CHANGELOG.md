# Changelog

## [2025-02-20] Fix Cloud Build Configuration

### Problems Fixed

1. Cloud Build Trigger Creation Error:
   - Error: `INVALID_ARGUMENT: Request contains an invalid argument`
   - Fix: Updated Cloud Build trigger configuration to use `source_to_build` block instead of deprecated `trigger_template`
   - Changed in: `infrastructure/modules/cloud-build/main.tf`
   - Verification: Trigger created successfully
   - Configuration:
     ```yaml
     sourceToBuild:
       ref: refs/heads/master
       repoType: CLOUD_SOURCE_REPOSITORIES
       uri: https://source.developers.google.com/p/example-project-id/r/sonus-activator
     ```

2. Storage Access Error:
   - Error: `sonus-transcription-sa@example-project-id.iam.gserviceaccount.com does not have storage.objects.create access to the Google Cloud Storage object`

### Changes Made

1. Created required GCS buckets:
```bash
gsutil mb -l REGION gs://example-project-id-build-logs
gsutil mb -l REGION gs://example-project-id-test-reports
```

2. Granted permissions to service accounts:
```bash
# Grant permissions to Cloud Build service account
gsutil iam ch serviceAccount:PROJECT_NUMBER@cloudbuild.gserviceaccount.com:objectViewer,objectCreator gs://example-project-id-build-logs gs://example-project-id-test-reports

# Grant permissions to Sonus service account
gsutil iam ch serviceAccount:sonus-transcription-sa@example-project-id.iam.gserviceaccount.com:objectCreator,objectViewer gs://example-project-id-build-logs gs://example-project-id-test-reports
```

3. Fixed Python package structure:
   - Added `setup.py` at project root with proper package configuration
   - Configured package to use src-layout with `package_dir={"": "src"}`
   - Added required dependencies in `install_requires`

4. Updated Cloud Build configuration:
   - Modified `cloudbuild.yaml` to install package in development mode
   - Combined pip install and pytest steps to use same Python environment
   - Added proper working directory configuration for test execution

### Required Terraform Changes

The following resources need to be added to Terraform configuration:

1. GCS Buckets:
```hcl
resource "google_storage_bucket" "build_logs" {
  name          = "example-project-id-build-logs"
  location      = "REGION"
  force_destroy = true
}

resource "google_storage_bucket" "test_reports" {
  name          = "example-project-id-test-reports"
  location      = "REGION"
  force_destroy = true
}
```

2. IAM Permissions:
```hcl
resource "google_storage_bucket_iam_member" "cloudbuild_logs_access" {
  bucket = google_storage_bucket.build_logs.name
  role   = "roles/storage.objectViewer"
  member = "serviceAccount:${data.google_project.project.number}@cloudbuild.gserviceaccount.com"
}

resource "google_storage_bucket_iam_member" "cloudbuild_logs_creator" {
  bucket = google_storage_bucket.build_logs.name
  role   = "roles/storage.objectCreator"
  member = "serviceAccount:${data.google_project.project.number}@cloudbuild.gserviceaccount.com"
}

resource "google_storage_bucket_iam_member" "cloudbuild_reports_access" {
  bucket = google_storage_bucket.test_reports.name
  role   = "roles/storage.objectViewer"
  member = "serviceAccount:${data.google_project.project.number}@cloudbuild.gserviceaccount.com"
}

resource "google_storage_bucket_iam_member" "cloudbuild_reports_creator" {
  bucket = google_storage_bucket.test_reports.name
  role   = "roles/storage.objectCreator"
  member = "serviceAccount:${data.google_project.project.number}@cloudbuild.gserviceaccount.com"
}

resource "google_storage_bucket_iam_member" "sonus_logs_access" {
  bucket = google_storage_bucket.build_logs.name
  role   = "roles/storage.objectViewer"
  member = "serviceAccount:${google_service_account.transcription_sa.email}"
}

resource "google_storage_bucket_iam_member" "sonus_logs_creator" {
  bucket = google_storage_bucket.build_logs.name
  role   = "roles/storage.objectCreator"
  member = "serviceAccount:${google_service_account.transcription_sa.email}"
}

resource "google_storage_bucket_iam_member" "sonus_reports_access" {
  bucket = google_storage_bucket.test_reports.name
  role   = "roles/storage.objectViewer"
  member = "serviceAccount:${google_service_account.transcription_sa.email}"
}

resource "google_storage_bucket_iam_member" "sonus_reports_creator" {
  bucket = google_storage_bucket.test_reports.name
  role   = "roles/storage.objectCreator"
  member = "serviceAccount:${google_service_account.transcription_sa.email}"
}
