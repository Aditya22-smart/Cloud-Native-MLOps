# Root outputs.tf

output "ingress_static_ip" {
  description = "Global static IP reserved for the GKE Ingress"
  value       = google_compute_global_address.ingress_ip.address
}

output "ingress_static_ip_name" {
  description = "Resource name of the global static IP"
  value       = google_compute_global_address.ingress_ip.name
}

output "network_name" {
  description = "The name of the VPC network"
  value       = module.vpc.network_name
}

output "subnet_name" {
  description = "The name of the primary subnet"
  value       = module.vpc.subnet_name
}

output "pods_range_name" {
  description = "Secondary IP range name for Kubernetes pods"
  value       = module.vpc.pods_range_name
}

output "services_range_name" {
  description = "Secondary IP range name for Kubernetes services"
  value       = module.vpc.services_range_name
}

output "gke_cluster_name" {
  description = "The name of the GKE cluster"
  value       = module.gke.cluster_name
}

output "gke_cluster_location" {
  description = "The zone of the GKE cluster"
  value       = module.gke.cluster_location
}

output "gke_cluster_endpoint" {
  description = "The Kubernetes control plane endpoint"
  value       = module.gke.cluster_endpoint
}

output "gke_node_service_account" {
  description = "The service account email attached to GKE nodes"
  value       = module.gke.node_service_account_email
}

output "pricing_app_service_account" {
  description = "The GCP service account email bound to Workload Identity for pricing-api pods"
  value       = google_service_account.pricing_app.email
}

output "jenkins_ci_service_account" {
  description = "The GCP service account email attached to Jenkins CI VM"
  value       = module.gce.jenkins_ci_service_account
}

output "gce_instance_names" {
  description = "Names of the provisioned GCE VMs"
  value       = module.gce.instance_names
}

output "gce_instance_internal_ips" {
  description = "Internal IP addresses of the provisioned GCE VMs"
  value       = module.gce.instance_internal_ips
}

output "artifact_registry_url" {
  description = "Base URL for Artifact Registry Docker repository"
  value       = module.artifact_registry.repository_url
}

output "models_bucket_name" {
  description = "Name of the ML models storage bucket"
  value       = module.gcs.models_bucket_name
}

output "datasets_bucket_name" {
  description = "Name of the datasets storage bucket"
  value       = module.gcs.datasets_bucket_name
}
