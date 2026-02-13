output "service_account_email" {
  description = "The email of the service account"
  value       = google_service_account.transcription_sa.email
}

output "source_repository_url" {
  description = "The URL of the source code repository"
  value       = module.source_repo.repository_url
}

output "artifact_registry_path" {
  description = "The path to the container registry"
  value       = module.artifact_registry.repository_url
}

output "activator_image" {
  description = "The full path to the activator container image"
  value       = "${module.artifact_registry.image_path}/activator:${var.activator_version}"
}

output "transcriber_image" {
  description = "The full path to the transcriber container image"
  value       = "${module.artifact_registry.image_path}/transcriber:${var.transcriber_version}"
}

output "build_trigger_url" {
  description = "The URL to view the build trigger in Cloud Console"
  value       = module.cloud_build.build_trigger_url
}

output "activator_job_name" {
  description = "The name of the deployed activator Cloud Run job"
  value       = module.cloud_run_activator.job_name
}

output "activator_scheduler_name" {
  description = "The name of the activator Cloud Scheduler job"
  value       = module.cloud_run_activator.scheduler_name
}

output "build_artifacts_bucket" {
  description = "The name of the bucket storing build artifacts"
  value       = module.cloud_build.artifacts_bucket
}

output "build_logs_bucket" {
  description = "The name of the bucket storing build logs"
  value       = module.storage.build_logs_bucket
}

output "test_reports_bucket" {
  description = "The name of the bucket storing test reports"
  value       = module.storage.test_reports_bucket
}

output "service_account_key" {
  description = "The service account key (sensitive)"
  value       = google_service_account_key.sa_key.private_key
  sensitive   = true
}

output "next_steps" {
  description = "Next steps to complete the setup"
  value       = <<EOT
Setup completed successfully! Next steps:

1. Initialize the source repositories:
   gcloud source repos clone ${module.source_repo.repository_name} --project=${var.project_id}
   gcloud source repos clone sonus-transcriber --project=${var.project_id}

2. Push initial code for activator:
   cd ${module.source_repo.repository_name}
   git add .
   git commit -m "Initial commit"
   git push origin main

3. Push initial code for transcriber:
   cd ../sonus-transcriber
   git add .
   git commit -m "Initial commit"
   git push origin main

4. Monitor the builds:
   ${module.cloud_build.build_trigger_url}

5. View the deployed jobs in Cloud Console:
   Activator: https://console.cloud.google.com/run/jobs/details/${var.region}/${module.cloud_run_activator.job_name}?project=${var.project_id}

6. Save the service account key (will be shown after apply):
   terraform output -raw service_account_key | base64 -d > sonus-sa-key.json
EOT
}
