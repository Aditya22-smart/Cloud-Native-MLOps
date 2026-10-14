# Dedicated Service Account for CI host: jenkins-ci-<env>
resource "google_service_account" "jenkins_ci" {
  account_id   = "jenkins-ci-${var.environment}"
  display_name = "Jenkins CI Runner Service Account (${var.environment})"
  project      = var.project_id
}

# CI Service Account IAM grants
resource "google_project_iam_member" "ci_artifact_writer" {
  project = var.project_id
  role    = "roles/artifactregistry.writer"
  member  = "serviceAccount:${google_service_account.jenkins_ci.email}"
}

resource "google_project_iam_member" "ci_container_developer" {
  project = var.project_id
  role    = "roles/container.developer"
  member  = "serviceAccount:${google_service_account.jenkins_ci.email}"
}

resource "google_storage_bucket_iam_member" "ci_models_admin" {
  bucket = var.models_bucket_name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.jenkins_ci.email}"
}

# Dedicated Service Account for ELK host
resource "google_service_account" "elk_host" {
  account_id   = "elk-host-${var.environment}"
  display_name = "ELK Logging Host Service Account (${var.environment})"
  project      = var.project_id
}

# Boot disk image: Ubuntu 22.04 LTS
data "google_compute_image" "ubuntu_2204" {
  family  = "ubuntu-2204-lts"
  project = "ubuntu-os-cloud"
}

# GCE Virtual Machine Instances
resource "google_compute_instance" "vm" {
  for_each     = var.instances
  name         = "pricing-${var.environment}-${each.key}"
  machine_type = each.value.machine_type
  zone         = var.zone
  project      = var.project_id

  boot_disk {
    initialize_params {
      image = data.google_compute_image.ubuntu_2204.self_link
      size  = each.value.disk_size_gb
      type  = "pd-standard"
    }
  }

  network_interface {
    subnetwork = var.subnet_id

    dynamic "access_config" {
      for_each = each.value.assign_public_ip ? [1] : []
      content {}
    }
  }

  service_account {
    email  = each.key == "ci" ? google_service_account.jenkins_ci.email : google_service_account.elk_host.email
    scopes = ["https://www.googleapis.com/auth/cloud-platform"]
  }

  metadata = {
    enable-oslogin = "TRUE"
    ssh-keys       = var.ssh_public_key != "" ? "${var.ssh_user}:${var.ssh_public_key}" : ""
  }

  labels = {
    project = "pricing"
    env     = var.environment
    role    = each.value.role
    owner   = "aditya"
  }
}
