output "instance_names" {
  description = "Map of instance names"
  value       = { for k, v in google_compute_instance.vm : k => v.name }
}

output "instance_internal_ips" {
  description = "Map of instance internal IPs"
  value       = { for k, v in google_compute_instance.vm : k => v.network_interface[0].network_ip }
}

output "jenkins_ci_service_account" {
  description = "Service account email attached to Jenkins CI host"
  value       = google_service_account.jenkins_ci.email
}
