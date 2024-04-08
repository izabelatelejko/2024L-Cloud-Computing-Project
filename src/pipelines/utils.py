"""Pipeline utils."""

import numpy as np
from google.cloud import bigquery
from sklearn.ensemble import RandomForestClassifier
import pandas as pd


def remove_highly_correlated_features(df, threshold=0.9):
    corr_matrix = df.corr().abs()
    upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
    to_drop = [column for column in upper.columns if any(upper[column] > threshold)]
    return to_drop


def remove_constant_features(df):
    return [column for column in df.columns if df[column].nunique() == 1]


def standarise_float_columns(df):
    for column in df.columns:
        if df[column].dtype == "float64":
            df[column] = (df[column] - df[column].mean()) / df[column].std()
    return df


def normalise_int_columns(df):
    for column in df.columns:
        if df[column].dtype == "int64":
            df[column] = (df[column] - df[column].min()) / (
                df[column].max() - df[column].min()
            )
    return df


def initial_pokemon_preprocess(df):
    n_poke_appeared = np.sum(df.iloc[:, 49:200], axis=1)
    cols_to_be_dropped = (
        ["class", "appearedLocalTime", "continent", "city", "weather", "_id", "index"]
        + list(df.columns[36:42])
        + list(df.columns[43:49])
        + list(df.columns[49:200])
    )
    df = df.drop(cols_to_be_dropped, axis=1)
    df["n_poks_appeared"] = n_poke_appeared

    df.loc[df["appearedDayOfWeek"] == "dummy_day", "appearedDayOfWeek"] = "Monday"

    tranform_time_of_day = {"morning": 0, "afternoon": 1, "evening": 2, "night": 3}
    transform_day_of_week = {
        "Monday": 0,
        "Tuesday": 1,
        "Wednesday": 2,
        "Thursday": 3,
        "Friday": 4,
        "Saturday": 5,
        "Sunday": 6,
    }

    # One Hot Encode weather icon
    df = pd.concat(
        [df, pd.get_dummies(df["weatherIcon"], drop_first=True)], axis=1
    ).drop("weatherIcon", axis=1)

    # Label Encode Time of Day
    df["appearedTimeOfDay"] = df["appearedTimeOfDay"].map(tranform_time_of_day)
    # Label Encode day of week
    df["appearedDayOfWeek"] = df["appearedDayOfWeek"].map(transform_day_of_week)

    # Change bools into ints
    df = df * 1

    # Label encode urban instead of OHE
    df["urbanization_level"] = df["urban"] + df["suburban"] + df["midurban"]
    df = df.drop(["urban", "suburban", "midurban", "rural"], axis=1)

    return df


def preprocess_data(df, target_column_name):
    df = initial_pokemon_preprocess(df)
    y = df[target_column_name]
    X = df.drop(columns=[target_column_name])

    X_processed = X.drop(remove_highly_correlated_features(df, threshold=0.7), axis=1)
    X_processed = X_processed.drop(remove_constant_features(X_processed), axis=1)
    X_processed = standarise_float_columns(X_processed)
    X_processed = normalise_int_columns(X_processed)
    X_processed[target_column_name] = y

    return X_processed


def model_train(X_processed, target_column_name):
    y = X_processed[target_column_name]
    X = X_processed.drop(columns=[target_column_name])

    clf = RandomForestClassifier(
        max_depth=5, random_state=1307, n_estimators=100, class_weight="balanced"
    )
    clf.fit(X, y)

    return clf
