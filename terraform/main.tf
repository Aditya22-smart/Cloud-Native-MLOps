# Root main.tf: Wires networking, GKE, GCE, storage, container registry, and Workload Identity

# 1. Custom VPC, subnets, Cloud NAT, and firewall rules
module "vpc" {
  source = "./modules/vpc"

  project_id           = var.project_id
  region               = var.region
  environment          = var.environment
  subnet_cidr          = var.subnet_cidr
  pods_subnet_cidr     = var.pods_subnet_cidr
  services_subnet_cidr = var.services_subnet_cidr
}

# 2. GKE Standard Zonal Cluster with Workload Identity
module "gke" {
  source = "./modules/gke"

  project_id              = var.project_id
  region                  = var.region
  zone                    = var.zone
  environment             = var.environment
  network_id              = module.vpc.network_id
  subnet_id               = module.vpc.subnet_id
  pods_range_name         = module.vpc.pods_range_name
  services_range_name     = module.vpc.services_range_name
  master_authorized_cidrs = var.master_authorized_cidrs
  machine_type            = var.gke_machine_type
  min_node_count          = var.gke_min_nodes
  max_node_count          = var.gke_max_nodes
  deletion_protection     = var.deletion_protection
}

# 3. GCE Virtual Machines (CI and ELK hosts)
module "gce" {
  source = "./modules/gce"

  project_id         = var.project_id
  zone               = var.zone
  environment        = var.environment
  subnet_id          = module.vpc.subnet_id
  models_bucket_name = module.gcs.models_bucket_name
}

# 4. Dedicated Pod Identity GCP Service Account: pricing-app-<env>
resource "google_service_account" "pricing_app" {
  account_id   = "pricing-app-${var.environment}"
  display_name = "Workload Identity Service Account for Pricing App (${var.environment})"
  project      = var.project_id
}

# Workload Identity binding: allows K8s SA 'pricing-api' in namespace 'pricing' to impersonate GCP SA
resource "google_service_account_iam_member" "workload_identity_binding" {
  service_account_id = google_service_account.pricing_app.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "serviceAccount:${var.project_id}.svc.id.goog[pricing/pricing-api]"
}

# Global Static IP for Ingress: pricing-ingress-ip
resource "google_compute_global_address" "ingress_ip" {
  name        = "pricing-ingress-ip"
  description = "Global external static IP reserved for GKE pricing ingress"
  project     = var.project_id
}

# 5. Artifact Registry for Docker images
module "artifact_registry" {
  source = "./modules/artifact_registry"

  project_id  = var.project_id
  region      = var.region
  environment = var.environment

  writer_service_accounts = [module.gce.jenkins_ci_service_account]
  reader_service_accounts = [module.gke.node_service_account_email]
}

# 6. Cloud Storage buckets for models and datasets
module "gcs" {
  source = "./modules/gcs"

  project_id    = var.project_id
  region        = var.region
  environment   = var.environment
  force_destroy = var.force_destroy

  pod_identity_service_accounts = [google_service_account.pricing_app.email]
}
