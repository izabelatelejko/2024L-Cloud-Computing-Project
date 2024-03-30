resource "google_artifact_registry_repository" "docker_img_repo" {
  location = "europe-west3"
  repository_id = "docker-img"
  description = "Repository keeps docker images for Vertex AI"
  format = "DOCKER"
}