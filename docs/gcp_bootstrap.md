# GCP Bootstrap Guide: Cloud-Native MLOps Dynamic Pricing Platform

This guide contains the ordered, reproducible bootstrap instructions for setting up the Google Cloud Platform (GCP) project, billing alerts, IAM permissions, Cloud Storage state backend, and branch protections for the project.

---

## 1. Project Information & Environment Variables

Export the agreed variables before running any commands:

```bash
export PROJECT_ID="<your-gcp-project-id>"
export REGION="asia-south1"
export ZONE="asia-south1-a"
export TFSTATE_BUCKET="${PROJECT_ID}-tfstate"

# Teammate Google accounts
export BISHWAJEET_EMAIL="<bishwajeet-email>@gmail.com"
export SHREYAS_EMAIL="<shreyas-email>@gmail.com"
```

Verify your active account and project:
```bash
gcloud auth list
gcloud config set project "${PROJECT_ID}"
```

---

## 2. Enable Required GCP APIs

Enable the mandatory service APIs required across Terraform, GKE, Artifact Registry, Secret Manager, and networking:

```bash
gcloud services enable \
  compute.googleapis.com \
  container.googleapis.com \
  artifactregistry.googleapis.com \
  secretmanager.googleapis.com \
  storage.googleapis.com \
  iam.googleapis.com \
  cloudresourcemanager.googleapis.com \
  serviceusage.googleapis.com \
  servicenetworking.googleapis.com \
  iap.googleapis.com \
  certificatemanager.googleapis.com
```

---

## 3. Remote Terraform State Bucket (GCS)

Terraform state must be stored in a centralized, version-controlled Cloud Storage bucket:

```bash
# Create bucket with uniform bucket-level access
gcloud storage buckets create "gs://${TFSTATE_BUCKET}" \
  --project="${PROJECT_ID}" \
  --location="${REGION}" \
  --uniform-bucket-level-access

# Enable object versioning to protect against accidental state corruption
gcloud storage buckets update "gs://${TFSTATE_BUCKET}" --versioning
```

---

## 4. Teammate IAM Access

Grant required development and read/write privileges to Bishwajeet (App/ML) and Shreyas (CI/CD/Observability):

```bash
# Storage access (for checking state bucket and model artifacts)
gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
  --member="user:${BISHWAJEET_EMAIL}" \
  --role="roles/storage.objectAdmin"

gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
  --member="user:${SHREYAS_EMAIL}" \
  --role="roles/storage.objectViewer"

# Artifact Registry access
gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
  --member="user:${BISHWAJEET_EMAIL}" \
  --role="roles/artifactregistry.writer"

gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
  --member="user:${SHREYAS_EMAIL}" \
  --role="roles/artifactregistry.writer"

# GKE viewer / developer access
gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
  --member="user:${BISHWAJEET_EMAIL}" \
  --role="roles/container.developer"

gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
  --member="user:${SHREYAS_EMAIL}" \
  --role="roles/container.developer"

# Compute Viewer
gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
  --member="user:${BISHWAJEET_EMAIL}" \
  --role="roles/compute.viewer"

gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
  --member="user:${SHREYAS_EMAIL}" \
  --role="roles/compute.viewer"
```

Verify that teammates can list the tfstate bucket:
```bash
gcloud storage ls "gs://${TFSTATE_BUCKET}"
```

---

## 5. Billing Budget & Alerts

To prevent unexpected billing on trial credits:
1. Navigate to **Google Cloud Console > Billing > Budgets & alerts**.
2. Create a budget for project `${PROJECT_ID}`.
3. Set alert thresholds at **50%**, **75%**, **90%**, and **100%** of budget.
4. Add email notification recipients for all three team members.

---

## 6. Git Branch Protections & Repository Rules

Ensure Git branching follows the team standard:
- `main`: Production-ready code; direct pushes restricted.
- `dev`: Active integration branch; all PRs merge here first.
- Feature branches cut from `dev`: `feature/infra-<topic>`.

### GitHub / GitLab Branch Protection Rules:
1. Protect `main`:
   - Require pull request reviews before merging (at least 1 review).
   - Require status checks to pass before merging.
   - Do not allow bypass for direct pushes or force pushes.
2. Protect `dev`:
   - Require pull request reviews (PR review ring: Aditya reviewed by Shreyas, Shreyas by Bishwajeet, Bishwajeet by Aditya).
   - Prevent force pushes.
