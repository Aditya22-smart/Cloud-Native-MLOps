variable "project_id" {
  description = "The GCP Project ID"
  type        = string
}

variable "zone" {
  description = "The GCP zone for the instances"
  type        = string
}

variable "environment" {
  description = "Deployment environment name (staging or prod)"
  type        = string
}

variable "subnet_id" {
  description = "Subnetwork ID for VM network interfaces"
  type        = string
}

variable "models_bucket_name" {
  description = "GCS models bucket name for CI IAM permissions"
  type        = string
}

variable "instances" {
  description = "Map of VM instances to provision (e.g. ci, elk)"
  type = map(object({
    machine_type     = string
    disk_size_gb     = number
    role             = string
    assign_public_ip = bool
  }))
  default = {
    ci = {
      machine_type     = "e2-standard-2"
      disk_size_gb     = 50
      role             = "ci"
      assign_public_ip = false
    }
    elk = {
      machine_type     = "e2-standard-2"
      disk_size_gb     = 50
      role             = "elk"
      assign_public_ip = false
    }
  }
}

variable "ssh_user" {
  description = "Admin SSH user for provisioning"
  type        = string
  default     = "aditya"
}

variable "ssh_public_key" {
  description = "Public SSH key for instances"
  type        = string
  default     = ""
}
