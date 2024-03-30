#!/bin/bash     
PROJECT_ID="test-house-418522"
REGION="europe-west3"
REPOSITORY="houseprice"
IMAGE='training'
IMAGE_TAG='training:latest'

docker build -t $IMAGE .
docker tag $IMAGE $REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY/$IMAGE_TAG