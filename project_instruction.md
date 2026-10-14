# Project Information: Cloud-Native MLOps Dynamic Pricing Platform

---

## 1. Project Identity & Metadata

* **Project Title:** Cloud-Native MLOps Platform: Resilient E-Commerce Dynamic Pricing & Demand Forecasting Engine
* **Short Title:** Cloud-Native Dynamic Pricing Platform
* **Academic Program:** Third Year B.Tech in Computer Science and Engineering (Data Science)


* **Institution:** Dwarkadas J. Sanghvi College of Engineering (Autonomous College Affiliated to the University of Mumbai)


* **Target Course:** DevOps Laboratory (`DJS23DOE311L`) — Semester V


* **Team Size:** 3 Members
* **Designated Cloud Provider:** Google Cloud Platform (GCP)
* **Target Workload:** Scalable ML Microservice Architecture with Continuous Retraining Loops



---

## 2. Cloud Provider Mandate: Google Cloud Platform (GCP)

> **CRITICAL DIRECTIVE FOR AGENTS & DEVELOPERS:**
> All cloud infrastructure, provisioning scripts, deployment targets, and container registries **MUST USE GOOGLE CLOUD PLATFORM (GCP)**. Do not write AWS (EC2/S3/EKS) or Azure definitions.

### GCP Services Mapping

| Infrastructure Role | Standard Tooling | GCP Service Implementation |
| --- | --- | --- |
| **Compute & Orchestration** | Kubernetes | **Google Kubernetes Engine (GKE)** (Standard or Autopilot cluster) |
| **Virtual Machines (IaC/Ansible)** | Compute Engine | **Google Compute Engine (GCE)** (`e2-medium` / `e2-standard-2` instances) |
| **Virtual Networking** | VPC & Firewalls | **GCP VPC Network, Subnets, and Cloud Firewall Rules** |
| **Container Registry** | Image Repository | **Google Artifact Registry** (`pkg.dev`) |
| **Infrastructure as Code** | Terraform | **HashiCorp Terraform with `google` & `google-beta` providers** |
| **Object Storage (Models/Data)** | Blob Storage | **Google Cloud Storage (GCS)** Buckets (`gs://`) |
| **Ingress & Traffic Gateway** | Load Balancer | **GKE Ingress backed by Google Cloud HTTP(S) Load Balancer** with SSL/TLS certificates |
| **Identity & Access** | IAM & Security | **GCP IAM Service Accounts**, **GCP Secret Manager**, and **Kubernetes Secrets** |

---

## 3. Academic Syllabus Coverage (DevOps Laboratory: `DJS23DOE311L`)

This project implements all 10 units outlined in the autonomous college syllabus:

* **Unit 1: Virtualization and Containerization with Docker**

* Multi-stage `Dockerfile` minimizing image size and attack surface.


* Multi-container local orchestration via `docker-compose.yml` linking the Flask API and mock logging agents.




* **Unit 2: Infrastructure as Code with Terraform**

* Modular Terraform configurations (`modules/vpc`, `modules/gke`, `modules/gce`) targeting GCP.


* Workspaces for environment isolation (`staging`, `prod`) and automated resource teardown scripts (`terraform destroy`).




* **Unit 3: Configuration Management with Puppet and Ansible**

* Ansible playbooks and modular roles automating GCE node package installation (`docker`, `python3-pip`, `curl`).


* Security hardening, system user creation, and service configuration idempotency.




* **Unit 4: Continuous Integration with Jenkins**

* Multi-stage declarative `Jenkinsfile` triggered via GitHub push webhooks.


* Automated SonarQube static code quality analysis and security vulnerability gates.




* **Unit 5: Automated Testing using Selenium**

* End-to-end headless browser testing via Selenium WebDriver asserting pricing calculator outputs.


* Automated screenshot capture upon test assertion failures archived to Jenkins artifacts.




* **Unit 6: DevOps Automation and Scripting**

* Bash scripts for health verification and container auto-restarts.


* Automated cron jobs for scheduled tasks.


* Python-based ChatOps bot delivering webhook failure and deployment notifications to Discord/Slack.




* **Unit 7: Container Orchestration with Kubernetes**

* Production manifests for GKE Deployments, ClusterIP Services, and Resource Quotas.


* Horizontal Pod Autoscaler (HPA) configured for dynamic traffic-based pod scaling.




* **Unit 8: Traffic Management with Kubernetes Ingress**

* Ingress configuration handling path-based routing (`/` to Frontend UI, `/api` to Flask Inference Service).


* SSL/TLS certificate termination via Kubernetes TLS secrets.




* **Unit 9: Monitoring and Logging with ELK Stack**

* Logstash shipping structured JSON logs from the Flask application to Elasticsearch.


* Kibana dashboards tracking request throughput, p95 API latency, and model inference distributions.




* **Unit 10: MLOps with PyCaret**

* Automated machine learning regression pipeline trained on pricing features using PyCaret.


* Deployment as a low-latency Flask REST API with automated retraining pipelines triggered on data drift.





---

## 4. System Architecture & Information Flow

