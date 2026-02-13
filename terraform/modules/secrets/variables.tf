variable "project_id" {
  description = "The ID of the project"
  type        = string
}

variable "region" {
  description = "The region to create resources in"
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

variable "hf_token" {
  description = "Hugging Face token value"
  type        = string
  default     = "hf_...."
}
