PROJECT_ID="cloud-computing-project-418718"
REGION="europe-west3"
REPOSITORY="docker-img"
IMAGE_TAG='streamlit_app:latest'

# Build a local docker image
docker build -t streamlit_image .
docker tag streamlit_image $REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY/$IMAGE_TAG

# Configure Docker
gcloud auth configure-docker $REGION-docker.pkg.dev

# Push
docker push $REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY/$IMAGE_TAG