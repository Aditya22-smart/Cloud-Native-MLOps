# Docker-format repository: pricing
resource "google_artifact_registry_repository" "pricing" {
  provider      = google-beta
  project       = var.project_id
  location      = var.region
  repository_id = "pricing"
  description   = "Docker container repository for Dynamic Pricing microservices"
  format        = "DOCKER"

  labels = {
    project = "pricing"
    env     = var.environment
    owner   = "aditya"
  }
}

# Writer IAM bindings (e.g. Jenkins CI service account)
resource "google_artifact_registry_repository_iam_member" "writers" {
  for_each   = var.writer_service_accounts
  project    = var.project_id
  location   = google_artifact_registry_repository.pricing.location
  repository = google_artifact_registry_repository.pricing.name
  role       = "roles/artifactregistry.writer"
  member     = "serviceAccount:${each.value}"
}

# Reader IAM bindings (e.g. GKE Node service account)
resource "google_artifact_registry_repository_iam_member" "readers" {
  for_each   = var.reader_service_accounts
  project    = var.project_id
  location   = google_artifact_registry_repository.pricing.location
  repository = google_artifact_registry_repository.pricing.name
  role       = "roles/artifactregistry.reader"
  member     = "serviceAccount:${each.value}"
}
