output "network_id" {
  description = "The ID of the VPC network"
  value       = google_compute_network.vpc.id
}

output "network_name" {
  description = "The name of the VPC network"
  value       = google_compute_network.vpc.name
}

output "subnet_id" {
  description = "The ID of the primary subnet"
  value       = google_compute_subnetwork.subnet.id
}

output "subnet_name" {
  description = "The name of the primary subnet"
  value       = google_compute_subnetwork.subnet.name
}

output "pods_range_name" {
  description = "The secondary range name for pods"
  value       = "pricing-${var.environment}-pods"
}

output "services_range_name" {
  description = "The secondary range name for services"
  value       = "pricing-${var.environment}-services"
}
