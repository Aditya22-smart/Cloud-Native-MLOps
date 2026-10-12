variable "project_id" {
  description = "The GCP Project ID"
  type        = string
}

variable "region" {
  description = "The GCP region for the VPC and subnet"
  type        = string
}

variable "environment" {
  description = "Environment name (e.g. staging, prod)"
  type        = string
}

variable "subnet_cidr" {
  description = "Primary IP range for the subnet"
  type        = string
}

variable "pods_subnet_cidr" {
  description = "Secondary IP range for GKE Pods"
  type        = string
}

variable "services_subnet_cidr" {
  description = "Secondary IP range for GKE Services"
  type        = string
}
