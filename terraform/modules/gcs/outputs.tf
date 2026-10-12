output "models_bucket_name" {
  description = "Name of the ML models storage bucket"
  value       = google_storage_bucket.models.name
}

output "models_bucket_url" {
  description = "GCS URL of the ML models storage bucket"
  value       = google_storage_bucket.models.url
}

output "datasets_bucket_name" {
  description = "Name of the datasets storage bucket"
  value       = google_storage_bucket.datasets.name
}

output "datasets_bucket_url" {
  description = "GCS URL of the datasets storage bucket"
  value       = google_storage_bucket.datasets.url
}
