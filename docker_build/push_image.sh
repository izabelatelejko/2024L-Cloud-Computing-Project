#!/bin/bash     
PROJECT_ID="cloud-computing-project-418718"
REGION="europe-west3"
REPOSITORY="docker_img"
IMAGE_TAG='training:latest'

# Configure Docker
gcloud auth configure-docker $REGION-docker.pkg.dev

# Push
docker push $REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY/$IMAGE_TAG