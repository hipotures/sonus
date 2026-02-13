output "topic_name" {
  description = "The name of the Pub/Sub topic"
  value       = google_pubsub_topic.sonus_pubsub_topic.name
}

output "subscription_name" {
  description = "The name of the Pub/Sub subscription"
  value       = google_pubsub_subscription.sonus_transcriber_subscription.name
}

output "topic_id" {
  description = "The ID of the Pub/Sub topic"
  value       = google_pubsub_topic.sonus_pubsub_topic.id
}

output "subscription_id" {
  description = "The ID of the Pub/Sub subscription"
  value       = google_pubsub_subscription.sonus_transcriber_subscription.id
}

# Test outputs
output "test_topic_name" {
  description = "The name of the test Pub/Sub topic"
  value       = google_pubsub_topic.sonus_pubsub_topic_test.name
}

output "test_subscription_name" {
  description = "The name of the test Pub/Sub subscription"
  value       = google_pubsub_subscription.sonus_transcriber_subscription_test.name
}

output "test_topic_id" {
  description = "The ID of the test Pub/Sub topic"
  value       = google_pubsub_topic.sonus_pubsub_topic_test.id
}

output "test_subscription_id" {
  description = "The ID of the test Pub/Sub subscription"
  value       = google_pubsub_subscription.sonus_transcriber_subscription_test.id
}
