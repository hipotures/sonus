variable "project_id" {
  description = "The ID of the project where the repository will be created"
  type        = string
}

variable "region" {
  description = "The region where resources will be created"
  type        = string
}

variable "repo_name" {
  description = "Name of the repository"
  type        = string
  default     = "sonus-activator"
}

variable "initial_version" {
  description = "Initial version tag for the repository"
  type        = string
  default     = "0.0.1"
}

variable "service_account_email" {
  description = "Service account email that will be used for Cloud Build"
  type        = string
}

variable "project_number" {
  description = "The numeric ID of the GCP project"
  type        = string
}
