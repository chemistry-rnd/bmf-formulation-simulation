#!/bin/bash
set -e

PROJECT_ID="scalewithai-vc"
REGION="europe-west1"
SERVICE_NAME="brief-form"
IMAGE="europe-west1-docker.pkg.dev/$PROJECT_ID/chatbot/brief"

echo "=== Deploying aiqarus Brief Form ==="
echo ""

# 1. Build and push Docker image
echo ">>> Building Docker image..."
docker build -t $IMAGE .
docker push $IMAGE
echo ">>> Image pushed"

# 2. Deploy to Cloud Run
echo ">>> Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image=$IMAGE \
  --region=$REGION \
  --platform=managed \
  --allow-unauthenticated \
  --service-account=chatbot-backend@$PROJECT_ID.iam.gserviceaccount.com \
  --set-env-vars="GCP_PROJECT=$PROJECT_ID,FIRESTORE_ENABLED=true" \
  --min-instances=0 \
  --max-instances=2 \
  --memory=256Mi \
  --cpu=1 \
  --timeout=60 \
  --project=$PROJECT_ID
echo ">>> Cloud Run deployed"

# 3. Get service URL
URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --project=$PROJECT_ID --format='value(status.url)')
echo ""
echo "=== DEPLOY COMPLETE ==="
echo "Cloud Run URL: $URL"
echo ""
echo "Next: configure DNS in Timeweb"
echo "  build-ai-assistant.aiqarus.ru → CNAME → ${URL#https://}"
