#!/bin/bash     
PROJECT_ID="test-house-418522"
REGION="europe-west3"
REPOSITORY="houseprice"
IMAGE_TAG='training:latest'

# Create repository in the artifact registry
gcloud beta artifacts repositories create $REPOSITORY \
  --repository-format=docker \
  --location=$REGION

# Configure Docker
gcloud auth configure-docker $REGION-docker.pkg.dev

# Push
docker push $REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY/$IMAGE_TAG