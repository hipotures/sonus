output "build_logs_bucket" {
  description = "The name of the bucket storing build logs"
  value       = google_storage_bucket.build_logs.name
}

output "test_reports_bucket" {
  description = "The name of the bucket storing test reports"
  value       = google_storage_bucket.test_reports.name
}

output "build_logs_bucket_url" {
  description = "The URL of the bucket storing build logs"
  value       = google_storage_bucket.build_logs.url
}

output "test_reports_bucket_url" {
  description = "The URL of the bucket storing test reports"
  value       = google_storage_bucket.test_reports.url
}
