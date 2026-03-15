#!/bin/bash
set -e

PROJECT_ID="scalewithai-vc"
REGION="europe-west1"
SERVICE_NAME="chatbot-api"
IMAGE="europe-west1-docker.pkg.dev/$PROJECT_ID/chatbot/api"

echo "=== Deploying ScaleWithAI VC ==="
echo ""

# 1. Build and push Docker image
echo ">>> Building backend Docker image..."
cd backend
docker build -t $IMAGE .
docker push $IMAGE
cd ..
echo ">>> Backend image pushed"

# 2. Deploy to Cloud Run
echo ">>> Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image=$IMAGE \
  --region=$REGION \
  --platform=managed \
  --allow-unauthenticated \
  --service-account=chatbot-backend@$PROJECT_ID.iam.gserviceaccount.com \
  --set-env-vars="GCP_PROJECT=$PROJECT_ID" \
  --min-instances=0 \
  --max-instances=3 \
  --memory=512Mi \
  --cpu=1 \
  --timeout=300 \
  --project=$PROJECT_ID
echo ">>> Cloud Run deployed"

# 3. Deploy frontend to Firebase Hosting
echo ">>> Deploying frontend to Firebase Hosting..."
firebase deploy --only hosting --project=$PROJECT_ID
echo ">>> Firebase Hosting deployed"

echo ""
echo "=== DEPLOY COMPLETE ==="
echo "Site: https://vc.aiqarus.ru"
