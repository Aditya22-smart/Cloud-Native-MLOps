#!/usr/bin/env bash
# destroy.sh: Safe controlled environment teardown script

set -euo pipefail

if [ "$#" -ne 1 ]; then
  echo "Usage: $0 <environment>"
  echo "Example: $0 staging"
  exit 1
fi

TARGET_ENV="$1"
TFVARS_FILE="workspaces/${TARGET_ENV}.tfvars"

if [ ! -f "$TFVARS_FILE" ]; then
  echo "Error: Varfile '$TFVARS_FILE' not found."
  exit 1
fi

echo "=========================================================="
echo " [DANGER] YOU ARE ABOUT TO DESTROY ENVIRONMENT: ${TARGET_ENV}"
echo "=========================================================="
echo "This will destroy all Cloud infrastructure associated with"
echo "workspace: ${TARGET_ENV}"
echo ""

read -rp "To confirm destruction, please type '${TARGET_ENV}': " CONFIRMATION

if [ "$CONFIRMATION" != "$TARGET_ENV" ]; then
  echo "Confirmation mismatched. Aborting destruction."
  exit 1
fi

echo "Switching workspace to '${TARGET_ENV}'..."
terraform workspace select "$TARGET_ENV" || terraform workspace new "$TARGET_ENV"

echo "Running terraform destroy for '${TARGET_ENV}'..."
terraform destroy -var-file="$TFVARS_FILE"

echo "Environment '${TARGET_ENV}' destroyed successfully."
