output "init_repo_id" {
  value = null_resource.init_repo.id
}

output "repository_id" {
  value = google_sourcerepo_repository.activator.id
}

output "repository_name" {
  value = google_sourcerepo_repository.activator.name
}

output "repository_url" {
  value = google_sourcerepo_repository.activator.url
}
