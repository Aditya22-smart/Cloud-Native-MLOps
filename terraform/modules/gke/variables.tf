variable "project_id" {
  description = "The GCP Project ID"
  type        = string
}

variable "region" {
  description = "The GCP region for the GKE cluster"
  type        = string
}

variable "zone" {
  description = "The GCP zone for the GKE cluster"
  type        = string
}

variable "environment" {
  description = "Deployment environment name (staging or prod)"
  type        = string
}

variable "network_id" {
  description = "The VPC network ID"
  type        = string
}

variable "subnet_id" {
  description = "The primary subnetwork ID"
  type        = string
}

variable "pods_range_name" {
  description = "Secondary range name for Pods"
  type        = string
}

variable "services_range_name" {
  description = "Secondary range name for Services"
  type        = string
}

variable "master_authorized_cidrs" {
  description = "List of CIDR blocks authorized to access Kubernetes master API"
  type = list(object({
    cidr_block   = string
    display_name = string
  }))
  default = []
}

variable "machine_type" {
  description = "GKE Node machine type"
  type        = string
  default     = "e2-standard-2"
}

variable "min_node_count" {
  description = "Minimum nodes in node pool autoscaling"
  type        = number
  default     = 1
}

variable "max_node_count" {
  description = "Maximum nodes in node pool autoscaling"
  type        = number
  default     = 3
}

variable "deletion_protection" {
  description = "Prevent accidental deletion of the cluster (false for staging, true for prod)"
  type        = bool
  default     = false
}
