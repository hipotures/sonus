variable "project_id" {
  description = "The ID of the project"
  type        = string
}

variable "region" {
  description = "The region to create resources in"
  type        = string
}

variable "pubsub_config" {
  description = "Pub/Sub topic and subscription names"
  type = object({
    topic = string
    subscription = string
  })
  default = {
    topic = "sonus-pubsub-topic-test"
    subscription = "sonus-transcriber-sub-test"
  }
}
