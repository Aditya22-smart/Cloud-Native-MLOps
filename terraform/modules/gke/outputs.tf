output "cluster_name" {
  description = "The name of the GKE cluster"
  value       = google_container_cluster.primary.name
}

output "cluster_location" {
  description = "The location (zone) of the GKE cluster"
  value       = google_container_cluster.primary.location
}

output "cluster_endpoint" {
  description = "The IP address of the GKE cluster Kubernetes master"
  value       = google_container_cluster.primary.endpoint
}

output "node_service_account_email" {
  description = "The email of the dedicated GKE node service account"
  value       = google_service_account.gke_nodes.email
}
