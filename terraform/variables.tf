variable "project_id" {
  description = "The ID of the GCP project"
  type        = string
  default     = "example-project-id"
}

variable "region" {
  description = "The region where resources will be created"
  type        = string
  default     = "REGION"
}

variable "activator_version" {
  description = "The version of the activator service"
  type        = string
  default     = "latest"
}

variable "transcriber_version" {
  description = "The version of the transcriber service"
  type        = string
  default     = "latest"
}

variable "debug_mode" {
  description = "Enable debug mode for the activator service"
  type        = bool
  default     = false
}

variable "audio_extensions" {
  description = "Comma-separated list of supported audio file extensions"
  type        = string
  default     = "mp3,wav,m4a,flac"
}

variable "video_extensions" {
  description = "Comma-separated list of supported video file extensions"
  type        = string
  default     = "mp4,mov,avi,mkv"
}

variable "service_account_name" {
  description = "Name of the service account for the activator service"
  type        = string
  default     = "sonus-transcription-sa"
}

variable "service_account_display_name" {
  description = "Display name of the service account"
  type        = string
  default     = "Sonus Transcription Service Account"
}

variable "repository_name" {
  description = "Name of the source code repository"
  type        = string
  default     = "sonus-activator"
}

variable "transcriber_repository_name" {
  description = "Name of the transcriber source code repository"
  type        = string
  default     = "sonus-transcriber"
}

variable "artifact_repository_name" {
  description = "Name of the Artifact Registry repository"
  type        = string
  default     = "sonus"
}

variable "build_trigger_name" {
  description = "Name of the Cloud Build trigger"
  type        = string
  default     = "activator-build"
}

variable "transcriber_trigger_name" {
  description = "Name of the Cloud Build trigger for transcriber"
  type        = string
  default     = "transcriber-build"
}

variable "build_branch_pattern" {
  description = "Branch pattern for triggering builds"
  type        = string
  default     = "^master$"
}

variable "labels" {
  description = "Labels to be applied to all resources"
  type = object({
    env    = string
    domain = string
    app    = string
  })
  default = {
    env    = "prod"
    domain = "ai"
    app    = "sonus"
  }
}
