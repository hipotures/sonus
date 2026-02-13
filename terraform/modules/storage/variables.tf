variable "project_id" {
  description = "The ID of the project"
  type        = string
}

variable "region" {
  description = "The region to create resources in"
  type        = string
}

variable "cloudbuild_sa_email" {
  description = "The email of the Cloud Build service account"
  type        = string
}

variable "service_account_email" {
  description = "The email of the service account to grant access to"
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