```text
 ┌────────────────────────────────────────────────────────────────────────────────────────┐
 │ 1. CONTINUOUS DELIVERY ENGINE (Jenkins & GCP Artifact Registry)                        │
 │                                                                                        │
 │  Developer Push ──> GitHub Webhook ──> Jenkins Pipeline                               │
 │                                           │                                            │
 │                      ┌────────────────────┼────────────────────┐                       │
 │                      ▼                    ▼                    ▼                       │
 │                 [SonarQube]       [Docker GCR/GAR Build] [Selenium E2E Tests]          │
 │                Quality Gate       GCP Artifact Registry   Screenshots on Failure       │
 └───────────────────────────────────────────┬────────────────────────────────────────────┘
                                             │ Deploy (kubectl apply)
                                             ▼
 ┌────────────────────────────────────────────────────────────────────────────────────────┐
 │ 2. GOOGLE CLOUD PLATFORM (GKE Cluster Runtime & Networking)                            │
 │                                                                                        │
 │  Terraform (IaC on GCP) ──> Ansible (GCE Config) ──> Google Kubernetes Engine (GKE)    │
 │                                                                                        │
 │                       [GCP Cloud HTTP(S) Load Balancer & Ingress]                      │
 │                                      │ (TLS Termination)                               │
 │                      ┌───────────────┴───────────────┐                                 │
 │                      ▼                               ▼                                 │
 │              Path: / (Web UI)             Path: /api (Flask Inference)                 │
 │             [Frontend Pods]               [PyCaret Dynamic Pricing API]                │
 │                                                      │                                 │
 │                                            [GKE HPA Autoscaler: 70%]                   │
 └──────────────────────────────────────────────────────┼─────────────────────────────────┘
                                                        │ JSON Logs & Metrics
                                                        ▼
 ┌────────────────────────────────────────────────────────────────────────────────────────┐
 │ 3. OBSERVABILITY & CONTINUOUS RETRAINING LOOP (ELK Stack & MLOps)                      │
 │                                                                                        │
 │  [Flask Inference Engine] ──> [Logstash] ──> [Elasticsearch] ──> [Kibana Dashboard]   │
 │                                                     │                                  │
 │                                               Query Latency                            │
 │                                                     ▼                                  │
 │   Jenkins Retrain Job  <─── Webhook ──── [Drift Monitor Script] ───> [ChatOps Webhook] │
 │  (pycaret.regression)                     (Statistical Drift)         (Slack/Discord)  │
 └────────────────────────────────────────────────────────────────────────────────────────┘

```

---

## 5. Machine Learning & Application Specification

* **Problem Domain:** Dynamic Price Optimization and Demand Forecasting.
* **Dataset:** E-Commerce Retail Pricing & Demand Signals Dataset (Tabular, ~35,000–100,000 records).
* Features: `Base_Price`, `Competitor_Price`, `Inventory_Level`, `Units_Sold_Past_7D`, `Promotion_Type`, `Discount_Pct`, `Seasonal_Trend`.
* Target: `Optimal_Price` (Regression) or `Predicted_Demand`.


* **Model Framework:** PyCaret (`pycaret.regression`) evaluating LightGBM, Random Forest, and Gradient Boosting algorithms.


* **Artifact:** Serialized `.pkl` model artifact loaded into runtime memory at application startup.


* **Microservice API Contract:**
* `GET /`: Renders responsive pricing calculator web UI.
* `POST /api/predict`: Accepts feature JSON payload, calculates dynamic price elasticity, and returns output within 50ms.
* `GET /health`: Liveness and readiness health checks returning HTTP 200.
* `POST /api/retrain`: Reloads model artifacts dynamically with zero downtime.





---

## 6. Team Division of Responsibilities (3 Members)

### Member 1: GCP Infrastructure, Orchestration & Network Security

* Write modular Terraform configurations (`google` provider) for GCP VPC, subnets, GCE instances, and GKE clusters.


* Manage Terraform workspaces (`staging` vs. `prod`) and state locking.


* Build Ansible playbooks for GCE node bootstrapping, user permissions, and package setups.


* Author Kubernetes manifests (`deployment.yaml`, `service.yaml`, `hpa.yaml`, `ingress.yaml`) with TLS termination on GKE.



### Member 2: CI/CD Pipelines, Code Quality & Test Automation

* Author multi-stage production `Dockerfile` pushing to Google Artifact Registry.


* Configure local multi-container environments using `docker-compose.yml`.


* Construct declarative `Jenkinsfile` orchestrating pipeline checkout, image compilation, and GKE rollout.


* Enforce SonarQube static code quality gates and security checks.


* Build the Selenium WebDriver browser test suite to validate UI inputs and capture failure screenshots.



### Member 3: MLOps Engineering, Centralized Logging & Automation Scripting

* Train, evaluate, tune, and export the PyCaret dynamic pricing regression model to `src/model/pipeline.pkl`.


* Build the Flask REST microservice (`src/app.py`) with structured JSON logging.


* Configure Logstash pipelines, Elasticsearch indexing, and Kibana operational dashboards.


* Develop `scripts/monitor_drift.py` for statistical drift detection and trigger Jenkins retraining.


* Implement `scripts/auto_restart.sh` and `scripts/chatops_bot.py` for automated ChatOps incident alerting.



---

## 7. Guidelines for AI Agents & Developers

When inspecting, generating, or modifying code in this repository, all AI agents and contributors must observe these rules:

1. **Cloud Exclusivity:** Strictly use Google Cloud Platform (GCP) conventions, SDKs, and resource types (e.g., `google_container_cluster`, `google_compute_network`, `google_artifact_registry_repository`).
2. **Secrets & Security:** Never hardcode GCP service account keys, passwords, or webhook tokens in repository code. Rely on environment variables, GCP Secret Manager, or Kubernetes Secrets.


3. **Consistency Across Modules:** Maintain alignment between the input feature keys in `src/app.py`, the PyCaret dataframe columns in `src/model/train.py`, and the form input element IDs in `src/templates/index.html` and `tests/test_ui_selenium.py`.
4. **Idempotency & Clean Code:** Ensure all Terraform and Ansible configurations are strictly idempotent and safe to re-run.