variable "project_id" {
  description = "The GCP Project ID"
  type        = string
}

variable "region" {
  description = "The GCP region for the repository"
  type        = string
}

variable "environment" {
  description = "Deployment environment name"
  type        = string
}

variable "writer_service_accounts" {
  description = "Map of key-name to service account emails granted write access"
  type        = map(string)
  default     = {}
}

variable "reader_service_accounts" {
  description = "Map of key-name to service account emails granted read access"
  type        = map(string)
  default     = {}
}
