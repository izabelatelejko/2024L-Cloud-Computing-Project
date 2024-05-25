PROJECT_ID="cloud-computing-project-418718"
REGION="europe-west3"
REPOSITORY="streamlit"
IMAGE_TAG='streamlit_app:latest'

# Build a local docker image
docker build -t streamlit_image .

# Configure Docker
gcloud auth configure-docker $REGION-docker.pkg.dev

# Push
docker push $REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY/$IMAGE_TAG