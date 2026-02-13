# Create HF token secret
resource "google_secret_manager_secret" "hf_token" {
  secret_id = "hf-token"
  project   = var.project_id

  replication {
    user_managed {
      replicas {
        location = var.region
      }
    }
  }

  labels = var.labels
}

# Add initial version of the secret
resource "google_secret_manager_secret_version" "hf_token_version" {
  secret      = google_secret_manager_secret.hf_token.id
  secret_data = var.hf_token
}
