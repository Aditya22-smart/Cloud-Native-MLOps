# Terraform Infrastructure: Cloud-Native MLOps Dynamic Pricing Platform

This directory contains production-grade, modular Terraform code for provisioning Google Cloud Platform (GCP) infrastructure across environments (`staging`, `prod`).

---

## 1. Directory Structure

```text
terraform/
├── README.md                  # This guide
├── versions.tf               # Terraform and provider constraints
├── providers.tf              # Google and google-beta provider configurations
├── variables.tf              # Global input variables
├── main.tf                   # Root module orchestrating child modules
├── outputs.tf                # Shared infrastructure outputs
├── backend.hcl.example       # Example remote state backend configuration
├── terraform.tfvars.example  # Example variable definitions
├── destroy.sh                # Controlled environment teardown script
├── modules/                  # Reusable infrastructure modules
│   ├── vpc/                  # VPC, subnets, NAT, and firewall rules
│   ├── gke/                  # GKE standard cluster, node pools, Workload Identity
│   ├── gce/                  # CI (Jenkins/SonarQube) & ELK VM instances
│   ├── artifact_registry/   # Docker container registry & IAM bindings
│   └── gcs/                  # Versioned model and dataset storage buckets
└── workspaces/               # Per-environment variable definitions
    ├── staging.tfvars
    └── prod.tfvars
```

---

## 2. Lock File Decision (`.terraform.lock.hcl`)

Per team decision **D2** (documented in `ADITYA_TASK.md` Section 6 and Project Spec 10.3):
- `.terraform.lock.hcl` **is committed to version control**.
- **Rationale:** Ensures deterministic, repeatable provider plugin versions across all developer workstations and the Jenkins CI runner, preventing unexpected provider upgrades from breaking state or syntax.

---

## 3. Remote Backend Bootstrap

Terraform state is stored remotely in Google Cloud Storage (GCS) with object versioning enabled. Backend variables cannot be declared inside backend blocks, so configuration is supplied via a backend config file.

1. Create a `backend.hcl` from `backend.hcl.example`:
   ```bash
   cp backend.hcl.example backend.hcl
   ```
2. Set your bucket name:
   ```hcl
   bucket = "<PROJECT_ID>-tfstate"
   prefix = "terraform/state"
   ```
3. Initialize Terraform with the backend config:
   ```bash
   terraform init -backend-config=backend.hcl
   ```

---

## 4. Workspace & Multi-Environment Workflow

Environments are managed via Terraform workspaces (`staging` and `prod`).

### Select or Create a Workspace
```bash
# Create staging workspace
terraform workspace new staging
# Or select if it already exists
terraform workspace select staging
```

### Validate and Plan
```bash
# Format check
terraform fmt -check -recursive

# Syntax validation (local/offline)
terraform init -backend=false
terraform validate

# Plan against staging
terraform plan -var-file=workspaces/staging.tfvars
```

### Apply (Requires Explicit Approval)
```bash
terraform apply -var-file=workspaces/staging.tfvars
```

---

## 5. Teardown Safety (`destroy.sh`)

To prevent accidental destruction of production infrastructure and manage limited trial credits, always use `destroy.sh`:

```bash
chmod +x destroy.sh
./destroy.sh staging
```
The script confirms the active workspace and requires typing the environment name before invoking `terraform destroy`.
