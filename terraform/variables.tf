variable "project_id" {
  description = "The GCP Project ID"
  type        = string
}

variable "region" {
  description = "The GCP region to deploy resources into"
  type        = string
  default     = "asia-south1"
}

variable "zone" {
  description = "The GCP zone for single-zone resources"
  type        = string
  default     = "asia-south1-a"
}

variable "environment" {
  description = "Deployment environment (staging or prod)"
  type        = string
  default     = "staging"
}

variable "owner" {
  description = "Resource owner identifier"
  type        = string
  default     = "aditya"
}

# Networking
variable "subnet_cidr" {
  description = "Primary CIDR block for the custom VPC subnet"
  type        = string
  default     = "10.10.0.0/20"
}

variable "pods_subnet_cidr" {
  description = "Secondary CIDR block for Kubernetes Pods"
  type        = string
  default     = "10.11.0.0/16"
}

variable "services_subnet_cidr" {
  description = "Secondary CIDR block for Kubernetes Services"
  type        = string
  default     = "10.12.0.0/20"
}

# Storage
variable "force_destroy" {
  description = "Allow destruction of buckets containing objects (recommended true for staging, false for prod)"
  type        = bool
  default     = true
}

# GKE Cluster
variable "master_authorized_cidrs" {
  description = "List of CIDR blocks authorized to access Kubernetes master API"
  type = list(object({
    cidr_block   = string
    display_name = string
  }))
  default = []
}

variable "gke_machine_type" {
  description = "GKE Node machine type"
  type        = string
  default     = "e2-standard-2"
}

variable "gke_min_nodes" {
  description = "Minimum nodes in node pool autoscaling"
  type        = number
  default     = 1
}

variable "gke_max_nodes" {
  description = "Maximum nodes in node pool autoscaling"
  type        = number
  default     = 3
}

variable "deletion_protection" {
  description = "Prevent accidental deletion of the cluster (false for staging, true for prod)"
  type        = bool
  default     = false
}
