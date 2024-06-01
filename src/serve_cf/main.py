import json
import pickle
from datetime import datetime

import functions_framework
import pandas as pd
from google.cloud import storage
import os

from const import BUCKET_NAME, PROJECT_NAME


def find_top_probas(probas, top_n=3):
    probas = probas.flatten()
    top_n_idx = probas.argsort()[-top_n:][::-1]
    return top_n_idx


def find_newest_model_date(client, model_name):
    blobs = client.list_blobs(BUCKET_NAME, prefix="models/" + model_name + "/")

    newest_model_date = None
    newest_model_accuracy = None
    newest_time = datetime.min

    for blob in blobs:
        model_path = blob.name.split("/")[-1]
        model_timestamp = datetime.strptime(model_path.split("_")[0], "%d-%m-%Y:%H%M")
        if model_timestamp > newest_time:
            newest_model_date = model_path.split("_")[0]
            newest_time = model_timestamp
            newest_model_accuracy = model_path.split("_")[1]

    return newest_model_date, newest_model_accuracy


def preprocess_input(input_df, train_features):
    input_df = input_df.drop(train_features["consts"], axis=1)
    input_df = input_df.drop(train_features["high_corrs"], axis=1)
    input_df = (input_df - train_features["means"]) / train_features["stds"]

    return input_df


def get_model_prediction(input_json, model_name, model_accuracy):
    storage_client = storage.Client(PROJECT_NAME)
    newest_model_date, _ = find_newest_model_date(storage_client, model_name)

    model_bucket = storage_client.bucket(BUCKET_NAME)

    model_blob = model_bucket.blob(
        os.path.join(
            "models", model_name, newest_model_date + "_" + str(model_accuracy)
        )
    )
    model_pickle = model_blob.download_as_string()
    model = pickle.loads(model_pickle)

    train_features_blob = model_bucket.blob(
        os.path.join(
            "models", "train_features", newest_model_date, "preprocess_features"
        )
    )
    train_features_pickle = train_features_blob.download_as_string()
    train_features = pickle.loads(train_features_pickle)

    input_df = pd.DataFrame(input_json, index=[0])
    input_df = preprocess_input(input_df, train_features)

    prediction = model.predict_proba(input_df)

    prediction = find_top_probas(prediction, top_n=9)

    return f"{prediction}"


def get_model_metrics():
    # model_names = [f"clf{i}" for i in range(5)]
    model_names = [f"clf{i}" for i in range(2)]
    storage_client = storage.Client(PROJECT_NAME)
    models_with_acc = {}
    for model_name in model_names:
        print(model_name)
        _, model_acc = find_newest_model_date(storage_client, model_name)
        models_with_acc[model_name] = model_acc

    return models_with_acc


@functions_framework.http
def run(request):
    request_type = request.get_json().get("request_type")
    model_name = request.get_json().get("model_name")
    model_accuracy = request.get_json().get("model_accuracy")
    if request_type == "get_model_prediction":
        return_value = get_model_prediction(
            json.loads(request.get_json().get("input")), model_name, model_accuracy
        )
    elif request_type == "get_model_metrics":
        return_value = get_model_metrics()
    return return_value
