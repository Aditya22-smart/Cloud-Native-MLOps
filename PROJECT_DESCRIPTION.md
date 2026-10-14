# Cloud-Native MLOps Dynamic Pricing Platform

### Resilient E-Commerce Dynamic Pricing & Demand Forecasting Engine

> **This is a group project.** This document is the shared technical specification for the entire platform. Every contributor — application, ML, infrastructure, CI/CD, and observability work — should be read and implemented against this single reference so that the independently developed pieces integrate cleanly into one working system.

**Course:** DevOps Laboratory (`DJS23DOE311L`) — Semester V
**Program:** B.Tech Computer Science & Engineering (Data Science)
**Institution:** Dwarkadas J. Sanghvi College of Engineering (Autonomous, University of Mumbai)
**Cloud Provider:** Google Cloud Platform (GCP) — mandatory
**Workload:** Scalable ML microservice architecture with continuous retraining loops

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Problem Domain & Objectives](#2-problem-domain--objectives)
3. [Technology Stack](#3-technology-stack)
4. [System Architecture](#4-system-architecture)
5. [Repository Layout](#5-repository-layout)
6. [Machine Learning Specification](#6-machine-learning-specification)
7. [Microservice API Contract](#7-microservice-api-contract)
8. [Component Specifications](#8-component-specifications)
9. [Observability & Drift Detection](#9-observability--drift-detection)
10. [Security & Secrets Management](#10-security--secrets-management)
11. [Syllabus Coverage Matrix](#11-syllabus-coverage-matrix)
12. [Development Standards](#12-development-standards)
13. [Environment Setup](#13-environment-setup)
14. [Local Development Workflow](#14-local-development-workflow)
15. [Operating Constraints](#15-operating-constraints)

---

## 1. Project Overview

This project is an automated, resilient, cloud-native machine learning serving platform designed for real-time e-commerce price optimization and demand forecasting. It bridges data science model lifecycle management with production platform engineering across containerization, Infrastructure as Code, configuration management, GitOps CI/CD, container orchestration, end-to-end testing, centralized observability, and automated retraining loops.

The platform centers on a Python/Flask microservice that predicts dynamic retail prices from demand signals. Around that service, the project constructs a complete production platform on Google Cloud: a Jenkins-driven delivery pipeline with SonarQube quality gates, a GKE cluster provisioned by Terraform and configured by Ansible, an SSL/TLS-terminated ingress with path-based routing, an ELK observability stack, and — the defining capability — a **closed-loop retraining system** in which production traffic is monitored for statistical drift and automatically triggers model retraining and redeployment.

### 1.1 The Central Idea

Most of this project is conventional DevOps. One part is not: the **feedback loop**.

A static model deployed once degrades silently as the market changes. This platform closes that gap end to end:

```text
Real traffic -> prediction -> structured logs -> ELK -> drift analysis
                                                          |
                        <----- retrain + redeploy <-------+  (when mu +/- 2 sigma is breached)
```

The practical consequence is that the model, the platform, and the monitoring are not three separate deliverables — they are one system. Observability exists not merely to display dashboards, but to produce the signal that drives retraining.

---

## 2. Problem Domain & Objectives

### 2.1 Problem Domain

Dynamic Price Optimization and Demand Forecasting. Given a set of product and market features, the system predicts the optimal price to charge to maximise revenue while remaining competitive.

### 2.2 Objectives

| # | Objective |
|---|---|
| 1 | Serve single-digit-millisecond price predictions from a low-latency Flask REST API |
| 2 | Keep the model fresh automatically in response to real-world data drift |
| 3 | Guarantee that no code reaching production has bypassed automated quality and security gates |
| 4 | Make the entire environment reproducible and disposable through code, not manual console clicks |
| 5 | Centralise all telemetry so inference latency, throughput, and prediction distribution are observable |
| 6 | Ensure every infrastructure layer is idempotent and safe to re-run without side effects |

---

## 3. Technology Stack

### 3.1 Application & ML

| Component | Technology | Version Constraint |
|---|---|---|
| Language | Python | **3.9+ — strictly avoid 3.12 and above** (PyCaret binary incompatibility) |
| Web Framework | Flask | >= 2.2.0 |
| AutoML | PyCaret (`pycaret.regression`) | >= 3.0.0 |
| ML Runtime | scikit-learn, LightGBM | — |
| Data Handling | pandas, numpy | — |
| Testing | Selenium WebDriver | >= 4.0.0 |
| HTTP Client | requests | — |

### 3.2 Infrastructure & Orchestration

| Component | Technology | Version Constraint |
|---|---|---|
| IaC | Terraform (`google`, `google-beta` providers) | >= 1.3 |
| Configuration Management | Ansible | >= 2.12 |
| Container Orchestration | Google Kubernetes Engine (GKE) | K8s v1.26+ |
| Containers | Docker, Docker Compose | Compose v2+ |
| Cloud | GCP — GKE, GCE, VPC, Artifact Registry, GCS, Secret Manager, IAM | — |

### 3.3 CI/CD & Observability

| Component | Technology | Version Constraint |
|---|---|---|
| CI/CD | Jenkins (Declarative Pipeline) | — |
| SAST / Quality Gate | SonarQube Scanner | — |
| Log Aggregation | Logstash | 8.x |
| Log Storage | Elasticsearch | 8.x |
| Visualisation | Kibana | 8.x |

---

## 4. System Architecture

### 4.1 Full Platform Architecture

```text
 +--------------------------------------------------------------------------------------+
 | 1. CONTINUOUS DELIVERY ENGINE (Jenkins & GCP Artifact Registry)                      |
 |                                                                                      |
 |   Developer Push --> GitHub Webhook --> Jenkins Pipeline                             |
 |                                              |                                       |
 |                       +----------------------+----------------------+                |
 |                       v                      v                      v                |
 |                 [SonarQube]       [Docker GAR Build]     [Selenium E2E Tests]        |
 |                Quality Gate       Artifact Registry     Screenshots on Failure      |
 +------------------------------------------+-------------------------------------------+
                                            | Deploy (kubectl apply)
                                            v
 +--------------------------------------------------------------------------------------+
 | 2. GOOGLE CLOUD PLATFORM (GKE Cluster Runtime & Networking)                          |
 |                                                                                      |
 |   Terraform (IaC) --> Ansible (GCE Config) --> Google Kubernetes Engine (GKE)         |
 |                                                                                      |
 |                    [GCP Cloud HTTP(S) Load Balancer & Ingress]                      |
 |                                   |  (TLS Termination)                               |
 |                   +---------------+---------------+                                 |
 |                   v                               v                                 |
 |           Path: / (Web UI)             Path: /api (Flask Inference)                 |
 |          [Frontend UI Pods]               [PyCaret Dynamic Pricing API]              |
 |                                                  |                                 |
 |                                          [GKE HPA Autoscaler: 70%]                   |
 +---------------------------------------------------+----------------------------------+
                                                     | JSON Logs & Metrics
                                                     v
 +--------------------------------------------------------------------------------------+
 | 3. OBSERVABILITY & CONTINUOUS RETRAINING LOOP (ELK Stack & MLOps)                    |
 |                                                                                      |
 |   [Flask Inference] --> [Logstash] --> [Elasticsearch] --> [Kibana Dashboard]         |
 |                                                |                                     |
 |                                          Query Latency                            |
 |                                                v                                     |
 |     Jenkins Retrain Job <--- Webhook --- [Drift Monitor Script] ---> [ChatOps Webhook] |
 |     (pycaret.regression)              (Statistical Drift)         (Slack/Discord)    |
 +--------------------------------------------------------------------------------------+
```

### 4.2 GitHub-First Source Model (Commit Identity)

```text
[ Git Push / PR ] --> [ GitHub Repository ]
                              |  (Webhook Trigger)
                              v
              +--------------------------------------+
              |  Jenkins CI/CD Pipeline              |
              |  1. Checkout & Dependency Setup      |
              |  2. SonarQube SAST & Quality Gate    |
              |  3. Multi-Stage Docker Build & Tag    |
              |  4. Push to Artifact Registry        |
              |  5. Rolling Update to GKE            |
              |  6. Selenium E2E (screenshots)        |
              +-----------------+--------------------+
                                |
                                v
              +--------------------------------------+
              |  Kubernetes Cluster (GKE)            |
              |  [ Ingress: TLS + Path Routing ]     |
              |         |                            |
              |    +----+----+                       |
              |    v         v                       |
              | [UI Pods] [Flask + PyCaret Pods]     |
              |           (HPA Scaling)              |
              +-----------+--------------------------+
                          | (JSON Telemetry)
                          v
              +--------------------------------------+
              |  ELK Stack                           |
              |  [Logstash] -> [Elasticsearch]        |
              |        -> [Kibana Dashboards]         |
              +-----------------+--------------------+
                                | (Drift Query)
                                v
                    [ Python Script / Cron Job ]
                          |            |
              +-----------+            +-----------+
              v                                    v
      [ ChatOps Webhook Alert ]        [ Jenkins Retrain Job ]
```

### 4.3 Request Lifecycle

```text
Client
  |
  v
Google Cloud HTTP(S) Load Balancer  -- TLS terminated here
  |
  v
GKE Ingress Controller  -- path match
  |
  +-- "/"  --> Web UI
  |
  +-- "/api" --> Flask Inference Service
                 |
                 +--> validate payload against feature schema
                 +--> construct single-row pandas DataFrame
                 +--> pipeline.predict(df)          <-- in-memory, no reload
                 +--> build response {predicted_price, latency_ms}
                 +--> emit structured JSON log      <-- timestamp, client_ip,
                 |                                      input_features,
                 |                                      predicted_price,
                 |                                      latency_ms, http_status
                 v
              Response (< 50ms target)
```

---

## 5. Repository Layout

```text
Cloud-Native-MLOps/
|
|-- README.md                      Project introduction & architecture overview
|-- PROJECT_DESCRIPTION.md         This document — full platform specification
|-- AGENTS.md                      Developer & agent reference guide
|-- project_instruction.md         Academic brief & syllabus requirements
|-- Dockerfile                     Multi-stage production image (port 5000, non-root)
|-- docker-compose.yml             Local multi-container orchestration
|-- .dockerignore                  Build context exclusions
|-- .gitignore                     Excludes secrets, state files, artifacts
|-- .env.example                   Non-secret configuration template
|
|-- src/
|   |-- app.py                     Flask microservice (all 4 endpoints)
|   |-- requirements.txt           Pinned Python dependencies
|   |-- wsgi.py                    WSGI entrypoint for production serving
|   |-- logger.py                  Structured JSON logging configuration
|   |-- config.py                  Environment-driven configuration loader
|   |-- model_singleton.py         Thread-safe model lifecycle & hot-swap
|   |-- templates/
|   |   `-- index.html             Responsive pricing calculator UI
|   `-- model/
|       |-- train.py               PyCaret training / comparison / export
|       |-- generate_dataset.py    Deterministic synthetic dataset generator
|       |-- evaluate.py            Model evaluation & metrics report
|       `-- pipeline.pkl           Serialized PyCaret pipeline artifact
|
|-- scripts/
|   |-- monitor_drift.py           24h ES drift analysis (mu +/- 2 sigma)
|   |-- chatops_bot.py             Slack / Discord webhook notifier
|   |-- auto_restart.sh            Cron-driven container health & restart
|   |-- seed_predictions.py        Seeds ES with realistic telemetry for demos
|   `-- retrain.sh                 Jenkins-invoked retraining entrypoint
|
|-- tests/
|   |-- test_ui_selenium.py        Headless E2E UI tests w/ screenshots
|   |-- test_api.py                API contract unit tests
|   |-- conftest.py                Shared pytest fixtures
|   `-- reports/screenshots/       Failure screenshot artifacts (gitignored)
|
|-- k8s/
|   |-- namespace.yaml
|   |-- deployment.yaml            Replicas, resources, probes, security context
|   |-- service.yaml               ClusterIP services (UI + inference)
|   |-- ingress.yaml               Path routing + TLS (tls-pricing-secret)
|   |-- hpa.yaml                   Target 70% average CPU
|   |-- secrets.yaml               Secret templates (no literal values)
|   |-- configmap.yaml             Non-sensitive configuration
|   |-- resourcequota.yaml         Namespace quotas
|   |-- kustomization.yaml         Environment overlay base
|   `-- overlays/{staging,prod}/   Per-environment patches
|
|-- terraform/
|   |-- versions.tf                Terraform + provider version constraints
|   |-- providers.tf               google & google-beta provider config
|   |-- variables.tf               Typed input variables
|   |-- main.tf                    Root module wiring
|   |-- outputs.tf                 Exported values (LB IP, registry paths)
|   |-- terraform.tfvars.example   Non-secret variable template
|   |-- modules/
|   |   |-- vpc/                   VPC, subnets, Cloud Firewall, routes
|   |   |-- gke/                   GKE cluster, node pools, add-ons
|   |   |-- gce/                   GCE instances for Ansible management
|   |   |-- artifact_registry/     GAR docker repository + IAM binding
|   |   └── gcs/                   Bucket for models and datasets
|   `-- workspaces/
|       |-- staging.tfvars         Staging environment configuration
|       `-- prod.tfvars            Production environment configuration
|
|-- ansible/
|   |-- site.yml                   Master playbook (role orchestration)
|   |-- inventory.ini              Static inventory (or GCP dynamic inventory)
|   |-- group_vars/all.yml         Shared variables
|   |-- roles/
|   |   |-- docker_setup/          Install Docker + Compose
|   |   |-- security_hardening/    Users, SSH, firewall, sysctl
|   |   |-- python_setup/          Python 3.11 + venv + dependencies
|   |   |-- app_deploy/            Deploy service, configure env, systemd
|   |   └── monitoring_setup/       Log shipper configuration
|
|-- cicd/
|   |-- Jenkinsfile                Declarative 6-stage pipeline
|   |-- sonar-project.properties   SonarQube project config
|   |-- vars/vars.groovy           Shared pipeline variables
|   `-- libs/retrain.groovy        Retrain job shared library
|
|-- monitoring/
|   |-- logstash.conf              JSON parsing -> pricing-logs-* index
|   |-- elasticsearch-template.json Index template & ILM policy
|   |-- kibana_dashboard.json      Saved objects (NDJSON)
|   |-- kibana_setup.sh            Dashboard import automation
|   `-- filebeat.yml               GKE log shipping sidecar config
|
`-- data/
    |-- raw/pricing_dataset.csv    Generated training dataset (gitignored)
    `-- schemas/feature_schema.json Single source of truth for features
```

---

## 6. Machine Learning Specification

### 6.1 Dataset

| Attribute | Value |
|---|---|
| Domain | E-Commerce Retail Pricing & Demand Signals |
| Type | Tabular |
| Volume | ~35,000 – 100,000 records |
| Target variable | `Optimal_Price` (Regression) or `Predicted_Demand` |

### 6.2 Feature Schema — Single Source of Truth

These seven features and one target constitute the **contract between every component** in the platform. Any divergence between the training dataframe, the API payload, the HTML form, and the Selenium tests is a defect.

```json
{
  "Base_Price":          { "type": "float",   "description": "Original listed price of the product" },
  "Competitor_Price":    { "type": "float",   "description": "Closest competitor's current price" },
  "Inventory_Level":     { "type": "integer", "description": "Units currently in stock" },
  "Units_Sold_Past_7D":  { "type": "integer", "description": "Units sold in trailing 7 days" },
  "Promotion_Type":      { "type": "category","description": "none | percentage | bundle | clearance" },
  "Discount_Pct":        { "type": "float",   "description": "Discount percentage applied, 0-100" },
  "Seasonal_Trend":      { "type": "float",   "description": "Seasonal demand multiplier" },
  "Optimal_Price":       { "type": "float",   "description": "TARGET VARIABLE" }
}
```

### 6.3 Model Framework

**PyCaret (`pycaret.regression`)** — the regression AutoML module.

Candidate algorithms evaluated during `compare_models()`:

- **LightGBM** — gradient boosting, fast and strong on tabular data
- **Random Forest** — robust ensemble baseline
- **Gradient Boosting** — classic sklearn GBT

### 6.4 Training Pipeline (`src/model/train.py`)

```text
1. Load dataset from data/raw/pricing_dataset.csv
2. pycaret.regression.setup()           -- target = Optimal_Price, session id logged
3. compare_models()                     -- LightGBM / RF / Gradient Boosting
4. Select best model by MAE (tie-break RMSE)
5. tune() / finalize_model()            -- fold-based validation
6. Evaluate on holdout:  MAE, RMSE, R2, MAPE
7. save_model() --> src/model/pkl_files/...  (pycaret native)
8. Export entire setup+model --> src/model/pipeline.pkl   <-- single artifact
```

The artifact must be a **complete pipeline** — preprocessing, imputation, encoding, and the trained estimator bundled together — so that inference requires only raw feature values.

### 6.5 Dataset Generation

Since a production dataset is not distributed with the repository, `src/model/generate_dataset.py` synthesises one deterministically:

- Fixed random seed for reproducibility across all contributors
- Realistic price-elasticity demand curves (higher `Competitor_Price` relative to `Base_Price` suppresses `Optimal_Price`)
- Inventory pressure: low `Inventory_Level` and high `Units_Sold_Past_7D` raise `Optimal_Price`
- `Promotion_Type` and `Discount_Pct` correlated with seasonal trend
- Configurable row count (default 50,000)

The generator is what makes drift demonstrable: regenerating with a shifted demand regime produces the distribution shift that `monitor_drift.py` detects.

### 6.6 Model Serving

The pipeline is deserialised **once** at application startup and held in memory. Per-request work is limited to constructing a single-row DataFrame and calling `predict()`.

To hit the sub-50ms target:

- No model reloading on request
- No per-request schema compilation or network calls
- Structured logging serialised cheaply and flushed asynchronously so telemetry does not block the response

---

## 7. Microservice API Contract

Base URL: `https://<load-balancer-host>`

### 7.1 `GET /` — Pricing Calculator UI

**Purpose:** Render the responsive pricing calculator web interface.

**Response:** `200 OK`, `text/html` from `src/templates/index.html`

### 7.2 `POST /api/predict` — Price Prediction

**Purpose:** Ingest feature JSON, compute the dynamic price elasticity, return the predicted price.

**Request:**

```json
{
  "Base_Price": 1299.00,
  "Competitor_Price": 1349.00,
  "Inventory_Level": 240,
  "Units_Sold_Past_7D": 512,
  "Promotion_Type": "percentage",
  "Discount_Pct": 12.5,
  "Seasonal_Trend": 1.15
}
```

**Response:** `200 OK`

```json
{
  "predicted_price": 1342.77,
  "latency_ms": 11.4,
  "model_version": "lgbm_ensemble_v1",
  "timestamp": "2026-01-14T09:22:41.113Z"
}
```

**Error responses:**

| Status | Condition |
|---|---|
| `400` | Missing feature, wrong type, or out-of-range value |
| `422` | Schema validation failure with per-field detail |
| `500` | Model inference failure |

**Performance target:** end-to-end inference **under 50ms**.

### 7.3 `GET /health` — Liveness & Readiness

**Purpose:** Kubernetes liveness and readiness probe endpoint.

**Response:** `200 OK`

```json
{
  "status": "healthy",
  "model_loaded": true,
  "model_version": "lgbm_ensemble_v1",
  "uptime_seconds": 8412,
  "timestamp": "2026-01-14T09:22:41.113Z"
}
```

Returns `503` if the model artifact is missing or unloadable, which correctly removes the pod from the Service endpoints set.

### 7.4 `POST /api/retrain` — Zero-Downtime Hot Reload

**Purpose:** Swap in a newly trained `pipeline.pkl` without dropping in-flight requests or restarting the pod.

**Behaviour:**

1. Acquire the model lock
2. Deserialise the candidate artifact from disk (or GCS)
3. Run a smoke-test prediction to validate it
4. Atomically rebind the in-memory reference
5. Release the lock

Requests in flight continue against the previous model and complete normally; subsequent requests use the new one. The swap is a pointer assignment under a mutex, not a reload, so there is no window where no model is available.

The endpoint is **protected** by a shared secret supplied via environment variable or Kubernetes Secret, and should be invoked by Jenkins after a successful retraining run rather than exposed publicly.

**Response:** `200 OK`

```json
{
  "status": "reloaded",
  "model_version": "lgbm_ensemble_v2",
  "previous_version": "lgbm_ensemble_v1",
  "reload_latency_ms": 843.2,
  "timestamp": "2026-01-14T09:22:41.113Z"
}
```

---

## 8. Component Specifications

### 8.1 Containerisation — `Dockerfile`

| Requirement | Detail |
|---|---|
| Build strategy | **Multi-stage** — builder stage compiles dependencies; runtime stage carries only artefacts |
| Runtime user | **Non-root** dedicated user, no shell where avoidable |
| Exposed port | `5000` |
| Base image | Slim, pinned by digest or explicit tag |
| Signal handling | Exec-form `CMD` so Gunicorn receives `SIGTERM` for graceful shutdown |

Stage separation keeps compilers, build headers, and pip caches out of the runtime image, reducing both image size and CVE surface.

### 8.2 Local Orchestration — `docker-compose.yml`

Brings up the full local stack:

- **Flask API** — the microservice, volume-mounted for live reload
- **Elasticsearch** — single-node, memory-locked
- **Logstash** — reads container stdout, parses JSON, writes to Elasticsearch
- **Kibana** — dashboards
- **(Optional) Jenkins + SonarQube** — for pipeline testing

All credentials flow from a local `.env` file, never from committed values.

### 8.3 Infrastructure as Code — `terraform/`

| Requirement | Detail |
|---|---|
| Providers | `google` and `google-beta` |
| Module structure | `vpc`, `gke`, `gce`, `artifact_registry`, `gcs` |
| Environment isolation | Terraform workspaces — `staging` and `prod` |
| State | Remote backend (GCS bucket); `*.tfstate` gitignored |
| Teardown | `terraform destroy` script per workspace |
| Idempotency | No resource depends on creation order or manual pre-seeding |

**Module responsibilities:**

- **`modules/vpc`** — custom-mode VPC network, subnets with secondary ranges, Cloud NAT, Cloud Firewall rules, private service access for GKE
- **`modules/gke`** — Standard or Autopilot cluster, node pools with labels/taints, workload identity, network policy
- **`modules/gce`** — `e2-medium` / `e2-standard-2` instances acting as Ansible-managed nodes, service account attachment, IAM roles
- **`modules/artifact_registry`** — Docker-format repository at `pkg.dev`, IAM binding granting Artifact Registry Writer
- **`modules/gcs`** — buckets for model artifacts and datasets, uniform bucket-level access, versioning

**Workspace usage:**

```bash
terraform workspace select staging || terraform workspace new staging
terraform init
terraform plan  -var-file=workspaces/staging.tfvars
terraform apply -var-file=workspaces/staging.tfvars
```

### 8.4 Configuration Management — `ansible/`

| Requirement | Detail |
|---|---|
| Idempotency | All tasks use modules (not raw `command`/`shell` where avoidable) and declare handlers |
| Roles | `docker_setup`, `security_hardening`, `python_setup`, `app_deploy`, `monitoring_setup` |
| Target OS | Ubuntu / Debian |
| Orchestration | `ansible/site.yml` imports roles in order |

**Role responsibilities:**

- **`docker_setup`** — Docker Engine + Compose plugin from the official apt repository, daemon hardening, non-root `docker` group membership
- **`security_hardening`** — dedicated system user, SSH key-only auth, UFW rules, unattended security upgrades, `sysctl` tuning, password policy
- **`python_setup`** — Python 3.11 (the required version), `venv`, `requirements.txt` install
- **`app_deploy`** — checkout or pull image, render environment file from variables, systemd unit for the Flask service, start/enable/reload
- **`monitoring_setup`** — install and configure the log shipper

Every role carries `defaults/main.yml`, `tasks/main.yml`, and `handlers/main.yml`.

### 8.5 Container Orchestration — `k8s/`

**Deployment requirements:**

- `resources.requests` and `resources.limits` defined for **both** CPU and memory
- `livenessProbe` and `readinessProbe` both pointing at `/health`
- Rolling update strategy with sane `maxSurge` / `maxUnavailable`
- Security context: non-root, read-only root filesystem where possible, dropped capabilities
- Environment sourced from ConfigMap (non-sensitive) and Secret (sensitive)
- Image pulled from Artifact Registry using Workload Identity — no stored JSON keys

**Service:**

ClusterIP Services exposing the UI and the inference backend separately so that ingress can route each path to its own backend.

**HPA:**

- `averageUtilization: 70` on CPU
- Explicit `apiVersion: autoscaling/v2`
- Min/max replicas defined per environment

**ResourceQuota:**

Namespace-level quotas on compute resources, object count, and ephemeral storage.

### 8.6 Traffic Management — `k8s/ingress.yaml`

| Requirement | Detail |
|---|---|
| Class | `gce` (GKE Ingress, backed by Google Cloud HTTP(S) Load Balancer) |
| Path `/` | Routes to the Web UI service |
| Path `/api` | Routes to the Flask inference service |
| TLS | Terminated at the ingress using secret `tls-pricing-secret` |
| Annotation | `kubernetes.io/ingress.allow-http: "false"` to force HTTPS |
| Certificate | Managed Certificate or pre-provisioned Google SSL certificate referenced in the annotation |

### 8.7 CI/CD — `cicd/Jenkinsfile`

Declarative pipeline with GitHub webhook trigger. Stages execute in **strict order**:

| # | Stage | Purpose |
|---|---|---|
| 1 | **Checkout** | Retrieve source, cache dependencies where possible |
| 2 | **Static Analysis & Quality Gate** | SonarQube scanner + `waitForQualityGate`. **Build fails** on coverage or security gate failure |
| 3 | **Multi-Stage Docker Build** | Build the production image, tag with commit SHA and branch |
| 4 | **Push to Artifact Registry** | Authenticate to `pkg.dev`, push both tagged and latest |
| 5 | **GKE Rolling Update** | `kubectl apply`, wait for rollout, verify readiness |
| 6 | **Selenium Functional UI Test** | Headless E2E against the live deployment |

Additional pipeline behaviour:

- Secrets sourced from Jenkins Credentials — never literals in the `Jenkinsfile`
- `post { failure }` captures diagnostics and notifies ChatOps
- Test screenshots archived as Jenkins artifacts from `reports/screenshots/`
- A separate **retrain job** exists, triggerable by webhook from the drift monitor

### 8.8 End-to-End Testing — `tests/test_ui_selenium.py`

| Requirement | Detail |
|---|---|
| Mode | Headless Chrome |
| Coverage | Form field rendering, valid submission, predicted price returned and formatted, invalid input handling, API latency within threshold |
| Selectors | Drive the UI by the **same element IDs** the template defines |
| Failure handling | `try/except` around assertions; on failure capture `driver.save_screenshot("reports/screenshots/<test>_<timestamp>.png")` |
| Artifacts | Screenshot directory created on demand; archived by Jenkins |

### 8.9 Automation Scripts — `scripts/`

**`auto_restart.sh`** — designed for cron. Inspects container/service health, restarts failed processes, logs actions, exits non-zero if remediation fails.

**`chatops_bot.py`** — sends structured webhook payloads to Slack or Discord. Notifies on deployment success, deployment failure, drift detection, and retrain completion. Webhook URLs read from environment.

**`monitor_drift.py`** — see §9.2.

---

## 9. Observability & Drift Detection

### 9.1 ELK Pipeline

**Log format.** `src/app.py` emits one JSON object per request to stdout:

```json
{
  "timestamp": "2026-01-14T09:22:41.113Z",
  "client_ip": "10.42.0.19",
  "input_features": {
    "Base_Price": 1299.0, "Competitor_Price": 1349.0, "Inventory_Level": 240,
    "Units_Sold_Past_7D": 512, "Promotion_Type": "percentage",
    "Discount_Pct": 12.5, "Seasonal_Trend": 1.15
  },
  "predicted_price": 1342.77,
  "latency_ms": 11.4,
  "http_status": 200
}
```

**Logstash** (`monitoring/logstash.conf`) parses the JSON and writes to:

```text
pricing-logs-%{+YYYY.MM.dd}
```

Daily indices, enabling time-partitioned retention. An index template with ILM manages rollover and deletion.

On GKE, container stdout is collected by the cluster logging agent or Filebeat and forwarded to Logstash; locally, Logstash tails the container log stream directly.

**Kibana dashboards** (`monitoring/kibana_dashboard.json`, NDJSON saved objects) visualise:

- Total request throughput over time
- Average and **p95** inference latency
- Distribution of predicted prices (histogram)
- HTTP status code breakdown
- Top client IPs

### 9.2 Drift Detection (`scripts/monitor_drift.py`)

The automation core of the project.

```text
1. Query Elasticsearch index pricing-logs-* for the trailing 24 hours
2. Aggregate predicted_price values  ->  [p1, p2, ... pn]
3. Compute baseline:  mu = mean(values)
                     sigma = stddev(values)
4. Compute current window mean (most recent 6 hours)
5. If abs(current_mean - mu) > 2 * sigma:
       -> DRIFT DETECTED
6.     invoke scripts/chatops_bot.py   (Slack / Discord alert)
7.     POST webhook to Jenkins to trigger the retrain pipeline
8. Otherwise: exit 0 silently (no alert noise)
```

A configurable minimum sample size prevents drift evaluation on statistically insignificant windows.

### 9.3 Retraining Loop

```text
Drift Detected
      |
      v
Jenkins Retrain Job (webhook-triggered)
      |
      v
src/model/train.py  -- re-run against latest data
      |
      v
New pipeline.pkl --> Artifact Registry / GCS
      |
      v
GKE Rolling Update
      |
      v
POST /api/retrain  -- zero-downtime hot reload
      |
      v
ChatOps notification: "New model lgbm_ensemble_v2 deployed"
```

---

## 10. Security & Secrets Management

### 10.1 Absolute Rules

**Never commit to the repository:**

- GCP service account JSON keys
- API keys or OAuth client secrets
- Slack or Discord webhook URLs
- Jenkins API tokens
- Elasticsearch credentials
- TLS private keys
- Terraform state files

**All such values are read from:**

1. Environment variables in local development (`.env`, gitignored; template in `.env.example`)
2. GCP Secret Manager for cloud-managed secrets
3. Kubernetes Secrets for runtime injection
4. Jenkins Credentials for pipeline secrets

### 10.2 Google Cloud Authentication

- **Workload Identity Federation** for GKE — pods authenticate to GCP without any key material in the cluster
- **Service accounts** with least-privilege IAM roles for Terraform and Ansible operations
- **ADC / `gcloud auth application-default login`** for local tooling

### 10.3 Git Ignores

`.gitignore` must exclude:

```text
*.tfstate
*.tfstate.*
.terraform/
.terraform.lock.hcl      # committed per environment policy; document the choice
*.pem
*.key
secrets.yaml            # use .example.yaml templates instead
.env
__pycache__/
*.pyc
.venv/
venv/
pipeline.pkl
data/raw/
reports/screenshots/
```

### 10.4 Webhook Endpoint Protection

`POST /api/retrain` is guarded by a bearer token from an environment variable. The drift monitor supplies it. Without the token the endpoint returns `401`.

---

## 11. Syllabus Coverage Matrix

| Unit | Topic | Implementation Artifact |
|---|---|---|
| 1 | Virtualisation & Containerisation | Multi-stage `Dockerfile`; `docker-compose.yml` linking API + logging agents |
| 2 | Infrastructure as Code | Modular Terraform (`vpc`, `gke`, `gce`, `artifact_registry`, `gcs`); `staging`/`prod` workspaces; destroy scripts |
| 3 | Configuration Management | Ansible playbooks & modular roles; hardening; user creation; idempotency |
| 4 | Continuous Integration | Declarative `Jenkinsfile`; GitHub webhook trigger; SonarQube quality & security gates |
| 5 | Automated Testing | Headless Selenium WebDriver; assertions on pricing calculator output; failure screenshots archived |
| 6 | DevOps Automation & Scripting | Bash health checks; cron scheduling; Python ChatOps bot (Slack/Discord) |
| 7 | Container Orchestration | GKE Deployments; ClusterIP Services; ResourceQuota; HPA at 70% CPU |
| 8 | Traffic Management | GKE Ingress path routing `/` and `/api`; TLS termination via K8s Secret |
| 9 | Monitoring & Logging | Logstash JSON ingestion; Elasticsearch `pricing-logs-*`; Kibana throughput/p95/distribution dashboards |
| 10 | MLOps with PyCaret | Automated PyCaret regression pipeline; Flask REST serving; drift-triggered retraining |

---

## 12. Development Standards

### 12.1 Python Style

- Strict **PEP 8** compliance
- Type hints on public functions
- Docstrings for modules, classes, and non-obvious functions
- No secrets in source
- No hardcoded feature names outside the shared schema module

### 12.2 Git Branching

| Branch | Purpose |
|---|---|
| `main` | Production-ready; direct pushes restricted |
| `dev` | Active integration branch |
| `feature/<name>` | Feature development |

### 12.3 Commit Convention

Conventional Commits:

```text
feat: add selenium end-to-end form validation
fix: resolve HPA cpu metric binding in deployment manifest
ci: enforce sonarqube threshold quality gate
infra: add terraform workspace configuration for staging
docs: document drift detection thresholds
```

### 12.4 Cross-Component Consistency

The single most common integration defect in this platform is a **feature-name mismatch** between components. The following must always agree exactly:

```text
src/model/train.py        dataframe column names
        |
        v
data/schemas/feature_schema.json   <-- single source of truth
        |
        +--> src/app.py             JSON payload keys
        +--> src/templates/index.html   HTML input element ids
        +--> tests/test_ui_selenium.py  Selenium selectors
        +--> scripts/monitor_drift.py   aggregation fields
```

When the schema changes, update `feature_schema.json` first, then propagate.

---

## 13. Environment Setup

### 13.1 Python

```bash
# Verify a compatible interpreter (3.9 - 3.11)
python3 --version

# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r src/requirements.txt
```

> **Do not use Python 3.12 or newer.** PyCaret and its LightGBM binary dependencies are not compatible with 3.12+ and installation or import will fail.

### 13.2 Generate the Dataset and Train

```bash
python src/model/generate_dataset.py --rows 50000
python src/model/train.py
python src/model/evaluate.py
```

Artifacts land in `src/model/pipeline.pkl`.

### 13.3 Run the Service

```bash
python src/app.py
curl http://localhost:5000/health
```

### 13.4 Tooling

| Tool | Minimum Version |
|---|---|
| Terraform | 1.3 |
| Ansible | 2.12 |
| Docker / Compose | Compose v2 |
| kubectl | 1.26+ |

GCP authentication:

```bash
gcloud auth application-default login
gcloud config set project <PROJECT_ID>
```

---

## 14. Local Development Workflow

### 14.1 Full Stack with Docker Compose

```bash
cp .env.example .env      # fill in local, non-production values
docker compose up --build
```

- Application: <http://localhost:5000>
- Kibana: <http://localhost:5601>

Verify logs flow end to end:

```bash
curl -X POST http://localhost:5000/api/predict \
  -H 'Content-Type: application/json' \
  -d '{"Base_Price":1299,"Competitor_Price":1349,"Inventory_Level":240,
       "Units_Sold_Past_7D":512,"Promotion_Type":"percentage",
       "Discount_Pct":12.5,"Seasonal_Trend":1.15}'

# Confirm the document landed in Elasticsearch
curl http://localhost:9200/pricing-logs-*/_search?pretty
```

### 14.2 Kubernetes Manifests

```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secrets.yaml          # values injected, not committed
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/hpa.yaml
kubectl apply -f k8s/ingress.yaml

kubectl rollout status deployment/pricing-api -n pricing
kubectl get hpa pricing-api -n pricing
```

### 14.3 Drift Simulation

```bash
# Seed realistic prediction history
python scripts/seed_predictions.py

# Regenerate the dataset under a shifted demand regime
python src/model/generate_dataset.py --rows 50000 --demand-shift 0.25

# Verify the monitor detects it
python scripts/monitor_drift.py
```

### 14.4 Automated Health Check

```bash
crontab -e
*/5 * * * * /path/to/scripts/auto_restart.sh >> /var/log/auto_restart.log 2>&1
```

---

## 15. Operating Constraints

### 15.1 Absolute Constraints

1. **GCP only.** No AWS (`ec2`, `s3`, `eks`) or Azure resource types anywhere in code or configuration.
2. **No hardcoded secrets.** API keys, service account paths, passwords, and webhook URLs are read exclusively from environment variables, GCP Secret Manager, or Kubernetes Secrets.
3. **Python 3.9 – 3.11.** Never 3.12+.
4. **Idempotency.** All Terraform and Ansible configuration is safe to apply repeatedly without drift or error.
5. **Sub-50ms inference.** The model is loaded once and never reloaded per request.
6. **Zero-downtime reload.** `/api/retrain` performs an atomic swap, not a restart.
7. **Schema consistency.** Feature names are identical across training, API, UI, tests, and scripts.
8. **Kubernetes v1.26+ conventions.** Explicit `apiVersion`, correct `metadata.labels`, selectors matching the template labels exactly.

### 15.2 Performance Targets

| Metric | Target |
|---|---|
| `/api/predict` latency (p95) | < 50 ms |
| Model load at startup | Once, before serving traffic |
| Hot reload latency | < 2 s |
| `/health` response | < 100 ms |

### 15.3 Known Environmental Constraints

- PyCaret/LightGBM require Python 3.9–3.11; a 3.12+ interpreter will fail at install or import time
- The ELK stack is memory-intensive; local Elasticsearch should be started with a memory lock (`bootstrap.memory_lock: true`, `ulimits.memlock: -1`)
- SonarQube requires an active scanner token and a reachable server; the quality gate blocks the pipeline when coverage or security thresholds are unmet
- GKE Ingress provisions a Google Cloud Load Balancer asynchronously — DNS propagation can delay external access after `terraform apply`
- Artifact Registry requires IAM binding for the deploying principal, not just repository creation

---

## Summary

This platform delivers a production-grade dynamic pricing microservice and, more importantly, the **closed operational loop** that keeps it accurate: continuous delivery with enforced quality gates, reproducible cloud infrastructure, declarative configuration management, path-based TLS-secured traffic management, centralised telemetry, and statistical drift detection that automatically triggers retraining and zero-downtime redeployment.

Every component specified in this document exists to serve that loop.

---

*Maintained as the shared specification for the group. Update this document when any interface — feature schema, API contract, image coordinates, or configuration variable names — changes.*