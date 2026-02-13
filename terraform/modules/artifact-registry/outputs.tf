output "repository_id" {
  description = "The ID of the created repository"
  value       = google_artifact_registry_repository.sonus.id
}

output "repository_name" {
  description = "The name of the created repository"
  value       = google_artifact_registry_repository.sonus.name
}

output "repository_location" {
  description = "The location of the repository"
  value       = google_artifact_registry_repository.sonus.location
}

output "repository_url" {
  description = "The URL of the repository"
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/${var.repository_id}"
}

output "image_path" {
  description = "The base path for container images in this repository"
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/${var.repository_id}"
}
