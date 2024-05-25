# # Enable the required Google Cloud APIs

# resource "google_project_service" "all" {
#   for_each = toset([
#     "artifactregistry.googleapis.com",
#     "cloudbuild.googleapis.com",
#     "compute.googleapis.com",
#     "run.googleapis.com",
#     "secretmanager.googleapis.com",
#     "sql-component.googleapis.com",
#     "sqladmin.googleapis.com",
#   ])
#   project            = "cloud-computing-project-418718"
#   service            = each.key
#   disable_on_destroy = false
# }

# # create a Cloud SQL instance

# resource "google_sql_database_instance" "main" {
#   name             = "main"
#   database_version = "POSTGRES_14"
#   region           = "europe-west3"
#   deletion_protection = false

#   settings {
#     tier = "db-f1-micro"
#   }
#   depends_on = [
#     google_project_service.all
#   ]
# }

# # Create a database and user

# resource "google_sql_database" "main" {
#   name     = "main"
#   instance = google_sql_database_instance.main.name
# }

# resource "google_sql_user" "djuser" {
#   instance     = google_sql_database_instance.main.name
#   name         = "djuser"
#   password     = "DJuser123"
# }

# # Create a service account and grant it the required permissions

# resource "google_service_account" "cloudrun_django_sa" {
#   account_id   = "cloudrun-django-sa"
#   display_name = "Cloud Run Service Account for the Django application"
# }

# resource "google_project_iam_binding" "cloudsql_client_binding" {
#   project = "cloud-computing-project-418718"
#   for_each = toset([
#     "cloudsql.client",
#     "run.viewer",
#   ])
#   role = "roles/${each.key}"

#   members = [
#     "serviceAccount:${google_service_account.cloudrun_django_sa.email}"
#   ]
# }

# resource "google_storage_bucket_iam_binding" "bucket_sa_access" {
#   role    = "roles/storage.admin"
#   bucket  = "project_bucket_52dfc7cd"

#   members = [
#     "serviceAccount:${google_service_account.cloudrun_django_sa.email}"
#   ]
# }

# # Create secret manager

# locals {
#   ar_repository   = "europe-west3-docker.pkg.dev/cloud-computing-project-418718/docker-img"
#   image           = "${local.ar_repository}/django-on-cloudrun:bootstrap"
# }

# resource "google_secret_manager_secret" "application_settings" {
#   secret_id = "application_settings"

#   replication {
#     auto {}
#   }
#   depends_on = [google_project_service.all]

# }

# resource "google_secret_manager_secret_version" "application_settings" {
#   secret = google_secret_manager_secret.application_settings.id

#   secret_data = templatefile("${path.module}/application_settings.tftpl", {
#     staticfiles_bucket = "project_bucket_52dfc7cd"
#     secret_key = "HVbGGP5gRJrtVq7RZQUAGT6o8RSkiS"
#     user       = google_sql_user.djuser
#     instance   = google_sql_database_instance.main
#     database   = google_sql_database.main
#   })
# }

# # Grant the Cloud Run service account access to the secrets

# resource "google_secret_manager_secret_iam_binding" "application_settings" {
#   secret_id = google_secret_manager_secret.application_settings.id
#   role      = "roles/secretmanager.secretAccessor"
#   members   = [
#     "serviceAccount:${google_service_account.cloudrun_django_sa.email}"
#   ] 
# }

# # Generate a random password for the superuser and store it in Secret Manager

# resource "random_password" "superuser_password" {
#   length  = 32
#   special = false
# }

# resource "google_secret_manager_secret" "superuser_password" {
#   secret_id = "superuser_password"

#   replication {
#     auto {}
#   }
#   depends_on = [google_project_service.all]
# }

# resource "google_secret_manager_secret_version" "superuser_password" {
#   secret      = google_secret_manager_secret.superuser_password.id
#   secret_data = random_password.superuser_password.result
# }

# # Grant the Cloud Run service account access to the superuser password

# resource "google_secret_manager_secret_iam_binding" "superuser_password" {
#   secret_id = google_secret_manager_secret.superuser_password.id
#   role      = "roles/secretmanager.secretAccessor"
#   members   = [
#     "serviceAccount:${google_service_account.cloudrun_django_sa.email}"
#   ]
# }

# # Build the application image that the Cloud Run service and jobs will use

# resource "terraform_data" "bootstrap" {
#   provisioner "local-exec" {
#     working_dir = "${path.module}/../django/djangocloudrun"
#     command     = "gcloud builds submit --pack image=${local.image} ../"
#   }
# }

# # Create a Cloud Run job to run the Django migrations and collect static files

# resource "google_cloud_run_v2_job" "migrate_collectstatic" {
#   name     = "migrate-collectstatic"
#   location = "europe-west3"

