variable "project_id" {
  description = "The ID of the project where the registry will be created"
  type        = string
}

variable "project_number" {
  description = "The numeric ID of the GCP project"
  type        = string
}

variable "region" {
  description = "The region where the registry will be created"
  type        = string
}

variable "repository_id" {
  description = "The ID of the registry repository"
  type        = string
  default     = "sonus"
}

variable "repository_description" {
  description = "The description of the registry repository"
  type        = string
  default     = "Container registry for Sonus application"
}

variable "service_account_email" {
  description = "Service account email that will be granted access to the registry"
  type        = string
}

variable "labels" {
  description = "Labels to be applied to resources"
  type = object({
    env    = string
    domain = string
    app    = string
  })
}
