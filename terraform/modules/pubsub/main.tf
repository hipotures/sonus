# Production resources
resource "google_pubsub_topic" "sonus_pubsub_topic" {
  name = "sonus-pubsub-topic"
  labels = {
    env      = "prod"
    domain   = "ai"
    app      = "sonus"
    component = "pubsub"
  }
}

resource "google_pubsub_subscription" "sonus_transcriber_subscription" {
  name  = "sonus-transcriber-sub"
  topic = google_pubsub_topic.sonus_pubsub_topic.name

  ack_deadline_seconds = 600  # Maximum allowed: 10 minutes
  retain_acked_messages = true  # Required for message retention to work
  message_retention_duration = "604800s"  # 7 days in seconds
  expiration_policy {
    ttl = ""  # Subscription never expires
  }
  enable_message_ordering = false

  labels = {
    env      = "prod"
    domain   = "ai"
    app      = "sonus"
    component = "pubsub"
  }
}

# Test resources (always created for testing purposes)
resource "google_pubsub_topic" "sonus_pubsub_topic_test" {
  name = "sonus-pubsub-topic-test"
  labels = {
    env      = "test"
    domain   = "ai"
    app      = "sonus"
    component = "pubsub"
  }
}

resource "google_pubsub_subscription" "sonus_transcriber_subscription_test" {
  name  = "sonus-transcriber-sub-test"
  topic = google_pubsub_topic.sonus_pubsub_topic_test.name

  ack_deadline_seconds = 600  # Maximum allowed: 10 minutes
  retain_acked_messages = true  # Required for message retention to work
  message_retention_duration = "3600s"  # 1 hour in seconds for test queue
  expiration_policy {
    ttl = ""  # Subscription never expires
  }
  enable_message_ordering = false

  labels = {
    env      = "test"
    domain   = "ai"
    app      = "sonus"
    component = "pubsub"
  }
}
