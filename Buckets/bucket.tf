resource "random_id" "storage_id" {
  byte_length = 4
  prefix      = "project_bucket_"
}

provider "google" {
  project = "cloud-computing-project-418718"
}

resource "google_storage_bucket" "project_bucket" {
    name          = random_id.storage_id.hex
    location      = "europe-west3"
    force_destroy = true
}

# resource "google_storage_bucket_access_control" "bucket-access-rule" {
#   bucket = google_storage_bucket.project_bucket
#   role   = "READER"
#   entity = "allUsers"
# }