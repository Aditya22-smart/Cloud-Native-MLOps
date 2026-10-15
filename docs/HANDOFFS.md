# Shared Team Handoffs Log

This file tracks cross-member dependencies and contract handoffs between Aditya (Cloud Platform), Bishwajeet (App/ML), and Shreyas (CI/CD/Observability).

---

### H3: Frozen Contract & Namespace/Secrets Architecture (from: aditya-agent, to: bishwajeet, shreyas, needed by: Day 4)
- **Need:** Agreement on frozen names, numeric UID/GID, port/probe paths, and ConfigMap vs Secret split.
- **Why:** Kubernetes manifests (`k8s/`) and Dockerfile/CI deployment commands require exact naming parity.
- **Specification:**
  - **Namespace:** `pricing`
  - **App Port / Probes:** `5000` / `GET /health` (readiness & liveness)
  - **Container UID/GID:** `10001:10001` (numeric non-root)
  - **Services (ClusterIP):** `pricing-ui` (UI, port 80 -> 5000), `pricing-api` (Inference, port 80 -> 5000)
  - **Ingress routing:** `/` to `pricing-ui`, `/api` to `pricing-api`
  - **Artifact Registry Repo:** `<REGION>-docker.pkg.dev/<PROJECT_ID>/pricing/pricing-api:<git-sha>`
  - **ConfigMap (`pricing-config`):** `MODEL_PATH`, `MODEL_VERSION`, `ELASTICSEARCH_URL`, `LOGSTASH_HOST`, `GCS_MODEL_BUCKET`, `APP_BASE_URL`
  - **Secret (`pricing-secrets`):** `RETRAIN_TOKEN`, `JENKINS_RETRAIN_TOKEN`, `SLACK_WEBHOOK_URL` / `DISCORD_WEBHOOK_URL`
- **Status:** accepted (implemented in staging overlay)

---

### H7: CI Host & GKE Deployment Credentials (from: aditya-agent, to: shreyas, needed by: Day 6/7)
- **Host VM:** `pricing-staging-ci` (Internal IP: `10.10.0.2`, Zone: `asia-south1-a`)
- **Attached Service Account:** `jenkins-ci-staging@aditya-devops-lab.iam.gserviceaccount.com` (Pre-authorized with `roles/artifactregistry.writer`, `roles/container.developer`, and `roles/storage.objectAdmin`)
- **GKE Cluster:** `pricing-staging` in `asia-south1-a`
- **Registry Target:** `asia-south1-docker.pkg.dev/aditya-devops-lab/pricing/pricing-api:<git-sha>`
- **Deployment Command for Jenkinsfile:**
  ```bash
  gcloud container clusters get-credentials pricing-staging --zone asia-south1-a --project aditya-devops-lab
  kubectl set image deployment/pricing-api pricing-api=asia-south1-docker.pkg.dev/aditya-devops-lab/pricing/pricing-api:${GIT_SHA} -n pricing
  kubectl rollout status deployment/pricing-api -n pricing
  ```
- **Status:** ready for Jenkins pipeline execution

---

### H8: Model Storage & Container Registry Access (from: aditya-agent, to: bishwajeet, needed by: Day 6)
- **Models Bucket:** `gs://aditya-devops-lab-staging-models/pipeline.pkl`
- **Docker Authentication:** `gcloud auth configure-docker asia-south1-docker.pkg.dev`
- **Model Upload Command:** `gcloud storage cp src/model/pipeline.pkl gs://aditya-devops-lab-staging-models/pipeline.pkl`
- **Status:** complete (v1.0.0 image and 330MB pipeline.pkl deployed)

---

### H11: Public HTTPS Staging Endpoint (from: aditya-agent, to: shreyas, bishwajeet, needed by: Day 7)
- **Public URL:** `https://pricing-staging.136.81.137.108.sslip.io`
- **Direct IP:** `https://136.81.137.108`
- **Endpoints:**
  - `GET /`: Dynamic Pricing Calculator HTML UI
  - `GET /health`: Microservice Liveness & Readiness probe
  - `POST /api/predict`: Real-time Dynamic Pricing inference
- **Selenium Testing Requirement (H10):** Functional tests must enable `--ignore-certificate-errors` and `acceptInsecureCerts: true` to handle the staging self-signed TLS certificate (`tls-pricing-secret`).
- **Status:** verified live with HTTP 200 responses on all endpoints

---

### H12: GitHub Webhook Ingress for Jenkins (from: aditya-agent, to: shreyas, needed by: Day 7)
- **CI Webhook Port:** Port `8080` (Jenkins) on `pricing-staging-ci`
- **Firewall Range:** Restricted to official GitHub webhook CIDR ranges (`https://api.github.com/meta`) or protected via internal VPN/IAP.
- **Status:** configured in VPC firewall rules

