variable "project_id" {
  description = "The ID of the project"
  type        = string
}

variable "region" {
  description = "The region to create resources in"
  type        = string
}

variable "service_account_email" {
  description = "The email of the service account to run the job"
  type        = string
}

variable "image" {
  description = "The container image to run"
  type        = string
}

variable "debug_mode" {
  description = "Enable debug mode"
  type        = bool
  default     = false
}

variable "audio_extensions" {
  description = "Comma-separated list of supported audio extensions"
  type        = string
  default     = "mp3,wav,m4a,flac"
}

variable "video_extensions" {
  description = "Comma-separated list of supported video extensions"
  type        = string
  default     = "mp4,mov,avi,mkv"
}

variable "job_name" {
  description = "Name of the Cloud Run job"
  type        = string
}

variable "schedule" {
  description = "Cron schedule expression"
  type        = string
  default     = "11 * * * *"
}

variable "time_zone" {
  description = "Time zone for the scheduler"
  type        = string
  default     = "Europe/Warsaw"
}

variable "attempt_deadline" {
  description = "The deadline for job attempts"
  type        = string
  default     = "320s"
}

variable "labels" {
  description = "Labels to be applied to resources"
  type = object({
    env    = string
    domain = string
    app    = string
  })
}

variable "cpu" {
  description = "Number of CPU units for the job (e.g., 1000m for 1 CPU)"
  type        = string
  default     = "1000m"
}

variable "memory" {
  description = "Memory allocation for the job (e.g., 512Mi)"
  type        = string
  default     = "512Mi"
}

variable "execution_timeout" {
  description = "Maximum execution time for the job"
  type        = string
  default     = "3600s"  # 1 hour
}

variable "max_retries" {
  description = "Maximum number of retries for the job"
  type        = number
  default     = 3
}

variable "hf_token_secret" {
  description = "Name of the secret containing Hugging Face token"
  type        = string
  default     = "hf-token"
}

variable "enable_memory_volume" {
  description = "Enable in-memory volume for temporary storage"
  type        = bool
  default     = false
}

variable "memory_volume_size" {
  description = "Size of the in-memory volume (e.g., 1Gi)"
  type        = string
  default     = "1Gi"
}

variable "enable_gcs_volume" {
  description = "Enable GCS volume mount"
  type        = bool
  default     = false
}

variable "gcs_bucket_name" {
  description = "Name of the GCS bucket to mount"
  type        = string
  default     = ""
}

variable "parallelism" {
  description = "Maximum number of tasks that can run in parallel"
  type        = number
  default     = 4  # Maximum 4 parallel tasks
}

variable "pubsub_topic" {
  description = "Name of the Pub/Sub topic to use"
  type        = string
  default     = ""
}

variable "pubsub_subscription" {
  description = "Name of the Pub/Sub subscription to use"
  type        = string
  default     = ""
}

variable "pubsub_config" {
  description = "PubSub configuration in format 'topic|subscription'"
  type        = string
  default     = "sonus-pubsub-topic|sonus-transcriber-sub"
}
