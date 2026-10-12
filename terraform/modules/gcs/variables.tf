variable "project_id" {
  description = "The GCP Project ID"
  type        = string
}

variable "region" {
  description = "The GCP region for the storage buckets"
  type        = string
}

variable "environment" {
  description = "Deployment environment name"
  type        = string
}

variable "force_destroy" {
  description = "Whether to allow force-destruction of bucket content upon terraform destroy"
  type        = bool
  default     = true
}

variable "pod_identity_service_accounts" {
  description = "List of GCP service account emails granted objectAdmin on models bucket"
  type        = list(string)
  default     = []
}
