provider "google" {
  project = var.project_id
  region  = var.region
}

provider "google-beta" {
  project = var.project_id
  region  = var.region
}

# Configure the backend to store state in Cloud Storage
# Uncomment and configure once the bucket is created
# terraform {
#   backend "gcs" {
#     bucket = "example-terraform-state"
#     prefix = "sonus/activator"
#   }
# }
