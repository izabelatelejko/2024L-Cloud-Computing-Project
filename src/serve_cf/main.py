import functions_framework
import json
from datetime import datetime
from google.cloud import storage


BUCKET_NAME = "project_bucket_52dfc7cd"
PROJECT_NAME = "cloud-computing-project-418718"


def find_newest_model(client):
    blobs = client.list_blobs(BUCKET_NAME, prefix="models")

    newest_model = None
    newest_time = datetime.min

    for blob in blobs:
        model_timestamp = datetime.strptime(blob.name.split("/")[-1], "%d-%m-%Y:%H%M")
        if model_timestamp > newest_time:
            newest_model = blob.name
            newest_time = model_timestamp

    return newest_model


def get_model_prediction(input_json):
    storage_client = storage.Client("cloud-computing-project-418718")
    newest_model = find_newest_model(storage_client)

    # TODO: next step is to download pickle from newest_model location, load it as scikit learn model and make prediction from input_json

    return newest_model


@functions_framework.http
def run(request):
    request_type = request.get_json().get("request_type")
    if request_type == "get_model_prediction":
        return_value = get_model_prediction(json.loads(request.get_json().get("input")))
    return return_value
