output "job_name" {
  description = "The name of the Cloud Run job"
  value       = google_cloud_run_v2_job.job.name
}

output "job_id" {
  description = "The ID of the Cloud Run job"
  value       = google_cloud_run_v2_job.job.id
}

output "scheduler_name" {
  description = "The name of the Cloud Scheduler job"
  value       = google_cloud_scheduler_job.scheduler.name
}

output "scheduler_id" {
  description = "The ID of the Cloud Scheduler job"
  value       = google_cloud_scheduler_job.scheduler.id
}

output "job_location" {
  description = "The location of the Cloud Run job"
  value       = google_cloud_run_v2_job.job.location
}
