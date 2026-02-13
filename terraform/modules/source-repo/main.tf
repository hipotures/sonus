# Enable Cloud Source Repositories API
resource "google_project_service" "sourcerepo" {
  service = "sourcerepo.googleapis.com"
  disable_on_destroy = false
}

# Create the repository
resource "google_sourcerepo_repository" "activator" {
  name = var.repo_name
  project = var.project_id
  depends_on = [google_project_service.sourcerepo]
}

# Grant Cloud Build service account access to the repository
resource "google_sourcerepo_repository_iam_member" "cloudbuild_access" {
  project = var.project_id
  repository = google_sourcerepo_repository.activator.name
  role = "roles/source.reader"
  member = "serviceAccount:${var.service_account_email}"
}

# Grant Cloud Build service account access to the repository
resource "google_sourcerepo_repository_iam_member" "cloudbuild_service_account_access" {
  project = var.project_id
  repository = google_sourcerepo_repository.activator.name
  role = "roles/source.reader"
  member = "serviceAccount:${var.project_number}@cloudbuild.gserviceaccount.com"
}

# Initialize repository with code
resource "null_resource" "init_repo" {
  depends_on = [google_sourcerepo_repository.activator]

  triggers = {
    repository_id = google_sourcerepo_repository.activator.id
    version = var.initial_version
  }

  provisioner "local-exec" {
    command = <<-EOT
      # Create temporary directory
      TEMP_DIR=$(mktemp -d)
      
      # Copy source files
      cp -r ${path.module}/files/* $TEMP_DIR/
      
      # Initialize git repo
      cd $TEMP_DIR
      git init
      git config user.email "terraform@example.com"
      git config user.name "Terraform"
      
      # Add and commit files
      git add .
      git commit -m "Initial commit - version ${var.initial_version}"
      
      # Add remote and push
      git remote add origin https://source.developers.google.com/p/${var.project_id}/r/${var.repo_name}
      
      # Configure git credential helper for GCP
      git config credential.helper gcloud.sh
      
      # Push to master
      git push origin master
      
      # Cleanup
      cd ..
      rm -rf $TEMP_DIR
    EOT
  }
}
