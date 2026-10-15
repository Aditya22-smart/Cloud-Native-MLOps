# Models GCS Bucket
resource "google_storage_bucket" "models" {
  name                        = "${var.project_id}-${var.environment}-models"
  location                    = var.region
  force_destroy               = var.force_destroy
  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }

  labels = {
    project = "pricing"
    env     = var.environment
    owner   = "aditya"
  }
}

# Datasets GCS Bucket
resource "google_storage_bucket" "datasets" {
  name                        = "${var.project_id}-${var.environment}-datasets"
  location                    = var.region
  force_destroy               = var.force_destroy
  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }

  labels = {
    project = "pricing"
    env     = var.environment
    owner   = "aditya"
  }
}

# IAM: Pod Identity SA gets objectAdmin on models bucket
resource "google_storage_bucket_iam_member" "models_admin" {
  for_each = var.pod_identity_service_accounts
  bucket   = google_storage_bucket.models.name
  role     = "roles/storage.objectAdmin"
  member   = "serviceAccount:${each.value}"
}
