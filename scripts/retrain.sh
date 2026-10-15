#!/bin/bash
set -e

if [ -f .env ]; then
    source .env
fi

if [ -z "$GCS_MODEL_BUCKET" ] || [ -z "$RETRAIN_TOKEN" ] || [ -z "$APP_BASE_URL" ]; then
    echo "Error: Required environment variables (GCS_MODEL_BUCKET, RETRAIN_TOKEN, APP_BASE_URL) are not set."
    exit 1
fi

echo "Starting automated model retraining pipeline..."
python src/model/train.py

echo "Uploading new pipeline.pkl artifact to GCS..."
gsutil cp src/model/pipeline.pkl "gs://${GCS_MODEL_BUCKET}/pipeline.pkl"

echo "Triggering zero-downtime hot reload..."
curl -X POST -H "Authorization: Bearer ${RETRAIN_TOKEN}" "${APP_BASE_URL}/api/retrain"

echo -e "\nRetrain loop complete."