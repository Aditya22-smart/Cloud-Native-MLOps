---

### `AGENTS.md`

```markdown
# AGENTS.md: Developer & Agent Reference Guide

This file provides system context, architecture rules, dependency standards, operational workflows, and constraints for artificial intelligence agents and developers contributing to the **Cloud-Native MLOps Dynamic Pricing Platform**.

---

## 1. Project Intent & Scope

- **Primary Goal:** Provide a production-grade, highly automated microservice that predicts dynamic retail prices based on demand signals while showcasing complete adherence to the DevOps Laboratory (`DJS23DOE311L`) syllabus.
- **Application Core:** A Python/Flask microservice exposing:
  - `GET /`: Serves the user pricing calculator web interface.
  - `POST /api/predict`: Ingests JSON payload with product and market features, returning predicted dynamic price and inference latency.
  - `GET /health`: Kubernetes liveness and readiness probe endpoint.
  - `POST /api/retrain`: Endpoint to trigger automated model retraining or reload a newly trained serialized pipeline artifact.
- **ML Engine:** PyCaret Regression module (`pycaret.regression`). Serialized pipeline artifacts must be stored as `pipeline.pkl` under `src/model/`.

---

## 2. Environment & Dependency Specifications

- **Runtime:** Python 3.9+ (Avoid Python 3.12+ to prevent PyCaret dependency conflicts).
- **Core Libraries:**
  - `flask>=2.2.0`
  - `pycaret>=3.0.0`
  - `scikit-learn`
  - `pandas`
  - `selenium>=4.0.0`
  - `requests`
- **Infrastructure & Orchestration:**
  - Terraform >= 1.3
  - Ansible >= 2.12
  - Kubernetes (Minikube / MicroK8s / K8s v1.26+)
  - Docker & Docker Compose v2+
- **CI/CD & Observability:**
  - Jenkins (Declarative pipeline using `Jenkinsfile`)
  - SonarQube Scanner
  - ELK Stack (Elasticsearch 8.x, Logstash 8.x, Kibana 8.x)

---

## 3. Architecture & Technical Constraints

### A. Containerization (`Dockerfile`)
- Must use multi-stage builds to minimize image surface and security vulnerabilities.
- Non-root user must be configured for running the Flask service.
- Must expose port `5000`.

### B. Infrastructure as Code (`terraform/`)
- Code must reside in reusable modules (`compute`, `network`).
- Workspaces (`terraform workspace new <env>`) must be supported for `dev`, `staging`, and `prod`.
- Secrets, credentials, and state files (`*.tfstate`) must be excluded from version control via `.gitignore`.

### C. Configuration Management (`ansible/`)
- Playbooks must use idempotency principles.
- Use modular Ansible roles (`docker_setup`, `security_hardening`, `app_deploy`).
- Must run cleanly against target Ubuntu/Debian Linux hosts.

### D. Continuous Integration (`cicd/Jenkinsfile`)
- Every pipeline execution must follow these mandatory stages in order:
  1. `Checkout`
  2. `Static Analysis & SonarQube Quality Gate` (must break build if coverage or security gate fails)
  3. `Build & Tag Docker Image`
  4. `Deploy to Cluster` (Rolling update on Kubernetes)
  5. `Post-Deploy Functional Test (Selenium)`
- Selenium failures must store screenshots in the Jenkins workspace under `reports/screenshots/`.

### E. Container Orchestration & Ingress (`k8s/`)
- Deployments must define resource requests and limits (`cpu`, `memory`).
- Liveness and readiness probes must point to `/health`.
- Horizontal Pod Autoscaler (HPA) configured to target 70% average CPU utilization.
- Ingress manifest must configure path routing:
  - `/` -> UI / Web Service
  - `/api` -> Flask Inference Service
- Ingress must reference a Kubernetes secret for SSL/TLS termination (`tls-pricing-secret`).

### F. Centralized Logging & Observability (`monitoring/`)
- Flask API must output structured JSON logs containing: `timestamp`, `client_ip`, `input_features`, `predicted_price`, `latency_ms`, `http_status`.
- Logstash configuration (`logstash.conf`) must parse incoming JSON and forward to the Elasticsearch index `pricing-logs-%{+YYYY.MM.dd}`.
- Kibana must provide visualization for total requests, average inference latency, and price prediction distribution.

### G. Drift Detection & Automation Scripts (`scripts/`)
- `monitor_drift.py`: Queries Elasticsearch for the trailing 24 hours of prediction data. If the mean predicted price shifts beyond a defined statistical threshold ($\mu \pm 2\sigma$), it invokes:
  1. `chatops_bot.py`: Sends a webhook payload to Discord/Slack.
  2. A webhook call to Jenkins to trigger the retrain pipeline (`src/model/train.py`).
- `auto_restart.sh`: A shell script designed for cron execution that inspects container/service health and restarts failed processes automatically.

---

## 4. Coding & Commit Standards

- **Python Style:** Strict adherence to PEP 8.
- **Git Branching:**
  - `main`: Production-ready code; direct pushes restricted.
  - `dev`: Active integration branch.
  - Feature branches: `feature/<feature-name>`.
- **Commit Messages:** Follow conventional commits:
  - `feat: add selenium end-to-end form validation`
  - `fix: resolve HPA cpu metric binding in deployment manifest`
  - `ci: enforce sonarqube threshold quality gate`
  - `infra: add terraform workspace configuration for staging`

---

## 5. Agent Instructions for Code Generation

When requested to create or modify code in this repository:
1. Always preserve the relationship between components (e.g., ensure the Flask route parameter names exactly match the PyCaret inference dataframe schema and the Selenium form input element IDs).
2. Avoid hardcoding passwords, API tokens, or webhook URLs; always read them from environment variables or Kubernetes secrets.
3. Keep YAML manifests clean, explicitly defining `apiVersion`, metadata labels, and selectors matching standard Kubernetes v1.26+ conventions.