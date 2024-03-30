provider "google" {
  project = "cloud-computing-project-418718"
}

resource "google_storage_bucket" "project_bucket" {
    name          = "project_bucket_52dfc7cd"
    location      = "europe-west3"
    force_destroy = true
}