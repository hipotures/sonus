# Enable Cloud Scheduler API
resource "google_project_service" "cloudscheduler_api" {
  project = var.project_id
  service = "cloudscheduler.googleapis.com"
  disable_on_destroy = false
}

# Create Cloud Run job
resource "google_cloud_run_v2_job" "job" {
  name     = var.job_name
  location = var.region
  deletion_protection = false
  
  labels = var.labels
  
  template {
    parallelism = var.parallelism
    template {
      dynamic "volumes" {
        for_each = var.enable_memory_volume ? [1] : []
        content {
          name = "work"
          empty_dir {
            medium = "MEMORY"
            size_limit = var.memory_volume_size
          }
        }
      }

      dynamic "volumes" {
        for_each = var.enable_gcs_volume ? [1] : []
        content {
          name = "whisperx-models"
          gcs {
            bucket = var.gcs_bucket_name
            read_only = false
          }
        }
      }

      containers {
        image = var.image
        
        resources {
          limits = {
            cpu    = var.cpu
            memory = var.memory
          }
        }

        env {
          name  = "PROJECT_ID"
          value = var.project_id
        }
        
        env {
          name  = "DEBUG"
          value = tostring(var.debug_mode)
        }
        
        env {
          name  = "AUDIO_EXTENSIONS"
          value = var.audio_extensions
        }
        
        env {
          name  = "VIDEO_EXTENSIONS"
          value = var.video_extensions
        }

        env {
          name  = "PUBSUB_CONFIG"
          value = var.pubsub_config
        }

        env {
          name  = "SERVICE_ACCOUNT_EMAIL"
          value = var.service_account_email
        }

        env {
          name = "HF_TOKEN"
          value_source {
            secret_key_ref {
              secret = var.hf_token_secret
              version = "latest"
            }
          }
        }

        dynamic "volume_mounts" {
          for_each = var.enable_memory_volume ? [1] : []
          content {
            name = "work"
            mount_path = "/tmp/sonus/work"
          }
        }

        dynamic "volume_mounts" {
          for_each = var.enable_gcs_volume ? [1] : []
          content {
            name = "whisperx-models"
            mount_path = "/models"
          }
        }
      }

      service_account = var.service_account_email
      timeout = var.execution_timeout
      max_retries = var.max_retries
    }
  }
}

# Create Cloud Scheduler job
resource "google_cloud_scheduler_job" "scheduler" {
  name             = "${var.job_name}-schedule"
  description      = "Triggers ${var.job_name} job ${var.schedule}"
  schedule         = var.schedule
  time_zone        = var.time_zone
  attempt_deadline = var.attempt_deadline
  region          = var.region

  http_target {
    http_method = "POST"
    uri         = "https://${var.region}-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/${var.project_id}/jobs/${google_cloud_run_v2_job.job.name}:run"
    
    oauth_token {
      service_account_email = var.service_account_email
    }
  }

  depends_on = [
    google_project_service.cloudscheduler_api,
    google_cloud_run_v2_job.job
  ]
}
