output "repository_id" {
  description = "The repository ID"
  value       = google_artifact_registry_repository.pricing.repository_id
}

output "repository_name" {
  description = "The fully qualified name of the repository"
  value       = google_artifact_registry_repository.pricing.name
}

output "repository_url" {
  description = "Docker image repository URL base"
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.pricing.repository_id}"
}
