terraform {
  required_version = ">= 1.3, < 2.0.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.38.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 5.38.0"
    }
  }

  # Partial backend configuration. Bucket and prefix provided via -backend-config=backend.hcl
  backend "gcs" {}
}
