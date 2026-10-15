# Staging Cloud Infrastructure Outputs (Day 6 & Day 7)

**Last Updated:** 2026-10-15  
**GCP Project ID:** `aditya-devops-lab`  
**Region / Zone:** `asia-south1` / `asia-south1-a`  
**Environment:** `staging`  

---

## 1. Network & Ingress Access Points

| Component | Value | Notes |
| :--- | :--- | :--- |
| **Ingress Static External IP** | `136.81.137.108` | Reserved global IP `pricing-ingress-ip` |
| **Web UI Public URL** | `https://pricing-staging.136.81.137.108.sslip.io/` | Global HTTP(S) Load Balancer |
| **REST API Prediction URL** | `https://pricing-staging.136.81.137.108.sslip.io/api/predict` | `POST` dynamic inference |
| **Health Check URL** | `https://pricing-staging.136.81.137.108.sslip.io/health` | HTTP 200 liveness/readiness |
| **Direct IP Access** | `https://136.81.137.108/` | Supported via defaultBackend |
| **VPC Network Name** | `pricing-staging-vpc` | Custom VPC |
| **Subnet CIDR** | `10.10.0.0/20` (`pricing-staging-subnet`) | Private Google Access enabled |
| **Pods Secondary Range** | `10.11.0.0/16` (`pricing-staging-pods`) | VPC-Native GKE IP allocation |
| **Services Secondary Range** | `10.12.0.0/20` (`pricing-staging-services`) | GKE ClusterIP allocation |

---

## 2. Container Orchestration (GKE)

| Component | Value | Notes |
| :--- | :--- | :--- |
| **Cluster Name** | `pricing-staging` | Standard Zonal Cluster |
| **Master API Endpoint** | `https://34.93.95.131` | Port 443 |
| **Kubernetes Version** | `v1.36.4-gke.1391002` | Regular Release Channel |
| **Node Pool Name** | `pricing-staging-node-pool` | Autoscaling 1 to 3 nodes |
| **Machine Type** | `e2-standard-2` | 2 vCPUs, 8 GB RAM |
| **Workload Identity Pool** | `aditya-devops-lab.svc.id.goog` | Active |
| **K8s ServiceAccount** | `pricing-api` (namespace: `pricing`) | Annotated with GCP SA |
| **Workload Identity GCP SA** | `pricing-app-staging@aditya-devops-lab.iam.gserviceaccount.com` | `roles/iam.workloadIdentityUser` |

---

## 3. Container Registry & Model Storage

| Component | Value | Access / Roles |
| :--- | :--- | :--- |
| **Artifact Registry Docker Repo** | `asia-south1-docker.pkg.dev/aditya-devops-lab/pricing` | Docker repository |
| **Container Image URI** | `asia-south1-docker.pkg.dev/aditya-devops-lab/pricing/pricing-api:v1.0.0` | Multi-stage, non-root user 10001 |
| **Models GCS Bucket** | `gs://aditya-devops-lab-staging-models` | Versioned, Uniform Bucket-Level Access |
| **Datasets GCS Bucket** | `gs://aditya-devops-lab-staging-datasets` | Versioned, Uniform Bucket-Level Access |
| **Model Pipeline Artifact** | `gs://aditya-devops-lab-staging-models/pipeline.pkl` | 330 MB PyCaret serialized pipeline |

---

## 4. Compute Engine Hosts (CI & ELK)

| Host Name | Internal IP | External IP | Role & Services |
| :--- | :--- | :--- | :--- |
| `pricing-staging-ci` | `10.10.0.2` | Ephemeral | Jenkins CI Controller, SonarQube Scanner |
| `pricing-staging-elk` | `10.10.0.3` | Ephemeral | Elasticsearch (9200), Logstash (5044), Kibana (5601) |

---

## 5. GCP Service Accounts

| Service Account Email | Purpose & Attached Roles |
| :--- | :--- |
| `gke-nodes-staging@aditya-devops-lab.iam.gserviceaccount.com` | GKE Node Pool SA (`logging.logWriter`, `monitoring.metricWriter`, `artifactregistry.reader`) |
| `pricing-app-staging@aditya-devops-lab.iam.gserviceaccount.com` | Pod Identity SA (`storage.objectAdmin` on models bucket) |
| `jenkins-ci-staging@aditya-devops-lab.iam.gserviceaccount.com` | Jenkins host SA (`artifactregistry.writer`, `container.developer`, `storage.objectAdmin`) |
| `elk-host-staging@aditya-devops-lab.iam.gserviceaccount.com` | ELK host SA |