#   template {
#     template {
#       service_account = google_service_account.cloudrun_django_sa.email

#       volumes {
#         name = "cloudsql"
#         cloud_sql_instance {
#           instances = [google_sql_database_instance.main.connection_name]
#         }
#       }
      
#       containers {
#         image   = local.image
#         command = ["migrate_collectstatic"]

#         env {
#           name = "APPLICATION_SETTINGS"
#           value_source {
            
#             secret_key_ref {
#               version = google_secret_manager_secret_version.application_settings.version
#               secret  = google_secret_manager_secret_version.application_settings.secret
#             }
#           }
#         }

#         volume_mounts {
#           name       = "cloudsql"
#           mount_path = "/cloudsql"
#         }

#       }
#     }
#   }

#   depends_on = [
#     terraform_data.bootstrap,
#   ]
# }

# # Create a Cloud Run job to create the superuser

# resource "google_cloud_run_v2_job" "create_superuser" {
#   name     = "create-superuser"
#   location = "europe-west3"

#   template {
#     template {
#       service_account = google_service_account.cloudrun_django_sa.email

#       volumes {
#         name = "cloudsql"
#         cloud_sql_instance {
#           instances = [google_sql_database_instance.main.connection_name]
#         }
#       }

#       containers {
#         image   = local.image
#         command = ["create_superuser"]

#         env {
#           name = "APPLICATION_SETTINGS"
#           value_source {
#             secret_key_ref {
#               version = google_secret_manager_secret_version.application_settings.version
#               secret  = google_secret_manager_secret_version.application_settings.secret
#             }
#           }
#         }

#         env {
#           name = "DJANGO_SUPERUSER_PASSWORD"
#           value_source {
#             secret_key_ref {
#               version = google_secret_manager_secret_version.superuser_password.version
#               secret  = google_secret_manager_secret_version.superuser_password.secret
#             }
#           }
#         }

#         volume_mounts {
#           name       = "cloudsql"
#           mount_path = "/cloudsql"
#         }

#       }
#     }
#   }

#   depends_on = [
#     terraform_data.bootstrap
#   ]
# }

# # Run the migrate-collectstatic job

# resource "terraform_data" "execute_migrate_collectstatic" {
#   provisioner "local-exec" {
#     command = "gcloud run jobs execute migrate-collectstatic --region 'europe-west3' --wait"
#   }

#   depends_on = [
#     google_cloud_run_v2_job.migrate_collectstatic,
#   ]
# }

# # Run the create-superuser job

# resource "terraform_data" "execute_create_superuser" {

#   provisioner "local-exec" {
#     command = "gcloud run jobs execute create-superuser --region 'europe-west3' --wait"
#   }

#   depends_on = [
#     google_cloud_run_v2_job.create_superuser,
#   ]
# }


# # Create a Cloud Run service

# resource "google_cloud_run_service" "app" {
#   name                       = "django-on-cloudrun"
#   location                   = "europe-west3"
#   autogenerate_revision_name = true
  

#   lifecycle {
#     replace_triggered_by = [terraform_data.bootstrap]
#   }

#   template {
#     spec {
#       service_account_name = google_service_account.cloudrun_django_sa.email
#       containers {
#         image = local.image

#         env {
#           name  = "SERVICE_NAME"
#           value = "django-on-cloudrun"
#         }

#         env {
#           name = "APPLICATION_SETTINGS"
#           value_from {
#               secret_key_ref {
#               key  = google_secret_manager_secret_version.application_settings.version
#               name = google_secret_manager_secret.application_settings.secret_id
#             }
#           }
#         }
#       }
#     }

#     metadata {
#       annotations = {
#         "autoscaling.knative.dev/maxScale"      = "1"
#         "run.googleapis.com/cloudsql-instances" = google_sql_database_instance.main.connection_name
#         "run.googleapis.com/client-name"        = "terraform"
#       }
#     }


#   }

#   traffic {
#     percent         = 100
#     latest_revision = true
#   }

#   depends_on = [
#     terraform_data.execute_migrate_collectstatic,
#     terraform_data.execute_create_superuser,
#   ]

# }

# # Grant permission to unauthenticated users to invoke the Cloud Run service

# data "google_iam_policy" "noauth" {
#   binding {
#     role    = "roles/run.invoker"
#     members = ["allUsers"]
#   }
# }

# resource "google_cloud_run_service_iam_policy" "noauth" {
#   location = google_cloud_run_service.app.location
#   project  = google_cloud_run_service.app.project
#   service  = google_cloud_run_service.app.name

#   policy_data = data.google_iam_policy.noauth.policy_data
# }

# output "service_url" {
#   value = google_cloud_run_service.app.status[0].url
# }