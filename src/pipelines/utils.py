"""Pipeline utils."""

import numpy as np
from google.cloud import bigquery
from sklearn.ensemble import RandomForestClassifier


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


# to delete:
# def create_table_from_df(bq_client, df, table_id, write_disposition="WRITE_APPEND"):
#     job_config = bigquery.LoadJobConfig(write_disposition=write_disposition)
#     job = bq_client.load_table_from_dataframe(df, table_id, job_config=job_config)
#     job.result()


def preprocess_data(df, target_column_name):
    y = df[target_column_name]
    X = df.drop(columns=[target_column_name])

    X_processed = X.drop(remove_highly_correlated_features(df, threshold=0.7), axis=1)
    X_processed = X_processed.drop(["visitorid", "index"], axis=1)
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
