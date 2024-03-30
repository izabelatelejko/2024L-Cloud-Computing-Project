#!/bin/bash     
PROJECT_ID="cloud-computing-project-418718"
REGION="europe-west3"
REPOSITORY="docker_img"
IMAGE='training'
IMAGE_TAG='training:latest'

docker build -t $IMAGE .
docker tag $IMAGE $REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY/$IMAGE_TAG