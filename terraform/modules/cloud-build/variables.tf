variable "project_id" {
  description = "The ID of the project where the Cloud Build trigger will be created"
  type        = string
}

variable "project_number" {
  description = "The numeric ID of the GCP project"
  type        = string
}

variable "region" {
  description = "The region where resources will be created"
  type        = string
}

variable "repository_id" {
  description = "The ID of the source repository"
  type        = string
}

variable "repository_name" {
  description = "The name of the source repository"
  type        = string
}

variable "artifact_registry_location" {
  description = "The location of the Artifact Registry repository"
  type        = string
}

variable "artifact_registry_repository" {
  description = "The name of the Artifact Registry repository"
  type        = string
}

variable "service_account_email" {
  description = "The email of the service account to use for Cloud Build"
  type        = string
}

variable "initial_version" {
  description = "The initial version tag for the container image"
  type        = string
  default     = "0.0.1"
}

variable "trigger_name" {
  description = "The name of the Cloud Build trigger"
  type        = string
  default     = "activator-build"
}

variable "transcriber_trigger_name" {
  description = "The name of the Cloud Build trigger for transcriber"
  type        = string
  default     = "transcriber-build"
}

variable "transcriber_repository_name" {
  description = "The name of the transcriber source repository"
  type        = string
  default     = "sonus-transcriber"
}

variable "branch_pattern" {
  description = "The branch pattern to trigger builds on"
  type        = string
  default     = "^master$"
}

variable "labels" {
  description = "Labels to be applied to resources"
  type = object({
    env    = string
    domain = string
    app    = string
  })
}
