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
  description = "List of service account emails granted write access"
  type        = list(string)
  default     = []
}

variable "reader_service_accounts" {
  description = "List of service account emails granted read access"
  type        = list(string)
  default     = []
}
