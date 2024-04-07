# 2024L-Cloud-Computing-Project
Project for the 2024L Cloud Computing course

## TODO:

* **step for model validation**
* **add to config some model related params**
* automatically create project in terraform and enable Vertex AI, BigQuery, and Artifact Registry
* automatically add permissions for default service account (`storage.objects`, `bigquery`)
* automatically add users to project  
* function to run all templates (and generate them first for DOCKER and TERRAFORM) - `setup_project` or sth
* add `IMAGE` to config (for now we have fixed value: `training`) ?
* add serving CF deployment in workflows using command `gcloud functions deploy <CF-name> --gen2 --runtime=python310 --region=europe-west3 --source=.terraform/cf_source/<source_folder>/ --entry-point=run --trigger-http`
<<<<<<< HEAD
* on model bucket keep models only for X days (perhaps add maintenance pipeline which does that?)
=======
* add logging (when pipeline code will be ready)
>>>>>>> 8a41805499a4c2fdcd4e32c40f4b7a563802591e

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
./docker_build/build.sh
./docker_build/push_image.sh
```

### Upload data to BQ table

```{sh}
python3 load_mock_data.py
```
