
resource "google_storage_bucket" "serve_cf_bucket" {
  name                        = "serve_cf_bucket_35ar32da"
  location                    = "europe-west3"
  uniform_bucket_level_access = true
}

data "archive_file" "serve_cf_zip" {
  type        = "zip"
  output_path = "/tmp/serving-function-source.zip"
  source_dir  = "../src/serve_cf"
}

resource "google_storage_bucket_object" "test_zip" {
  name   = "serving-function-source.zip"
  bucket = google_storage_bucket.serve_cf_bucket.name
  source = data.archive_file.serve_cf_zip.output_path
}

resource "google_cloudfunctions2_function" "serve_cf" {
  name        = "serve-cf"
  location    = "europe-west3"
  description = "CF which serves models and metrics"

  build_config {
    runtime     = "python310"
    entry_point = "run"
    source {
      storage_source {
        bucket = google_storage_bucket.serve_cf_bucket.name
        object = google_storage_bucket_object.test_zip.name
      }
    }
  }

  service_config {
    max_instance_count = 1
    available_memory   = "256M"
    timeout_seconds    = 60
  }
}

resource "google_cloud_run_service_iam_member" "cf_member" {
  location = google_cloudfunctions2_function.serve_cf.location
  service  = google_cloudfunctions2_function.serve_cf.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}