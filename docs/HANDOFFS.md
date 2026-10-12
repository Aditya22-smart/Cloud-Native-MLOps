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
- **Status:** open (aditya-agent proposing default)
