# Custom-mode VPC Network
resource "google_compute_network" "vpc" {
  name                    = "pricing-${var.environment}-vpc"
  auto_create_subnetworks = false
  routing_mode            = "REGIONAL"
}

# Subnet with secondary ranges for VPC-native GKE cluster
resource "google_compute_subnetwork" "subnet" {
  name                     = "pricing-${var.environment}-subnet"
  ip_cidr_range            = var.subnet_cidr
  region                   = var.region
  network                  = google_compute_network.vpc.id
  private_ip_google_access = true

  secondary_ip_range {
    range_name    = "pricing-${var.environment}-pods"
    ip_cidr_range = var.pods_subnet_cidr
  }

  secondary_ip_range {
    range_name    = "pricing-${var.environment}-services"
    ip_cidr_range = var.services_subnet_cidr
  }
}

# Cloud Router for egress NAT
resource "google_compute_router" "router" {
  name    = "pricing-${var.environment}-router"
  region  = var.region
  network = google_compute_network.vpc.id
}

# Cloud NAT for private GKE nodes and VMs to access internet
resource "google_compute_router_nat" "nat" {
  name                               = "pricing-${var.environment}-nat"
  router                             = google_compute_router.router.name
  region                             = var.region
  nat_ip_allocate_option             = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"

  log_config {
    enable = true
    filter = "ERRORS_ONLY"
  }
}

# Firewall: Internal subnet communication
resource "google_compute_firewall" "allow_internal" {
  name    = "pricing-${var.environment}-allow-internal"
  network = google_compute_network.vpc.id

  allow {
    protocol = "tcp"
  }
  allow {
    protocol = "udp"
  }
  allow {
    protocol = "icmp"
  }

  source_ranges = [
    var.subnet_cidr,
    var.pods_subnet_cidr,
    var.services_subnet_cidr
  ]
}

# Firewall: Identity-Aware Proxy (IAP) SSH access (Port 22 from 35.235.240.0/20)
resource "google_compute_firewall" "allow_iap_ssh" {
  name        = "pricing-${var.environment}-allow-iap-ssh"
  network     = google_compute_network.vpc.id
  description = "Allow SSH via Google Cloud Identity-Aware Proxy"

  allow {
    protocol = "tcp"
    ports    = ["22"]
  }

  source_ranges = ["35.235.240.0/20"]
}

# Firewall: Google Load Balancer & Ingress Health Checks (130.211.0.0/22 and 35.191.0.0/16)
resource "google_compute_firewall" "allow_health_checks" {
  name        = "pricing-${var.environment}-allow-health-checks"
  network     = google_compute_network.vpc.id
  description = "Allow health checks from Google Global Cloud Load Balancers"

  allow {
    protocol = "tcp"
  }

  source_ranges = [
    "130.211.0.0/22",
    "35.191.0.0/16"
  ]
}

# Private Service Access: Reserved global address range for Google managed services
resource "google_compute_global_address" "private_service_access" {
  name          = "pricing-${var.environment}-psa-range"
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  prefix_length = 16
  network       = google_compute_network.vpc.id
}

# Service Networking Connection
resource "google_service_networking_connection" "private_vpc_connection" {
  network                 = google_compute_network.vpc.id
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.private_service_access.name]
}
