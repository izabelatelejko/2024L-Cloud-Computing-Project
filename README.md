# 2024L-Cloud-Computing-Project
Project for the 2024L Cloud Computing course

## TODO:

* step for model validation
* automatically create project in terraform and enable Vertex AI, BigQuery, and Artifact Registry
* automatically add permissions for default service account (`storage.objects`, `bigquery`)
* automatically add users to project  
* function to run all templates (and generate them first for DOCKER and TERRAFORM) - `setup_project` or sth
* add `IMAGE` to config (for now we have fixed value: `training`) ?

### Authenticate with gcloud

```{sh}
gcloud auth application-default login
gcloud auth login
gcloud config set project <project_id>
gcloud auth application-default set-quota-project <project_id>
```

### Run terraform scripts

```{sh}
cd terraform
terraform init
terraform plan
terraform apply # confirm with yes
```

### Build and push docker image

```{sh}
./build_docker/build.sh
./build_docker/push_image.sh
```
