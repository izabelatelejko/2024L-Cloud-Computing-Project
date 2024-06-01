"""Pipeline utils."""

import numpy as np
import pandas as pd
from google.cloud import bigquery
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression


def remove_highly_correlated_features(df, threshold=0.9):
    corr_matrix = df.corr().abs()
    upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
    to_drop = [column for column in upper.columns if any(upper[column] > threshold)]
    return to_drop


def find_constant_features(df):
    return [column for column in df.columns if df[column].nunique() == 1]


def standarize_columns(df):
    df_means = df.mean()
    df_std = df.std()
    df = (df - df_means) / df_std
    return df, df_means.to_list(), df_std.to_list()


def initial_pokemon_preprocess(df):
    df = df.drop(["index"], axis=1)
    n_poke_appeared = np.sum(df.iloc[:, 49:200], axis=1)
    cols_to_be_dropped = (
        ["class", "appearedLocalTime", "continent", "city", "weather", "_id"]
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

    # Merge two partly cloudy weatheras into one column
    df["partly-cloudy"] = df["partly-cloudy-day"] + df["partly-cloudy-night"]
    df = df.drop(["partly-cloudy-day", "partly-cloudy-night"], axis=1)

    # Drop exact times of sunset and sinrise since they provide similar information as the date
    df = df.drop(
        [
            "sunriseHour",
            "sunriseMinute",
            "sunriseMinutesMidnight",
            "sunsetMinutesMidnight",
            "sunsetHour",
            "sunsetMinute",
        ],
        axis=1,
    )

    return df


def preprocess_data(df, target_column_name):
    df = initial_pokemon_preprocess(df)
    y = df[target_column_name]
    X = df.drop(columns=[target_column_name])

    X_high_corr = remove_highly_correlated_features(X, threshold=0.7)
    X_processed = X.drop(X_high_corr, axis=1)

    X_constant = find_constant_features(X_processed)
    X_processed = X_processed.drop(X_constant, axis=1)

    X_processed, X_means, X_std = standarize_columns(X_processed)

    training_features = {
        "means": X_means,
        "stds": X_std,
        "consts": X_constant,
        "high_corrs": X_high_corr,
    }
    X_processed[target_column_name] = y

    return X_processed, training_features


def model_train(X_processed, target_column_name):
    y = X_processed[target_column_name]
    X = X_processed.drop(columns=[target_column_name])

    print("Defining models...")
    clf1 = RandomForestClassifier(
        max_depth=5, random_state=1307, n_estimators=100, class_weight="balanced"
    )
    clf2 = GradientBoostingClassifier()
    clf3 = KNeighborsClassifier()
    clf4 = RandomForestClassifier(
        random_state=1307, n_estimators=100, criterion="entropy"
    )
    clf5 = LogisticRegression(max_iter=1000)

    print("Fitting model 1...")
    clf1.fit(X, y)
    print("Fitting model 2...")
    clf2.fit(X, y)
    print("Fitting model 3...")
    clf3.fit(X, y)
    print("Fitting model 4...")
    clf4.fit(X, y)
    print("Fitting model 5...")
    clf5.fit(X, y)

    return [clf1, clf2, clf3, clf4, clf5]
