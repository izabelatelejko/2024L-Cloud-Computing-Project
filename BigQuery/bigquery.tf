provider "google" {
  project = "cloud-computing-project-418718"
}

resource "google_bigquery_dataset" "common" {
    dataset_id                  = "common_ds"
    friendly_name               = "Common dataset"
    description                 = "Keeps tables and stage tables for models"
    location                    = "europe-west3"
}

resource "google_bigquery_table" "main_data" {
    dataset_id = "common_ds"
    table_id   = "main_data"
    deletion_protection = false

    schema = file("./main_schema.json")

    depends_on = [
        google_bigquery_dataset.common,
    ]
}

resource "google_bigquery_table" "stg_data" {
    dataset_id = "common_ds"
    table_id   = "stage_data"
    deletion_protection = false

    schema = file("./stg_schema.json")

    depends_on = [
        google_bigquery_dataset.common,
    ]
}


# resource "google_bigquery_dataset_access" "access" {
#   dataset_id    = google_bigquery_dataset.dataset.dataset_id
#   role          = "OWNER"
#   user_by_email = google_service_account.bqowner.email
# }

