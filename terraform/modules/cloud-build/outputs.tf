output "trigger_id" {
  description = "The ID of the created Cloud Build trigger"
  value       = google_cloudbuild_trigger.activator_build.id
}

output "trigger_name" {
  description = "The name of the created Cloud Build trigger"
  value       = google_cloudbuild_trigger.activator_build.name
}

output "artifacts_bucket" {
  description = "The name of the bucket storing build artifacts"
  value       = google_storage_bucket.build_artifacts.name
}

output "build_service_account" {
  description = "The service account used by Cloud Build"
  value       = "${var.project_id}@cloudbuild.gserviceaccount.com"
}

output "build_trigger_url" {
  description = "The URL to view the build trigger in the Cloud Console"
  value       = "https://console.cloud.google.com/cloud-build/triggers;region=${var.region}/edit/${google_cloudbuild_trigger.activator_build.id}?project=${var.project_id}"
}

output "registry_path" {
  description = "The full path to the container registry"
  value       = "${var.artifact_registry_location}-docker.pkg.dev/${var.project_id}/${var.artifact_registry_repository}"
}
