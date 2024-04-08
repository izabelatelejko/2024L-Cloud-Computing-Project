import json
import pickle
from datetime import datetime

import functions_framework
import pandas as pd
from google.cloud import storage
import os

BUCKET_NAME = "project_bucket_52dfc7cd"
PROJECT_NAME = "cloud-computing-project-418718"


def find_top_probas(probas, top_n=3):
    probas = probas.flatten()
    top_n_idx = probas.argsort()[-top_n:][::-1]
    return top_n_idx


def find_newest_model(client):
    blobs = client.list_blobs(BUCKET_NAME, prefix="models")

    newest_model = None
    newest_time = datetime.min

    for blob in blobs:
        model_timestamp = datetime.strptime(blob.name.split("/")[-2], "%d-%m-%Y:%H%M")
        if model_timestamp > newest_time:
            newest_model = blob.name.split("/")[-2]
            newest_time = model_timestamp

    return newest_model


def get_model_prediction(input_json):
    storage_client = storage.Client(PROJECT_NAME)
    newest_model_folder = find_newest_model(storage_client)

    model_bucket = storage_client.bucket(BUCKET_NAME)

    model_blob = model_bucket.blob(os.path.join("models", newest_model_folder, "model"))
    model_pickle = model_blob.download_as_string()
    model = pickle.loads(model_pickle)

    train_features_blob = model_bucket.blob(
        os.path.join("models", newest_model_folder, "preprocess_features")
    )
    train_features_pickle = train_features_blob.download_as_string()
    train_features = pickle.loads(train_features_pickle)

    prediction = model.predict_proba(pd.DataFrame(input_json, index=[0]))

    prediction = find_top_probas(prediction, top_n=3)

    return (
        f"Got model: {newest_model_folder}. You can encounter pokemons: {prediction}."
    )


@functions_framework.http
def run(request):
    request_type = request.get_json().get("request_type")
    if request_type == "get_model_prediction":
        return_value = get_model_prediction(json.loads(request.get_json().get("input")))
    return return_value
