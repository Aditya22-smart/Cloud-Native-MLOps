# Cloud-Native MLOps Dynamic Pricing Platform

[![Python](https://img.shields.io/badge/Python-3.10-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Google Cloud](https://img.shields.io/badge/GCP-asia--south1-4285F4?logo=google-cloud&logoColor=white)](https://cloud.google.com/)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-GKE_v1.30+-326CE5?logo=kubernetes&logoColor=white)](https://kubernetes.io/)
[![Terraform](https://img.shields.io/badge/IaC-Terraform-7B42BC?logo=terraform&logoColor=white)](https://www.terraform.io/)
[![Ansible](https://img.shields.io/badge/Config-Ansible_2.12+-EE0000?logo=ansible&logoColor=white)](https://www.ansible.com/)
[![Jenkins](https://img.shields.io/badge/CI%2FCD-Jenkins_Pipeline-D24939?logo=jenkins&logoColor=white)](https://www.jenkins.io/)
[![SonarQube](https://img.shields.io/badge/Quality_Gate-Passed-4E9BCD?logo=sonarqube&logoColor=white)](https://www.sonarqube.org/)
[![ELK Stack](https://img.shields.io/badge/Observability-ELK_8.x-005571?logo=elastic&logoColor=white)](https://www.elastic.co/)
[![Selenium](https://img.shields.io/badge/Testing-Selenium_Grid-43B02A?logo=selenium&logoColor=white)](https://www.selenium.dev/)

> **A production-grade, highly automated cloud-native machine learning platform** designed for real-time e-commerce price optimization and demand forecasting. Built on Google Cloud Platform (GCP) with continuous integration, automated deployment, horizontal pod autoscaling, centralized telemetry, statistical drift monitoring, and self-healing retraining loops.

---

## 📌 Table of Contents

- [System Architecture](#-system-architecture)
- [Key Features](#-key-features)
- [Live Staging Deployment](#-live-staging-deployment)
- [Project Directory Layout](#-project-directory-layout)
- [CI/CD Pipeline Workflow](#-cicd-pipeline-workflow)
- [Infrastructure as Code (Terraform)](#-infrastructure-as-code-terraform)
- [Configuration Management (Ansible)](#-configuration-management-ansible)
- [Observability & Drift Detection](#-observability--drift-detection)
- [Local Quickstart](#-local-quickstart)
- [Automated Testing](#-automated-testing)

---

## 🏗 System Architecture

```text
                                  ┌────────────────────────────────────────────────────────┐
                                  │                  DEVELOPER WORKFLOW                    │
                                  └──────────────────────────┬─────────────────────────────┘
                                                             │ Git Push / Pull Request
                                                             ▼
                                                ┌─────────────────────────┐
                                                │   GitHub (dev / main)   │
                                                └────────────┬────────────┘
                                                             │ Webhook Trigger
                                                             ▼
┌─────────────────────────────────────────────── Jenkins CI/CD Pipeline ───────────────────────────────────────────────┐
│ [1. Checkout] ─> [2. SonarQube SAST] ─> [3. Docker Build] ─> [4. Push to GAR] ─> [5. Deploy GKE] ─> [6. Selenium E2E] │
└────────────────────────────────────────────────────────────┬─────────────────────────────────────────────────────────┘
                                                             │ Rolling Update
                                                             ▼
┌────────────────────────────────────── Google Kubernetes Engine (GKE) ─────────────────────────────────────────────────┐
│                                                                                                                       │
│   Incoming HTTPS Traffic                                                                                              │
│            │                                                                                                          │
│            ▼                                                                                                          │
│   [ GKE Ingress (SSL/TLS Termination) ]                                                                               │
│            ├── Path: /     ───────────> [ pricing-ui Service (ClusterIP) ] ─────────> [ Web Pricing UI ]              │
│            └── Path: /api  ───────────> [ pricing-api Service (ClusterIP) ] ────────> [ Flask + PyCaret ML Pods ]   │
│                                                                                               │                       │
│                                              ┌────────────────────────────────────────────────┤ (Autoscaling)         │
│                                              ▼                                                ▼                       │
│                                   [ Horizontal Pod Autoscaler ]                  [ Persistent Models GCS Bucket ]     │
│                                        (Target: 70% CPU)                            gs://...-staging-models/          │
│                                                                                                                       │
│   Log Streaming via Filebeat DaemonSet ───────────────────────────────────────────────────────────────────────────────┘
│            │
│            ▼
│   [ Logstash (Port 5044) ] ──> [ Elasticsearch (Port 9200) ] ──> [ Kibana Dashboards (Port 5601) ]
│                                           │
│                                           ▼
│                                 [ Drift Detector (Cron) ]
│                                           │ (Statistical deviation > 2σ)
│                                           ├──> [ ChatOps Bot: Discord / Slack Alert ]
│                                           └──> [ Automated Retrain Pipeline Webhook ]
```

---

## ⚡ Key Features

| Capability | Technical Implementation | Highlights |
| :--- | :--- | :--- |
| **ML Inference Engine** | Flask 2.2+, PyCaret Regression, Gunicorn | Real-time pricing predictions under 30ms latency with strict payload validation. |
| **Interactive UI** | Vanilla HTML5, Modern CSS, Fetch API | Glassmorphism pricing calculator embedded directly in the microservice. |
| **Containerization** | Docker Multi-Stage Build | Non-root runtime user (`app:app`), minimal image surface, built-in health checks. |
| **IaC Automation** | Terraform >= 1.3 | Reusable modules (`network`, `compute`), multi-environment workspaces (`staging`, `prod`). |
| **Config Management** | Ansible >= 2.12 | Modular, idempotent roles: `docker_setup`, `security_hardening`, `app_deploy`. |
| **Container Orchestration** | GKE v1.30+ (Cluster: `pricing-staging`) | Path-based routing, resource requests/limits, liveness/readiness probes, HPA (1–5 pods). |
| **Continuous Integration** | Declarative Jenkins Pipeline | 6 automated stages: Quality Gate, Build, Push, Rolling Deployment, Selenium UI tests. |
| **Static Code Analysis** | SonarQube Scanner | 0 Vulnerabilities, 0 Bugs, Quality Gate enforced before cluster rollout. |
| **Telemetry & Logging** | ELK Stack 8.x + Filebeat | Structured JSON logging captures latency, inputs, status code, and predictions. |
| **Drift Detection & ChatOps** | Python 3, Cron, Discord/Slack Webhooks | Evaluates 24-hour inference logs for price drift ($\mu \pm 2\sigma$) and auto-triggers retraining. |

---

## 🌐 Live Staging Deployment

The platform is provisioned and deployed live on Google Cloud Platform:

| Component | Target URL / Identifier | Status |
| :--- | :--- | :--- |
| **Web Pricing UI** | [`https://pricing-staging.136.81.137.108.sslip.io`](https://pricing-staging.136.81.137.108.sslip.io) | `HTTP 200 OK` |
| **Liveness & Readiness** | [`https://pricing-staging.136.81.137.108.sslip.io/health`](https://pricing-staging.136.81.137.108.sslip.io/health) | `HTTP 200 (healthy)` |
| **Prediction API** | `POST https://pricing-staging.136.81.137.108.sslip.io/api/predict` | `HTTP 200 JSON` |
| **GKE Cluster** | `pricing-staging` (Zone: `asia-south1-a`, Endpoint: `34.93.95.131`) | `2 Nodes Ready` |
| **Artifact Registry** | `asia-south1-docker.pkg.dev/aditya-devops-lab/pricing/pricing-api` | `Images Active` |
| **Model Registry (GCS)** | `gs://aditya-devops-lab-staging-models/pipeline.pkl` | `330MB Pipeline` |

---

## 📁 Project Directory Layout

```text
.
├── AGENTS.md                   # System rules, coding standards, and agent guidelines
├── Dockerfile                  # Multi-stage production container build (non-root)
├── docker-compose.yml          # Local multi-service stack (Flask, Selenium, Jenkins)
├── requirements.txt            # Root dependencies (pycaret, scikit-learn, pandas)
├── cicd/
│   ├── Jenkinsfile             # 6-Stage Declarative CI/CD pipeline
│   ├── docker-compose.yml      # CI stack (Jenkins, SonarQube, PostgreSQL)
│   └── sonar-project.properties# SonarQube project rules & scope configuration
├── k8s/
│   ├── base/                   # Kustomize base manifests (deployment, service, hpa)
│   └── overlays/
│       ├── staging/            # Staging environment overlay with ingress & secrets
│       └── prod/               # Production environment overlay
├── terraform/
│   ├── modules/
│   │   ├── network/            # VPC, public/private subnets, Cloud NAT, firewall rules
│   │   └── compute/            # GKE cluster, node pools, service accounts, IAM roles
│   └── environments/
│       ├── staging/            # Staging workspace infrastructure variables
│       └── prod/               # Production workspace infrastructure variables
├── ansible/
│   ├── site.yml                # Master configuration playbook
│   ├── inventory/              # Hosts inventory (hosts.ini)
│   └── roles/
│       ├── docker_setup/       # Automated Docker Engine & compose installation
│       ├── security_hardening/ # UFW firewall, fail2ban, SSH hardening, non-root user
│       └── app_deploy/         # Application deployment & systemd service setup
├── monitoring/
│   ├── docker-compose.yml      # Observability stack (Elasticsearch, Logstash, Kibana)
│   ├── filebeat.yml            # Filebeat daemon log forwarding configuration
│   └── logstash.conf           # Logstash JSON parsing pipeline & Elasticsearch indexer
├── scripts/
│   ├── auto_restart.sh         # Cron-based self-healing process monitor
│   ├── chatops_bot.py          # Discord & Slack incident notification webhook
│   ├── load_test_hpa.py        # Concurrent synthetic load generator for HPA testing
│   ├── monitor_drift.py        # Statistical model drift detector (μ ± 2σ evaluation)
│   └── seed_predictions.py     # Generates mock inference logs for observability testing
├── src/
│   ├── app.py                  # Flask microservice routes (/health, /api/predict, /)
│   ├── config.py               # Application environment configuration
│   ├── logger.py               # Structured JSON logger
│   ├── model_singleton.py      # Thread-safe serialized model loader
│   ├── model/
│   │   ├── train.py            # Model training & validation script
│   │   ├── evaluate.py         # Model evaluation metrics (MAE, RMSE, R²)
│   │   └── pipeline.pkl        # Serialized regression model artifact
│   └── static/ & templates/    # Dynamic pricing UI templates & assets
└── tests/
    ├── test_api.py             # Unit and integration tests for Flask API
    ├── test_model_singleton.py # Tests for thread-safe model caching
    └── test_ui_selenium.py     # End-to-end browser tests via Selenium Grid
```

---

## 🔄 CI/CD Pipeline Workflow

The declarative pipeline in [`cicd/Jenkinsfile`](cicd/Jenkinsfile) triggers on changes to the `dev` branch:

1. **Checkout**: Checks out source code from Git with commit hash tracking.
2. **Static Analysis & SonarQube**: Executes `sonar-scanner` and halts pipeline execution if the Quality Gate fails.
3. **Build & Tag Docker Image**: Builds production multi-stage image tagged with `${GIT_SHA}` and `latest`.
4. **Push to Artifact Registry**: Authenticates with Google Cloud and pushes to `asia-south1-docker.pkg.dev`.
5. **Deploy to GKE**: Triggers a rolling update on Kubernetes deployment `pricing-api` and verifies rollout status.
6. **Post-Deploy Functional Test (Selenium)**: Executes browser-based E2E tests against the live staging cluster, capturing failure screenshots if any assertion fails.

---

## 📈 Observability & Drift Detection

### 1. Structured JSON Logging
Every inference request logs a structured JSON object to stdout:
```json
{
  "timestamp": "2026-10-15T18:30:00Z",
  "client_ip": "136.81.137.108",
  "input_features": {
    "Base_Price": 120.0,
    "Competitor_Price": 115.0,
    "Inventory_Level": 80,
    "Units_Sold_Past_7D": 150,
    "Discount_Pct": 12.0,
    "Seasonal_Trend": 1.25,
    "Promotion_Type": "percentage"
  },
  "predicted_price": 108.42,
  "latency_ms": 14.8,
  "http_status": 200
}
```

### 2. Filebeat & Logstash Pipeline
- **Filebeat DaemonSet**: Deployed across GKE nodes, tailing container logs and streaming to Logstash on port `5044`.
- **Logstash**: Parses JSON payloads, extracts request metadata, and routes to Elasticsearch index `pricing-logs-%{+YYYY.MM.dd}`.
- **Kibana**: Visualizes real-time request rates, average latency, and price distribution curves.

### 3. Automated Drift Detection & Self-Healing Retraining
- [`scripts/monitor_drift.py`](scripts/monitor_drift.py) runs on a cron schedule, querying Elasticsearch for trailing 24-hour prediction metrics.
- If the trailing mean price shifts beyond statistical bounds ($\mu_{baseline} \pm 2\sigma$), the script:
  1. Issues an immediate alert to **Discord/Slack** via [`scripts/chatops_bot.py`](scripts/chatops_bot.py).
  2. Dispatches an authenticated webhook to Jenkins to trigger pipeline retraining ([`src/model/train.py`](src/model/train.py)).

---

## 🚀 Local Quickstart

### Prerequisites
- Docker & Docker Compose v2+
- Python 3.9 or 3.10

### 1. Run the Full Stack Locally
```bash
# Clone the repository
git clone https://github.com/Aditya22-smart/Cloud-Native-MLOps.git
cd Cloud-Native-MLOps

# Start Application, Selenium Grid, and Monitoring
docker compose up -d --build
```

### 2. Verify Endpoints
- **Pricing Calculator UI**: Open `http://localhost:5000` in your browser.
- **Health Check**:
  ```bash
  curl -s http://localhost:5000/health
  # {"status": "healthy", "model_version": "v1.0.0"}
  ```
- **Predict Endpoint**:
  ```bash
  curl -s -X POST http://localhost:5000/api/predict \
    -H "Content-Type: application/json" \
    -d '{
      "Base_Price": 100.0,
      "Competitor_Price": 95.0,
      "Inventory_Level": 200,
      "Units_Sold_Past_7D": 50,
      "Discount_Pct": 10.0,
      "Seasonal_Trend": 1.1,
      "Promotion_Type": "percentage"
    }'
  ```

---

## 🧪 Automated Testing

### Run Unit & Integration Tests
```bash
docker run --rm \
  -e PYTHONPATH=/app \
  asia-south1-docker.pkg.dev/aditya-devops-lab/pricing/pricing-api:latest \
  pytest tests/test_api.py tests/test_model_singleton.py
```

### Run End-to-End Selenium Tests
```bash
pytest tests/test_ui_selenium.py
```

### Run Synthetic HPA Load Test
```bash
python3 scripts/load_test_hpa.py
```
*(Sends concurrent requests to validate autoscaling up to 5 pods).*