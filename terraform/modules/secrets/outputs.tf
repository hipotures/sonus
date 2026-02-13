output "hf_token_secret_id" {
  description = "The ID of the HF token secret"
  value       = google_secret_manager_secret.hf_token.id
}

output "hf_token_secret_name" {
  description = "The name of the HF token secret"
  value       = google_secret_manager_secret.hf_token.name
}
