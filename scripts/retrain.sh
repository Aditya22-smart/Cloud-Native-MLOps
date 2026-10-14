#!/bin/bash
# scripts/retrain.sh

set -e
echo "Starting automated model retraining pipeline..."

# Call Bishwajeet's training script
python src/model/train.py

echo "Uploading new pipeline.pkl artifact to GCS..."
# Uses the GCS bucket provisioned by Aditya
gsutil cp src/model/pipeline.pkl gs://$GCS_MODEL_BUCKET/models/latest/pipeline.pkl

echo "Triggering zero-downtime hot reload..."
# The /api/retrain endpoint is guarded by a bearer token
curl -X POST -H "Authorization: Bearer $RETRAIN_TOKEN" http://localhost:5000/api/retrain

echo -e "\nRetrain loop complete."