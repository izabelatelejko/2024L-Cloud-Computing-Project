resource "google_bigquery_dataset" "common" {
    dataset_id                  = "common_ds"
    friendly_name               = "Common dataset"
    description                 = "Keeps tables and stage tables for models"
    location                    = "europe-west3"
}

resource "google_bigquery_table" "main_data" {
    dataset_id = "common_ds"
    table_id   = "main_table"
    deletion_protection = false

    schema = file("./table_schemas/main_schema.json")

    depends_on = [
        google_bigquery_dataset.common,
    ]
}
